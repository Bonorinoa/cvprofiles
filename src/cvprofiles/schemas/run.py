"""Run / freeze manifest fragments (determinism contract)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FreezeBundle(BaseModel):
    """Content inputs that define a reproducible engine run (hash preimage pieces)."""

    model_config = ConfigDict(extra="forbid")

    scores_hash: str = Field(..., min_length=64, max_length=64)
    network_hash: str = Field(..., min_length=64, max_length=64)
    beta_hash: str = Field(..., min_length=64, max_length=64)
    package_version: str
    schema_version: str = "1"
    seed: int = Field(default=0, ge=0)
    delta: float = Field(default=0.0, ge=0.0)
    # v1.1: bootstrap over units. Producers must pass normalize_n_boot():
    # < 1 (or None) serializes as JSON null so v1.0-era run_ids stay bit-stable.
    n_boot: int | None = Field(
        default=None,
        description=(
            "Bootstrap replicate count in the freeze preimage. "
            "Normalize with freeze.normalize_n_boot(): < 1 -> None (null), >= 1 -> int."
        ),
    )
    config: dict[str, Any] = Field(
        default_factory=dict,
        description="Extra freeze-relevant knobs (must be JSON-canonical).",
    )


class RunManifest(BaseModel):
    """Written under reports/runs/<run_id>/ for audit (M2+ fills paths/artifacts)."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1"
    run_id: str
    freeze: FreezeBundle
    created_at: str | None = Field(
        default=None,
        description="Wall-clock ISO timestamp; NEVER included in run_id hash.",
    )
    artifact_paths: dict[str, str] = Field(default_factory=dict)
    notes: str | None = None
    # v2.0 thread c: θ-anchor provenance. Excluded from the freeze preimage
    # (docs/12 D4): anchors are documentation, not engine inputs.
    anchors_hash: str | None = Field(
        default=None,
        description="SHA-256 of the validated anchors.yaml (if supplied).",
    )
