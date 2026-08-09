"""Paper-facing synthetic verification for position paper v6.

Finite-sample engine check only. Population DGP tables in the paper remain
authoritative closed-form quantities — do not replace them with these numbers.

Writes under reports/runs/paper_v6_synth_p4p5/ (gitignored bulk output).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import run_score

OUT = Path("reports/runs/paper_v6_synth_p4p5")
OUT.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(20260808)
n = 2000


def z(x: np.ndarray) -> np.ndarray:
    x = np.asarray(x, float)
    return (x - x.mean()) / x.std(ddof=0)


def main() -> None:
    # Latent structure approximating paper loadings (finite-sample verification)
    G = (rng.random(n) < 0.5).astype(int)
    C = z(rng.normal(size=n) + 0.40 * (2 * G - 1))
    Vd = z(rng.normal(size=n))
    eps_vc = rng.normal(size=n)
    eps_y = rng.normal(size=n)
    Vc = z(0.80 * C + np.sqrt(max(1 - 0.80**2, 0)) * eps_vc)
    Y = z(0.60 * C + np.sqrt(max(1 - 0.60**2, 0)) * eps_y)

    loadings = {
        "m_true": (0.90, 0.0),
        "m_weak": (0.50, 0.0),
        "m_contam": (0.70, 0.55),
        "m_method": (0.20, 0.0),
        "m_noise": (0.0, 0.0),
    }

    def make_m(
        lc: float,
        ld: float,
        *,
        method_dom: bool = False,
        pure_noise: bool = False,
    ) -> np.ndarray:
        if pure_noise:
            return z(rng.normal(size=n))
        core = lc * C + ld * Vd
        if method_dom:
            raw = core + 2.0 * rng.normal(size=n)
        else:
            target_var = max(1e-6, 1.0 - lc**2 - ld**2)
            raw = core + np.sqrt(target_var) * rng.normal(size=n)
        return z(raw)

    cols: dict = {
        "unit_id": [f"u{i:04d}" for i in range(n)],
        "v_c": Vc,
        "v_d": Vd,
        "G": G.astype(float),
        "y": Y,
    }
    for name, (lc, ld) in loadings.items():
        cols[name] = make_m(
            lc,
            ld,
            method_dom=(name == "m_method"),
            pure_noise=(name == "m_noise"),
        )

    df = pd.DataFrame(cols)
    scores_path = OUT / "scores.csv"
    df.to_csv(scores_path, index=False)

    roles = {
        "unit_id": "unit_id",
        "measures": list(loadings),
        "aux": ["v_c", "v_d", "G"],
        "outcome": "y",
        "diagnostic": [],
    }
    (OUT / "roles.json").write_text(json.dumps(roles, indent=2))

    beta = {
        "schema_version": "1",
        "type": "corr_y",
        "outcome": "y",
        "params": {},
    }
    (OUT / "beta.yaml").write_text(yaml.safe_dump(beta, sort_keys=False))

    network_a = {
        "schema_version": "1",
        "name": "dgp_a",
        "delta": 0.0,
        "restrictions": [
            {"id": "r_conv", "type": "corr_min", "theta": 0.39, "params": {"variable": "v_c"}},
            {"id": "r_disc", "type": "corr_zero", "theta": 0.25, "params": {"variable": "v_d"}},
            {
                "id": "r_grp",
                "type": "mean_order",
                "theta": 0.25,
                "params": {"group": "G", "sign": 1},
            },
        ],
    }
    (OUT / "network_a.yaml").write_text(yaml.safe_dump(network_a, sort_keys=False))

    network_d = {
        "schema_version": "1",
        "name": "dgp_d_stage",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_conv_s",
                "type": "corr_min",
                "theta": 0.40,
                "params": {"variable": "v_c"},
                "stage": "select",
            },
            {
                "id": "r_disc_s",
                "type": "corr_zero",
                "theta": 0.60,
                "params": {"variable": "v_d"},
                "stage": "select",
            },
            {
                "id": "r_disc_h",
                "type": "corr_zero",
                "theta": 0.20,
                "params": {"variable": "v_d"},
                "stage": "holdout",
            },
            {
                "id": "r_grp_h",
                "type": "mean_order",
                "theta": 0.25,
                "params": {"group": "G", "sign": 1},
                "stage": "holdout",
            },
        ],
    }
    (OUT / "network_d.yaml").write_text(yaml.safe_dump(network_d, sort_keys=False))

    print("=== CLOSED FORM (paper; do not replace) ===")
    print("DGP A: M*={m_true,m_weak}, Theta*={0.30,0.54}")
    print("DGP D: select admits true/weak/contam; holdout fails contam; pass 2/3 vs anchor 1/2")

    # DGP A + P5
    out_a = OUT / "run_a"
    out_a.mkdir(exist_ok=True)
    res_a = run_profile(
        scores=scores_path,
        roles=OUT / "roles.json",
        network=OUT / "network_a.yaml",
        beta=OUT / "beta.yaml",
        out_dir=out_a,
        seed=20260808,
        n_boot=400,
        alpha=0.10,
        kappa=2.0,
        title="DGP A finite-sample illustration",
        write_parquet=False,
    )
    s_a = summary_dict(res_a)
    print("\n=== DGP A finite-sample (n=2000, n_boot=400) ===")
    print("run_id:", s_a.get("run_id"))
    print("admissible:", s_a.get("admissible"))
    print("range_L/U:", s_a.get("range_L"), s_a.get("range_U"))
    print("empty:", s_a.get("empty"))

    roles_m = ScoreColumnRoles.model_validate(roles)
    scored = run_score(df, roles_m, policy="none")
    bundle_a = run_restrict(scored.roles, network_a, OUT / "beta.yaml")
    ident_a = run_identify(scored.frame, scored.roles, bundle_a)
    print("sample slacks:\n", ident_a.slacks.round(3).to_string())
    print("beta:", {k: round(float(v), 3) for k, v in ident_a.beta_values.items()})
    if res_a.coverage:
        c = res_a.coverage
        print(f"coverage band [{c.band_L:.4f}, {c.band_U:.4f}] alpha={c.alpha}")
        print(
            f"empty_rate={c.empty_replicate_rate:.4f} "
            f"nonempty={c.replicates_nonempty}/{c.replicates_total}"
        )
        print(
            "boundary:",
            [
                (
                    b.measure,
                    round(b.margin, 4),
                    None if b.se is None else round(b.se, 4),
                    b.boundary,
                )
                for b in c.boundary
            ],
        )
        print(
            "p_hat_m:",
            {k: (None if v is None else round(v, 3)) for k, v in c.p_hat_m.items()},
        )

    # DGP D stage-split
    out_d = OUT / "run_d_stage"
    out_d.mkdir(exist_ok=True)
    res_d = run_profile(
        scores=scores_path,
        roles=OUT / "roles.json",
        network=OUT / "network_d.yaml",
        beta=OUT / "beta.yaml",
        out_dir=out_d,
        seed=20260808,
        n_boot=200,
        title="DGP D stage-split illustration",
        write_parquet=False,
    )
    s_d = summary_dict(res_d)
    adm_d = json.loads((out_d / "admissible.json").read_text())
    print("\n=== DGP D stage-split (P4a) ===")
    print("run_id:", s_d.get("run_id"))
    print("admissible (select-gated headline):", s_d.get("admissible"))
    print("M_star_select:", s_d.get("M_star_select"))
    print("M_star_robust:", s_d.get("M_star_robust"))
    print("holdout block:", json.dumps(adm_d.get("holdout"), indent=2)[:1200])
    bundle_d = run_restrict(scored.roles, network_d, OUT / "beta.yaml")
    ident_d = run_identify(scored.frame, scored.roles, bundle_d)
    print("slacks (all stages):\n", ident_d.slacks.round(3).to_string())
    print("holdout_verdict:", ident_d.holdout_verdict)

    # Units-split on DGP A network
    hold_ids = [f"u{i:04d}" for i in range(400)]
    out_u = OUT / "run_units_split"
    out_u.mkdir(exist_ok=True)
    res_u = run_profile(
        scores=scores_path,
        roles=OUT / "roles.json",
        network=OUT / "network_a.yaml",
        beta=OUT / "beta.yaml",
        out_dir=out_u,
        seed=20260808,
        n_boot=200,
        holdout_units=hold_ids,
        title="Units-split illustration on DGP A network",
        write_parquet=False,
    )
    s_u = summary_dict(res_u)
    adm_u = json.loads((out_u / "admissible.json").read_text())
    print("\n=== Units-split on DGP A network (P4b) ===")
    print("run_id:", s_u.get("run_id"))
    print("admissible/robust:", s_u.get("admissible"))
    print("M_star_select:", s_u.get("M_star_select"))
    print("M_star_robust:", s_u.get("M_star_robust"))
    print("range:", s_u.get("range_L"), s_u.get("range_U"))
    print("holdout.units count:", len((adm_u.get("holdout") or {}).get("units") or []))
    if res_u.coverage:
        c = res_u.coverage
        print(
            f"coverage (selection unc., NOT holdout band): "
            f"[{c.band_L:.4f}, {c.band_U:.4f}] empty_rate={c.empty_replicate_rate:.4f}"
        )

    summary = {
        "note": (
            "Finite-sample engine verification only. "
            "Paper DGP tables remain population closed-form."
        ),
        "package_version": "2.5.0",
        "engine_commit": "e088b06",
        "n": n,
        "seed": 20260808,
        "closed_form_dgp_a": {
            "M_star": ["m_true", "m_weak"],
            "Theta_star": [0.30, 0.54],
        },
        "finite_sample_a": {
            # summary_dict keys: M_star, L, U (not admissible/range_*)
            "run_id": s_a.get("run_id"),
            "M_star": s_a.get("M_star"),
            "L": s_a.get("L"),
            "U": s_a.get("U"),
            "sample_slacks": ident_a.slacks.round(4).to_dict(),
            "beta": {k: float(v) for k, v in ident_a.beta_values.items()},
            "coverage": None
            if res_a.coverage is None
            else {
                "band_L": res_a.coverage.band_L,
                "band_U": res_a.coverage.band_U,
                "empty_replicate_rate": res_a.coverage.empty_replicate_rate,
                "p_hat_m": res_a.coverage.p_hat_m,
                "boundary": [
                    {
                        "measure": b.measure,
                        "margin": b.margin,
                        "se": b.se,
                        "boundary": b.boundary,
                    }
                    for b in res_a.coverage.boundary
                ],
            },
        },
        "stage_split_d": {
            "run_id": s_d.get("run_id"),
            "M_star": s_d.get("M_star"),
            "M_star_select": s_d.get("M_star_select"),
            "M_star_robust": s_d.get("M_star_robust"),
            "L": s_d.get("L"),
            "U": s_d.get("U"),
            "holdout_verdict": ident_d.holdout_verdict,
            "holdout": adm_d.get("holdout"),
        },
        "units_split": {
            "run_id": s_u.get("run_id"),
            "M_star": s_u.get("M_star"),
            "M_star_select": s_u.get("M_star_select"),
            "M_star_robust": s_u.get("M_star_robust"),
            "L": s_u.get("L"),
            "U": s_u.get("U"),
            "coverage_band": None
            if res_u.coverage is None
            else [res_u.coverage.band_L, res_u.coverage.band_U],
            "empty_replicate_rate": None
            if res_u.coverage is None
            else res_u.coverage.empty_replicate_rate,
        },
    }
    out_path = OUT / "paper_synth_summary.json"
    out_path.write_text(json.dumps(summary, indent=2, default=str))
    print("\nWrote", out_path)


if __name__ == "__main__":
    main()
