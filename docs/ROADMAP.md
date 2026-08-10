# Roadmap

**Live document.** This is the current-state roadmap for cvprofiles. It evolves together with the engineering log (`docs/12_Decision_Engineering_Log.md`) — when scope changes, the roadmap and the log change in the same review. The README carries only current posture, not this history.

## Shipped

### v1.0 (2026-08-01 — thin first-principles spine)

1. **Schemas + freeze contract** — typed score matrix, network, β, run manifest
2. **SCORE → RESTRICT → IDENTIFY** — slacks, M\*, [L,U] = min/max B\* (no bootstrap)
3. **Thin REPORT** — HTML/JSON; empty M\* is a clean success
4. **Synth harness re-impl** under package/tests (H1a / H2 / H3 / H4; H1_latent diagnostic)
5. **Installable package + minimal CI**

### v1.1 (tagged `v1.1.0` 2026-08-04 — MVP; superseded by v2.0.0)

- Units-only bootstrap with conservative, additive percentile diagnostics
- Deterministic θ-grid sensitivity surface; headline remains [L,U]=min/max B\*
- Pipeline, CLI, JSON/HTML audit panels, package-native evidence, and minimal CI
- Provisional synthetic-only protocol lock (`docs/16`) with an audited MC50 proof table (seeds 0..49); H5 Trust design locked (`docs/17`), first frozen run (n=35) accepted as **preliminary paper-facing evidence**; empirical/paper inputs remain Augusto-owned *[H5 re-graded 2026-08-07 to historical/regression witness — docs/16 §9; v3 headline is the IVS cultural-values lane]*

### v2.0 (published on PyPI 2026-08-06 — tag `v2.0.0`)

- Measure discipline: absolute δ-grid, evaluator growth (`mean_order` / `rank_agree` / `ols_coef`), θ-anchor pre-data audit
- Independent tutorials verified against the PyPI package: synthetic walk-through + H5 replication, and the v2.0 diagnostics tour
- All v2.0-DONE criteria complete (2026-08-06) — B4 methodology statement locked (`docs/METHODOLOGY.md`)

### v2.5 (tagged `v2.5.0` 2026-08-08 — engine infrastructure checkpoint; **not** on PyPI)

Rev 3 P1–P5 engine go closed (synthetic-first):

- **P2 evaluators:** `corr_zero` (discriminant), `monotone_rank` (continuous monotone)
- **P3 betas:** `diff_means`, `map_distance` (pinned loadings IO; no PCA fit)
- **P4 holdout:** restriction-level `stage` + country-level **units-split** (paper falsifiable core)
- **P5 coverage:** additive **uncertainty band** (D1; honest label; boundary $|\mathrm{margin}| \le \kappa\cdot\mathrm{SE}$; headline $[L,U]$ unchanged)
- Latest PyPI is `3.0.0` (2026-08-10); Gate C release completed

### v2.5.2 (tagged `v2.5.2` 2026-08-09 — WVS/GPS tutorial milestone; PyPI publish pending owner uv publish)
- **WVS/GPS input-builder + E2E tutorial** (`tutorials/cvprofiles_wvs_gps_inputs.ipynb`): synthetic oracle walk-through → country-level profile (menu {GPS patience}, aux {risktaking, q275_mean}) → individual-level **GPS-only** profile; disjoint-survey cross-product lesson (78.8M rows refused); corrected placeholder networks (`params.variable` = aux column, not the measure)

### v2.5.1 (PyPI release 2026-08-09 — first PyPI since 2.0.0)

- **CLI holdout exposure (audit B, P0):** `--holdout-units` (comma-separated unit ids; select on train, verdict on hold; headline = M\*_robust; order-normalized sorted-unique in freeze config; forks run_id), `--alpha` (coverage band tail probability, default 0.10) and `--kappa` (boundary attribution rule, default 2.0); validation mirrors inference/coverage.py; α/κ excluded from freeze preimage; stdout-JSON / stderr-notes contract preserved; empty M\* exits 0
- **Docs synced to shipped state (audit A1-A3, D2, D5):** USER_GUIDE / METHODOLOGY / README / ARCHITECTURE carry the shipped v2.5.0 engine features (holdout stage + units-split, coverage band, `corr_zero` / `monotone_rank`, `diff_means` / `map_distance`); README install-from-source pins v2.5.1; WVS/GPS lane README cross-repo SCA2 data dependency + WVS Wave 7 no-direct-risk-item disclosure
- **Version-consistency CI (audit D4):** `tools/check_version_consistency.py` asserts posture docs (AGENTS / README / USER_GUIDE / METHODOLOGY / ARCHITECTURE) match `__version__` on every bump; hermetic tests

## Current backlog

- **Paper-facing protocol freeze:** [`docs/16_Paper_Protocol_Freeze.md`](16_Paper_Protocol_Freeze.md) — construct, score matrix, menu, researcher-authored R, θ, δ, β, and evidence posture (synthetic-only portion locked provisional; **§9 Gate A amendment 2026-08-07** opens the IVS designated-evaluation box, run gated; **§11 amendment 2026-08-10 promotes the WVS/GPS patience application to flagship empirical example and defers IVS**)
- **M10 / H5:** country-level generalized trust — design **LOCKED as historical** (`docs/17`); n=35 run **re-graded to historical/regression witness** (2026-08-07); reproducible via `tools/verify_h5_trust.py`; not the v3 evidence base
- **v3 IVS cultural-values lane:** [`docs/18_IVS_Cultural_Map.md`](18_IVS_Cultural_Map.md) — Tao et al. (2024)-style evaluation on Joint EVS/WVS 2017–2022 v5.0; design fields **Augusto-authored**, run **gated** (Gate B); **DEFERRED 2026-08-10 (`docs/16` §11)** — design container stays RESERVED; hard items Y003/PC2′ remain open; open-weight policy (no adapters, no proprietary APIs)
- **Next-sprint scope box:** **P6 SUPERSEDED → v3.1** (decision 2026-08-10, docs/16 §12): the benchmark kit + IVS harness scaffold are deferred to v3.1; the v3.0.0 empirical evidence base is the WVS/GPS patience flagship application (§11, accepted frozen run). Then P7/Gate C → `v3.0.0` (in progress). Plan authority: `reports/DEVELOPMENT_PLAN_v3_REV3.md`; application authority: `reports/DEVELOPMENT_PLAN_WVS_GPS_APPLICATION.md`
- **WVS/GPS preferences intermediate lane:** `evals/wvs_gps_preferences/` — patience + risk-taking on **local** GPS (Falk et al. 2018, country + individual) + WVS Wave 7 (codebook-verified Q13/Q14/Q48/Q49/Q275/R/Q279; missing codes -1..-5 masked, never imputed); interactive input-builder notebook (no form GUI); **PROMOTED to flagship public-facing empirical example 2026-08-10 (`docs/16` §11)** — patience application, 7-measure menu (GPS positive control, WVS proxies, composite C=F(φ), two llama.cpp prompting measures, noise negative control), aux-only network, OLS β on log GDP pc, 80/20 country units-split vs random-selection baseline; monolith `run_application.py` + `verify_wvs_gps.py`; plan `reports/DEVELOPMENT_PLAN_WVS_GPS_APPLICATION.md`; **frozen-run gated, not a paper headline result; IVS deferred**

## Change log

| Date | Change |
|---|---|
| 2026-08-06 | Extracted from README into a live doc (docs/12, docs strategy decision) |
| 2026-08-07 | Phase 3 tutorials shipped (IRT-as-scoring + sensemakr-on-survivors); batch orchestrator (`tools/run_many.py`) documented; tag `v2.0.1a1` dev checkpoint |
| 2026-08-07 | **Gate A signed** — `docs/16` §9 amendment (IVS lane, coverage, holdout semantics, evaluators, open-weight policy); H5 re-graded to historical; `docs/18` created; v3 plan/inventory committed |
| 2026-08-08 | **Rev 3 P1–P5 engine closed** — tag `v2.5.0` infrastructure checkpoint (not PyPI); P6 deferred |
| 2026-08-09 | **P6 tag decision** — P6 ships as its own checkpoint tag (independent of P7; candidate `v2.6.0`); stale-reference sweep (AGENTS.md, test literals) |
| 2026-08-09 | WVS/GPS preferences intermediate lane opened (docs/12, docs/16 §10); GUI deferred, input-builder notebook chosen |
| 2026-08-09 | **v2.5.1 PyPI release** — first PyPI since 2.0.0: CLI holdout exposure (`--holdout-units`/`--alpha`/`--kappa`), docs synced to shipped state, version-consistency CI check |
| 2026-08-10 | **WVS/GPS patience application promoted to flagship empirical example** — `docs/16` §11 amendment (IVS deferred, RESERVED); decision card D1–D10 frozen (menu, aux-only network, OLS β, 80/20 units-split, random-selection baseline, Llama-3.1-8B + Phi-4-mini prompt arms); plan `reports/DEVELOPMENT_PLAN_WVS_GPS_APPLICATION.md` |
| 2026-08-10 | **Frozen run ACCEPTED; v3.0.0 release path opened** — docs/16 §12: v3.0.0 = infrastructure + flagship application; P6 superseded → v3.1; headline `M*_select = [gps, prompt_a]`, `[L,U] = [0.328, 0.402]`, random-null 100th percentile; verifier exit 0 |
