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
- Provisional synthetic-only protocol lock (`docs/16`) with an audited MC50 proof table (seeds 0..49); H5 Trust design locked (`docs/17`), first frozen run (n=35) accepted as **preliminary paper-facing evidence**; empirical/paper inputs remain Augusto-owned

### v2.0 (published on PyPI 2026-08-06 — tag `v2.0.0`)

- Measure discipline: absolute δ-grid, evaluator growth (`mean_order` / `rank_agree` / `ols_coef`), θ-anchor pre-data audit
- Independent tutorials verified against the PyPI package: synthetic walk-through + H5 replication, and the v2.0 diagnostics tour
- All v2.0-DONE criteria complete (2026-08-06) — B4 methodology statement locked (`docs/METHODOLOGY.md`); dev cycle at `2.0.1a1`

## Current backlog

- **Paper-facing protocol freeze:** [`docs/16_Paper_Protocol_Freeze.md`](16_Paper_Protocol_Freeze.md) — construct, score matrix, menu, researcher-authored R, θ, δ, β, and evidence posture (synthetic-only portion currently locked provisional)
- **M10 / H5:** country-level generalized trust baseline — design **LOCKED** (`docs/17`); first frozen run (n=35) accepted as **preliminary paper-facing evidence** (`reports/summaries/h5_trust_evidence_summary.json`); final paper lock + release remain Augusto's
- **Next-sprint scope box:** to be drafted after the v2.0 release; LaTeX report remains later backlog

## Change log

| Date | Change |
|---|---|
| 2026-08-06 | Extracted from README into a live doc (docs/12, docs strategy decision) |
| 2026-08-07 | Phase 3 tutorials shipped (IRT-as-scoring + sensemakr-on-survivors); batch orchestrator (`tools/run_many.py`) documented; tag `v2.0.1a1` dev checkpoint |
