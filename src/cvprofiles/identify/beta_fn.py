"""Target functional evaluators (v2.0: corr_y, ols_coef)."""

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
    raise SlackError(
        f"beta type {beta.type!r} not implemented in the v2.0 registry "
        f"(schema allows declaration; evaluators: corr_y, ols_coef)"
    )
