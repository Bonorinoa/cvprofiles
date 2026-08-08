# cvprofiles — Grounded Package-State, Gap-Inventory & Paper-Readiness Scan

**Scan agent:** read-only sweep of `~/Hermes/Projects/cvprofiles` (no modifications, no terminal).
**Date:** 2026-08-07. **Consumer:** lead engineer agent (v3.0.0 scheduling + Nature/PNAS-level position-paper prep, SCA2 cultural applications).
**Method:** every claim grounded in a file path + line reference. Anything not found in the tree is marked **not found**.

---

## 1. PACKAGE STATE

### 1.1 Version and identity
| Field | Value | Source |
|---|---|---|
| Package name | `cvprofiles` | `pyproject.toml:2` |
| Version | **`2.0.1a1`** (dev cycle after 2.0.0) | `pyproject.toml:3`, `src/cvprofiles/__init__.py:5` |
| License | MIT | `pyproject.toml:6` |
| requires-python | `>=3.11` | `pyproject.toml:7` |
| Author | Augusto Gonzalez Bonorino | `pyproject.toml:8` |
| Build backend | hatchling (src-layout) | `pyproject.toml:47-49` |
| CLI entry | `cvprofiles = cvprofiles.cli:app` | `pyproject.toml:44-45` |

### 1.2 Release history (per AGENTS.md + docs/12 + manifest)
| Tag / release | SHA / date | Status |
|---|---|---|
| `v0.1` (annotated, immovable) | `fb62b48bcb704f60eee7d6641ed0a344eb72bfda`; must keep peeling there | AGENTS.md:26; PROJECT_MANIFEST.md:15-16 |
| `v1.1.0` (MVP + inference layer) | `fce31c8`, tagged 2026-08-04; superseded by 2.0.0 | AGENTS.md:44; PROJECT_MANIFEST.md:17-18 |
| `v2.0.0` (measure discipline) | `6abb6e4`, **published on PyPI 2026-08-06**; wheel sha256 == PyPI digest verified | AGENTS.md:43; docs/12 (2026-08-06 entry); audits/2026-08-06_post_release_audit.md:12-16, 26-33 |
| Dev cycle | `2.0.1a1` resumed 2026-08-06 (atomic bump, golden refresh) | docs/12 (2026-08-06 "dev cycle resumed" entry, line 839-841) |

PyPI posture: 2.0.0 live (wheel + sdist, owner Bonorinoa, `>=3.11`, yanked=false); PyPI project description is the pre-publication README (cosmetic staleness, refreshes at next release) — docs/12 line 821-822, audits file:30.

### 1.3 Engine state machine
`SCORE → RESTRICT → IDENTIFY → REPORT` (AGENTS.md:10-16; ARCHITECTURE.md §1:7-44). Invariant: frozen scores + pinned network + fixed seed ⇒ bit-stable run (ARCHITECTURE.md:53). No LLM in engine/import graph (AGENTS.md:20; enforced in CI, `ci.yml:52-78`).

### 1.4 Module map (shipped layout, ARCHITECTURE.md §2:57-71 + source)
| Module | One-line purpose |
|---|---|
| `src/cvprofiles/__init__.py` | version only (`__version__ = "2.0.1a1"`, `__init__.py:5`) |
| `cli.py` | thin Typer CLI, `cvprofiles run`; stdout=JSON, stderr=human; empty M* = exit 0 (`cli.py:84-209`) |
| `pipeline.py` | `run_profile()` composition of 4 states + additive inference layers; freeze bundle; stale-layer cleanup (`pipeline.py:67-268`) |
| `freeze.py` | canonical hashing, run_id, `n_boot` normalization (`freeze.py:1-279`) |
| `score/` | load → validate → normalize → frozen manifest + scores_hash (`ARCHITECTURE.md:63`) |
| `restrict/` | network/beta parsers, column binding, hashing (`ARCHITECTURE.md:64`) |
| `schemas/` | pydantic v2 (extra=forbid): scores, network, beta, run (`ARCHITECTURE.md:65`) |
| `identify/` | slacks → M* → β image → [L,U]=min/max B*; `slacks.py` (restriction registry), `beta_fn.py` (β registry) (`ARCHITECTURE.md:66`) |
| `inference/` | bootstrap, theta_grid, delta_grid — **additive diagnostics**, excluded from freeze preimage (`ARCHITECTURE.md:67`; `pipeline.py:5-17`) |
| `anchors/` | θ-anchor parse, completeness check, `anchors_hash` (excluded from preimage) (`ARCHITECTURE.md:68`; `anchors/pipeline.py:1-136`) |
| `report/` | JSON dump + Jinja2 HTML from one shared payload (`ARCHITECTURE.md:69`; `report/pipeline.py:35-60`) |
| `synth/` | DGPs + oracle networks + metrics — eval only, not paper path (`ARCHITECTURE.md:70`) |

### 1.5 Test suite facts
- **27 test files** under `tests/` (`test_*.py`, search_files target=files) — includes per-evaluator suites (mean_order, rank_agree, ols_coef, anchors, delta_grid, theta_grid, bootstrap), freeze, identify, H5-trust (build/verify/engine-smoke), import-graph hygiene, run_many, v1_1/v2 wiring.
- **169 `def test_` functions** counted across test files (search_files count; excludes conftest). Parametrization means pytest-collected total is higher; last logged full-suite count: **222 passed** (docs/12 line 936, 2026-08-06 batch orchestrator); 217 passed at the post-release audit (audits file:26).
- pytest config: `testpaths=["tests"]`, `pythonpath=["src"]`, marker `slow` (pyproject.toml:55-60).
- CI: `.github/workflows/ci.yml` — matrix py3.11+3.12; steps: ruff (src+tests+tools), docs-math-delimiter check, mypy strict, pytest+coverage (report, no gate), CLI version smoke (asserts `2.0.1a1`), import-graph hygiene (no LLM, no museum import), mini-fixture run smoke, and a `wheel-smoke` job (build + fresh-venv install + profile run) (`ci.yml:13-143`).

### 1.6 Lint / type tooling
- ruff: line-length 100, target py311, select `E,F,I,UP,B`; per-file ignore `tools/verify_h5_trust.py: E501` (pyproject.toml:62-74).
- mypy: `strict = true`, `python_version = "3.12"` (superset target for numpy 2.5 PEP-695 stubs), packages `cvprofiles`, `mypy_path="src"` (pyproject.toml:76-84). Local battery mirrors CI (AGENTS.md:93-99).

---

## 2. DOCS & GOVERNANCE STATE

### 2.1 Locked / dated docs
| Doc | Lock state |
|---|---|
| `docs/METHODOLOGY.md` | **"Canonical methodology statement (locked 2026-08-06, B4)"** (METHODOLOGY.md:3); "Package semantics are canonical where this doc and code disagree" (METHODOLOGY.md:3) |
| `docs/12_Decision_Engineering_Log.md` | append-only engineering/scope decisions; "Do not rewrite history — reverse a decision with a new dated entry" (docs/12:3-5); dated entries 2026-08-01 → 2026-08-06 |
| `docs/13_Evaluations_Log.md` | append-only evidence narrative (docs/13:3-7) |
| `docs/16_Paper_Protocol_Freeze.md` | **Status line (line 3):** "`protocol-v1-synth-provisional` — provisional synthetic-only lock; empirical/paper fields remain open". Protocol rule: post-lock changes require a dated amendment; "Silence is not consent" (docs/16:21) |
| `docs/17_H5_Trust_Design.md` | **"LOCKED AS H5 DESIGN (2026-08-04) … Empirical run gated"** (docs/17:3); run requires frozen scores + pinned seed + package version + independent audit + Augusto's run decision (docs/17:118) |
| `docs/ROADMAP.md` | live; no v3 scope box yet — "Next-sprint scope box: to be drafted after the v2.0 release" (ROADMAP.md:32) |
| `docs/PROJECT_MANIFEST.md` | machine-readable state; h5_trust block records M*, [0.370754, 0.623891], n=35 (PROJECT_MANIFEST.md:50-64) |
| `audits/2026-08-06_post_release_audit.md` | post-2.0.0 audit; verdict "release claim holds up"; 3 findings, 6 non-blocking recommendations (audits file:6, 10-16) |

### 2.2 docs/16 §8 amendment (2026-08-04, dated) — quotes
- **Status update:** "for the H5 Trust evaluation only, the researcher-owned fields in §3 are **LOCKED as design** per `docs/17_H5_Trust_Design.md`, approved by Augusto on 2026-08-04" (docs/16:127-129) — construct paragraph, unit/universe (country `iso3`, WVS7 ∩ GPS, n≈40, floor ≥ 200), menu (4 valid WVS facets + 2 designed-invalid), network `R` (gps_trust 0.3 / rule_of_law 0.3 / gini −0.1), θ anchors pre-data, δ=0, β=`corr_y` on `log_gdp_pc`.
- **Run decision (2026-08-04):** "Augusto granted **preliminary paper-facing evidence** approval for the first frozen build (n=35). Headline checkpoint: M\*={m_trust_general, m_trust_in_group}, [L,U]=[0.371,0.624], FA=0, cold H4; diagnostics: θ-grid empties at λ≥1.5, bootstrap band [0.174,0.752] with 17.5% empty replicates. Tracked summary: `reports/summaries/h5_trust_evidence_summary.json`. This is a checkpoint, not a release: final paper lock, tag, PyPI, and push remain Augusto's." (docs/16:133)
- **What it does NOT authorize:** "any other H5/empirical run, engine change, tag, PyPI publication, push, or a `docs/13` evidence claim by implication. The provisional synthetic-only protocol and the MC50 table (§4) are unchanged." (docs/16:135)

### 2.3 Authority per AGENTS.md
- Augusto owns all main-path empirical/paper choices: construct, unit/universe, score matrix + protocol, menu, empirical R/anchors/θ/δ/β, paper claims, reporting placement, H5/public-baseline choice, **release posture, tag, and PyPI publication** (AGENTS.md:31-35).
- Agents may author oracle networks **only for synthetic DGPs**; "Do not invent an empirical network to make H5 or a paper table move" (AGENTS.md:37).
- docs/16 is "LOCKED AS PROVISIONAL SYNTHETIC-ONLY. It does not authorize empirical/H5 work, engine changes, pushes, tags, PyPI publication, or a release claim by implication" (AGENTS.md:39); n=35 is "a checkpoint, not a release" (AGENTS.md:39).
- Convention 6: "Do not push, tag, publish, rewrite history, or modify `v0.1` without a task-specific explicit user decision" (AGENTS.md:80).
- Conflict rule: "If code and current policy documentation disagree, stop and surface the conflict" (AGENTS.md:71).

### 2.4 What is NOT authorized by implication
Any empirical run beyond the designated H5 Trust evaluation; engine changes; any tag/push/PyPI; any docs/13 evidence claim from the checkpoint; empirical network authorship by agents; H5/public-baseline choice; citing spam/calhousing as paper evidence (AGENTS.md:37,39,49; docs/16:135; spam README:3; calhousing README:3).

---

## 3. EVALS INVENTORY

### 3.1 `evals/h5_trust/` — designated H5 Trust evaluation
Present (search_files): `build_dataset.py`, `verify_audit.py`, `data/{scores.csv, score_manifest.json, roles_h5_trust.json, network_h5_trust.yaml, beta_h5_trust.yaml, anchors_h5_trust.yaml}`, `runs_verify/{default,cold}/` (full artifact sets incl. `report.html`, `admissible.json`, `range.json`, `slacks.*`), `proof_summary.json`, `README.md`.
- Status: "FIRST FROZEN BUILD COMPLETE (2026-08-04) — dev gate + auditor exit 0. NOT YET A PAPER CLAIM" (h5_trust/README.md:3-4).
- **n=35 preliminary checkpoint** (AGENTS.md:39; docs/16:133; docs/13:393-421): M*={m_trust_general, m_trust_in_group}, [L,U]=[0.371,0.624] (exact 0.37075446228800285 / 0.62389053803067 in `reports/summaries/h5_trust_evidence_summary.json:61-62`), FA=0, cold H4, θ-grid empties λ≥1.5, bootstrap band [0.174,0.752], 17.5% empty replicates, package `1.1.0a1`, parent SHA `cd6455d6` (evidence_summary:9-10).
- Frozen inputs committed; universe 66 WVS → 42 with GPS/aux/floor → 35 after 7 coverage drops (evidence_summary:14-28; score_manifest.json:5-19).

### 3.2 `evals/realworld/` — intermediate, NOT H5
- **spam_validity** (20newsgroups text): "**Status:** intermediate evaluation · **NOT** main path · **NOT** paper H5" (spam README:3); FA=0, oracle M*, [L,U]=[0.1873,0.8460], harsh empty, cold H4 (docs/13:210-241); agent-authored incidental R authorized for eval only (spam README:62-63).
- **calhousing_validity** (tabular, n=20640): "**Status:** INTERMEDIATE / NOT MAIN PATH / NOT H5 / NOT A PAPER RESULT" (calhousing README:3); FA=0, [L,U]=[0.1658,0.9514], small-n admission flips, transform-choice flips admission, NaN fail-loud (calhousing README:37-77; docs/13:326-373).
- AGENTS.md:49: "Both are **intermediate / not H5** … Do not cite them as paper evidence."

### 3.3 `evals/synthetic/` — museum
`v0_poc.py` = "**Monolith** SCORE→REPORT proof. `POC_VERSION=v0_1_poc`. Museum piece." (synthetic README:7-11); AGENTS.md:27 — keep present and **unimported** from `src/`; enforced in CI (`ci.yml:52-78`) and by tests/test_import_graph.py.

---

## 4. IMPLEMENTED vs DOCUMENTED GAP INVENTORY (critical)

### 4.1 Restrictions registry (`identify/slacks.py`, `schemas/network.py`)
| Type | Implemented? | Evidence |
|---|---|---|
| `corr_min` | ✅ signed lower bound `Corr(m,V) − θ` | `slacks.py:59-64`; schema `schemas/network.py:50-52`; METHODOLOGY.md:38 |
| `corr_sign` | ✅ `sign·Corr − θ` | `slacks.py:66-75`; METHODOLOGY.md:39 |
| `mean_order` | ✅ binary 0/1 group, `sign·(mean(m\|g=1)−mean(m\|g=0)) − θ` | `slacks.py:77-100`; fixture `data/fixtures/mean_order_v1/` (docs/12 M-b1) |
| `rank_agree` | ✅ Spearman ρ vs `ref_measure`, ties averaged | `slacks.py:102-108`; fixture `rank_agree_v1` (docs/12 M-b2) |
| `stability` | ⚠️ **schema-only, fails loud** | `schemas/network.py:11-17` lists it; no evaluator → `SlackError` ("schema-only until a fixture demands it", `slacks.py:110-113`; METHODOLOGY.md:42) |
| `monotone_*` | ❌ **named gap** — "no evaluator for *monotone-in-continuous-covariate* (e.g. 'trust is increasing in income')" | METHODOLOGY.md:51; docs/12:918,924. Extension path documented: schema type + evaluator + fail-loud default (METHODOLOGY.md:51) |
| unknown types | fail loud at parse time | `schemas/network.py:11-17`; `slacks.py:110-113` |

### 4.2 Beta functional registry (`identify/beta_fn.py`, `schemas/beta.py`)
| Type | Implemented? | Evidence |
|---|---|---|
| `corr_y` | ✅ | `beta_fn.py:53-61` |
| `ols_coef` | ✅ standardized numpy closed-form, non-empty `params.controls`, no statsmodels | `beta_fn.py:62-73`, `_ols_coef` 22-44; ARCHITECTURE.md:118; docs/12 D5 |
| `diff_means` | ⚠️ schema-only fail-loud | `schemas/beta.py:9,15-16`; `beta_fn.py:74-77`; audit file:58-59 |

### 4.3 Inference diagnostics — implemented, all additive
- **bootstrap** (`inference/bootstrap.py`): units-only, menu fixed, seeded `default_rng`, pointwise percentile over non-empty replicates, degenerate counted, headline unchanged (bootstrap.py:1-18, 59-147). Locked semantics docs/12 (2026-08-01 M6 entry); docs/16 §2:43-44.
- **theta_grid** (`inference/theta_grid.py`): λ scales θ magnitudes only; λ=1.0 headline; never auto-selected; excluded from preimage (theta_grid.py:1-21, 98-112). docs/16 §2:45-46.
- **delta_grid** (`inference/delta_grid.py`): absolute δ, IDENTIFY-side `delta_override` (never touches network/beta hash), excluded from preimage (delta_grid.py:1-19, 96-118).
- **θ-anchor audit** (`anchors/pipeline.py`): schema'd anchors.yaml, completeness enforced, `anchors_hash` **excluded from the freeze preimage** ("documentation provenance, not engine inputs", anchors/pipeline.py:1-9, 120-126).
- **Freeze/hash contract** (`freeze.py`): canonical JSON/CSV hashing; run_id preimage keys = `beta_hash, config, delta, n_boot, network_hash, package_version, schema_version, scores_hash, seed` (freeze.py:17-20, 184-207); `n_boot` normalized `<1 ⇒ null` for v1.0 bit-stability (freeze.py:172-181); excluded: `created_at`, paths, hostnames, grids, anchors (freeze.py:22-23; pipeline.py:10-17). **`package_version` is inside run_id** (docs/12 M1 entry) — version bumps change run_id.
- All four layers off unless requested; stale artifacts cleaned (pipeline.py:150-159).

### 4.4 Documented-but-missing (paper-relevant)
- **Coupled admissibility↔β inference layer** — **not found** (search for `coupled`, `holdout`, `R_holdout`, `R_select` across the repo: 0 hits). Bootstrap/θ-grid/δ-grid re-run IDENTIFY per replicate/grid point (bootstrap.py:102, theta_grid.py:134, delta_grid.py:115) but there is no layer that propagates *admissibility classification uncertainty* into a joint/confidence statement about β; headline remains deterministic min/max B* (docs/16:32; AGENTS.md:22).
- **Holdout-restriction workflow (R_select vs R_holdout / pre-registered holdout restrictions)** — **not found**. docs/16:33-35 locks "rejected measures never enter the headline range" and empty-set honesty; nothing implements splitting restrictions into selection vs holdout evaluation.
- **Deep-trust-study evaluators** — cross-country invariance, demographic gradients, discriminant restrictions: **not found**. Registry tops out at the 4 implemented types + named `monotone_*` gap (METHODOLOGY.md:51) — a "trust increasing in income" demographic-gradient restriction would currently have to be binned into `mean_order` or approximated by `corr_sign` (METHODOLOGY.md:51).
- **docs/16 §2 "Paper interpretation of inference"** — still **AWAITING AUGUSTO** ("Decide whether bootstrap output is appendix-only diagnostics, a conservative uncertainty summary, or another explicitly bounded interpretation", docs/16:47).
- docs/16 §3 researcher-owned inputs: construct, unit/universe, score matrix, menu, R, θ, δ, β, claims — all **AWAITING AUGUSTO** except the H5-design-locked set (docs/16:55-63).

### 4.5 Code-but-undocumented / doc tensions (surfaced per AGENTS.md:71)
1. **docs/17 §3 vs frozen manifest (real conflict).** `docs/17_H5_Trust_Design.md:40` still says the `rule_of_law` aux comes from "WGI `rq`", but the frozen manifest records "World Bank WGI rule_of_law (**rl**)" (`evals/h5_trust/data/score_manifest.json:35`), docs/12 line 646-648 records the rq→rl transcription fix ("`rq` is Regulatory Quality. Corrected to `rl`"), and docs/17 itself §10 line 101 says "WGI (World Bank) `rl`". §3 was not updated; internal doc inconsistency + doc-vs-artifact mismatch.
2. **docs/16 package baseline is stale.** docs/16:5 says "**Package baseline:** `cvprofiles==1.1.0a1`" — the freeze predates v2.0.0 (PyPI 2026-08-06) and the current dev `2.0.1a1`. Since `package_version` is in the run_id preimage (freeze.py:202; docs/12 M1), any paper run under a newer version gets a different run_id than the n=35 checkpoint run; the protocol doc has not been re-baselined.
3. **n≈40 vs n=35.** docs/17:23 "Expected n ≈ 40 (exact overlap verified at scaffold time)" vs frozen n=35 (evidence_summary:40; docs/13:397 — 7 countries dropped for missing Gini/GDP coverage). Explained in docs/13; manifest carries the counts. Minor drift, not a defect.
4. **`mean_order` default sign.** Schema defaults `params.sign=1` (schemas/network.py:60-62) — documented only in the decision log (docs/12 D3), not in METHODOLOGY.md's registry table (METHODOLOGY.md:40 shows the formula with sign but no default note). Minor.
5. **anchors `pre_data` is a process commitment the engine cannot verify** — explicitly documented as such (anchors/pipeline.py:38-44; docs/12 D4). Not a gap, but paper reviewers may want the timing claim backed by git/file metadata.

---

## 5. PAPER-READINESS ASSESSMENT (grounded)

### 5.1 What exists the paper can use today
- **H5 Trust n=35 preliminary paper-facing evidence** (owner-approved checkpoint): M*={m_trust_general, m_trust_in_group}, [L,U]=[0.371,0.624], FA=0, cold H4, θ-grid empties λ≥1.5, bootstrap band [0.174,0.752] with 17.5% empty replicates — `reports/summaries/h5_trust_evidence_summary.json` (lines 41-135), docs/16:133, docs/13:393-421.
- **θ anchors (pre-data, literature-grounded)** — auditable artifact `evals/h5_trust/data/anchors_h5_trust.yaml` (docs/17 §6:66-74); completeness machine-checked (anchors/pipeline.py:97-117).
- **Audit trail**: `evals/h5_trust/verify_audit.py`, independent read-only verifier `tools/verify_h5_trust.py` (docs/17 §11:108-113), `proof_summary.json`, freeze hashes + cold double-run (H4) discipline (freeze.py; docs/16:35).
- **Freeze/run-id contract** with provenance fields (parent SHA, package version, seed list) — docs/16 Provenance rule (139); `tools/verify_v11_protocol_synth_mc50.py` as the audit pattern.
- **Provisional synthetic MC50 protocol table** (seeds 0..49, 200 scenario-seed cells, all gates green) — `reports/summaries/v1_1_protocol_synth_mc50_summary.json`; docs/13:278-313. Synthetic-only, not H5.
- **Two tutorials executed against the published PyPI wheel** (synthetic walkthrough + H5 replication; diagnostics tour) — docs/12:816-818, 858; README.md:104-105.

### 5.2 What the paper needs that does NOT exist yet
1. **Coupled admissibility + β inference layer** (the coupling between which measures enter M* and the estimate/range of β). **Not found** (0 hits for coupled/holdout/R_select/R_holdout). Current diagnostics condition on admission per replicate but no object quantifies the joint uncertainty.
2. **Pre-registered holdout-restriction workflow** — an R_select/R_holdout split with the holdout set untouched until the deep-trust evaluation runs. **Not found.** Would also need a lock in docs/16 (amendment path) because it changes what "the stated network" means for the headline run.
3. **Evaluators for the deep trust study**: cross-country invariance (e.g. mean_order by region with sign, or a new invariance evaluator), demographic gradients (needs `monotone_*`, the named gap, METHODOLOGY.md:51), discriminant restrictions (e.g. institution measure must NOT track rule_of_law — currently only expressible as a negative `corr_sign` with sign=−1, which exists). Registry growth follows the locked pattern: fixture + semantics lock + schema type + evaluator + fail-loud (METHODOLOGY.md:51; docs/12 D3-D5; docs/12:726).
4. **docs/16 amendment for any change to the headline range or freeze preimage.** docs/16:21: post-lock changes require a dated amendment. **Governance flag:** if a coupled-inference confidence region becomes the *headline* [L,U] (rather than additive), that collides with the locked method spine (docs/16 §1:32: "headline range is [min B*, max B*]"; AGENTS.md:22) and with the freeze-preimage contract (AGENTS.md:24: bootstrap/θ-grid excluded from preimage; diagnostics never replace the headline). That change is **Augusto's decision** (AGENTS.md:31-35) and would need: a dated docs/12 entry + docs/16 amendment (possibly a new §8-style amendment), a METHODOLOGY.md inference-stance update, and a freeze-contract change (freeze.py preimage keys, ARCHITECTURE.md:113) with a version-discipline consequence (package_version is in run_id — freeze.py:202).
5. **Re-baselining docs/16 to the shipped version** before new evidence runs (see §4.5.2).

---

## 6. RELEASE POSTURE for v3.0.0

### 6.1 Current release gates (as documented)
- **ROADMAP.md** — no v3 gates exist yet; next-sprint scope box "to be drafted after the v2.0 release" (ROADMAP.md:32). Change log only through 2026-08-06 (ROADMAP.md:36-38).
- **docs/archive/15_MVP_Release_Checklist.md** — archived v1.1-candidate checklist; "must be green before promotion" items: CI green (py3.11+3.12), ruff/mypy/pytest (130→157 passed at recapture), version smoke, golden freeze match, synth battery gates, bootstrap/θ-grid policies honored, v0.1 peel intact, museum unimported/no-LLM, docs/12+13 updated (15_MVP_Release_Checklist.md:16-28). PyPI = "**Augusto only**" (line 36). No v3.0.0 checklist exists.
- **docs/16 §6** — "Tag and PyPI publication | **DEFERRED** | Release-review and Augusto-owned; this protocol draft does not publish" (docs/16:102).
- **AGENTS.md** — authority: Augusto owns "release posture, tag, and PyPI publication" (AGENTS.md:35); convention 6: no push/tag/publish without a task-specific explicit user decision (AGENTS.md:80). Precedents: v1.1.0 tagged on Augusto's explicit "let's tag this baby" (docs/12:706-717); 2.0.0 PyPI published on dated explicit authorization (docs/12:795-800), with Augusto running `uv publish` himself (token never in agent session, docs/12:813-815).

### 6.2 Candidate gate criteria for v3.0.0 (grounded in project conventions)
1. **Coupled inference layer implemented + tested** (TDD: RED→GREEN, AGENTS.md:76) — with an explicit semantics lock (docs/12 dated entry, mirroring D3-D5/D1 pattern, docs/12:725-728) and a decision on whether it stays additive (preimage-excluded like bootstrap/θ-grid, AGENTS.md:24) or redefines the headline (→ governance flag in §5.2.4).
2. **Deep trust study with holdout protocol** — R_select/R_holdout workflow, pre-registered holdout restrictions, n≥35 re-run or expansion; requires Augusto's run decision + dated docs/16 amendment (docs/16:21, 125-135 pattern); new evaluators (monotone_*, invariance/discriminant) via fixture + semantics lock.
3. **Battery green**: ruff, mypy strict, pytest (last logged 222), both proof verifiers exit 0 (`tools/verify_h5_trust.py`, `tools/verify_v11_protocol_synth_mc50.py`), `git diff --check`, `v0.1` peel intact (AGENTS.md:93-99).
4. **Docs updated**: METHODOLOGY (inference stance if headline changes), ARCHITECTURE (module map for any new inference/evaluator modules), ROADMAP, PROJECT_MANIFEST (dev_version/target_version), docs/12 dated entries, docs/13 evidence rows (only for audited, authorized evidence), docs/16 amendment (required for any paper-facing change).
5. **Version discipline**: atomic bump `2.0.1a1 → 3.0.0` with golden refresh and all version literals (pyproject, `__init__`, uv.lock, tests, CI, README) — precedent docs/12:422, 807-809; `tools/refresh_mini_golden.py` exists.
6. **Augusto's explicit release decision** (AGENTS.md:35, 80; docs/16:102): tag + PyPI authorization with Augusto executing the upload (precedent docs/12:813-815).

---

## Appendix A — Files read (grounding set)
AGENTS.md; README.md; pyproject.toml; .github/workflows/ci.yml; docs/{METHODOLOGY, ARCHITECTURE, ROADMAP, PROJECT_MANIFEST, 12, 13, 16, 17, USER_GUIDE(partial)}; docs/archive/{15_MVP_Release_Checklist, 18_Measure_Discipline_Plan(partial)}; audits/2026-08-06_post_release_audit.md; src/cvprofiles/{__init__, cli, pipeline, freeze}.py; src/cvprofiles/{identify/{slacks,beta_fn,pipeline}, inference/{bootstrap,theta_grid,delta_grid}, anchors/pipeline, schemas/{network,beta}, report/pipeline}.py; evals/{h5_trust/README, h5_trust/data/score_manifest.json, realworld/{spam_validity,calhousing_validity}/README.md, synthetic/README.md}; reports/summaries/h5_trust_evidence_summary.json; tests/ (file inventory + test-function count).
