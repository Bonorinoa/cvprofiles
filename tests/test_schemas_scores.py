"""ScoreColumnRoles / ScoreManifest contract tests (M1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cvprofiles.schemas.scores import ScoreColumnRoles, ScoreManifest


def test_mini_roles_validate(mini_roles: ScoreColumnRoles) -> None:
    assert mini_roles.unit_id == "unit_id"
    assert mini_roles.measures == ["m_good", "m_weak", "m_slop"]
    assert mini_roles.aux == ["v_aux"]
    assert mini_roles.outcome == "y"
    assert mini_roles.diagnostic == ["V_star"]


def test_roles_reject_empty_measures() -> None:
    with pytest.raises(ValidationError):
        ScoreColumnRoles(measures=[])


def test_roles_reject_overlap_outcome_in_measures() -> None:
    with pytest.raises(ValidationError, match="appears in both"):
        ScoreColumnRoles(measures=["m1", "y"], outcome="y")


def test_roles_reject_overlap_aux_measure() -> None:
    with pytest.raises(ValidationError, match="appears in both"):
        ScoreColumnRoles(measures=["m1", "v_aux"], aux=["v_aux"])


def test_roles_reject_duplicate_measure_names() -> None:
    with pytest.raises(ValidationError, match="unique"):
        ScoreColumnRoles(measures=["m1", "m1"])


def test_score_manifest_aligns_measures(mini_roles: ScoreColumnRoles) -> None:
    man = ScoreManifest(
        roles=mini_roles,
        n_rows=10,
        n_measures=3,
        measure_columns=list(mini_roles.measures),
    )
    assert man.n_measures == 3
    assert man.scores_hash is None


def test_score_manifest_rejects_measure_mismatch(mini_roles: ScoreColumnRoles) -> None:
    with pytest.raises(ValidationError):
        ScoreManifest(
            roles=mini_roles,
            n_rows=10,
            n_measures=2,
            measure_columns=["m_good", "m_weak"],
        )


def test_score_manifest_rejects_reordered_measures(mini_roles: ScoreColumnRoles) -> None:
    with pytest.raises(ValidationError, match="measure_columns must match"):
        ScoreManifest(
            roles=mini_roles,
            n_rows=10,
            n_measures=3,
            measure_columns=["m_slop", "m_good", "m_weak"],
        )
