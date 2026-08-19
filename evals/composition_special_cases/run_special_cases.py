"""Recover empty-R and Campbell-Fiske special cases on frozen scores.

Not imported from src/. Uses the installed/editable cvprofiles 3.0.1 engine.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from cvprofiles import __version__
from cvprofiles.identify.beta_fn import evaluate_beta
from cvprofiles.identify.slacks import evaluate_slack
from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import RestrictionSpec

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[1]
PATIENCE_INPUTS = REPO / "evals" / "wvs_gps_preferences" / "data" / "inputs"
VALIDITY = Path(
    "/Users/bonorinoa/Desktop/Github_Repositories/SCA2_PofW/data/validity"
)
# Current seven-measure country patience menu (F7): fresh LLM columns joined
# onto the human frame; roles define GPS, Q13, Q14, composite, Llama, Phi, noise.
EMPTY_R_SCORES = (
    REPO / "evals" / "wvs_gps_two_resolution" / "data" / "country" / "patience_llm_extension.csv"
)
EMPTY_R_ROLES = (
    REPO / "evals" / "wvs_gps_two_resolution" / "roles" / "patience_country_llm.json"
)
EMPTY_R_BETA = (
    REPO / "evals" / "wvs_gps_two_resolution" / "betas" / "patience_country.yaml"
)
OUT = ROOT / "runs"
OUT.mkdir(parents=True, exist_ok=True)

# 2026-08-18 closeout (F7): empty_R re-frozen on the CURRENT seven-measure
# country patience menu (GPS, Q13, Q14, composite, Llama, Phi, noise).
# Superseded values (-0.219, 0.402) covered the 2026-08-10 pilot menu whose
# prompt columns were m_prompt_a/m_prompt_b; the current menu's max beta is
# Phi = 0.5649.
PAPER_L = -0.2187
PAPER_U = 0.5649
PAPER_ROUND = (-0.219, 0.565)

MTMM_MEASURES = [
    "gps_patience",
    "m_patience_child_qualities",
    "gps_trust",
    "m_trust_general",
]

# Restrictions that *name* each measure in the authored 2x2 (classical cells).
CELLS: dict[str, list[RestrictionSpec]] = {
    "gps_patience": [
        RestrictionSpec(
            id="conv_gps_patience_vs_wvs",
            type="corr_min",
            theta=0.30,
            params={"variable": "m_patience_child_qualities"},
        ),
        RestrictionSpec(
            id="disc_gps_patience_vs_gps_trust",
            type="corr_zero",
            theta=0.35,
            params={"variable": "gps_trust"},
        ),
        RestrictionSpec(
            id="disc_gps_patience_vs_wvs_trust",
            type="corr_zero",
            theta=0.35,
            params={"variable": "m_trust_general"},
        ),
    ],
    "m_patience_child_qualities": [
        RestrictionSpec(
            id="conv_wvs_patience_vs_gps",
            type="corr_min",
            theta=0.30,
            params={"variable": "gps_patience"},
        ),
        RestrictionSpec(
            id="disc_wvs_patience_vs_wvs_trust",
            type="corr_zero",
            theta=0.35,
            params={"variable": "m_trust_general"},
        ),
        RestrictionSpec(
            id="disc_gps_trust_vs_wvs_patience",
            type="corr_zero",
            theta=0.35,
            params={"variable": "gps_trust"},
        ),
    ],
    "gps_trust": [
        RestrictionSpec(
            id="conv_gps_trust_vs_wvs",
            type="corr_min",
            theta=0.30,
            params={"variable": "m_trust_general"},
        ),
        RestrictionSpec(
            id="disc_gps_patience_vs_gps_trust",
            type="corr_zero",
            theta=0.35,
            params={"variable": "gps_patience"},
        ),
        RestrictionSpec(
            id="disc_gps_trust_vs_wvs_patience",
            type="corr_zero",
            theta=0.35,
            params={"variable": "m_patience_child_qualities"},
        ),
    ],
    "m_trust_general": [
        RestrictionSpec(
            id="conv_wvs_trust_vs_gps",
            type="corr_min",
            theta=0.30,
            params={"variable": "gps_trust"},
        ),
        RestrictionSpec(
            id="disc_wvs_patience_vs_wvs_trust",
            type="corr_zero",
            theta=0.35,
            params={"variable": "m_patience_child_qualities"},
        ),
        RestrictionSpec(
            id="disc_gps_patience_vs_wvs_trust",
            type="corr_zero",
            theta=0.35,
            params={"variable": "gps_patience"},
        ),
    ],
}


def _write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def run_empty_r() -> dict:
    result = run_profile(
        scores=EMPTY_R_SCORES,
        roles=EMPTY_R_ROLES,
        network=ROOT / "networks" / "empty_R.yaml",
        beta=EMPTY_R_BETA,
        out_dir=OUT / "empty_R_current_menu",
        seed=20260814,
        title="Unrestricted multiverse (empty R) — current seven-measure country patience menu",
    )
    summary = summary_dict(result)
    betas = result.identify.beta_values
    L = float(min(betas.values()))
    U = float(max(betas.values()))
    range_L = result.identify.range_L
    range_U = result.identify.range_U
    if range_L is None or range_U is None:
        raise RuntimeError("empty_R run returned an empty range")
    payload = {
        "package_version": __version__,
        "empty_R": True,
        "note": (
            "2026-08-18 re-freeze (F7): current seven-measure country patience menu. "
            "Superseded run: runs/empty_R (2026-08-10 pilot menu, paper_round [-0.219, 0.402])."
        ),
        "n_units": int(result.score.frame.shape[0]),
        "M_star": list(result.identify.admissible),
        "menu": list(result.identify.measures),
        "beta_values": {k: float(v) for k, v in betas.items()},
        "L": float(range_L),
        "U": float(range_U),
        "L_from_full_menu": L,
        "U_from_full_menu": U,
        "recovers_full_menu": set(result.identify.admissible)
        == set(result.identify.measures),
        "matches_min_max_beta": abs(float(range_L) - L) < 1e-12
        and abs(float(range_U) - U) < 1e-12,
        "paper_table5_L": PAPER_L,
        "paper_table5_U": PAPER_U,
        "matches_table5_to_4dp": abs(L - PAPER_L) < 5e-5
        and abs(U - PAPER_U) < 5e-5,
        "paper_round": list(PAPER_ROUND),
        "run_id": result.run_id,
        "engine_summary": {
            "empty": summary["empty"],
            "L": summary["L"],
            "U": summary["U"],
        },
    }
    _write_json(ROOT / "empty_R_patience_recovery.json", payload)
    return payload


def build_mtmm_scores() -> pd.DataFrame:
    full = pd.read_csv(VALIDITY / "scores_full.csv")
    pat = pd.read_csv(PATIENCE_INPUTS / "scores.csv")
    keep = ["iso3", *MTMM_MEASURES]
    left = full[keep].copy()
    right = pat[["unit_id", "q275_mean", "log_gdp_pc"]].rename(
        columns={"unit_id": "iso3"}
    )
    merged = left.merge(right, on="iso3", how="inner")
    before = len(merged)
    merged = merged.dropna(subset=MTMM_MEASURES + ["q275_mean", "log_gdp_pc"])
    merged = merged.rename(columns={"iso3": "unit_id"})
    out = ROOT / "scores_mtmm.csv"
    merged.to_csv(out, index=False)
    print(f"MTMM scores: {before} joined, {len(merged)} complete -> {out}")
    return merged


def pairwise_cells(frame: pd.DataFrame) -> dict:
    slacks: dict[str, dict[str, float]] = {}
    corrs: dict[str, dict[str, float]] = {}
    for m, restrs in CELLS.items():
        slacks[m] = {}
        mvec = frame[m].to_numpy(dtype=float)
        for r in restrs:
            slacks[m][r.id] = float(evaluate_slack(mvec, frame, r))
        corrs[m] = {}
        for other in MTMM_MEASURES:
            if other == m:
                continue
            corrs[m][other] = float(frame[m].corr(frame[other]))
    retain = []
    fail = {}
    for m, restrs in CELLS.items():
        failing = [r.id for r in restrs if slacks[m][r.id] < 0]
        if failing:
            fail[m] = failing
        else:
            retain.append(m)
    beta = BetaSpec.model_validate_json(
        (ROOT / "beta.yaml").read_text().replace("'", '"')
        if False
        else json.dumps(
            {
                "schema_version": "1",
                "type": "ols_coef",
                "outcome": "log_gdp_pc",
                "params": {"controls": ["q275_mean"]},
            }
        )
    )
    # load beta from yaml via engine schema
    import yaml

    beta = BetaSpec.model_validate(yaml.safe_load((ROOT / "beta.yaml").read_text()))
    betas = {m: float(evaluate_beta(frame, m, beta)) for m in MTMM_MEASURES}
    return {
        "n_units": int(len(frame)),
        "correlations": corrs,
        "pair_slacks": slacks,
        "classical_retain": retain,
        "classical_fail": fail,
        "beta_values": betas,
    }


def run_full_menu_engine() -> dict:
    result = run_profile(
        scores=ROOT / "scores_mtmm.csv",
        roles=ROOT / "roles_mtmm.json",
        network=ROOT / "networks" / "mtmm_patience_trust.yaml",
        beta=ROOT / "beta.yaml",
        anchors=ROOT / "networks" / "anchors.yaml",
        out_dir=OUT / "mtmm_full_menu",
        seed=20260814,
        title="MTMM patience x trust (engine applies every r to every m)",
    )
    return {
        "M_star_engine_global": list(result.identify.admissible),
        "empty": result.identify.empty,
        "L": result.identify.range_L,
        "U": result.identify.range_U,
        "run_id": result.run_id,
        "rejected": result.identify.rejected,
        "note": (
            "Engine evaluates every restriction on every measure. "
            "This is stricter than classical per-instrument MTMM inspection."
        ),
    }


def main() -> None:
    print("package", __version__)
    empty = run_empty_r()
    print(
        "empty_R",
        empty["L"],
        empty["U"],
        "round",
        empty["paper_round"],
        "ok",
        empty["matches_table5_to_4dp"],
        empty["recovers_full_menu"],
    )
    frame = build_mtmm_scores()
    classical = pairwise_cells(frame)
    engine = run_full_menu_engine()
    payload = {
        "package_version": __version__,
        "tau_conv": 0.30,
        "tau_disc": 0.35,
        **classical,
        **engine,
        "bridge_matches_classical": set(engine["M_star_engine_global"])
        == set(classical["classical_retain"]),
    }
    _write_json(ROOT / "mtmm_patience_trust_recovery.json", payload)
    print("classical retain", classical["classical_retain"])
    print("engine global M*", engine["M_star_engine_global"])
    print("correlations")
    for m, row in classical["correlations"].items():
        print(" ", m, row)


if __name__ == "__main__":
    main()
