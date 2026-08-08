"""Target functional evaluators (v3: corr_y, ols_coef, diff_means, map_distance)."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from cvprofiles.identify.slacks import SlackError, pearson_corr
from cvprofiles.schemas.beta import BetaSpec


def _zscore(v: np.ndarray) -> np.ndarray:
    """Standardize with ddof=0 (matching SCORE's zscore convention)."""
    sd = float(np.std(v, ddof=0))
    if not math.isfinite(sd) or sd == 0.0:
        raise SlackError("ols_coef requires non-zero variance on all columns")
    return (v - float(np.mean(v))) / sd


def _ols_coef(
    frame: pd.DataFrame, measure: str, outcome: str, controls: list[str]
) -> float:
    """Standardized OLS coefficient on the measure, adjusting for controls.

    numpy closed form: X = [1, z(controls)..., z(measure)], solve X'X b = X'zy.
    β(m) is the last coefficient. No statsmodels dependency (docs/12 D5).
    """
    m = frame[measure].to_numpy(dtype=float)
    if not np.isfinite(m).all():
        raise SlackError("ols_coef measure must be finite")
    zy = _zscore(frame[outcome].to_numpy(dtype=float))
    zc = [_zscore(frame[c].to_numpy(dtype=float)) for c in controls]
    zm = _zscore(m)
    x = np.column_stack([np.ones(len(zy)), *zc, zm])
    try:
        beta = np.linalg.solve(x.T @ x, x.T @ zy)
    except np.linalg.LinAlgError as exc:
        raise SlackError("ols_coef design matrix is singular") from exc
    coef = float(beta[-1])
    if not math.isfinite(coef):
        raise SlackError("ols_coef produced non-finite coefficient")
    return coef


def _diff_means(frame: pd.DataFrame, measure: str, group: str, sign: float) -> float:
    """Group mean gap: sign * (mean(m|G=1) - mean(m|G=0)).

    Group must be a binary 0/1 indicator (same fail-loud pattern as mean_order).
    Outcome is unused — the contrast is on the measure itself.
    """
    if measure not in frame.columns:
        raise SlackError(f"missing measure column {measure!r}")
    if group not in frame.columns:
        raise SlackError(f"missing group column {group!r}")
    if sign not in (1.0, -1.0):
        raise SlackError("diff_means requires params.sign in {+1,-1}")
    m = frame[measure].to_numpy(dtype=float)
    if not np.isfinite(m).all():
        raise SlackError("diff_means measure must be finite")
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
    gap = float(np.mean(m[in_group]) - np.mean(m[~in_group]))
    out = sign * gap
    if not math.isfinite(out):
        raise SlackError("diff_means produced non-finite coefficient")
    return out


def _map_distance(
    frame: pd.DataFrame,
    measure: str,
    items: list[str],
    loadings: list[list[float]],
    target: list[float],
) -> float:
    """Measure-dependent 2D Euclidean map distance (docs/12 2026-08-08).

    β(m) = ||z̄(m) − z_target||₂ where z̄(m) = mean_i (x_i(m) @ L).
    Item columns resolve as ``{measure}__{item_id}``. The measure column must
    exist (IDENTIFY contract) but is not used in the arithmetic.
    """
    if measure not in frame.columns:
        raise SlackError(f"missing measure column {measure!r}")
    if not items:
        raise SlackError("map_distance requires non-empty items")
    if len(loadings) != len(items):
        raise SlackError(
            f"map_distance loadings length {len(loadings)} != items length {len(items)}"
        )
    if len(target) != 2:
        raise SlackError("map_distance target must have length 2")
    cols: list[str] = []
    for j in items:
        col = f"{measure}__{j}"
        if col not in frame.columns:
            raise SlackError(f"missing map_distance item column {col!r}")
        cols.append(col)
    x = frame[cols].to_numpy(dtype=float)
    if not np.isfinite(x).all():
        raise SlackError("map_distance item columns must be finite")
    l_mat = np.asarray(loadings, dtype=float)
    if l_mat.shape != (len(items), 2) or not np.isfinite(l_mat).all():
        raise SlackError("map_distance loadings must be finite shape (K, 2)")
    t_vec = np.asarray(target, dtype=float)
    if t_vec.shape != (2,) or not np.isfinite(t_vec).all():
        raise SlackError("map_distance target must be finite length-2")
    zbar = x.mean(axis=0) @ l_mat
    dist = float(np.linalg.norm(zbar - t_vec))
    if not math.isfinite(dist):
        raise SlackError("map_distance produced non-finite distance")
    return dist


def evaluate_beta(
    frame: pd.DataFrame,
    measure: str,
    beta: BetaSpec,
) -> float:
    """Evaluate β(m) for one measure."""
    if beta.type == "corr_y":
        if measure not in frame.columns:
            raise SlackError(f"missing measure column {measure!r}")
        if beta.outcome not in frame.columns:
            raise SlackError(f"missing outcome column {beta.outcome!r}")
        return pearson_corr(
            frame[measure].to_numpy(dtype=float),
            frame[beta.outcome].to_numpy(dtype=float),
        )
    if beta.type == "ols_coef":
        if measure not in frame.columns:
            raise SlackError(f"missing measure column {measure!r}")
        if beta.outcome not in frame.columns:
            raise SlackError(f"missing outcome column {beta.outcome!r}")
        controls = beta.params.get("controls")
        if not isinstance(controls, list) or not controls:
            raise SlackError(
                "ols_coef requires params.controls (non-empty list of columns)"
            )
        cols = [str(c) for c in controls]
        return _ols_coef(frame, measure, beta.outcome, cols)
    if beta.type == "diff_means":
        # v3 P3 (docs/12 2026-08-08): group mean gap on the measure.
        group = beta.params.get("group")
        if not isinstance(group, str) or not group:
            raise SlackError("diff_means requires params.group (column name)")
        sign_f = float(beta.params.get("sign", 1))
        return _diff_means(frame, measure, group, sign_f)
    if beta.type == "map_distance":
        # v3 P3 (docs/12 2026-08-08): measure-dependent 2D map distance.
        items_raw = beta.params.get("items")
        if not isinstance(items_raw, list) or not items_raw:
            raise SlackError("map_distance requires params.items (non-empty list)")
        items = [str(j) for j in items_raw]
        loadings_raw = beta.params.get("loadings")
        if not isinstance(loadings_raw, list):
            raise SlackError("map_distance requires params.loadings")
        loadings = [[float(v) for v in row] for row in loadings_raw]
        target_raw = beta.params.get("target")
        if not isinstance(target_raw, list):
            raise SlackError("map_distance requires params.target")
        target = [float(v) for v in target_raw]
        return _map_distance(frame, measure, items, loadings, target)
    raise SlackError(
        f"beta type {beta.type!r} not implemented in the v3 registry "
        f"(schema allows declaration; evaluators: corr_y, ols_coef, "
        f"diff_means, map_distance)"
    )
