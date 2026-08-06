# cvprofiles — Post-Release Audit (2026-08-06)

**Scope:** methodology, software system, and open-source infrastructure (CI/CD + packaging).
**Object:** `cvprofiles` v2.0.0 (PyPI, published 2026-08-06), repo HEAD `5be92f1` (dev `2.0.1a1`).
**Auditor stance:** independent re-verification — nothing taken on trust from the release session.
**Status:** AUDIT COMPLETE — 3 findings, 2 doc-drift items, 1 open v2.0-DONE criterion, 6 recommendations (non-blocking).

---

## 0. Executive verdict

The release claim **holds up to independent re-verification**. The local wheel in `dist/` is
bit-identical to the PyPI artifact (sha256 match), the full local battery is green (217 tests,
ruff, mypy strict, both proof verifiers), CI is green on the current head, tags are immovable
and pushed, and a **new second tutorial executes end-to-end against `pip install cvprofiles==2.0.0`**
with all self-checking assertions passing.

The one caveat to the previous session's "verified everything": verification was tutorial +
battery + verifiers — strong, but not coverage-measured, and the CI does not build/install the
wheel. Those are cheap to close (Section 5).

**Headline numbers (re-verified this session):**

| Check | Result |
|---|---|
| Local battery (pytest / ruff / mypy strict / diff / tag peel) | 217 passed · clean · clean · OK · `v0.1→fb62b48` |
| MC50 proof verifier (`verify_v11_protocol_synth_mc50.py`) | `{"passed": true, "scenario_seed_cells": 200}`, exit 0 |
| H5 Trust verifier (`verify_h5_trust.py`, correct invocation) | `{"errors": [], "passed": true}`, exit 0 |
| Wheel sha256 vs PyPI JSON API digest | **match** (`a125ae1d…`) |
| PyPI version / requires-python | `2.0.0`, `>=3.11`, yanked=false |
| CI on HEAD `5be92f1` (GitHub API) | success (2026-08-06T02:15:29Z) |
| Git sync | local `main` == `origin/main`; tags `v0.1`, `v1.1.0`, `v2.0.0` pushed, annotated, immovable |
| New diagnostics-tour tutorial vs installed PyPI package | executes clean, **ALL ASSERTIONS PASSED** |

---

## 1. Methodology audit — formalization ↔ engine

**Single source of truth (docs/03 §"Compact formalization", lines 23–36) vs engine:**

| Formalization | Engine | Verdict |
|---|---|---|
| Menu `M = {m_j}` finite, researcher-supplied | `roles.measures` (`score/pipeline.py:32-37`); no prompt search | ✅ |
| `r ∈ R`: `E[g_r(m, V; θ_r)] ≥ 0` | registry `RestrictionSpec` (`schemas/network.py:11-17,20-65`) | ✅ |
| Slack `s_r(m)`; `M* = {m : s_r ≥ 0 ∀r}` (with δ) | `slack_matrix` + admit iff `slack ≥ −δ` (`identify/pipeline.py:93-104`; `slacks.py:116-129`) | ✅ |
| `B* = {β(m) : m ∈ M*}`; `[L,U] = min/max B*` | `beta_values` on full menu; range on survivors only (`identify/pipeline.py:106-120`) | ✅ |
| Empty `M*` = feature, not crash; `[L,U]` null | `empty=True`, `range_L/U=None`, exit 0 (`identify/pipeline.py:113-116`; `cli.py:147-151`) | ✅ |
| Never auto-loosen θ | no auto-loosening path exists; θ-grid λ never auto-selected (`inference/theta_grid.py:10-12`) | ✅ |
| Bootstrap over **units**, menu fixed | `run_bootstrap` units-only, `default_rng(seed)`, percentile over non-empty, degenerate counted (`inference/bootstrap.py:59-147`) | ✅ |
| θ-grid diagnostic; sign never scaled; excluded from preimage | `lambda_value` scales magnitudes only; grid not in freeze preimage (`inference/theta_grid.py:1-21`) | ✅ |
| δ tolerance absolute; IDENTIFY-side override | `delta_override` never touches `network_hash`/`beta_hash` (`identify/pipeline.py:78-82`) | ✅ |
| θ-anchor: schema'd, completeness-checked, excluded from preimage | `anchors/pipeline.py:97-126`; witness test passes | ✅ |
| Paper numbers only from frozen inputs + pinned network + seed + version | freeze/run_id contract (`freeze.py:1-31`); NaN/Inf fail loud (`freeze.py:86-90`) | ✅ |

**Registry coverage:** `corr_min`, `corr_sign`, `mean_order`, `rank_agree` implemented with
hand-computed goldens; `stability` schema-only and **fails loud** at IDENTIFY
(`slacks.py:110-113`) — per the "schema may list types not yet evaluated" lock. β: `corr_y`,
`ols_coef` (numpy closed-form, no statsmodels, `beta_fn.py:22-44`); `diff_means` declared but
unimplemented → fail loud at evaluate (`beta_fn.py:74-77`).

**Inference stance is honest and conservative:** the bootstrap band is pointwise and
conditional on admission (`docs/12`, 2026-08-01 entry, line 432); degenerate replicates are
counted, never dropped (`bootstrap.py:109-114`). The headline `[L,U]` is never replaced by any
diagnostic layer — verified by the composition regression test (`test_v2_wiring.py`) and by
the new tutorial.

### Findings (methodology)

- **M1 — docs/03 `corr_min` semantics row is stale (DRAFT-catalog vs engine).**
  `docs/03_Methodology.md:63` sketches `corr_min` as `|Corr| − θ` (absolute). The engine
  implements a **signed lower bound** `Corr − θ` (`slacks.py:59-64`), which is also the
  semantics used by the H5 design (`docs/17_H5_Trust_Design.md:59-60,70-71`: "corr ≥ 0.3")
  and by both tutorials. The engine is right (an absolute-correlation "min" would admit
  anti-correlated measures — nonsense for trust). **Fix the doc, not the code:** amend the
  `docs/03` row to `Corr(m, V_k) ≥ θ` / `Corr − θ`, and note the correction in `docs/12`.
- **M2 — `docs/17` design example uses `direction:`; engine schema uses `sign:`.
  `docs/17_H5_Trust_Design.md:61` shows `corr_sign(gini, direction: -1, ...)`, but the engine
  validates `params.sign ∈ {+1,−1}` (`schemas/network.py:53-56`) and the frozen H5 input uses
  `sign: -1` (`evals/h5_trust/data/network_h5_trust.yaml:14-16`). The pinned input is correct;
  the design-doc example is stale. Fix the example line.
- **M3 — B4 methodology statement is still open** (the only remaining v2.0-DONE criterion,
  per `docs/18_Measure_Discipline_Plan.md` status map). It is a docs/03 amendment + paper-protocol
  step with **Augusto-owned wording**. The audit confirms nothing else blocks a v2.0-DONE close-out.
- **M4 — silent parquet-write swallow in IDENTIFY artifacts.** `identify/pipeline.py:154-155`
  wraps `to_parquet` in `try/except Exception: pass`. CSV remains the load-bearing artifact, so
  this is not a correctness risk, but it hides disk/permission failures. Recommend logging the
  skip to stderr or failing loud; keep CSV-first if you prefer resilience.
- **M5 — pytest suppresses all DeprecationWarnings** (`pyproject.toml:57`). This can hide
  upstream deprecations (pandas 3.x era). Recommend narrowing to specific warnings or removing.

**Methodology overall:** the compact formalization is a faithful, auditable contract, not a
marketing gloss. The closest-ancestor framing (Leamer-style specification uncertainty moved to
measurement functions) is preserved; nothing in the engine overclaims sharp PI.

---

## 2. Software audit

**Architecture:** true src-layout, 4-state module spine (`score/`, `restrict/`, `identify/`,
`report/`), inference layers additive (`inference/`), pydantic `extra="forbid"` schemas, domain
errors wrapping pydantic at both file and dict IO paths (`restrict/pipeline.py:34-86`;
`anchors/pipeline.py:71-94`). Import graph is LLM-free and museum-free — enforced by an AST
check in CI (`ci.yml:49-75`) and by `test_import_graph.py`.

**Determinism:** canonical JSON/CSV hashing with NaN/Inf fail-loud (`freeze.py`), 17-significant-
digit float formatting, run_id preimage excludes wall clock/paths/hostnames. Version is in the
preimage, so version bumps atomically refresh goldens — the tooling exists
(`tools/refresh_mini_golden.py`) and the rule is respected (goldens refreshed in the same
commits as bumps).

**Test suite:** 26 test files; 217 tests pass in ~6s. Covers schemas, freeze, each evaluator
(`test_mean_order.py`, `test_rank_agree.py`, `test_ols_coef.py`), bootstrap/θ-grid/δ-grid,
anchors, wiring (stale-artifact cleanup), import graph, mini-fixture contract, H5 engine smoke,
and the two proof auditors. **Gap:** no coverage measurement configured — the suite exercises
all modules but the coverage fraction is unknown. Recommend `pytest-cov` (report-only at first).

**CLI contract:** stdout pure JSON, stderr crumbs, exit 0 on empty `M*`, fail-loud grid parsers
(duplicates/positivity), `--n-boot` min 0 (`cli.py:22-61,84-151`). Verified live via the new
tutorial's CLI cell (`exit code: 0`, parsed JSON agrees with the engine).

**Post-release reliability hardening is real:** the `anchors.json` stale-artifact cleanup fix
(`eb2bbb6`) closes a genuine run-dir mirroring hole, with a witness test. Run directories
mirror exactly the layers produced — verified in the new tutorial's artifact listing (18 files,
exactly the expected set).

---

## 3. Release & provenance verification (independent)

| Claim from release session | Re-verification | Verdict |
|---|---|---|
| "2.0.0 published on PyPI" | PyPI JSON API: version present, not yanked, upload 2026-08-06T01:27Z | ✅ |
| "Local wheel == PyPI artifact" | `shasum -a 256 dist/…whl` = `a125ae1d…` == PyPI `digests.sha256` | ✅ |
| "Tutorial verified against PyPI package" | New venv, `pip install cvprofiles==2.0.0`; **new** tutorial executes, ALL ASSERTIONS PASSED | ✅ |
| "CI green on reconciliation head" | GitHub Actions API: `5be92f1` → success | ✅ |
| "Tags immovable" | `v0.1→fb62b48`, `v1.1.0→fce31c8`, `v2.0.0→6abb6e4`; all present on origin | ✅ |
| "H5 replication bit-identical" | H5 verifier passes on the frozen proof + `runs_verify/default`; evidence summary numbers `[0.370754, 0.623891]` intact | ✅ |

**One CI wrinkle, honestly documented:** the atomic version alignment to `2.0.0` missed the
CLI-smoke version literal → CI failed on `965c73e`, fixed one commit later (`7c20919`) and
green since. This is exactly the pitfall now in the skill runbook; no recurrence on `83472f9`,
`eb2bbb6`, or `5be92f1`.

---

## 4. Open-source infrastructure evaluation

### Strengths (unusually good for an academic methods package)

- **uv-first, hatchling, src-layout** with `requires-python >=3.11`, py3.11/3.12 matrix
  (`pyproject.toml:46-53`, `ci.yml:17-21`).
- **CI contract** covers ruff, mypy strict, pytest, CLI version smoke, AST import-graph hygiene,
  and a mini-fixture end-to-end smoke with assertions (`ci.yml:35-97`). Concurrency cancel,
  `fail-fast: false`.
- **Release discipline:** immutable annotated tags + manifest SHAs, CHANGELOG, AGENTS.md,
  dual live logs, atomic version bumps, golden refresh tooling, committed proof verifiers,
  allow-listed proof summaries vs ignored bulk runs.
- **Security posture:** user-owned PyPI token (never in chat/agent), independent verification
  chain (PyPI JSON + sha256 + fresh-venv notebook). This is the right shape for an academic repo.
- **Honest metadata:** `Development Status :: 3 - Alpha` matches reality; MIT; LICENSE present.

### Gaps (prioritized)

| # | Gap | Why it matters | Cost | Recommendation |
|---|---|---|---|---|
| R1 | **No wheel build/install check in CI** | The mini-fixture smoke runs the *editable* install; packaging regressions (force-include duplicates, missing templates) surface only at release time. The runbook hit one (`uv build` duplicate-path). | Low | Add a CI job: `uv build` → fresh-venv install of the wheel → run one profile + assert report.html exists. |
| R2 | **No coverage measurement** | "217 tests pass" ≠ coverage of all branches; the audit can't certify the uncovered fraction. | Low | Add `pytest-cov` (dev extra) + report-only CI step; set a soft floor later. |
| R3 | **PyPI landing README is stale** | Published description still says "publication in progress / PyPI publication pending" (README at publish time, polished after). Cosmetic but visible to adopters. | Trivial | Fold into the next release (PyPI doesn't allow same-version re-upload). Do **not** burn a 2.0.1 for it unless adoption matters now. |
| R4 | **Manifest `dev_version` stale** | `docs/PROJECT_MANIFEST.md:9` still `2.0.0` while package is `2.0.1a1`. Doc/code current-state drift — the exact class AGENTS.md says to surface. | Trivial | Add `docs/PROJECT_MANIFEST.md dev_version:` to the atomic version-bump checklist; fix now. |
| R5 | **License metadata style** | `license = { text = "MIT" }` (legacy table) vs modern SPDX `license = "MIT"` + `license-files`. | Trivial | Modernize at next bump. |
| R6 | **Optional release automation** | A `publish.yml` with trusted publishing (OIDC) would remove the manual token flow. | Medium | Optional — the current user-owned flow is deliberate and safe. If you adopt OIDC, keep the independent verification chain. |

Also worth considering (non-blocking): py3.13 in the matrix when stubs allow; a `uv lock --check`
CI step; `Development Status` → Beta once a non-dev stable line stabilizes; Dependabot for dev
deps if you want freshness alerts.

---

## 5. New tutorial — `tutorials/cvprofiles_diagnostics_tour.ipynb`

Built and **executed against the installed PyPI package** (`cvprofiles==2.0.0` in a fresh
venv, wheel-only, `PYTHONPATH` unset). 24 cells, fully self-contained (no repo files).

What it demonstrates, with real executed numbers:

| Capability | Executed result |
|---|---|
| All 4 evaluators in one network | slack matrix prints all four columns; `m_weak`'s rank_agree slack 0.046 = the "barely admissible" margin |
| `ols_coef` β with control | β(m_good)=0.4505, β(m_weak)=0.2262, β(m_groupy)=0.4552 |
| Wide range as finding | `[L,U] = [0.226, 0.455]` with 3 admissible measures |
| θ-grid | λ=1.5 drops `m_weak` → range tightens to [0.4505, 0.4552]; λ≥2.0 **empty** |
| δ-grid monotone | 3 → 4 → 5 measures; at δ=0.9 range [−0.263, 0.455] — discipline evaporates |
| Bootstrap band additive | band [0.134, 0.544]; 200/200 non-empty; headline untouched |
| Anchors | same `run_id` with/without anchors; incomplete set → `AnchorError` naming the missing ids |
| CLI | `cvprofiles run` exit 0, stdout pure JSON, agrees with the Python API |
| Contracts | **ALL ASSERTIONS PASSED** (survivors-only range, preimage exclusion, monotonicity, empty honesty) |

Files changed (uncommitted): `tutorials/cvprofiles_diagnostics_tour.ipynb` (new, clean, no
executed outputs), `tutorials/README.md` (wired in + execute commands).

---

## 6. Open items for Augusto

1. **B4 methodology statement** — the last v2.0-DONE criterion; wording is yours. I can draft
   for your review, but per the authority lock it stays your call.
2. **M1/M2 doc-drift fixes** (docs/03 `corr_min` row, docs/17 `direction:` example) + R4
   (manifest `dev_version`) — one small docs commit, or fold into the next sprint's drift sweep.
3. **R1/R2 (CI wheel-build check + coverage)** — my recommendation for the next release cycle;
   low cost, closes the "verified because the tutorial worked" gap properly.
4. **Commit/push of the new tutorial** (and optionally this audit report under `audits/`).
5. **R3** — decide whether the stale PyPI landing text matters enough for a 2.0.1 sooner than the
   natural next release.

---

## Appendix — evidence commands (all run this session)

```
uv run ruff check src tests tools            # All checks passed!
uv run mypy src                              # Success: no issues in 31 source files
uv run pytest -q --tb=short                  # 217 passed in 6.12s
uv run cvprofiles --version                  # cvprofiles 2.0.1a1
git rev-parse 'v0.1^{}'                      # fb62b48bcb704f60eee7d6641ed0a344eb72bfda
shasum -a 256 dist/cvprofiles-2.0.0-py3-none-any.whl   # a125ae1d… == PyPI digest
uv run python tools/verify_h5_trust.py --proof evals/h5_trust/proof_summary.json \
  --roles evals/h5_trust/data/roles_h5_trust.json --out-root evals/h5_trust/runs_verify/default \
  --anchors evals/h5_trust/data/anchors_h5_trust.yaml --network evals/h5_trust/data/network_h5_trust.yaml
                                                  # {"errors": [], "n_errors": 0, "passed": true}
uv run python tools/verify_v11_protocol_synth_mc50.py   # {"errors": [], "passed": true, ...}
# GitHub REST API: /repos/Bonorinoa/cvprofiles/actions/runs — 5be92f1 success
# Fresh venv: pip install cvprofiles==2.0.0 jupyter nbconvert ipykernel
# nbconvert --execute on a copy of the new tutorial → ALL ASSERTIONS PASSED
```

Note on the H5 verifier: the correct invocation targets `evals/h5_trust/proof_summary.json`
(the proof artifact) + `runs_verify/default` (the run artifacts), not the compact evidence
summary under `reports/summaries/`. The latter is an index, not the audited proof — worth a
comment in the tool or README so the next auditor doesn't repeat my first (wrong) invocation.

---

## Follow-up (same day) — findings closed, B4 pending

All actionable findings from this audit were closed on 2026-08-06 (see `docs/12` entry and
`CHANGELOG.md` [Unreleased]):

| Item | Closure |
|---|---|
| M1 (docs/03 corr_min row) | corrected to signed lower bound; engine canonical |
| M2 (docs/17 `direction:`) | example corrected to `sign: -1`; pinned input untouched |
| M4 (silent parquet fallback) | warns on stderr now; TDD test `tests/test_audit_fixes.py` |
| M5 (DeprecationWarning suppression) | blanket filter removed; suite green |
| R1 (no wheel build/install in CI) | new `wheel-smoke` job added |
| R2 (no coverage) | `pytest-cov`; CI reports; **local 88%** of `cvprofiles` |
| R3 (PyPI landing README) | deferred to next release (no same-version re-upload) |
| R4 (manifest `dev_version`) | refreshed to `2.0.1a1` |
| R5 (license metadata) | `license = "MIT"` (PEP 639), build verified |
| R6 (OIDC publish) | deferred — user-owned token flow stays deliberate posture |
| New tutorial | `tutorials/cvprofiles_diagnostics_tour.ipynb` shipped + executed vs PyPI wheel |

**B4 LOCKED** — v2.0 methodology statement (docs/03 §Statement of methodology, Option B,
Augusto-approved 2026-08-06). **All findings closed.**
