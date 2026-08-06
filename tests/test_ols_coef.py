"""ols_coef beta evaluator tests (v2.0 thread b, M-b3; docs/12 2026-08-05 D5).

Semantics: β = standardized OLS coefficient on m with params.controls
(all columns z-scored ddof=0, matching SCORE's zscore convention; numpy
closed form); singular design / non-finite / zero-variance fail loud.

Fixture ols_v1 (hand-computed): c=1..10, m_conf=c^2, y=2c+m_conf exactly.
  sd_c  = sqrt(8.25)   ≈ 2.8723
  sd_m  = sqrt(1051.05)≈ 32.420
  sd_y  = sqrt(1447.05)≈ 38.040
  standardized beta on m_conf (control c) = sd_m/sd_y ≈ 0.85227
  marginal corr(m_conf, y) ≈ 0.9994 > beta (confound adjustment)
  corr(m_conf, c) ≈ 0.9746 >= 0.5 -> admitted; corr(m_slop, c) ≈ 0.297 -> rejected
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.identify.slacks import pearson_corr
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import load_roles, run_score


@pytest.fixture
def ols_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "ols_v1"


@pytest.fixture
def ols_roles(ols_path: Path) -> ScoreColumnRoles:
    return load_roles(ols_path / "roles.json")


@pytest.fixture
def scored_ols(ols_path: Path, ols_roles: ScoreColumnRoles):
    return run_score(pd.read_csv(ols_path / "scores.csv"), ols_roles, policy="none")


@pytest.fixture
def restrict_ols(ols_path: Path, ols_roles: ScoreColumnRoles):
    return run_restrict(ols_roles, ols_path / "network.yaml", ols_path / "beta.yaml")


def test_ols_coef_beta_matches_hand_golden(scored_ols, restrict_ols) -> None:
    result = run_identify(scored_ols.frame, scored_ols.roles, restrict_ols)
    assert set(result.admissible) == {"m_conf"}
    assert result.point_id is True
    beta_m = result.beta_values["m_conf"]
    assert beta_m == pytest.approx(0.85227, abs=1e-4)
    assert result.range_L == pytest.approx(beta_m, abs=1e-12)
    assert result.range_U == pytest.approx(beta_m, abs=1e-12)


def test_ols_coef_adjusts_for_confound(scored_ols, restrict_ols) -> None:
    result = run_identify(scored_ols.frame, scored_ols.roles, restrict_ols)
    r_ym = pearson_corr(
        scored_ols.frame["m_conf"].to_numpy(dtype=float),
        scored_ols.frame["y"].to_numpy(dtype=float),
    )
    assert r_ym > result.beta_values["m_conf"] + 0.05


def test_ols_coef_empty_controls_fails_at_evaluate(
    ols_path: Path, ols_roles, scored_ols
) -> None:
    net = ols_path / "network.yaml"
    beta = {"schema_version": "1", "type": "ols_coef", "outcome": "y", "params": {}}
    bundle = run_restrict(ols_roles, net, beta)
    with pytest.raises(IdentifyError, match="controls"):
        run_identify(scored_ols.frame, scored_ols.roles, bundle)


def test_ols_coef_missing_control_column_fails_at_restrict(
    ols_path: Path, ols_roles
) -> None:
    beta = {
        "schema_version": "1",
        "type": "ols_coef",
        "outcome": "y",
        "params": {"controls": ["does_not_exist"]},
    }
    with pytest.raises(RestrictError, match="control"):
        run_restrict(ols_roles, ols_path / "network.yaml", beta)


def test_ols_coef_singular_design_fails_loud() -> None:
    # m_dup == c exactly -> [1, c, m_dup] is singular
    df = pd.DataFrame(
        {
            "unit_id": ["a", "b", "c", "d", "e"],
            "m_dup": [1.0, 2.0, 3.0, 4.0, 5.0],
            "c": [1.0, 2.0, 3.0, 4.0, 5.0],
            "v": [1.0, 2.0, 3.0, 4.0, 5.0],
            "y": [1.0, 4.0, 9.0, 16.0, 25.0],
        }
    )
    roles = ScoreColumnRoles(
        unit_id="unit_id",
        measures=["m_dup"],
        aux=["c", "v"],
        outcome="y",
        diagnostic=[],
    )
    net = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_v",
                "type": "corr_sign",
                "theta": 0.5,
                "params": {"variable": "v", "sign": 1},
            }
        ],
    }
    beta = {
        "schema_version": "1",
        "type": "ols_coef",
        "outcome": "y",
        "params": {"controls": ["c"]},
    }
    bundle = run_restrict(roles, net, beta)
    with pytest.raises(IdentifyError, match="singular"):
        run_identify(df, roles, bundle)


def test_ols_coef_zero_variance_control_fails_loud() -> None:
    df = pd.DataFrame(
        {
            "unit_id": ["a", "b", "c", "d", "e"],
            "m": [2.0, 4.0, 6.0, 8.0, 10.0],
            "v": [1.0, 2.0, 3.0, 4.0, 5.0],
            "c": [5.0, 5.0, 5.0, 5.0, 5.0],  # constant control
            "y": [3.0, 6.0, 9.0, 12.0, 15.0],
        }
    )
    roles = ScoreColumnRoles(
        unit_id="unit_id",
        measures=["m"],
        aux=["v", "c"],
        outcome="y",
        diagnostic=[],
    )
    net = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_v",
                "type": "corr_sign",
                "theta": 0.5,
                "params": {"variable": "v", "sign": 1},
            }
        ],
    }
    beta = {
        "schema_version": "1",
        "type": "ols_coef",
        "outcome": "y",
        "params": {"controls": ["c"]},
    }
    bundle = run_restrict(roles, net, beta)
    with pytest.raises(IdentifyError, match="variance"):
        run_identify(df, roles, bundle)
