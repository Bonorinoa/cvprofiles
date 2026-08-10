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
- Finite researcher-supplied menu $M$; no prompt-space search in engine.
- Construct validity = partial ID over measurement menu under researcher nomological network $R,\theta$.
- Closest ancestor: Leamer → measurement functions; formal home: partial identification.
- Network $R$ answers validity-of-$C$; $\beta$ answers downstream conclusion — **not hard-coded as derivatives of each other**.
- **USER OWNS** construct definition, every nomological restriction and $\theta$ anchor, go/no-go, paper narrative (main path).
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
- Slack sign: $s_r(m)\ge 0$ satisfied; default $\delta=0$; always also report a small $\delta$-grid as sensitivity, not headline.
- First $\beta$: `corr_y` primary; `ols_coef` secondary check in PoC.
- Bootstrap (when implemented at M6): over **units** only; menu fixed; `numpy.random.Generator`; $B=999$; percentile on $(L,U)$; conservative tone; sharp PI optional garnish.
- Prereg bars (working): $c_{\min}=0.90$, $f_{\max}=0.05$ at $\delta=0$ — freeze later with eval evidence.
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
- **PoC gate (mechanical):** SCORE→RESTRICT→IDENTIFY→REPORT path works; FA=0 on invalids; empty $M^*$ handled; user condition “code for synthetic evals before git” is satisfied **mechanically**.
- **PoC gate (scientific honesty):** not clean enough to freeze H1–H4 or declare synthetic evals “done.” Three DGP/harness bugs + coverage-metric attenuation issue logged (see eval log).
- **Git:** still **no remote**. Local `git init` is now *eligible* per user rule, but deferred one beat so Augusto can choose: init on v0 as historical snapshot vs wait for v0.1 bugfixes. Agent will not init until user picks.
- **No silent θ-loosening** to manufacture coverage.

**Rationale:** Empty docs theater avoided; also avoid celebrating a misleading coverage=0 or a misnamed `all_invalid`.

---

## 2026-08-01 — H1 coverage vs attenuation (open methodology)

**Decision (OPEN at time of writing — superseded by next entry):**
See following entry. Original A/B/C/D menu preserved as historical context only.

Under $\beta=\mathrm{corr}_y$, oracle $\beta^*=\mathrm{Corr}(V^*,y)$ systematically exceeds $\mathrm{Corr}(m,y)$ for noisy admissible $m$ (classical attenuation / EIV).

---

## 2026-08-01 — Q22/Q23/Q24 closed; v0.1 PoC hygiene before git

**Decision (LOCKED):**

**Q22 — H1 metrics (hybrid A+B; reject C for reported range):**
- **H1a** (gate): false-admission of `invalid_*`/`wrong_construct` + anchor (`m_dict`) retained in $M^*$ under oracle $R$.
- **H1b** (gate / construction invariant): when anchor $\in M^*$, $\beta(m_{\mathrm{anchor}})\in[L,U]$ because $[L,U]=\min/\max B^*$. Primary scientific bite is H1a + H3 + H4, not celebrating H1b=1.0.
- **H1_latent** (diagnostic only): fraction of seeds with $\mathrm{Corr}(V^*,y)\in[L,U]$. Expected low under attenuation. Never a CI/package gate.
- **Reject C:** no attenuation band painted onto reported $[L,U]$.
- **Reject** silent $\theta$-loosening or swapping latent target into the scientific range.

**Q23 — near_miss under oracle $R$:**
- Near-misses (`m_near`, `m_floor`) must **fail ≥1 restriction by DGP design** under standard oracle $R$.
- Do not relabel to `valid` to clear the metric.
- Near-miss admission is logged separately; not FA.

**Q24 — process:**
- v0.1 monolith hygiene **before** M1 package layout and **before** local `git init`.
- Local git init **only if** v0.1 battery exits 0 / gates green. Still **no remote**.

**PoC gates (v0.1 exit criteria):**
| Scenario | Must hold |
|---|---|
| `oracle_easy`, `oracle_with_slop` | FA=0; anchor in $M^*$ all seeds; H1b=1 when nonempty; near_miss not all admitted |
| `harsh_theta`, `all_invalid` | empty_set_rate=1.0; FA=0 |
| all | cold determinism True; H1_latent reported but not gated |

**Rationale:** Load-bearing claim is admissible set + image of $\beta$, not recovery of latent Corr(V*,y). Reliable PoC is user-stated prerequisite for repo.

---

## 2026-08-01 — v0.1 PoC gates GREEN; local git init authorized

**Decision:**
- `evals/synthetic/v0_poc.py` (`v0_1_poc`) exit code **0**; all programmed gates passed.
- Proof summary: `reports/summaries/v0_1_poc_summary.json` (committed); per-seed JSON under `reports/runs/` stays local/ignored.
- **Local `git init` + first commit authorized.** Still **no GitHub remote**, no push, no `AGENTS.md`, no M1 package layout until Augusto asks.
- Monolith remains museum evidence; never import into `src/`.
- H1b=1.0 recorded as construction invariant, not oversold.

**Gate snapshot (5 seeds):**
| Scenario | empty | FA | anchor_in | H1b | H1_latent | cold | slop $\bar\beta$ |
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
  - One construct per run; small $J$; freeze recipes in `scoring_notes.md` beside runs.
- Indexed from root README, `docs/README.md`, `PROJECT_MANIFEST.md`; glossary terms added.
- Does **not** author SCA2/H5 empirical $R$; SCA-style worked pattern is illustrative posture only.
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
- **In v1.0:** installable thin package `src/cvprofiles` + CLI; SCORE → RESTRICT → IDENTIFY → thin REPORT (HTML/JSON); finite menu; sample slacks → $M^*$ → $[L,U]=\min/\max B^*$; freeze hash + bit-stable rerun; synthetic harness re-implemented under package/tests (H1a / H2 / H3 / H4); empty $M^*$ clean success; no LLM in engine or installable import graph.
- **Out of v1.0:** **M6 bootstrap / θ-grid → v1.1**; M10 / H5 / real baseline / USER empirical network content; sharp PI; prompt search / measure generation; GUI/SaaS; importing museum monolith into `src/`; moving tag `v0.1`; “fully tested MVP” polish.
- **Build order (strict):** M1 → M2 → M3 → M4 → M5 → M7(thin) → M8 → M9. **No M6. No M10 this sprint.**
- **Gate path:** G1 → G2 → G3 → G4 → G5 → G7-thin → G8-mini → package install/CI. G7/G8 re-enter from G5 (not G6) for this sprint. G6 deferred to v1.1.
- **Hypothesis wording (unchanged):** H1a / H1b gates; H1_latent diagnostic only (attenuation). See `03`, `05`.
- **Tag `v0.1` @ `fb62b48`:** immovable. Methods KB + museum PoC only. Do not move, delete, or retag.
- **Museum:** `evals/synthetic/v0_poc.py` stays present and **unimported**. Package path must earn its own gates; museum was directional only.
- **Authority split unchanged:** USER owns construct / every $R,\theta$ / go-no-go / paper narrative. Agent may author oracle networks for synthetic DGPs only. Doc-14 remains DRAFT process guidance — not package defaults that author constructs.
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

**Follow-ups:** M4 slacks + $M^*$; M5 $\beta$ + min/max range.

---

## 2026-08-01 — M4/M5 G4/G5 IDENTIFY (LOCKED)

**Decision:**
- Evaluators in v1.0 thin spine: **`corr_min`**, **`corr_sign`** only. Other schema types fail loud until a fixture demands them.
- $s_r \ge -\delta$; $\delta=0$ default. Full slack matrix + `rejected` reasons.
- $M^*$ from survivors; empty $M^*$ is **success** (not exception).
- $\beta$: **`corr_y` only**. $[L,U]=\min/\max B^*$ on survivors; non-survivors still get $\beta(m)$ marked rejected.
- Never loosen $\theta$; never include rejected $\beta$ in range; no bootstrap (v1.1).
- Harsh fixture: `data/fixtures/mini_v1/network_harsh.yaml` with `corr_min` $\theta=0.999$ (above max sample corr on mini) → true empty $M^*$.

**G4/G5 proof:** `tests/test_identify.py` — FA=0 on `m_slop`; empty harsh; cold double-run; range is image of $B^*$ only.

**Follow-ups:** M7 thin REPORT + `run` composition. No M6.

---

## 2026-08-01 — M7 G7 thin REPORT + full run composition (LOCKED)

**Decision:**
- Thin REPORT: `report.html` (Jinja2 one-page audit) + `report.json` (machine-complete). No TeX this sprint. No bootstrap/θ panels (footer notes v1.1).
- Full composition: `cvprofiles.pipeline.run_profile` = SCORE → RESTRICT → IDENTIFY → REPORT into one run directory under `reports/runs/<run_id>/` (or `--out`).
- CLI: `cvprofiles run --scores --roles --network --beta [--out] [--policy] [--seed] [--title]`.
  - **stdout = pure JSON summary** (machine-parseable).
  - Human status crumbs → **stderr only**.
- Empty $M^*$ is exit code **0**; HTML shows first-class “Empty admissible set — success, not a crash” callout; never auto-loosen $\theta$.
- G7 enters from **G5** (not G6) for v1.0 thin spine. Bootstrap remains v1.1.
- Jinja template packaged via hatch `force-include` of `report/templates/`.
- mini_v1 e2e: oracle $M^*=\{m\_good,m\_weak\}$, FA=0 on `m_slop`; harsh empty clean; cold double-run same `run_id` / $M^*$ / $[L,U]$; golden freeze hashes unchanged under `1.0.0a1`.

**G7 proof:** `tests/test_report.py` + `tests/test_pipeline_e2e.py`; full suite green; live demos under `reports/runs/demo_mini_v1_*` (gitignored).

**Follow-ups:** M8 package synth harness re-impl (H1a/H2/H3/H4); M9 minimal CI. **No M6 this sprint.** Do not tag `v1.0.0` from this chat.

---

## 2026-08-01 — M8 package synth harness (LOCKED)

**Decision:**
- Re-implement synthetic DGP + oracle $R$ + metrics + battery under `src/cvprofiles/synth/`.
- **Museum** `evals/synthetic/v0_poc.py` remains historical only — **never import**.
- Battery drives the **real package path**: `run_score` → `run_restrict` → `run_identify` (not a parallel identify).
- Scenarios (v1.0 mini battery): `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`.
- Seeds: `0..4`; $n=1000$; $\delta=0$; $\beta=\mathrm{corr}_y$; SCORE policy `none` (DGP emits analysis-ready columns; optional internal centering is DGP-side only if needed).
- Oracle $R$ (eval-only, agent-OK): `corr_min(v_aux)` + `corr_sign(v_aux,+)` — uses existing evaluators only. Harsh raises `corr_min` $\theta$. No bootstrap/θ-grid (M6 = v1.1).
- Gates:
  - **H1a:** FA of labels in `{invalid_confounded, invalid_noise, wrong_construct}` = 0 on oracle scenarios; anchor `m_dict` ∈ $M^*$ on all oracle seeds.
  - **H1b:** $\beta(m_{\mathrm{dict}})\in[L,U]$ when nonempty (construction invariant).
  - **H1_latent:** $\mathrm{Corr}(V^*,y)\in[L,U]$ — **diagnostic only**; attenuation → often 0 is OK.
  - **H3:** empty rate = 1.0 on `harsh_theta` and `all_invalid`.
  - **H4:** cold independent double-run equality of slacks / $M^*$ / $L,U$.
- Near-miss admissions logged separately; not FA. Near-miss must fail ≥1 oracle restriction by DGP design.
- Artifacts: `reports/summaries/v1_0_package_synth_summary.json` (committed proof); per-seed dumps optional/gitignored.
- Do **not** loosen $\theta$ to chase H1_latent. Do **not** bump package version (`1.0.0a1`).

**Rationale:** Package path must earn its own gates before M9 packaging confidence.

**Follow-ups:** M9 minimal CI only after green M8. Sibling chat owns `v1.0.0` tag evaluation.

---

## 2026-08-01 — Push main without M9; intermediate real-world audit authorized

**Decision:**
- User authorized **push of main** (`29bdea1`) **without M9 CI**. Known gap: no GitHub Actions yet; accepted deliberately.
- User authorized agent to **author an intermediate (non-main-path) real-world audit** to stress the package on free public data — **not** H5 / paper empirical network.
- Intermediate audit lives on branch **`feat/realworld-spam`**: spamminess construct over 20newsgroups-derived multi-measure matrix (sklearn, free, offline-cached). Agent-authored incidental $R$ OK **only** here.
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
  - Per replicate: slacks → $M^*_b$ → $\beta$ on survivors → $(L_b,U_b)$; percentile band $(2.5\%,97.5\%)$ over **non-empty** replicates only.
  - `empty_replicate_rate` always reported; all-empty ⇒ band null + note.
  - **Headline $[L,U]$ stays $\min/\max B^*$** on the full sample; bootstrap band is additive metadata and never replaces the headline.
  - `bootstrap.json` written only when `n_boot ≥ 1`; default `n_boot=0` preserves v1.0 bit-stability of existing runs. `n_boot` in the freeze preimage: `< 1` ⇒ JSON `null` (v1.0 bit-stability), `≥ 1` ⇒ int.
  - Bootstrap uses the run's existing `seed` (already in the preimage); **no** new preimage key.
  - Degenerate replicates (NaN β, e.g. zero-variance resamples) counted as `degenerate_replicate_rate`, excluded from the band, never silently dropped.
  - Band is **pointwise**: 2.5% of the $L_b$ distribution, 97.5% of the $U_b$ distribution — not the joint hull. Reflects sampling variation *conditional on admission*; $M^*$ membership flips across replicates are real, not bugs.
- **θ-grid (LOCKED semantics):**
  - Declared scale multipliers $\lambda$ applied to **all** $\theta_r$ ($\lambda=1.0$ = declared network).
  - Diagnostic sensitivity surface only: per $\lambda$ → $M^*$, $[L,U]$, empty flag → `theta_grid.json`.
  - **Never** auto-select $\lambda$ (no coverage-chasing, no auto-loosening). Headline is always $\lambda=1.0$.
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
- Locked synthetic box: scenarios `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`; $n=1000$; SCORE policy `none`; $\delta=0$; β=`corr_y`; battery seeds `0..49`.
- Load-bearing gates: H1a false-admission and anchor retention, H1b, H3, and H4. H2 is not separate; false admission is the H1a/H2 component.
- Additive diagnostics: H1_latent; bootstrap with fixed probe seed `7` and `n_boot=80`; θ-grid with $\lambda\in\{0.5,1.0,2.0\}$. Bootstrap/θ-grid are appendix diagnostics only, not the headline range or sharp-PI claims.
- The shipped `reports/summaries/v1_1_package_synth_summary.json` with seeds `0..4` remains untouched package smoke evidence. The protocol table will use a distinct summary path.
- Empirical construct, unit/universe, score matrix/menu, empirical $R$, paper θ anchors, paper δ interpretation, paper β choice, paper claims, and reporting placement remain Augusto-owned and unresolved.
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

---

## 2026-08-05 — Anchors confirmed; v2.0 DONE phase + PyPI publication authorized

**Decision (dated, Augusto explicit):**
- The H5 θ-anchor transcription (`evals/h5_trust/data/anchors_h5_trust.yaml`) is **confirmed as written** (D6/D7 review point closed).
- Approved: proceed through the v2.0 DONE criteria in the recommended order and **publish the package to PyPI**, verified by an independent notebook tutorial (synthetic data first, then the H5 replication).
- This is the explicit publication authorization previously held open (AGENTS.md convention 6). It authorizes: version alignment for publication, `uv build`, the PyPI upload of the release version, the `v2.0.0` symbolization tag, and the branch/tag push. It does **not** change the four-state spine or any scientific lock.
- First PyPI deployment for Augusto: a walk-through accompanies the close-out.

**Follow-ups:** atomic version bump `1.1.0a1 → 2.0.0a1` (+ golden refresh) → battery re-run → tutorial (synthetic + H5) → build/publish → tag/push → reconciliation.

---

## 2026-08-05 — v2.0.0 release preparation (version alignment)

**Decision (recorded):** aligning the package version to `2.0.0` for the first PyPI publication (convention: version alignment at publish; docs/12 2026-08-01). Atomic with golden refresh and all version literals. The wheel built from this commit is the published artifact; the repo may return to a dev version (`2.0.1a1`) in a later dev cycle. Tags `v0.1` / `v1.1.0` unchanged. PyPI upload is executed by Augusto in his own terminal (token never enters the agent session).

---

## 2026-08-06 — cvprofiles 2.0.0 published to PyPI (release close-out)

**Decision (recorded):** Augusto ran `uv publish` in his own terminal (the API token never entered the agent session); both artifacts uploaded. Independent verification (not self-report):
- **PyPI JSON API:** cvprofiles 2.0.0 live (wheel + sdist, owner Bonorinoa, `requires-python >=3.11`); local wheel sha256 `a125ae1d…` == PyPI's recorded sha256 (provenance: the artifact on PyPI is the one built from `6abb6e4`).
- **Tutorial verification against the PyPI package:** clean venv, `pip install cvprofiles==2.0.0` from PyPI, notebook executed via nbconvert. Part 1 (synthetic) green with the empty-set contrast; Part 2 H5 replication bit-identical — M\*={m_trust_general, m_trust_in_group}, [L,U]=[0.37075446228800285, 0.62389053803067]; assertion cell passed.
- **Tag:** annotated `v2.0.0` @ `6abb6e4` (release-prep commit whose wheel was published); branch + tag pushed.
- Full suite **215 passed**; ruff/mypy clean; tags `v0.1` / `v1.1.0` intact.

**Open / honest notes:**
- The PyPI project description is the pre-publication README (says "publication in progress"); it refreshes on the next release. Cosmetic only.
- Paper protocol fields remain Augusto-owned; H5 numbers remain preliminary paper-facing evidence.
- Dev cycle may resume at `2.0.1a1` when new work starts (atomic bump + golden refresh).

---

## 2026-08-06 — post-release reliability audit (instrument hardening)

**Decision (recorded):** post-2.0.0 audit of the shipped instrument with a measurement-validation lens:
- **Fixed (contract bug):** run-directory stale-artifact cleanup did not cover `anchors.json` (bootstrap/theta/delta were covered). Re-running a directory without anchors left a stale `anchors.json`, violating "run dirs mirror exactly the layers this run produced". Added the cleanup line + witness test.
- **Added (regression):** all-diagnostic-layers composition test — bootstrap + θ-grid + δ-grid + anchors together; headline unchanged; all HTML panels render; artifact inventory matches disk.
- **Docs surface:** module docstring/comment/run-manifest notes refreshed from v1.1-spine language to v2.0 (no behavior change; notes not in the freeze preimage).
- **Audited and left as-is (reliable by design):** evaluator edge cases (zero-variance → `SlackError`; non-binary mean_order group → fail; singular ols_coef design → fail; Spearman ties averaged), NaN fail-loud in SCORE/freeze, empty-M\* exit-0, survivors-only range, preimage exclusions (grids + anchors), verifiers exit 0, provenance/hash checks.
- Full suite **217 passed**; ruff/mypy clean; H5 + MC50 verifiers exit 0.

---

## 2026-08-06 — dev cycle resumed at 2.0.1a1

**Decision (recorded):** after the 2.0.0 publication, the repo resumes a dev version: atomic bump `2.0.0 → 2.0.1a1` (delegated subagent, verified by the main agent): pyproject + `__init__` + uv.lock + mini golden refresh (run_id `52d4baab…`, content hashes stable) + version-literal tests + CI CLI-smoke literal + README/AGENTS posture. Commit `821c737`; **217 passed**, ruff/mypy clean; no push/tag by the subagent. `v2.0.0` published artifact and all historical proofs untouched. Next engine work proceeds from `2.0.1a1`.

---

## 2026-08-06 — post-release audit follow-up: findings closed (docs + hardening)

**Decision (recorded):** independent post-release audit (methodology + software + CI/packaging) found no load-bearing defects; the release claims re-verified (217 tests, ruff, mypy strict, both proof verifiers exit 0, wheel sha256 == PyPI digest, CI green on HEAD). This entry closes the actionable findings:

- **M1 — docs/03 `corr_min` semantics corrected.** The DRAFT catalog sketched `corr_min` as absolute correlation (`|Corr| − θ`); the engine (and docs/17, and the frozen H5 network) implement a **signed lower bound** `Corr(m,V) ≥ θ` (slack `Corr − θ`). Engine semantics are canonical; docs/03 row corrected 2026-08-06. Code unchanged.
- **M2 — docs/17 example uses `sign:`.** The pinned-network block in `docs/17` §5 showed `corr_sign(... direction: -1 ...)`; the engine schema validates `params.sign ∈ {+1,−1}` and the frozen input already used `sign: -1`. Example line corrected; pinned network untouched.
- **M4 — slacks.parquet write failure is now observable.** `write_identify_artifacts` previously swallowed `to_parquet` exceptions (`except: pass`). It now prints a warning to stderr; CSV remains authoritative. TDD: RED (silent) → GREEN (`tests/test_audit_fixes.py`).
- **M5 — blanket DeprecationWarning suppression removed.** `pyproject.toml` no longer ignores all DeprecationWarnings; full suite green with none surfacing.
- **R1 — CI wheel smoke.** New `wheel-smoke` job: `uv build` → fresh-venv install of the wheel → run the mini fixture profile from the installed package → assert report.html/range.json/M* (catches packaging regressions the editable smoke cannot).
- **R2 — coverage measured.** `pytest-cov` in dev extras; CI pytest step reports coverage (no gate). Local: **88%** line coverage of `cvprofiles` (1563 stmts, 185 missed).
- **R4 — manifest `dev_version` refreshed** to `2.0.1a1` (stale `2.0.0` was a current-state literal; audit rule: the atomic version-bump checklist includes `docs/PROJECT_MANIFEST.md`).
- **R5 — SPDX license metadata.** `license = {text = "MIT"}` → `license = "MIT"` (PEP 639); `uv build` verified (`License-Expression: MIT`, template packaged).
- **R3 (PyPI landing README staleness) and R6 (OIDC publish automation)** — **deferred, no action:** R3 refreshes at the next release (PyPI forbids same-version re-upload); R6 stays out of scope while the user-owned token flow is the deliberate posture.
- **Tutorial #2 shipped** — `tutorials/cvprofiles_diagnostics_tour.ipynb` (v2.0 measure-discipline tour; all four evaluators, ols_coef, bootstrap + θ-grid + δ-grid + anchors in one run, CLI, self-checking assertions). Executed against `pip install cvprofiles==2.0.0` in a fresh venv: ALL ASSERTIONS PASSED. Cell ids added (nbformat warning cleared); deterministic run_id `890f95c2…`.
- **Verifier invocation documented** — `tools/verify_h5_trust.py` docstring now carries the exact command and the two traps (`--proof` = proof artifact, `--out-root` = run-artifacts dir).

---

## 2026-08-06 — B4 methodology statement LOCKED (v2.0 DONE complete)

**Decision (dated, Augusto-approved):** Augusto selected **Option B** (framework + inference stance, docs/03 only) from three proposed drafts. Locked into `docs/03` as the "Statement of methodology (v2.0 — B4, LOCKED 2026-08-06)" section: partial identification over a finite menu of measurement functions; `M*` under researcher-authored R with thresholds θ; `[L,U] = [min β(M*), max β(M*)]`; empty/wide ranges as findings; bootstrap/θ-grid/δ-grid additive; Leamer-ancestor positioning; conservative inference stance. This closes the **last v2.0-DONE criterion** (docs/18 status map now all ✅). No version bump implied — package stays `2.0.1a1` dev unless Augusto decides otherwise.

**Status update (same day):** the B4 lock entry above closes the audit's last open item — **all v2.0-DONE criteria are now complete**.

---

## 2026-08-06 — pre-sprint hygiene sweep (v2 → v3)

**Decision (recorded):** final hygiene sweep before the next sprint's design session. Fixed current-posture drift only; historical dated entries and proof artifacts intentionally untouched (per the drift-sweep rule: historical lines stay, current-state lines move):

- **README.md:** roadmap now shows v1.0 shipped / v1.1 superseded / **v2.0 published + all DONE criteria complete**; "PyPI publication pending" and "v2.0 (in progress)" removed; diagnostics-tour notebook added to the doc map; repo-status bullets reconciled.
- **docs/15:** release checklist posture → `v2.0.0` published; v2.0 DONE.
- **docs/10:** Q19 (PyPI publication) moved to Resolved with a breadcrumb row; other open rows stay.
- **docs/13:** appended the audit + v2.0-DONE closure row.
- **Source docstrings:** `schemas/network.py` ("v1.0 schema registry" → v2.0), `schemas/beta.py` ("corr_y only (M5)" → v2.0 evaluators), `cli.py` ("thin v1.0 spine" → thin spine v2.0), `report/pipeline.py` range note "(v1.1)" → "(v2.0)" (notes not in the freeze preimage).
- **Wiring:** `audits/` added to the manifest `directories:` list and the AGENTS.md truth table; AGENTS.md posture notes B4 locked.
- **Local junk:** root `.DS_Store` removed (gitignored, untracked).
- **Left as-is (deliberate):** museum `evals/synthetic/v0_poc.py` (unimported), historical `1.0.0a1`/`1.1.0a1` literals in dated log rows and CHANGELOG release entries, `dist/` published artifacts (provenance), protocol-freeze `AWAITING AUGUSTO` rows (open by design), `stability`/`diff_means` schema-only fail-loud types.

No engine behavior changed; full battery green; next-sprint scope box (docs/19) to be drafted in the new session with the manifest/doc-map/AGENTS wiring done in the same commit.

---

## 2026-08-06 — docs strategy: public-docs rewrite phase (Augusto feedback; Phase 0 shipped)

**Decision (recorded, Augusto-directed):** Augusto reviewed the public-facing documentation and directed a docs-first strategy change. Adopted: **markdown-only for human docs** (no LaTeX doc pipeline; LaTeX stays reserved for the paper and the backlog LaTeX report), consolidated public doc set, and a thin batch-orchestration utility as a later phase. This entry records Phase 0 (shipped); Phase 1 (consolidation) and Phase 2 (method statements + batch utility) get their own dated entries when they land.

**Phase 0 shipped (docs-only, no engine behavior change; 218-test battery green):**

- **README.md rewritten from scratch** for a public/PyPI audience:
  - Removed local-path and Hermes-profile rows (`Hermes profile`, `Path`); removed the Augusto-as-primary-user framing (owner row kept as authorship only, consistent with `pyproject.toml`).
  - Added an **Acknowledgments** section crediting Hermes Agent (Nous Research) as a development tool — explicitly noting that running the package requires only Python and a personal computer.
  - **Install + Quickstart moved near the top** (`pip install cvprofiles` + a real CLI invocation against `data/fixtures/mini_v1/` with measured JSON output; verified live).
  - **Reproducibility contracts promoted to a first-class section** (frozen runs, hashes, survivors-only range, empty-M*-as-success, additive diagnostics).
  - Added a **"When to use cvprofiles (and when not to)"** positioning table (vs Leamer / OVB / variance GSA).
  - Removed all math from the README (PyPI does not render LaTeX); document map trimmed; roadmap moved out.
- **Roadmap extracted to `docs/ROADMAP.md`** — live document, maintained alongside `docs/12`; README keeps only current posture.
- **Math delimiter sweep across all markdown docs**: `\(...\)` → `$...$`, `\[...\]` → `$$...$$` (GitHub-compatible KaTeX), display environments `align*` → `aligned`, and a double-escaped `\\(\\theta\\)` anomaly fixed in docs/14. Verified 0 remaining occurrences outside code fences/inline code. Tutorial notebooks intentionally untouched (Jupyter renders `\(...\)` natively). Tooling: `tools/convert_math_delims.py` (one-shot migration) + `tools/scan_math_delims.py --check` (CI gate).
- **CI**: new "Docs math delimiters use GitHub-compatible $ syntax" step runs the scanner in `--check` mode.
- **docs/01**: users table now leads with empirical researchers (not Augusto); removed the "matches Hermes profile" name note.
- **Left as-is (deliberate):** append-only logs `docs/12`/`docs/13`, governance locks `docs/16`/`docs/17`, and `PROJECT_MANIFEST.md` keep their internal Hermes/local-path references (they are not user-facing package docs; the manifest is machine-readable internal state).

**Phase 1 (next):** consolidate to a public doc set (`METHODOLOGY`, `USER_GUIDE`, `ARCHITECTURE`) written from shipped state in researcher voice; archive pre-ship scaffold docs; update AGENTS.md truth-table + PROJECT_MANIFEST. **Phase 2 (next):** registry rationale + monotonicity gap statement, scalar-entry rationale, report anatomy, when-to-use positioning, and a thin `tools/run_many.py` batch utility (TDD).

---

## 2026-08-06 — docs consolidation shipped (Phase 1)

**Decision (recorded, Augusto-directed):** consolidated the 18-file numbered scaffold into a small public doc set written from shipped state, per the Phase 0 plan. History is preserved: every pre-ship doc moved (not deleted) into `docs/archive/` with a mapping README.

**Shipped (docs-only, no engine behavior change):**

- **New public docs** (researcher voice, markdown, math in `$` delimiters):
  - `docs/METHODOLOGY.md` — canonical method statement (B4 content carried over from archived `docs/03`), restriction registry **with rationale and the monotone-in-continuous-covariate gap**, target registry, inference stance, empty-set aesthetics, when-to-use positioning, notation. Supersedes `docs/03`, `docs/11`.
  - `docs/USER_GUIDE.md` — the four input files with real shapes, CLI + Python API, output artifacts, **report anatomy**, composites/splits, anchors, units, θ-anchor discipline, worked GPS pattern, checklists. Supersedes `docs/14`, CLI/IO parts of `docs/02`.
  - `docs/ARCHITECTURE.md` — four-state machine, **actual shipped module map**, IO contracts, determinism/freeze contract, evaluator registries, report construction, observability, tech stack, failure aesthetics. Supersedes `docs/02`, `docs/06`, `docs/08`.
- **Archived** (git mv, history preserved): `docs/archive/` now holds 01–11, 14, 15, 18 with `README.md` mapping each to its replacement. Kept live: 12, 13, 16, 17, PROJECT_MANIFEST, ROADMAP.
- **Rewired references:** root README doc map + positioning pointer; `docs/README.md` index; AGENTS.md truth table (incl. `docs/18` → archive pointer); PROJECT_MANIFEST reading order + v2_0 plan pointer; `docs/16` source columns and References section now cite METHODOLOGY/USER_GUIDE/ARCHITECTURE or archive paths. Historical log rows in `docs/12`/`docs/13` intentionally untouched (append-only).
- **Shipped-state corrections baked in:** consolidated docs describe the package as it is — numpy closed-form `ols_coef` (no statsmodels; the old `docs/06` said statsmodels), actual `identify/`/`inference/`/`anchors/` module layout, actual artifact set, real CLI flags.
- **Registry rationale + monotonicity gap** (Phase 2 content, folded in early since the docs were being written): narrow registry justified; learned judges/ML slacks explicitly positioned as upstream scoring or downstream robustness, not engine features; `monotone_in_continuous_covariate` named as the known gap with an extension path.

**Left as-is (deliberate):** tutorial notebooks (unchanged), `tools/` verifiers' `docs/16`/`docs/17` string references (both files stay live), archived docs' internal cross-links (historical; archive README says so).

**Phase 2 remaining:** thin `tools/run_many.py` batch utility (TDD) + USER_GUIDE batch-pattern pointer, when it lands.

---

## 2026-08-06 — batch orchestrator shipped (Phase 2)

**Decision (recorded, Augusto-directed):** shipped the thin batch utility answering the multi-construct workflow question ("six GPS dimensions on different networks"). Orchestration only — the engine remains single-construct per run; no engine code changed.

**Shipped (TDD, RED → GREEN; 222-test battery green):**

- **`tools/run_many.py`** — batch orchestrator: one shared SCORE input + roles, N (network, beta) profiles from a YAML manifest, each run via `run_profile` into `<out_root>/<id>/`. Relative network/beta paths resolve against the manifest directory. Writes a machine-readable `batch_summary.json`; stdout is one JSON summary (same contract as `cvprofiles run`); empty M* per profile is exit-0 success. Fail-loud `BatchError` on manifest schema problems or missing profile files.
- **`tests/test_run_many.py`** — 4 tests: two-profile batch (non-empty + empty contrast using the mini fixture's `network.yaml`/`network_harsh.yaml`), relative-path resolution, missing profile file fails loud, missing `profiles` key fails loud. RED observed (ModuleNotFoundError), GREEN after implementation.
- **Determinism witness:** the `good` profile's run_id in the batch equals the single-run mini-fixture run_id (`52d4baab…`) — batch composition does not perturb the freeze.
- **`docs/USER_GUIDE.md` §4.6** — "Single construct per run, batch many": manifest shape, CLI invocation, artifact contract.
- **Scratch cleanup:** one-shot debug tools from the Phase 0 math sweep (`inspect_backslashes.py`, `repr_line350.py`, `verify_conversion.py`, `strip_trailing_ws.py`) removed with Augusto's consent.

**Not done:** engine-level multi-construct joint admissibility remains out of scope (docs/01 archived lock); IRT/sensemakr tutorials deferred to Phase 3 (checkpoint decision).

---

## 2026-08-07 — Phase 3 tutorials shipped + dev checkpoint tag

**Decision (recorded, Augusto-directed):** shipped the two planned Phase-3 tutorials and closed the docs/tooling sprint with a dev checkpoint tag `v2.0.1a1` (a checkpoint, not a release — paper protocol and PyPI publication remain Augusto's).

**Shipped:**

- **`tutorials/cvprofiles_irt_scoring_tutorial.ipynb`** — IRT as a SCORE-upstream scorer. Hand-rolled 1PL (Rasch) fit via scipy (empirical-difficulty init, L-BFGS-B); n=300, J=30; IRT θ recovery ≈ sum score (0.907 vs 0.906); both admitted, noisy measure rejected. Deliberate lesson: the engine is score-agnostic; IRT is one auditable scoring technology upstream of the menu.
- **`tutorials/cvprofiles_sensemakr_tutorial.ipynb`** — OVB sensitivity on a survivor. Hand-rolled Cinelli–Hazlett (2020): partial R², exact OVB identity (impact × imbalance, `u ~ m + w` regression), CH partial-R² reparameterization, robustness value RV_q. All on z-scored variables so numbers line up with the profile's standardized β (0.694 = 0.694). Exact identity recovers full-model τ to <1e-8; CH reparameterization matches.
- **`tools/build_tutorials.py`** — committed, reproducible notebook builder (stdlib-only, nbformat 4.5, empty outputs). E501 per-file ignore added (same precedent as `verify_h5_trust.py`).
- **Verification:** both notebooks executed against the freshly built wheel (`cvprofiles-2.0.1a1`) in a fresh venv via nbconvert — zero errors, all assertions pass. This doubles as the wheel smoke for the tag.
- **Docs:** tutorials/README (four notebooks + regeneration instructions), README doc map, ROADMAP change-log row, CHANGELOG entry.
- **Scratch cleanup:** `experiment_irt_fit.py`, `debug_ch.py`, `inspect_executed_nb.py` removed with Augusto's consent (mass-deletion gate approved).

**Engineering lessons recorded:**
- The first 1PL fit attempt (BFGS, J=10, naive init) failed to converge and recovered θ worse than the naive sum score (0.546 vs 0.816) — a misleading tutorial. Fix: L-BFGS-B, J=30, empirical-difficulty init. Lesson: hand-rolled JMLE needs good initialization and enough items; tutorials must teach the honest comparison, not a false "IRT wins" claim.
- The CH partial-R² formula recovers |bias| *approximately* (sample analogue); the exact OVB identity γ̂δ̂ is exact to machine precision. The tutorial now teaches both, asserting exactness on the identity and a tight tolerance on the reparameterization.
- The wrong imbalance regression (`D ~ X + Z` coefficient on Z) breaks the identity; the correct one is `Z ~ D + X` coefficient on D (impact × imbalance form).

---

## 2026-08-07 — Gate A signed: v3 amendment bundle (IVS lane, coverage, holdout, evaluators, open-weight policy)

**Decision (recorded, Augusto-directed):** Augusto authorized the full Gate A bundle ("address all the tasks in Gate A as you proposed, everything should stay open-weight or easily interpretable"). All seven decisions + the T24 H5 re-grade are **DECIDED 2026-08-07** and recorded in `docs/16` §9 (dated amendment):

1. **D1 coverage mandate** — additive-but-mandatory; α=0.10, κ=2; honest "uncertainty band" language; no freeze-preimage change.
2. **D2 IVS cultural-values lane is THE v3 direction** — H5 Trust superseded as headline; Joint EVS/WVS 2017–2022 v5.0, Inglehart–Welzel axes, frozen human PCA loadings.
3. **D3 `map_distance` + loadings provenance** — `map_distance` approved as β-registry extension; **Tao et al. published loadings reused verbatim** (incl. PC2′ = 1.61·PC2 − 0.01); fresh PCA fit **not authorized**; `beta_hash` carve-out signed.
4. **D4 evaluator registry** — `monotone_rank` + `corr_zero` (two-sided) approved; fit note: `monotone_rank` only if a continuous-covariate restriction exists (IW axes are PCA axes).
5. **D5 adapters NOT reopened** — no DPO adapters; open-weight prompt-based baselines only.
6. **D6 proprietary APIs NOT reopened** — open-weight local models only for paper-reproducible scoring.
7. **D7 holdout semantics** — country-level units-split is the paper's falsifiable core; restriction-level `stage` split ships as WP2 machinery.
8. **D8/T24 H5 re-grade signed** — n=35 run re-graded to historical/regression witness (docs/13 + docs/17 executed).

**Open-weight policy (affirmative):** all v3 evidence-generating computation uses open-weight local models and fully interpretable artifacts; the engine stays model-free; the harness lives in `evals/`, never `src/` (AST-enforced).

**What Gate A unblocks:** P2 (coverage core + wiring + worked example), P3 (holdout workflow), P4 (evaluators), P5a (IVS design + teaching walkthrough + harness) — all may start once the amendment bundle is committed. Long-lead T32 (Joint EVS/WVS data acquisition) may start in parallel.

**Scope sequencing (clarification, same date):** "unblocks" above means the **semantics locks** for P2–P5a are now committed — the phases are authorized to be *prepared* (planning, fixtures, TDD scaffolding per phase). Actual **implementation** of each phase is a separate work package requiring an explicit task-specific go (AGENTS.md rule 6), as is any push. This entry records the Gate A decisions; it does not by itself start P2 code.

**Not authorized by this entry:** any engine code change, empirical run, tag, PyPI publication, or push. Those remain separately gated (Gate B run decision, Gate C release decision; push requires a task-specific go). Implementation of P2–P5a is a separate work package requiring its own go, as clarified above.

**Docs created/updated in this bundle:** `docs/16` §9 (amendment), `docs/18_IVS_Cultural_Map.md` (design skeleton, authorship Augusto-owned), `docs/17` + `docs/13` (H5 re-grade), `docs/ROADMAP.md`, `docs/PROJECT_MANIFEST.md` (v3_0 block), `docs/README.md` (doc map rows), `README.md`, `AGENTS.md` (truth table row for docs/18).

**Date provenance (2026-08-08, append-only):** the Gate A entry and `docs/16` §9 are stamped 2026-08-07 per the plan's date convention (DEVELOPMENT_PLAN Rev 2 header, 2026-08-07; bundle drafted with the plan). Git-verified execution and commit occurred **2026-08-08** (`b971708`). Execution date governs; no stamp was rewritten.

---

## 2026-08-08 — Rev 3 sprint accepted: P1–P5 engine go (synthetic-first)

**Decision (recorded, Augusto-directed):** Augusto accepted all recommendations in `reports/DEVELOPMENT_PLAN_v3_REV3.md` and authorized engine work for **P1–P5 only**:

1. **Execution authority:** Rev 3 supersedes Rev 2 for sprint execution. Rev 2 remains historical Gate A planning context.
2. **Scope:** P1 synth gate freeze → P2 evaluators (`corr_zero`, `monotone_rank`) → P3 betas (`diff_means`, `map_distance`) → P4 holdout (stage + units-split) → P5 coverage uncertainty band → docs pass at end of P5.
3. **Decision-card defaults locked:** tag = infra + synth (empirical post-tag); holdout headline on $M^*_{\mathrm{robust}}=M^*_{\mathrm{select}}\cap M^*_{\mathrm{holdout}}$; holdout split in freeze `config`; `stability` deferred; coverage = uncertainty band (no CI language); open-weight only; ship `diff_means`; MTMM panel optional/not blocking.
4. **Synthetic-first:** every WP merges only with oracle DGP/fixture goldens, FA/empty honesty, cold freeze core, named gate ids. No real-world/empirical examples in this go.
5. **Explicitly NOT authorized by this entry:** P6 (benchmark kit / IVS harness), P7 (version bump / RC), Gate B empirical run, tag `v3.0.0`, push, PyPI, empirical network authorship, Joint microdata work.

**Baseline at acceptance:** `2.0.1a1`, 223 tests green, ruff/mypy clean, HEAD `64a9eb2`, `v0.1` peel intact.

**Next:** P1 gate spec (`reports/synth_v3_gate_spec.md`) then TDD implementation of P2–P5.

---

## 2026-08-08 — P2 evaluators: corr_zero shipped; monotone_rank fixture pins co-landed evaluator

**Decision / engineering note (P2):**

1. **`corr_zero` (H_disc)** — shipped with TDD fixture `data/fixtures/corr_zero_v1/` and `tests/test_corr_zero.py`. Slack $=\theta - |\mathrm{Corr}(m,V)|$. Commit `6721cb7`.
2. **`monotone_rank` (H_mono)** — schema + evaluator co-landed in the same `corr_zero` commit (shared `RestrictionType` / bind / slacks branch). **TDD deviation:** production evaluator path existed before the dedicated fixture tests. Behavior is now pinned by `data/fixtures/monotone_rank_v1/` + `tests/test_monotone_rank.py` (including `sign=-1` path). Fixture tests were written against measured goldens and are green before this log entry's accompanying commit.
3. **`stability`** remains schema-only fail-loud (decision card #4).

**Not done in P2:** P3 betas, P4 holdout, P5 coverage, docs pass, version bump.

---

## 2026-08-08 — P3 map_distance semantics lock (before implementation)

**Decision (LOCKED for P3 H_beta_map; amended same day — see below):** thin `map_distance` β evaluator, no PCA fit.

### Amended definition (measure-dependent — supersedes draft constant-β wording)

A constant-across-menu distance (shared item columns, measure unused) would collapse $[L,U]$ to a point and nullify the package question. **Rejected.** Implement measure-dependent projection:

$$
\beta(m)=\bigl\|\overline{z}(m)-z^{\mathrm{target}}\bigr\|_2,
\quad
\overline{z}(m)=\frac{1}{n}\sum_{i=1}^{n} x_i(m)\,L
$$

where $x_i(m)$ is the length-$K$ **item vector for measure $m$** at unit $i$, and $L$ is the pinned $K\times 2$ loadings matrix.

**Column resolution:** for measure id `m` and each item id `j` in `params.items`, the SCORE column is **`{m}__{j}`** (double underscore). Example: measure `m_base`, items `["A008","A165"]` → columns `m_base__A008`, `m_base__A165`.

**Params (all in `BetaSpec.params`, enter `beta_hash` via `model_dump`):**
- `items`: `list[str]`, length $K\ge 1$ — item ids (suffixes), not full column names
- `loadings`: `list[list[float]]`, shape $(K, 2)$ — pinned loadings (no fit)
- `target`: `list[float]`, length 2 — target point on the map

**Binding / fail-loud:**
- For every menu measure `m` and every item `j`, column `{m}__{j}` must exist in SCORE available columns
- `len(loadings) == len(items)`; each row length exactly 2; all finite
- `target` length exactly 2; all finite
- Non-finite item cells fail loud at evaluate
- Measure column `m` itself must still exist (roles/IDENTIFY contract) but is **not** used in the distance arithmetic

**Explicit non-claims:** no SVD/PCA fit; no PC2′ rescaling inside the engine; Tao loadings are Gate B transcription, not engine logic.

**Preimage:** items/loadings/target in beta params ⇒ `beta_hash` moves when they change (Gate A D3). Mini fixture stays `corr_y` — mini golden untouched.

**Next:** RED fixture `map_distance_v1` + tests → GREEN → commit; then P4.

---

## 2026-08-08 — P4 holdout semantics lock (before implementation)

**Decision (LOCKED for P4; Rev 3 decision card #2/#3):** holdout is the paper's falsifiable core (D7). Two layers ship under synthetic gates only.

### 1. Restriction-level `stage` (WP machinery)

- `RestrictionSpec.stage: Literal["select","holdout"] | None = None`.
- **None / omitted = select** (admission filter). Explicit `"holdout"` marks a restriction that does **not** gate sample admission; its slacks are still computed and reported as findings.
- **Freeze dump rule (critical):** `hash_network` must **omit only the `stage` key when it is `None`**. Do **not** use blanket `exclude_none=True` on the whole network dump — that would also drop `NetworkConfig.name is None` and move hashes for nameless networks. Implementation: `model_dump(mode="json")` then `pop("stage")` from each restriction when value is `None`. Explicit `stage: "holdout"` (and explicit `"select"` if authored) enter the hash.
- **Regression:** after the schema change, `hash_network(mini_network)` must still equal `mini_expected_freeze["network_hash"]` with **no golden refresh**.
- IDENTIFY: admit on $R_{\mathrm{select}}$ only (`stage is None` or `stage == "select"`). Compute slacks for **all** restrictions. Holdout-stage failures never raise; they populate a holdout verdict payload (exit 0).
- **Degenerate network:** RESTRICT fails loud if the network has ≥1 holdout-stage restriction and **zero** select-stage restrictions (vacuous admit-all is not a valid profile).

### 2. Units-split (D7 paper core)

- Holdout unit list lives in freeze **`config.holdout_units`**: sorted unique list of `unit_id` strings. Absent / empty ⇒ no units-split (legacy path; `config={}` bit-stable).
- Composition when `holdout_units` nonempty:
  1. Train frame = units **not** in the holdout list → slacks + select-only admission → `M_star_select`
  2. Holdout frame = units **in** the list → slacks for all restrictions → per-measure holdout compliance (select-stage + holdout-stage on holdout units)
  3. `M_star_robust = M_star_select ∩ {m : holdout-compliant}`
  4. Headline $[L,U]$ = min/max $\beta$ on **`M_star_robust`**; empty robust = success (null range)
  5. Additive panels: select-only range; holdout findings (not errors)
- Fail loud: unknown unit ids in the list; empty train set; empty holdout set after filter.
- Same scores/network/beta + different `holdout_units` ⇒ different `run_id` (config already in preimage).

### 3. Bootstrap interplay — option (b) LOCKED

- **Headline path** uses units-split + robust set when `holdout_units` is set.
- **Bootstrap band** remains units-only full-frame resample → `run_identify` with **select-stage admission only** (no per-replicate units-split re-composition). Holdout verdict is a **full-sample point finding** outside the band.
- Band label/docs: **"selection uncertainty on the pooled sample; not a holdout-robustness band."**
- Rationale: keeps bootstrap call path thin; avoids degenerate empty-train/empty-holdout replicates; honest non-claim. Option (a) (train-resample + fixed holdout compliance per replicate) is deferred post-P5 if the paper needs it.
- Holdout unit list is never re-drawn inside bootstrap.

### 4. Report payload keys (stable names)

- `M_star` / `admissible` = **headline survivors** (= robust when units-split active, else select/legacy).
- Additive: `M_star_select`, `M_star_robust`, `holdout` block (`units`, `verdict` / failing restriction ids).
- No renamed fields; empty paths exit-0 and template-safe.

### 5. Architecture

- `run_identify` becomes stage-aware (select-only admission + optional holdout-stage findings on the same frame).
- Units-split composition may live in `run_identify` (optional `holdout_units` + `unit_id_col`) **or** a thin helper called from `pipeline.run_profile`; prefer one path so bootstrap and pipeline do not diverge on stage filtering.
- `run_profile` passes `holdout_units` into freeze `config` (today hardcodes `config={}`).

### 6. Explicit non-goals

- No CLI `--holdout-units` required in P4 (pipeline API + tests sufficient).
- No boolean holdout column on the scores frame.
- No P5 coverage theorem; no P6/IVS empirical; no version bump.

**Next:** RED tests (mini hash stable + stage admission) → GREEN P4a → P4b units-split → P5 → docs.

---

## 2026-08-08 — P4a implementation record + P4b units-split decisions (before code)

**Authorization basis:** Rev 3 P1–P5 engine go accepted (`fbd9277`, 2026-08-08); P4 semantics lock (`d502a19`). P4a commit `a3ba3a2`.

### P4a shipped (`a3ba3a2`)

- `RestrictionSpec.stage: Literal["select","holdout"] | None` (select-by-omission).
- `hash_network` surgical pop of `stage=None` (never blanket `exclude_none`); mini golden bit-stable, no refresh.
- `NetworkConfig._stage_mix_valid` schema validator rejects degenerate holdout-only networks on every construction path.
- `run_identify`: slacks for all restrictions; M* admission select-stage only; `holdout_verdict` additive.
- Report/admissible payloads: additive `holdout` key (`units: None` until P4b).
- Verified: 8/8 holdout tests; full suite 260 passed (2 pre-existing CLI PATH-shadow environmental failures — `~/.local/bin/cvprofiles` is the Hermes launcher, not the package CLI; CI installs the real wheel and passes).

### P4b decisions (LOCKED, before code)

1. **β frame (referee-visible):** headline β image is computed on the **full pooled frame** over `M*_robust = M*_select ∩ M*_compliant`. The units-split protects **admissibility decisions only**; it does not re-estimate β on a subset. Rationale: holdout is a selection-robustness device, not a second estimator; re-estimating β on a subset would conflate sampling noise with measurement admissibility. Additive panels: select-only range (full-frame β over `M*_select`); holdout compliance findings. The strict alternative (β on holdout/train frames only) was considered and rejected — it would change the paper's headline claim.
2. **`holdout_units` normalization:** user-supplied list of unit_id strings. `None` and `[]` both mean **no split** (lock §2: "Absent / empty ⇒ no units-split; `config={}` bit-stable"). A non-empty list activates the split and must satisfy — all ids present in the scores frame, train non-empty, holdout non-empty — else fail loud. **Sorted-unique list normalized inside the engine before entering freeze `config`** so list order cannot move `run_id`. Witness test: `["u03","u01","u02"]` and `["u01","u02","u03"]` ⇒ same run_id.
3. **Bootstrap interplay (lock §3 literal):** `run_identify` gains `include_holdout_verdict: bool = True`; `run_bootstrap` passes `False` (units-only full-frame resample, select-stage admission only; holdout verdict is a full-sample point finding outside the band, never per-replicate).
4. **θ/δ grids:** remain select-only diagnostics on the full frame (same posture as bootstrap option (b)). The units-split headline is the only split object in P4; grids are viewports, not claims.
5. **Explicit `stage:"select"` canonical form:** per P4 lock (`d502a19`), explicit select enters the hash when authored. Authors should omit `stage` for select (canonical form). Canonicalizing select→omitted in `hash_network` was considered and **deferred** — it would deviate from the locked freeze semantics; revisit only via dated amendment.
6. **Report payload (split active):** additive `M_star_select`, `M_star_robust`, and `holdout.units`; `holdout` block states `select_frame: train`, `holdout_frame: holdout`; slacks.csv remains all-restriction (select-stage columns from the train frame, holdout-stage columns from the holdout frame). In split mode `holdout_verdict` = failing restriction ids (**any stage**) per measure on the **hold frame** (compliance per lock §2); in legacy (no-split) mode it remains failing holdout-stage ids on the full frame. `admissible`/`M_star`/`empty`/range = robust semantics.
7. Empty robust set = clean success (range null, exit 0). No CLI `--holdout-units` in P4; pipeline API + tests sufficient (lock §6).
8. **Split-frame size guard (clarification):** with "all ids present + non-empty list" validation, an empty holdout is unreachable; the real reachable degeneracy is a **1-row hold frame** (every registry evaluator requires n >= 2). Fail loud at the boundary when either split frame has < 2 rows.
9. **summary_dict / artifacts additive keys (legacy):** `M_star_select` and `M_star_robust` are ALWAYS present — in legacy (no-split) they equal `admissible`; `holdout.units` is None in legacy. No renamed fields; empty paths remain template-safe.

**Next:** P4b RED (`tests/test_holdout_units_split.py`, goldens from the real fixture) → GREEN (normalize helper, `run_identify` split path, `run_profile` config wiring, bootstrap flag) → P5 coverage band → docs.

---

## 2026-08-08 — P5 coverage uncertainty band: semantics lock (before code)

**Decision (LOCKED for P5; Rev 3 decision card #5/#6):** the D1 coverage layer ships as an additive **uncertainty band** over the existing units-only bootstrap replicates. Diagnostic viewport, never a replacement for the headline $[L,U] = \min/\max B^\*$.

### 1. Object and label
- When bootstrap is enabled (`n_boot >= 1`), the run additionally produces a **coverage block** (`coverage.json`) computed from the SAME per-replicate $(L_b, U_b)$ samples as `bootstrap.json` — one resampling loop, no second RNG stream, no RNG-state divergence.
- Honest label: **"uncertainty band"**. Never "confidence interval", "coverage guarantee", or "CI". A formal coverage theorem under arbitrary selection coupling is deferred (Rev 3 non-goal).
- The band is **selection uncertainty on the pooled sample** (P4 bootstrap lock §3: replicates admit on select-stage restrictions only; the holdout verdict is a full-sample point finding OUTSIDE the band). Explicitly **NOT a holdout-robustness band**.

### 2. Quantile default (resolves v1.1 vs Rev 3)
- v1.1 `bootstrap.json` keeps its locked percentile band $(0.025, 0.975)$ — no golden refresh, existing tests/artifacts unchanged. That pair is the $\alpha = 0.05$ case of the coverage rule.
- The coverage block generalizes: per-side $\alpha/2$ quantiles over non-empty replicates, **default $\alpha = 0.10$** (band $(0.05, 0.95)$). `alpha` is a `run_profile` parameter (default 0.10), validated $0 < \alpha < 1$.
- Both bands are reported and clearly labeled: the range box keeps the v1.1 "bootstrap percentile band" line; the coverage panel is the primary "uncertainty band" block.

### 3. Boundary attribution (margin $\le \kappa \cdot \mathrm{SE}$)
- $\mathrm{margin}_m = \min_r s_r(m)$ over restriction columns of the **pooled full-frame slacks** (all restrictions, select + holdout-stage; same object the bootstrap replicates compute — P4 lock §3 replicates use `slack_matrix(frame, measures, all restrictions)`).
- $\mathrm{SE}_m$ = sample SD (ddof=1) of per-replicate $\min_r s_r(m; X_b)$ across **non-empty** replicates (collected inside the existing loop).
- boundary iff $\mathrm{margin}_m \le \kappa \cdot \mathrm{SE}_m$, **default $\kappa = 2.0$**.
- Requires non-empty replicates $\ge 2$; otherwise SE = null and the boundary set is empty with a note. Rejected measures can be boundary (rejected by a hair is fragile).

### 4. $\hat p_m$ (admission frequency)
- $\hat p_m$ = (# non-empty replicates where $m \in M^\*_b$) / (# non-empty replicates). Denominator matches the band; degenerate replicates excluded. Descriptive, not a coverage statement.

### 5. Payload and wiring
- `coverage.json` keys: `schema_version`, `purpose`, `alpha`, `quantiles`, `band_L`, `band_U`, replicate counts (total/nonempty/empty/degenerate + rates), `boundary: [{measure, margin, se, kappa, boundary}]`, `p_hat_m: {measure: float}`, `note` (honest label + "not a holdout-robustness band").
- Present iff `n_boot >= 1`; structured nulls when all replicates empty (band null + note, exit 0).
- Stale `coverage.json` removed when bootstrap off (same pattern as `bootstrap.json`).
- `BootstrapResult` gains additive fields (`min_slack_samples`, `admission_counts`) with defaults — `bootstrap_payload` v1.1 shape unchanged.

### 6. Freeze preimage
- `alpha` and `kappa` are EXCLUDED from the freeze preimage. No new `FreezeBundle.config` keys. Witness: same bundle + different alpha ⇒ same `run_id`, different `coverage.json`.
- No CLI flag in P5 (pipeline API + tests sufficient — P4 lock §6 pattern).

### 7. Explicit non-goals (deferred)
Formal coverage theorem; m-out-of-n bootstrap as primary; replacing the headline band; train-resample + fixed-holdout per-replicate design (P4 lock §3 option (a)); conservative projection cross-check; MTMM full panel (T29).

**Next:** RED (`tests/test_coverage.py`) → GREEN (`inference/coverage.py` + bootstrap loop extensions + wiring) → docs pass.

---

## 2026-08-08 — P5 coverage: non-empty-replicate denominator clarification (before code)

Lock §3/§4 say $SE_m$ and $\hat p_m$ run "across non-empty replicates." Ambiguity: does "non-empty" mean (a) replicate whose **overall** $M^\*_b$ is non-empty, or (b) replicate where the **individual measure** $m$ is admitted?

**Decision (LOCKED): reading (a).** For both $SE_m$ and $\hat p_m$, the denominator is the set of replicates whose overall $M^\*_b$ is non-empty — the same replicates that produce the band (v1.1 convention "percentile band over NON-EMPTY replicates only", docs/12:426). Rationale: matches the band denominator; $\hat p_m$ then has a consistent, interpretable base; per-replicate min-slacks are well-defined even for never-admitted measures (usually negative), so $SE$ remains meaningful. **Rejected measures can therefore be boundary.** All-empty ⇒ denominator 0 ⇒ band null, $\hat p_m$ null per measure, boundary empty (structured nulls, exit 0).

**Pinned in RED tests by:** `len(min_slack_samples[m]) == replicates_nonempty` for every measure $m$.

---

## 2026-08-08 — P5 coverage: boundary rule corrected to $|\mathrm{margin}|$ (methodological amendment, before code)

Lock §3 defined boundary as $\mathrm{margin}_m \le \kappa \cdot \mathrm{SE}_m$ with the intent "rejected by a hair is fragile." As written, the rule is **vacuous for rejected measures**: on the full frame a rejected measure has $\mathrm{margin}_m < 0$, and $\kappa \cdot \mathrm{SE}_m > 0$, so $\mathrm{margin}_m \le \kappa \cdot \mathrm{SE}_m$ holds trivially for EVERY rejected measure regardless of how far it missed the threshold. The boundary set would be the rejected set, adding no information beyond the admission verdict.

**Decision (LOCKED, corrects §3):** $\mathrm{boundary} \iff |\mathrm{margin}_m| \le \kappa \cdot \mathrm{SE}_m$. Distance from the threshold is the object: a strongly rejected measure (large negative margin) is **not** fragile; only measures within $\kappa \cdot \mathrm{SE}$ of the threshold in either direction are flagged. Preserves the intent — fragile admissions (margin just above 0) and near-miss rejections (margin just below 0) are boundary; far-rejected measures are not.

**Pinned in RED tests by:** rule-equivalence on $|\mathrm{margin}|$ for every measure; a deterministic far-rejected case (single `corr_min` with $\theta$ = midpoint of the top-two measured correlations ⇒ the anti-correlated measure misses by ≈ the full distance to $\theta$, well beyond $\kappa \cdot \mathrm{SE}$) is NOT boundary; the near-threshold case is covered by the rule-equivalence itself.

---

## 2026-08-08 — P5 coverage: implementation record (after code)

**Shipped at commit `e088b06`** (post-amendment `cb566c8`). GREEN under the corrected $|\mathrm{margin}| \le \kappa \cdot \mathrm{SE}$ rule. Initial pass: **283 passed**, ruff clean, mypy clean. Final pass after identity regression: **284 passed**.

### Identity regression pin (Rev 3 P5 exit)
`tests/test_coverage.py::test_headline_min_max_b_star_unchanged_by_inference_layers` — committed after `e088b06` as a regression pin on existing behavior (NOT a TDD-first feature). Asserts `run_profile(n_boot=20, alpha=0.10)` produces bit-identical `identify.range_L`, `range_U`, `admissible`, `M_star_select`, `M_star_robust` vs. `run_profile()` with no inference layers. If this ever fails, `run_profile` is mutating the headline — a real bug, not paperable.

### Process disclosures (honest record)
- The pre-`cb566c8` "GREEN" runs were against the old signed rule and are historically invalid as P5 evidence. The final battery under the amended $|\mathrm{margin}|$ rule is what counts.
- The $|\mathrm{margin}|$ RED was observed on the rule tests but not committed as a standalone RED commit (covered by the existing RED suite at `b9920d5` re-run after the rule flip).
- Amendment `cb566c8` is committed but pending user ratification (governance-correct vehicle, awaiting confirmation).

### Scope honoured
- **One resampling loop.** `run_bootstrap` collects per-measure min-slacks and admission counts across non-empty replicates in the SAME loop as `(L_b, U_b)`; `compute_coverage` consumes the `BootstrapResult` and does no RNG. Replay equivalence preserved: same bundle + same seed ⇒ identical `bootstrap.json` AND identical `coverage.json`. `bootstrap_payload` v1.1 shape unchanged (coverage is a separate artifact).
- **Honest wording everywhere.** Module docstring, `note=` payload string, HTML template, JSON `headline_note`: "uncertainty band" — never "confidence interval" / "coverage guarantee" / "CI".
- **Selection-only band.** Bootstrap replicates admit on select-stage restrictions only (P4 lock §3); the holdout verdict is a full-sample point finding OUTSIDE the band. Explicitly NOT a holdout-robustness band.
- **$\alpha$/$\kappa$ excluded from freeze preimage.** New `run_profile` kwargs (`alpha=0.10`, `kappa=2.0`); no `FreezeBundle.config` keys. Witness: same bundle + different `alpha` ⇒ same `run_id`, different `coverage.json` (`tests/test_coverage.py::test_alpha_kappa_never_enter_freeze_preimage`).
- **Stale-artifact cleanup.** `coverage.json` removed when bootstrap turns off (same pattern as `bootstrap.json`).
- **No CLI flag** in P5 (pipeline API + tests sufficient — P4 lock §6 pattern).

### Subtle correctness note
Under a units-split active, coverage margins are computed on **pooled full-frame slacks** while bootstrap replicates are **selection-only on the full frame**. That matches the locked P4b semantics: the band is selection uncertainty, the holdout verdict is the robustness object (a point finding outside the band). A future reader should NOT "fix" the coverage frame by switching to train/hold splits — that would change the lock.

### Boundary rule (governs §3)
$|\mathrm{margin}_m| \le \kappa \cdot \mathrm{SE}_m$ (amendment `cb566c8`). Distance from the threshold is the object. Far-rejected measures are NOT boundary; near-threshold admissions and near-miss rejections ARE.

### Deferred (explicit non-goals — restated for the record)
Formal coverage theorem under arbitrary selection coupling; m-out-of-n bootstrap as primary; replacing the headline band; train-resample + fixed-holdout per-replicate design (P4 lock §3 option (a)); conservative projection cross-check; MTMM full panel (T29).

---

## 2026-08-08 — P5 boundary amendment ratified + v2.5.0 infrastructure checkpoint

**Decision (LOCKED, Augusto-directed):**

1. **Boundary rule amendment `cb566c8` ratified.** $\mathrm{boundary} \iff |\mathrm{margin}_m| \le \kappa \cdot \mathrm{SE}_m$ is the governing P5 rule (corrects the pre-amendment signed-margin draft). Distance from the threshold is the object; far-rejected measures are not boundary.

2. **Rev 3 P1–P5 engine go is closed.** Coverage green; honest "uncertainty band" wording; no freeze-key creep for α/κ; identity pin that headline $\min/\max B^*$ is unchanged by inference layers; docs pass landed (`e258dca`).

3. **Tag `v2.5.0` authorized as an infrastructure checkpoint** (package version aligned `2.0.1a1 → 2.5.0` with golden refresh). Explicitly **not** a PyPI release — latest published package remains `2.0.0`. Explicitly **not** `v3.0.0` / Gate C.

4. **P6 deferred** pending discussion after push. Gate B empirical IVS run, Gate C release, and PyPI upload remain Augusto-owned and separately gated.

**Rationale:** mid-sprint engine capability is real and greened; calling it `2.5.0` keeps `3.0.0` reserved for the full Rev 3 + paper-infra close-out without overclaiming a major release.

**Not authorized by this entry:** PyPI publish of 2.5.0; P6 start; empirical network authorship; Joint microdata run; tag move of `v0.1` / `v2.0.0`.

**AGENTS.md note:** protected-file edit timed out during the bump; posture line may lag until Augusto approves a follow-up edit. Durable records (CHANGELOG, docs/12, MANIFEST, README, pyproject) carry `2.5.0`.

---

## 2026-08-09 — P6 tag decision: own checkpoint tag (independent of P7)

**Decision (Augusto-directed, 2026-08-09):** P6 (benchmark kit + IVS harness scaffold + synthetic verifier + teaching notebook) ships as **its own tag**, because its task set is independent of P7 (integration/RC/docs). P6 is a self-contained infrastructure deliverable; it should not be folded into the `v3.0.0` release cut.

**Implications:**
- Tag sequence: `v2.5.0` (P1–P5, 2026-08-08) → **P6 tag** → `v3.0.0` at P7/Gate C (still Augusto-gated).
- P6 exit = its own gate: benchmark bundle + verifier exit 0 on synthetic IVS freeze + tutorial under wheel + AST import-graph lock + battery; then stop for the tag decision.
- P6 does **not** open Gate B (no empirical network authorship, no Joint microdata run, no real IVS scoring).
- Tag version for P6 to be confirmed by Augusto at P6 close (candidate: `v2.6.0` following the v2.x infrastructure-checkpoint convention).

**Not authorized by this entry:** P6 implementation start (separate go), tag creation, PyPI, Gate B, empirical authorship.

---

## 2026-08-09 — WVS/GPS preferences lane: intermediate demo opened (Augusto-directed)

**Decision (Augusto-directed, 2026-08-09):**

- **Lane opened** at `evals/wvs_gps_preferences/` for **patience** and **risk-taking** on local data: GPS (Falk et al. 2018; country level ~80 countries + individual level ~80k) and WVS Wave 7 (2017–2022) codebook-verified items — Q13 "thrift" (patience proxy), Q14 "determination, perseverance" (persistence proxy), Q48 freedom of choice/control 1–10 (agency proxy), Q49 life satisfaction (wellbeing outcome), Q275/Q275R education ISCED (convergent outcome/control), Q279 employment status incl. category 3 self-employed (risk revealed-preference proxy). **WVS Wave 7 core has NO direct risk-taking item** — the risk menu leans on GPS `risktaking` + WVS self-employment + discriminant proxies. WVS missing codes `-1..-5` are masked, never imputed.
- **Framing:** INTERMEDIATE DEMO + POSITION-PAPER COMPLEMENT. NOT paper headline evidence, NOT Gate B, NOT the v3 evidence base. The IVS cultural-values lane (`docs/18`, Gate B) remains the v3 paper headline.
- **v3.0 honest target (re-framed):** prove the concept on the patience/risk application with observable pipeline-consistency validation (cold rerun bit-identical, freeze core, empty paths) — a green-light test before spending resources on IVS data acquisition and the Tao et al. reproduction.
- **GUI decision:** NO form-based GUI for the core. An interactive input-builder notebook ships instead: it walks through authoring the four inputs (`scores.csv`, `roles.json`, `network.yaml`, `beta.yaml`) with validation, generating frozen input files. Form-based GUI stays out of scope unless a future dated decision reopens it.
- **P6 scope (supersedes the Rev 3 synthetic-only framing for this lane):** (1) input-builder notebook; (2) frozen data build (GPS + WVS proxies); (3) two profiles — patience (menu = GPS patience + Q13 + Q14) and risk (menu = GPS risktaking + self-employment); (4) network $R$ + $\beta$ authored by Augusto (agent scaffolds + oracle synthetic checks only); (5) units-split holdout by country (the D7 falsifiable core on real data); (6) `verify_wvs_gps.py` auditor (following the `verify_h5_trust.py` pattern); (7) E2E tutorial notebook. P6 ships as its own checkpoint tag (candidate v2.6.0, per the 2026-08-09 P6 decision above).

**Not authorized by this entry:** agent authorship of the empirical network; PyPI; Gate B IVS run; real IVS data acquisition; tag; push; use of this lane as paper headline evidence.

## 2026-08-09 — 2.5.1 release track: audit fix sprint + tag; PyPI publish deferred

**Context:** Independent audit (2026-08-09) found the docs one major version behind shipped v2.5.0 (A1–A3), the units-split holdout Python-API-only with no CLI flags (B, P0), and PyPI still at 2.0.0 (D1). Four parallel agents closed the doc sync, CLI exposure, version-consistency CI, and the trust-lane recon.

**Decisions (2026-08-09):**

- **CLI holdout exposure (B):** `--holdout-units`, `--alpha`, `--kappa` added to `cvprofiles run`; stdout-JSON / stderr-notes contract preserved; run_id-stability verified live (default and α/κ-tuned runs keep the golden run_id `8f5d240d…`; holdout forks).
- **Version-consistency CI (D4):** `tools/check_version_consistency.py` asserts AGENTS/README/USER_GUIDE/METHODOLOGY/ARCHITECTURE current-posture version lines match `__version__` on every bump; hermetic tests; wired into `ci.yml`. Kills the A1–A3 drift class permanently.
- **Docs sync (A1–A3, D2, D5):** USER_GUIDE/METHODOLOGY/README/ARCHITECTURE moved to shipped v2.5.0 state (holdout stage + units-split, coverage band, `corr_zero`/`monotone_rank`, `diff_means`/`map_distance`, θ on raw sample-statistic scale); README install-from-source pins tags ("main is development; tags are the paper anchors"); WVS/GPS lane README records the cross-repo SCA2 data dependency and the WVS Wave 7 no-direct-risk-item disclosure.
- **Version bump 2.5.0 → 2.5.1** (commit `b4cf0bd`): atomic literal move + golden refresh via `tools/refresh_mini_golden.py` (new mini run_id `8f5d240d…`; content hashes static — no algorithm drift); annotated tag `v2.5.1` pushed 2026-08-09; wheel built and contents verified (templates included, stale 2.0.0/2.0.1a1 artifacts removed from `dist/`).
- **PyPI publish DEFERRED (Augusto-directed, 2026-08-09):** wait until the WVS/GPS tutorial iteration is polished; publish then, followed by the independent verification chain (PyPI JSON API, sha256, fresh-venv `pip install`, notebook execution on the wheel). Posture lines read "tagged; publish pending" until then.
- **Trust-benchmark lane (D3):** recon plan written at `evals/trust_benchmark/PLAN.md`; SCA2-adapter-vs-persona comparison declared **out of scope** (SCA2 project work) by Augusto; plan retained untracked as recon reference only. The feasible empirical lane is the GPS-WVS patience/risk demo.

**Not authorized by this entry:** PyPI upload (owner token step); any claim of published release before upload; empirical network authorship.
