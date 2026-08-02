"""Target functional evaluators (v1.0: corr_y only)."""

from __future__ import annotations

import pandas as pd

from cvprofiles.identify.slacks import SlackError, pearson_corr
from cvprofiles.schemas.beta import BetaSpec


def evaluate_beta(
    frame: pd.DataFrame,
    measure: str,
    beta: BetaSpec,
) -> float:
    """Evaluate β(m) for one measure."""
    if beta.type != "corr_y":
        raise SlackError(
            f"beta type {beta.type!r} not implemented in v1.0 thin spine "
            f"(schema allows declaration; evaluator is corr_y only)"
        )
    if measure not in frame.columns:
        raise SlackError(f"missing measure column {measure!r}")
    if beta.outcome not in frame.columns:
        raise SlackError(f"missing outcome column {beta.outcome!r}")
    return pearson_corr(
        frame[measure].to_numpy(dtype=float),
        frame[beta.outcome].to_numpy(dtype=float),
    )
