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

The current paper protocol (`governance/PAPER_PROTOCOL_FREEZE.md`) is **LOCKED AS PROVISIONAL SYNTHETIC-ONLY**. It does not authorize engine changes, pushes, tags, PyPI publication, or a release claim by implication; empirical work runs only under its dated amendments. The designated H5 Trust evaluation ran 2026-08-04, was re-graded historical 2026-08-07 (§9), and the lane was removed from the repository 2026-08-21. **2026-08-10 (§11):** the **WVS/GPS patience application** is the **flagship public-facing empirical example** — run-gated (frozen scores + pinned network/β + fixed seed + package version + independent audit exit 0 + owner's run decision); the **IVS cultural-values evaluation** (`governance/IVS_CULTURAL_MAP.md`) is **deferred** (design container RESERVED, not active). Open-weight policy for v3: open-weight local models and interpretable artifacts only; no DPO adapters, no proprietary APIs (D5/D6, §9). Final paper lock, tag, and PyPI remain the owner's.

Post-release hygiene (2026-08-21): the H5 evaluation lane (`evals/h5_trust/`, `tools/verify_h5_trust.py`, H5 tests, proof summary) was deleted; internal sprint notes under `reports/` are local-only; docs were reorganized into public `docs/`, append-only `logs/`, and `governance/`.

## Current posture

- Package version: `3.0.2` — **v3.0.2 reproducibility patch (2026-08-18)**: closes external-audit F1–F8 (round-trip CSV parsing; golden tolerances; `--skip-build`; current-menu empty_R re-freeze `[-0.219, 0.565]`; committed partial r). v3.0.1 (2026-08-14) added the named `empty_R` unrestricted-multiverse special case; v3.0.0 remains the infrastructure + flagship application release (WVS/GPS patience: headline `M*_select = [m_gps_patience, m_prompt_a]`, `[L,U] = [0.328, 0.402]`; `docs/16` §11/§12). v2.5.2 was the WVS/GPS tutorial milestone PyPI release (2026-08-09); v2.5.1 was the first PyPI since 2.0.0; v2.5.0 was the Rev 3 P1–P5 infrastructure checkpoint. P6 deferred to v3.1.
- v1.1 inference layer shipped and **tagged `v1.1.0`** (2026-08-04, `fce31c8`); superseded by the 2.0.0 release.
- **v2.0 measure discipline DONE** (plan: historical, untracked since 2026-08-21 — `docs/archive/18_Measure_Discipline_Plan.md` in git history): δ-grid, evaluator growth (`mean_order`/`rank_agree`/`ols_coef`), θ-anchor artifacts shipped 2026-08-05; tutorial verified against the PyPI package; released as `2.0.0`. **B4 methodology statement LOCKED 2026-08-06 — all v2.0-DONE criteria complete.**
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
| `logs/DECISIONS.md` | Append-only engineering/scope decisions (formerly `docs/12_Decision_Engineering_Log.md`; relocated 2026-08-21) |
| `logs/EVALUATIONS.md` | Evidence interpretations and artifact pointers (formerly `docs/13_Evaluations_Log.md`) |
| `governance/PAPER_PROTOCOL_FREEZE.md` | Paper-facing locks, open fields, and provenance rule (formerly `docs/16_Paper_Protocol_Freeze.md`; § numbering retained) |
| `governance/H5_TRUST_DESIGN.md` | H5 Trust design record — **SUPERSEDED**: lane removed from the repo 2026-08-21 |
| `governance/IVS_CULTURAL_MAP.md` | IVS cultural-values lane design container (run gated; deferred) |
| `governance/PROJECT_MANIFEST.md` | Machine-readable project state and locks |
| `paper/` | Methods-journal paper source (moved from the lab repository 2026-08-21) |
| `audits/` | Dated audit reports (findings + closure status); internal sprint notes under `reports/` are local-only |
| `pyproject.toml` | Package version, dependencies, lint/type/test configuration |
| `.github/workflows/ci.yml`, `.github/workflows/release.yml` | CI contract; tag-push release pipeline |
| `.gitignore` | Tracked proofs versus ignored run output |

Historical note: pre-consolidation scaffold docs that lived in `docs/archive/` were removed from tracking 2026-08-21; recover with `git show v3.0.2:docs/archive/<file>` if ever needed. References to `docs/12|13|16|17|18` in older documents map to the relocated paths above.

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
