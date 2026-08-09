"""Bootstrap over units (v1.1 M6; semantics LOCKED in docs/12, 2026-08-01).

Contract:
- Efron units-only resampling with replacement; the menu (measures) is fixed —
  never resample measures.
- Single ``numpy.random.default_rng(seed)`` stream per call; no global RNG.
  Generator streams are NEP 19 stable, so pinned seeds replay exactly.
- Per replicate: ``run_identify`` (slacks → M* → β → (L_b, U_b)) — the exact
  same admission code path as the headline; no hand-rolled slack logic.
- P4b (docs/12 2026-08-08): per-replicate ``run_identify`` passes
  ``include_holdout_verdict=False`` (selection-only band; holdout verdict is
  a full-sample point finding outside the band).
- Percentile band over NON-EMPTY replicates only. All replicates empty ⇒
  band null + note. Degenerate replicates (resample-induced evaluation
  failure, e.g. zero-variance columns) are counted separately, excluded from
  the band, and never silently dropped. Counting them is safe because the
  headline run already succeeded on the full frame before bootstrap is
  attempted, so config-level errors cannot be replicate-specific.
- The headline ``[L,U] = min/max B*`` on the full sample is NEVER replaced
  here; the band is additive metadata.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.restrict.pipeline import RestrictBundle
from cvprofiles.schemas.scores import ScoreColumnRoles


class BootstrapError(ValueError):
    """Loud bootstrap failure (bad inputs; empty replicates are not errors)."""


@dataclass(frozen=True)
class BootstrapResult:
    """Bootstrap-over-units output (additive to the headline range)."""

    n_boot: int
    seed_used: int
    quantiles: tuple[float, float]
    band_L: float | None
    band_U: float | None
    replicates_total: int
    replicates_nonempty: int
    replicates_empty: int
    replicates_degenerate: int
    empty_replicate_rate: float
    degenerate_replicate_rate: float
    band_method: str
    note: str | None
    L_samples: tuple[float, ...]
    U_samples: tuple[float, ...]


def run_bootstrap(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    restrict: RestrictBundle,
    *,
    n_boot: int,
    seed: int,
    quantiles: tuple[float, float] = (0.025, 0.975),
) -> BootstrapResult:
    """Efron units-only bootstrap percentile band for (L, U).

    Deterministic in ``seed`` (single ``default_rng`` stream). Replicates
    whose M* is empty are counted but excluded from the band; replicates
    whose evaluation fails (resample degeneracy) are counted separately.
    """
    if not isinstance(restrict, RestrictBundle):
        raise BootstrapError("run_bootstrap requires a RestrictBundle")
    n_boot_i = int(n_boot)
    if n_boot_i < 1:
        raise BootstrapError("n_boot must be >= 1 (bootstrap is off when < 1)")
    seed_i = int(seed)
    if seed_i < 0:
        raise BootstrapError("seed must be >= 0")
    q_lo, q_hi = float(quantiles[0]), float(quantiles[1])
    if not (0.0 < q_lo < q_hi < 1.0):
        raise BootstrapError("quantiles must satisfy 0 < q_lo < q_hi < 1")

    n = len(frame)
    if n < 1:
        raise BootstrapError("bootstrap requires a non-empty frame")

    rng = np.random.default_rng(seed_i)

    L_samples: list[float] = []
    U_samples: list[float] = []
    n_empty = 0
    n_degenerate = 0
    for _ in range(n_boot_i):
        # Draw per replicate: same NEP-19 stream as one (n_boot, n) draw
        # (arrays fill in C order) but O(n) memory, not O(n_boot * n).
        row = rng.integers(0, n, size=n)
        frame_b = frame.iloc[row].reset_index(drop=True)
        try:
            res = run_identify(
                frame_b, roles, restrict, include_holdout_verdict=False
            )
        except IdentifyError:
            n_degenerate += 1
            continue
        if res.empty:
            n_empty += 1
            continue
        assert res.range_L is not None and res.range_U is not None  # non-empty ⇒ set
        if not (math.isfinite(res.range_L) and math.isfinite(res.range_U)):
            # Zero-variance resample columns can yield NaN correlations that
            # pass admission but poison the band. Count as degenerate, exclude.
            n_degenerate += 1
            continue
        L_samples.append(float(res.range_L))
        U_samples.append(float(res.range_U))

    nonempty = len(L_samples)
    if nonempty:
        band_L = float(np.quantile(np.asarray(L_samples), q_lo))
        band_U = float(np.quantile(np.asarray(U_samples), q_hi))
        note = None
    else:
        band_L = None
        band_U = None
        note = (
            "all replicates empty (or degenerate): band is null; "
            "headline [L,U] unchanged"
        )

    return BootstrapResult(
        n_boot=n_boot_i,
        seed_used=seed_i,
        quantiles=(q_lo, q_hi),
        band_L=band_L,
        band_U=band_U,
        replicates_total=n_boot_i,
        replicates_nonempty=nonempty,
        replicates_empty=n_empty,
        replicates_degenerate=n_degenerate,
        empty_replicate_rate=n_empty / n_boot_i,
        degenerate_replicate_rate=n_degenerate / n_boot_i,
        band_method="percentile_nonempty",
        note=note,
        L_samples=tuple(L_samples),
        U_samples=tuple(U_samples),
    )


def bootstrap_payload(result: BootstrapResult) -> dict[str, Any]:
    """JSON-serializable audit payload (written as bootstrap.json in E)."""
    return {
        "schema_version": "1",
        "method": "efron_units_only",
        "band_method": result.band_method,
        "quantile_method": "linear",
        "n_boot": result.n_boot,
        "seed": result.seed_used,
        "quantiles": [result.quantiles[0], result.quantiles[1]],
        "band_L": result.band_L,
        "band_U": result.band_U,
        "replicates_total": result.replicates_total,
        "replicates_nonempty": result.replicates_nonempty,
        "replicates_empty": result.replicates_empty,
        "replicates_degenerate": result.replicates_degenerate,
        "empty_replicate_rate": result.empty_replicate_rate,
        "degenerate_replicate_rate": result.degenerate_replicate_rate,
        "note": result.note,
        "headline_note": (
            "Headline [L,U] remains min/max B* on the full sample; "
            "the bootstrap band is additive metadata."
        ),
        "samples": {"L": list(result.L_samples), "U": list(result.U_samples)},
    }
