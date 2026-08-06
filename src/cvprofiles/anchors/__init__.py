"""θ-anchor documentation discipline (v2.0 thread c).

Pre-data anchors as a first-class schema'd artifact: one anchor per
restriction id, hashed for provenance (anchors_hash), excluded from the
freeze preimage. "Pre-data" is a process commitment — the engine enforces
completeness + hash, never timing.
"""

from cvprofiles.anchors.pipeline import (
    AnchorError,
    AnchorsConfig,
    ThetaAnchor,
    anchors_hash,
    anchors_payload,
    parse_anchors,
    validate_completeness,
)

__all__ = [
    "AnchorError",
    "AnchorsConfig",
    "ThetaAnchor",
    "anchors_hash",
    "anchors_payload",
    "parse_anchors",
    "validate_completeness",
]
