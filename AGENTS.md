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

The current paper protocol (`docs/16_Paper_Protocol_Freeze.md`) is **LOCKED AS PROVISIONAL SYNTHETIC-ONLY**. It does not authorize empirical/H5 work, engine changes, pushes, tags, PyPI publication, or a release claim by implication.

## Current posture

- Package development version: `1.1.0a1`.
- v1.1 inference layer is a verified development artifact on `main`; no v1.1 tag or PyPI release exists.
- `reports/summaries/v1_1_package_synth_summary.json` is package smoke evidence (seeds `0..4`).
- `reports/summaries/v1_1_protocol_synth_mc50_summary.json` is a distinct provisional synthetic-only MC50 proof artifact (seeds `0..49`). It is not H5 or a full empirical paper lock.
- `reports/runs/` contains reproducible bulk outputs and is ignored. Allow-listed proof summaries under `reports/summaries/` are tracked.

## Where truth lives

| Source | Use |
|---|---|
| `README.md` | Orientation, scope, current package posture |
| `docs/PROJECT_MANIFEST.md` | Machine-readable project state and locks |
| `docs/12_Decision_Engineering_Log.md` | Append-only engineering/scope decisions |
| `docs/13_Evaluations_Log.md` | Evidence interpretations and artifact pointers |
| `docs/15_MVP_Release_Checklist.md` | Release-review input; not release authority |
| `docs/16_Paper_Protocol_Freeze.md` | Paper-facing locks, open fields, and provenance rule |
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
