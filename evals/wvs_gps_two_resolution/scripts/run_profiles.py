"""Run the four confirmatory two-resolution profiles + baselines.

Networks and anchors were authored before this script inspects slacks.
"""

from __future__ import annotations

import json
from itertools import combinations
from pathlib import Path

import numpy as np
import yaml

from cvprofiles import __version__
from cvprofiles.identify.beta_fn import evaluate_beta
from cvprofiles.identify.slacks import slack_matrix
from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "runs"
OUT.mkdir(parents=True, exist_ok=True)
SEED = 20260814
N_BOOT = 1000
THETA_GRID = [0.5, 1.0, 1.5, 2.0]
N_DRAWS = 500

PROFILES = [
    {
        "id": "patience_country",
        "scores": ROOT / "data/country/patience.csv",
        "roles": ROOT / "roles/patience_country.json",
        "network": ROOT / "networks/patience_country.yaml",
        "beta": ROOT / "betas/patience_country.yaml",
        "anchors": ROOT / "networks/patience_country_anchors.yaml",
        "canonical": "m_wvs_q13",
        "title": "Patience — country",
    },
    {
        "id": "trust_country",
        "scores": ROOT / "data/country/trust.csv",
        "roles": ROOT / "roles/trust_country.json",
        "network": ROOT / "networks/trust_country.yaml",
        "beta": ROOT / "betas/trust_country.yaml",
        "anchors": ROOT / "networks/trust_country_anchors.yaml",
        "canonical": "m_trust_general",
        "title": "Trust — country",
    },
    {
        "id": "patience_cells",
        "scores": ROOT / "data/cells/patience.csv",
        "roles": ROOT / "roles/patience_cells.json",
        "network": ROOT / "networks/patience_cells.yaml",
        "beta": ROOT / "betas/patience_cells.yaml",
        "anchors": ROOT / "networks/patience_cells_anchors.yaml",
        "canonical": "m_wvs_q13",
        "title": "Patience — cells",
    },
    {
        "id": "trust_cells",
        "scores": ROOT / "data/cells/trust.csv",
        "roles": ROOT / "roles/trust_cells.json",
        "network": ROOT / "networks/trust_cells.yaml",
        "beta": ROOT / "betas/trust_cells.yaml",
        "anchors": ROOT / "networks/trust_cells_anchors.yaml",
        "canonical": "m_trust_general",
        "title": "Trust — cells",
    },
]


def _json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n")


def holdout_pass_rate(frame, measures, network: NetworkConfig, delta: float = 0.0) -> float:
    hold = [r for r in network.restrictions if r.stage == "holdout"]
    if not measures:
        return 0.0
    if not hold:
        return 1.0
    sl = slack_matrix(frame, measures, hold)
    n_pass = 0
    for m in measures:
        if all(float(sl.at[m, r.id]) >= -delta for r in hold):
            n_pass += 1
    return n_pass / len(measures)


def baselines(frame, roles_path: Path, network: NetworkConfig, beta: BetaSpec, canonical: str, selected: list[str]) -> dict:
    roles = json.loads(roles_path.read_text())
    menu = [m for m in roles["measures"] if m != "m_noise"]
    rng = np.random.default_rng(SEED)
    out: dict = {"menu_without_noise": menu, "n_draws": N_DRAWS}
    tool_rate = holdout_pass_rate(frame, selected, network)
    out["tool_holdout_pass_rate"] = tool_rate
    out["canonical"] = canonical
    out["canonical_in_menu"] = canonical in menu
    if canonical in menu:
        out["canonical_holdout_pass_rate"] = holdout_pass_rate(frame, [canonical], network)

    betas = {m: float(evaluate_beta(frame, m, beta)) for m in menu}
    best = max(menu, key=lambda m: abs(betas[m]))
    out["best_abs_beta"] = best
    out["best_abs_beta_value"] = betas[best]
    out["best_abs_beta_holdout_pass_rate"] = holdout_pass_rate(frame, [best], network)

    for k in (1, 2, 3):
        if k > len(menu):
            continue
        draws = []
        for _ in range(N_DRAWS):
            subset = list(rng.choice(menu, size=k, replace=False))
            draws.append(holdout_pass_rate(frame, subset, network))
        arr = np.asarray(draws, dtype=float)
        out[f"random_k{k}"] = {
            "pass_rate_mean": float(arr.mean()),
            "pass_rate_p50": float(np.quantile(arr, 0.50)),
            "pass_rate_p95": float(np.quantile(arr, 0.95)),
            "tool_percentile": float(np.mean(arr <= tool_rate)) if selected else None,
        }
    # exact enumeration for k=1 as a check
    k1 = {m: holdout_pass_rate(frame, [m], network) for m in menu}
    out["per_measure_holdout"] = k1
    return out


def run_one(spec: dict) -> dict:
    dest = OUT / spec["id"]
    result = run_profile(
        scores=spec["scores"],
        roles=spec["roles"],
        network=spec["network"],
        beta=spec["beta"],
        anchors=spec["anchors"],
        out_dir=dest,
        seed=SEED,
        n_boot=N_BOOT,
        theta_grid_lambdas=THETA_GRID,
        title=spec["title"],
    )
    summary = summary_dict(result)
    network = NetworkConfig.model_validate(yaml.safe_load(spec["network"].read_text()))
    beta = BetaSpec.model_validate(yaml.safe_load(spec["beta"].read_text()))
    base = baselines(
        result.score.frame,
        spec["roles"],
        network,
        beta,
        spec["canonical"],
        list(result.identify.admissible),
    )
    payload = {
        "id": spec["id"],
        "package_version": __version__,
        "n_units": int(result.score.frame.shape[0]),
        "headline_posture": "restriction_stage_split_M_star_select",
        **summary,
        "beta_values": {k: float(v) for k, v in result.identify.beta_values.items()},
        "holdout_verdict": result.identify.holdout_verdict,
        "baselines": base,
        "empty_replicate_rate": (
            None if result.coverage is None else result.coverage.empty_replicate_rate
        ),
        "coverage_band": (
            None
            if result.coverage is None
            else [result.coverage.band_L, result.coverage.band_U]
        ),
    }
    _json(dest / "profile_summary.json", payload)
    return payload


def main() -> None:
    print("package", __version__)
    summaries = []
    for spec in PROFILES:
        print("running", spec["id"], "...")
        summaries.append(run_one(spec))
        s = summaries[-1]
        print(
            " ",
            s["id"],
            "n=",
            s["n_units"],
            "M*=",
            s["M_star"],
            "L,U=",
            s["L"],
            s["U"],
            "empty_rep=",
            s["empty_replicate_rate"],
        )
    _json(ROOT / "application_summary.json", {
        "package_version": __version__,
        "seed": SEED,
        "n_boot": N_BOOT,
        "profiles": summaries,
    })


if __name__ == "__main__":
    main()
