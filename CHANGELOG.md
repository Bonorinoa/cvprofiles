# Changelog

All notable project milestones live here. Detailed decisions → `docs/12_Decision_Engineering_Log.md`. Eval learnings → `docs/13_Evaluations_Log.md`.

Format: keep newest first.

## [Unreleased]

### Added
- **M1 / G1:** installable `src/cvprofiles` (`1.0.0a1`) + `pyproject.toml` + thin CLI
- Pydantic v2 schemas (scores / network / beta / freeze run manifests)
- Freeze hash + `run_id` util (`cvprofiles.freeze`); algorithm locked in `docs/12`
- Mini fixture `data/fixtures/mini_v1/` + golden `expected_freeze.json`
- Contract tests (schemas, freeze bit-stability, import-graph hygiene, mini load)
- **Phase 0 (v1.0 sprint start):** scope box — thin first-principles spine; M6 bootstrap/θ-grid deferred to v1.1; no M10 this sprint
- Past-tense docs: public repo + tag `v0.1` @ `fb62b48` live; G7/G8 re-enter from G5 for v1.0; H1a/H1b gates + H1_latent diagnostic pointers
- `docs/14_Researcher_Input_Guide.md` — DRAFT process guide for composites, anchors, SCORE/RESTRICT prep (not part of tag `v0.1`)

### Planned (v1.0 spine)
- M2 SCORE → M3 RESTRICT → M4/M5 IDENTIFY → M7 thin REPORT
- Synth harness re-impl under package/tests (H1a / H2 / H3 / H4) — M8
- Minimal CI + install polish — M9

### Planned (later)
- Bootstrap / θ-grid (**v1.1**, not v1.0)
- `AGENTS.md`
- Paper prereg freeze
- Public baseline H5 (USER-authored network only)

## [0.1.0] — 2026-08-01

**Symbolizes v0.1:** methods knowledge base + green synthetic PoC (museum monolith).  
**Not** a PyPI release. **Not** the package API.

### Added
- Project scaffold under `~/Hermes/Projects/cvprofiles`
- Methods-first documentation suite (`docs/01`–`13`, `PROJECT_MANIFEST.md`)
- Dual live logs (decision/engineering + evaluations)
- MIT `LICENSE`
- **`evals/synthetic/v0_poc.py`** monolith (`POC_VERSION=v0_1_poc`) — SCORE→REPORT synthetic battery with gate check
- Proof summary `reports/summaries/v0_1_poc_summary.json`

### Fixed / learned
- **v0 → v0.1 hygiene:** distinct `oracle_with_slop`; true empty `all_invalid`; cold determinism; near_miss fails by design
- **H1 split locked:** H1a/H1b gates; H1_latent diagnostic only (attenuation); no \(\theta\)-loosening
- v0.1 battery **exit 0** (FA=0, empty honesty, anchor retention, cold OK)

### Explicit non-contents
- No `src/cvprofiles` package layout
- No bootstrap / θ-grid inference layer
- No real-data baseline / H5 network
- No LLM inside the engine
