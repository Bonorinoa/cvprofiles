"""Synthetic DGP suite for package-path gates (eval-only; not paper path).

Museum ``evals/synthetic/v0_poc.py`` is inspiration only — never import it.
"""

from __future__ import annotations

from cvprofiles.synth.battery import (
    BATTERY_VERSION,
    GateResult,
    run_battery,
    write_battery_summary,
)
from cvprofiles.synth.dgp import LABELS, MEASURES, SCENARIOS, make_dgp, roles_for_menu
from cvprofiles.synth.metrics import SeedMetrics, metrics_from_identify
from cvprofiles.synth.oracle_r import beta_corr_y, network_for

__all__ = [
    "BATTERY_VERSION",
    "LABELS",
    "MEASURES",
    "SCENARIOS",
    "GateResult",
    "SeedMetrics",
    "beta_corr_y",
    "make_dgp",
    "metrics_from_identify",
    "network_for",
    "roles_for_menu",
    "run_battery",
    "write_battery_summary",
]
