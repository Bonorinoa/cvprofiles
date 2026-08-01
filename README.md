# cvprofiles

**Construct-validity profiles for cheap multi-measure AI operationalizations.**

Open, high-observability research tooling that treats construct validity as **partial identification over a menu of measurement functions**, disciplined by a researcher-authored nomological network. The engine returns an admissible measurement set \(M^*\) and a construct-identified range \([L,U]\) for a target functional \(\beta(\cdot)\). Empty sets and wide ranges are scientific features, not product failures.

| | |
|---|---|
| **Status** | v0.1 synthetic PoC **gates green**; local git; **no GitHub remote yet** |
| **Type** | Academic methods tool (Python package + paper) |
| **Owner** | Augusto Gonzalez Bonorino |
| **License** | MIT |
| **Hermes profile** | `cvprofiles` |
| **Path** | `~/Hermes/Projects/cvprofiles` |
| **PoC** | `evals/synthetic/v0_poc.py` (`v0_1_poc`) — museum monolith, not package |
| **Proof summary** | `reports/summaries/v0_1_poc_summary.json` |

## Thesis spine (one paragraph)

Researcher supplies unit×measure scores (SCORE). Researcher authors a nomological network \(R\) with thresholds \(\theta\) and a target \(\beta(\cdot)\) (RESTRICT). Engine computes sample slacks, keeps admissible measures \(M^*\), maps survivors through \(\beta\), and reports \(B^* / [L,U]\) with bootstrap and \(\theta\)-sensitivity (IDENTIFY). Audit trail in HTML/JSON/LaTeX a non-coder can steer (REPORT). Engine is **score-agnostic and model-free**. No LLM lives inside the engine.

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
| [`docs/PROJECT_MANIFEST.md`](docs/PROJECT_MANIFEST.md) | Machine-readable index |

## MVP roadmap (sketch)

1. **Schemas + freeze contract** — typed score matrix, network, \(\beta\), run manifest  
2. **IDENTIFY on synthetic truth** — known \(V^*\), known valid/invalid \(m_j\)  
3. **Range + bootstrap + \(\theta\)-grid** — honest conservative \([L,U]\)  
4. **REPORT** — HTML/JSON/LaTeX audit trail  
5. **One public baseline** — boring, heavily documented association study (choice deferred)

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

- Local git after green v0.1 PoC (prerequisite met).
- **No GitHub remote** until explicitly requested.
- Package layout (`src/cvprofiles`) not started — M1 next when ready.
- Run PoC: `.venv/bin/python evals/synthetic/v0_poc.py` (expects exit 0).
