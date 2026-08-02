"""Target functional β(·) declaration (RESTRICT input)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

BetaType = Literal["corr_y", "ols_coef", "diff_means"]


class BetaSpec(BaseModel):
    """Named target functional. v1.0 evaluator implements ``corr_y`` only (M5)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    type: BetaType = "corr_y"
    outcome: str = Field(default="y", min_length=1)
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Type-specific args (e.g. controls for ols_coef, threshold for diff_means).",
    )

    @model_validator(mode="after")
    def _type_params(self) -> BetaSpec:
        if self.type == "diff_means" and "threshold" not in self.params:
            # Allow declaration without threshold at schema time only if omitted;
            # M5 evaluator will fail loud if missing when evaluating.
            pass
        return self
