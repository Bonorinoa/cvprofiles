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
- All v2.0-DONE criteria complete (2026-08-06) — B4 methodology statement locked (`docs/METHODOLOGY.md`); dev cycle at `2.0.1a1`

## Current backlog

- **Paper-facing protocol freeze:** [`docs/16_Paper_Protocol_Freeze.md`](16_Paper_Protocol_Freeze.md) — construct, score matrix, menu, researcher-authored R, θ, δ, β, and evidence posture (synthetic-only portion locked provisional; **§9 Gate A amendment 2026-08-07** opens the IVS designated-evaluation box, run gated)
- **M10 / H5:** country-level generalized trust — design **LOCKED as historical** (`docs/17`); n=35 run **re-graded to historical/regression witness** (2026-08-07); reproducible via `tools/verify_h5_trust.py`; not the v3 evidence base
- **v3 IVS cultural-values lane (new headline):** [`docs/18_IVS_Cultural_Map.md`](18_IVS_Cultural_Map.md) — Tao et al. (2024)-style evaluation on Joint EVS/WVS 2017–2022 v5.0; design fields **Augusto-authored**, run **gated** (Gate B); open-weight policy (no adapters, no proprietary APIs); P2 coverage / P3 holdout / P4 evaluators / P5a design-teaching-harness per `reports/DEVELOPMENT_PLAN.md`
- **Next-sprint scope box:** v3.0.0 phase-gated plan (`reports/DEVELOPMENT_PLAN.md`) — Gate A signed 2026-08-07; P2–P5a unblocked; LaTeX report remains later backlog

## Change log

| Date | Change |
|---|---|
| 2026-08-06 | Extracted from README into a live doc (docs/12, docs strategy decision) |
| 2026-08-07 | Phase 3 tutorials shipped (IRT-as-scoring + sensemakr-on-survivors); batch orchestrator (`tools/run_many.py`) documented; tag `v2.0.1a1` dev checkpoint |
| 2026-08-07 | **Gate A signed** — `docs/16` §9 amendment (IVS lane, coverage, holdout semantics, evaluators, open-weight policy); H5 re-graded to historical; `docs/18` created; v3 plan/inventory committed |
