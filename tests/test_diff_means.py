"""diff_means beta evaluator tests (v3 P3; gate H_beta_dm).

Semantics (locked): β(m) = sign * (mean(m|G=1) - mean(m|G=0)).
Group must be a binary 0/1 aux column (fail loud otherwise).
sign default +1. Outcome is required by schema/bind but unused by the evaluator
(group contrast on the measure, not on y).

Fixture diff_means_v1 (same scores as mean_order_v1; hand-computed gaps):
  m_high: mean(g=1)=0.8, mean(g=0)=0.2 → gap +0.60
  m_low:  mean(g=1)=0.22, mean(g=0)=0.18 → gap +0.04
  m_slop: mean(g=1)=0.12, mean(g=0)=0.92 → gap -0.80
Network uses a non-binding corr_min so all three admit; range = [min β, max β].
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.identify.beta_fn import evaluate_beta
from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.identify.slacks import SlackError
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import load_roles, run_score


@pytest.fixture
def dm_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "diff_means_v1"


@pytest.fixture
def dm_roles(dm_path: Path) -> ScoreColumnRoles:
    return load_roles(dm_path / "roles.json")


@pytest.fixture
def scored_dm(dm_path: Path, dm_roles: ScoreColumnRoles):
    return run_score(pd.read_csv(dm_path / "scores.csv"), dm_roles, policy="none")


@pytest.fixture
def restrict_dm(dm_path: Path, dm_roles: ScoreColumnRoles):
    return run_restrict(dm_roles, dm_path / "network.yaml", dm_path / "beta.yaml")


def test_diff_means_hand_golden_betas(scored_dm, restrict_dm) -> None:
    result = run_identify(scored_dm.frame, scored_dm.roles, restrict_dm)
    assert set(result.admissible) == {"m_high", "m_low", "m_slop"}
    assert result.beta_values["m_high"] == pytest.approx(0.6, abs=1e-9)
    assert result.beta_values["m_low"] == pytest.approx(0.04, abs=1e-9)
    assert result.beta_values["m_slop"] == pytest.approx(-0.8, abs=1e-9)
    assert result.range_L == pytest.approx(-0.8, abs=1e-9)
    assert result.range_U == pytest.approx(0.6, abs=1e-9)


def test_diff_means_sign_negative_flips(scored_dm, dm_roles, dm_path) -> None:
    beta = {
        "schema_version": "1",
        "type": "diff_means",
        "outcome": "y",
        "params": {"group": "group", "sign": -1},
    }
    bundle = run_restrict(dm_roles, dm_path / "network.yaml", beta)
    result = run_identify(scored_dm.frame, scored_dm.roles, bundle)
    assert result.beta_values["m_high"] == pytest.approx(-0.6, abs=1e-9)
    assert result.beta_values["m_slop"] == pytest.approx(0.8, abs=1e-9)


def test_diff_means_default_sign_is_positive(scored_dm, dm_roles, dm_path) -> None:
    beta = {
        "schema_version": "1",
        "type": "diff_means",
        "outcome": "y",
        "params": {"group": "group"},  # no sign → +1
    }
    bundle = run_restrict(dm_roles, dm_path / "network.yaml", beta)
    result = run_identify(scored_dm.frame, scored_dm.roles, bundle)
    assert result.beta_values["m_high"] == pytest.approx(0.6, abs=1e-9)


def test_diff_means_missing_group_fails_at_restrict(dm_path: Path, dm_roles) -> None:
    beta = {
        "schema_version": "1",
        "type": "diff_means",
        "outcome": "y",
        "params": {},
    }
    with pytest.raises(RestrictError, match="group"):
        run_restrict(dm_roles, dm_path / "network.yaml", beta)


def test_diff_means_missing_group_column_fails_at_restrict(
    dm_path: Path, dm_roles
) -> None:
    beta = {
        "schema_version": "1",
        "type": "diff_means",
        "outcome": "y",
        "params": {"group": "not_a_column"},
    }
    with pytest.raises(RestrictError, match="not found|group"):
        run_restrict(dm_roles, dm_path / "network.yaml", beta)


def test_diff_means_non_binary_group_fails_loud(scored_dm, dm_roles, dm_path) -> None:
    frame = scored_dm.frame.copy()
    frame["group"] = [1, 1, 1, 1, 1, 2, 2, 2, 2, 2]  # not {0,1}
    beta = BetaSpec(
        type="diff_means", outcome="y", params={"group": "group", "sign": 1}
    )
    with pytest.raises((IdentifyError, SlackError), match="binary|0/1|group"):
        # Direct evaluator path (bind already passed on roles with group present)
        evaluate_beta(frame, "m_high", beta)


def test_diff_means_direct_evaluator(scored_dm) -> None:
    beta = BetaSpec(
        type="diff_means", outcome="y", params={"group": "group", "sign": 1}
    )
    assert evaluate_beta(scored_dm.frame, "m_high", beta) == pytest.approx(
        0.6, abs=1e-9
    )
    assert evaluate_beta(scored_dm.frame, "m_slop", beta) == pytest.approx(
        -0.8, abs=1e-9
    )
