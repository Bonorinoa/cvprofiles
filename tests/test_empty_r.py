"""empty_R is a named special case: unrestricted multiverse, not a silent admit-all."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from cvprofiles.freeze import hash_network
from cvprofiles.identify.pipeline import run_identify
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import run_score

_ATOL = 1e-10


def test_empty_restrictions_without_flag_still_fail() -> None:
    with pytest.raises(ValidationError, match="empty_R|restrictions"):
        NetworkConfig(restrictions=[])


def test_empty_r_flag_with_nonempty_restrictions_fails() -> None:
    with pytest.raises(ValidationError, match="empty_R"):
        NetworkConfig(
            empty_R=True,
            restrictions=[
                {
                    "id": "r1",
                    "type": "corr_min",
                    "theta": 0.3,
                    "params": {"variable": "v_aux"},
                }
            ],
        )


def test_empty_r_true_empty_list_validates() -> None:
    net = NetworkConfig(empty_R=True, restrictions=[], name="unrestricted_multiverse")
    assert net.empty_R is True
    assert net.restrictions == []


def test_holdout_only_network_still_illegal() -> None:
    with pytest.raises(ValidationError, match="degenerate"):
        NetworkConfig(
            restrictions=[
                {
                    "id": "r_holdout_only",
                    "type": "corr_min",
                    "theta": 0.5,
                    "params": {"variable": "v_aux"},
                    "stage": "holdout",
                }
            ]
        )


def test_default_empty_r_false_omitted_from_network_hash(
    mini_network: NetworkConfig,
) -> None:
    """Adding empty_R=False must not move pre-3.0.1 network hashes."""
    assert mini_network.empty_R is False
    dumped = mini_network.model_dump(mode="json")
    assert dumped.get("empty_R") is False
    hashed = hash_network(mini_network)
    assert hashed == "3540790e5f4394b08f2d995ea74d064ed5489228fd5c0d34c1d525b07131f921"


def test_empty_r_true_forks_network_hash(mini_network: NetworkConfig) -> None:
    empty = NetworkConfig(empty_R=True, restrictions=[], name=mini_network.name)
    assert hash_network(empty) != hash_network(mini_network)


def test_empty_r_admits_full_menu_and_range_is_full_image(
    mini_dir: Path,
    mini_roles: ScoreColumnRoles,
    mini_scores_df,
) -> None:
    scored = run_score(mini_scores_df, mini_roles, policy="none")
    restrict = run_restrict(
        mini_roles,
        {"schema_version": "1", "empty_R": True, "delta": 0.0, "restrictions": []},
        mini_dir / "beta.yaml",
    )
    result = run_identify(scored.frame, scored.roles, restrict)

    assert result.empty is False
    assert set(result.admissible) == set(mini_roles.measures)
    assert result.admissible == list(mini_roles.measures)
    b_all = [result.beta_values[m] for m in mini_roles.measures]
    assert result.range_L == pytest.approx(min(b_all), abs=_ATOL)
    assert result.range_U == pytest.approx(max(b_all), abs=_ATOL)
    # slop is the designed-invalid; unrestricted range must include it
    assert "m_slop" in result.admissible
    assert result.range_L == pytest.approx(result.beta_values["m_slop"], abs=_ATOL)


def test_empty_list_without_flag_fails_at_restrict(mini_dir: Path, mini_roles) -> None:
    with pytest.raises((RestrictError, ValidationError), match="empty_R|restrictions"):
        run_restrict(
            mini_roles,
            {"schema_version": "1", "delta": 0.0, "restrictions": []},
            mini_dir / "beta.yaml",
        )
