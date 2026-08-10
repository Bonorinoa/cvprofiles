"""Hermetic tests for tools/check_version_consistency.py (audit D4).

The checker must not depend on the real repo's current docs state (which is
mid-fix by a parallel docs agent). Every test builds a minimal synthetic tree
in tmp_path at a FAKE version (9.8.7) and drives the tool as a subprocess.

Posture lines checked (see the tool's docstring contract table):
  src/cvprofiles/__init__.py   __version__ = "X.Y.Z"
  pyproject.toml               version = "X.Y.Z"          ([project])
  AGENTS.md                    - Package version: `X.Y.Z`
  README.md                    | **Version** | **X.Y.Z** |
  docs/USER_GUIDE.md           ... shipped vX.Y.Z ...
  docs/ARCHITECTURE.md         ... reflects the shipped vX.Y.Z package ...
  docs/METHODOLOGY.md          - Package version: `X.Y.Z`  (currently absent
                                in the real repo; checker must demand it)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

TOOL = Path(__file__).resolve().parents[1] / "tools" / "check_version_consistency.py"
FAKE = "9.8.7"  # never collides with the real repo's version


def _write_tree(root: Path) -> None:
    (root / "src" / "cvprofiles").mkdir(parents=True)
    (root / "docs").mkdir()
    (root / "src" / "cvprofiles" / "__init__.py").write_text(
        f'__version__ = "{FAKE}"\n', encoding="utf-8"
    )
    (root / "pyproject.toml").write_text(
        f'[project]\nversion = "{FAKE}"\n', encoding="utf-8"
    )
    (root / "AGENTS.md").write_text(
        f"- Package version: `{FAKE}` - fake posture for tests.\n", encoding="utf-8"
    )
    (root / "README.md").write_text(
        f"# fake\n\n| **Version** | **{FAKE}** tagged (fake) |\n"
        "| **Status** | tags `v1.1.0`, `v2.0.0` frozen |\n",
        encoding="utf-8",
    )
    (root / "docs" / "USER_GUIDE.md").write_text(
        f"# User Guide\n\nHow to run. Reflects the shipped v{FAKE} package.\n",
        encoding="utf-8",
    )
    (root / "docs" / "ARCHITECTURE.md").write_text(
        f"# Architecture\n\nReflects the shipped v{FAKE} package.\n",
        encoding="utf-8",
    )
    (root / "docs" / "METHODOLOGY.md").write_text(
        f"# Methodology\n\n- Package version: `{FAKE}`\n", encoding="utf-8"
    )


def _run(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(TOOL), "--root", str(root)],
        capture_output=True,
        text=True,
        timeout=60,
    )


def _replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"{old!r} not found in {path}"
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_consistent_tree_passes(tmp_path: Path) -> None:
    _write_tree(tmp_path)
    res = _run(tmp_path)
    assert res.returncode == 0, res.stdout + res.stderr
    assert FAKE in res.stdout
    assert "version consistency ok" in res.stdout


@pytest.mark.parametrize(
    ("rel", "old", "new", "expected_file"),
    [
        ("docs/USER_GUIDE.md", f"shipped v{FAKE}", "shipped v0.0.0", "USER_GUIDE.md"),
        # Real current drift shape: USER_GUIDE says "shipped v2.0" (two-component
        # old version) while the package is 3.0.0 - must be flagged as drift.
        ("docs/USER_GUIDE.md", f"shipped v{FAKE}", "shipped v2.0", "USER_GUIDE.md"),
        ("docs/ARCHITECTURE.md", f"shipped v{FAKE}", "shipped v0.0.0", "ARCHITECTURE.md"),
        ("AGENTS.md", f"`{FAKE}`", "`0.0.0`", "AGENTS.md"),
        ("README.md", f"**{FAKE}**", "**0.0.0**", "README.md"),
        ("docs/METHODOLOGY.md", f"`{FAKE}`", "`0.0.0`", "METHODOLOGY.md"),
        ("pyproject.toml", f'"{FAKE}"', '"0.0.0"', "pyproject.toml"),
    ],
)
def test_single_posture_line_tamper_fails(
    tmp_path: Path, rel: str, old: str, new: str, expected_file: str
) -> None:
    _write_tree(tmp_path)
    _replace(tmp_path / rel, old, new)
    res = _run(tmp_path)
    assert res.returncode == 1, res.stdout + res.stderr
    assert expected_file in res.stdout
    assert "VERSION DRIFT" in res.stdout
    assert f"expected: {FAKE}" in res.stdout


def test_sources_disagree_fails(tmp_path: Path) -> None:
    _write_tree(tmp_path)
    _replace(tmp_path / "pyproject.toml", f'"{FAKE}"', '"0.0.0"')
    res = _run(tmp_path)
    assert res.returncode == 1, res.stdout + res.stderr
    assert "pyproject.toml" in res.stdout
    assert "src/cvprofiles/__init__.py" in res.stdout
    assert "0.0.0" in res.stdout


def test_methodology_missing_posture_line_fails(tmp_path: Path) -> None:
    _write_tree(tmp_path)
    (tmp_path / "docs" / "METHODOLOGY.md").write_text(
        "# Methodology\n\nCanonical statement, no version yet.\n", encoding="utf-8"
    )
    res = _run(tmp_path)
    assert res.returncode == 1, res.stdout + res.stderr
    assert "METHODOLOGY.md" in res.stdout
    assert "no current-version posture line" in res.stdout
    assert "Package version" in res.stdout


def test_historical_version_mentions_are_immune(tmp_path: Path) -> None:
    """CHANGELOG entries, tag lists, and old-version prose must not trip it."""
    _write_tree(tmp_path)
    (tmp_path / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 0.1.0 - 2024\n- first release\n"
        "## 2.0.0 - 2026\n- shipped v2.0.0 as the PyPI release\n",
        encoding="utf-8",
    )
    # README already carries the historical "Status" row; add a History
    # section and an old-version prose mention in the guide for good measure.
    (tmp_path / "README.md").write_text(
        (tmp_path / "README.md").read_text(encoding="utf-8")
        + "\n## History\nv1.1.0 and v2.0.0 are superseded releases.\n",
        encoding="utf-8",
    )
    (tmp_path / "docs" / "USER_GUIDE.md").write_text(
        (tmp_path / "docs" / "USER_GUIDE.md").read_text(encoding="utf-8")
        + "Supersedes the v1.1.0-era scaffold (but this is not a 'shipped v' claim).\n",
        encoding="utf-8",
    )
    res = _run(tmp_path)
    assert res.returncode == 0, res.stdout + res.stderr
    assert "version consistency ok" in res.stdout
