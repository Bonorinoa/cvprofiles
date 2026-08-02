# Merge safety checklist — feat/realworld-spam → main

**Purpose:** evaluate whether this branch is safe to merge into `main`.  
**Not a release checklist.** Tag `v1.0.0` is still owned by the sibling release chat / Augusto.

## Branch contents (beyond `main` @ `29bdea1`)

1. **M9 CI** — `.github/workflows/ci.yml` (pytest + ruff + mini smoke on 3.11/3.12)
2. **Intermediate real-world audit** — `evals/realworld/spam_validity/` (NOT H5 / not paper path)
3. Docs/log updates for M9 + intermediate audit

## Must be green before merge

- [ ] GitHub Actions `ci` green on this branch (PR or push)
- [ ] Local: `uv sync --extra dev && uv run ruff check src tests && uv run pytest -q`
- [ ] Local: mini CLI smoke (same as CI step)
- [ ] Tag `v0.1` still `fb62b48` (`git rev-parse v0.1^{}`)
- [ ] Museum `evals/synthetic/v0_poc.py` present and unimported by `src/`
- [ ] No LLM client in package import graph
- [ ] `package_version` still `1.0.0a1` (or goldens refreshed if bumped)

## Scope / narrative checks

- [ ] Spam audit framed as **intermediate only** (README + `docs/13`) — not main-path H5
- [ ] Agent-authored spam network not presented as USER empirical theory
- [ ] M6 bootstrap still out of tree / deferred to v1.1
- [ ] No force-push / no rewrite of `v0.1`

## After merge (recommended, not automatic)

- [ ] Confirm CI runs on `main`
- [ ] Decide M9-only backport vs keep audit on main (audit is fine on main if labeled intermediate)
- [ ] Do **not** tag `v1.0.0` from merge alone — run sibling acceptance list

## Explicit non-blockers for merge

- No bootstrap/θ-grid (by design)
- No PyPI publish
- No full paper prereg freeze
- Spam audit does not need sklearn in default package deps (audit is evals-only; CI does not require it)
