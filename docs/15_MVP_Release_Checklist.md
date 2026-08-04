# MVP release checklist (v1.1 candidate)

**Purpose:** evaluate whether current `main` is promotable as an MVP (v1.1 candidate).
Tag / release decision is owned by the sibling release-review chat + Augusto — this checklist **feeds** that decision; it does not replace it.

**Supersedes:** the former branch-merge checklist (`feat/realworld-spam`), which was merged and deleted.

## Candidate contents

- v1.0 thin spine: SCORE → RESTRICT → IDENTIFY → thin REPORT, `[L,U]=min/max B*`
- M8 package-native synth battery (H1a / H1b / H3 / H4 green)
- M9 minimal CI (pytest / ruff / CLI / import-hygiene / mini smoke on py3.11+3.12)
- Intermediate real-world spam audit (**not** H5)
- **v1.1:** bootstrap over units + θ-grid sensitivity surface (diagnostic)

## Must be green before promotion

- [ ] GitHub Actions `ci` green on `main` (py3.11 + py3.12)
- [ ] `uv sync --extra dev && uv run ruff check src tests && uv run pytest -q` green
- [ ] Mini fixture SCORE→REPORT smoke green; golden hashes match **current** `package_version`
- [ ] Synth battery green (H1a FA=0, H1b=1, H3 empty honesty, H4 cold)
- [ ] v1.1: bootstrap band computed; empty-replicate policy honored; headline `[L,U]` unchanged
- [ ] v1.1: θ-grid diagnostic surface present; **no** auto-loosening of θ
- [ ] Tag `v0.1` still `fb62b48`
- [ ] Museum present and unimported; no LLM in package import graph
- [ ] `docs/12` + `docs/13` updated for the candidate

## Scope / narrative checks

- [ ] Bootstrap/θ-grid framed as **diagnostic / conservative**, not sharp-PI claims
- [ ] Headline range still `min/max B*`; inference layers are additive metadata
- [ ] Spam audit framed **intermediate only** (not H5); agent-authored R labeled as such
- [ ] No force-push / no rewrite of `v0.1`
- [ ] PyPI name availability checked (Q19) before any publish intent

## Explicit non-blockers

- PyPI publish (separate decision)
- Full paper prereg freeze
- H5 / USER empirical network
- Sharp PI theory

## After promotion

- Tag (e.g. `v1.1.0`) **only** via release-review chat + Augusto
- CHANGELOG promotion entry
- Open v1.2 backlog: δ-grid, `mean_order`/`rank_agree` evaluators, `ols_coef`, LaTeX report
