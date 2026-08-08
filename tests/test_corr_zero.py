"""corr_zero evaluator tests (v3 P2; docs/12 2026-08-08; gate H_disc).

Semantics: params {variable}; slack = theta - |Corr(m, V)|.
Two-sided discriminant: admit when |corr| is small enough (slack >= -delta).

Fixture corr_zero_v1 (hand-computed, n=10; v_conv=0..9, v_disc=[1,-1]*5):
  m_valid  = v_conv           corr_conv=1.0       corr_disc≈-0.1741
             s_min=0.5        s_zero≈0.1259       → admitted
  m_linked = v_disc           corr_conv≈-0.1741   corr_disc=1.0
             s_min≈-0.6741    s_zero=-0.7         → rejected (both)
  m_noise  fixed noise        corr_conv≈0.1154    corr_disc≈-0.1326
             s_min≈-0.3846    s_zero≈0.1674       → rejected by r_corr_min only
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
def cz_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "corr_zero_v1"


@pytest.fixture
def cz_roles(cz_path: Path) -> ScoreColumnRoles:
    return load_roles(cz_path / "roles.json")


@pytest.fixture
def scored_cz(cz_path: Path, cz_roles: ScoreColumnRoles):
    return run_score(pd.read_csv(cz_path / "scores.csv"), cz_roles, policy="none")


@pytest.fixture
def restrict_cz(cz_path: Path, cz_roles: ScoreColumnRoles):
    return run_restrict(cz_roles, cz_path / "network.yaml", cz_path / "beta.yaml")


def test_corr_zero_schema_requires_variable() -> None:
    with pytest.raises(ValidationError, match="variable"):
        RestrictionSpec(id="r1", type="corr_zero", theta=0.3, params={})


def test_corr_zero_schema_accepts_variable() -> None:
    r = RestrictionSpec(
        id="r1", type="corr_zero", theta=0.3, params={"variable": "v_disc"}
    )
    assert r.type == "corr_zero"
    assert r.params["variable"] == "v_disc"


def test_corr_zero_admits_valid_rejects_linked_and_noise(scored_cz, restrict_cz) -> None:
    result = run_identify(scored_cz.frame, scored_cz.roles, restrict_cz)
    assert set(result.admissible) == {"m_valid"}
    assert set(result.rejected) == {"m_linked", "m_noise"}
    # m_linked fails both; m_noise fails only convergent bar
    assert "r_corr_zero_disc" in result.rejected["m_linked"]
    assert "r_corr_min_conv" in result.rejected["m_linked"]
    assert result.rejected["m_noise"] == ["r_corr_min_conv"]


def test_corr_zero_hand_golden_slacks(scored_cz, restrict_cz) -> None:
    result = run_identify(scored_cz.frame, scored_cz.roles, restrict_cz)
    assert result.slacks.at["m_valid", "r_corr_zero_disc"] == pytest.approx(
        0.125922344, abs=1e-6
    )
    assert result.slacks.at["m_linked", "r_corr_zero_disc"] == pytest.approx(
        -0.7, abs=1e-9
    )
    assert result.slacks.at["m_noise", "r_corr_zero_disc"] == pytest.approx(
        0.1673604727, abs=1e-6
    )
    assert result.slacks.at["m_valid", "r_corr_min_conv"] == pytest.approx(0.5, abs=1e-9)
    assert result.slacks.at["m_linked", "r_corr_min_conv"] == pytest.approx(
        -0.674077656, abs=1e-6
    )


def test_corr_zero_direct_evaluator(scored_cz) -> None:
    frame = scored_cz.frame
    r = RestrictionSpec(
        id="r_z", type="corr_zero", theta=0.3, params={"variable": "v_disc"}
    )
    s_valid = evaluate_slack(frame["m_valid"].to_numpy(dtype=float), frame, r)
    s_linked = evaluate_slack(frame["m_linked"].to_numpy(dtype=float), frame, r)
    assert s_valid == pytest.approx(0.125922344, abs=1e-6)
    assert s_linked == pytest.approx(-0.7, abs=1e-9)


def test_corr_zero_missing_variable_fails_at_restrict(
    cz_path: Path, cz_roles: ScoreColumnRoles
) -> None:
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_corr_zero_disc",
                "type": "corr_zero",
                "theta": 0.3,
                "params": {"variable": "not_a_column"},
            }
        ],
    }
    with pytest.raises(RestrictError, match="not found|variable"):
        run_restrict(cz_roles, raw, cz_path / "beta.yaml")


def test_corr_zero_missing_column_at_identify_fails_loud(scored_cz, cz_roles) -> None:
    # Bind passes if column is in roles.diagnostic; force evaluator-side miss by
    # stripping the column from the frame after restrict with a present aux.
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_z",
                "type": "corr_zero",
                "theta": 0.3,
                "params": {"variable": "v_disc"},
            }
        ],
    }
    bundle = run_restrict(cz_roles, raw, {"type": "corr_y", "outcome": "y", "params": {}})
    frame = scored_cz.frame.drop(columns=["v_disc"])
    with pytest.raises(IdentifyError, match="missing variable|v_disc"):
        run_identify(frame, scored_cz.roles, bundle)
