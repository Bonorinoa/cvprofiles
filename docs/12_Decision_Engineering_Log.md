# Decision and Engineering Log

This is a **live** document. Update whenever project direction, implementation details, or important lessons change. Do not rewrite history — reverse a decision with a new dated entry.

Coding agents: read this before inventing architecture.

---

## 2026-08-01 — Project graduated / scaffold v0

**Decision:**
- Create active project `cvprofiles` at `~/Hermes/Projects/cvprofiles`.
- Hermes desktop Project workspace anchored to that path.
- Day-0 deliverable = **methods-first knowledge base** (not engine code, not GitHub remote).
- Document suite is a **lean research-tool** set (01–13 + manifest), not the Phronesis voice-app suite. Intentionally **no** `15_Design_Spec`, RAG, system-prompt, or agent-tool-spec docs at v0 — visual product design is out of scope for the methods package MVP.

**Rationale:**
- Thesis spine already locked in profile `SOUL.md`; project docs must make it operable for cross-agent work.
- User requested scaffold + software strategy + methodological decisions + prereg **before** GitHub.
- Empty admissible sets / wide ranges as features require report + eval discipline from day one → dual live logs.

---

## 2026-08-01 — Spine locks (from SOUL / thesis; project-confirmed in scaffold)

**Decision (LOCKED):**
- Four states: SCORE → RESTRICT → IDENTIFY → REPORT.
- Thesis core = states 1–3; SCORE is ingest/schema only.
- Engine is **score-agnostic and model-free**; no LLM inside the engine.
- Finite researcher-supplied menu \(M\); no prompt-space search in engine.
- Construct validity = partial ID over measurement menu under researcher nomological network \(R,\theta\).
- Closest ancestor: Leamer → measurement functions; formal home: partial identification.
- Network \(R\) answers validity-of-\(C\); \(\beta\) answers downstream conclusion — **not hard-coded as derivatives of each other**.
- **USER OWNS** construct definition, every nomological restriction and \(\theta\) anchor, go/no-go, paper narrative (main path).
- Agent may author **oracle-compatible networks for synthetic DGPs only**; must not silently author main-path empirical networks.
- H5 (real baseline) is a **template only** until Augusto fills it; agent authorship of H5 main-path network is rejected.
- Synthetic DGP suite + four debug metrics **before** real baselines.
- Paper numbers only from frozen scores + pinned network + fixed seed + package version.
- Progress read from on-disk artifacts + these logs, not git archaeology alone.
- Hard non-goals remain (foundation training, annotation campaigns as main path, SAE/hypothesis-gen core, PPI/MARS co-equal, SCA/ABM spine, proprietary API dependence for paper path, “automate all empirical economics”).

**Rationale:** Durable thesis identity; prevents scope collapse into scorer product or pure OVB tooling.

---

## 2026-08-01 — Provisional engineering defaults (DRAFT until Augusto confirms)

**Decision (PROPOSED — not frozen at time of writing; superseded by next entry):**

See following entry for confirmed locks. Original proposal table left as historical draft context only.

---

## 2026-08-01 — User confirmations + agent-judgement defaults + PoC-before-git

**Decision (LOCKED by user / agent judgement as noted):**

User confirmed:
- **Stack** as proposed (Python ≥3.11, uv, pydantic v2, pandas/pyarrow, NumPy/SciPy/statsmodels, Typer, Jinja2, pytest/ruff/mypy).
- **License:** MIT.
- **Package name:** `cvprofiles`.
- **Baseline criterion:** boring, heavily documented public association study (dataset still unchosen; H5 network still USER-OWNED template).

Agent-judgement defaults (user: “sensible defaults, use your judgement”):
- Slack sign: \(s_r(m)\ge 0\) satisfied; default \(\delta=0\); always also report a small \(\delta\)-grid as sensitivity, not headline.
- First \(\beta\): `corr_y` primary; `ols_coef` secondary check in PoC.
- Bootstrap (when implemented at M6): over **units** only; menu fixed; `numpy.random.Generator`; \(B=999\); percentile on \((L,U)\); conservative tone; sharp PI optional garnish.
- Prereg bars (working): \(c_{\min}=0.90\), \(f_{\max}=0.05\) at \(\delta=0\) — freeze later with eval evidence.
- MVP restriction registry start: `corr_sign`, `corr_min`, `mean_order`, `rank_agree`, `stability` (PoC uses a subset).
- Paraphrase measure label default: **`valid`** (Q9 closed unless reopened); H2 false-admission does not count paraphrase as invalid.
- First vertical slice for package path remains M4–M5 core; **bootstrap not required in v0 PoC**.

Process locks:
- **No `git init` / no GitHub** until a working synthetic PoC exists and has been exercised.
- PoC form: **one monolith script** (not package layout). Keep as historical evidence under `evals/synthetic/` when packaging later — do not delete.
- `AGENTS.md` still deferred.
- H5 content still blank.

**Rationale:**
- User wants proof-of-concept synthetic evals before version control so the first commit is not empty docs theater.
- Monolith is intentional throwaway inspiration, not the future module boundaries.
- Parameter micromanagement deferred to agent defaults to keep momentum; logs preserve the choices.

**Still open:** real baseline dataset (Q12); H5 network content; run_id hash algorithm (M1); restriction registry extension mechanism; PyPI name clash check before publish.

---

## 2026-08-01 — Dual-log convention

**Decision:**
- `12_Decision_Engineering_Log.md` = engineering + scope locks.
- `13_Evaluations_Log.md` = synthetic/real eval runs and metric learnings.
- Both live from day 0; append-only narrative (machine summaries may sit beside them later under `reports/`).

**Rationale:** User requirement for cross-agent context; weekly progress from artifacts + logs.

---

## 2026-08-01 — GitHub / git timing

**Decision:**
- **No git remote** and no assumption of GitHub until Augusto confirms post-scaffold checkpoint.
- Local `git init` optional at confirmation time.
- `AGENTS.md` deferred until coding-agent handoff (after M0 confirm; typically with/after M1).

**Rationale:** User asked to be better informed before repo setup; docs-first.

---

## 2026-08-01 — v0_poc executed; PoC gate met with caveats

**Decision:**
- First synthetic battery ran successfully via `evals/synthetic/v0_poc.py` + project `.venv` (Python 3.11, numpy, pandas).
- Artifacts: `reports/runs/v0_poc_*.json`, summary JSON; narrative in `13_Evaluations_Log.md`.
- **PoC gate (mechanical):** SCORE→RESTRICT→IDENTIFY→REPORT path works; FA=0 on invalids; empty \(M^*\) handled; user condition “code for synthetic evals before git” is satisfied **mechanically**.
- **PoC gate (scientific honesty):** not clean enough to freeze H1–H4 or declare synthetic evals “done.” Three DGP/harness bugs + coverage-metric attenuation issue logged (see eval log).
- **Git:** still **no remote**. Local `git init` is now *eligible* per user rule, but deferred one beat so Augusto can choose: init on v0 as historical snapshot vs wait for v0.1 bugfixes. Agent will not init until user picks.
- **No silent θ-loosening** to manufacture coverage.

**Rationale:** Empty docs theater avoided; also avoid celebrating a misleading coverage=0 or a misnamed `all_invalid`.

---

## 2026-08-01 — H1 coverage vs attenuation (open methodology)

**Decision (OPEN at time of writing — superseded by next entry):**
See following entry. Original A/B/C/D menu preserved as historical context only.

Under \(\beta=\mathrm{corr}_y\), oracle \(\beta^*=\mathrm{Corr}(V^*,y)\) systematically exceeds \(\mathrm{Corr}(m,y)\) for noisy admissible \(m\) (classical attenuation / EIV).

---

## 2026-08-01 — Q22/Q23/Q24 closed; v0.1 PoC hygiene before git

**Decision (LOCKED):**

**Q22 — H1 metrics (hybrid A+B; reject C for reported range):**
- **H1a** (gate): false-admission of `invalid_*`/`wrong_construct` + anchor (`m_dict`) retained in \(M^*\) under oracle \(R\).
- **H1b** (gate / construction invariant): when anchor \(\in M^*\), \(\beta(m_{\mathrm{anchor}})\in[L,U]\) because \([L,U]=\min/\max B^*\). Primary scientific bite is H1a + H3 + H4, not celebrating H1b=1.0.
- **H1_latent** (diagnostic only): fraction of seeds with \(\mathrm{Corr}(V^*,y)\in[L,U]\). Expected low under attenuation. Never a CI/package gate.
- **Reject C:** no attenuation band painted onto reported \([L,U]\).
- **Reject** silent \(\theta\)-loosening or swapping latent target into the scientific range.

**Q23 — near_miss under oracle \(R\):**
- Near-misses (`m_near`, `m_floor`) must **fail ≥1 restriction by DGP design** under standard oracle \(R\).
- Do not relabel to `valid` to clear the metric.
- Near-miss admission is logged separately; not FA.

**Q24 — process:**
- v0.1 monolith hygiene **before** M1 package layout and **before** local `git init`.
- Local git init **only if** v0.1 battery exits 0 / gates green. Still **no remote**.

**PoC gates (v0.1 exit criteria):**
| Scenario | Must hold |
|---|---|
| `oracle_easy`, `oracle_with_slop` | FA=0; anchor in \(M^*\) all seeds; H1b=1 when nonempty; near_miss not all admitted |
| `harsh_theta`, `all_invalid` | empty_set_rate=1.0; FA=0 |
| all | cold determinism True; H1_latent reported but not gated |

**Rationale:** Load-bearing claim is admissible set + image of \(\beta\), not recovery of latent Corr(V*,y). Reliable PoC is user-stated prerequisite for repo.

---

## 2026-08-01 — v0.1 PoC gates GREEN; local git init authorized

**Decision:**
- `evals/synthetic/v0_poc.py` (`v0_1_poc`) exit code **0**; all programmed gates passed.
- Proof summary: `reports/summaries/v0_1_poc_summary.json` (committed); per-seed JSON under `reports/runs/` stays local/ignored.
- **Local `git init` + first commit authorized.** Still **no GitHub remote**, no push, no `AGENTS.md`, no M1 package layout until Augusto asks.
- Monolith remains museum evidence; never import into `src/`.
- H1b=1.0 recorded as construction invariant, not oversold.

**Gate snapshot (5 seeds):**
| Scenario | empty | FA | anchor_in | H1b | H1_latent | cold | slop \(\bar\beta\) |
|---|---:|---:|---:|---:|---:|---|---:|
| oracle_easy | 0 | 0 | 1 | 1 | 0 | yes | 0.481 |
| oracle_with_slop | 0 | 0 | 1 | 1 | 0 | yes | 0.547 |
| harsh_theta | 1 | 0 | 0 | n/a | n/a | yes | — |
| all_invalid | 1 | 0 | 0 | n/a | n/a | yes | — |

**Rationale:** User required a reliable synthetic PoC before initiating a repo. Mechanical + honest-metric gates are now green.

---

## 2026-08-01 — Public GitHub repo authorized as v0.1 symbolization

**Decision:**
- User requested: create **public** `Bonorinoa/cvprofiles` and initialize with documentation + green PoC script; this **symbolizes v0.1**.
- Contents of v0.1: methods KB (`docs/01`–`13`), dual live logs, MIT license, museum monolith `evals/synthetic/v0_poc.py` (`v0_1_poc`), proof summary `reports/summaries/v0_1_poc_summary.json`.
- **Not** in v0.1: `src/cvprofiles` package, bootstrap/θ-grid, `AGENTS.md`, H5/real baseline, PyPI publish.
- Tag intent: annotated `v0.1` on the release commit after remote exists.
- Monolith stays under `evals/synthetic/` forever as historical evidence — never import into `src/`.
- Supersedes prior “no remote until requested” note: remote is now explicitly requested.

**Rationale:** PoC gate was the prerequisite; user now wants the public artifact.

---

## 2026-08-01 — Researcher input guide (composites, anchors, postures)

**Decision:**
- Add `docs/14_Researcher_Input_Guide.md` as the human-facing prep guide for SCORE/RESTRICT inputs.
- **Guidelines (DRAFT, process — not a main-path network):**
  - Scoring/composites stay **upstream**; engine remains score-agnostic.
  - **Split by default** across objects, response technologies, and instrument families; composite only inside a coherent facet (opposite-movement test).
  - Distinguish anchor roles: **P1 criterion**, **P2 peer**, **synthetic eval anchor**, optional **rank-ref**.
  - Recommended empirical sequence when a system was trained to a standard (e.g. LLM→GPS): **criterion recovery first**, peer/external network second.
  - Common unit required; no row-merge of distinct survey microdata; join at moments when needed.
  - One construct per run; small \(J\); freeze recipes in `scoring_notes.md` beside runs.
- Indexed from root README, `docs/README.md`, `PROJECT_MANIFEST.md`; glossary terms added.
- Does **not** author SCA2/H5 empirical \(R\); SCA-style worked pattern is illustrative posture only.
- Lands on **`main` after tag `v0.1`** — does **not** move the freeze.

**Rationale:** User correctly noted scoring is a non-trivial researcher decision; docs needed durable guidelines (when to break composites, what to anchor on) without collapsing USER-owned theory into package defaults.

---

## 2026-08-01 — Public remote, tag v0.1, and GitHub Release LIVE

**Decision:**
- Public repo: https://github.com/Bonorinoa/cvprofiles
- `origin` → `https://github.com/Bonorinoa/cvprofiles.git`
- Annotated tag **`v0.1`** frozen on commit **`fb62b48`** (methods KB + green museum PoC only)
- GitHub Release: https://github.com/Bonorinoa/cvprofiles/releases/tag/v0.1
- **v0.1 contents:** docs 01–13, dual live logs, MIT, `evals/synthetic/v0_poc.py` (`v0_1_poc`), `reports/summaries/v0_1_poc_summary.json`
- **v0.1 non-contents:** no `src/cvprofiles`, no bootstrap/θ-grid, no H5/real baseline, no PyPI, no `AGENTS.md`
- Doc-14 cluster is a **post-v0.1** commit on `main` only — **tag not moved**, not part of the freeze symbolization
- `main` may advance past `v0.1`; the tag remains the v0.1.0 symbolization point

**Rationale:** User asked to create the public repo and symbolize v0.1 with documentation + PoC. Prerequisite green PoC was met; remote/tag/release complete the request.

---

## 2026-08-01 — v1.0 open sprint: thin first-principles spine; bootstrap deferred

**Decision (LOCKED this sprint):**

- **v1.0 goal:** validate core first principles of the system we ship — not full MVP in historical `09` backlog, not paper-complete, not fully tested polish.
- **In v1.0:** installable thin package `src/cvprofiles` + CLI; SCORE → RESTRICT → IDENTIFY → thin REPORT (HTML/JSON); finite menu; sample slacks → \(M^*\) → \([L,U]=\min/\max B^*\); freeze hash + bit-stable rerun; synthetic harness re-implemented under package/tests (H1a / H2 / H3 / H4); empty \(M^*\) clean success; no LLM in engine or installable import graph.
- **Out of v1.0:** **M6 bootstrap / θ-grid → v1.1**; M10 / H5 / real baseline / USER empirical network content; sharp PI; prompt search / measure generation; GUI/SaaS; importing museum monolith into `src/`; moving tag `v0.1`; “fully tested MVP” polish.
- **Build order (strict):** M1 → M2 → M3 → M4 → M5 → M7(thin) → M8 → M9. **No M6. No M10 this sprint.**
- **Gate path:** G1 → G2 → G3 → G4 → G5 → G7-thin → G8-mini → package install/CI. G7/G8 re-enter from G5 (not G6) for this sprint. G6 deferred to v1.1.
- **Hypothesis wording (unchanged):** H1a / H1b gates; H1_latent diagnostic only (attenuation). See `03`, `05`.
- **Tag `v0.1` @ `fb62b48`:** immovable. Methods KB + museum PoC only. Do not move, delete, or retag.
- **Museum:** `evals/synthetic/v0_poc.py` stays present and **unimported**. Package path must earn its own gates; museum was directional only.
- **Authority split unchanged:** USER owns construct / every \(R,\theta\) / go-no-go / paper narrative. Agent may author oracle networks for synthetic DGPs only. Doc-14 remains DRAFT process guidance — not package defaults that author constructs.
- **Sibling chat:** version-control evaluation / release review owns tag/release candidates. This sprint implements; propose `v1.0.0` only when acceptance list green and Augusto asks; do not tag from this chat by default.
- **Phase 0 (this entry’s commit):** docs hygiene only — past-tense public repo + tag live; v1.0 scope box in `09` + manifest; G6/bootstrap wording deferred; H1a/H1b/H1_latent pointers. No methodology expansion; no hard non-goal reopening.

**Rationale:** User opened v1.0 as a thin spine sprint with bootstrap explicitly deferred. Prevents full-MVP scope collapse and keeps first-principles validation observable.

**Follow-ups:** M1 schemas + freeze hash + mini fixture + contract tests; lock run_id hash algorithm in a subsequent M1 decision-log entry.

---

## 2026-08-01 — M1 G1: schemas + freeze hash + mini_v1 (LOCKED)

**Decision (LOCKED):**

### Package / G1 exit
- Installable package path begun: `src/cvprofiles` + `pyproject.toml` (hatchling src-layout) + thin Typer CLI (`cvprofiles --version`).
- Version pin for development: **`1.0.0a1`** (not a `v1.0.0` tag).
- Pydantic v2 schemas: `ScoreColumnRoles`, `ScoreManifest`, `RestrictionSpec`, `NetworkConfig`, `BetaSpec`, `FreezeBundle`, `RunManifest`.
- Restriction **type registry at schema level** (v1.0 ids): `corr_sign`, `corr_min`, `mean_order`, `rank_agree`, `stability`. Unknown types fail loud. **Evaluators remain M4** — schema-only here.
- Mini fixture: `data/fixtures/mini_v1/` (hand scores, roles, network, beta, golden `expected_freeze.json`).
- Contract tests green (schemas + freeze + import-graph hygiene + mini load). Museum `evals/synthetic/v0_poc.py` present and **unimported**. No LLM client in package import graph.
- **G1 exit met.** SCORE/IDENTIFY/REPORT logic not started (M2+).

### Freeze / run_id algorithm (LOCKED — implementation: `cvprofiles.freeze`)
1. Piece hashes are bare lowercase SHA-256 hex (64 chars); no `sha256:` prefix.
2. Canonical JSON: UTF-8, `sort_keys=True`, separators `(",", ":")`, `allow_nan=False`.
3. `network_hash` / `beta_hash`: SHA-256 of canonical JSON of `model_dump(mode="json")` for validated `NetworkConfig` / `BetaSpec`.
4. `scores_hash`: SHA-256 of canonical CSV bytes of the score table:
   - columns in caller-declared order;
   - rows sorted by `unit_id` ascending (string sort, stable mergesort);
   - header = comma-joined column names;
   - floats with 17 significant digits (`format(x, ".17g")`); ints plain; bool `0`/`1`;
   - **NaN/Inf fail loud** (never coerced to empty);
   - other missing → empty field; UTF-8; trailing newline after last row.
5. **Default freeze columns:** `unit_id + measures + aux + outcome`. **Diagnostics** (e.g. `V_star`) are **out** of `scores_hash` unless the caller intentionally versions them.
6. `run_id` = SHA-256 of canonical JSON preimage with keys:
   `beta_hash`, `config`, `delta`, `n_boot`, `network_hash`, `package_version`, `schema_version`, `scores_hash`, `seed`.
   - v1.0: `n_boot` is JSON `null`.
   - **`package_version` is inside `run_id`** — version bumps change `run_id` and require refreshing `data/fixtures/mini_v1/expected_freeze.json` in the same change.
7. **Excluded from run_id preimage:** `created_at`, wall clock, absolute paths, hostnames, artifact path maps, report HTML.

**Rationale:** Bit-stable freezes are load-bearing for H4 and paper discipline. Locking the algorithm at M1 prevents silent hash drift when SCORE/IDENTIFY land.

**G1 proof:** `uv run pytest` green; golden hashes under `data/fixtures/mini_v1/expected_freeze.json`; tag `v0.1` still `@ fb62b48`.

**Follow-ups:** M2 SCORE only (ingest → `S_frozen` + manifest). Do not start IDENTIFY until SCORE contracts pass.

---

## 2026-08-01 — M2 SCORE normalization policy (LOCKED)

**Decision (LOCKED before SCORE code):**

1. **Default policy: `none`.** Frozen user matrices are trusted as supplied. SCORE validates and freezes; it does **not** silently rescale.
2. **Optional opt-in:** `zscore_measures=True` z-scores **measure columns only** (ddof=0, sample std). Aux, outcome, diagnostics, unit_id are never z-scored by this flag.
3. **mini_v1** uses `policy: none` so locked `scores_hash` / `expected_freeze.json` stay bit-stable under `1.0.0a1`.
4. **Fail loud** (no partial freeze): missing role columns; empty frame; duplicate `unit_id`; non-finite values on freeze columns (unit_id + measures + aux + outcome). Diagnostics may be non-finite without blocking freeze of engine columns.
5. **Freeze column order:** `unit_id`, then `roles.measures`, then `roles.aux`, then `outcome` if set. Diagnostics out of default `scores_hash`.
6. **Museum PoC z-scoring** was a DGP convenience, not the package default. Package path does not import museum.

**Rationale:** User owns upstream scaling. Silent z-score would move paper hashes and hide researcher choices.

**Follow-ups:** implement SCORE library + tests; then M3.

---

## 2026-08-01 — M3 G3 RESTRICT (LOCKED)

**Decision:**
- `cvprofiles.restrict`: load network/beta YAML → validate → bind columns against SCORE roles → `network_hash` / `beta_hash`.
- Invalid schema/YAML/missing columns raise **`RestrictError`** (never raw pydantic at IO boundary).
- No slacks at RESTRICT. No construct authorship; doc-14 remains process guidance only.
- mini_v1 golden `network_hash` / `beta_hash` match `expected_freeze.json`.

**G3 proof:** `tests/test_restrict.py` green.

**Follow-ups:** M4 slacks + \(M^*\); M5 \(\beta\) + min/max range.

---

## 2026-08-01 — M4/M5 G4/G5 IDENTIFY (LOCKED)

**Decision:**
- Evaluators in v1.0 thin spine: **`corr_min`**, **`corr_sign`** only. Other schema types fail loud until a fixture demands them.
- \(s_r \ge -\delta\); \(\delta=0\) default. Full slack matrix + `rejected` reasons.
- \(M^*\) from survivors; empty \(M^*\) is **success** (not exception).
- \(\beta\): **`corr_y` only**. \([L,U]=\min/\max B^*\) on survivors; non-survivors still get \(\beta(m)\) marked rejected.
- Never loosen \(\theta\); never include rejected \(\beta\) in range; no bootstrap (v1.1).
- Harsh fixture: `data/fixtures/mini_v1/network_harsh.yaml` with `corr_min` \(\theta=0.999\) (above max sample corr on mini) → true empty \(M^*\).

**G4/G5 proof:** `tests/test_identify.py` — FA=0 on `m_slop`; empty harsh; cold double-run; range is image of \(B^*\) only.

**Follow-ups:** M7 thin REPORT + `run` composition. No M6.

---

## 2026-08-01 — M7 G7 thin REPORT + full run composition (LOCKED)

**Decision:**
- Thin REPORT: `report.html` (Jinja2 one-page audit) + `report.json` (machine-complete). No TeX this sprint. No bootstrap/θ panels (footer notes v1.1).
- Full composition: `cvprofiles.pipeline.run_profile` = SCORE → RESTRICT → IDENTIFY → REPORT into one run directory under `reports/runs/<run_id>/` (or `--out`).
- CLI: `cvprofiles run --scores --roles --network --beta [--out] [--policy] [--seed] [--title]`.
  - **stdout = pure JSON summary** (machine-parseable).
  - Human status crumbs → **stderr only**.
- Empty \(M^*\) is exit code **0**; HTML shows first-class “Empty admissible set — success, not a crash” callout; never auto-loosen \(\theta\).
- G7 enters from **G5** (not G6) for v1.0 thin spine. Bootstrap remains v1.1.
- Jinja template packaged via hatch `force-include` of `report/templates/`.
- mini_v1 e2e: oracle \(M^*=\{m\_good,m\_weak\}\), FA=0 on `m_slop`; harsh empty clean; cold double-run same `run_id` / \(M^*\) / \([L,U]\); golden freeze hashes unchanged under `1.0.0a1`.

**G7 proof:** `tests/test_report.py` + `tests/test_pipeline_e2e.py`; full suite green; live demos under `reports/runs/demo_mini_v1_*` (gitignored).

**Follow-ups:** M8 package synth harness re-impl (H1a/H2/H3/H4); M9 minimal CI. **No M6 this sprint.** Do not tag `v1.0.0` from this chat.

---

## 2026-08-01 — M8 package synth harness (LOCKED)

**Decision:**
- Re-implement synthetic DGP + oracle \(R\) + metrics + battery under `src/cvprofiles/synth/`.
- **Museum** `evals/synthetic/v0_poc.py` remains historical only — **never import**.
- Battery drives the **real package path**: `run_score` → `run_restrict` → `run_identify` (not a parallel identify).
- Scenarios (v1.0 mini battery): `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`.
- Seeds: `0..4`; \(n=1000\); \(\delta=0\); \(\beta=\mathrm{corr}_y\); SCORE policy `none` (DGP emits analysis-ready columns; optional internal centering is DGP-side only if needed).
- Oracle \(R\) (eval-only, agent-OK): `corr_min(v_aux)` + `corr_sign(v_aux,+)` — uses existing evaluators only. Harsh raises `corr_min` \(\theta\). No bootstrap/θ-grid (M6 = v1.1).
- Gates:
  - **H1a:** FA of labels in `{invalid_confounded, invalid_noise, wrong_construct}` = 0 on oracle scenarios; anchor `m_dict` ∈ \(M^*\) on all oracle seeds.
  - **H1b:** \(\beta(m_{\mathrm{dict}})\in[L,U]\) when nonempty (construction invariant).
  - **H1_latent:** \(\mathrm{Corr}(V^*,y)\in[L,U]\) — **diagnostic only**; attenuation → often 0 is OK.
  - **H3:** empty rate = 1.0 on `harsh_theta` and `all_invalid`.
  - **H4:** cold independent double-run equality of slacks / \(M^*\) / \(L,U\).
- Near-miss admissions logged separately; not FA. Near-miss must fail ≥1 oracle restriction by DGP design.
- Artifacts: `reports/summaries/v1_0_package_synth_summary.json` (committed proof); per-seed dumps optional/gitignored.
- Do **not** loosen \(\theta\) to chase H1_latent. Do **not** bump package version (`1.0.0a1`).

**Rationale:** Package path must earn its own gates before M9 packaging confidence.

**Follow-ups:** M9 minimal CI only after green M8. Sibling chat owns `v1.0.0` tag evaluation.

---

## 2026-08-01 — Push main without M9; intermediate real-world audit authorized

**Decision:**
- User authorized **push of main** (`29bdea1`) **without M9 CI**. Known gap: no GitHub Actions yet; accepted deliberately.
- User authorized agent to **author an intermediate (non-main-path) real-world audit** to stress the package on free public data — **not** H5 / paper empirical network.
- Intermediate audit lives on branch **`feat/realworld-spam`**: spamminess construct over 20newsgroups-derived multi-measure matrix (sklearn, free, offline-cached). Agent-authored incidental \(R\) OK **only** here.
- **Still locked:** no silent main-path H5 network; no museum import; no `v0.1` move; M6 bootstrap still v1.1.

**Rationale:** Packaging confidence needs more than synthetic DGPs; intermediate domain-agnostic stress is allowed when user explicitly reopens that lane without collapsing H5 ownership.

**Follow-ups:** Keep audit off `main` until Augusto reviews; M9 still recommended before tagging `v1.0.0`.

---

## 2026-08-01 — M9 minimal CI (LOCKED on branch for merge eval)

**Decision:**
- Add GitHub Actions workflow `.github/workflows/ci.yml`:
  - triggers: push to `main` / `feat/**`, PRs to `main`
  - matrix: Python **3.11**, **3.12**
  - steps: `uv sync --extra dev` → `ruff check src tests` → `pytest` → CLI version smoke → AST import-graph hygiene (no LLM / no museum) → mini fixture `cvprofiles run` SCORE→REPORT smoke
- CI does **not** require sklearn / spam audit (evals-only; optional local).
- Merge-safety checklist: `docs/15_Merge_Safety_feat_realworld_spam.md`.
- Still **no** PyPI publish, **no** `v1.0.0` tag from this change, **no** M6 bootstrap.

**Rationale:** Close the known “main pushed without CI” gap before merge evaluation.

**Follow-ups:** Confirm Actions green on branch/PR; merge only after checklist; sibling chat for `v1.0.0`.

---

## 2026-08-01 — v1.1 sprint opened: inference layer (M6) + MVP evidence (LOCKED)

**Decision (LOCKED):**

- **v1.1 scope:** deferred M6 — bootstrap over units + θ-grid sensitivity — plus packaging evidence (battery re-run, `docs/13` row, release checklist `docs/15_MVP_Release_Checklist.md`).
- **Version:** dev `1.0.0a1` → `1.1.0a1`; bump is **atomic** with golden refresh (`data/fixtures/mini_v1/expected_freeze.json`) and **all** version literals (pyproject, `uv.lock`, tests, CI workflow, README). Tool: `tools/refresh_mini_golden.py` (shipped in the bump commit; reads `cvprofiles.__version__`, never hardcodes). **No** tag from this chat.
- **Bootstrap (LOCKED semantics):**
  - Units-only resampling with replacement; **menu fixed** (never resample measures).
  - Single `numpy.random.default_rng(seed)` stream per run; no global RNG.
  - Per replicate: slacks → \(M^*_b\) → \(\beta\) on survivors → \((L_b,U_b)\); percentile band \((2.5\%,97.5\%)\) over **non-empty** replicates only.
  - `empty_replicate_rate` always reported; all-empty ⇒ band null + note.
  - **Headline \([L,U]\) stays \(\min/\max B^*\)** on the full sample; bootstrap band is additive metadata and never replaces the headline.
  - `bootstrap.json` written only when `n_boot ≥ 1`; default `n_boot=0` preserves v1.0 bit-stability of existing runs. `n_boot` in the freeze preimage: `< 1` ⇒ JSON `null` (v1.0 bit-stability), `≥ 1` ⇒ int.
  - Bootstrap uses the run's existing `seed` (already in the preimage); **no** new preimage key.
  - Degenerate replicates (NaN β, e.g. zero-variance resamples) counted as `degenerate_replicate_rate`, excluded from the band, never silently dropped.
  - Band is **pointwise**: 2.5% of the \(L_b\) distribution, 97.5% of the \(U_b\) distribution — not the joint hull. Reflects sampling variation *conditional on admission*; \(M^*\) membership flips across replicates are real, not bugs.
- **θ-grid (LOCKED semantics):**
  - Declared scale multipliers \(\lambda\) applied to **all** \(\theta_r\) (\(\lambda=1.0\) = declared network).
  - Diagnostic sensitivity surface only: per \(\lambda\) → \(M^*\), \([L,U]\), empty flag → `theta_grid.json`.
  - **Never** auto-select \(\lambda\) (no coverage-chasing, no auto-loosening). Headline is always \(\lambda=1.0\).
  - λ scales **threshold magnitudes only**; sign/direction constraints are never scaled. λ ∈ positive reals; grid config is **not** part of the freeze preimage (diagnostic viewport; same bundle + different grid ⇒ same run_id, different `theta_grid.json`). Off unless explicitly requested.
- **Evidence:** battery re-run under `1.1.0a1` → `reports/summaries/v1_1_package_synth_summary.json`; `docs/13` row; spam audit proof is version-agnostic and remains v1.0-era evidence (optional re-verify under 1.1.0a1).
- **Q19:** PyPI name availability check recorded as a note; publishing is **not** in v1.1.
- Release checklist: former `docs/15_Merge_Safety_feat_realworld_spam.md` converted to `docs/15_MVP_Release_Checklist.md` (branch was merged + deleted).

**Rationale:** User asked to close the v1.1 package with enough observed capability to promote as MVP. Tag / release decision stays with the release-review chat; this chat ships evidence only.

**Follow-ups:** atomic version bump → bootstrap → θ-grid → wiring → evidence → handoff push. No tag, no PyPI, no sharp-PI claims, no δ-grid (separate decision).

---

## 2026-08-04 — v1.1 implementation/evidence close-out; release review pending

- **A–F implementation/evidence:** `cfee00e` → `d35e657` → `dddc681` → `283ef27` → `098e2fa` → `784c1be`; `main` pushed and clean at `784c1be` before this documentation close-out.
- **Package:** `1.1.0a1`; local final pre-close verification was ruff clean, **121 passed**, CLI version smoke passed, `v0.1` remained immutable at `fb62b48bcb704f60eee7d6641ed0a344eb72bfda`.
- **Evidence:** `reports/summaries/v1_1_package_synth_summary.json`; generated against parent `098e2fa`, with package-native battery and inference probes audited in `docs/13`.
- **Q19:** PyPI JSON endpoint returned HTTP 404 (name appears available); no publication attempted.
- **Boundary:** no v1.1 tag, no PyPI release, no USER empirical network, no H5, no sharp-PI claim, and no δ-grid. Release-review chat + Augusto own promotion/tag decisions. GitHub Actions status was not observed locally and remains for release review to confirm.

---

## 2026-08-04 — v1.1 verification close-out (local-only)

**Decision:**
- Augusto confirmed GitHub Actions `ci` green on `main` via the GitHub UI at `9ece618`; this is recorded as owner confirmation, not agent-fetched evidence.
- Local verification was recaptured: ruff clean, **121 tests passed**, CLI version `1.1.0a1`, `v0.1` remains immutable, import hygiene passed, and the museum PoC remains present and unimported.
- This close-out is documentation-only; no package code, tests, tools, version, goldens, or inference semantics changed.
- v1.1 is treated as a shipped and verified development artifact on `main`. No v1.1 tag or PyPI publication has been made; release posture remains Augusto/release-review owned.

**Rationale:**
- The implementation and local gates were already complete. Owner-confirmed remote CI closes the verification gap without silently converting a development artifact into a public release.

**Follow-ups:**
- Gate A: decide whether to keep `1.1.0a1` as the dev artifact while protocol/evidence work proceeds, prepare a release-review handoff, or defer release posture.
- Do not begin the paper-facing protocol freeze until the release posture is acknowledged.

---

## Open Engineering Notes

- Stack/license/package name confirmed; Q22/Q23/Q24 closed; v0.1 green and **public**.
- Tag/release live at `fb62b48`; **`main`** carries M1–M9 + intermediate spam audit + v1.1 inference layer and evidence, plus the close-out commits (protocol lock, MC50 audit tool, strict typing enforcement).
- **v1.0 spine shipped** on main; **v1.1 shipped and locally verified; CI green per Augusto’s GitHub UI confirmation:** bootstrap + θ-grid (M6) + MVP evidence; tag/PyPI remain pending.
- **run_id / freeze hash algorithm LOCKED at M1**; version bumps move run_id (golden refresh in same commit).
- **SCORE normalization LOCKED:** default `none`; optional `zscore_measures` on measures only.
- **RESTRICT/IDENTIFY thin spine live:** corr_min/corr_sign + corr_y.
- **REPORT + `run` composition live (M7).** M9 CI live on main.
- **M8 synth harness green;** museum unimported.
- Do **not** import museum monolith into `src/`.
- Do **not** move tag `v0.1`.
- Dev version bumps are not release tags.

---

## 2026-08-04 — Gate A: retain verified development posture

**Decision:**
- Augusto chose to keep `1.1.0a1` as a verified development artifact while the paper-facing protocol freeze and synthetic evidence work proceed.
- No v1.1 tag or PyPI publication is authorized by this decision.
- Phase 2 is authorized as a documentation-only protocol draft; Phase 3 remains blocked until Gate B receives an explicit `LOCKED` or `LOCKED AS PROVISIONAL SYNTHETIC-ONLY PROTOCOL` response.

**Rationale:**
- The package is locally verified and CI-green by owner confirmation, but a public release is not the scientific bottleneck. Protocol discipline should precede paper-facing evidence.

**Follow-ups:**
- Draft `docs/16_Paper_Protocol_Freeze.md` with locked, awaiting, and deferred fields.
- Do not invent a construct, score matrix, empirical network, θ, δ, or β choice.

---

## 2026-08-04 — Gate B: provisional synthetic-only protocol locked by delegation

**Decision:**
- Augusto delegated the synthetic protocol decision to the agent. This delegation is recorded as **`LOCKED AS PROVISIONAL SYNTHETIC-ONLY PROTOCOL`**, not as a full paper lock.
- Locked synthetic box: scenarios `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`; \(n=1000\); SCORE policy `none`; \(\delta=0\); β=`corr_y`; battery seeds `0..49`.
- Load-bearing gates: H1a false-admission and anchor retention, H1b, H3, and H4. H2 is not separate; false admission is the H1a/H2 component.
- Additive diagnostics: H1_latent; bootstrap with fixed probe seed `7` and `n_boot=80`; θ-grid with \(\lambda\in\{0.5,1.0,2.0\}\). Bootstrap/θ-grid are appendix diagnostics only, not the headline range or sharp-PI claims.
- The shipped `reports/summaries/v1_1_package_synth_summary.json` with seeds `0..4` remains untouched package smoke evidence. The protocol table will use a distinct summary path.
- Empirical construct, unit/universe, score matrix/menu, empirical \(R\), paper θ anchors, paper δ interpretation, paper β choice, paper claims, and reporting placement remain Augusto-owned and unresolved.
- No engine change, push, tag, PyPI publication, or empirical/H5 run is authorized by this lock.

**Rationale:**
- A broader predeclared seed list produces a more useful synthetic protocol table than relabeling the five-seed package smoke battery, while keeping the scientific claims boundary explicit.

**Follow-ups:**
- Run one distinct MC50 evidence tool through the existing public package path.
- Independently audit the summary JSON, then append the result to `docs/13` and stop at Gate C.

---

## Reversal policy

To reopen a LOCKED item: new dated entry here stating what changes and why. Chat agreement alone is not enough for future agents.

---

## 2026-08-04 — MC50 proof audit tool + strict typing enforcement

**Decision (LOCKED):**
- Add a read-only MC50 proof auditor `tools/verify_v11_protocol_synth_mc50.py` and its
  TDD suite `tests/test_v11_protocol_synth_mc50_audit.py` (9 tests). The tool
  validates the committed `reports/summaries/v1_1_protocol_synth_mc50_summary.json`
  against the locked protocol: provenance/identity fields, settings (scenarios,
  seeds `0..49`, `n=1000`, `delta=0`, `beta=corr_y`), per-seed structural
  invariants, recomputed aggregates, gate agreement, strict JSON non-finite
  rejection, bootstrap count/band semantics, harsh-empty contrast, and museum
  import hygiene. It is deliberately read-only: it never reruns the generator,
  writes artifacts, calls git, or touches the network.
- Fix three pre-existing strict mypy failures without weakening configuration:
  scalar narrowing via `pd.to_numeric(..., errors="raise")` in
  `identify/pipeline.py` and `report/pipeline.py`, and removal of an obsolete
  `type: ignore` in `inference/theta_grid.py`. No runtime behavior changed;
  targeted suites (identify/report/theta_grid) remained green before and after.
- Enforce strict typing in CI: `.github/workflows/ci.yml` now runs
  `uv run mypy src` and `uv run ruff check src tests tools` (previously
  `src tests` only). Local quality battery now matches CI scope.

**Verification (2026-08-04):** ruff clean; mypy `Success: no issues found in 28
source files`; pytest `130 passed`; MC50 auditor exits 0 with
`{"errors": [], "passed": true, "protocol_id": "protocol-v1-synth-provisional-mc50",
"scenario_seed_cells": 200}`; CLI version `1.1.0a1`; `v0.1` unchanged.

**Review note:** an independent reviewer subagent confirmed the verifier is
read-only and raised no blocking findings; a second review pass could not run
because the subagent model had no credits. The audit evidence therefore rests on
the tool's own tests plus that static review. Future evidence claims should cite
the tool command, not remembered numbers.

**Follow-ups:** documentation reconciliation (README/manifest/open questions) and
the human-only release/protocol decisions remain open.

---

## 2026-08-04 — Intermediate tabular audit authorized: calhousing_validity

**Decision (LOCKED):**
- Augusto authorized an intermediate (non-H5) real-world stress on California
  housing (sklearn `fetch_california_housing`, n=20640, tabular), following the
  spam-audit pattern but testing the engine's domain-agnosticism on non-text,
  skewed features with a larger menu (J=8).
- Agent-authored incidental construct "housing quality / desirability" and
  incidental oracle R: `corr_min(v_aux, 0.15)` + `corr_sign(v_aux, +, 0.05)`;
  harsh contrast `corr_min(v_aux, 0.9999)`.
- Lives on branch `feat/intermediate-calhousing`; no merge to `main` until
  Augusto reviews.
- Capability boundaries recorded in the audit README and a pointer in
  `AGENTS.md` so future agents do not cite this lane as paper evidence.

**Calibration note (harsh θ):** the first harsh θ=0.99 did not empty because
`m_spacious_uncrowded` correlates ≈0.9985 with `v_aux` (both are log-composites
of the same signals). Per the harsh-fixture rule, θ was set above the max sample
statistic (0.9999). This is tightening a designed empty contrast, not loosening
or chasing a gate; the oracle θ (0.15/0.05) was unchanged.

**Findings (verify_audit.py exit 0):** FA=0; all 6 designed valids admitted;
`[L,U]=[0.1658, 0.9514]`; harsh empty with first-class callout; cold H4; same
scores_hash; small-n (n=200) clean but **admission flips** (`m_geo_dict`
longitude proxy admitted at n=200, rejected at n=20640) — sampling variation,
documented as a capability boundary; NaN in a measure column fails loud with
`ScoreError` (engine does not impute).

**Boundary:** intermediate only; not H5; no paper claim; no CI changes (sklearn
remains an evals-only dependency, not in core package CI).

---

## 2026-08-04 — H5 Trust design approved (country-level generalized trust)

**Decision (LOCKED as H5 design; run gated):**
- Augusto directed an H5 evaluation design **independent of the SCA2 validity
  precedent**, targeting country-level generalized trust using WVS Wave 7 +
  GPS (behavioral anchor) + AmericasBarometer (2-country probe only), with
  public economic auxiliaries (WDI/WGI).
- The construct paragraph was drafted by the agent at Augusto's **explicit
  one-off delegation** and **approved verbatim** by Augusto. Final wording is
  Augusto's; the delegation does not generalize.
- The nomological network was proposed by the agent with literature anchors and
  **pinned by Augusto**: `corr_min(gps_trust, 0.3)` +
  `corr_min(rule_of_law, 0.3)` + `corr_sign(gini, -1, 0.1)`; δ=0; β=`corr_y`
  with `y = log_gdp_pc` (outcome **not** in the network).
- SCORE input approved: menu = 4 designed-valid WVS facets + 2 designed-invalid
  (`m_noise`, `m_share_agriculture`); aux = gps_trust, rule_of_law, gini;
  unweighted country means default, weighted as diagnostic; per-item respondent
  floor ≥ 200.
- Claims boundary: admissibility + construct-identified range + measurement
  fragility only; no causality, no interchangeability, no country rankings.

**Why independent of SCA2:** the SCA2 folder's `scores_trust.csv` / pilot
network / minimal engine are a separate lab lane (pkg 0.1.0, USA/MEX-adjacent).
H5 numbers must come from a fresh cvprofiles build from raw files with freeze
hashing; SCA2 appears only as data provenance.

**Full spec:** `docs/17_H5_Trust_Design.md`.

**Boundary:** design lock only. Empirical run requires frozen scores + pinned
seed + package version + independent audit + Augusto's run decision. No engine
change, tag, push, or PyPI by this approval. `docs/16` amended 2026-08-04;
synthetic-only MC50 protocol unaffected.

---

## 2026-08-04 — H5 Trust: first frozen build + dev gate (n=35), run gated for paper

**Decision (recorded):**
- Augusto authorized direct read of the SCA2 raw-data folder for the H5 Trust
  build. Builder fixes from real-schema discovery: `convert_categoricals=False`
  for the WVS `.dta` (non-unique value labels), GPS country code column
  `isocode`, WGI legacy-code map (`ROM→ROU`, `ADO→AND`, `ZAR→COD`, `KSV→XKX`,
  `TMP→TLS`), and WDI ISO-3 mapping via `/v2/country` + `countryiso3code`.
- **Transcription fix:** docs/17 listed the WGI Rule-of-Law indicator as `rq`;
  `rq` is Regulatory Quality. Corrected to `rl`. Design intent unchanged
  (rule of law); no network/θ change.
- **Coverage rule clarified:** aux/outcome NaN = no coverage → country excluded
  per the universe rule (never imputed), recorded in the manifest
  (`dropped_missing_coverage`). Measure-column NaN stays fail-loud (aggregation
  bug guard). Empty resulting sample is a BuildError, not an empty frozen file.
- First build + dev gate + independent auditor all exit 0. Numbers in docs/13.

**Boundary:** this is a run of the *design-locked* evaluation, which docs/16 §8
authorizes once frozen inputs + audit exist. It is **not** paper acceptance:
no `docs/13` claim beyond first-run evidence, no tag, no push, no PyPI.
Augusto's explicit run decision is still required before any paper-facing use
or further evidence claims.

---

## 2026-08-04 — H5 Trust: preliminary paper-facing evidence approval (checkpoint)

**Decision (dated):** Augusto granted **preliminary approval** of the first
frozen H5 Trust run (n=35, M\*={m_trust_general, m_trust_in_group},
[L,U]=[0.371,0.624], FA=0, cold H4, audited) as **paper-facing evidence** —
this is the `docs/16` §8 run decision for this designated evaluation.

**What this authorizes:**
- Checkpointing the numbers and minting the tracked evidence summary
  (`reports/summaries/h5_trust_evidence_summary.json`, generated by
  `tools/make_h5_trust_summary.py`, allow-listed in `.gitignore`).
- Citing the first run as paper-facing evidence in project docs/logs.
- Continuing toward v1.1 close-out and the v2.0 roadmap.

**What it does NOT authorize:**
- Final paper lock (Gate C accept) or submission claims — "preliminary" means
  the numbers may still be amended by a dated decision before submission.
- Tag, PyPI publication, or push without a separate explicit decision.
- Any other empirical run (this approval covers the trust evaluation only).

**Artifacts:** proof `evals/h5_trust/proof_summary.json` (auditor exit 0);
summary `reports/summaries/h5_trust_evidence_summary.json`; frozen inputs
`evals/h5_trust/data/scores.csv` + `score_manifest.json`.

---

## 2026-08-04 — Release posture: push + CI fix (mypy target 3.12)

**Decision (recorded):**
- Pushed `main` to origin (`1e8f4a1..fc426fe`) as part of the Augusto-directed
  release posture; tree synced, CI green on the new head.
- **CI root cause found:** uv.lock resolves numpy 2.5.1 for Python >=3.12; its
  stubs use PEP 695 `type` statements, which mypy rejects when
  `python_version="3.11"`. Fix: `[tool.mypy] python_version = "3.12"`
  (superset target; source is 3.11-compatible). Verified locally against the
  exact failing combination and confirmed by CI (`fc426fe` success, both jobs).
  The red runs on `50d5fb2`/`1e8f4a1`/`1e06f3c` were this same issue.

**Boundary:** tag `v1.1.0` and PyPI publication remain Augusto + release-review
decisions; nothing tagged or published.

---

## 2026-08-04 — v1.1.0 tagged (MVP release symbolization)

**Decision (dated, Augusto explicit):** "let's tag this baby" — create and push
the annotated `v1.1.0` tag symbolizing the MVP: v1.0 thin spine + v1.1
bootstrap/θ-grid inference layer + H5 Trust preliminary paper-facing evidence
+ packaging/CI fixes.

**Convention:** tag-as-symbolization (v0.1 precedent). The wheel on the tag
remains dev `1.1.0a1`; PyPI publication is a separate decision with version
alignment at publish time.

**Boundary:** `v0.1` untouched; no PyPI publish; no further tag moves.

---

## 2026-08-05 — v2.0 measure discipline opened: nine decisions pinned (LOCKED)

**Decision (LOCKED):** Augusto approved the measure-discipline plan (`docs/18_Measure_Discipline_Plan.md`) and pinned the nine open decisions:

1. **δ-grid semantics — absolute grid.** Finite, unique, sorted ascending, δ ≥ 0, duplicates fail loud. Headline remains the *declared* δ run (computed outside the surface; no implicit injection). Grid settings are **excluded from the freeze preimage** (same bundle + different grid ⇒ same `run_id`, different `delta_grid.json`), mirroring the θ-grid contract including stale-layer cleanup. `run_identify` gains `delta_override: float | None = None` (default None ⇒ bundle δ; bit-identical default path). Multiplier semantics rejected (degenerate at δ=0).
2. **Evaluator order confirmed:** `mean_order` → `rank_agree` → `ols_coef`, each with a semantics lock before code; `stability` / `diff_means` remain schema-only fail-loud until a fixture demands them.
3. **ols_coef — manual implementation.** numpy closed-form point coefficient; **no statsmodels core dependency**. β is a point functional feeding `[L,U]`; bootstrap already carries uncertainty, so standard errors are not needed for the range. statsmodels may be added later only via a dated decision if robust SEs become a report requirement.
4. **θ-anchor artifact — schema'd `anchors.yaml`.** Fields: `restriction_id`, `citation_key`, `source_phrase`, `anchor_kind` ({literature, derived, author}), `pre_data`. Engine enforces completeness (every restriction id, exactly one) and records `anchors_hash` in the run manifest + `anchors.json` in the run dir + a report panel. Excluded from the freeze preimage (witness: ± anchors ⇒ same `run_id`). **"Pre-data" is a process commitment** — the engine cannot verify file timing; the artifact makes the "literature-grounded θ" claim machine-checkable rather than prose. Purpose: preregistration for thresholds (see `docs/18`).
5. **Version discipline:** keep `1.1.0a1` through ENTRY; bump `2.0.0a1` atomically with golden refresh at the ENTRY→DONE transition.
6. **v2.0 DONE = all four dimensions green** (functional, measurement-methodological, evidence/paper/observability, engineering/release) **plus a new deliverable:** the end output of v2.0 is an **importable `cvprofiles` package with an H5-replication tutorial** (tutorial reproduces M\*={m_trust_general, m_trust_in_group}, [L,U]=[0.371,0.624] from frozen inputs via the installed wheel).
7. **Documentation drift sweep first:** milestone 0 fixes AGENTS.md posture, README roadmap/repo-status, `docs/16` §6 pointer, `docs/15` backlog wording, `docs/10` breadcrumbs, manifest, and `docs/README.md` — before any engine code.
8. **Sprint style:** per-thread checkpoints (stop after each thread for go/no-go).
9. **H5 δ-grid run authorized** (gated on thread (a) shipping): run the δ-grid on the frozen H5 Trust inputs; use a distinct `--out` directory so stale-layer cleanup does not remove the original `bootstrap.json`/`theta_grid.json` from the default run-id dir; append a `docs/13` row.

**Rationale:** closes the 2026-08-01 provisional default "always also report a small δ-grid as sensitivity" as a v2.0 feature; keeps the engine thin (manual OLS, no new dependency); makes threshold discipline auditable.

**Follow-ups:** commit milestone 0 (doc hygiene + `docs/18`); then thread (a) M-a1 with a RED test. Per-thread checkpoints.

---

## 2026-08-05 — v2.0 thread (a) δ-grid complete (close-out)

**Decision (recorded):** δ-grid tolerance layer shipped and verified:
- M-a1 `11e5179` — `delta_override` on `run_identify` (default None bit-identical; finite/≥0 enforced)
- M-a2 `a44e65f` — `cvprofiles.inference.delta_grid` engine (absolute-δ validation, rows, payload)
- M-a3 `ab30d18` — wiring: `run_profile(delta_grid_deltas=...)`, CLI `--delta-grid`, `delta_grid.json`, stale-layer cleanup, HTML/JSON panels, preimage witness (same bundle + different grid ⇒ same `run_id`)
- M-a4 — evidence: H5 Trust δ-grid run on frozen inputs (seed 0). Headline bit-identical ([0.370754, 0.623891]); out_group admits at δ≥0.005; designed-invalid `m_noise` admits at δ=0.5 with L collapsing to −0.319 — logged in `docs/13` as the tolerance-discipline object lesson.
- Full suite **178 passed**; ruff/mypy clean; tags `v0.1` / `v1.1.0` intact.

**Boundary:** diagnostic only; headline range unchanged; no version bump (per D5); H5 δ-grid numbers are not paper evidence beyond the existing preliminary checkpoint. Thread (b) evaluator registry next, pending Augusto's go.

---

## 2026-08-05 — v2.0 thread (b): evaluator semantics locked (D3/D4/D5)

**Decision (LOCKED):** Augusto approved the thread (b) semantics recommended in the docs/18 plan (proceed with M-b*):

- **D3 — mean_order** (`docs/18` thread b, M-b1): params `{group, sign}`, `sign ∈ {+1,−1}` default `+1` (schema-validated); `group` must be a **binary 0/1 indicator** column (fail loud on non-binary, non-finite, or missing column at bind/evaluate). Slack = `sign·(mean(m | g=1) − mean(m | g=0)) − θ`. Fixture `data/fixtures/mean_order_v1/` (hand-computed goldens: m_high 0.30, m_low −0.26, m_slop −1.10).
- **D4 — rank_agree** (M-b2): Spearman ρ between m and `ref_measure` (ties via average ranks), slack = `ρ − θ`; non-finite / missing ref fails loud. Fixture `data/fixtures/rank_agree_v1/` with θ=0.8.
- **D5 — ols_coef** (M-b3): β = **standardized OLS coefficient** on m with `params.controls`; all columns (outcome, controls, measure) z-scored ddof=0 (matching SCORE's zscore convention); numpy closed form; singular design / non-finite → fail loud. No statsmodels core dependency (decision 3). Fixture `data/fixtures/ols_v1/` with exact-recovery golden.
- Registry discipline unchanged: `stability` and `diff_means` stay schema-only fail-loud until a fixture demands them.

**Rationale:** locked semantics precede code so each evaluator is auditable and fixtures are hand-computable.

**Follow-ups:** M-b1 mean_order → M-b2 rank_agree → M-b3 ols_coef → M-b4 evidence. One commit per milestone.

---

## 2026-08-05 — v2.0 thread (b) evaluator registry complete (close-out)

**Decision (recorded):** evaluator registry growth shipped and verified:
- M-b1 `910ee0d` — `mean_order` (schema `sign` param + evaluator; fixture `mean_order_v1`, hand goldens 0.30 / −0.26 / −1.10)
- M-b2 `83cd1a7` — `rank_agree` (Spearman via pandas average ranks — scipy.stats has no stubs under strict mypy; fixture `rank_agree_v1`, ρ goldens 1.0 / −0.7576 / −1.0 + ties convention)
- M-b3 `15720c1` — `ols_coef` (standardized numpy closed form, **no statsmodels**; fixture `ols_v1`, exact-recovery golden β≈0.85227, confound-adjustment + singular/zero-variance fail-loud)
- M-b4 — evidence: full suite **196 passed**; three fixtures exercised through the real spine; `docs/13` row.
- `stability` / `diff_means` stay schema-only fail-loud (no fixture demands them).

**Boundary:** feature layer; headline semantics unchanged; no version bump. Thread (c) θ-anchor discipline next, pending Augusto's go.

---

## 2026-08-05 — v2.0 thread (c) θ-anchor discipline complete; ENTRY COMPLETE (close-out)

**Decision (recorded):** θ-anchor documentation discipline shipped and verified:
- M-c1 `0a33554` — `cvprofiles.anchors` schema (restriction_id / citation_key / source_phrase / anchor_kind / pre_data) + completeness validation + `anchors_hash` (canonical JSON, **excluded from the freeze preimage**); `RunManifest.anchors_hash` (additive)
- M-c2 `4e8d15e` — `run_profile(anchors=...)`, CLI `--anchors`, `anchors.json` artifact, HTML "θ-anchors · pre-data audit" panel, summary key; witness: ± anchors ⇒ same `run_id`
- M-c3 `213548c` — H5 anchors transcription (`evals/h5_trust/data/anchors_h5_trust.yaml`, docs/17 §6; **Augusto review point**) + `tools/verify_h5_trust.py` completeness/pre-data pass (audit exit 0, 0 errors)
- M-c4 — `docs/14` §13 anchor practice guidance (process, not engine defaults); `docs/13` row; `docs/18` status
- Full suite **215 passed**; ruff/mypy clean; tags `v0.1` / `v1.1.0` intact.

**Measure-discipline ENTRY complete** (threads a/b/c). Remaining v2.0 DONE criteria: methodology statement (B4), battery re-run under `2.0.0a1` with atomic golden refresh (B5/D3), evidence re-audit (C3), H5-replication tutorial (C5). No version bump yet (D5).