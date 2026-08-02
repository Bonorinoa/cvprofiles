"""Package meta + import-graph hygiene (M1)."""

from __future__ import annotations

import ast
import importlib
import subprocess
import sys
from pathlib import Path

import cvprofiles

FORBIDDEN_DEPS = (
    "openai",
    "anthropic",
    "httpx",
    "requests",
    "litellm",
    "google.generativeai",
    "cohere",
)

MUSEUM_MARKERS = (
    "evals.synthetic",
    "v0_poc",
    "evals/synthetic/v0_poc",
)


def test_version() -> None:
    assert cvprofiles.__version__ == "1.0.0a1"


def test_import_core_modules() -> None:
    importlib.import_module("cvprofiles.schemas")
    importlib.import_module("cvprofiles.freeze")
    importlib.import_module("cvprofiles.cli")
    importlib.import_module("cvprofiles.score")
    importlib.import_module("cvprofiles.restrict")
    importlib.import_module("cvprofiles.identify")
    importlib.import_module("cvprofiles.report")


def test_cli_version() -> None:
    proc = subprocess.run(
        [sys.executable, "-m", "cvprofiles", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    out = (proc.stdout or "") + (proc.stderr or "")
    assert "1.0.0a1" in out
    # Console script path (editable install)
    proc2 = subprocess.run(
        ["cvprofiles", "--version"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert "1.0.0a1" in ((proc2.stdout or "") + (proc2.stderr or ""))


def test_no_forbidden_third_party_in_sys_modules_after_import() -> None:
    # Fresh-ish check: none of the forbidden packages should be loaded solely
    # because we imported cvprofiles (they may exist on system — only fail if loaded).
    importlib.import_module("cvprofiles")
    importlib.import_module("cvprofiles.freeze")
    loaded = set(sys.modules)
    for name in FORBIDDEN_DEPS:
        # top-level name
        assert name not in loaded, f"forbidden module loaded: {name}"
        # prefix form
        assert not any(m == name or m.startswith(name + ".") for m in loaded), name


def test_src_has_no_museum_or_llm_imports(repo_root: Path) -> None:
    src = repo_root / "src" / "cvprofiles"
    py_files = list(src.rglob("*.py"))
    assert py_files
    offenders: list[str] = []
    for path in py_files:
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    mod = alias.name
                    if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_DEPS):
                        offenders.append(f"{path}:{mod}")
                    if any(m in mod for m in MUSEUM_MARKERS):
                        offenders.append(f"{path}:museum:{mod}")
            elif isinstance(node, ast.ImportFrom):
                mod = node.module or ""
                if any(mod == f or mod.startswith(f + ".") for f in FORBIDDEN_DEPS):
                    offenders.append(f"{path}:{mod}")
                if any(m in mod for m in MUSEUM_MARKERS):
                    offenders.append(f"{path}:museum:{mod}")
                if any(m in (alias.name or "") for alias in node.names for m in MUSEUM_MARKERS):
                    offenders.append(f"{path}:museum-name")
    assert not offenders, offenders


def test_museum_file_still_present_unimported(repo_root: Path) -> None:
    museum = repo_root / "evals" / "synthetic" / "v0_poc.py"
    assert museum.is_file()
    # Package tree must not reference the path string either (cheap scan).
    src_text = "\n".join(p.read_text() for p in (repo_root / "src" / "cvprofiles").rglob("*.py"))
    assert "v0_poc" not in src_text
    assert "evals.synthetic" not in src_text
