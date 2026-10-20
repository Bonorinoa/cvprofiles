"""Inference layer (v1.1/v2.0/v3): bootstrap + θ-grid + δ-grid + coverage band
+ conservative confidence region (DECISIONS 2026-10-20)."""

from __future__ import annotations

from cvprofiles.inference.bootstrap import (
    BootstrapError,
    BootstrapResult,
    bootstrap_payload,
    run_bootstrap,
)
from cvprofiles.inference.confidence_region import (
    ConfidenceRegionError,
    ConfidenceRegionResult,
    compute_confidence_region,
    confidence_region_payload,
)
from cvprofiles.inference.coverage import (
    BoundaryRow,
    CoverageError,
    CoverageResult,
    compute_coverage,
    coverage_payload,
)
from cvprofiles.inference.theta_grid import (
    ThetaGridError,
    ThetaGridResult,
    ThetaGridRow,
    run_theta_grid,
    theta_grid_payload,
)

__all__ = [
    "BoundaryRow",
    "BootstrapError",
    "BootstrapResult",
    "ConfidenceRegionError",
    "ConfidenceRegionResult",
    "CoverageError",
    "CoverageResult",
    "ThetaGridError",
    "ThetaGridResult",
    "ThetaGridRow",
    "bootstrap_payload",
    "compute_confidence_region",
    "confidence_region_payload",
    "compute_coverage",
    "coverage_payload",
    "run_bootstrap",
    "run_theta_grid",
    "theta_grid_payload",
]
