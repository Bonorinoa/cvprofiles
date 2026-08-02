"""Synthetic gate metrics (H1a/H1b/H1_latent/H3/H4). Labels stay outside IDENTIFY."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd

from cvprofiles.identify.pipeline import IdentifyResult
from cvprofiles.identify.slacks import pearson_corr
from cvprofiles.synth.dgp import (
    ANCHOR,
    INVALID_LABELS,
    LABELS,
    NEAR_MISS_LABELS,
)


@dataclass(frozen=True)
class SeedMetrics:
    scenario: str
    seed: int
    n: int
    empty: bool
    M_star: list[str]
    L: float | None
    U: float | None
    point_id: bool
    # H1a
    false_admissions: list[str]
    fa_rate: float  # 0 or 1 for this seed (any FA → 1)
    n_invalid_admitted: int
    anchor_in_M: bool
    # H1b
    h1b: bool | None  # None if empty
    beta_anchor: float | None
    # H1_latent (diagnostic)
    h1_latent: bool | None
    beta_latent: float | None
    # near-miss (not FA)
    near_miss_admitted: list[str]
    # H4 filled by battery when double-run
    cold_match: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def metrics_from_identify(
    *,
    scenario: str,
    seed: int,
    n: int,
    identify: IdentifyResult,
    frame: pd.DataFrame,
    labels: dict[str, str] | None = None,
    anchor: str = ANCHOR,
) -> SeedMetrics:
    """Compute seed-level metrics from an IdentifyResult + DGP frame/labels."""
    lab = labels if labels is not None else LABELS
    M_star = list(identify.admissible)
    empty = bool(identify.empty)

    invalids = [m for m, role in lab.items() if role in INVALID_LABELS]
    false_admissions = [m for m in M_star if m in invalids]
    near_misses = [m for m, role in lab.items() if role in NEAR_MISS_LABELS]
    near_miss_admitted = [m for m in M_star if m in near_misses]

    anchor_in = anchor in M_star
    beta_anchor = identify.beta_values.get(anchor)

    lo, hi = identify.range_L, identify.range_U
    if empty or lo is None or hi is None:
        h1b: bool | None = None
    elif beta_anchor is None or not anchor_in:
        h1b = False
    else:
        h1b = bool(lo - 1e-12 <= beta_anchor <= hi + 1e-12)

    # Latent diagnostic: Corr(V*, y) on the scored frame (same columns SCORE saw).
    beta_latent: float | None = None
    h1_latent: bool | None = None
    if "V_star" in frame.columns and identify.beta_values:
        try:
            beta_latent = pearson_corr(
                frame["V_star"].to_numpy(dtype=float),
                frame["y"].to_numpy(dtype=float),
            )
        except Exception:
            beta_latent = None
        if empty or beta_latent is None or lo is None or hi is None:
            h1_latent = None if empty else False
        else:
            h1_latent = bool(lo - 1e-12 <= beta_latent <= hi + 1e-12)

    return SeedMetrics(
        scenario=scenario,
        seed=int(seed),
        n=int(n),
        empty=empty,
        M_star=M_star,
        L=identify.range_L,
        U=identify.range_U,
        point_id=bool(identify.point_id),
        false_admissions=false_admissions,
        fa_rate=1.0 if false_admissions else 0.0,
        n_invalid_admitted=len(false_admissions),
        anchor_in_M=anchor_in,
        h1b=h1b,
        beta_anchor=beta_anchor,
        h1_latent=h1_latent,
        beta_latent=beta_latent,
        near_miss_admitted=near_miss_admitted,
        cold_match=None,
    )


def cold_cores_equal(a: IdentifyResult, b: IdentifyResult, atol: float = 1e-12) -> bool:
    """H4 core: M*, L, U, slacks, beta_values."""
    if a.admissible != b.admissible:
        return False
    if a.empty != b.empty:
        return False
    if a.empty:
        return True
    if a.range_L is None or b.range_L is None:
        return False
    if not np.isclose(a.range_L, b.range_L, atol=atol, equal_nan=True):
        return False
    if not np.isclose(a.range_U, b.range_U, atol=atol, equal_nan=True):  # type: ignore[arg-type]
        return False
    # slacks
    try:
        pd.testing.assert_frame_equal(
            a.slacks.sort_index(axis=0).sort_index(axis=1),
            b.slacks.sort_index(axis=0).sort_index(axis=1),
            rtol=0.0,
            atol=atol,
        )
    except AssertionError:
        return False
    for m in a.measures:
        if not np.isclose(a.beta_values[m], b.beta_values[m], atol=atol):
            return False
    return True
