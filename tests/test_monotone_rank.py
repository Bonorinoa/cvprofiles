"""monotone_rank evaluator tests (v3 P2; docs/12 2026-08-08; gate H_mono).

Semantics: params {variable, sign} with sign in {+1,-1} (default +1).
slack = sign * Spearman(m, V_cont) - theta.

Note: schema + evaluator co-landed with corr_zero (6721cb7) before this
fixture; this commit pins behavior including the sign=-1 path. TDD
deviation recorded in docs/12.

Fixture monotone_rank_v1 (hand-computed, n=10; v_cont=0..9; θ=0.5, sign=+1):
  m_up    = v_cont           ρ≈1.0   slack≈0.5    → admitted
  m_down  = -v_cont          ρ≈-1.0  slack≈-1.5   → rejected
  m_noise fixed noise        ρ≈0.1394 slack≈-0.3606 → rejected
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.identify.slacks import evaluate_slack
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.network import RestrictionSpec
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import load_roles, run_score


@pytest.fixture
def mr_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "monotone_rank_v1"


@pytest.fixture
def mr_roles(mr_path: Path) -> ScoreColumnRoles:
    return load_roles(mr_path / "roles.json")


@pytest.fixture
def scored_mr(mr_path: Path, mr_roles: ScoreColumnRoles):
    return run_score(pd.read_csv(mr_path / "scores.csv"), mr_roles, policy="none")


@pytest.fixture
def restrict_mr(mr_path: Path, mr_roles: ScoreColumnRoles):
    return run_restrict(mr_roles, mr_path / "network.yaml", mr_path / "beta.yaml")


def test_monotone_rank_schema_requires_variable() -> None:
    with pytest.raises(ValidationError, match="variable"):
        RestrictionSpec(id="r1", type="monotone_rank", theta=0.5, params={})


def test_monotone_rank_schema_bad_sign_fails() -> None:
    with pytest.raises(ValidationError, match="sign"):
        RestrictionSpec(
            id="r1",
            type="monotone_rank",
            theta=0.5,
            params={"variable": "v_cont", "sign": 0},
        )


def test_monotone_rank_schema_default_sign_ok() -> None:
    r = RestrictionSpec(
        id="r1", type="monotone_rank", theta=0.5, params={"variable": "v_cont"}
    )
    assert r.type == "monotone_rank"
    assert r.params.get("sign", 1) == 1


def test_monotone_rank_admits_up_rejects_down_and_noise(scored_mr, restrict_mr) -> None:
    result = run_identify(scored_mr.frame, scored_mr.roles, restrict_mr)
    assert set(result.admissible) == {"m_up"}
    assert set(result.rejected) == {"m_down", "m_noise"}
    assert result.rejected["m_down"] == ["r_mono_up"]
    assert result.rejected["m_noise"] == ["r_mono_up"]


def test_monotone_rank_hand_golden_slacks(scored_mr, restrict_mr) -> None:
    result = run_identify(scored_mr.frame, scored_mr.roles, restrict_mr)
    assert result.slacks.at["m_up", "r_mono_up"] == pytest.approx(0.5, abs=1e-9)
    assert result.slacks.at["m_down", "r_mono_up"] == pytest.approx(-1.5, abs=1e-9)
    assert result.slacks.at["m_noise", "r_mono_up"] == pytest.approx(
        -0.3606060606, abs=1e-6
    )


def test_monotone_rank_sign_negative_admits_down(scored_mr, mr_roles, mr_path) -> None:
    """sign=-1 path: anti-monotone measure should pass when sign flips."""
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_mono_down",
                "type": "monotone_rank",
                "theta": 0.5,
                "params": {"variable": "v_cont", "sign": -1},
            }
        ],
    }
    bundle = run_restrict(mr_roles, raw, mr_path / "beta.yaml")
    result = run_identify(scored_mr.frame, scored_mr.roles, bundle)
    assert "m_down" in result.admissible
    assert "m_up" not in result.admissible
    assert result.slacks.at["m_down", "r_mono_down"] == pytest.approx(0.5, abs=1e-9)
    assert result.slacks.at["m_up", "r_mono_down"] == pytest.approx(-1.5, abs=1e-9)


def test_monotone_rank_direct_evaluator(scored_mr) -> None:
    frame = scored_mr.frame
    r = RestrictionSpec(
        id="r_m",
        type="monotone_rank",
        theta=0.5,
        params={"variable": "v_cont", "sign": 1},
    )
    s_up = evaluate_slack(frame["m_up"].to_numpy(dtype=float), frame, r)
    s_down = evaluate_slack(frame["m_down"].to_numpy(dtype=float), frame, r)
    assert s_up == pytest.approx(0.5, abs=1e-9)
    assert s_down == pytest.approx(-1.5, abs=1e-9)


def test_monotone_rank_missing_variable_fails_at_restrict(
    mr_path: Path, mr_roles: ScoreColumnRoles
) -> None:
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_m",
                "type": "monotone_rank",
                "theta": 0.5,
                "params": {"variable": "not_a_column"},
            }
        ],
    }
    with pytest.raises(RestrictError, match="not found|variable"):
        run_restrict(mr_roles, raw, mr_path / "beta.yaml")


def test_monotone_rank_missing_column_at_identify_fails_loud(
    scored_mr, mr_roles
) -> None:
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_m",
                "type": "monotone_rank",
                "theta": 0.5,
                "params": {"variable": "v_cont"},
            }
        ],
    }
    bundle = run_restrict(
        mr_roles, raw, {"type": "corr_y", "outcome": "y", "params": {}}
    )
    frame = scored_mr.frame.drop(columns=["v_cont"])
    with pytest.raises(IdentifyError, match="missing variable|v_cont"):
        run_identify(frame, scored_mr.roles, bundle)
