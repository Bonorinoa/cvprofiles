"""CLI demo: emit mini_v1 four-file bundle and run the golden profile."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

INPUT_NAMES = ("scores.csv", "roles.json", "network.yaml", "beta.yaml")


def _run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True, cwd=cwd)


def _demo_cmd(out: Path, *extra: str) -> list[str]:
    return [sys.executable, "-m", "cvprofiles", "demo", "--out", str(out), *extra]


def test_demo_writes_mini_v1_inputs_and_matches_golden_freeze(
    mini_dir: Path, mini_expected_freeze: dict, tmp_path: Path
) -> None:
    out = tmp_path / "demo"
    proc = _run(_demo_cmd(out), cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    for name in INPUT_NAMES:
        written = (out / name).read_bytes()
        golden = (mini_dir / name).read_bytes()
        assert written == golden, name

    summary = json.loads(proc.stdout)
    assert summary["run_id"] == mini_expected_freeze["run_id"]
    assert summary["scores_hash"] == mini_expected_freeze["scores_hash"]
    assert summary["network_hash"] == mini_expected_freeze["network_hash"]
    assert summary["beta_hash"] == mini_expected_freeze["beta_hash"]
    assert summary["empty"] is False
    assert summary["M_star"] == ["m_good", "m_weak"]
    assert summary["rejected"] == {"m_slop": ["r_corr_min_aux", "r_corr_sign_aux"]}
    # F5 (2026-08-16 audit): golden floats on derived OLS coefficients must
    # carry a tolerance — last-ulp differences across BLAS/platforms are
    # expected and are not a scientific change.
    assert summary["L"] == pytest.approx(0.9908134006120914, rel=1e-12)
    assert summary["U"] == pytest.approx(0.9929645567186532, rel=1e-12)
    assert (out / "report.html").is_file()
    assert "m_slop" in proc.stderr
    assert "finding" in proc.stderr.lower()


def test_demo_existing_nonempty_out_fails_loud(tmp_path: Path) -> None:
    out = tmp_path / "demo"
    out.mkdir()
    (out / "stale.txt").write_text("keep", encoding="utf-8")
    proc = _run(_demo_cmd(out), cwd=tmp_path)
    assert proc.returncode == 2
    assert "not empty" in proc.stderr
    assert proc.stdout.strip() == ""
    assert (out / "stale.txt").read_text(encoding="utf-8") == "keep"
    assert not (out / "scores.csv").exists()


def test_demo_force_overwrites_nonempty_out(
    mini_expected_freeze: dict, tmp_path: Path
) -> None:
    out = tmp_path / "demo"
    out.mkdir()
    (out / "stale.txt").write_text("keep", encoding="utf-8")
    proc = _run(_demo_cmd(out, "--force"), cwd=tmp_path)
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["run_id"] == mini_expected_freeze["run_id"]
    assert (out / "scores.csv").is_file()
