"""Nomological network schemas (RESTRICT input). USER owns content on main path."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

# Known restriction type ids for the v2.0 schema registry.
# Evaluators land in the v2.0 registry; unknown types fail loud at parse time.
RestrictionType = Literal[
    "corr_sign",
    "corr_min",
    "mean_order",
    "rank_agree",
    "stability",
]


class RestrictionSpec(BaseModel):
    """One restriction r ∈ R with threshold θ_r.

    Type-specific fields live in ``params``. Common keys by type (docs/03):
      corr_sign  — variable, sign (+1|-1)
      corr_min   — variable
      mean_order — group
      rank_agree — ref_measure
      stability  — split policy (later)
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    type: RestrictionType
    theta: float
    params: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def _id_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("restriction id must be non-empty")
        return s

    @model_validator(mode="after")
    def _type_params(self) -> RestrictionSpec:
        t = self.type
        p = self.params
        if t in ("corr_sign", "corr_min"):
            if "variable" not in p:
                raise ValueError(f"{t} requires params.variable")
            if t == "corr_sign":
                sign = p.get("sign")
                if sign not in (-1, 1, -1.0, 1.0):
                    raise ValueError("corr_sign requires params.sign in {+1, -1}")
        if t == "mean_order":
            if "group" not in p:
                raise ValueError("mean_order requires params.group")
            sign = p.get("sign", 1)
            if sign not in (-1, 1, -1.0, 1.0):
                raise ValueError("mean_order requires params.sign in {+1,-1}")
        if t == "rank_agree" and "ref_measure" not in p:
            raise ValueError("rank_agree requires params.ref_measure")
        return self


class NetworkConfig(BaseModel):
    """Researcher-authored nomological network R with global slack tolerance δ."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    name: str | None = None
    delta: float = Field(
        default=0.0,
        ge=0.0,
        description="Slack tolerance; admit if s_r >= -delta.",
    )
    restrictions: list[RestrictionSpec] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _unique_ids(self) -> NetworkConfig:
        ids = [r.id for r in self.restrictions]
        if len(ids) != len(set(ids)):
            raise ValueError("restriction ids must be unique")
        return self


def parse_network(data: dict[str, Any]) -> NetworkConfig:
    """Parse and validate a network mapping (e.g. from YAML)."""
    return NetworkConfig.model_validate(data)


# Expose adapter for callers that want JSON-schema tooling later.
NetworkAdapter: TypeAdapter[NetworkConfig] = TypeAdapter(NetworkConfig)

RestrictionList = Annotated[list[RestrictionSpec], Field(min_length=1)]
