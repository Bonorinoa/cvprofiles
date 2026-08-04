"""Inference layer (v1.1): bootstrap over units + θ-grid sensitivity surface."""

from __future__ import annotations

from cvprofiles.inference.bootstrap import (
    BootstrapError,
    BootstrapResult,
    bootstrap_payload,
    run_bootstrap,
)
from cvprofiles.inference.theta_grid import (
    ThetaGridError,
    ThetaGridResult,
    ThetaGridRow,
    run_theta_grid,
    theta_grid_payload,
)

__all__ = [
    "BootstrapError",
    "BootstrapResult",
    "ThetaGridError",
    "ThetaGridResult",
    "ThetaGridRow",
    "bootstrap_payload",
    "run_bootstrap",
    "run_theta_grid",
    "theta_grid_payload",
]
