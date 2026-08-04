# cvprofiles

**Construct-validity profiles for cheap multi-measure AI operationalizations.**

Open, high-observability research tooling that treats construct validity as **partial identification over a menu of measurement functions**, disciplined by a researcher-authored nomological network. The engine returns an admissible measurement set \(M^*\) and a construct-identified range \([L,U]\) for a target functional \(\beta(\cdot)\). Empty sets and wide ranges are scientific features, not product failures.

| | |
|---|---|
| **Version** | **v0.1.0** tagged (methods KB + museum PoC); **v1.0 thin spine** (`1.0.0a1` package) |
| **Status** | Public repo live; tag `v0.1` @ `fb62b48` frozen; M1–M9 merged; v1.1 inference layer in progress |
| **Type** | Academic methods tool (Python package + paper) |
| **Owner** | Augusto Gonzalez Bonorino |
| **License** | MIT |
| **GitHub** | https://github.com/Bonorinoa/cvprofiles |
| **CI** | [![ci](https://github.com/Bonorinoa/cvprofiles/actions/workflows/ci.yml/badge.svg)](https://github.com/Bonorinoa/cvprofiles/actions/workflows/ci.yml) |
| **Hermes profile** | `cvprofiles` |
| **Path** | `~/Hermes/Projects/cvprofiles` |
| **PoC** | `evals/synthetic/v0_poc.py` (`v0_1_poc`) — **museum monolith**, not package |
| **Proof summary** | `reports/summaries/v0_1_poc_summary.json` (+ package synth summary) |

## Thesis spine (one paragraph)

Researcher supplies unit×measure scores (SCORE). Researcher authors a nomological network \(R\) with thresholds \(\theta\) and a target \(\beta(\cdot)\) (RESTRICT). Engine computes sample slacks, keeps admissible measures \(M^*\), maps survivors through \(\beta\), and reports \(B^* / [L,U]\) (IDENTIFY). **v1.0:** \([L,U]=\min/\max B^*\) only. Bootstrap and \(\theta\)-sensitivity are **v1.1**. Audit trail in HTML/JSON (LaTeX later) a non-coder can steer (REPORT). Engine is **score-agnostic and model-free**. No LLM lives inside the engine.

## Document map

Start here, then read in order:

| Doc | Purpose |
|---|---|
| [`docs/01_Project_Overview.md`](docs/01_Project_Overview.md) | Goals, users, scope, hard non-goals |
| [`docs/02_System_Architecture.md`](docs/02_System_Architecture.md) | 4-state machine, IO contracts, determinism |
| [`docs/03_Methodology.md`](docs/03_Methodology.md) | Menu, slacks, \(M^*\), \(B^*\), inference stance |
| [`docs/04_Synthetic_DGPs.md`](docs/04_Synthetic_DGPs.md) | Calibrated DGPs + four debug metrics |
| [`docs/05_Pre_Registration.md`](docs/05_Pre_Registration.md) | Draft H1–H5 (user owns theory) |
| [`docs/06_Tech_Stack.md`](docs/06_Tech_Stack.md) | Language, numeric stack, packaging |
| [`docs/07_Software_Development_Strategy.md`](docs/07_Software_Development_Strategy.md) | TDD, gates, agent workflow |
| [`docs/08_Observability_and_Evaluations.md`](docs/08_Observability_and_Evaluations.md) | Artifacts, metrics, report contract |
| [`docs/09_MVP_Plan.md`](docs/09_MVP_Plan.md) | Milestones and build order |
| [`docs/10_Open_Questions.md`](docs/10_Open_Questions.md) | Explicit deferrals |
| [`docs/11_Glossary.md`](docs/11_Glossary.md) | Notation |
| [`docs/12_Decision_Engineering_Log.md`](docs/12_Decision_Engineering_Log.md) | **LIVE** engineering decisions |
| [`docs/13_Evaluations_Log.md`](docs/13_Evaluations_Log.md) | **LIVE** eval runs and learnings |
| [`docs/14_Researcher_Input_Guide.md`](docs/14_Researcher_Input_Guide.md) | Composites, anchors, SCORE/RESTRICT prep |
| [`docs/15_MVP_Release_Checklist.md`](docs/15_MVP_Release_Checklist.md) | MVP release checklist (feeds release-review chat) |
| [`docs/PROJECT_MANIFEST.md`](docs/PROJECT_MANIFEST.md) | Machine-readable index |

## Roadmap

### v1.0 (this sprint — thin first-principles spine)

1. **Schemas + freeze contract** — typed score matrix, network, \(\beta\), run manifest  
2. **SCORE → RESTRICT → IDENTIFY** — slacks, \(M^*\), \([L,U]=\min/\max B^*\) (no bootstrap)  
3. **Thin REPORT** — HTML/JSON; empty \(M^*\) is a clean success  
4. **Synth harness re-impl** under package/tests (H1a / H2 / H3 / H4; H1_latent diagnostic)  
5. **Installable package + minimal CI**

### Later

- **v1.1:** bootstrap + \(\theta\)-grid  
- **M10 / H5:** one public baseline — boring, heavily documented association study (USER-authored network only; choice deferred)

See [`docs/09_MVP_Plan.md`](docs/09_MVP_Plan.md) for the locked v1.0 scope box and acceptance list.

## Hard non-goals (unless reopened in the decision log)

- Foundation-model training  
- New human annotation campaigns as the main path  
- Hypothesis-generation / SAE pipelines as thesis core  
- Full PPI/MARS reimplementation as co-equal deliverable  
- LLM-agent ABMs / SCA product work as this spine  
- Proprietary API dependence for paper-reproducible results  
- “Automate all of empirical economics” platforms  

## Working convention

Progress is read from **on-disk artifacts** (slacks, \(M^*\), ranges, `report.html`) and the two live logs — not from git archaeology alone. Paper numbers come only from **frozen score matrices + pinned network + fixed seed**.

## Repo status

- **Tag `v0.1` @ `fb62b48` (live, immovable):** documentation suite + museum synthetic PoC with green gates.  
  Release: https://github.com/Bonorinoa/cvprofiles/releases/tag/v0.1
- **`main`:** v1.0 spine through M9 (`1.0.0a1`) + intermediate spam audit, merged.
- **v1.1 in progress:** bootstrap over units + θ-grid sensitivity (diagnostic; headline \([L,U]=\min/\max B^*\) unchanged).
- **Not yet:** PyPI release; any tag (release-review chat + Augusto decide).

### Install (dev)

```bash
uv sync --extra dev
uv run pytest -q
uv run cvprofiles --version
```

### Museum PoC (expects exit 0; do not import into `src/`)

```bash
uv venv --python 3.11 .venv
uv pip install --python .venv/bin/python numpy pandas
.venv/bin/python evals/synthetic/v0_poc.py
```

- Progress is read from on-disk artifacts + `docs/12` / `docs/13`, not git archaeology alone.
