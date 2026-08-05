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

- [x] GitHub Actions `ci` green on `main` (py3.11 + py3.12) — **confirmed by Augusto via GitHub UI** at `9ece618` (not fetched by agent; release review may re-confirm)
- [x] Local CI-equivalent: `uv run ruff check src tests tools`, `uv run mypy src`, and `uv run pytest -q` — **130 passed** (after the MC50 audit suite)
- [x] Package version smoke: `uv run cvprofiles --version` → `1.1.0a1`
- [x] Mini fixture freeze golden matches current package version; `n_boot` is JSON `null` when bootstrap is off
- [x] Synth battery green (H1a FA=0, H1b=1, H3 empty honesty, H4 cold); proof summary audited
- [x] v1.1 bootstrap band computed; empty/degenerate policy honored; headline `[L,U]` unchanged
- [x] v1.1 θ-grid diagnostic surface present; λ=1.0 equals headline; no auto-loosening; grid excluded from freeze preimage
- [x] Tag `v0.1` still resolves to `fb62b48bcb704f60eee7d6641ed0a344eb72bfda`
- [x] Museum present and unimported; no LLM in package import graph
- [x] `docs/12` + `docs/13` updated for the candidate

## Recapture (2026-08-04, post-H5-trust)

- [x] Local CI-equivalent re-verified: **157 passed**; ruff clean; mypy clean (28 files); `cvprofiles 1.1.0a1`; `v0.1` intact
- [x] H5 Trust first frozen run (n=35) accepted as **preliminary paper-facing evidence** (docs/16 §8 run decision; docs/12; `reports/summaries/h5_trust_evidence_summary.json`)
- [x] **Packaging:** `uv build` wheel + sdist build cleanly (removed duplicate force-include); wheel installed in a fresh venv → CLI version smoke, template packaged, H5 run reproduces bit-identical M\* / [L,U]
- [x] Push `main` + CI green on the new head — `fc426fe` **success** (py3.11 + py3.12; mypy fix for numpy 2.5.1 PEP 695 stubs)
- [x] Tag `v1.1.0` — created and pushed 2026-08-04 (Augusto's explicit decision; docs/12)
- [ ] PyPI publication decision — **Augusto only**

## Scope / narrative checks

- [x] Bootstrap/θ-grid framed as **diagnostic / conservative**, not sharp-PI claims
- [x] Headline range still `min/max B*`; inference layers are additive metadata
- [x] Spam audit framed **intermediate only** (not H5); agent-authored R labeled as such
- [x] No force-push / no rewrite of `v0.1`
- [x] PyPI name availability checked (Q19): `https://pypi.org/pypi/cvprofiles/json` returned HTTP **404**; no publish attempted

## Handoff evidence (2026-08-04)

- **Implementation/evidence tree at handoff start:** `784c1be` (`main`, pushed and clean before this close-out)
- **Package:** `1.1.0a1`; final verification recaptured below after the close-out documentation commit
- **Automated evidence:** 121 tests passed; ruff clean; CLI version smoke passed
- **2026-08-04 verification recapture:** 121 tests passed; ruff clean; `cvprofiles 1.1.0a1`; `v0.1` intact; import hygiene passed; museum present; CI green confirmed by Augusto via GitHub UI at `9ece618`.
- **Synthetic evidence:** `reports/summaries/v1_1_package_synth_summary.json`
- **Evidence generator:** `tools/v11_synth_summary.py`; summary generated against parent SHA `098e2fa`
- **Evaluation log:** `docs/13_Evaluations_Log.md` v1.1 row
- **Frozen fixture:** `data/fixtures/mini_v1/expected_freeze.json`
- **Inference run artifacts (ignored, reproducible):** `reports/runs/v1_1_package_synth/`
- **Immutable tag:** `v0.1` → `fb62b48bcb704f60eee7d6641ed0a344eb72bfda`
- **No tag / no PyPI publish:** release-review chat and Augusto own those decisions
- **Explicit exclusions:** no H5, no USER empirical network, no sharp-PI claim, no δ-grid, no measure generation, no museum import

## Explicit non-blockers

- PyPI publish (separate decision)
- Full paper prereg freeze
- H5 / USER empirical network
- Sharp PI theory

## After promotion

- Tag (e.g. `v1.1.0`) **only** via release-review chat + Augusto
- CHANGELOG promotion entry
- Open v1.2 backlog: δ-grid, `mean_order`/`rank_agree` evaluators, `ols_coef`, LaTeX report
