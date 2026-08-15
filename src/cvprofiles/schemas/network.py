"""Nomological network schemas (RESTRICT input). USER owns content on main path."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, TypeAdapter, field_validator, model_validator

# Known restriction type ids for the v3 registry.
# Evaluators land when fixtures demand them; unknown types fail loud at parse time.
RestrictionType = Literal[
    "corr_sign",
    "corr_min",
    "mean_order",
    "rank_agree",
    "corr_zero",
    "monotone_rank",
    "stability",
]


class RestrictionSpec(BaseModel):
    """One restriction r ∈ R with threshold θ_r.

    Type-specific fields live in ``params``. Common keys by type:
      corr_sign      — variable, sign (+1|-1)
      corr_min       — variable
      mean_order     — group, sign (+1|-1, default +1)
      rank_agree     — ref_measure
      corr_zero      — variable  (two-sided discriminant: θ − |Corr|)
      monotone_rank  — variable, sign (+1|-1, default +1)
      stability      — split policy (schema-only)
    """

    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1)
    type: RestrictionType
    theta: float
    params: dict[str, Any] = Field(default_factory=dict)
    # P4 (docs/12 2026-08-08): None/omitted = select (admission filter).
    # Explicit "holdout" = compliance finding only (slacks computed, never
    # rejects from M*).
    stage: Literal["select", "holdout"] | None = Field(
        default=None,
        description=(
            "Admission stage: None/'select' gates M*; 'holdout' marks a "
            "finding restriction that never rejects from M*."
        ),
    )

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
        if t in ("corr_sign", "corr_min", "corr_zero"):
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
        if t == "monotone_rank":
            if "variable" not in p:
                raise ValueError("monotone_rank requires params.variable")
            sign = p.get("sign", 1)
            if sign not in (-1, 1, -1.0, 1.0):
                raise ValueError("monotone_rank requires params.sign in {+1,-1}")
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
    empty_R: bool = Field(
        default=False,
        description=(
            "Named unrestricted-multiverse special case. True requires an "
            "empty restriction list and admits every menu measure. Accidental "
            "empty files without this flag still fail loud."
        ),
    )
    restrictions: list[RestrictionSpec] = Field(default_factory=list, min_length=0)

    @model_validator(mode="after")
    def _unique_ids(self) -> NetworkConfig:
        ids = [r.id for r in self.restrictions]
        if len(ids) != len(set(ids)):
            raise ValueError("restriction ids must be unique")
        return self

    @model_validator(mode="after")
    def _empty_r_contract(self) -> NetworkConfig:
        """empty_R is opt-in; an empty list without the flag is still illegal."""
        if self.empty_R and self.restrictions:
            raise ValueError("empty_R=true requires restrictions: []")
        if not self.empty_R and not self.restrictions:
            raise ValueError(
                "empty restrictions require empty_R=true "
                "(unrestricted multiverse is a named special case)"
            )
        return self

    @model_validator(mode="after")
    def _stage_mix_valid(self) -> NetworkConfig:
        """P4 (docs/12 2026-08-08): reject degenerate holdout-only networks.

        A network with >=1 holdout-stage restriction and zero select-stage
        restrictions would admit everything vacuously — not a valid profile.
        Schema-level so every construction path (YAML, dict, API) enforces it.
        empty_R is a different object (no restrictions at all) and is handled
        by _empty_r_contract.
        """
        has_holdout = any(r.stage == "holdout" for r in self.restrictions)
        has_select = any(
            r.stage is None or r.stage == "select" for r in self.restrictions
        )
        if has_holdout and not has_select:
            raise ValueError(
                "degenerate network: >=1 holdout-stage restriction and zero "
                "select-stage restrictions (vacuous admit-all is not a valid "
                "profile)"
            )
        return self


def parse_network(data: dict[str, Any]) -> NetworkConfig:
    """Parse and validate a network mapping (e.g. from YAML)."""
    return NetworkConfig.model_validate(data)


# Expose adapter for callers that want JSON-schema tooling later.
NetworkAdapter: TypeAdapter[NetworkConfig] = TypeAdapter(NetworkConfig)

RestrictionList = Annotated[list[RestrictionSpec], Field(min_length=0)]
