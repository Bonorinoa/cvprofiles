"""Holdout stage machinery (v3 P4a; docs/12 2026-08-08; gates H_holdout_stage).

Freeze rule: stage=None is omitted from network_hash dump so mini golden
stays bit-stable. Explicit stage=holdout enters the hash. Admission uses
select-stage restrictions only; holdout-stage slacks are findings.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest
from pydantic import ValidationError

from cvprofiles.freeze import hash_network
from cvprofiles.identify.pipeline import run_identify
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.network import NetworkConfig, RestrictionSpec
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import run_score


@pytest.fixture
def mini_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "mini_v1"


def test_mini_network_hash_stable_after_stage_field(
    mini_network: NetworkConfig, mini_expected_freeze: dict
) -> None:
    """Merge-blocker: adding stage must not move existing network_hash."""
    assert hash_network(mini_network) == mini_expected_freeze["network_hash"]


def test_stage_default_is_none_and_parses_as_select() -> None:
    r = RestrictionSpec(
        id="r1", type="corr_min", theta=0.3, params={"variable": "v_aux"}
    )
    assert r.stage is None
    r2 = RestrictionSpec(
        id="r2",
        type="corr_min",
        theta=0.3,
        params={"variable": "v_aux"},
        stage="select",
    )
    assert r2.stage == "select"
    r3 = RestrictionSpec(
        id="r3",
        type="corr_min",
        theta=0.3,
        params={"variable": "v_aux"},
        stage="holdout",
    )
    assert r3.stage == "holdout"


def test_stage_bad_value_fails() -> None:
    with pytest.raises(ValidationError):
        RestrictionSpec(
            id="r1",
            type="corr_min",
            theta=0.3,
            params={"variable": "v_aux"},
            stage="train",  # type: ignore[arg-type]
        )


def test_explicit_holdout_stage_moves_network_hash(
    mini_network: NetworkConfig, mini_expected_freeze: dict
) -> None:
    """Isolate stage: same restrictions, one flipped to holdout + one select kept."""
    # Two-restriction network: first holdout, second select (same as mini's second).
    # Compared to mini (both select-by-omission), hash must move solely due to stage.
    raw = mini_network.model_dump(mode="json")
    raw["restrictions"][0]["stage"] = "holdout"
    # second restriction stays stage=None (select); no extra restriction added
    moved = NetworkConfig.model_validate(raw)
    assert hash_network(moved) != mini_expected_freeze["network_hash"]
    # And the freeze dump must serialize stage=holdout for the first restriction
    from cvprofiles.freeze import hash_canonical_json

    # After freeze normalization, holdout stage must remain
    # (hash_network applies the pop-None rule)
    assert hash_network(moved) == hash_canonical_json(
        _network_freeze_payload(moved)
    )


def _network_freeze_payload(network: NetworkConfig) -> dict:
    """Mirror freeze.hash_network dump rule for assertion helpers."""
    payload = network.model_dump(mode="json")
    if payload.get("empty_R") is False:
        payload.pop("empty_R", None)
    for r in payload.get("restrictions", []):
        if r.get("stage") is None:
            r.pop("stage", None)
    return payload


def test_holdout_only_network_fails_at_restrict(
    mini_path: Path, mini_roles: ScoreColumnRoles
) -> None:
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_holdout_only",
                "type": "corr_min",
                "theta": 0.5,
                "params": {"variable": "v_aux"},
                "stage": "holdout",
            }
        ],
    }
    with pytest.raises(RestrictError, match="select|holdout-only|degenerate"):
        run_restrict(mini_roles, raw, mini_path / "beta.yaml")


def test_select_only_admission_ignores_holdout_stage_failures(
    mini_path: Path, mini_roles: ScoreColumnRoles, mini_scores_df: pd.DataFrame
) -> None:
    """Holdout-stage restriction can fail without rejecting from M*."""
    scored = run_score(mini_scores_df, mini_roles, policy="none")
    # Select: very weak bar (all admit). Holdout: impossible bar (all fail).
    raw = {
        "schema_version": "1",
        "name": "stage_split_v1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_select_weak",
                "type": "corr_min",
                "theta": -1.0,
                "params": {"variable": "v_aux"},
                "stage": "select",
            },
            {
                "id": "r_holdout_harsh",
                "type": "corr_min",
                "theta": 2.0,  # impossible — structural fail, not knife-edge
                "params": {"variable": "v_aux"},
                "stage": "holdout",
            },
        ],
    }
    bundle = run_restrict(mini_roles, raw, mini_path / "beta.yaml")
    result = run_identify(scored.frame, scored.roles, bundle)
    # All menu measures should admit (select bar is -1)
    assert set(result.admissible) == set(scored.roles.measures)
    # Holdout failures are findings, not selection rejections
    assert "r_holdout_harsh" not in {
        rid for fails in result.rejected.values() for rid in fails
    }
    # Verdict payload present
    assert result.holdout_verdict is not None
    # Every measure should fail the harsh holdout restriction
    for m in scored.roles.measures:
        assert "r_holdout_harsh" in result.holdout_verdict.get(m, [])


def test_holdout_stage_slacks_still_computed(
    mini_path: Path, mini_roles: ScoreColumnRoles, mini_scores_df: pd.DataFrame
) -> None:
    scored = run_score(mini_scores_df, mini_roles, policy="none")
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_select",
                "type": "corr_min",
                "theta": -1.0,
                "params": {"variable": "v_aux"},
            },
            {
                "id": "r_holdout",
                "type": "corr_min",
                "theta": 0.0,
                "params": {"variable": "v_aux"},
                "stage": "holdout",
            },
        ],
    }
    bundle = run_restrict(mini_roles, raw, mini_path / "beta.yaml")
    result = run_identify(scored.frame, scored.roles, bundle)
    assert "r_holdout" in result.slacks.columns
    assert "r_select" in result.slacks.columns


def test_legacy_network_without_stage_unchanged(
    mini_roles: ScoreColumnRoles,
    mini_scores_df: pd.DataFrame,
    mini_network: NetworkConfig,
    mini_beta,
) -> None:
    """Omitted stage behaves exactly as pre-P4 admission."""
    scored = run_score(mini_scores_df, mini_roles, policy="none")
    bundle = run_restrict(mini_roles, mini_network, mini_beta)
    result = run_identify(scored.frame, scored.roles, bundle)
    # Mini oracle: m_good and m_weak admit; m_slop rejected
    assert "m_good" in result.admissible
    assert "m_weak" in result.admissible
    assert "m_slop" in result.rejected
    assert result.holdout_verdict is None or result.holdout_verdict == {}
