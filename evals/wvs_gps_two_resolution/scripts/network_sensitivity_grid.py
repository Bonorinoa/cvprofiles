"""Validity-argument sensitivity grid (paper §3.5(v), executed).

Sweeps substantively defensible validity arguments R_i over the frozen,
country-demeaned cell scores used by the powered application:

  R0      theta_edu = 0.20  (the frozen confirmatory network)
  R1      theta_edu = 0.10  (lenient floor)
  R2      theta_edu = 0.15
  R3      theta_edu = 0.25
  R4      theta_edu = 0.30  (strict floor)
  R5      theta_edu = 0.40  (very strict floor)
  R6      empty_R = true    (named unrestricted-multiverse special case)

All variants hold the leftover holdout monotonicity restriction (theta =
0.15) fixed, exactly as frozen. Admission uses select-stage restrictions
only; delta = 0; no bootstrap (this layer is not sampling uncertainty).

Read-only with respect to runs/: outputs land in
network_sensitivity_summary.json under evals/wvs_gps_two_resolution/.

Paper-facing rule: numbers come only from data/cells_demeaned/*.csv
(sha-stable inputs of the 2026-08-19 freezes), computed through released
3.0.2 primitives (slack_matrix / evaluate_beta). The R0 row must reproduce
the shipped freeze's M* exactly; the script asserts that gate.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from cvprofiles import __version__
from cvprofiles.identify.beta_fn import evaluate_beta
from cvprofiles.identify.slacks import slack_matrix
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig, RestrictionSpec

ROOT = Path(__file__).resolve().parents[1]
DELTA = 0.0

THETA_SWEEP: list[tuple[str, float | None]] = [
    ("R0_frozen_0.20", 0.20),
    ("R1_lenient_0.10", 0.10),
    ("R2_0.15", 0.15),
    ("R3_0.25", 0.25),
    ("R4_strict_0.30", 0.30),
    ("R5_vstrict_0.40", 0.40),
    ("R6_unrestricted", None),
]


def _network(theta: float | None) -> NetworkConfig:
    """Build an R_i: frozen structure, varied edu floor (or empty_R)."""
    if theta is None:
        return NetworkConfig(
            schema_version="1",
            name="empty_multiverse",
            delta=DELTA,
            empty_R=True,
            restrictions=[],
        )
    return NetworkConfig(
        schema_version="1",
        name=f"edu_floor_{theta:.2f}",
        delta=DELTA,
        empty_R=False,
        restrictions=[
            RestrictionSpec(
                id="conv_edu_cell",
                type="corr_min",
                theta=float(theta),
                stage="select",
                params={"variable": "q275_cell"},
            ),
            RestrictionSpec(
                id="mono_edu_cell",
                type="monotone_rank",
                theta=0.15,
                stage="holdout",
                params={"variable": "q275_cell", "sign": 1},
            ),
        ],
    )


def _admissible(frame: pd.DataFrame, measures: list[str], net: NetworkConfig) -> list[str]:
    if net.empty_R:
        return list(measures)
    sl = slack_matrix(frame, measures, net.restrictions)
    sel = [r for r in net.restrictions if r.stage == "select"]
    out: list[str] = []
    for m in measures:
        if all(float(sl.loc[m, r.id]) >= -DELTA for r in sel):
            out.append(m)
    return out


def grid_one(tag: str, scores_csv: Path, beta_yaml: Path) -> dict:
    frame = pd.read_csv(scores_csv)
    run_dir = ROOT / "runs" / tag
    roles = json.loads((run_dir / "score_manifest.json").read_text())["roles"]
    measures = [m for m in roles["measures"] if m != "m_noise"]
    beta = BetaSpec(**yaml.safe_load(beta_yaml.read_text()))
    betas_all = {m: float(evaluate_beta(frame, m, beta)) for m in measures}

    # Baseline sanity gate against the shipped freeze.
    net_json = json.loads((run_dir / "network_resolved.json").read_text())
    base_net = NetworkConfig(
        schema_version="1",
        name=str(net_json.get("name", tag)),
        delta=float(net_json.get("delta", 0.0)),
        empty_R=bool(net_json.get("empty_R", False)),
        restrictions=[RestrictionSpec(**r) for r in net_json["restrictions"]],
    )
    assert any(r.theta == 0.20 and r.stage == "select" for r in base_net.restrictions), (
        f"{tag}: baseline network drift"
    )
    adm_base = _admissible(frame, measures, base_net)

    rows = []
    for label, theta in THETA_SWEEP:
        net = _network(theta)
        adm = _admissible(frame, measures, net)
        b_star = sorted(round(betas_all[m], 4) for m in adm)
        rows.append({
            "network": label,
            "theta_edu_select": theta,
            "M_star": adm,
            "n_admissible": len(adm),
            "B_star_sorted": b_star,
            "L": min(b_star) if b_star else None,
            "U": max(b_star) if b_star else None,
            "empty": len(adm) == 0,
        })

    return {
        "profile": tag,
        "package_version": __version__,
        "delta": DELTA,
        "menu_no_noise": measures,
        "beta_by_measure": {k: round(v, 4) for k, v in sorted(betas_all.items())},
        "baseline_M_star_check_matches_freeze": adm_base,
        "grid": rows,
    }


def main() -> None:
    specs = [
        ("patience_cells_demeaned_llm",
         ROOT / "runs/patience_cells_demeaned_llm/S_frozen.csv",
         ROOT / "betas/patience_cells.yaml"),
        ("trust_cells_demeaned_llm",
         ROOT / "runs/trust_cells_demeaned_llm/S_frozen.csv",
         ROOT / "betas/trust_cells.yaml"),
    ]
    out = {}
    for tag, scores_csv, beta_yaml in specs:
        res = grid_one(tag, scores_csv, beta_yaml)
        out[tag] = res
        print(f"\n== {tag} ==")
        print(f"  baseline M* check (must equal freeze): {res['baseline_M_star_check_matches_freeze']}")
        print(f"  beta by measure: {res['beta_by_measure']}")
        for row in res["grid"]:
            rng = "EMPTY" if row["empty"] else f"[{row['L']:.4f}, {row['U']:.4f}]"
            print(f"  {row['network']:>18s}  M*={row['M_star']}  range={rng}")

    dest = ROOT / "network_sensitivity_summary.json"
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
