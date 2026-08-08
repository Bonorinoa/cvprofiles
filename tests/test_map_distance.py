"""map_distance beta evaluator tests (v3 P3; gate H_beta_map).

Semantics (docs/12 2026-08-08): measure-dependent 2D Euclidean distance.
  β(m) = ||z̄(m) − z_target||₂
  z̄(m) = mean_i (x_i(m) @ L)
  item columns resolved as ``{measure}__{item_id}``.

Fixture map_distance_v1 (K=2, L=I₂, target=[0,0], n=2):
  m_close items always [0,0] → z̄=[0,0] → β=0.0
  m_far   items always [3,4] → z̄=[3,4] → β=5.0
  range = [0.0, 5.0] when both admit.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.freeze import hash_beta
from cvprofiles.identify.beta_fn import evaluate_beta
from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.identify.slacks import SlackError
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import load_roles, run_score


@pytest.fixture
def md_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "map_distance_v1"


@pytest.fixture
def md_roles(md_path: Path) -> ScoreColumnRoles:
    return load_roles(md_path / "roles.json")


@pytest.fixture
def scored_md(md_path: Path, md_roles: ScoreColumnRoles):
    return run_score(pd.read_csv(md_path / "scores.csv"), md_roles, policy="none")


@pytest.fixture
def restrict_md(md_path: Path, md_roles: ScoreColumnRoles):
    return run_restrict(md_roles, md_path / "network.yaml", md_path / "beta.yaml")


def test_map_distance_hand_golden_betas(scored_md, restrict_md) -> None:
    result = run_identify(scored_md.frame, scored_md.roles, restrict_md)
    assert set(result.admissible) == {"m_close", "m_far"}
    assert result.beta_values["m_close"] == pytest.approx(0.0, abs=1e-12)
    assert result.beta_values["m_far"] == pytest.approx(5.0, abs=1e-12)
    assert result.range_L == pytest.approx(0.0, abs=1e-12)
    assert result.range_U == pytest.approx(5.0, abs=1e-12)
    assert result.point_id is False


def test_map_distance_direct_evaluator(scored_md) -> None:
    beta = BetaSpec(
        type="map_distance",
        outcome="y",
        params={
            "items": ["A", "B"],
            "loadings": [[1.0, 0.0], [0.0, 1.0]],
            "target": [0.0, 0.0],
        },
    )
    assert evaluate_beta(scored_md.frame, "m_close", beta) == pytest.approx(
        0.0, abs=1e-12
    )
    assert evaluate_beta(scored_md.frame, "m_far", beta) == pytest.approx(
        5.0, abs=1e-12
    )


def test_map_distance_loadings_change_moves_beta_and_hash(
    scored_md, md_roles, md_path
) -> None:
    beta_a = {
        "schema_version": "1",
        "type": "map_distance",
        "outcome": "y",
        "params": {
            "items": ["A", "B"],
            "loadings": [[1.0, 0.0], [0.0, 1.0]],
            "target": [0.0, 0.0],
        },
    }
    beta_b = {
        "schema_version": "1",
        "type": "map_distance",
        "outcome": "y",
        "params": {
            "items": ["A", "B"],
            "loadings": [[2.0, 0.0], [0.0, 2.0]],  # scale L by 2
            "target": [0.0, 0.0],
        },
    }
    bundle_a = run_restrict(md_roles, md_path / "network.yaml", beta_a)
    bundle_b = run_restrict(md_roles, md_path / "network.yaml", beta_b)
    assert bundle_a.beta_hash != bundle_b.beta_hash
    assert hash_beta(bundle_a.beta) == bundle_a.beta_hash

    res_a = run_identify(scored_md.frame, scored_md.roles, bundle_a)
    res_b = run_identify(scored_md.frame, scored_md.roles, bundle_b)
    # m_far with L=2I: z̄=[6,8], d=10
    assert res_a.beta_values["m_far"] == pytest.approx(5.0, abs=1e-12)
    assert res_b.beta_values["m_far"] == pytest.approx(10.0, abs=1e-12)


def test_map_distance_missing_item_column_fails_at_restrict(
    md_path: Path, md_roles
) -> None:
    beta = {
        "schema_version": "1",
        "type": "map_distance",
        "outcome": "y",
        "params": {
            "items": ["A", "MISSING"],
            "loadings": [[1.0, 0.0], [0.0, 1.0]],
            "target": [0.0, 0.0],
        },
    }
    with pytest.raises(RestrictError, match="item|not found|MISSING"):
        run_restrict(md_roles, md_path / "network.yaml", beta)


def test_map_distance_bad_loadings_shape_fails_at_restrict(
    md_path: Path, md_roles
) -> None:
    beta = {
        "schema_version": "1",
        "type": "map_distance",
        "outcome": "y",
        "params": {
            "items": ["A", "B"],
            "loadings": [[1.0, 0.0]],  # K mismatch
            "target": [0.0, 0.0],
        },
    }
    with pytest.raises(RestrictError, match="loadings|shape|length"):
        run_restrict(md_roles, md_path / "network.yaml", beta)


def test_map_distance_bad_target_fails_at_restrict(md_path: Path, md_roles) -> None:
    beta = {
        "schema_version": "1",
        "type": "map_distance",
        "outcome": "y",
        "params": {
            "items": ["A", "B"],
            "loadings": [[1.0, 0.0], [0.0, 1.0]],
            "target": [0.0],  # not length 2
        },
    }
    with pytest.raises(RestrictError, match="target"):
        run_restrict(md_roles, md_path / "network.yaml", beta)


def test_map_distance_missing_items_fails_at_restrict(md_path: Path, md_roles) -> None:
    beta = {
        "schema_version": "1",
        "type": "map_distance",
        "outcome": "y",
        "params": {
            "loadings": [[1.0, 0.0], [0.0, 1.0]],
            "target": [0.0, 0.0],
        },
    }
    with pytest.raises(RestrictError, match="items"):
        run_restrict(md_roles, md_path / "network.yaml", beta)


def test_map_distance_nonfinite_items_fail_loud(scored_md) -> None:
    frame = scored_md.frame.copy()
    frame.loc[0, "m_far__A"] = float("nan")
    beta = BetaSpec(
        type="map_distance",
        outcome="y",
        params={
            "items": ["A", "B"],
            "loadings": [[1.0, 0.0], [0.0, 1.0]],
            "target": [0.0, 0.0],
        },
    )
    with pytest.raises((IdentifyError, SlackError), match="finite|non-finite|NaN"):
        evaluate_beta(frame, "m_far", beta)
