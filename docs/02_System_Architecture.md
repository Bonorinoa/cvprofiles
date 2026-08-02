# 02 — System Architecture

**Status:** scaffold v0 (2026-08-01) — LOCKED spine; IO details DRAFT until first schema PR  
**Principle:** state machine first. Observability beats cleverness. No LLM inside the engine.

## Four-state machine

```
                    user-supplied artifacts
                            |
                            v
              +---------------------------+
              |  0  SCORE                 |
              |  ingest unit×measure      |
              |  + auxiliaries + outcome  |
              |  validate / normalize     |
              |  DO NOT invent measures   |
              +-------------+-------------+
                            |
                     frozen score matrix S
                            v
              +---------------------------+
              |  1  RESTRICT              |
              |  parse network R, θ       |
              |  parse target β(·)        |
              +-------------+-------------+
                            |
                  (S, R, θ, β) run bundle
                            v
              +---------------------------+
              |  2  IDENTIFY              |
              |  slacks s_r(m_j)          |
              |  M* = {m : s_r ≥ 0 ∀ r}   |
              |  B* = {β(m) : m ∈ M*}     |
              |  [L,U]=min/max B* (v1.0)  |
              |  bootstrap, θ-grid = v1.1 |
              +-------------+-------------+
                            |
                   identification bundle
                            v
              +---------------------------+
              |  3  REPORT                |
              |  HTML / JSON / LaTeX      |
              |  audit trail              |
              +---------------------------+
```

| State | Thesis role | Mutates scores? | May call LLM? |
|---|---|---|---|
| 0 SCORE | Ingest only | Normalize only | **No** (upstream of engine) |
| 1 RESTRICT | Thesis core | No | **No** |
| 2 IDENTIFY | Thesis core | No | **No** |
| 3 REPORT | Thesis core | No | **No** (templating only) |

**Invariant:** frozen scores + pinned network + fixed seed ⇒ reproducible engine run (bit-stable within documented float policy).

## Module map (planned package layout)

```
cvprofiles/
  score/        # schemas, validation, normalization, freeze hash
  restrict/     # network parser, θ schema, β registry
  identify/     # slacks, M*, β(m), range, bootstrap, θ-grid
  report/       # HTML/JSON/LaTeX emitters
  synth/        # DGPs + four debug metrics (dev/eval, not paper path)
  cli/          # thin Typer entrypoints per state + full run
```

Each state is a **pure-ish transform** with explicit inputs/outputs on disk. Prefer files over hidden global state. A full run is composition, not a god-object.

## IO contracts (DRAFT shapes)

### SCORE in
| Artifact | Role |
|---|---|
| `scores.parquet` / `.csv` | Units × measures; columns are `m_j` ids |
| `aux.parquet` (optional) | Auxiliaries \(V\) used in restrictions |
| `outcome.parquet` (optional) | Outcome / other inputs to \(\beta\) |
| `units.json` | Unit id column name, sample weights (optional) |

### SCORE out
| Artifact | Role |
|---|---|
| `S_frozen.parquet` | Validated, normalized matrix |
| `score_manifest.json` | Column map, n, J, hash, normalization policy |

### RESTRICT in
| Artifact | Role |
|---|---|
| `network.yaml` | Restrictions \(r \in R\), each with type, fields, \(\theta_r\) |
| `beta.yaml` | Target functional declaration + args |
| `S_frozen` + manifest | From SCORE |

### RESTRICT out
| Artifact | Role |
|---|---|
| `restrict_bundle.json` | Parsed R, θ vector, β spec, validation report |

### IDENTIFY out
| Artifact | Role |
|---|---|
| `slacks.parquet` | \(s_r(m_j)\) matrix (measures × restrictions) |
| `admissible.json` | \(M^*\) member list + failure reasons for non-members |
| `beta_values.json` | \(\beta(m)\) for each \(m \in M\) (flag survivors) |
| `range.json` | \([L,U]=\min/\max B^*\) (v1.0); point-ID flag; empty-set flag |
| `bootstrap.json` | Replicates summary (not raw draws by default) — **v1.1** |
| `theta_grid.json` | Sensitivity surface summary — **v1.1** |
| `identify_manifest.json` | seed, float policy, package version; `n_boot` when M6 lands |

### REPORT out
| Artifact | Role |
|---|---|
| `report.html` | Primary human audit trail |
| `report.json` | Machine-complete dump |
| `report.tex` | Paper-facing tables/figures stubs |

## Determinism & freeze contract

1. Every full run writes a **run directory** under `reports/runs/<run_id>/`.  
2. `run_id` = content hash of `(S_frozen hash, network hash, beta hash, seed, package_version, config)`.  
3. Paper path: only artifacts from a run directory with pinned hashes are citable.  
4. Bootstrap RNG is seeded; stream is documented (NumPy Generator, not global `np.random`).  
5. Float comparisons for slacks use an explicit tolerance \(\delta\) (default TBD; see open questions) — never raw `== 0` without policy.

## What is deliberately not in the architecture

- Vector DB / RAG  
- Agent loop inside IDENTIFY  
- Measure generation (prompt library, annotation UI) as engine stages  
- Causal DAG editor  
- Multi-tenant service layer  

Upstream scorers (LLM APIs, dictionaries, PCA) are **user workflows** that produce columns for SCORE. They are documented as recipes, not engine modules.

## Data flow (ASCII, single run)

```
[user scores] --> SCORE --> S_frozen ----------------+
[network.yaml] -> RESTRICT -> bundle ----------------+--> IDENTIFY --> artifacts --> REPORT
[beta.yaml]  ---/     seed; n_boot/θ-grid = v1.1 ---/
```

## Failure aesthetics (architectural)

| Condition | Engine behavior |
|---|---|
| Empty \(M^*\) | Success exit; `range.json` marks empty; report explains binding restrictions |
| Singleton \(M^*\) | Point-ID flag true; still emit range; bootstrap/θ diagnostics at v1.1 |
| All measures fail one \(r\) | Surface that \(r\) as dominant; do not auto-loosen \(\theta\) |
| Schema invalid | Fail loud at SCORE/RESTRICT; never partial-identify on garbage |

## Cross-cutting

- **Logging:** structured JSON lines per state; no chatty progress bars as the only record.  
- **Config:** YAML/TOML for humans; JSON manifests for machines.  
- **Tests:** each state has contract tests; IDENTIFY has synthetic oracle tests (see `04`, `08`).
