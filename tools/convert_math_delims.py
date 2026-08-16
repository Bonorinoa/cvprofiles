"""Convert LaTeX-style math delimiters to GitHub-compatible $ delimiters in markdown.

Rules (Phase 0 math sweep, docs/12 2026-08-06):
- Outside fenced code blocks and inline code spans only (never touch code).
- \\( ... \\)  ->  $ ... $
- \\[ ... \\]  ->  $$ ... $$
- Double-escaped variants (2+ backslashes before the delimiter) -> single $.
- Display environments: \\begin{align*} -> \\begin{aligned} (KaTeX-safe on GitHub).

Notebooks (.ipynb) are intentionally NOT converted: Jupyter renders \\(...\\)
natively via MathJax, and the tutorials must keep working in Jupyter.
"""

from __future__ import annotations

import pathlib
import re

FILES = [pathlib.Path("README.md"), *sorted(pathlib.Path("docs").glob("*.md"))]

# Order matters: 2+-backslash variants first, then single backslash.
_PAREN_OPEN = re.compile(r"\\{1,2}\(")
_PAREN_CLOSE = re.compile(r"\\{1,2}\)")
_BRACKET_OPEN = re.compile(r"\\{1,2}\[")
_BRACKET_CLOSE = re.compile(r"\\{1,2}\]")


def _convert_segment(seg: str) -> str:
    out = _BRACKET_OPEN.sub("$$", seg)
    out = _BRACKET_CLOSE.sub("$$", out)
    out = _PAREN_OPEN.sub("$", out)
    out = _PAREN_CLOSE.sub("$", out)
    return out


def _convert_prose(line: str) -> str:
    """Convert math only in the non-inline-code parts of a prose line."""
    parts = re.split(r"(`[^`]*`)", line)
    return "".join(_convert_segment(p) if not p.startswith("`") else p for p in parts)


def convert_file(p: pathlib.Path) -> int:
    """Convert one file; return number of lines changed."""
    text = p.read_text()
    lines = text.splitlines()
    out: list[str] = []
    in_fence = False
    changed = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("```") or stripped.startswith("~~~"):
            in_fence = not in_fence
            out.append(line)
            continue
        if in_fence:
            out.append(line)
            continue
        new = _convert_prose(line)
        # KaTeX-safe environment rename only in display blocks ($$ ... $$).
        new = new.replace("\\begin{align*}", "\\begin{aligned}")
        new = new.replace("\\end{align*}", "\\end{aligned}")
        if new != line:
            changed += 1
        out.append(new)
    p.write_text("\n".join(out) + ("\n" if text.endswith("\n") else ""))
    return changed


def main() -> None:
    total = 0
    for p in FILES:
        n = convert_file(p)
        total += n
        print(f"{p}: {n} lines changed")
    print(f"total lines changed: {total}")


if __name__ == "__main__":
    main()
