# 09 — MVP Plan

**Status:** v1.0 spine sprint shipped (2026-08-01); historical context for later sprints
**Authority:** governed the v1.0 sprint; full MVP backlog remains context only.

---

## v1.0 scope box (LOCKED this sprint)

**Goal:** validate core first principles of the system we ship — not the full MVP below, not paper-complete, not fully tested polish.

### In v1.0

- Installable thin package: `src/cvprofiles` + `pyproject.toml` + CLI
- States: SCORE → RESTRICT → IDENTIFY → thin REPORT (HTML/JSON)
- Finite menu; sample slacks → $M^*$ → $[L,U]=\min/\max B^*$ (**no bootstrap**)
- Freeze hash + bit-stable rerun of the same bundle
- Synthetic harness **re-implemented** under package/tests (gates H1a / H2 / H3 / H4)
- Empty $M^*$ is a clean success path (feature, not crash)
- No LLM in the engine or installable import graph

### Explicitly out of v1.0

- **M6 bootstrap / θ-grid → v1.1** (deferred by user)
- M10 / H5 / real baseline / USER empirical network content
- Sharp PI, prompt search, measure generation, GUI/SaaS
- Importing or packaging the museum monolith as the library
- Moving tag `v0.1` or rewriting history
- “Fully tested MVP” polish

**v1.0 ≠ full milestone list below.** Museum PoC (`evals/synthetic/v0_poc.py`) was directional only; package path must earn its own gates. Tag `v0.1` @ `fb62b48` is frozen forever.

### v1.0 build order (strict)

```
M1 → M2 → M3 → M4 → M5 → M7(thin) → M8 → M9
# No M6. No M10 this sprint.
```

### v1.0 acceptance (minimum)

- [x] `uv sync` / editable install runs without API keys
- [x] CLI or library: SCORE→REPORT on frozen mini fixture
- [x] Empty $M^*$ → clean report (not a crash); fail loud only on bad schema
- [x] Oracle slop excluded; FA = 0 on designed invalids
- [x] Cold twice-run identical freeze outputs (H4)
- [x] No LLM dependency in package import graph
- [x] Museum `evals/synthetic/v0_poc.py` still present and **unimported**
- [x] `docs/12` / `docs/13` updated for package battery
- [x] Tag `v0.1` still points at `fb62b48`
- [x] M9 minimal CI workflow present (green on branch before merge)

---

## Full MVP definition (backlog context)

A researcher can:

1. Supply a frozen unit×measure score matrix (+ aux/outcome),
2. Supply `network.yaml` + `beta.yaml`,
3. Run a local CLI,
4. Receive $M^*$, $[L,U]$, bootstrap/θ diagnostics, and `report.html`,
5. Reproduce the run from hashes + seed,

…and we can show on **synthetic DGPs** that H1–H4 behave as preregistered (directionally at MVP; fully at paper freeze).

**Note:** item 4’s bootstrap/θ layer is **v1.1+**. v1.0 ships min/max $B^*$ only.

## Out of MVP (unchanged hard non-goals)

- Real baseline H5 completion (gated)
- GUI / web app
- Prompt search / measure generation engine
- Sharp PI theory package
- Multi-construct networks
- Polished docs site

## Milestones (full backlog)

| ID | Milestone | Deliverable artifact | Unblocks | v1.0? |
|---|---|---|---|---|
| M0 | Design scaffold | This docs suite + dual logs | G0 review | done |
| M1 | Schemas + freeze hash | Pydantic models; `data/fixtures/mini_*`; hash util | SCORE | **yes** |
| M2 | SCORE | `S_frozen` + `score_manifest.json` | RESTRICT | **yes** |
| M3 | RESTRICT | Parsed bundle; reject bad networks | IDENTIFY | **yes** |
| M4 | IDENTIFY slacks + $M^*$ | `slacks.parquet`, `admissible.json` | range | **yes** |
| M5 | $\beta$, range, empty handling | `beta_values.json`, `range.json` | inference / REPORT | **yes** |
| M6 | Bootstrap + $\theta$-grid | `bootstrap.json`, `theta_grid.json` | full inference | **v1.1** |
| M7 | REPORT | HTML/JSON/(TeX stub) | harness UX | **yes (thin)** |
| M8 | Synth harness + metrics | `evals`/`tests` battery; eval log rows | H1–H4 evidence | **yes (mini)** |
| M9 | Package + CI | installable `cvprofiles`; GHA | external users | **yes (minimal)** |
| M10 | Real baseline (gated) | Frozen scores + **USER** network + paper tables | H5 | **no** |

## Full-MVP build order (historical; not this sprint)

```
M0 → M1 → M2 → M3 → M4 → M5 → M6 → M7 → M8 → M9
                                      ↘ M10 only after M8 gate + user network
```

v1.0 skips M6 and M10. Do not start M10 because a deadline wants a “real” figure.

## First vertical slice (v1.0 path)

Smallest end-to-end path after M1:

- 3-measure mini fixture
- 2 restrictions (`corr_min`, `corr_sign`)
- $\beta = $ `corr_y`
- slacks → $M^*$ → min/max range **without** bootstrap
- one-page HTML

Then thicken inference (v1.1) and DGPs.

## Time posture

Masters/thesis-compatible: prefer a **thin correct spine** over broad restriction catalogs. Add restriction types only when a synthetic scenario demands them.

## Acceptance for full “MVP demo” (beyond v1.0)

- [ ] Empty $M^*$ run produces clean report
- [ ] Oracle slop excluded on `oracle_with_slop` mini
- [ ] Twice-run identical `run_id` outputs
- [ ] Eval log has ≥1 battery row with four metrics
- [ ] No LLM dependency in package import graph
- [ ] Bootstrap + θ-grid present (v1.1)

## GitHub (past tense)

- Public repo **live:** https://github.com/Bonorinoa/cvprofiles
- Annotated tag **`v0.1`** frozen at **`fb62b48`** (methods KB + museum PoC only)
- GitHub Release: https://github.com/Bonorinoa/cvprofiles/releases/tag/v0.1
- `main` may advance; **do not move or retag `v0.1`**
- Propose tag `v1.0.0` only when package path reproduces green gates; sibling release chat evaluates candidates
