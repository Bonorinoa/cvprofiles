# 07 — Software Development Strategy

**Status:** scaffold v0 (2026-08-01)

## Goals

1. Engine correctness over feature velocity.  
2. Cross-agent continuity via docs + dual live logs + on-disk artifacts.  
3. No vibe-engineered sprawl: **state machine boundaries** are module boundaries.

## Method: component-by-component + TDD

Build order mirrors states (see `09_MVP_Plan.md`). For each component:

1. Write contract tests (schemas, golden fixtures).  
2. Watch them fail.  
3. Implement minimal code.  
4. Add oracle/synthetic tests where applicable.  
5. Emit artifacts to a run directory.  
6. Log decisions/eval learnings.  
7. Checkpoint with Augusto before next state.

## Gates (do not skip)

| Gate | Entry criterion | Exit criterion | v1.0? |
|---|---|---|---|
| G0 Docs | — | This suite reviewed; open questions listed | done |
| G1 Schemas | G0 | Pydantic models + fixture validates; freeze hash stable | **yes** |
| G2 SCORE | G1 | Normalization + manifest; bad input fails loud | **yes** |
| G3 RESTRICT | G2 | network/beta parse; invalid \(R\) rejected | **yes** |
| G4 IDENTIFY slacks | G3 | Slack matrix matches hand-computed fixture | **yes** |
| G5 \(M^*\) + range | G4 | Oracle DGP: membership + \([L,U]=\min/\max B^*\) vs truth labels | **yes** |
| G6 Bootstrap + \(\theta\)-grid | G5 | Seed-stable bootstrap; θ-sensitivity | **v1.1** (deferred) |
| G7 REPORT | G5 (v1.0 thin) / G6 (full) | HTML/JSON from same bundle; empty-\(M^*\) beautiful | **yes (thin)** |
| G8 Synth harness | G7 | H1a / H1b / H2 / H3 / H4 logged; H1_latent diagnostic only; CI mini battery | **yes (mini)** |
| G9 Package + real baseline | G8 | installable package + CI; real baseline only with USER network | package **yes**; H5 **no** |

### v1.0 gate path (thin spine)

```
G1 → G2 → G3 → G4 → G5 → G7-thin → G8-mini → package install/CI
# G6 bootstrap/θ-grid deferred to v1.1
# H5 / real baseline out of v1.0
```

**Hypothesis wording:** primary gates are **H1a** (admissible-set integrity / FA) and **H1b** (feasible-anchor coverage, construction invariant). **H1_latent** is diagnostic only (attenuation). See `03_Methodology.md` and `05_Pre_Registration.md`.

**GitHub (past tense):** public repo https://github.com/Bonorinoa/cvprofiles and tag `v0.1` @ `fb62b48` are live. No coding-agent free-for-all until `AGENTS.md` exists (deferred).

## Agent roles

| Actor | Owns |
|---|---|
| Augusto | Construct theory, \(R,\theta\), \(\beta\) choice, go/no-go gates, paper narrative, taste |
| Hermes (this profile) | Scaffolding, scope police, method clarity, tests design, logs, packaging strategy |
| Coding agent (later) | Implementation against docs; no architecture invention |

Handoff rule: coding agent reads `PROJECT_MANIFEST.md` required order + live logs. If docs and code conflict, **stop and update docs** — do not “fix forward.”

## PR / change discipline (when git exists)

- One gate or one restriction type per PR when possible.  
- Conventional commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.  
- Every architecture change updates `12_Decision_Engineering_Log.md` in the same PR.  
- Every eval battery run appends `13_Evaluations_Log.md`.  
- Paper numbers only from tagged freeze runs.

## Testing strategy

| Tier | What |
|---|---|
| Unit | Pure functions (corr, slack formulas) |
| Contract | Schema round-trips, manifest hashes |
| Oracle | Synthetic labels vs \(M^*\) |
| Golden | Tiny fixture numeric snapshots |
| Report smoke | HTML contains admission table + empty-state copy |
| Repro | Run twice → identical hashes/outputs |

## What “done” looks like for a week

Not “merged N PRs.” Rather:

- New artifacts under `reports/runs/`  
- Eval log rows with four metrics  
- Decision log entries if scope moved  

## Anti-patterns

- Collapsing SCORE and measure generation into one module  
- Calling LLMs “just to fill defaults” inside RESTRICT  
- Auto-relaxing \(\theta\) when \(M^*\) empty  
- Kitchen-sink `utils.py` that bypasses state IO contracts  
- Importing Phronesis voice/RAG infrastructure  

## AGENTS.md

Deferred until first code milestone approaches. Until then, SOUL + this suite is authority.
