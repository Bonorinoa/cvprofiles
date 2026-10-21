"""Conservative CR as a DIAGNOSTIC on the WVS/GPS patience flagship (n=41 countries).

DIAGNOSTIC ONLY. Not paper evidence and not a run-gate decision (AGENTS.md;
logs/DECISIONS.md 2026-10-20 leaves the flagship CR run to Augusto). Writes
only under a git-ignored output directory (default reports/runs/...); never
touches reports/summaries/, allow-lists, paper/ or the frozen inputs.

Route (spec reports/specs/conservative_cr_spec.md §3.3, §7; decision D8):
the flagship β is ``ols_coef``, which has no native CR interval. This script
computes β and its SE upstream, here in evals/ (never in src/), and hands them
to the engine as β type ``external``:

  1. β(m) = standardized OLS coefficient on z(m) in z(y) ~ 1 + z(q275_mean) + z(m),
     the same numpy closed form as cvprofiles.identify.beta_fn._ols_coef,
     checked against the engine's beta_values (fresh v3 run and the frozen
     runs_stage4 artifact) to <= 1e-12.
  2. Two SE choices -> two beta_estimates CSVs:
       hc1   HC1 sandwich on the z-scored regression, df = n - k (Stata
             ``regress, vce(robust)`` convention). Treats the z-scoring as fixed.
       boot  units (country) pairs bootstrap SD of the standardized coefficient,
             re-standardizing inside every replicate; fixed seed; normal
             critical values (no df).
  3. run_profile with β ``external`` + confidence_region=True on the frozen
     scores/network, full frame (no holdout_units: the CR refuses them, D7),
     robust slack SE, alpha1 = alpha2 = 0.05, endpoint and simultaneous variants.
  4. Asserts the plug-in headline still equals the frozen
     M*_select = [m_gps_patience, m_prompt_a], [L, U] = [0.328, 0.402].

Assumptions the CR needs and this frame only approximately meets: i.i.d.
countries (A1); θ/δ/network fixed before the data (A1; θ for disc_risk was
re-anchored 2026-08-10); valid β SEs (A3, our claim here). Do NOT run this on
the cell-level frames (n=480 cells nested in countries): rows are not i.i.d.

    uv run python evals/wvs_gps_preferences/cr_diagnostic.py

stdout = one JSON summary; human crumbs on stderr.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
INPUTS = HERE / "data" / "inputs"
FROZEN_RUN = HERE / "data" / "runs_stage4"
DEFAULT_OUT = REPO / "reports" / "runs" / "wvs_gps_cr_diagnostic"

SEED = 20260810  # flagship run seed (frozen run_manifest)
N_BOOT_SE = 9999
FROZEN_SELECT = ["m_gps_patience", "m_prompt_a"]
FROZEN_L_3DP = 0.328
FROZEN_U_3DP = 0.402
BETA_TOL = 1e-12
SE_CHOICES = ("hc1", "boot")
VARIANTS = ("endpoint", "simultaneous")


def log(msg: str) -> None:
    print(msg, file=sys.stderr)


def zscore(v: np.ndarray) -> np.ndarray:
    """ddof=0 z-score, as cvprofiles' _zscore (SCORE convention)."""
    sd = float(np.std(v, ddof=0))
    if not math.isfinite(sd) or sd == 0.0:
        raise ValueError("zscore requires non-zero variance")
    return (v - float(np.mean(v))) / sd


def design(
    y: np.ndarray, controls: list[np.ndarray], m: np.ndarray
) -> tuple[np.ndarray, np.ndarray]:
    """X = [1, z(controls)..., z(m)], zy — the _ols_coef design."""
    zy = zscore(y)
    x = np.column_stack([np.ones(len(zy)), *[zscore(c) for c in controls], zscore(m)])
    return x, zy


def std_ols(y: np.ndarray, controls: list[np.ndarray], m: np.ndarray) -> float:
    """Standardized OLS coefficient on the measure (last coefficient)."""
    x, zy = design(y, controls, m)
    return float(np.linalg.solve(x.T @ x, x.T @ zy)[-1])


def hc1_se(y: np.ndarray, controls: list[np.ndarray], m: np.ndarray) -> tuple[float, int]:
    """HC1 SE of the last coefficient of the z-scored regression, and df = n - k."""
    x, zy = design(y, controls, m)
    n, k = x.shape
    xtx_inv = np.linalg.inv(x.T @ x)
    resid = zy - x @ (xtx_inv @ (x.T @ zy))
    meat = (x * resid[:, None] ** 2).T @ x
    vcov = (n / (n - k)) * xtx_inv @ meat @ xtx_inv
    return math.sqrt(float(vcov[-1, -1])), n - k


def boot_se(
    y: np.ndarray,
    controls: list[np.ndarray],
    m: np.ndarray,
    idx: np.ndarray,
) -> tuple[float, int, int]:
    """Units-bootstrap SD of the standardized coefficient (re-standardized per draw).

    Returns (se, n_used, n_degenerate). Degenerate draws (a zero-variance or
    singular column) are skipped and counted, never imputed.
    """
    draws: list[float] = []
    n_bad = 0
    for row in idx:
        try:
            coef = std_ols(y[row], [c[row] for c in controls], m[row])
        except (ValueError, np.linalg.LinAlgError):
            n_bad += 1
            continue
        if not math.isfinite(coef):
            n_bad += 1
            continue
        draws.append(coef)
    return float(np.std(np.asarray(draws), ddof=1)), len(draws), n_bad


def write_estimates(path: Path, rows: list[dict[str, Any]]) -> None:
    """beta_estimates.csv with round-trip float formatting (.17g)."""
    pd.DataFrame(rows).to_csv(path, index=False, float_format="%.17g", lineterminator="\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text())


def freeze_ids(run_dir: Path) -> dict[str, Any]:
    man = read_json(run_dir / "run_manifest.json")
    fz = man["freeze"]
    return {
        "run_id": man["run_id"],
        "scores_hash": fz["scores_hash"],
        "network_hash": fz["network_hash"],
        "beta_hash": fz["beta_hash"],
        "package_version": fz["package_version"],
        "config": fz["config"],
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--inputs", type=Path, default=INPUTS)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--n-boot-se", type=int, default=N_BOOT_SE)
    args = p.parse_args(argv)

    from cvprofiles import __version__
    from cvprofiles.pipeline import run_profile

    inputs: Path = args.inputs
    out: Path = args.out
    out.mkdir(parents=True, exist_ok=True)

    roles = read_json(inputs / "roles.json")
    beta_spec = yaml.safe_load((inputs / "beta.yaml").read_text())
    assert beta_spec["type"] == "ols_coef", beta_spec
    outcome = str(beta_spec["outcome"])
    controls_cols = [str(c) for c in beta_spec["params"]["controls"]]
    menu = [str(m) for m in roles["measures"]]

    # Same reader as the engine's SCORE stage (v3.0.2 round-trip parsing).
    frame = pd.read_csv(inputs / "scores.csv", float_precision="round_trip")
    n = len(frame)
    y = frame[outcome].to_numpy(dtype=float)
    ctrl = [frame[c].to_numpy(dtype=float) for c in controls_cols]
    log(f"[cr-diag] n={n} countries, menu={len(menu)}, controls={controls_cols}")

    # --- 1. reference engine run (ols_coef, full frame, no CR) -------------
    ref_dir = out / "ref_ols_coef"
    run_profile(
        scores=inputs / "scores.csv",
        roles=inputs / "roles.json",
        network=inputs / "network.yaml",
        beta=inputs / "beta.yaml",
        out_dir=ref_dir,
        seed=args.seed,
        title="WVS/GPS patience — CR diagnostic (reference ols_coef)",
    )
    engine_beta = read_json(ref_dir / "beta_values.json")["beta_values"]
    frozen_beta = read_json(FROZEN_RUN / "beta_values.json")["beta_values"]
    ref_range = read_json(ref_dir / "range.json")
    ref_adm = read_json(ref_dir / "admissible.json")

    # --- 2. β and SEs computed here (upstream of the engine) ---------------
    rng = np.random.default_rng(args.seed)
    idx = rng.integers(0, n, size=(args.n_boot_se, n))  # shared country draws
    per_measure: dict[str, dict[str, Any]] = {}
    for mname in menu:
        mv = frame[mname].to_numpy(dtype=float)
        b = std_ols(y, ctrl, mv)
        s_hc1, df_hc1 = hc1_se(y, ctrl, mv)
        s_boot, n_used, n_bad = boot_se(y, ctrl, mv, idx)
        per_measure[mname] = {
            "beta_hat": b,
            "diff_vs_engine": abs(b - float(engine_beta[mname])),
            "diff_vs_frozen_runs_stage4": abs(b - float(frozen_beta[mname])),
            "se_hc1": s_hc1,
            "df_hc1": df_hc1,
            "se_boot": s_boot,
            "boot_used": n_used,
            "boot_degenerate": n_bad,
            "se_ratio_boot_over_hc1": s_boot / s_hc1,
        }
    max_diff_engine = max(v["diff_vs_engine"] for v in per_measure.values())
    max_diff_frozen = max(v["diff_vs_frozen_runs_stage4"] for v in per_measure.values())
    if max_diff_engine > BETA_TOL or max_diff_frozen > BETA_TOL:
        raise SystemExit(
            f"β reproduction failed: max |diff| engine={max_diff_engine:.3g}, "
            f"frozen={max_diff_frozen:.3g} (tol {BETA_TOL})"
        )
    log(
        f"[cr-diag] β reproduces engine to {max_diff_engine:.2e}, "
        f"frozen runs_stage4 to {max_diff_frozen:.2e}"
    )

    estimator = "standardized OLS z(y)~1+z(q275_mean)+z(m); numpy closed form = cvprofiles ols_coef"
    est_paths = {
        "hc1": out / "beta_estimates_hc1.csv",
        "boot": out / "beta_estimates_boot.csv",
    }
    write_estimates(
        est_paths["hc1"],
        [
            {
                "measure": m,
                "beta_hat": v["beta_hat"],
                "se": v["se_hc1"],
                "df": float(v["df_hc1"]),
                "vcov": "HC1 on z-scored regression (z-scoring treated as fixed)",
                "n_obs": n,
                "estimator": estimator,
            }
            for m, v in per_measure.items()
        ],
    )
    write_estimates(
        est_paths["boot"],
        [
            {
                "measure": m,
                "beta_hat": v["beta_hat"],
                "se": v["se_boot"],
                "vcov": (
                    f"units bootstrap SD, B={args.n_boot_se}, seed={args.seed}, "
                    "re-standardized per draw"
                ),
                "n_obs": n,
                "estimator": estimator,
            }
            for m, v in per_measure.items()
        ],
    )
    beta_external = out / "beta_external.yaml"
    beta_external.write_text(
        yaml.safe_dump(
            {"schema_version": "1", "type": "external", "outcome": outcome, "params": {}},
            sort_keys=False,
        )
    )

    # --- 3. external β + CR runs -------------------------------------------
    runs: dict[str, dict[str, Any]] = {}
    for se_choice in SE_CHOICES:
        for variant in VARIANTS:
            key = f"{se_choice}_{variant}"
            run_dir = out / f"cr_{key}"
            run_profile(
                scores=inputs / "scores.csv",
                roles=inputs / "roles.json",
                network=inputs / "network.yaml",
                beta=beta_external,
                out_dir=run_dir,
                seed=args.seed,
                title=f"WVS/GPS patience — CR diagnostic ({se_choice}, {variant})",
                beta_estimates=est_paths[se_choice],
                confidence_region=True,
                cr_alpha1=0.05,
                cr_alpha2=0.05,
                cr_variant=variant,
                cr_se="robust",
            )
            rng_ = read_json(run_dir / "range.json")
            adm = read_json(run_dir / "admissible.json")
            cr = read_json(run_dir / "confidence_region.json")
            headline_ok = (
                adm["M_star_select"] == FROZEN_SELECT
                and rng_["L"] == ref_range["L"]
                and rng_["U"] == ref_range["U"]
                and round(rng_["L"], 3) == FROZEN_L_3DP
                and round(rng_["U"], 3) == FROZEN_U_3DP
            )
            if not headline_ok:
                raise SystemExit(f"{key}: plug-in headline moved: {adm['M_star_select']} {rng_}")
            runs[key] = {
                "out_dir": str(run_dir.relative_to(REPO))
                if run_dir.is_relative_to(REPO)
                else str(run_dir),
                "headline": {"M_star_select": adm["M_star_select"], "L": rng_["L"], "U": rng_["U"]},
                "freeze": freeze_ids(run_dir),
                "CR_L": cr["CR_L"],
                "CR_U": cr["CR_U"],
                "empty_outer": cr["empty_outer"],
                "M_plus": cr["M_plus"],
                "M_minus": cr["M_minus"],
                "status": cr["status"],
                "levels": cr["levels"],
                "nominal_coverage": cr["nominal_coverage"],
                "se_method": cr["se_method"],
                "slack_bounds": cr["slack_bounds"],
                "beta_intervals": cr["beta_intervals"],
                "beta_estimates_hash": cr["beta_estimates_hash"],
            }
            log(
                f"[cr-diag] {key}: CR=[{cr['CR_L']:.3f}, {cr['CR_U']:.3f}] "
                f"M+={cr['M_plus']} M-={cr['M_minus']}"
            )

    summary = {
        "purpose": "DIAGNOSTIC — conservative CR on the WVS/GPS flagship country frame; "
        "not paper evidence, not a run-gate decision",
        "package_version": __version__,
        "seed": args.seed,
        "n_units": n,
        "menu": menu,
        "frozen_headline": {
            "M_star_select": FROZEN_SELECT,
            "L_3dp": FROZEN_L_3DP,
            "U_3dp": FROZEN_U_3DP,
        },
        "reference_ols_coef_run": {
            "M_star_select": ref_adm["M_star_select"],
            "L": ref_range["L"],
            "U": ref_range["U"],
            "freeze": freeze_ids(ref_dir),
        },
        "frozen_runs_stage4": freeze_ids(FROZEN_RUN),
        "beta_reproduction": {
            "max_abs_diff_vs_engine": max_diff_engine,
            "max_abs_diff_vs_frozen_runs_stage4": max_diff_frozen,
            "tol": BETA_TOL,
        },
        "n_boot_se": args.n_boot_se,
        "per_measure": per_measure,
        "runs": runs,
    }
    (out / "cr_diagnostic_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
