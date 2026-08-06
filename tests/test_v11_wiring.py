"""v1.1 wiring gates: pipeline, CLI, report, and freeze-layer contracts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

from cvprofiles import __version__
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


def test_pipeline_default_reproduces_golden_and_null_boot(
    mini_dir: Path, mini_expected_freeze: dict, tmp_path: Path
) -> None:
    result = run_profile(**_run_kwargs(mini_dir), out_dir=tmp_path / "default")
    assert result.run_id == mini_expected_freeze["run_id"]
    assert result.run_manifest.freeze.n_boot is None
    assert result.bootstrap is None
    assert result.theta_grid is None
    assert not (result.out_dir / "bootstrap.json").exists()
    assert not (result.out_dir / "theta_grid.json").exists()


def test_bootstrap_is_additive_and_changes_freeze(
    mini_dir: Path, mini_expected_freeze: dict, tmp_path: Path
) -> None:
    default = run_profile(**_run_kwargs(mini_dir), out_dir=tmp_path / "default")
    result = run_profile(
        **_run_kwargs(mini_dir), out_dir=tmp_path / "bootstrap", n_boot=20, seed=7
    )
    assert default.run_id == mini_expected_freeze["run_id"]
    assert result.run_id != default.run_id
    assert result.run_manifest.freeze.n_boot == 20
    assert result.bootstrap is not None
    assert (result.out_dir / "bootstrap.json").is_file()
    assert result.identify.range_L is not None
    assert result.identify.range_U is not None
    assert result.report.payload["range"]["L"] == result.identify.range_L
    assert result.report.payload["range"]["U"] == result.identify.range_U
    assert result.report.payload["range"]["bootstrap"]["see"] == "bootstrap.json"


def test_html_renders_both_inference_panels(
    mini_dir: Path, tmp_path: Path
) -> None:
    result = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "panels",
        n_boot=12,
        theta_grid_lambdas=[0.5, 1.0, 2.0],
    )
    html = (result.out_dir / "report.html").read_text()
    assert "Bootstrap inference" in html
    assert "θ-grid sensitivity" in html
    assert "headline [L, U] above remains" in html
    assert "not part of the freeze preimage" in html


def test_theta_grid_is_diagnostic_not_freeze_input(
    mini_dir: Path, tmp_path: Path
) -> None:
    a = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "grid_a",
        theta_grid_lambdas=[0.5, 1.0],
    )
    b = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "grid_b",
        theta_grid_lambdas=[2.0, 4.0],
    )
    assert a.run_id == b.run_id
    assert a.theta_grid is not None and b.theta_grid is not None
    assert a.theta_grid.lambdas != b.theta_grid.lambdas
    assert json.loads((a.out_dir / "theta_grid.json").read_text())["lambda_scales"] == [
        0.5,
        1.0,
    ]
    assert json.loads((b.out_dir / "theta_grid.json").read_text())["lambda_scales"] == [
        2.0,
        4.0,
    ]


def test_stale_inference_artifacts_are_removed_when_layers_turn_off(
    mini_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "reuse"
    run_profile(
        **_run_kwargs(mini_dir),
        out_dir=out,
        n_boot=10,
        theta_grid_lambdas=[1.0, 2.0],
    )
    assert (out / "bootstrap.json").is_file()
    assert (out / "theta_grid.json").is_file()

    result = run_profile(**_run_kwargs(mini_dir), out_dir=out)
    assert result.bootstrap is None and result.theta_grid is None
    assert not (out / "bootstrap.json").exists()
    assert not (out / "theta_grid.json").exists()
    assert result.run_manifest.artifact_paths.get("bootstrap.json") is None
    assert result.run_manifest.artifact_paths.get("theta_grid.json") is None


def test_empty_network_with_inference_is_clean_success(
    mini_dir: Path, tmp_path: Path
) -> None:
    result = run_profile(
        **_run_kwargs(mini_dir, "network_harsh.yaml"),
        out_dir=tmp_path / "harsh",
        n_boot=15,
        theta_grid_lambdas=[1.0, 2.0],
    )
    assert result.identify.empty is True
    assert result.identify.range_L is None and result.identify.range_U is None
    assert result.bootstrap is not None
    assert result.theta_grid is not None
    assert result.report.payload["range"]["L"] is None
    assert result.report.payload["range"]["U"] is None
    assert (result.out_dir / "report.html").is_file()


def test_cli_inference_flags_keep_stdout_machine_json(
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
            "--n-boot",
            "12",
            "--theta-grid",
            "0.5,1.0,2.0",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["n_boot"] == 12
    assert summary["bootstrap"]["artifact"] == "bootstrap.json"
    assert summary["theta_grid"]["lambdas"] == [0.5, 1.0, 2.0]
    assert (out / "bootstrap.json").is_file()
    assert (out / "theta_grid.json").is_file()
    assert "M*=" in proc.stderr


def test_cli_bad_theta_grid_fails_loud_and_does_not_emit_summary(
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
            "--theta-grid",
            "1.0,,2.0",
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 2
    assert "theta-grid" in proc.stderr
    assert proc.stdout.strip() == ""


def test_summary_is_additive_and_reports_package_version(
    mini_dir: Path, tmp_path: Path
) -> None:
    result = run_profile(
        **_run_kwargs(mini_dir),
        out_dir=tmp_path / "summary",
        n_boot=5,
        theta_grid_lambdas=[1.0],
    )
    summary = summary_dict(result)
    assert summary["bootstrap"]["n_boot"] == 5
    assert summary["theta_grid"]["headline_lambda"] == 1.0
    assert result.report.payload["package_version"] == __version__
    assert __version__ == "2.0.0"
