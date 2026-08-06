"""mean_order evaluator tests (v2.0 thread b, M-b1; docs/12 2026-08-05 D3).

Semantics: params {group, sign} with sign in {+1,-1} (default +1); group must
be a binary 0/1 indicator column (fail loud otherwise).
slack = sign*(mean(m | g=1) - mean(m | g=0)) - theta.

Fixture mean_order_v1 (hand-computed):
  mean(m_high | g=1)=0.8, | g=0)=0.2  -> gap 0.60 -> slack 0.30  (admitted)
  mean(m_low  | g=1)=0.22, | g=0)=0.18 -> gap 0.04 -> slack -0.26 (rejected)
  mean(m_slop | g=1)=0.12, | g=0)=0.92 -> gap -0.80 -> slack -1.10 (rejected)
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.restrict.pipeline import RestrictError, run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import load_roles, run_score


@pytest.fixture
def mo_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "mean_order_v1"


@pytest.fixture
def mo_roles(mo_path: Path) -> ScoreColumnRoles:
    return load_roles(mo_path / "roles.json")


@pytest.fixture
def scored_mo(mo_path: Path, mo_roles: ScoreColumnRoles):
    return run_score(pd.read_csv(mo_path / "scores.csv"), mo_roles, policy="none")


@pytest.fixture
def restrict_mo(mo_path: Path, mo_roles: ScoreColumnRoles):
    return run_restrict(mo_roles, mo_path / "network.yaml", mo_path / "beta.yaml")


def test_mean_order_admits_high_rejects_low_and_slop(scored_mo, restrict_mo) -> None:
    result = run_identify(scored_mo.frame, scored_mo.roles, restrict_mo)
    assert set(result.admissible) == {"m_high"}
    assert set(result.rejected) == {"m_low", "m_slop"}
    assert result.rejected["m_low"] == ["r_mean_order_group"]
    assert result.rejected["m_slop"] == ["r_mean_order_group"]


def test_mean_order_hand_golden_slacks(scored_mo, restrict_mo) -> None:
    result = run_identify(scored_mo.frame, scored_mo.roles, restrict_mo)
    assert result.slacks.at["m_high", "r_mean_order_group"] == pytest.approx(
        0.30, abs=1e-9
    )
    assert result.slacks.at["m_low", "r_mean_order_group"] == pytest.approx(
        -0.26, abs=1e-9
    )
    assert result.slacks.at["m_slop", "r_mean_order_group"] == pytest.approx(
        -1.10, abs=1e-9
    )


def test_mean_order_default_sign_is_positive(mo_path: Path, mo_roles, scored_mo) -> None:
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_mean_order_group",
                "type": "mean_order",
                "theta": 0.3,
                "params": {"group": "group"},  # no sign -> +1
            }
        ],
    }
    bundle = run_restrict(mo_roles, raw, mo_path / "beta.yaml")
    result = run_identify(scored_mo.frame, scored_mo.roles, bundle)
    assert set(result.admissible) == {"m_high"}
    assert result.slacks.at["m_high", "r_mean_order_group"] == pytest.approx(
        0.30, abs=1e-9
    )


def test_mean_order_sign_minus_flips_admission(scored_mo, restrict_mo) -> None:
    flipped = restrict_mo.network.model_copy(
        deep=True,
        update={
            "restrictions": [
                r.model_copy(update={"params": {"group": "group", "sign": -1}})
                for r in restrict_mo.network.restrictions
            ]
        },
    )
    bundle = run_restrict(scored_mo.roles, flipped, restrict_mo.beta)
    result = run_identify(scored_mo.frame, scored_mo.roles, bundle)
    # m_slop gap -0.80 -> slack -(-0.80)-0.3 = 0.50 admitted; m_high flips to -0.9
    assert set(result.admissible) == {"m_slop"}
    assert result.slacks.at["m_slop", "r_mean_order_group"] == pytest.approx(
        0.50, abs=1e-9
    )
    assert result.slacks.at["m_high", "r_mean_order_group"] == pytest.approx(
        -0.90, abs=1e-9
    )


def test_mean_order_group_must_be_binary(scored_mo, restrict_mo) -> None:
    df = scored_mo.frame.copy()
    df.loc[df.index[0], "group"] = 2.0
    with pytest.raises(IdentifyError, match="binary"):
        run_identify(df, scored_mo.roles, restrict_mo)


def test_mean_order_missing_group_column_fails_at_restrict(
    mo_path: Path, mo_roles, scored_mo
) -> None:
    raw = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_mean_order_group",
                "type": "mean_order",
                "theta": 0.3,
                "params": {"group": "does_not_exist"},
            }
        ],
    }
    with pytest.raises(RestrictError, match="group column"):
        run_restrict(mo_roles, raw, mo_path / "beta.yaml")
