"""Regression tests from the 2026-08-06 post-release audit follow-up."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.identify.pipeline import run_identify, write_identify_artifacts
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import run_score


@pytest.fixture
def identify_mini(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_dir: Path,
):
    scored = run_score(mini_scores_df, mini_roles, policy="none")
    restrict = run_restrict(mini_roles, mini_dir / "network.yaml", mini_dir / "beta.yaml")
    return run_identify(scored.frame, scored.roles, restrict)


def test_identify_parquet_failure_is_observable(
    identify_mini, tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture
) -> None:
    """M4 (audit): a slacks.parquet write failure must be surfaced, not swallowed.

    CSV remains the authoritative artifact, but silence hides disk/permission
    failures — the warning must land on stderr and the parquet path must be
    absent from the returned artifact map.
    """

    def _boom(*args, **kwargs):
        raise OSError("simulated parquet backend failure")

    monkeypatch.setattr(pd.DataFrame, "to_parquet", _boom)

    paths = write_identify_artifacts(identify_mini, tmp_path)

    assert (tmp_path / "slacks.csv").exists()
    assert "slacks.parquet" not in paths
    captured = capsys.readouterr()
    assert "slacks.parquet" in captured.err
