"""rank_agree evaluator tests (v2.0 thread b, M-b2; docs/12 2026-08-05 D4).

Semantics: Spearman ρ between m and params.ref_measure (ties via average
ranks), slack = ρ - theta.

Fixture rank_agree_v1 (hand-computed, θ=0.8; ranks ascending, ties averaged):
  m_rank_ok   same rank order as ref     -> ρ=1.0        -> slack 0.2000 (admitted)
  m_rank_ok2  same rank order as ref     -> ρ=1.0        -> slack 0.2000 (admitted)
  m_rank_mid  ranks [10,9,8,7,6,1,2,3,4,5] vs ref -> ρ≈−0.7576 -> slack −1.5576 (rejected)
  m_rank_bad  reversed order             -> ρ=−1.0       -> slack −1.8000 (rejected)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import load_roles, run_score


@pytest.fixture
def ra_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "rank_agree_v1"


@pytest.fixture
def ra_roles(ra_path: Path) -> ScoreColumnRoles:
    return load_roles(ra_path / "roles.json")


@pytest.fixture
def scored_ra(ra_path: Path, ra_roles: ScoreColumnRoles):
    return run_score(pd.read_csv(ra_path / "scores.csv"), ra_roles, policy="none")


@pytest.fixture
def restrict_ra(ra_path: Path, ra_roles: ScoreColumnRoles):
    return run_restrict(ra_roles, ra_path / "network.yaml", ra_path / "beta.yaml")


def test_rank_agree_admits_ok_rejects_mid_and_bad(scored_ra, restrict_ra) -> None:
    result = run_identify(scored_ra.frame, scored_ra.roles, restrict_ra)
    assert set(result.admissible) == {"m_rank_ok", "m_rank_ok2"}
    assert set(result.rejected) == {"m_rank_mid", "m_rank_bad"}
    assert result.rejected["m_rank_mid"] == ["r_rank_agree_ref"]
    assert result.rejected["m_rank_bad"] == ["r_rank_agree_ref"]


def test_rank_agree_hand_golden_slacks(scored_ra, restrict_ra) -> None:
    result = run_identify(scored_ra.frame, scored_ra.roles, restrict_ra)
    assert result.slacks.at["m_rank_ok", "r_rank_agree_ref"] == pytest.approx(
        0.2, abs=1e-9
    )
    assert result.slacks.at["m_rank_ok2", "r_rank_agree_ref"] == pytest.approx(
        0.2, abs=1e-9
    )
    assert result.slacks.at["m_rank_mid", "r_rank_agree_ref"] == pytest.approx(
        -0.7575757576 - 0.8, abs=1e-5
    )
    assert result.slacks.at["m_rank_bad", "r_rank_agree_ref"] == pytest.approx(
        -1.8, abs=1e-9
    )


def test_rank_agree_missing_ref_fails_at_restrict(
    ra_path: Path, ra_roles, scored_ra
) -> None:
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_rank_agree_ref",
                "type": "rank_agree",
                "theta": 0.8,
                "params": {"ref_measure": "does_not_exist"},
            }
        ],
    }
    with pytest.raises(RestrictError, match="ref_measure"):
        run_restrict(ra_roles, raw, ra_path / "beta.yaml")


def test_rank_agree_ties_use_average_ranks(ra_path: Path) -> None:
    # ref [1..5]; m = [3,3,1,5,4] -> average ranks [2.5,2.5,1,5,4]
    # Spearman vs [1..5] = 5.5 / sqrt(10 * 9.5) ≈ 0.5643
    df = pd.DataFrame(
        {
            "unit_id": ["a", "b", "c", "d", "e"],
            "m_tie": [3.0, 3.0, 1.0, 5.0, 4.0],
            "ref_measure": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [1.0, 2.0, 3.0, 4.0, 5.0],
        }
    )
    roles = ScoreColumnRoles(
        unit_id="unit_id",
        measures=["m_tie"],
        aux=["ref_measure"],
        outcome="y",
        diagnostic=[],
    )
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_rank_agree_ref",
                "type": "rank_agree",
                "theta": 0.5,
                "params": {"ref_measure": "ref_measure"},
            }
        ],
    }
    bundle = run_restrict(roles, raw, ra_path / "beta.yaml")
    result = run_identify(df, roles, bundle)
    assert result.slacks.at["m_tie", "r_rank_agree_ref"] == pytest.approx(
        0.5643 - 0.5, abs=1e-4
    )


def test_rank_agree_nonfinite_ref_fails_loud(scored_ra, restrict_ra) -> None:
    df = scored_ra.frame.copy()
    df.loc[df.index[0], "ref_measure"] = float("nan")
    with pytest.raises(IdentifyError, match="finite"):
        run_identify(df, scored_ra.roles, restrict_ra)
