# Changelog

All notable project milestones live here. Detailed decisions → `docs/12_Decision_Engineering_Log.md`. Eval learnings → `docs/13_Evaluations_Log.md`.

Format: keep newest first.

## [Unreleased]

### Planned
- Package `src/cvprofiles` layout (M1+)
- Bootstrap / θ-grid
- `AGENTS.md`
- Paper prereg freeze
- Public baseline H5 (USER-authored network only)

### Added (post-v0.1 on main)
- `docs/14_Researcher_Input_Guide.md` — DRAFT process guide for composites, anchors, SCORE/RESTRICT prep (not part of tag `v0.1`)

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
