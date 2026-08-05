"""θ-grid sensitivity surface (v1.1 M6; semantics LOCKED in docs/12, 2026-08-01).

Contract:
- Declared scale multipliers λ ∈ positive reals applied to **all** θ_r
  (thresholds of every restriction). For positive λ, "scale the magnitude"
  and "multiply θ" coincide; the ``sign``/direction params and the slack
  tolerance δ are NEVER scaled.
- Diagnostic sensitivity surface only: per λ → M*, [L,U], empty flag →
  ``theta_grid.json`` (written in the wiring step).
- **Never** auto-select λ (no coverage-chasing, no auto-loosening). The
  headline range is always the declared network, i.e. λ = 1.0, computed
  outside this surface.
- The grid is **not** part of the freeze preimage: it is a diagnostic
  viewport. Same bundle + different grid ⇒ same run_id, different
  ``theta_grid.json``. Off unless explicitly requested.
- The grid is used exactly as declared (validated, sorted ascending);
  λ = 1.0 is not injected. Duplicate λ values fail loud.

Each grid point re-runs the full RESTRICT → IDENTIFY path, so admission on a
scaled network uses the exact same code path as the headline.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import pandas as pd

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.restrict.pipeline import RestrictBundle, run_restrict
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.scores import ScoreColumnRoles


class ThetaGridError(ValueError):
    """Loud θ-grid failure (bad λ declarations; empty rows are not errors)."""


@dataclass(frozen=True)
class ThetaGridRow:
    """One grid point: the IDENTIFY outcome under λ-scaled thresholds."""

    lambda_value: float
    network_hash: str
    thetas: dict[str, float]  # restriction id → scaled θ
    admissible: tuple[str, ...]
    n_admissible: int
    empty: bool
    point_id: bool
    range_L: float | None
    range_U: float | None


@dataclass(frozen=True)
class ThetaGridResult:
    """θ-grid surface output (diagnostic; additive to the headline)."""

    lambdas: tuple[float, ...]  # validated, sorted ascending
    rows: tuple[ThetaGridRow, ...]
    note: str

    def row_for(self, lambda_value: float) -> ThetaGridRow | None:
        for row in self.rows:
            if row.lambda_value == lambda_value:
                return row
        return None


def _validate_lambdas(lambdas: Any) -> list[float]:
    """Validate λ declarations: finite, strictly positive, unique."""
    try:
        seq = list(lambdas)
    except TypeError as exc:
        raise ThetaGridError("theta grid lambdas must be a sequence") from exc
    if not seq:
        raise ThetaGridError("theta grid requires at least one lambda")
    seen: set[float] = set()
    out: list[float] = []
    for raw in seq:
        try:
            lam = float(raw)
        except (TypeError, ValueError) as exc:
            raise ThetaGridError(f"lambda {raw!r} is not a number") from exc
        if not math.isfinite(lam):
            raise ThetaGridError(f"lambda {raw!r} must be finite")
        if lam <= 0.0:
            raise ThetaGridError(f"lambda {raw!r} must be > 0")
        if lam in seen:
            raise ThetaGridError(f"duplicate lambda {raw!r} in theta grid")
        seen.add(lam)
        out.append(lam)
    out.sort()
    return out


def _scale_network(network: NetworkConfig, lam: float) -> NetworkConfig:
    """Return a copy of ``network`` with every θ_r multiplied by ``lam``.

    Only thresholds move: restriction ids/types, ``params`` (including
    ``sign`` direction), and the slack tolerance δ are untouched.
    """
    return network.model_copy(
        deep=True,
        update={
            "restrictions": [
                r.model_copy(update={"theta": float(r.theta) * lam})
                for r in network.restrictions
            ]
        },
    )


def run_theta_grid(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    bundle: RestrictBundle,
    lambdas: Any,
) -> ThetaGridResult:
    """Evaluate the declared network at each λ-scaled threshold vector.

    Deterministic (no RNG). Each grid point re-runs run_restrict +
    run_identify, so rows use the exact same admission path as the headline.
    Empty M* rows are first-class outcomes, not failures.
    """
    if not isinstance(bundle, RestrictBundle):
        raise ThetaGridError("run_theta_grid requires a RestrictBundle")
    lams = _validate_lambdas(lambdas)

    rows: list[ThetaGridRow] = []
    for lam in lams:
        scaled = _scale_network(bundle.network, lam)
        scaled_bundle = run_restrict(roles, scaled, bundle.beta)
        res = run_identify(frame, roles, scaled_bundle)
        rows.append(
            ThetaGridRow(
                lambda_value=lam,
                network_hash=scaled_bundle.network_hash,
                thetas={r.id: float(r.theta) for r in scaled.restrictions},
                admissible=tuple(res.admissible),
                n_admissible=len(res.admissible),
                empty=res.empty,
                point_id=res.point_id,
                range_L=res.range_L,
                range_U=res.range_U,
            )
        )

    return ThetaGridResult(
        lambdas=tuple(lams),
        rows=tuple(rows),
        note=(
            "Diagnostic theta-sensitivity surface only. Headline [L,U] is "
            "always lambda=1.0; lambda is never auto-selected."
        ),
    )


def theta_grid_payload(result: ThetaGridResult) -> dict[str, Any]:
    """JSON-serializable audit payload (written as theta_grid.json in E)."""
    return {
        "schema_version": "1",
        "purpose": "diagnostic_theta_sensitivity",
        "headline_lambda": 1.0,
        "lambda_scales": list(result.lambdas),
        "note": result.note,
        "rows": [
            {
                "lambda": row.lambda_value,
                "network_hash": row.network_hash,
                "thetas": row.thetas,
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
