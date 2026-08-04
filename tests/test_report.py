"""Thin REPORT contract tests (M7 / G7 from G5)."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from cvprofiles import __version__
from cvprofiles.freeze import build_freeze_bundle, compute_run_id
from cvprofiles.identify.pipeline import run_identify
from cvprofiles.report.pipeline import write_report
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.schemas.run import RunManifest
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import run_score


def _run_manifest(score, restrict, seed: int = 0) -> RunManifest:
    assert score.manifest.scores_hash is not None
    freeze = build_freeze_bundle(
        scores_hash=score.manifest.scores_hash,
        network_hash=restrict.network_hash,
        beta_hash=restrict.beta_hash,
        package_version=__version__,
        seed=seed,
        delta=float(restrict.delta),
        n_boot=None,
        config={},
    )
    run_id = compute_run_id(
        scores_hash=freeze.scores_hash,
        network_hash=freeze.network_hash,
        beta_hash=freeze.beta_hash,
        package_version=freeze.package_version,
        seed=freeze.seed,
        delta=freeze.delta,
        n_boot=None,
        config={},
    )
    return RunManifest(
        run_id=run_id,
        freeze=freeze,
        created_at="1970-01-01T00:00:00Z",
        artifact_paths={},
        notes="test",
    )


def test_report_oracle_html_json(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_dir: Path,
    tmp_path: Path,
    mini_expected_freeze: dict,
) -> None:
    score = run_score(mini_scores_df, mini_roles, policy="none")
    restrict = run_restrict(mini_roles, mini_dir / "network.yaml", mini_dir / "beta.yaml")
    identify = run_identify(score.frame, score.roles, restrict)
    man = _run_manifest(score, restrict)
    assert man.run_id == mini_expected_freeze["run_id"]

    result = write_report(
        run_manifest=man,
        restrict=restrict,
        identify=identify,
        out_dir=tmp_path,
        title="mini_v1 exposure (oracle)",
    )
    assert result.html_path.is_file()
    assert result.json_path.is_file()
    html = result.html_path.read_text()
    payload = json.loads(result.json_path.read_text())

    assert payload["empty"] is False
    assert set(payload["admissible"]) == {"m_good", "m_weak"}
    assert "m_slop" in payload["rejected"]
    assert payload["L"] is not None and payload["U"] is not None
    assert payload["range"]["bootstrap"] is None
    assert payload["run_id"] == mini_expected_freeze["run_id"]

    assert "m_good" in html and "m_slop" in html
    assert "admissible" in html
    assert "Empty admissible set" not in html
    assert "min/max" in html or "min/max B*" in html or "B*" in html
    assert "v1.1 inference" in html


def test_report_empty_is_beautiful(
    mini_scores_df: pd.DataFrame,
    mini_roles: ScoreColumnRoles,
    mini_dir: Path,
    tmp_path: Path,
) -> None:
    score = run_score(mini_scores_df, mini_roles, policy="none")
    restrict = run_restrict(
        mini_roles, mini_dir / "network_harsh.yaml", mini_dir / "beta.yaml"
    )
    identify = run_identify(score.frame, score.roles, restrict)
    assert identify.empty is True
    man = _run_manifest(score, restrict)

    result = write_report(
        run_manifest=man,
        restrict=restrict,
        identify=identify,
        out_dir=tmp_path,
        title="mini_v1 exposure (harsh empty)",
    )
    html = result.html_path.read_text()
    payload = json.loads(result.json_path.read_text())

    assert payload["empty"] is True
    assert payload["L"] is None and payload["U"] is None
    assert payload["admissible"] == []
    assert "Empty admissible set" in html
    assert "success, not a crash" in html
    assert "do not auto-loosen" in html
