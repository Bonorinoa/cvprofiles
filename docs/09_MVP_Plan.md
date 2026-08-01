# 09 — MVP Plan

**Status:** scaffold v0 (2026-08-01)

## MVP definition

A researcher can:

1. Supply a frozen unit×measure score matrix (+ aux/outcome),  
2. Supply `network.yaml` + `beta.yaml`,  
3. Run a local CLI,  
4. Receive \(M^*\), \([L,U]\), bootstrap/θ diagnostics, and `report.html`,  
5. Reproduce the run from hashes + seed,

…and we can show on **synthetic DGPs** that H1–H4 behave as preregistered (directionally at MVP; fully at paper freeze).

## Out of MVP

- Real baseline H5 completion (gated)  
- GUI / web app  
- Prompt search / measure generation engine  
- Sharp PI theory package  
- Multi-construct networks  
- Polished docs site  

## Milestones

| ID | Milestone | Deliverable artifact | Unblocks |
|---|---|---|---|
| M0 | Design scaffold | This docs suite + dual logs | G0 review |
| M1 | Schemas + freeze hash | Pydantic models; `data/fixtures/mini_*`; hash util | SCORE |
| M2 | SCORE | `S_frozen` + `score_manifest.json` | RESTRICT |
| M3 | RESTRICT | Parsed bundle; reject bad networks | IDENTIFY |
| M4 | IDENTIFY slacks + \(M^*\) | `slacks.parquet`, `admissible.json` | range |
| M5 | \(\beta\), range, empty handling | `beta_values.json`, `range.json` | inference |
| M6 | Bootstrap + \(\theta\)-grid | `bootstrap.json`, `theta_grid.json` | REPORT / H1 |
| M7 | REPORT | HTML/JSON/(TeX stub) | harness UX |
| M8 | Synth harness + four metrics | `evals/synthetic` battery; eval log rows | H1–H4 evidence |
| M9 | Package + CI | installable `cvprofiles`; GHA | external users |
| M10 | Real baseline (gated) | Frozen scores + **USER** network + paper tables | H5 |

## Build order (strict)

```
M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9
                                      ↘ M10 only after M8 gate + user network
```

Do not start M10 because a deadline wants a “real” figure. Synthetic gate first.

## First vertical slice (proposed)

Smallest end-to-end path after M1:

- 3-measure mini fixture  
- 2 restrictions (`corr_min`, `corr_sign`)  
- \(\beta = \) `corr_y`  
- slacks → \(M^*\) → min/max range **without** bootstrap  
- one-page HTML  

Then thicken inference and DGPs.

## Time posture

Masters/thesis-compatible: prefer a **thin correct spine** over broad restriction catalogs. Add restriction types only when a synthetic scenario demands them.

## Acceptance for “MVP demo”

- [ ] Empty \(M^*\) run produces clean report  
- [ ] Oracle slop excluded on `oracle_with_slop` mini  
- [ ] Twice-run identical `run_id` outputs  
- [ ] Eval log has ≥1 battery row with four metrics  
- [ ] No LLM dependency in package import graph  

## GitHub

Create remote **after** M0 confirmation (this checkpoint). Local `git init` optional at same time; remote when Augusto ready.
