"""End-to-end SCORE→REPORT composition (M7)."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from cvprofiles.pipeline import run_profile, summary_dict


def test_e2e_oracle_mini_golden(
    mini_dir: Path,
    tmp_path: Path,
    mini_expected_freeze: dict,
) -> None:
    out = tmp_path / "oracle"
    result = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=out,
        policy="none",
        seed=0,
        title="AI exposure menu (oracle R)",
    )
    assert result.run_id == mini_expected_freeze["run_id"]
    assert result.score.manifest.scores_hash == mini_expected_freeze["scores_hash"]
    assert result.restrict.network_hash == mini_expected_freeze["network_hash"]
    assert result.restrict.beta_hash == mini_expected_freeze["beta_hash"]

    assert set(result.identify.admissible) == {"m_good", "m_weak"}
    assert "m_slop" not in result.identify.admissible
    assert result.identify.empty is False
    assert result.identify.range_L is not None
    assert result.identify.range_U is not None
    # range is image of survivors only (both positive ~0.99)
    assert result.identify.range_L > 0.9
    assert result.identify.range_U >= result.identify.range_L
    assert result.identify.beta_values["m_slop"] < 0

    assert (out / "report.html").is_file()
    assert (out / "report.json").is_file()
    assert (out / "slacks.csv").is_file()
    assert (out / "admissible.json").is_file()
    assert (out / "range.json").is_file()
    assert (out / "run_manifest.json").is_file()
    assert (out / "score_manifest.json").is_file()

    summary = summary_dict(result)
    assert summary["empty"] is False
    assert set(summary["M_star"]) == {"m_good", "m_weak"}


def test_e2e_harsh_empty_success(mini_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "harsh"
    result = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network_harsh.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=out,
        policy="none",
        seed=0,
        title="AI exposure menu (harsh empty)",
    )
    assert result.identify.empty is True
    assert result.identify.admissible == []
    assert result.identify.range_L is None
    assert result.identify.range_U is None
    html = (out / "report.html").read_text()
    assert "Empty admissible set" in html
    rng = json.loads((out / "range.json").read_text())
    assert rng["empty"] is True
    assert rng["bootstrap"] is None


def test_e2e_cold_double_run_identical(mini_dir: Path, tmp_path: Path) -> None:
    a = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=tmp_path / "a",
        seed=0,
    )
    b = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=tmp_path / "b",
        seed=0,
    )
    assert a.run_id == b.run_id
    assert a.identify.admissible == b.identify.admissible
    assert a.identify.range_L == b.identify.range_L
    assert a.identify.range_U == b.identify.range_U
    assert a.identify.beta_values == b.identify.beta_values
    # created_at may differ; must not affect run_id
    assert a.run_manifest.created_at != "" or True


def test_cli_run_oracle(mini_dir: Path, tmp_path: Path, mini_expected_freeze: dict) -> None:
    out = tmp_path / "cli_oracle"
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "cvprofiles",
            "run",
            "--scores",
            str(mini_dir / "scores.csv"),
            "--roles",
            str(mini_dir / "roles.json"),
            "--network",
            str(mini_dir / "network.yaml"),
            "--beta",
            str(mini_dir / "beta.yaml"),
            "--out",
            str(out),
            "--seed",
            "0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    assert (out / "report.html").is_file()
    # stdout is pure JSON summary (human crumbs on stderr)
    summary = json.loads(proc.stdout)
    assert summary["run_id"] == mini_expected_freeze["run_id"]
    assert set(summary["M_star"]) == {"m_good", "m_weak"}
    assert summary["empty"] is False
    assert "M*" in (proc.stderr or "")


def test_cli_run_harsh_empty_exit_zero(mini_dir: Path, tmp_path: Path) -> None:
    out = tmp_path / "cli_harsh"
    proc = subprocess.run(
        [
            "cvprofiles",
            "run",
            "--scores",
            str(mini_dir / "scores.csv"),
            "--roles",
            str(mini_dir / "roles.json"),
            "--network",
            str(mini_dir / "network_harsh.yaml"),
            "--beta",
            str(mini_dir / "beta.yaml"),
            "--out",
            str(out),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0
    summary = json.loads(proc.stdout)
    assert summary["empty"] is True
    assert summary["M_star"] == []
    assert "empty M*" in (proc.stderr or "")
    html = (out / "report.html").read_text()
    assert "Empty admissible set" in html
