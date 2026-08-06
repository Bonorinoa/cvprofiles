"""v2.0 δ-grid tolerance surface tests (thread a; docs/12 2026-08-05 D1).

Contract under test:
- absolute δ values: finite, unique, sorted ascending, δ >= 0
- headline = declared δ run (row equality when the declared δ is in the grid)
- monotone superset: M*(δ1) ⊆ M*(δ2) for δ1 < δ2 (admission is slack >= -δ)
- rows never touch network_hash / beta_hash (tolerance is IDENTIFY-side)
- payload JSON-serializable; empty rows carry L=U=None
- grid excluded from the freeze preimage is a wiring-level witness
  (tests/test_v2_wiring.py, M-a3)
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.inference.delta_grid import (
    DeltaGridError,
    delta_grid_payload,
    run_delta_grid,
)
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import run_score


@pytest.fixture
def scored_mini(mini_scores_df: pd.DataFrame, mini_roles: ScoreColumnRoles):
    return run_score(mini_scores_df, mini_roles, policy="none")


@pytest.fixture
def restrict_mini(mini_dir: Path, mini_roles: ScoreColumnRoles):
    return run_restrict(mini_roles, mini_dir / "network.yaml", mini_dir / "beta.yaml")


@pytest.fixture
def restrict_harsh(mini_dir: Path, mini_roles: ScoreColumnRoles):
    return run_restrict(
        mini_roles, mini_dir / "network_harsh.yaml", mini_dir / "beta.yaml"
    )


# --- validation ---


def test_validate_deltas_sorted_and_unique(scored_mini, restrict_mini) -> None:
    result = run_delta_grid(
        scored_mini.frame, scored_mini.roles, restrict_mini, [0.1, 0.0, 0.05]
    )
    assert result.deltas == (0.0, 0.05, 0.1)
    assert [r.delta_value for r in result.rows] == [0.0, 0.05, 0.1]


def test_validate_deltas_duplicates_fail_loud(scored_mini, restrict_mini) -> None:
    with pytest.raises(DeltaGridError, match="duplicate"):
        run_delta_grid(scored_mini.frame, scored_mini.roles, restrict_mini, [0.0, 0.0])


def test_validate_deltas_negative_fails_loud(scored_mini, restrict_mini) -> None:
    with pytest.raises(DeltaGridError, match="must be >= 0"):
        run_delta_grid(scored_mini.frame, scored_mini.roles, restrict_mini, [-0.1])


def test_validate_deltas_nonfinite_fails_loud(scored_mini, restrict_mini) -> None:
    with pytest.raises(DeltaGridError, match="finite"):
        run_delta_grid(
            scored_mini.frame, scored_mini.roles, restrict_mini, [float("nan")]
        )


def test_validate_deltas_empty_fails_loud(scored_mini, restrict_mini) -> None:
    with pytest.raises(DeltaGridError, match="at least one"):
        run_delta_grid(scored_mini.frame, scored_mini.roles, restrict_mini, [])


# --- engine ---


def test_headline_row_equals_declared_delta_run(scored_mini, restrict_mini) -> None:
    headline = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)
    grid = run_delta_grid(
        scored_mini.frame, scored_mini.roles, restrict_mini, [0.0, 0.1]
    )
    row = grid.row_for(0.0)
    assert row is not None
    assert tuple(row.admissible) == tuple(headline.admissible)
    assert row.range_L == headline.range_L
    assert row.range_U == headline.range_U
    assert row.empty == headline.empty
    assert grid.headline_delta == pytest.approx(restrict_mini.delta, abs=1e-12)


def test_monotone_superset_property(scored_mini, restrict_mini) -> None:
    # Measured on mini_v1: m_slop fails corr_min (-1.326) and corr_sign (-1.076);
    # at δ=1.4 both clear, so the oracle set grows {m_good,m_weak} -> +m_slop.
    grid = run_delta_grid(
        scored_mini.frame, scored_mini.roles, restrict_mini, [0.0, 0.5, 1.4]
    )
    a, b, c = (set(r.admissible) for r in grid.rows)
    assert a == {"m_good", "m_weak"}
    assert a <= b <= c
    assert c == {"m_good", "m_weak", "m_slop"}


def test_harsh_delta_sweep_empty_then_admits(scored_mini, restrict_harsh) -> None:
    # Hand-verified slacks on harsh: m_good -0.001311, m_weak -0.005854,
    # m_slop -1.974692 / -1.075692 (never admits in this grid).
    grid = run_delta_grid(
        scored_mini.frame, scored_mini.roles, restrict_harsh, [0.0, 0.01, 0.06]
    )
    assert grid.rows[0].empty is True
    assert set(grid.rows[1].admissible) == {"m_good", "m_weak"}
    assert set(grid.rows[2].admissible) == {"m_good", "m_weak"}
    assert all("m_slop" not in r.admissible for r in grid.rows)


def test_rows_share_network_and_beta_hashes(scored_mini, restrict_mini) -> None:
    grid = run_delta_grid(
        scored_mini.frame, scored_mini.roles, restrict_mini, [0.0, 0.1]
    )
    assert grid.network_hash == restrict_mini.network_hash
    assert grid.beta_hash == restrict_mini.beta_hash


# --- payload ---


def test_payload_is_json_serializable_with_none_empty_rows(
    scored_mini, restrict_harsh
) -> None:
    grid = run_delta_grid(
        scored_mini.frame, scored_mini.roles, restrict_harsh, [0.0, 0.01]
    )
    payload = delta_grid_payload(grid)
    text = json.dumps(payload)
    rows = payload["rows"]
    assert rows[0]["empty"] is True
    assert rows[0]["L"] is None and rows[0]["U"] is None
    assert rows[1]["empty"] is False
    assert payload["headline_delta"] == 0.0
    assert "delta" in text  # serialized fine
