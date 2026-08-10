"""Freeze hash + run_id contract tests (M1 / H4 precursor)."""

from __future__ import annotations

import copy

import numpy as np
import pandas as pd
import pytest

from cvprofiles import __version__
from cvprofiles.freeze import (
    build_freeze_bundle,
    compute_run_id,
    freeze_preimage,
    hash_beta,
    hash_network,
    hash_scores_frame,
    run_id_from_bundle,
)
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.scores import ScoreColumnRoles


def _hashes(
    df: pd.DataFrame,
    roles: ScoreColumnRoles,
    network: NetworkConfig,
    beta: BetaSpec,
    freeze_columns: list[str],
) -> tuple[str, str, str, str]:
    sh = hash_scores_frame(df, freeze_columns, unit_id_col=roles.unit_id)
    nh = hash_network(network)
    bh = hash_beta(beta)
    rid = compute_run_id(
        scores_hash=sh,
        network_hash=nh,
        beta_hash=bh,
        package_version=__version__,
        seed=0,
        delta=float(network.delta),
        n_boot=None,
        config={},
    )
    return sh, nh, bh, rid


def test_golden_freeze_matches_expected(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_network: NetworkConfig,
    mini_beta: BetaSpec,
    mini_freeze_columns: list[str],
    mini_expected_freeze: dict,
) -> None:
    assert __version__ == mini_expected_freeze["package_version"] == "3.0.0"
    sh, nh, bh, rid = _hashes(
        mini_scores_df, mini_roles, mini_network, mini_beta, mini_freeze_columns
    )
    assert sh == mini_expected_freeze["scores_hash"]
    assert nh == mini_expected_freeze["network_hash"]
    assert bh == mini_expected_freeze["beta_hash"]
    assert rid == mini_expected_freeze["run_id"]
    assert mini_freeze_columns == mini_expected_freeze["freeze_columns"]
    assert "V_star" not in mini_freeze_columns


def test_cold_double_hash_identical(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_network: NetworkConfig,
    mini_beta: BetaSpec,
    mini_freeze_columns: list[str],
) -> None:
    a = _hashes(mini_scores_df, mini_roles, mini_network, mini_beta, mini_freeze_columns)
    b = _hashes(mini_scores_df, mini_roles, mini_network, mini_beta, mini_freeze_columns)
    assert a == b


def test_row_order_invariance(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_freeze_columns: list[str],
) -> None:
    base = hash_scores_frame(
        mini_scores_df, mini_freeze_columns, unit_id_col=mini_roles.unit_id
    )
    shuffled = mini_scores_df.sample(frac=1.0, random_state=7).reset_index(drop=True)
    assert list(shuffled["unit_id"]) != list(mini_scores_df["unit_id"])
    again = hash_scores_frame(shuffled, mini_freeze_columns, unit_id_col=mini_roles.unit_id)
    assert again == base


def test_diagnostic_excluded_from_scores_hash(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_freeze_columns: list[str],
) -> None:
    base = hash_scores_frame(
        mini_scores_df, mini_freeze_columns, unit_id_col=mini_roles.unit_id
    )
    mutated = mini_scores_df.copy()
    mutated["V_star"] = mutated["V_star"] + 99.0
    again = hash_scores_frame(mutated, mini_freeze_columns, unit_id_col=mini_roles.unit_id)
    assert again == base


def test_score_cell_change_moves_hash(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_freeze_columns: list[str],
) -> None:
    base = hash_scores_frame(
        mini_scores_df, mini_freeze_columns, unit_id_col=mini_roles.unit_id
    )
    mutated = mini_scores_df.copy()
    mutated.loc[0, "m_good"] = float(mutated["m_good"].iloc[0]) + 0.01
    assert (
        hash_scores_frame(mutated, mini_freeze_columns, unit_id_col=mini_roles.unit_id)
        != base
    )


def test_theta_change_moves_network_hash(mini_network: NetworkConfig) -> None:
    base = hash_network(mini_network)
    tweaked = mini_network.model_copy(deep=True)
    r0 = tweaked.restrictions[0]
    tweaked.restrictions[0] = r0.model_copy(update={"theta": r0.theta + 0.05})
    assert hash_network(tweaked) != base


def test_seed_change_moves_run_id(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_network: NetworkConfig,
    mini_beta: BetaSpec,
    mini_freeze_columns: list[str],
) -> None:
    sh, nh, bh, rid0 = _hashes(
        mini_scores_df, mini_roles, mini_network, mini_beta, mini_freeze_columns
    )
    rid1 = compute_run_id(
        scores_hash=sh,
        network_hash=nh,
        beta_hash=bh,
        package_version=__version__,
        seed=1,
        delta=float(mini_network.delta),
        n_boot=None,
        config={},
    )
    assert rid1 != rid0


def test_preimage_keys_exclude_wall_clock_and_paths(
    mini_expected_freeze: dict,
) -> None:
    pre = freeze_preimage(
        scores_hash=mini_expected_freeze["scores_hash"],
        network_hash=mini_expected_freeze["network_hash"],
        beta_hash=mini_expected_freeze["beta_hash"],
        package_version=mini_expected_freeze["package_version"],
        seed=0,
        delta=0.0,
        n_boot=None,
        config={},
    )
    assert sorted(pre.keys()) == mini_expected_freeze["preimage_keys"]
    forbidden = {
        "created_at",
        "artifact_paths",
        "paths",
        "hostname",
        "host",
        "report_html",
        "timestamp",
    }
    assert forbidden.isdisjoint(pre.keys())


def test_run_id_from_bundle_matches_compute(
    mini_expected_freeze: dict,
) -> None:
    bundle = build_freeze_bundle(
        scores_hash=mini_expected_freeze["scores_hash"],
        network_hash=mini_expected_freeze["network_hash"],
        beta_hash=mini_expected_freeze["beta_hash"],
        package_version=mini_expected_freeze["package_version"],
        seed=0,
        delta=0.0,
        n_boot=None,
        config={},
    )
    assert run_id_from_bundle(bundle) == mini_expected_freeze["run_id"]


def test_bad_hex_rejected() -> None:
    good = "a" * 64
    with pytest.raises(ValueError, match="scores_hash"):
        compute_run_id(
            scores_hash="nope",
            network_hash=good,
            beta_hash=good,
            package_version="3.0.0",
        )
    with pytest.raises(ValueError, match="lowercase hex"):
        compute_run_id(
            scores_hash="A" * 64,
            network_hash=good,
            beta_hash=good,
            package_version="3.0.0",
        )


def test_nan_scores_rejected(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_freeze_columns: list[str],
) -> None:
    bad = mini_scores_df.copy()
    bad.loc[0, "m_good"] = np.nan
    with pytest.raises(ValueError, match="NaN|Inf"):
        hash_scores_frame(bad, mini_freeze_columns, unit_id_col=mini_roles.unit_id)


def test_missing_column_rejected(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
) -> None:
    with pytest.raises(ValueError, match="missing columns"):
        hash_scores_frame(
            mini_scores_df,
            ["unit_id", "not_a_column"],
            unit_id_col=mini_roles.unit_id,
        )


def test_package_version_in_preimage_changes_run_id(
    mini_expected_freeze: dict,
) -> None:
    rid_other = compute_run_id(
        scores_hash=mini_expected_freeze["scores_hash"],
        network_hash=mini_expected_freeze["network_hash"],
        beta_hash=mini_expected_freeze["beta_hash"],
        package_version="9.9.9",
        seed=0,
        delta=0.0,
        n_boot=None,
        config={},
    )
    assert rid_other != mini_expected_freeze["run_id"]


def test_deepcopy_network_hash_stable(mini_network: NetworkConfig) -> None:
    assert hash_network(copy.deepcopy(mini_network)) == hash_network(mini_network)
