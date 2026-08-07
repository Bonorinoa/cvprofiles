"""Scan markdown for LaTeX-style math delimiters outside code fences / inline code.

Phase 0 math sweep safety check: find every literal \\( \\) \\[ \\] occurrence
that is NOT inside a fenced code block or inline code span, so we know exactly
what the delimiter converter must touch.

Usage:
  python tools/scan_math_delims.py            # report occurrences, exit 0
  python tools/scan_math_delims.py --check    # exit 1 if any occurrence (CI)
"""

from __future__ import annotations

import pathlib
import re
import sys

FILES = [pathlib.Path("README.md"), *sorted(pathlib.Path("docs").glob("*.md"))]


def main() -> int:
    check = "--check" in sys.argv[1:]
    issues: list[str] = []
    in_fence = False
    for p in FILES:
        for i, line in enumerate(p.read_text().splitlines(), 1):
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_fence = not in_fence
                continue
            if in_fence:
                for marker in ("\\(", "\\)", "\\[", "\\]"):
                    if marker in line:
                        issues.append(f"{p}:{i} INSIDE-FENCE {marker}: {line.strip()[:80]}")
                continue
            # outside fences: split out inline code spans, inspect the rest
            for seg in re.split(r"`[^`]*`", line):
                for marker in ("\\(", "\\)", "\\[", "\\]"):
                    if marker in seg:
                        issues.append(f"{p}:{i} PROSE {marker}: {seg.strip()[:80]}")
    if issues:
        print(f"occurrences outside fences/inline-code: {len(issues)}")
        for x in issues:
            print(x)
        return 1 if check else 0
    print("no LaTeX-style math delimiters outside code (backslash-paren / backslash-bracket)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
