"""v2.0 measure discipline wiring gates (M-a3: δ-grid in pipeline/CLI/report).

Preimage witness: the δ-grid is a diagnostic viewport — same bundle +
different grid ⇒ same run_id, different delta_grid.json (docs/12 2026-08-05).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

from cvprofiles.pipeline import run_profile, summary_dict


class ProfilePaths(TypedDict):
    scores: Path
    roles: Path
    network: Path
    beta: Path


def _run_kwargs(mini_dir: Path, network: str = "network.yaml") -> ProfilePaths:
    return {
        "scores": mini_dir / "scores.csv",
        "roles": mini_dir / "roles.json",
        "network": mini_dir / network,
        "beta": mini_dir / "beta.yaml",
    }


def test_delta_grid_default_path_keeps_golden_run_id(
    mini_dir: Path, mini_expected_freeze: dict, tmp_path: Path
) -> None:
    default = run_profile(**_run_kwargs(mini_dir), out_dir=tmp_path / "default")
    assert default.run_id == mini_expected_freeze["run_id"]
    assert default.delta_grid is None
    assert not (default.out_dir / "delta_grid.json").exists()
    assert default.run_manifest.artifact_paths.get("delta_grid.json") is None


def test_delta_grid_is_diagnostic_not_freeze_input(
    mini_dir: Path, tmp_path: Path
) -> None:
    a = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "grid_a",
        delta_grid_deltas=[0.0, 0.1],
    )
    b = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "grid_b",
        delta_grid_deltas=[0.0, 0.2],
    )
    assert a.run_id == b.run_id
    assert a.delta_grid is not None and b.delta_grid is not None
    assert a.delta_grid.deltas != b.delta_grid.deltas
    assert json.loads((a.out_dir / "delta_grid.json").read_text())["deltas"] == [
        0.0,
        0.1,
    ]
    assert json.loads((b.out_dir / "delta_grid.json").read_text())["deltas"] == [
        0.0,
        0.2,
    ]
    assert (a.out_dir / "delta_grid.json").is_file()
    assert "delta_grid.json" in a.run_manifest.artifact_paths


def test_stale_delta_grid_artifact_removed_when_off(
    mini_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "reuse"
    run_profile(
        **_run_kwargs(mini_dir), out_dir=out, delta_grid_deltas=[0.0, 0.1]
    )
    assert (out / "delta_grid.json").is_file()

    result = run_profile(**_run_kwargs(mini_dir), out_dir=out)
    assert result.delta_grid is None
    assert not (out / "delta_grid.json").exists()
    assert result.run_manifest.artifact_paths.get("delta_grid.json") is None


def test_html_renders_delta_grid_panel(mini_dir: Path, tmp_path: Path) -> None:
    result = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "panels",
        delta_grid_deltas=[0.0, 0.05, 0.1],
    )
    html = (result.out_dir / "report.html").read_text()
    assert "δ-grid tolerance" in html
    assert "not part of the freeze preimage" in html
    assert result.report.payload["delta_grid"] is not None


def test_cli_delta_grid_keeps_stdout_machine_json(
    mini_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "cli"
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
            "7",
            "--delta-grid",
            "0,0.05,0.1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["delta_grid"]["deltas"] == [0.0, 0.05, 0.1]
    assert summary["delta_grid"]["artifact"] == "delta_grid.json"
    assert (out / "delta_grid.json").is_file()
    assert "M*=" in proc.stderr


def test_cli_bad_delta_grid_fails_loud_and_does_not_emit_summary(
    mini_dir: Path, tmp_path: Path
) -> None:
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
            str(tmp_path / "bad"),
            "--delta-grid",
            "0,,0.1",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "delta-grid" in proc.stderr
    assert "No such option" not in proc.stderr  # option exists; parse error path
    assert proc.stdout.strip() == ""


def test_summary_is_additive_with_delta_grid(
    mini_dir: Path, tmp_path: Path
) -> None:
    result = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "summary",
        delta_grid_deltas=[0.0, 0.1],
    )
    summary = summary_dict(result)
    assert summary["delta_grid"]["headline_delta"] == 0.0
    off = run_profile(**_run_kwargs(mini_dir), out_dir=tmp_path / "off")
    assert summary_dict(off)["delta_grid"] is None  # key present, layer off (v1.1 convention)
