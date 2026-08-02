"""Score-matrix column roles and SCORE manifest (ingest contract only)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScoreColumnRoles(BaseModel):
    """Explicit column roles for a unit×measure score table.

    Diagnostic columns (e.g. ``V_star``) may appear in fixtures but are not
    required by the engine and must not be used inside IDENTIFY.
    """

    model_config = ConfigDict(extra="forbid")

    unit_id: str = "unit_id"
    measures: list[str] = Field(..., min_length=1)
    aux: list[str] = Field(default_factory=list)
    outcome: str | None = None
    diagnostic: list[str] = Field(
        default_factory=list,
        description="Optional columns retained for eval diagnostics only (e.g. V_star).",
    )

    @field_validator("measures", "aux", "diagnostic")
    @classmethod
    def _unique_nonempty_names(cls, v: list[str]) -> list[str]:
        if any(not name or not str(name).strip() for name in v):
            raise ValueError("column names must be non-empty")
        if len(v) != len(set(v)):
            raise ValueError("column names within a role list must be unique")
        return list(v)

    @model_validator(mode="after")
    def _no_role_overlap(self) -> ScoreColumnRoles:
        bags: list[tuple[str, list[str]]] = [
            ("unit_id", [self.unit_id]),
            ("measures", self.measures),
            ("aux", self.aux),
            ("diagnostic", self.diagnostic),
        ]
        if self.outcome is not None:
            bags.append(("outcome", [self.outcome]))
        seen: dict[str, str] = {}
        for role, names in bags:
            for name in names:
                if name in seen:
                    raise ValueError(
                        f"column {name!r} appears in both {seen[name]!r} and {role!r}"
                    )
                seen[name] = role
        return self


class ScoreManifest(BaseModel):
    """Machine-readable SCORE output metadata (M1 schema; filled by M2)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    roles: ScoreColumnRoles
    n_rows: int = Field(..., ge=1)
    n_measures: int = Field(..., ge=1)
    measure_columns: list[str] = Field(..., min_length=1)
    normalization: dict[str, Any] = Field(
        default_factory=lambda: {"policy": "none", "zscore_measures": False},
        description="Normalization intent/result. SCORE (M2) applies policy.",
    )
    scores_hash: str | None = Field(
        default=None,
        description="SHA-256 hex of canonical score payload (set at freeze).",
    )
    dtypes: dict[str, str] = Field(default_factory=dict)

    @model_validator(mode="after")
    def _measures_align(self) -> ScoreManifest:
        if self.n_measures != len(self.measure_columns):
            raise ValueError("n_measures must equal len(measure_columns)")
        if list(self.measure_columns) != list(self.roles.measures):
            raise ValueError("measure_columns must match roles.measures exactly (order-sensitive)")
        return self
