"""Check that every current-version posture claim matches the package version.

Audit D4 (docs-version drift class): the package version has two sources of
truth -- ``pyproject.toml`` (packaging) and ``src/cvprofiles/__init__.py``
(``__version__``) -- and several docs carry "current posture" version claims
that have historically drifted from the engine. This tool asserts they all
agree, so the drift class cannot silently reopen.

Only CURRENT-posture lines are checked. Historical lines that legitimately
name old versions (CHANGELOG entries, release bullets, tag lists) are never
matched: every regex below is anchored to its posture line's shape.

Contract table (file -> regex -> rationale):

  src/cvprofiles/__init__.py
    ^__version__ = "(\\d+\\.\\d+\\.\\d+)"
    Runtime source of truth; the CLI and wheel read it. Every doc claim is
    compared against this.

  pyproject.toml
    ^version = "(\\d+\\.\\d+\\.\\d+)"
    Packaging source of truth; must equal __version__ (first top-level
    `version =` line, i.e. the [project] table).

  AGENTS.md
    ^(?:-\\s*)?Package version:.*?`(\\d+\\.\\d+\\.\\d+)`
    The "Current posture" bullet agents read as the operative package
    version. Historical release notes later in the same line are ignored.

  README.md
    ^\\|\\s*\\*\\*Version\\*\\*\\s*\\|\\s*\\*\\*(\\d+\\.\\d+\\.\\d+)\\*\\*
    The "Version" row of the header table users see as current release
    posture. The adjacent "Status" row (historical tag list) must NOT match.

  docs/USER_GUIDE.md
    shipped v(\\d+\\.\\d+(?:\\.\\d+)?)
    The guide's claim about which package it reflects. Accepts both the
    current two-component spelling ("shipped v2.0") and the canonical
    three-component one ("shipped v2.5.0"); both must equal __version__.
    Keep the phrase "shipped vX.Y.Z" when rewording line 3.

  docs/ARCHITECTURE.md
    (?i)reflects the shipped v(\\d+\\.\\d+(?:\\.\\d+)?)
    The design doc's intro claim about which package generation it
    describes; same drift shape as USER_GUIDE's intro claim. (?i) so the
    sentence-start "Reflects" spelling is accepted.

  docs/METHODOLOGY.md
    ^(?:-\\s*)?Package version:.*?`(\\d+\\.\\d+\\.\\d+)`
    The canonical method statement must name the engine version it
    describes. The line is currently ABSENT in the repo: add
    "- Package version: `X.Y.Z`" (mirroring AGENTS.md) to the header.

Usage:
  python tools/check_version_consistency.py             # repo root
  python tools/check_version_consistency.py --root DIR  # arbitrary tree

Exit 0 when everything agrees; exit 1 with a per-file report otherwise.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

VERSION_RE = r"\d+\.\d+\.\d+"
INIT_REL = "src/cvprofiles/__init__.py"
PROJECT_REL = "pyproject.toml"
INIT_PATTERN = rf'^__version__ = "({VERSION_RE})"'
PROJECT_PATTERN = rf'^version = "({VERSION_RE})"'


@dataclass(frozen=True)
class Spec:
    rel: str
    pattern: str
    hint: str = ""


DOC_SPECS: tuple[Spec, ...] = (
    Spec(
        "AGENTS.md",
        rf"^(?:-\s*)?Package version:.*?`({VERSION_RE})`",
        'keep the "- Package version: `X.Y.Z`" bullet under Current posture',
    ),
    Spec(
        "README.md",
        rf'^\|\s*\*\*Version\*\*\s*\|\s*\*\*({VERSION_RE})\*\*',
        'keep the "| **Version** | **X.Y.Z** |" row in the header table',
    ),
    Spec(
        "docs/USER_GUIDE.md",
        r"shipped v(\d+\.\d+(?:\.\d+)?)",
        'keep the phrase "shipped vX.Y.Z" when rewording the intro',
    ),
    Spec(
        "docs/ARCHITECTURE.md",
        r"(?i)reflects the shipped v(\d+\.\d+(?:\.\d+)?)",
        'keep the phrase "reflects the shipped vX.Y.Z package" in the intro',
    ),
    Spec(
        "docs/METHODOLOGY.md",
        rf"^(?:-\s*)?Package version:.*?`({VERSION_RE})`",
        'add a posture line to the METHODOLOGY header: "- Package version: `X.Y.Z`" '
        "(mirroring AGENTS.md), so the method statement cannot drift from the engine",
    ),
)


@dataclass
class Finding:
    rel: str
    lineno: int
    expected: str
    found: str | None
    line: str
    hint: str = ""


def _first_match(root: Path, rel: str, pattern: str) -> tuple[int, str] | None:
    """Return (lineno, captured version) of the first posture match, or None."""
    path = root / rel
    if not path.is_file():
        return None
    compiled = re.compile(pattern)
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        m = compiled.search(line)
        if m:
            return lineno, m.group(1)
    return None


def _line_at(root: Path, rel: str, lineno: int) -> str:
    lines = (root / rel).read_text(encoding="utf-8").splitlines()
    if 0 < lineno <= len(lines):
        return lines[lineno - 1]
    return "<line unavailable>"


def _report(expected: str, findings: list[Finding]) -> None:
    print("VERSION DRIFT - package version must match across sources and docs.")
    print(f"  expected: {expected}   ({INIT_REL})")
    for f in findings:
        print(f"  file:     {f.rel}")
        if f.found is None:
            print("  found:    (no current-version posture line)")
        else:
            print(f"  found:    {f.found}")
        if f.lineno:
            shown = f.line if len(f.line) <= 100 else f.line[:97] + "..."
            print(f"  line {f.lineno}: {shown}")
        if f.hint:
            print(f"  hint:     {f.hint}")
        print()
    print("Fix the drift above so docs cannot describe a version the engine is not.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Assert docs posture versions match the package version."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repo root to check (default: derived from this script's location)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()

    findings: list[Finding] = []

    init = _first_match(root, INIT_REL, INIT_PATTERN)
    proj = _first_match(root, PROJECT_REL, PROJECT_PATTERN)
    if init is None:
        findings.append(
            Finding(INIT_REL, 0, "?", None, "<no __version__ found>",
                    "add __version__ = \"X.Y.Z\" to src/cvprofiles/__init__.py")
        )
    if proj is None:
        findings.append(
            Finding(PROJECT_REL, 0, "?", None, "<no version found>",
                    "add version = \"X.Y.Z\" to the [project] table of pyproject.toml")
        )
    if init is None or proj is None:
        _report("?", findings)
        return 1

    expected = init[1]
    if proj[1] != expected:
        findings.append(
            Finding(
                PROJECT_REL, proj[0], expected, proj[1],
                _line_at(root, PROJECT_REL, proj[0]),
                "pyproject.toml and __init__.py disagree; packaging must equal "
                "the runtime __version__",
            )
        )

    for spec in DOC_SPECS:
        got = _first_match(root, spec.rel, spec.pattern)
        if got is None:
            findings.append(
                Finding(spec.rel, 0, expected, None, "<no matching posture line>",
                        spec.hint)
            )
        elif got[1] != expected:
            findings.append(
                Finding(spec.rel, got[0], expected, got[1],
                        _line_at(root, spec.rel, got[0]), spec.hint)
            )

    if findings:
        _report(expected, findings)
        return 1
    print(
        "version consistency ok: "
        f"{expected} across __init__, pyproject.toml, AGENTS.md, README.md, "
        "USER_GUIDE.md, METHODOLOGY.md, ARCHITECTURE.md"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
