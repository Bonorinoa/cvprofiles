"""Slack evaluators for the restriction registry.

Implemented: ``corr_min``, ``corr_sign``, ``mean_order``, ``rank_agree``,
``corr_zero``, ``monotone_rank``. Schema-only (``stability``) fails loud until
a fixture demands it.
"""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from cvprofiles.schemas.network import RestrictionSpec


class SlackError(ValueError):
    """Loud slack evaluation failure."""


def pearson_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Pearson correlation; fail loud on non-finite or zero-variance."""
    if len(x) != len(y):
        raise SlackError("corr length mismatch")
    if len(x) < 2:
        raise SlackError("corr requires n >= 2")
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise SlackError("corr inputs must be finite")
    # np.corrcoef is the package path (not museum)
    c = np.corrcoef(x, y)[0, 1]
    if not math.isfinite(float(c)):
        raise SlackError("corr produced non-finite result (zero variance?)")
    return float(c)


def spearman_corr(x: np.ndarray, y: np.ndarray) -> float:
    """Spearman rank correlation (ties get average ranks); fail loud.

    Ranking via pandas Series.rank(method='average') — pandas is a core dep
    with type stubs (scipy.stats has none under strict mypy).
    """
    if not np.isfinite(x).all() or not np.isfinite(y).all():
        raise SlackError("spearman inputs must be finite")
    rx = pd.Series(x).rank(method="average").to_numpy(dtype=float)
    ry = pd.Series(y).rank(method="average").to_numpy(dtype=float)
    return pearson_corr(rx, ry)


def evaluate_slack(
    measure: np.ndarray,
    frame: pd.DataFrame,
    restriction: RestrictionSpec,
) -> float:
    """Sample slack s_r(m). Satisfied when s_r >= -delta (delta applied by caller)."""
    t = restriction.type
    theta = float(restriction.theta)
    p = restriction.params

    if t == "corr_min":
        var = str(p["variable"])
        if var not in frame.columns:
            raise SlackError(f"missing variable column {var!r}")
        c = pearson_corr(measure, frame[var].to_numpy(dtype=float))
        return c - theta

    if t == "corr_sign":
        var = str(p["variable"])
        sign = p.get("sign")
        if sign not in (-1, 1, -1.0, 1.0):
            raise SlackError("corr_sign requires sign in {+1,-1}")
        sign_f = float(sign)
        if var not in frame.columns:
            raise SlackError(f"missing variable column {var!r}")
        c = pearson_corr(measure, frame[var].to_numpy(dtype=float))
        return sign_f * c - theta

    if t == "mean_order":
        # v2.0 thread b (docs/12 2026-08-05 D3): binary 0/1 indicator group;
        # slack = sign*(mean(m|g=1) - mean(m|g=0)) - theta.
        group = str(p["group"])
        if group not in frame.columns:
            raise SlackError(f"missing group column {group!r}")
        sign_f = float(p.get("sign", 1))
        if sign_f not in (1.0, -1.0):
            raise SlackError("mean_order requires params.sign in {+1,-1}")
        if not np.isfinite(measure).all():
            raise SlackError("mean_order measure must be finite")
        g = frame[group].to_numpy(dtype=float)
        if not np.isfinite(g).all():
            raise SlackError(f"group column {group!r} must be finite")
        vals = np.unique(g)
        if not (vals.size == 2 and set(vals) == {0.0, 1.0}):
            raise SlackError(
                f"group column {group!r} must be a binary 0/1 indicator "
                f"(got unique values {list(vals)})"
            )
        in_group = g == 1.0
        mean_in = float(np.mean(measure[in_group]))
        mean_out = float(np.mean(measure[~in_group]))
        return sign_f * (mean_in - mean_out) - theta

    if t == "rank_agree":
        # v2.0 thread b (docs/12 2026-08-05 D4): Spearman ρ vs ref_measure.
        ref = str(p["ref_measure"])
        if ref not in frame.columns:
            raise SlackError(f"missing ref_measure column {ref!r}")
        rho = spearman_corr(measure, frame[ref].to_numpy(dtype=float))
        return rho - theta

    if t == "corr_zero":
        # v3 P2 (docs/12 2026-08-08): two-sided discriminant.
        # slack = theta - |Corr(m, V)|; admit when |corr| is small enough.
        var = str(p["variable"])
        if var not in frame.columns:
            raise SlackError(f"missing variable column {var!r}")
        c = pearson_corr(measure, frame[var].to_numpy(dtype=float))
        return theta - abs(c)

    if t == "monotone_rank":
        # v3 P2: monotone-in-continuous-covariate via Spearman.
        # slack = sign * Spearman(m, V_cont) - theta.
        var = str(p["variable"])
        if var not in frame.columns:
            raise SlackError(f"missing variable column {var!r}")
        sign_f = float(p.get("sign", 1))
        if sign_f not in (1.0, -1.0):
            raise SlackError("monotone_rank requires params.sign in {+1,-1}")
        rho = spearman_corr(measure, frame[var].to_numpy(dtype=float))
        return sign_f * rho - theta

    raise SlackError(
        f"restriction type {t!r} has no evaluator in the v3 registry "
        f"(schema-only until a fixture demands it)"
    )


def slack_matrix(
    frame: pd.DataFrame,
    measures: list[str],
    restrictions: list[RestrictionSpec],
) -> pd.DataFrame:
    """Return DataFrame index=measures, columns=restriction ids, values=slacks."""
    data: dict[str, list[float]] = {r.id: [] for r in restrictions}
    for m in measures:
        if m not in frame.columns:
            raise SlackError(f"missing measure column {m!r}")
        mvec = frame[m].to_numpy(dtype=float)
        for r in restrictions:
            data[r.id].append(evaluate_slack(mvec, frame, r))
    if not restrictions:
        # empty_R: admit-all path; keep a measures index with zero columns
        return pd.DataFrame(index=list(measures))
    return pd.DataFrame(data, index=list(measures))
