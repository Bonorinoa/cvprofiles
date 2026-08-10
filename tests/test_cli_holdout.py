"""v2.5.0 CLI wiring gates: --holdout-units / --alpha / --kappa (audit B, P0).

The P4b units-split holdout and the P5 coverage band have lived in
``run_profile`` since v2.5.0 (src/cvprofiles/pipeline.py:89-91); this file
pins their CLI exposure and the stdout-JSON / stderr-notes contract:

- ``--holdout-units`` is a comma-separated unit-id list; empty string or
  empty tokens fail loud (mirrors ``_parse_theta_grid``). Duplicates are
  PASSED THROUGH: the pipeline normalizes sorted-unique inside
  ``normalize_holdout_units`` (identify/pipeline.py:73), so list order and
  duplicates can never fork ``run_id`` — the CLI parser stays a thin splitter.
- ``--alpha`` / ``--kappa`` mirror the coverage.py validation rules verbatim
  (inference/coverage.py:103-108): ``0 < alpha < 1`` finite; ``kappa`` finite
  ``> 0``. A violating value is a parse-time fail-loud: stderr note + exit 2,
  no summary JSON on stdout (same shape as the theta-grid/delta-grid gates).
- Regression: the default CLI run (no new flags) keeps the golden run_id —
  the new options must not enter the freeze preimage when absent, and
  alpha/kappa never do by design (coverage.py contract).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


def _base_cmd(mini_dir: Path, out: Path) -> list[str]:
    return [
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
    ]


def _run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


# --- regression: default run keeps the golden run_id (no preimage drift) ---


def test_cli_default_run_id_stable_without_new_flags(
    mini_dir: Path, mini_expected_freeze: dict, tmp_path: Path
) -> None:
    proc = _run(_base_cmd(mini_dir, tmp_path / "default"))
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["run_id"] == mini_expected_freeze["run_id"]
    assert summary["coverage"] is None  # layer off
    manifest = json.loads((tmp_path / "default" / "run_manifest.json").read_text())
    assert manifest["freeze"]["config"] == {}  # no new preimage keys


def test_cli_alpha_kappa_do_not_fork_default_run_id(
    mini_dir: Path, mini_expected_freeze: dict, tmp_path: Path
) -> None:
    """alpha/kappa are EXCLUDED from the freeze preimage (coverage.py:30-32)."""
    proc = _run(
        _base_cmd(mini_dir, tmp_path / "tuned") + ["--alpha", "0.2", "--kappa", "3.0"]
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["run_id"] == mini_expected_freeze["run_id"]


# --- happy paths ---


def test_cli_holdout_units_flag_keeps_stdout_machine_json(
    mini_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "cli"
    proc = _run(_base_cmd(mini_dir, out) + ["--holdout-units", "u01,u02,u03"])
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    # robust semantics are the split headline (summary_dict key names)
    assert summary["M_star_select"] == ["m_good", "m_weak"]
    assert summary["M_star_robust"] == ["m_good", "m_weak"]
    assert summary["M_star"] == ["m_good", "m_weak"]
    assert "M*=" in proc.stderr  # human crumb stays on stderr
    manifest = json.loads((out / "run_manifest.json").read_text())
    assert manifest["freeze"]["config"] == {"holdout_units": ["u01", "u02", "u03"]}


def test_cli_holdout_units_duplicates_passed_through(
    mini_dir: Path, tmp_path: Path
) -> None:
    """Choice documented: duplicates/order pass through the CLI parser; the
    pipeline's normalize_holdout_units dedupes sorted-unique (pipeline.py:138
    -> identify/pipeline.py:73), so dupes/order can never fork run_id."""
    a = _run(_base_cmd(mini_dir, tmp_path / "a") + ["--holdout-units", "u03,u01,u02"])
    b = _run(
        _base_cmd(mini_dir, tmp_path / "b")
        + ["--holdout-units", "u01,u02,u03,u01"]  # duplicate + reordered
    )
    assert a.returncode == 0, a.stderr
    assert b.returncode == 0, b.stderr
    assert json.loads(a.stdout)["run_id"] == json.loads(b.stdout)["run_id"]
    man_b = json.loads((tmp_path / "b" / "run_manifest.json").read_text())
    assert man_b["freeze"]["config"] == {"holdout_units": ["u01", "u02", "u03"]}


def test_cli_alpha_kappa_wire_into_coverage(
    mini_dir: Path, tmp_path: Path
) -> None:
    out = tmp_path / "cli"
    proc = _run(
        _base_cmd(mini_dir, out)
        + ["--n-boot", "12", "--seed", "7", "--alpha", "0.2", "--kappa", "1.5"]
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["coverage"]["alpha"] == 0.2
    assert summary["coverage"]["kappa"] == 1.5
    assert summary["coverage"]["artifact"] == "coverage.json"
    assert (out / "coverage.json").is_file()
    cov = json.loads((out / "coverage.json").read_text())
    assert cov["alpha"] == 0.2 and cov["kappa"] == 1.5
    assert "M*=" in proc.stderr


# --- fail-loud validation: parse-error path, exit 2, no summary on stdout ---


@pytest.mark.parametrize("bad", ["", "u01,,u03", " u01 , "])
def test_cli_bad_holdout_units_fails_loud(
    mini_dir: Path, tmp_path: Path, bad: str
) -> None:
    proc = _run(_base_cmd(mini_dir, tmp_path / "bad") + ["--holdout-units", bad])
    assert proc.returncode == 2
    assert "holdout-units" in proc.stderr
    assert "No such option" not in proc.stderr  # option exists; parse-error path
    assert proc.stdout.strip() == ""


@pytest.mark.parametrize("bad", ["0", "1", "-0.1", "1.5", "nan", "inf"])
def test_cli_bad_alpha_fails_loud(mini_dir: Path, tmp_path: Path, bad: str) -> None:
    proc = _run(_base_cmd(mini_dir, tmp_path / "bad") + ["--alpha", bad])
    assert proc.returncode == 2
    assert "alpha" in proc.stderr
    assert "No such option" not in proc.stderr  # option exists; validation path
    assert proc.stdout.strip() == ""


@pytest.mark.parametrize("bad", ["0", "-1", "nan", "inf"])
def test_cli_bad_kappa_fails_loud(mini_dir: Path, tmp_path: Path, bad: str) -> None:
    proc = _run(_base_cmd(mini_dir, tmp_path / "bad") + ["--kappa", bad])
    assert proc.returncode == 2
    assert "kappa" in proc.stderr
    assert "No such option" not in proc.stderr  # option exists; validation path
    assert proc.stdout.strip() == ""
