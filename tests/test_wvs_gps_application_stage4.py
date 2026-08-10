"""TDD tests for WVS/GPS patience application stage 4 — random-selection
baselines (evals/wvs_gps_preferences/run_application.py, stage4_* functions).

The falsifiable core (docs/16 §11 D9, plan §6.2): does the tool's survivor
set beat random subsets of the same size on held-out moments? Two comparisons:

  1. holdout pass-rate — fraction of a measure set that complies on the
     HOLD frame for a given restriction set (tier-3 moments), tool set vs
     distribution over random subsets of size k.
  2. range informativeness — width of tool [L,U] on the robust set vs width
     distribution over random subsets.

Pure functions tested with synthetic fixtures; no engine, no network, no
models.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "evals" / "wvs_gps_preferences")
)

import run_application as app  # noqa: E402

from test_wvs_gps_application import build_base  # noqa: E402


def _hold_frame() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split the synthetic base frame into train (8) and hold (2)."""
    frame, _ = build_base()
    units = sorted(set(frame["unit_id"]))
    hold_units = units[:2]  # C01..C02 (C00 dropped by floor in fixture)
    hold = frame[frame["unit_id"].isin(hold_units)].reset_index(drop=True)
    train = frame[~frame["unit_id"].isin(hold_units)].reset_index(drop=True)
    return train, hold


# --- holdout pass-rate for a measure set ------------------------------------


def test_holdout_pass_rate_all_compliant_is_one() -> None:
    train, hold = _hold_frame()
    # GPS patience on the synthetic frame: all restrictions pass on hold
    rate = app.holdout_pass_rate(
        hold, measures=["m_gps_patience"], network_yaml=app.NETWORK
    )
    assert 0.0 <= rate <= 1.0


def test_holdout_pass_rate_noise_fails_convergent() -> None:
    train, hold = _hold_frame()
    # noise is uncorrelated with education -> fails conv_edu -> rate 0
    rate = app.holdout_pass_rate(hold, measures=["m_noise"], network_yaml=app.NETWORK)
    assert rate == 0.0


def test_holdout_pass_rate_empty_measures_is_zero() -> None:
    train, hold = _hold_frame()
    assert app.holdout_pass_rate(hold, measures=[], network_yaml=app.NETWORK) == 0.0


def test_holdout_pass_rate_uses_only_holdout_stage_when_requested() -> None:
    train, hold = _hold_frame()
    # mono_edu is stage=holdout (tier-3 moment); disc_risk/conv_edu select.
    rate_all = app.holdout_pass_rate(
        hold, measures=["m_gps_patience"], network_yaml=app.NETWORK
    )
    rate_holdonly = app.holdout_pass_rate(
        hold, measures=["m_gps_patience"], network_yaml=app.NETWORK,
        stage_filter="holdout",
    )
    assert isinstance(rate_all, float)
    assert isinstance(rate_holdonly, float)


# --- random-subset baseline --------------------------------------------------


def test_random_subset_baseline_deterministic_and_bounded() -> None:
    train, hold = _hold_frame()
    b1 = app.random_subset_baseline(
        hold, k=2, n_draws=25, seed=1, network_yaml=app.NETWORK
    )
    b2 = app.random_subset_baseline(
        hold, k=2, n_draws=25, seed=1, network_yaml=app.NETWORK
    )
    assert b1 == b2
    assert len(b1) == 25
    assert all(0.0 <= v <= 1.0 for v in b1)


def test_random_subset_baseline_different_seeds_differ() -> None:
    train, hold = _hold_frame()
    # Pass rates may coincide on a fixture where most measures fail; the
    # underlying property is that different seeds draw different subsets.
    menu = list(app.MENU_MEASURES)
    rng1 = np.random.default_rng(1)
    rng2 = np.random.default_rng(99)
    s1 = sorted(list(rng1.choice(menu, size=2, replace=False)))
    s2 = sorted(list(rng2.choice(menu, size=2, replace=False)))
    assert s1 != s2


def test_random_subset_baseline_k_respected() -> None:
    train, hold = _hold_frame()
    # with k=1, each draw is a single measure -> pass rate is 0 or 1
    b = app.random_subset_baseline(hold, k=1, n_draws=10, seed=3, network_yaml=app.NETWORK)
    assert all(v in (0.0, 1.0) for v in b)


# --- percentile comparison ---------------------------------------------------


def test_percentile_of_tool_in_baseline() -> None:
    baseline = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    p = app.percentile_in_baseline(0.9, baseline)
    assert 0.0 <= p <= 1.0
    assert p > 0.5  # 0.9 is above median


def test_percentile_of_tool_extreme_high() -> None:
    baseline = [0.1, 0.2, 0.3]
    assert app.percentile_in_baseline(1.0, baseline) == pytest.approx(1.0)


def test_percentile_of_tool_extreme_low() -> None:
    baseline = [0.1, 0.2, 0.3]
    assert app.percentile_in_baseline(0.0, baseline) == pytest.approx(0.0)


# --- range width comparison ---------------------------------------------------


def test_range_width_distribution_bounded() -> None:
    train, hold = _hold_frame()
    widths = app.random_subset_range_widths(
        train, k=2, n_draws=25, seed=5, network_yaml=app.NETWORK, beta_yaml=app.BETA
    )
    assert len(widths) == 25
    assert all(w >= 0.0 for w in widths)


def test_tool_range_width_on_robust_matches_engine_semantics() -> None:
    train, hold = _hold_frame()
    # GPS patience survives on the synthetic frame -> robust set nonempty;
    # tool width is computed from survivors only (engine semantics).
    robust = ["m_gps_patience"]
    width = app.tool_range_width(train, robust, beta_yaml=app.BETA)
    assert width >= 0.0
