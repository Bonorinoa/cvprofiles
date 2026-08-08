"""Target functional β(·) declaration (RESTRICT input)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

BetaType = Literal["corr_y", "ols_coef", "diff_means"]


class BetaSpec(BaseModel):
    """Named target functional.

    v3 evaluators: ``corr_y``, ``ols_coef``, ``diff_means``.
    ``map_distance`` may be added as a separate registry extension (P3).
    Group/controls binding is enforced at RESTRICT, not schema parse time.
    """

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    type: BetaType = "corr_y"
    outcome: str = Field(default="y", min_length=1)
    params: dict[str, Any] = Field(
        default_factory=dict,
        description=(
            "Type-specific args (e.g. controls for ols_coef, "
            "group/sign for diff_means)."
        ),
    )
