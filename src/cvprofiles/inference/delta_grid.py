"""δ-grid tolerance surface (v2.0 thread a; semantics LOCKED in docs/12, 2026-08-05).

Contract:
- **Absolute δ values** (not multipliers; multiplier semantics degenerate at
  δ=0, the package default). Grid declared as finite, unique, sorted
  ascending, δ >= 0; duplicates fail loud.
- Each grid point re-runs the full IDENTIFY path with a ``delta_override``,
  so rows use the exact same admission code path as the headline. The
  headline is the *declared* δ run, computed outside this surface — the
  same bundle's ``run_identify`` — and is never auto-selected or loosened.
- Diagnostic sensitivity surface only: per δ → M*, [L,U], empty flag →
  ``delta_grid.json`` (written in the wiring step).
- The grid is **not** part of the freeze preimage: it is a diagnostic
  viewport. Same bundle + different grid ⇒ same ``run_id``, different
  ``delta_grid.json``. Off unless explicitly requested.
- δ rows never touch ``network_hash`` / ``beta_hash``: tolerance is an
  IDENTIFY-side override, not a network change (contrast θ-grid, which
  re-scales thresholds and re-hashes the network per row).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pandas as pd

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.restrict.pipeline import RestrictBundle
from cvprofiles.schemas.scores import ScoreColumnRoles


class DeltaGridError(ValueError):
    """Loud δ-grid failure (bad δ declarations; empty rows are not errors)."""


@dataclass(frozen=True)
class DeltaGridRow:
    """One grid point: the IDENTIFY outcome under a tolerance override."""

    delta_value: float
    admissible: tuple[str, ...]
    n_admissible: int
    empty: bool
    point_id: bool
    range_L: float | None
    range_U: float | None


@dataclass(frozen=True)
class DeltaGridResult:
    """δ-grid surface output (diagnostic; additive to the headline)."""

    deltas: tuple[float, ...]  # validated, sorted ascending
    rows: tuple[DeltaGridRow, ...]
    headline_delta: float  # the declared δ from the bundle
    network_hash: str
    beta_hash: str
    note: str

    def row_for(self, delta_value: float) -> DeltaGridRow | None:
        for row in self.rows:
            if row.delta_value == delta_value:
                return row
        return None


def _validate_deltas(deltas: Any) -> list[float]:
    """Validate δ declarations: finite, non-negative, unique."""
    try:
        seq = list(deltas)
    except TypeError as exc:
        raise DeltaGridError("delta grid deltas must be a sequence") from exc
    if not seq:
        raise DeltaGridError("delta grid requires at least one delta")
    seen: set[float] = set()
    out: list[float] = []
    for raw in seq:
        try:
            d = float(raw)
        except (TypeError, ValueError) as exc:
            raise DeltaGridError(f"delta {raw!r} is not a number") from exc
        if not math.isfinite(d):
            raise DeltaGridError(f"delta {raw!r} must be finite")
        if d < 0.0:
            raise DeltaGridError(f"delta {raw!r} must be >= 0")
        if d in seen:
            raise DeltaGridError(f"duplicate delta {raw!r} in delta grid")
        seen.add(d)
        out.append(d)
    out.sort()
    return out


def run_delta_grid(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    bundle: RestrictBundle,
    deltas: Any,
) -> DeltaGridResult:
    """Evaluate the declared network at each absolute tolerance override.

    Deterministic (no RNG). Each grid point re-runs ``run_identify`` with a
    ``delta_override``, so rows use the exact same admission path as the
    headline. Empty M* rows are first-class outcomes, not failures.
    """
    if not isinstance(bundle, RestrictBundle):
        raise DeltaGridError("run_delta_grid requires a RestrictBundle")
    ds = _validate_deltas(deltas)
    headline_delta = float(bundle.delta)

    rows: list[DeltaGridRow] = []
    for d in ds:
        res = run_identify(frame, roles, bundle, delta_override=d)
        rows.append(
            DeltaGridRow(
                delta_value=d,
                admissible=tuple(res.admissible),
                n_admissible=len(res.admissible),
                empty=res.empty,
                point_id=res.point_id,
                range_L=res.range_L,
                range_U=res.range_U,
            )
        )

    return DeltaGridResult(
        deltas=tuple(ds),
        rows=tuple(rows),
        headline_delta=headline_delta,
        network_hash=bundle.network_hash,
        beta_hash=bundle.beta_hash,
        note=(
            "Diagnostic delta-tolerance surface only. Headline [L,U] is always "
            "the declared δ (default 0); δ is never auto-selected."
        ),
    )


def delta_grid_payload(result: DeltaGridResult) -> dict[str, Any]:
    """JSON-serializable audit payload (written as delta_grid.json in M-a3)."""
    return {
        "schema_version": "1",
        "purpose": "diagnostic_delta_tolerance_sensitivity",
        "headline_delta": result.headline_delta,
        "deltas": list(result.deltas),
        "network_hash": result.network_hash,
        "beta_hash": result.beta_hash,
        "note": result.note,
        "rows": [
            {
                "delta": row.delta_value,
                "n_admissible": row.n_admissible,
                "admissible": list(row.admissible),
                "empty": row.empty,
                "point_id": row.point_id,
                "L": row.range_L,
                "U": row.range_U,
            }
            for row in result.rows
        ],
    }
