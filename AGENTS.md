# cvprofiles — Agent Handoff Contract

## Mission

`cvprofiles` is an open academic methods package for **construct-validity profiles**: partial identification over a finite, researcher-supplied menu of measurement functions. It is not a scorer product, an LLM application, an automated theory-authoring system, or a generic causal-sensitivity package.

The package state machine is:

```text
SCORE → RESTRICT → IDENTIFY → REPORT
```

- **SCORE:** ingest and validate user-supplied unit×measure scores. Do not generate measures.
- **RESTRICT:** bind a researcher-authored nomological network and target functional.
- **IDENTIFY:** compute slacks, the admissible set `M*`, and the headline range `[L,U]`.
- **REPORT:** produce JSON/HTML audit artifacts a non-coder can inspect.

## Non-negotiable scientific and package locks

- The engine is **score-agnostic and model-free**. No LLM client belongs in the package/import graph.
- The menu is finite and researcher supplied. Prompt search and measurement generation are upstream workflows, not engine features.
- The headline range is the image of beta on **survivors only**: `[L,U] = [min B*, max B*]`. Rejected measures may be diagnostic but never enter the range.
- Empty `M*` and wide ranges are valid scientific outputs. Never automatically loosen thresholds to avoid an empty set.
- Bootstrap and theta-grid are additive diagnostics. The headline range remains unchanged; theta-grid settings are excluded from the freeze preimage.
- Paper-relevant numbers require frozen scores, pinned network/beta, fixed seed, package version, and the locked freeze/run-id contract.
- The annotated `v0.1` tag is immovable and must continue to peel to `fb62b48bcb704f60eee7d6641ed0a344eb72bfda`.
- `evals/synthetic/v0_poc.py` is a historical museum artifact. Keep it present and **unimported** from `src/`.

## Authority and scope

Augusto owns all main-path empirical/paper choices:

- construct definition, unit/universe, score matrix and scoring protocol, and measurement menu;
- empirical nomological network `R`, anchors, directions, thresholds, tolerance policy, and beta choice;
- paper claims, reporting placement, H5/public-baseline choice, release posture, tag, and PyPI publication.

Agents may author oracle networks only for synthetic DGPs. Do not invent an empirical network to make H5 or a paper table move. The existing spam audit is intermediate stress evidence, **not H5**.

The current paper protocol (`docs/16_Paper_Protocol_Freeze.md`) is **LOCKED AS PROVISIONAL SYNTHETIC-ONLY**. It does not authorize empirical/H5 work, engine changes, pushes, tags, PyPI publication, or a release claim by implication. A dated amendment (`docs/16` §8, 2026-08-04) opens the empirical box **for the designated H5 Trust evaluation only**; its first frozen run (n=35) is **preliminary paper-facing evidence** (`reports/summaries/h5_trust_evidence_summary.json`) — a checkpoint, not a release. **Re-graded 2026-08-07 (Gate A, `docs/16` §9):** H5 Trust is **historical/regression witness**, not the v3 headline; the v3 empirical lane is the **IVS cultural-values evaluation** (`docs/18_IVS_Cultural_Map.md`), opened by the §9 amendment and **run-gated** (Gate B: frozen scores + pinned network/β + frozen loadings + fixed seed + package version + independent audit exit 0 + Augusto's run decision). Open-weight policy for v3: open-weight local models and interpretable artifacts only; no DPO adapters, no proprietary APIs (D5/D6, `docs/16` §9). Final paper lock, tag, and PyPI remain Augusto's.

## Current posture

- Package version: `2.0.1a1` — dev cycle resumed after **2.0.0 published on PyPI 2026-08-06** (tag `v2.0.0` @ `6abb6e4`).
- v1.1 inference layer shipped and **tagged `v1.1.0`** (2026-08-04, `fce31c8`); superseded by the 2.0.0 release.
- **v2.0 measure discipline DONE** (archived plan: `docs/archive/18_Measure_Discipline_Plan.md`): δ-grid, evaluator growth (`mean_order`/`rank_agree`/`ols_coef`), θ-anchor artifacts shipped 2026-08-05; tutorial verified against the PyPI package; released as `2.0.0`. **B4 methodology statement LOCKED 2026-08-06 — all v2.0-DONE criteria complete.**
- `reports/summaries/v1_1_package_synth_summary.json` is package smoke evidence (seeds `0..4`).
- `reports/summaries/v1_1_protocol_synth_mc50_summary.json` is a distinct provisional synthetic-only MC50 proof artifact (seeds `0..49`). It is not H5 or a full empirical paper lock.
- `reports/runs/` contains reproducible bulk outputs and is ignored. Allow-listed proof summaries under `reports/summaries/` are tracked.
- Intermediate real-world audits live under `evals/realworld/` (`spam_validity` text; `calhousing_validity` tabular). Both are **intermediate / not H5**; their READMEs record capability boundaries (no LLM calls in the engine, no missingness imputation, descriptive correlations only). Do not cite them as paper evidence.

## Where truth lives

| Source | Use |
|---|---|
| `README.md` | Orientation, scope, current package posture |
| `docs/METHODOLOGY.md` | Canonical method statement: menu, slacks, M*, B*, registry rationale, positioning |
| `docs/USER_GUIDE.md` | Researcher-facing input prep, CLI/API usage, report anatomy, checklists |
| `docs/ARCHITECTURE.md` | State machine, module map, IO contracts, determinism, tech stack |
| `docs/ROADMAP.md` | Live roadmap (maintained with the engineering log) |
| `docs/PROJECT_MANIFEST.md` | Machine-readable project state and locks |
| `docs/12_Decision_Engineering_Log.md` | Append-only engineering/scope decisions |
| `docs/13_Evaluations_Log.md` | Evidence interpretations and artifact pointers |
| `docs/16_Paper_Protocol_Freeze.md` | Paper-facing locks, open fields, and provenance rule |
| `docs/17_H5_Trust_Design.md` | H5 Trust design lock (run gated) — **historical** (re-graded 2026-08-07) |
| `docs/18_IVS_Cultural_Map.md` | v3 IVS cultural-values lane design container (Augusto-authored; run gated) |
| `docs/archive/` | Pre-consolidation scaffold (historical reference only) |
| `audits/` | Post-release audit reports (findings + closure status) |
| `pyproject.toml` | Package version, dependencies, lint/type/test configuration |
| `.github/workflows/ci.yml` | CI contract |
| `.gitignore` | Tracked proofs versus ignored run output |

If code and current policy documentation disagree, stop and surface the conflict; do not silently make code, docs, or theory conform.

## Working conventions

1. Read the relevant source, tests, and current decision/protocol docs before changing code.
2. Use strict TDD for behavioral source changes: write a focused test, observe RED, implement minimally, observe GREEN, then run the relevant module and full suite.
3. Keep implementation thin and observable. Do not add infrastructure, optional frameworks, or generic extension systems without a fixture and an explicit decision.
4. For docs/logs, preserve history: append a dated reversal or close-out rather than rewriting a prior decision.
5. Never commit ignored bulk run output. Verify proof-summary allow-lists before adding generated JSON.
6. Do not push, tag, publish, rewrite history, or modify `v0.1` without a task-specific explicit user decision.

## Commands

Bootstrap development dependencies:

```bash
uv sync --extra dev
```

Run the local quality battery:

```bash
uv run ruff check src tests tools
uv run mypy src
uv run pytest -q --tb=short
uv run cvprofiles --version
git diff --check
git rev-parse 'v0.1^{}'
```

For CLI changes, preserve the contract: stdout is machine-readable JSON; human status messages belong on stderr. Empty `M*` is an exit-0 success path.

Before a commit, inspect `git status -sb`, the diff, and relevant on-disk artifacts. Report measured outputs, not remembered numbers.

## Explicit non-goals unless a dated decision reopens them

- foundation-model training;
- new annotation campaigns as the main route;
- SAE/hypothesis-generation core;
- full PPI/MARS reimplementation;
- agent-based-model/SCA product work as the spine;
- proprietary APIs for paper-reproducible work;
- GUI/SaaS/heavy infrastructure;
- “automate all empirical economics.”

When in doubt, favor a small, auditable artifact over a clever abstraction. The point is disciplined measurement, not an elaborate machine for avoiding decisions.
