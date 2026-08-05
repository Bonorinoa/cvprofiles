"""Engine-schema smoke test for the design-locked H5 Trust inputs.

Runs the real cvprofiles pipeline on a synthetic country-level scores frame
using the *committed* roles/network/beta from evals/h5_trust/data. This proves
the pinned network schema (including corr_sign with sign=-1) is
engine-supported before any real data is fetched, and that the designed
invalids are rejected on a frame built to make them fail. Synthetic only; no
paper claim.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from cvprofiles.pipeline import run_profile, summary_dict

EVALS = Path(__file__).resolve().parents[1] / "evals" / "h5_trust"
DATA = EVALS / "data"
FREEZE_KEYS = (
    "empty",
    "M_star",
    "rejected",
    "L",
    "U",
    "point_id",
    "scores_hash",
    "network_hash",
    "beta_hash",
)

DESIGNED_INVALID = {"m_noise", "m_share_agriculture"}


def _synthetic_scores(rng: np.random.Generator) -> pd.DataFrame:
    iso3 = [f"CC{i:03d}" for i in range(8)]
    gps_trust = rng.normal(size=8)
    rule_of_law = 0.8 * gps_trust + 0.6 * rng.normal(size=8)
    gini = -0.7 * gps_trust + 0.5 * rng.normal(size=8)
    log_gdp = 0.9 * gps_trust + 0.4 * rng.normal(size=8)
    return pd.DataFrame(
        {
            "iso3": iso3,
            "m_trust_general": 0.7 * gps_trust + 0.3 * rng.normal(size=8),
            "m_trust_in_group": 0.6 * gps_trust + 0.4 * rng.normal(size=8),
            "m_trust_out_group": 0.8 * gps_trust + 0.2 * rng.normal(size=8),
            "m_trust_institution": 0.5 * gps_trust + 0.5 * rng.normal(size=8),
            # Designed-invalid: anti-correlated with the anchor / with rule of law.
            "m_noise": -0.9 * gps_trust + 0.1 * rng.normal(size=8),
            "m_share_agriculture": -0.8 * rule_of_law + 0.2 * rng.normal(size=8),
            "gps_trust": gps_trust,
            "rule_of_law": rule_of_law,
            "gini": gini,
            "log_gdp_pc": log_gdp,
            "n_trust_general": [2000] * 8,
            "n_trust_in_group": [2000] * 8,
            "n_trust_out_group": [2000] * 8,
            "n_trust_institution": [2000] * 8,
        }
    )


def _core(summary: dict) -> dict:
    return {k: summary[k] for k in FREEZE_KEYS}


def test_h5_network_schema_runs_and_rejects_designed_invalids(tmp_path: Path) -> None:
    rng = np.random.default_rng(20260804)
    scores_path = tmp_path / "scores.csv"
    _synthetic_scores(rng).to_csv(scores_path, index=False)

    s1 = summary_dict(
        run_profile(
            scores=scores_path,
            roles=DATA / "roles_h5_trust.json",
            network=DATA / "network_h5_trust.yaml",
            beta=DATA / "beta_h5_trust.yaml",
            out_dir=tmp_path / "run1",
            title="smoke",
            policy="none",
            seed=0,
        )
    )
    s2 = summary_dict(
        run_profile(
            scores=scores_path,
            roles=DATA / "roles_h5_trust.json",
            network=DATA / "network_h5_trust.yaml",
            beta=DATA / "beta_h5_trust.yaml",
            out_dir=tmp_path / "run2",
            title="smoke cold",
            policy="none",
            seed=0,
        )
    )

    import json

    roles = json.loads((DATA / "roles_h5_trust.json").read_text())
    menu = set(roles["measures"])

    # The pinned network schema is engine-supported and the design holds on
    # a frame built so the invalids fail: no designed-invalid is admitted.
    assert set(s1["M_star"]) <= menu
    assert not (set(s1["M_star"]) & DESIGNED_INVALID)
    # Cold freeze-core equality (synthetic smoke).
    assert _core(s1) == _core(s2)
    if not s1["empty"]:
        assert s1["L"] <= s1["U"]
