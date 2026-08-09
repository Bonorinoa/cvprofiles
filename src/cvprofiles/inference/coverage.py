"""Coverage uncertainty band (v3 P5; semantics LOCKED in docs/12, 2026-08-08).

Contract:
- The coverage block derives from the SAME per-replicate samples as
  ``bootstrap.json`` — ``compute_coverage`` consumes a ``BootstrapResult``;
  there is exactly one resampling loop, no second RNG stream, no RNG-state
  divergence. Replay equivalence: same bundle + same seed ⇒ identical bands.
- Honest label: "uncertainty band". NEVER "confidence interval", "coverage
  guarantee", or "CI". A formal coverage theorem under arbitrary selection
  coupling is deferred (Rev 3 non-goal).
- The band is selection uncertainty on the pooled sample: bootstrap
  replicates admit on select-stage restrictions only (P4 lock §3); the
  holdout verdict is a full-sample point finding OUTSIDE the band. Explicitly
  NOT a holdout-robustness band.
- Per-side alpha/2 quantiles over non-empty replicates, default alpha=0.10
  (band (0.05, 0.95)). ``bootstrap.json`` keeps its v1.1 locked percentile
  pair (0.025, 0.975) — the two artifacts are labeled differently on purpose.
- Boundary attribution: margin_m = min_r s_r(m) over ALL restrictions on the
  pooled full-frame slacks; SE_m = ddof=1 sample SD of per-replicate
  min-slacks across non-empty replicates; boundary iff |margin_m| <= kappa*SE_m
  (amendment cb566c8 — distance from the threshold; far-rejected measures are
  NOT boundary). Default kappa=2.0.
- "Non-empty replicate" = replicate whose overall M*_b is non-empty
  (docs/12 clarification, 2026-08-08). Denominator pinned by
  len(min_slack_samples[m]) == replicates_nonempty.
- p_hat_m = #admitted-in-nonempty-replicate / #non-empty-replicates.
  Descriptive, not a coverage statement. Null when denominator 0.
- All-empty (or < 2 non-empty) ⇒ structured nulls: band null, boundary empty,
  p_hat_m null, note explains. Exit 0.
- alpha/kappa are EXCLUDED from the freeze preimage: same bundle + different
  alpha ⇒ same run_id, different coverage.json. No new FreezeBundle.config
  keys.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd

from cvprofiles.identify.slacks import SlackError, slack_matrix
from cvprofiles.inference.bootstrap import BootstrapResult
from cvprofiles.restrict.pipeline import RestrictBundle
from cvprofiles.schemas.scores import ScoreColumnRoles


class CoverageError(ValueError):
    """Loud coverage failure (bad alpha/kappa; all-empty is NOT an error)."""


@dataclass(frozen=True)
class BoundaryRow:
    """One measure's boundary attribution (|margin| <= kappa * SE)."""

    measure: str
    margin: float
    se: float | None
    kappa: float
    boundary: bool


@dataclass(frozen=True)
class CoverageResult:
    """Coverage uncertainty band output (additive to the headline range)."""

    alpha: float
    kappa: float
    quantiles: tuple[float, float]
    band_L: float | None
    band_U: float | None
    replicates_total: int
    replicates_nonempty: int
    replicates_empty: int
    replicates_degenerate: int
    empty_replicate_rate: float
    degenerate_replicate_rate: float
    boundary: tuple[BoundaryRow, ...]
    p_hat_m: dict[str, float | None]
    note: str | None


def compute_coverage(
    result: BootstrapResult,
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    bundle: RestrictBundle,
    *,
    alpha: float = 0.10,
    kappa: float = 2.0,
) -> CoverageResult:
    """Compute the uncertainty band from an EXISTING BootstrapResult.

    One resampling loop (inside ``run_bootstrap``); this function only reads
    the collected samples. Deterministic in ``result``: no RNG here.
    """
    if not isinstance(result, BootstrapResult):
        raise CoverageError("compute_coverage requires a BootstrapResult")
    if not isinstance(bundle, RestrictBundle):
        raise CoverageError("compute_coverage requires a RestrictBundle")
    a = float(alpha)
    if not (0.0 < a < 1.0):
        raise CoverageError(f"alpha must satisfy 0 < alpha < 1 (got {alpha!r})")
    k = float(kappa)
    if not math.isfinite(k) or k <= 0.0:
        raise CoverageError(f"kappa must be finite and > 0 (got {kappa!r})")

    measures = list(roles.measures)
    q_lo, q_hi = a / 2.0, 1.0 - a / 2.0

    if result.replicates_nonempty == 0:
        band_L: float | None = None
        band_U: float | None = None
        boundary: tuple[BoundaryRow, ...] = ()
        p_hat: dict[str, float | None] = {m: None for m in measures}
        note = (
            "all replicates empty (or degenerate): uncertainty band is null; "
            "boundary set empty; admission frequencies null. Heuristic band — "
            "not a confidence interval and not a holdout-robustness band."
        )
    else:
        band_L = float(np.quantile(np.asarray(result.L_samples), q_lo))
        band_U = float(np.quantile(np.asarray(result.U_samples), q_hi))
        assert result.admission_counts is not None
        p_hat = {
            m: result.admission_counts[m] / result.replicates_nonempty
            for m in measures
        }

        if result.replicates_nonempty < 2:
            boundary = ()
            note = (
                f"fewer than 2 non-empty replicates ({result.replicates_nonempty}): "
                "SE undefined; boundary set empty. Heuristic band — not a "
                "confidence interval and not a holdout-robustness band."
            )
        else:
            try:
                sl = slack_matrix(frame, measures, bundle.network.restrictions)
            except SlackError as exc:
                raise CoverageError(str(exc)) from exc
            margins = sl.min(axis=1)
            rows: list[BoundaryRow] = []
            for m in measures:
                se: float | None = None
                if result.min_slack_samples is not None:
                    samples = result.min_slack_samples[m]
                    if len(samples) >= 2:
                        se = float(np.std(np.asarray(samples, dtype=float), ddof=1))
                margin = float(margins.loc[m])
                boundary_flag = se is not None and abs(margin) <= k * se
                rows.append(
                    BoundaryRow(
                        measure=m,
                        margin=margin,
                        se=se,
                        kappa=k,
                        boundary=boundary_flag,
                    )
                )
            boundary = tuple(rows)
            note = (
                "Heuristic uncertainty band over non-empty bootstrap replicates "
                "(selection uncertainty on the pooled sample; holdout verdict is "
                "a full-sample point finding outside the band). Not a confidence "
                "interval; not a holdout-robustness band. Boundary attribution: "
                "|margin_m| <= kappa * SE_m."
            )

    return CoverageResult(
        alpha=a,
        kappa=k,
        quantiles=(q_lo, q_hi),
        band_L=band_L,
        band_U=band_U,
        replicates_total=result.replicates_total,
        replicates_nonempty=result.replicates_nonempty,
        replicates_empty=result.replicates_empty,
        replicates_degenerate=result.replicates_degenerate,
        empty_replicate_rate=result.empty_replicate_rate,
        degenerate_replicate_rate=result.degenerate_replicate_rate,
        boundary=boundary,
        p_hat_m=p_hat,
        note=note,
    )


def coverage_payload(result: CoverageResult) -> dict[str, Any]:
    """JSON-serializable audit payload (written as coverage.json in E)."""
    return {
        "schema_version": "1",
        "purpose": "coverage_uncertainty_band",
        "alpha": result.alpha,
        "kappa": result.kappa,
        "quantiles": [result.quantiles[0], result.quantiles[1]],
        "band_L": result.band_L,
        "band_U": result.band_U,
        "replicates_total": result.replicates_total,
        "replicates_nonempty": result.replicates_nonempty,
        "replicates_empty": result.replicates_empty,
        "replicates_degenerate": result.replicates_degenerate,
        "empty_replicate_rate": result.empty_replicate_rate,
        "degenerate_replicate_rate": result.degenerate_replicate_rate,
        "boundary": [
            {
                "measure": row.measure,
                "margin": row.margin,
                "se": row.se,
                "kappa": row.kappa,
                "boundary": row.boundary,
            }
            for row in result.boundary
        ],
        "p_hat_m": result.p_hat_m,
        "note": result.note,
        "headline_note": (
            "Headline [L,U] remains min/max B* on the full sample; "
            "the uncertainty band is additive metadata and never replaces it."
        ),
    }
