# Changelog

All notable project milestones live here. Detailed decisions → `docs/12_Decision_Engineering_Log.md`. Eval learnings → `docs/13_Evaluations_Log.md`.

Format: keep newest first.

## [2.5.1] — 2026-08-09 (tagged; PyPI publish pending tutorial polish)

First PyPI release since 2.0.0: CLI exposure of the v2.5.0 engine features + docs synced to shipped state + version-consistency CI check.

### CLI (audit B, P0)
- `--holdout-units` (comma-separated unit ids; select on train, verdict on hold; headline = M\*_robust; order-normalized sorted-unique in freeze config; forks run_id)
- `--alpha` (coverage band tail probability, default 0.10) and `--kappa` (boundary attribution rule, default 2.0); validation mirrors inference/coverage.py; excluded from freeze preimage
- stdout-JSON / stderr-notes contract preserved; empty M\* exits 0

### Docs (audit A1-A3, D2, D5)
- USER_GUIDE / METHODOLOGY / README / ARCHITECTURE synced to shipped v2.5.0 engine (holdout stage + units-split, coverage band, corr_zero / monotone_rank, diff_means / map_distance; θ thresholds on raw sample-statistic scale)
- README install-from-source pins v2.5.1; "main is development; tags are the paper anchors"
- WVS/GPS lane README: cross-repo SCA2 data dependency + WVS Wave 7 no-direct-risk-item disclosure

### CI (audit D4)
- tools/check_version_consistency.py asserts posture docs (AGENTS / README / USER_GUIDE / METHODOLOGY / ARCHITECTURE) match __version__ on every bump; hermetic tests

### Boundary
- v3.0.0 remains Gate C; paper protocol fields remain Augusto-owned

## [2.5.0] — 2026-08-08 (tag `v2.5.0` — engine infrastructure checkpoint; **not** on PyPI)

Rev 3 P1–P5 engine go closed (synthetic-first). Latest PyPI remains `2.0.0`. Target `v3.0.0` remains Gate C.

### Engine (P2–P5)
- **Evaluators:** `corr_zero` (two-sided discriminant), `monotone_rank` (signed Spearman vs continuous V)
- **Betas:** `diff_means` (binary group mean gap), `map_distance` (2D Euclidean on pinned loadings; no PCA fit inside the engine)
- **Holdout:** restriction-level `stage: select|holdout` (freeze-safe optional field) + **units-split** (select on train units, compliance on hold units; robust headline)
- **Coverage uncertainty band (D1):** additive layer over units-only bootstrap — per-side α/2 quantiles (default α=0.10), empty-replicate rate, boundary attribution $|\mathrm{margin}_m| \le \kappa\cdot\mathrm{SE}_m$ (default κ=2), admission frequency $\hat p_m$. Honest label only (never CI / coverage guarantee). Headline $[L,U]=\min/\max B^*$ unchanged. α/κ excluded from freeze preimage.

### Boundary
- Tag only — **no PyPI upload** at 2.5.0
- P6 (benchmark kit / IVS harness / synthetic verifier / teaching notebook), Gate B empirical run, and Gate C `v3.0.0` remain deferred
- Paper protocol fields remain Augusto-owned

## [Unreleased] — dev 2.0.1a1 (docs consolidation + tooling + tutorials, 2026-08-07; tag `v2.0.1a1` dev checkpoint)

### Tutorials (Phase 3)
- **`tutorials/cvprofiles_irt_scoring_tutorial.ipynb`** — IRT as a SCORE-upstream scoring technology: hand-rolled 1PL (Rasch) fit (numpy + scipy, auditable), person scores → measure columns → profile; IRT and sum score both admitted, noisy measure rejected. Executed against the wheel in a fresh venv: all assertions pass.
- **`tutorials/cvprofiles_sensemakr_tutorial.ipynb`** — OVB sensitivity on a survivor: hand-rolled Cinelli–Hazlett (2020) implementation (partial R², exact OVB identity, robustness value RV_q); confirms the identity recovers the full-model coefficient. Executed against the wheel in a fresh venv: all assertions pass.
- Both regenerable from `tools/build_tutorials.py`.

### Tooling / docs (Phases 0–2, 2026-08-06/07)
- **Public doc consolidation** — `docs/METHODOLOGY.md`, `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md` written from shipped state in researcher voice; pre-ship scaffold archived (`docs/archive/`, mapping README); README rewritten (install+quickstart early, contracts first-class, positioning, Hermes acknowledgment); governance locks 12/13/16/17 kept live.
- **Batch orchestrator** — `tools/run_many.py`: one shared score matrix, N (network, beta) profiles from a YAML manifest, per-profile frozen run dirs + `batch_summary.json`; machine-JSON stdout; empty M* exit-0; fail-loud `BatchError`. 5 tests.
- **Math delimiter sweep** — all markdown docs converted to GitHub-KaTeX `$...$`/`$$...$$`; `tools/scan_math_delims.py --check` wired into CI.

### Boundary
- Tag `v2.0.1a1` marks a dev checkpoint, not a release; paper protocol and PyPI publication remain Augusto's.

## [Unreleased] — dev 2.0.1a1 (post-release audit follow-up, 2026-08-06)

### Hardening
- **CI wheel smoke** — new `wheel-smoke` job: `uv build` → fresh-venv install of the wheel → mini-fixture profile run from the installed package (R1; catches packaging regressions the editable smoke cannot)
- **Coverage measured** — `pytest-cov` in dev extras; CI pytest step reports coverage (no gate); local 88% of `cvprofiles` (1563 stmts, 185 missed) (R2)
- **Observable parquet fallback** — `slacks.parquet` write failures now warn on stderr instead of being swallowed; CSV remains authoritative (M4)
- **Deprecation warnings un-suppressed** — blanket `ignore::DeprecationWarning` removed; suite green with none surfacing (M5)
- **SPDX license metadata** — `license = "MIT"` (PEP 639); `uv build` verified (`License-Expression: MIT`, templates packaged) (R5)

### Docs / contract fixes
- docs/03 `corr_min` row corrected: **signed lower bound** `Corr(m,V) ≥ θ` (slack `Corr − θ`), not absolute correlation (M1; engine semantics canonical)
- docs/17 pinned-network example uses `sign: -1` (engine schema), not `direction:` (M2; pinned input already correct)
- `docs/PROJECT_MANIFEST.md` `dev_version` refreshed to `2.0.1a1` (R4)
- `tools/verify_h5_trust.py` docstring documents the exact invocation and its two traps (`--proof` = proof artifact; `--out-root` = run-artifacts dir)

### Tutorial
- **`tutorials/cvprofiles_diagnostics_tour.ipynb`** — v2.0 measure-discipline tour: all four restriction evaluators, `ols_coef` with controls, bootstrap + θ-grid + δ-grid + anchors in one run, CLI, self-checking assertions; executed against `pip install cvprofiles==2.0.0` in a fresh venv — ALL ASSERTIONS PASSED, deterministic run_id

### Boundary
- PyPI landing description staleness (R3) deferred to the next release (same-version re-upload forbidden); OIDC publish automation (R6) deferred — the user-owned token flow stays the deliberate posture
- **B4 methodology statement LOCKED** (2026-08-06, Option B — framework + inference stance in docs/03; Augusto-approved) — **all v2.0-DONE criteria now complete**

## [2.0.0] — 2026-08-06 (published on PyPI; tag `v2.0.0`)

### Measure discipline (v2.0, ENTRY complete 2026-08-05)

- **δ-grid tolerance layer** — absolute-δ sensitivity surface (`--delta-grid`, `delta_grid.json`, HTML/JSON panels); `delta_override` on `run_identify`; grid excluded from the freeze preimage (same bundle + different grid ⇒ same `run_id`)
- **Evaluator registry growth** — `mean_order` (binary 0/1 group, signed gap), `rank_agree` (Spearman, ties averaged), `ols_coef` (standardized numpy closed form, no statsmodels); `stability`/`diff_means` stay schema-only fail-loud
- **θ-anchor documentation discipline** — schema'd `anchors.yaml` (`cvprofiles.anchors`), completeness vs the pinned network, `anchors_hash` in manifest (excluded from the freeze preimage), HTML audit panel, CLI `--anchors`; H5 Trust transcription `evals/h5_trust/data/anchors_h5_trust.yaml` audited exit 0
- **Independent notebook tutorial** — `tutorials/cvprofiles_tutorial.ipynb`: synthetic walk-through first, then H5 replication; verified against the PyPI package (`pip install cvprofiles==2.0.0`): M\*={m_trust_general, m_trust_in_group}, [L,U] bit-identical
- **First PyPI publication** — version aligned `2.0.0` (2026-08-06); wheel + sdist uploaded; provenance verified (local wheel sha256 == PyPI sha256 `a125ae1d…`)
- Version spine: `2.0.0` on the release commit; dev cycle may resume at `2.0.1a1` later

### Boundary
- v1.1-era proof artifacts and the MC50 verifier's expected version remain at `1.1.0a1` (historical evidence)
- Paper protocol fields remain Augusto-owned; H5 numbers remain preliminary paper-facing evidence

## [1.1.0] — 2026-08-04 (MVP tag `v1.1.0`; PyPI publication separate)

### Engine — v1.1 inference layer (shipped on `main` as dev `1.1.0a1`)

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

### Tag `v1.1.0` (2026-08-04)

- Annotated tag `v1.1.0` created and pushed (Augusto's explicit decision) — symbolizes the MVP: v1.0 spine + v1.1 inference layer + H5 Trust preliminary evidence + packaging/CI fixes
- Tag-as-symbolization convention (v0.1 precedent): wheel remains dev `1.1.0a1`; PyPI publication is a separate decision with version alignment at publish time

## [Unreleased]

### Planned

- Measure discipline: δ-grid, evaluator registry growth (`mean_order`/`rank_agree`/`ols_coef`), θ-anchor documentation discipline
- H5 robustness checks + extensions (v2.0 roadmap)

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
