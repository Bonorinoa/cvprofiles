# 18 — Measure Discipline Plan (v2.0)

**Status:** COMPLETE — plan approved 2026-08-05 (Augusto). **Threads (a) δ-grid, (b) evaluator registry, (c) θ-anchor discipline ALL COMPLETE** (2026-08-05). **Released as `2.0.0` on PyPI 2026-08-06** (tag `v2.0.0` @ `6abb6e4`), tutorial verified against the PyPI package. Dev cycle resumed at `2.0.1a1` (2026-08-06). **B4 methodology statement LOCKED 2026-08-06 (Option B, Augusto-approved) — all v2.0-DONE criteria complete.** See `docs/12`, 2026-08-05/06.

**Purpose:** the standing scope box for the v2.0 measure-discipline sprint. Three threads, strict TDD, one commit per milestone, a dated `docs/12` entry before each new code family. The four-state spine does not grow a fifth state; all work is IDENTIFY-internal or REPORT-adjacent.

## Scope box

**In (build order):**

1. **(a) δ-grid tolerance layer** — closes the 2026-08-01 provisional default ("always also report a small δ-grid as sensitivity, not headline"), deferred to v1.1, which shipped θ-grid but explicitly never scales δ.
2. **(b) Evaluator registry growth** — `mean_order` → `rank_agree` → `ols_coef`.
3. **(c) θ-anchor documentation discipline** — pre-data anchors as a first-class schema'd artifact.

**Out (deliberately):** `stability` evaluator (schema-only; no fixture demands it), `diff_means` β (same), LaTeX report, sharp-PI theory, measure generation, H5 expansion, GUI/SaaS, any new state.

## Decisions pinned 2026-08-05 (full text in `docs/12`)

| # | Decision | Pinned value |
|---|---|---|
| 1 | δ-grid semantics | **Absolute δ grid** (finite, unique, sorted, δ ≥ 0, duplicates fail loud); headline = declared δ run; grid excluded from freeze preimage; `delta_override` param on `run_identify` |
| 2 | Evaluator order | `mean_order` → `rank_agree` → `ols_coef`; each with own semantics lock; `stability`/`diff_means` stay fail-loud |
| 3 | ols_coef implementation | **Manual** — numpy closed-form point coefficient; no statsmodels core dep |
| 4 | θ-anchor artifact | Schema'd `anchors.yaml`; engine enforces completeness + `anchors_hash`; excluded from preimage; "pre-data" = process commitment |
| 5 | Version discipline | `1.1.0a1` through ENTRY; bump `2.0.0a1` atomically with golden refresh at ENTRY→DONE |
| 6 | v2.0 DONE | All four dimensions green **+ importable package with an H5-replication tutorial** |
| 7 | Doc hygiene first | Milestone 0 sweeps all doc drift + README before engine code |
| 8 | Sprint style | Per-thread checkpoints |
| 9 | H5 δ-grid run | Authorized, gated on thread (a); distinct `--out` dir |

## Thread (a) — δ-grid tolerance layer

Semantics: absolute δ values; per row re-run IDENTIFY with a δ override; headline = declared δ (computed outside the surface). Grid settings excluded from the freeze preimage (same bundle + different grid ⇒ same `run_id`, different `delta_grid.json`), mirroring the θ-grid contract including stale-layer cleanup. δ never touches `network_hash` — the override lives in `run_identify`, not in a network copy.

**Status: DONE** (2026-08-05; commits `11e5179`, `a44e65f`, `ab30d18`). H5 Trust δ-grid run on frozen inputs (seed 0): headline bit-identical; out_group admits at δ ≥ 0.005; designed-invalid `m_noise` admits at δ=0.5 (L → −0.319). Numbers in `docs/13` 2026-08-05. Diagnostic only.

| Milestone | TDD shape | Fixture that demands it | Gate bars |
|---|---|---|---|
| M-a1 module + validation (`cvprofiles/inference/delta_grid.py`) | RED: `tests/test_delta_grid.py` (module missing) → minimal impl → GREEN | mini_v1 oracle + harsh networks | ruff/mypy/pytest green |
| M-a2 engine: rows re-run `run_identify` with override | RED: headline-equality + monotone-superset tests → impl → GREEN | **Property:** M\*(δ₁) ⊆ M\*(δ₂) for δ₁<δ₂ (admission is `slack ≥ −δ`); harsh: empty at δ=0, nonempty past threshold | row at declared δ == headline (no implicit injection); slacks unchanged across rows |
| M-a3 wiring: `run_profile(delta_grid_deltas=...)`, CLI `--delta-grid`, artifact write, stale cleanup, report panel | RED first: CLI contract tests ("No such option"), bad input exit 2, stdout pure JSON | mini_v1 e2e; **witness:** same bundle + different grid ⇒ same `run_id` | default-params==golden run_id at pipeline level; empty rows first-class |
| M-a4 evidence + docs | — | — | `docs/13` row (diagnostic only); `docs/16` §6 pointer swept; H5 δ-grid run (authorized) |

## Thread (b) — evaluator registry growth

Registry reality: schema lists 5 restriction types, evaluators implement 2; β schema lists 3 types, evaluator implements 1. No speculative evaluator — each ships only when its fixture demands it.

| Milestone | TDD shape | Fixture that demands it | Gate bars |
|---|---|---|---|
| M-b1 `mean_order` in `slacks.py` | RED (today: `SlackError` "no evaluator") → impl → GREEN | New `data/fixtures/mean_order_v1/` (group column; valid gap ≥ θ, invalids below) | hand-computed slack equality; RESTRICT binds group column |
| M-b2 `rank_agree` in `slacks.py` | RED→GREEN same shape | New `data/fixtures/rank_agree_v1/` (ref_measure column) | Spearman ρ − θ golden; ref column binding; non-finite ρ → `SlackError` |
| M-b3 `ols_coef` in `beta_fn.py` | RED: "not implemented" → impl → GREEN | New fixture (outcome + control columns) | hand-computed β (1e-9); `params.controls` required; headline default remains `corr_y` |
| M-b4 evidence + report | report panel shows β method label | e2e across fixtures | full suite; `docs/13` row; goldens untouched |

**Status: DONE** (2026-08-05; commits `910ee0d`, `83cd1a7`, `15720c1`). mean_order / rank_agree / ols_coef implemented with hand-golden fixtures; full suite 196 passed; `docs/13` 2026-08-05. Feature layer; headline semantics unchanged.

## Thread (c) — θ-anchor documentation discipline

**Why (rationale):** θ values currently live as prose (`docs/17` §6) — correct discipline but unverifiable. The anchor artifact makes it machine-checkable: one anchor per restriction, hashed into the run manifest so the report cites exactly the anchors the run used, and an auditor can assert "every θ has a pre-data anchor" without reading prose. Preregistration for thresholds; the anti-data-mining guard behind "literature-grounded, not data-mined."

**Honest boundary:** the engine cannot verify *when* a file was written. It enforces completeness + hash; "pre-data" remains Augusto's process commitment.

| Milestone | TDD shape | Fixture that demands it | Gate bars |
|---|---|---|---|
| M-c1 schema + validation + hash (`cvprofiles/anchors/`) | RED: `tests/test_anchors.py` (unknown id fails, missing anchor fails, valid hashes) → impl → GREEN | mini_v1 network (2 restrictions) + H5 pinned network (3 restrictions; anchors transcribed from `docs/17` §6) | completeness (every id, exactly one); `anchors_hash` = SHA-256 canonical JSON; **witness:** ± anchors ⇒ same `run_id` |
| M-c2 REPORT integration + manifest | RED: report test asserts anchors panel → impl → GREEN | mini_v1 with anchors | `anchors.json` in run dir; manifest records `anchors_hash`; None-safe template guard |
| M-c3 H5 retrofit + verifier extension | RED: `tools/verify_h5_trust.py` asserts completeness → extend → GREEN | H5 pinned network | auditor exit 0; anchors file under `evals/h5_trust/data/` |
| M-c4 workflow guidance + close-out | — | — | `docs/14` DRAFT section; `docs/13` row |

**Status: DONE** (2026-08-05; commits `0a33554`, `4e8d15e`, `213548c`). H5 transcription audited (exit 0, 0 errors); docs/14 §13 practice guidance. **ENTRY (threads a/b/c) COMPLETE.**

## v2.0 criteria (ENTRY = measure discipline delivers first; DONE = release)

**Status map (2026-08-06, post-publication):**

| Dimension | ENTRY | DONE |
|---|---|---|
| A. Functional / feature | ✅ A1–A5 | ✅ shipped + release-verified |
| B. Measurement-methodological | ✅ B1–B3 | ✅ **B4 methodology statement (2026-08-06, Option B)**; ✅ B5 |
| C. Evidence / paper / observability | ✅ C1–C2 | ✅ C3–C5 (tutorial verified against the PyPI package) |
| D. Engineering / release | ✅ D1–D2 | ✅ D3–D5 (`2.0.0` published; dev `2.0.1a1`) |

**B4 — methodology statement LOCKED** (docs/03 §Statement of methodology, 2026-08-06, Option B; Augusto-approved wording). **All v2.0-DONE criteria complete.**

### A. Functional / feature
- A1 (ENTRY) δ-grid ships — `test_delta_grid.py`: grid validation; per-row payload; headline equality; monotone superset; preimage exclusion witness.
- A2 (ENTRY) evaluators `mean_order`/`rank_agree`/`ols_coef` — per-evaluator hand-computed goldens; unimplemented types still fail loud.
- A3 (ENTRY) θ-anchor artifact — completeness, unknown-id failure, hash; ± anchors ⇒ same `run_id`.
- A4 (ENTRY) wiring end-to-end, default path bit-stable — `test_v2_wiring.py`: default `run_profile` reproduces golden `run_id`; CLI contract (exit 2 on bad input; stdout pure JSON; empty M\* exit 0).
- A5 (ENTRY) report renders new panels — null/empty guards; JSON report includes them.

### B. Measurement-methodological
- B1 (ENTRY) each evaluator has a locked semantics — dated `docs/12` entry precedes code; golden equality tests.
- B2 (ENTRY) δ-grid reporting distinguishes headline from tolerance surface — declared-δ row marked headline; no auto-loosening.
- B3 (ENTRY) anchor completeness enforced per network — validator test; no engine temporal claim.
- B4 (DONE) methodology statement updated — `docs/03` or dated amendment; `docs/16` §6 pointer swept.
- B5 (DONE) H-gate battery re-run under v2.0 dev version — tools + verifiers exit 0; goldens refreshed atomically.

### C. Evidence / paper / observability
- C1 (ENTRY) H5 evidence regenerable under v2.0 with anchors — `verify_h5_trust.py` (extended) + `verify_v11_protocol_synth_mc50.py` exit 0.
- C2 (ENTRY) manifest records `anchors_hash` + grid settings as metadata, not preimage.
- C3 (DONE) v2.0 evidence re-audited; `docs/13` rows per thread; paper numbers only from frozen inputs + pinned network + fixed seed + package version.
- C4 (DONE) artifact inventory matches disk; no silent no-op params.
- C5 (DONE, **new**) **H5 replication tutorial**: the end output of v2.0 is an importable `cvprofiles` package; a tutorial (docs/ or `evals/h5_trust/`) reproduces M\*={m_trust_general, m_trust_in_group}, [L,U]=[0.371,0.624] from frozen inputs via the installed wheel.

### D. Engineering / release
- D1 (ENTRY) strict TDD, one commit per milestone.
- D2 (ENTRY) ruff/mypy/CI green (3.11/3.12); import-graph hygiene extended.
- D3 (DONE) bump `2.0.0a1` atomically with golden refresh; `uv build` clean; fresh-venv wheel smoke bit-identical on mini + H5.
- D4 (DONE) tags immovable: `v0.1` @ `fb62b48…`, `v1.1.0` @ `fce31c8…`; no push/tag/PyPI without explicit instruction.
- D5 (DONE) dependency discipline: ols_coef manual (no new core dep); no heavy deps in core CI path.

## Verification battery (per milestone)

```bash
uv run ruff check src tests tools
uv run mypy src
uv run pytest -q --tb=short
uv run cvprofiles --version
git diff --check
git rev-parse 'v0.1^{}'
git rev-parse 'v1.1.0^{}'
```

## Checkpoint protocol

- Stop after each thread for go/no-go (AGENTS.md default; per-thread authorized 2026-08-05).
- One commit per milestone; decision-log entry precedes each new code family.
- Progress read from on-disk artifacts + dual logs, not git archaeology.
