"""Slack evaluators for the v1.0 restriction subset used by mini_v1.

Only ``corr_min`` and ``corr_sign`` are implemented for the thin spine.
Other registered types fail loud until a fixture demands them.
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

    raise SlackError(
        f"restriction type {t!r} has no evaluator in v1.0 thin spine "
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
    return pd.DataFrame(data, index=list(measures))
