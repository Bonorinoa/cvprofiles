# Changelog

All notable project milestones live here. Detailed decisions → `docs/12_Decision_Engineering_Log.md`. Eval learnings → `docs/13_Evaluations_Log.md`.

Format: keep newest first.

## [Unreleased]

### Shipped on `main` (v1.1 dev package `1.1.0a1`; release review pending)

- Bootstrap over observational units (percentile band over non-empty replicates; empty/degenerate counts reported) — **M6 inference layer**
- Deterministic θ-grid sensitivity surface (diagnostic; λ scales threshold magnitudes only; headline stays λ=1.0; grid excluded from freeze preimage)
- Additive pipeline, CLI (`--n-boot`, `--theta-grid`), JSON/HTML audit panels, and stale-layer cleanup
- Package-native battery and inference evidence: `reports/summaries/v1_1_package_synth_summary.json`
- MVP release checklist: `docs/15_MVP_Release_Checklist.md` (feeds release-review chat)
- Verification close-out: local ruff clean, 121 tests passed, version smoke and tag checks passed; GitHub Actions green confirmed by Augusto; no tag or PyPI publication attempted
- PyPI name availability checked (HTTP 404); publication decision remains open and is **not** part of v1.1
- Independent MC50 proof audit: `tools/verify_v11_protocol_synth_mc50.py` + `tests/test_v11_protocol_synth_mc50_audit.py` validate the provisional synthetic-only protocol table in a read-only pass
- Strict typing enforcement: `uv run mypy src` is green and enforced in CI; `ruff` now also lints `tools/` in CI
- Protocol/release documentation reconciliation: README/manifest/open-questions now reflect the provisional synthetic-only lock (`docs/16`), the MC50 proof table, and the new `AGENTS.md`; release posture unchanged

### H5 Trust — first paper-facing evaluation (2026-08-04)

- **Design lock:** `docs/17_H5_Trust_Design.md` — country-level generalized trust; WVS7 × GPS × WDI/WGI; pinned network (gps_trust 0.3 / rule_of_law 0.3 / gini −0.1); δ=0; β=corr_y on log GDP pc; claims boundary
- **First frozen build:** n=35 countries; `evals/h5_trust/build_dataset.py` (masking, aggregation, coverage rule, canonical hashes); reproducible `--fetch-wdi`/`--fetch-wgi`
- **Preliminary paper-facing evidence (owner-approved 2026-08-04):** M\*={m_trust_general, m_trust_in_group}, [L,U]=[0.371, 0.624], FA=0, cold H4; θ-grid empties at λ≥1.5; bootstrap band [0.174, 0.752] with 17.5% empty replicates
- Tracked summary: `reports/summaries/h5_trust_evidence_summary.json`; auditors `tools/verify_h5_trust.py` + `tools/verify_v11_protocol_synth_mc50.py`
- **Boundary:** preliminary checkpoint; final paper lock, tag, PyPI, and push remain Augusto's

### Release posture (2026-08-04)

- **Packaging fix:** removed duplicate hatchling force-include that broke `uv build` (report.html.j2 added twice); wheel now builds cleanly
- **Wheel verified from a fresh venv:** template packaged, console script works, H5 run reproduces bit-identical M\* and [L,U]
- Release checklist recaptured: 157 tests passed, ruff/mypy clean, `v0.1` intact; tag `v1.1.0` and PyPI publication remain Augusto + release-review decisions

## [1.0.0a1] — 2026-08-01 (spine shipped on `main`)

**v1.0 thin first-principles spine** — SCORE → RESTRICT → IDENTIFY → thin REPORT with `[L,U]=min/max B*`, freeze hashes, mini fixture, package-native synth battery, minimal CI, and an intermediate real-world spam audit (not H5). Merged to `main` @ `3be6367`. Tag decision owned by release-review chat.

### Added
- **M9 / minimal CI:** `.github/workflows/ci.yml` — uv sync, ruff, pytest, CLI smoke, import-graph hygiene, mini fixture SCORE→REPORT on Python 3.11/3.12
- **Intermediate real-world audit:** `evals/realworld/spam_validity/` — 20newsgroups multi-measure spamminess stress; `verify_audit.py` exit 0; FA=0; harsh empty; cold H4; **not** main-path H5
- **M8 / G8:** package-native synth harness (`src/cvprofiles/synth/`); battery drives real SCORE→RESTRICT→IDENTIFY; H1a/H1b/H3/H4 **green** on seeds `0..4`, \(n=1000\); H1_latent diagnostic only (attenuation → 0); proof `reports/summaries/v1_0_package_synth_summary.json`; museum unimported
- **M7 / G7:** thin REPORT (HTML/JSON); `run_profile` SCORE→REPORT composition; CLI `cvprofiles run` (stdout JSON / stderr crumbs); empty-\(M^*\) first-class; e2e on mini_v1 oracle + harsh
- **M5 / G5:** \(\beta=\mathrm{corr}_y\); \([L,U]=\min/\max B^*\) on survivors only; empty/point-ID flags; `range.json` notes bootstrap deferred to v1.1
- **M4 / G4:** IDENTIFY slacks (`corr_min`, `corr_sign`); \(M^*\) + rejection reasons; harsh empty fixture (`network_harsh.yaml`, \(\theta=0.999\)); FA=0 on `m_slop`
- **M3 / G3:** RESTRICT load/bind network+beta; `RestrictError` at IO boundary; golden network/beta hashes
- **M2 / G2:** SCORE pipeline (`run_score` / `write_score_artifacts`); default normalization `none`; optional `zscore_measures` on measures only; fail-loud on missing cols / empty / dup unit_id / non-finite; golden `scores_hash` match on mini_v1
- **M1 / G1:** installable `src/cvprofiles` (`1.0.0a1`) + `pyproject.toml` + thin CLI
- Pydantic v2 schemas (scores / network / beta / freeze run manifests)
- Freeze hash + `run_id` util (`cvprofiles.freeze`); algorithm locked in `docs/12`
- Mini fixture `data/fixtures/mini_v1/` + golden `expected_freeze.json`
- Contract tests (schemas, freeze bit-stability, import-graph hygiene, mini load)
- **Phase 0 (v1.0 sprint start):** scope box — thin first-principles spine; M6 bootstrap/θ-grid deferred to v1.1; no M10 this sprint
- Past-tense docs: public repo + tag `v0.1` @ `fb62b48` live; G7/G8 re-enter from G5 for v1.0; H1a/H1b gates + H1_latent diagnostic pointers
- `docs/14_Researcher_Input_Guide.md` — DRAFT process guide for composites, anchors, SCORE/RESTRICT prep (not part of tag `v0.1`)

### Planned (later)
- Paper prereg freeze
- Public baseline H5 (USER-authored network only)
- δ-grid, `mean_order`/`rank_agree` evaluators, `ols_coef`, LaTeX report (post-MVP backlog)

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
