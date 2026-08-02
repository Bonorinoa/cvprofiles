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

**Follow-ups:** M1 schemas + freeze hash + mini fixture + failing contract tests; lock run_id hash algorithm in a subsequent M1 decision-log entry.

---

## Open Engineering Notes

- Stack/license/package name confirmed; Q22/Q23/Q24 closed; v0.1 green and **public**.
- Tag/release live at `fb62b48`; `main` may advance (doc-14 DRAFT companion; v1.0 spine sprint live).
- **v1.0 scope locked** this sprint: thin spine; M6 → v1.1; no M10.
- Lock run_id hash spec at M1.
- Restriction registry extension mechanism still open.
- SCORE convention locked in PoC payload: z-score measures + v_aux/y/V_star; g binary.
- Package name PyPI availability unknown.
- Design Spec doc intentionally absent.
- `14_Researcher_Input_Guide` DRAFT — promote locked subsections after Augusto review (composite defaults, min \(n\)).
- Do **not** import museum monolith into `src/`.
- Do **not** move tag `v0.1`.

---

## Reversal policy

To reopen a LOCKED item: new dated entry here stating what changes and why. Chat agreement alone is not enough for future agents.
