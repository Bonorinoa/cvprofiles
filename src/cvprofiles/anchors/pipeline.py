"""θ-anchor parsing, completeness validation, and provenance hashing.

v2.0 thread c (docs/12 2026-08-05 D4/D6): anchors.yaml is a schema'd
pre-data artifact. One anchor per restriction id; completeness is enforced
against the pinned network. anchors_hash is SHA-256 of canonical JSON and is
**excluded from the freeze preimage** — it is documentation provenance, not
an engine input. "Pre-data" is a process commitment; the engine cannot
verify when a file was written.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from cvprofiles.freeze import hash_canonical_json
from cvprofiles.schemas.network import NetworkConfig

AnchorKind = Literal["literature", "derived", "author"]


class AnchorError(ValueError):
    """Loud anchor failure (parse / schema / completeness)."""


class ThetaAnchor(BaseModel):
    """One pre-data anchor for one restriction r."""

    model_config = ConfigDict(extra="forbid")

    restriction_id: str = Field(..., min_length=1)
    citation_key: str = Field(..., min_length=1)
    source_phrase: str = Field(..., min_length=1)
    anchor_kind: AnchorKind
    pre_data: bool = Field(
        default=True,
        description=(
            "Process commitment flag: anchor declared before data analysis. "
            "The engine cannot verify timing; this is the researcher's record."
        ),
    )

    @field_validator("restriction_id")
    @classmethod
    def _id_strip(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("restriction_id must be non-empty")
        return s


class AnchorsConfig(BaseModel):
    """The full anchor set for one network."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    anchors: list[ThetaAnchor] = Field(..., min_length=1)

    @model_validator(mode="after")
    def _unique_ids(self) -> AnchorsConfig:
        ids = [a.restriction_id for a in self.anchors]
        if len(ids) != len(set(ids)):
            raise ValueError("anchor restriction_ids must be unique")
        return self


def parse_anchors(source: Path | str | dict[str, Any]) -> AnchorsConfig:
    """Load and validate anchors from YAML path or mapping.

    All invalid inputs raise ``AnchorError`` (never raw pydantic at the IO
    boundary), mirroring the RESTRICT pattern.
    """
    if isinstance(source, dict):
        try:
            return AnchorsConfig.model_validate(source)
        except Exception as exc:  # pydantic ValidationError
            raise AnchorError(f"invalid anchors schema: {exc}") from exc
    p = Path(source)
    if not p.is_file():
        raise AnchorError(f"anchors file not found: {p}")
    try:
        raw = yaml.safe_load(p.read_text())
    except yaml.YAMLError as exc:
        raise AnchorError(f"invalid anchors YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise AnchorError("anchors YAML must be a mapping at top level")
    try:
        return AnchorsConfig.model_validate(raw)
    except Exception as exc:  # pydantic ValidationError
        raise AnchorError(f"invalid anchors schema: {exc}") from exc


def validate_completeness(
    config: AnchorsConfig, network: NetworkConfig
) -> AnchorsConfig:
    """Fail loud unless every restriction id has exactly one anchor.

    Unknown anchor ids (not in the network) also fail: an anchor must bind
    to a real restriction.
    """
    net_ids = {r.id for r in network.restrictions}
    anchor_ids = {a.restriction_id for a in config.anchors}
    missing = net_ids - anchor_ids
    if missing:
        raise AnchorError(
            f"missing anchors for restriction(s): {sorted(missing)}"
        )
    unknown = anchor_ids - net_ids
    if unknown:
        raise AnchorError(
            f"anchor restriction_id(s) not in the network: {sorted(unknown)}"
        )
    return config


def anchors_hash(config: AnchorsConfig) -> str:
    """SHA-256 hex of canonical JSON for the validated anchor set.

    Excluded from the freeze preimage by design (docs/12 D4): anchors are
    documentation provenance, not engine inputs.
    """
    return hash_canonical_json(config.model_dump(mode="json"))


def anchors_payload(config: AnchorsConfig) -> dict[str, Any]:
    """JSON-serializable audit payload (anchors.json + report panel)."""
    return {
        "schema_version": "1",
        "anchors_hash": anchors_hash(config),
        "n_anchors": len(config.anchors),
        "anchors": [a.model_dump(mode="json") for a in config.anchors],
    }
