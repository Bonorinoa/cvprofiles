# Architecture

How the package is built, what the IO contracts are, and how determinism is guaranteed. This supersedes the earlier `02_System_Architecture.md`, `06_Tech_Stack.md`, and `08_Observability_and_Evaluations.md` scaffolds (archived) and reflects the shipped v3.0.2 package.

## 1. Four-state machine

```text
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
              |  M* = {m : s_r ≥ -δ ∀ r}  |
              |  B* = {β(m) : m ∈ M*}     |
              |  [L,U]=min/max B*         |
              |  bootstrap, θ-grid, δ-grid|
              +-------------+-------------+
                            |
                   identification bundle
                            v
              +---------------------------+
              |  3  REPORT                |
              |  HTML / JSON audit trail  |
              +---------------------------+
```

| State | Role | Mutates scores? | May call LLM? |
|---|---|---|---|
| 0 SCORE | Ingest only | Normalize only | No (upstream of engine) |
| 1 RESTRICT | Thesis core | No | No |
| 2 IDENTIFY | Thesis core | No | No |
| 3 REPORT | Thesis core | No | No (templating only) |

**Invariant:** frozen scores + pinned network + fixed seed ⇒ reproducible engine run (bit-stable within the documented float policy).

## 2. Module map (shipped layout)

```text
src/cvprofiles/
  __init__.py            # version
  cli.py                 # thin Typer CLI: `cvprofiles run`
  pipeline.py            # run_profile() composition + freeze bundle
  freeze.py              # hashing, run_id, n_boot normalization
  score/                 # load → validate → normalize → freeze hash + manifest
  restrict/              # network/beta parsers, column binding, hashing
  schemas/               # pydantic: scores, network, beta, run
  identify/              # slack evaluators, beta evaluators, M*, [L,U]
  inference/             # bootstrap, theta_grid, delta_grid (additive)
  anchors/               # θ-anchor parse, completeness check, payload
  report/                # JSON dump + Jinja2 HTML (templates/)
  synth/                 # DGPs + oracle networks + metrics (eval, not paper path)
```

Each state is a pure-ish transform with explicit on-disk inputs/outputs. A full run is composition, not a god-object.

## 3. Inputs and outputs

### Inputs

| Artifact | Role | Format |
|---|---|---|
| scores | Unit × measures (+ aux/outcome) | CSV or parquet |
| roles.json | Column role map | JSON |
| network.yaml | Restrictions R + θ + δ | YAML |
| beta.yaml | Target functional | YAML |
| anchors.yaml (optional) | Pre-data θ anchors | YAML |

### Outputs (per run directory)

| Artifact | Role |
|---|---|
| `S_frozen.csv` / `.parquet` | Validated, normalized matrix |
| `score_manifest.json` | Column map, n, J, hash, normalization policy |
| `restrict_bundle.json` | Parsed R, θ, β spec |
| `slacks.csv` / `.parquet` | s_r(m_j) matrix (measures × restrictions) |
| `admissible.json` | M* member list + failure reasons for non-members |
| `beta_values.json` | β(m) for every m (survivors flagged) |
| `range.json` | [L,U], empty flag, point-id flag |
| `run_manifest.json` | hashes, seed, versions, settings |
| `bootstrap.json` | replicates summary (when enabled) |
| `theta_grid.json` | sensitivity surface summary (when enabled) |
| `delta_grid.json` | tolerance surface summary (when enabled) |
| `anchors.json` | anchor audit payload (when enabled) |
| `report.html` | primary human audit trail |
| `report.json` | machine-complete dump of the same payload |

## 4. Determinism and the freeze contract

1. Every full run writes a run directory under `reports/runs/<run_id>/` (or `--out`).
2. `run_id` = content hash of the frozen score matrix, network, β, seed, and package version. Same inputs ⇒ same id; colliding ids with different outputs is a critical bug.
3. Paper path: only artifacts from a run directory with pinned hashes are citable.
4. Bootstrap RNG is a seeded `numpy.random.Generator` (never the global `np.random`).
5. Float comparisons for slacks use the declared tolerance δ (default 0) — never raw `== 0` without policy.
6. **Diagnostics excluded from the preimage:** bootstrap count is normalized (`n_boot < 1 ⇒ null`), and θ-grid / δ-grid / anchors settings do not change the run_id. Same bundle + different grids ⇒ same id, different artifacts.

## 5. Slack and beta evaluators

- **Restriction registry** (`identify/slacks.py`): `corr_min`, `corr_sign`, `mean_order`, `rank_agree` implemented; `stability` is schema-only and fails loud until a fixture demands it. Unknown types fail loud at parse time. All evaluators are simple, finite-sample sample analogues — no kernel or ML nuisances in the validity layer.
- **Beta registry** (`identify/beta_fn.py`): `corr_y`, `ols_coef`. `ols_coef` is a numpy closed-form standardized OLS (no statsmodels dependency), requiring a non-empty control list.

## 6. Report construction

`report/pipeline.py` builds a single machine-complete payload dict, then:

- writes `report.json` directly, and
- renders `report.html` from a Jinja2 template (`report/templates/report.html.j2`).

The HTML and JSON share one payload, so they cannot disagree about numbers. The template is self-contained (no external assets) so `report.html` opens anywhere. Panel structure: construct/menu summary, headline range block, slack matrix, admissible set with binding restrictions, and optional bootstrap / θ-grid / δ-grid / anchor panels.

## 7. Observability

Progress is read from on-disk artifacts, not chat transcripts:

- slack matrices, admissible sets, ranges, `report.html`
- `logs/EVALUATIONS.md` — the narrative eval log
- `logs/DECISIONS.md` — append-only engineering decisions

Run directories are gitignored; allow-listed proof summaries under `reports/summaries/` are tracked.

## 8. Tech stack (shipped)

| Layer | Choice |
|---|---|
| Language | Python ≥ 3.11 |
| Packaging | `pyproject.toml` + hatchling (uv for dev) |
| Arrays / tables | NumPy, pandas, pyarrow |
| Schemas | Pydantic v2 (extra=forbid) |
| Config | PyYAML |
| CLI | Typer |
| Templates | Jinja2 |
| Tests | pytest, pytest-cov |
| Lint/type | ruff, mypy (strict) |
| CI | GitHub Actions: ruff, mypy, pytest+coverage, CLI smoke, import-graph hygiene, wheel smoke |

Dependencies are intentionally thin. Explicitly rejected for the engine core: cloud LLM SDKs, heavy orchestration, GUI frameworks, and (as a requirement) DuckDB/Polars.

## 9. What is deliberately not in the architecture

- Vector DB / RAG
- Agent loop inside IDENTIFY
- Measure generation (prompt library, annotation UI) as engine stages
- Causal DAG editor
- Multi-tenant service layer

Upstream scorers (LLM APIs, dictionaries, PCA) are user workflows that produce columns for SCORE. They are documented as recipes, not engine modules.

## 10. Failure aesthetics

| Condition | Engine behavior |
|---|---|
| Empty M* | Success exit; range.json marks empty; report explains binding restrictions |
| Singleton M* | Point-id flag true; still emit range; diagnostics still available |
| All measures fail one r | Surface that r as dominant; do not auto-loosen θ |
| Schema invalid | Fail loud at SCORE/RESTRICT; never partial-identify on garbage |

## 11. Package posture

- `v0.1` tag is immovable and peels to the museum PoC (`evals/synthetic/v0_poc.py`, unimported from src).
- `v1.1.0` (MVP + inference layer), `v2.0.0` (measure discipline, PyPI 2026-08-06), and `v2.5.0` (P1–P5 engine infrastructure checkpoint, 2026-08-08) are tagged.
- Current package version: `3.0.1` (empty_R unrestricted-multiverse special case; 3.0.0 remains the flagship-application release).
