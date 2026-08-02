"""SCORE state contract tests (M2 / G2)."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import ScoreError, run_score, write_score_artifacts


def test_score_mini_matches_golden_hash(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_expected_freeze: dict,
) -> None:
    result = run_score(mini_scores_df, mini_roles, policy="none")
    assert result.manifest.scores_hash == mini_expected_freeze["scores_hash"]
    assert result.manifest.normalization["policy"] == "none"
    assert result.freeze_columns == mini_expected_freeze["freeze_columns"]
    assert "V_star" not in result.freeze_columns
    assert result.manifest.n_rows == 10
    assert result.manifest.n_measures == 3


def test_score_row_order_invariant(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_expected_freeze: dict,
) -> None:
    shuffled = mini_scores_df.sample(frac=1.0, random_state=3).reset_index(drop=True)
    result = run_score(shuffled, mini_roles, policy="none")
    assert result.manifest.scores_hash == mini_expected_freeze["scores_hash"]


def test_score_diagnostic_mutation_does_not_change_hash(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_expected_freeze: dict,
) -> None:
    mutated = mini_scores_df.copy()
    mutated["V_star"] = mutated["V_star"] + 100.0
    result = run_score(mutated, mini_roles, policy="none")
    assert result.manifest.scores_hash == mini_expected_freeze["scores_hash"]


def test_score_missing_column_fails(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
) -> None:
    bad = mini_scores_df.drop(columns=["v_aux"])
    with pytest.raises(ScoreError, match="missing required columns"):
        run_score(bad, mini_roles, policy="none")


def test_score_empty_frame_fails(mini_roles: ScoreColumnRoles) -> None:
    df = pd.DataFrame(columns=["unit_id", "m_good", "m_weak", "m_slop", "v_aux", "y"])
    with pytest.raises(ScoreError, match="empty"):
        run_score(df, mini_roles, policy="none")


def test_score_duplicate_unit_id_fails(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
) -> None:
    bad = mini_scores_df.copy()
    bad.loc[1, "unit_id"] = bad.loc[0, "unit_id"]
    with pytest.raises(ScoreError, match="duplicate unit_id"):
        run_score(bad, mini_roles, policy="none")


def test_score_nan_fails(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
) -> None:
    bad = mini_scores_df.copy()
    bad.loc[0, "m_good"] = np.nan
    with pytest.raises(ScoreError, match="non-finite"):
        run_score(bad, mini_roles, policy="none")


def test_score_zscore_changes_hash(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_expected_freeze: dict,
) -> None:
    z = run_score(mini_scores_df, mini_roles, policy="zscore_measures")
    assert z.manifest.normalization["policy"] == "zscore_measures"
    assert z.manifest.scores_hash != mini_expected_freeze["scores_hash"]
    # Measures approximately mean 0
    for col in mini_roles.measures:
        assert abs(float(z.frame[col].mean())) < 1e-10


def test_write_score_artifacts(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    tmp_path: Path,
    mini_expected_freeze: dict,
) -> None:
    result = run_score(mini_scores_df, mini_roles, policy="none")
    paths = write_score_artifacts(result, tmp_path, parquet=True)
    assert paths["score_manifest.json"].is_file()
    assert paths["S_frozen.csv"].is_file()
    assert paths["S_frozen.parquet"].is_file()
    reloaded = pd.read_csv(paths["S_frozen.csv"])
    again = run_score(reloaded, mini_roles, policy="none")
    assert again.manifest.scores_hash == mini_expected_freeze["scores_hash"]
