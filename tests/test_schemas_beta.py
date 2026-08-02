"""BetaSpec contract tests (M1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cvprofiles.schemas.beta import BetaSpec


def test_mini_beta_corr_y(mini_beta: BetaSpec) -> None:
    assert mini_beta.type == "corr_y"
    assert mini_beta.outcome == "y"
    assert mini_beta.params == {}


def test_beta_defaults_to_corr_y() -> None:
    b = BetaSpec()
    assert b.type == "corr_y"
    assert b.outcome == "y"


def test_beta_unknown_type_fails() -> None:
    with pytest.raises(ValidationError):
        BetaSpec(type="not_a_beta")  # type: ignore[arg-type]


def test_beta_extra_field_forbidden() -> None:
    with pytest.raises(ValidationError):
        BetaSpec.model_validate({"type": "corr_y", "outcome": "y", "secret": 1})


def test_ols_coef_allowed_at_schema_level() -> None:
    b = BetaSpec(type="ols_coef", outcome="y", params={"controls": ["z"]})
    assert b.type == "ols_coef"
    assert b.params["controls"] == ["z"]
