# DEVELOPMENT_PLAN — cvprofiles v3.0.0 Rev 3 (infrastructure sprint)

**Date:** 2026-08-08  
**Author:** Hermes (cvprofiles co-engineer)  
**Status:** **ACCEPTED 2026-08-08** — Augusto accepted all decision-card defaults; engine go = **P1–P5 only** (synthetic-first); docs at end of P5; P6/P7/Gate B/C and empirical work deferred post-tag.  
**Supersedes for sprint execution:** `reports/DEVELOPMENT_PLAN.md` Rev 2 (2026-08-07). Rev 2 remains historical context; **this Rev 3 is the authority for the v3.0.0 implementation sprint.**  
**Inputs:** position paper v5 audit (2026-08-08), `docs/16` §9 Gate A locks, `reports/math_spec.md`, `reports/VERIFIED_TASK_INVENTORY.md` (T-ids cross-walked, not blindly trusted as done), package HEAD at acceptance `64a9eb2` / `2.0.1a1`.

---

## 0. One-sentence scope

**Tag `v3.0.0` ships installable measurement-selection infrastructure + synthetic proofs that make the position paper’s workflow executable and make a Tao-style cultural-prompting evaluation *runnable under open-weight policy* — not the paper’s headline empirical numbers and not Tao’s published point estimates.**

---

## 1. Non-negotiable framing

### 1.1 What v3.0.0 is

| Ships at tag | Does **not** ship at tag |
|---|---|
| Holdout machinery (units-split core + restriction `stage`) | Augusto-authored empirical network / θ / holdout countries |
| Evaluators `corr_zero`, `monotone_rank` | Real Joint IVS microdata run / paper-lock numbers |
| Betas `diff_means`, `map_distance` (+ loadings IO, no PCA fit) | DPO adapters / proprietary-API scoring (Gate A D5/D6) |
| Additive coverage / uncertainty-band layer (D1) | Coverage *theorem* or sharp PI |
| Synthetic battery v3 + allow-listed proof summary | H5 n=35 as headline evidence (stays historical) |
| IVS/Tao **harness scaffold** in `evals/` + verifier on **synthetic** IVS-shaped freeze | “We reproduced Tao et al. table X with model Y” |
| Docs/protocol amendment: baseline → 3.0.0; infra vs evidence split | Silent freeze-preimage changes |

### 1.2 “Replicate Tao” language (anti-overclaim)

**Allowed:** same evaluation *setup* — Joint EVS/WVS item space (verified codes), frozen human IW loadings (pinned artifact), country-level units, open-weight prompt baselines, holdout on unseen countries, leakage/process audit in harness, engine admissibility + \(\Theta^*\).

**Forbidden in tag claims:** exact reproduction of Tao’s published numbers with different models; “adapters beat prompting” as a designed result; PCA fit inside the engine; country-blindness as something IDENTIFY proves.

### 1.3 Synthetic-first control plane

Every engine work package merges only when:

1. Oracle DGP with **labels outside IDENTIFY**  
2. Focused tests RED → GREEN (AGENTS.md TDD)  
3. Cold rerun bit-stability on freeze core  
4. FA=0 / empty-honesty paths as applicable  
5. Full battery slice for that feature green  
6. `ruff` + `mypy strict` + `pytest -q`  
7. No `docs/13` empirical claim from synthetic runs  

No empirical path, no IVS microdata, no LLM client in `src/` (AST lock stays green).

### 1.4 Grade → WP map (audit layers B or worse only)

| Audit layer | Grade | Finding | WP | At v3.0.0 |
|---|---|---|---|---|
| Holdout / falsification | F | F1 / C13 | **WP-H** | **SHIP** machinery + synth proof |
| Restriction vocabulary | C+ | F3 / C10–C12 | **WP-R** | **SHIP** `corr_zero`, `monotone_rank`; **DEFER** `stability` |
| Estimand registry | B− | F3 / C15–C16 | **WP-B** | **SHIP** `diff_means`, `map_distance` |
| Inference honesty | C | F4 / C19 | **WP-I** | **SHIP** bounded D1 coverage layer; **DEFER** theory paper |
| Benchmark kit | D+ | F5 / C22 | **WP-K** | **SHIP** synth common-benchmark + verifiers + `run_many` profiles |
| Headline empirical demo | D | F2 / C23 | **WP-E** | **SHIP infra only**; real IVS run = **Gate B post-tag** |

A-grade layers (spine, freeze spirit, empty-\(M^*\), packaging) are touch-only for docs/compat — no redesign.

### 1.5 Inventory cross-walk (Rev 2 T-ids → Rev 3)

| Rev 3 WP | Primary T-ids (Rev 2) | Note |
|---|---|---|
| P0 plan freeze | T04/T05 (already signed Gate A) | Re-confirm; no re-litigate D1–D8 |
| P1 synth v3 | (new scenarios; battery version bump) | Not fully specified in T-list — **new** |
| WP-R | T12, T13, T14 | T14 defer default |
| WP-B | T26 (`map_distance`); `diff_means` was schema-only gap | `diff_means` not a named T — **added from audit** |
| WP-H | T09, T10, T11, T23 (units-split) | D7: units-split = paper core |
| WP-I | T06, T07, T08, T28 | T29 MTMM = optional diagnostic if time |
| WP-K / WP-E infra | T21 scaffold, T22, T30, T32 partial, T33 | Real T25 run **out of tag** |
| Release | T17–T20, T24 mechanical | Gate C = Augusto |

**Do not treat T06+ as done.** Source audit (2026-08-08): no holdout/stage/coverage/`corr_zero`/`map_distance` in `src/`.

### 1.6 Governing locks (unchanged)

- SCORE → RESTRICT → IDENTIFY → REPORT; score-agnostic; no LLM in engine  
- \([L,U] = \min/\max B^*\) on survivors only; empty \(M^*\) = success  
- Bootstrap/θ/δ/coverage **additive**; headline unchanged  
- D1: coverage **not** in freeze preimage  
- D3: `map_distance` changes `beta_hash` **inside major bump**, loadings = pinned artifact, **no fresh PCA**  
- D5/D6: no adapters, no proprietary APIs for paper-reproducible scoring  
- D7: country-level **units-split** = falsifiable core; `stage` = WP machinery  
- Agent may author **oracle** networks for synthetic DGPs only  
- `v0.1` immovable @ `fb62b48…`  
- Tag / push / PyPI = **Augusto-only**, task-specific go  

---

## 2. Phase diagram

```text
P0  Plan freeze + decision card  ──⛔ Augusto sign-off
 │
 ▼
P1  Synthetic control plane v3 (gate specs + failing stubs + DGP designs)
 │
 ├──────────────┬──────────────┐
 ▼              ▼              ▼
P2 WP-R       P3 WP-B        P4 WP-H (critical path / longest pole)
 evaluators    betas          holdout (units-split + stage)
 └──────────────┴──────┬───────┘
                       ▼
                 P5 WP-I coverage (bounded D1; after holdout schema stable)
                       ▼
                 P6 WP-K + WP-E infra (benchmark kit, IVS harness, verifier, tutorial)
                       ▼
                 P7 Integration + RC + docs/16 amendment  ──⛔ Gate C (tag/PyPI)
                       │
                       ▼  (post-tag, not required for v3.0.0)
                 Gate B  Augusto IVS network + real run + paper-lock
```

**Parallelism:** P2 ∥ P3 ∥ P4 after P1. P5 starts when P4 schema/report contract is stable (can draft tests earlier). P6 needs P2–P5 APIs. P7 is serial.

**Estimated engineer effort (order of magnitude, not a commitment):**  
P0 0.5d · P1 1.5–2d · P2 1–1.5d · P3 1–1.5d · P4 2–3d · P5 1.5–2d · P6 2–3d · P7 1–1.5d  
≈ **11–15 engineer-days** wall-clock shorter if P2/P3/P4 parallel.  
**Human latency:** decision card (now); Gate C release; Gate B post-tag (long pole for *paper numbers*, not for the tag).

---

## 3. Phases (scope · order · TDD · verification · exit)

### P0 — Plan freeze + semantics alignment (docs only)

**Scope**

- Land this file as sprint authority.  
- Pointer in `reports/DEVELOPMENT_PLAN.md` header → “superseded for execution by Rev 3”.  
- Optional: thin `docs/12` entry “Rev 3 draft under review” **only after** Augusto accepts the decision card (avoid log noise).  
- Freeze decision card answers into the plan (append “Accepted YYYY-MM-DD”).

**Order:** write → user sign-off → (optional) docs-only commit. **No `src/`.**

**Exit**

- [ ] Decision card returned (defaults or overrides)  
- [ ] Explicit **engine go** for P1 (and whether P2/P4 may start immediately after P1 green)  
- [ ] Confirmed: v3.0.0 = infrastructure tag; Gate B post-tag  

---

### P1 — Synthetic control plane v3 (merge gate for all features)

**Scope — lock designs before feature code**

Bump battery identity to e.g. `BATTERY_VERSION = "v3_0_package_synth"`. Keep existing scenarios (`oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`) as regression. **Add** oracle scenarios (labels outside IDENTIFY):

| Scenario id | Purpose | Designed truth |
|---|---|---|
| `holdout_valid` | Units-split honesty | Train-selected valids pass holdout \(R_H\) / holdout units |
| `holdout_invalid_test` | Falsification | Measure passes \(R_S\) on train, fails holdout by construction |
| `discriminant_mtmm` | `corr_zero` | High corr with convergent V; \|corr\| with discriminant V above θ → reject |
| `monotone_cont` | `monotone_rank` | Measure monotone in continuous V |
| `diff_means_shift` | `diff_means` β | Known group mean gap |
| `map_distance_2d` | `map_distance` β | Known 2D coords + pinned fake loadings; distance goldens |
| `coverage_boundary` | WP-I | Measure near slack boundary; empty-rate / band payload structure |

**Gate definitions (v3 battery)** — in addition to H1a/H1b/H3/H4:

| Gate | Rule |
|---|---|
| `H_holdout_valid` | On `holdout_valid`: FA=0; designed valids in robust set; cold match on holdout verdict |
| `H_holdout_reject` | On `holdout_invalid_test`: designed fake fails holdout verdict (finding, exit 0) |
| `H_disc` | Discriminant invalid never in \(M^*\) under `corr_zero` net |
| `H_mono` | Monotone valid retained; anti-monotone rejected |
| `H_beta_dm` | `diff_means` matches hand golden within tol |
| `H_beta_map` | `map_distance` matches hand golden; loadings hash recorded |
| `H_cov_payload` | When bootstrap on: coverage block present; headline = min/max \(B^*\); empty_rate ∈ [0,1] |

**Practical delivery of P1 (avoid framework sprawl)**

1. Short design note in-repo: `reports/synth_v3_gate_spec.md` (tables above + column layouts).  
2. DGP builders + **failing** tests per scenario (RED stubs OK if feature not landed).  
3. Battery runner accepts new scenarios; missing evaluator ⇒ scenario skipped with explicit `gate_notes`, **not** silent pass.  
4. Prefer implementing DGP+test **with** each WP, but **gate IDs and acceptance rules are frozen here** so WPs cannot invent metrics.

**Files (expected):** `src/cvprofiles/synth/{dgp,oracle_r,metrics,battery}.py`, `tests/test_synth_battery.py`, new `tests/test_synth_v3_*.py`, `reports/synth_v3_gate_spec.md`.

**Exit**

- [ ] Gate spec committed  
- [ ] Each WP has a named scenario + gate id  
- [ ] Old battery scenarios still runnable (regression)  
- [ ] No feature claimed green without its gate  

---

### P2 — WP-R Evaluators (`corr_zero`, `monotone_rank`)

**Semantics (Gate A D4 / math_spec §4)**

| Type | Slack (admit if \(\ge -\delta\)) | Params |
|---|---|---|
| `corr_zero` | \(\theta - \lvert\mathrm{Corr}(m,V)\rvert\) | `variable` (or `ref`), `theta` |
| `monotone_rank` | \(\mathrm{sign}\cdot\mathrm{Spearman}(m,V_{\mathrm{cont}}) - \theta\) | `variable`/`ref`, `sign` ∈ {+1,−1}, `theta` |

**TDD order (one commit per evaluator)**

1. Hand-computed golden fixture → RED (“no evaluator”)  
2. Schema `RestrictionType` + param validation  
3. Minimal branch in `identify/slacks.py` (reuse Spearman path from `rank_agree`)  
4. GREEN + migrate unimplemented-example test to remain on `stability`  
5. Battery slice `H_disc` / `H_mono`

**Defer:** `stability` (T14) unless decision card overrides — keep schema-only fail-loud.

**Docs:** METHODOLOGY registry table + gap closure note; USER_GUIDE examples.

**Exit:** evaluators green; FA=0 on oracle discriminant/monotone; battery notes updated; ruff/mypy/pytest green.

---

### P3 — WP-B Betas (`diff_means`, `map_distance`)

**`diff_means`**

- Implement evaluator (type already in schema).  
- Semantics lock in docs/12 **before** code:  
  \(\beta = \mathrm{sign}\cdot(\mathbb{E}[m\mid G{=}1]-\mathbb{E}[m\mid G{=}0])\) (or plain difference if sign default +1); group column from params or roles — **fail loud** if group not binary 0/1.  
- Optional treatment role: **not required** if group is an aux column (prefer aux to avoid roles schema churn unless needed).

**`map_distance` (D3)**

- \(\beta(m) = \lVert \hat{z}(m) - z^{\mathrm{target}} \rVert_2\) in 2D IW-style space.  
- **Loadings:** researcher-supplied pinned file (JSON/YAML); engine multiplies score vector by loadings — **no PCA fit**.  
- PC2′ rescaling is a **data/provenance** concern for empirical lane, not engine magic.  
- `beta_hash` includes loadings content (or loadings hash field in beta params) — document preimage carve-out already signed in `docs/16` §9.  
- Synth: `map_distance_2d` golden.

**Report/CLI:** accept new types; stdout remains pure JSON.

**Exit:** both betas green; `H_beta_*` gates; schema fail-loud for bad loadings shape; import graph unchanged.

---

### P4 — WP-H Holdout (**paper critical path**)

#### 4.1 Restriction-level `stage` (machinery)

- `RestrictionSpec.stage: Literal["select","holdout"] = "select"`.  
- Backward compatible: existing networks all-select.  
- IDENTIFY: admit on \(R_{\mathrm{select}}\) only; compute slacks for all.  
- REPORT three blocks: (a) selection \(M^*_{\mathrm{select}}\) + \([L,U]_{\mathrm{select}}\); (b) holdout slacks for survivors; (c) **holdout verdict** (pass/fail per measure, failing restriction ids) — **findings, not errors**, exit 0.  
- `network_hash` changes when stage fields appear (major bump — OK).

#### 4.2 Units-split composition (D7 paper core)

- Run config / roles extension: explicit `holdout_units: list[unit_id]` **or** boolean column declared in roles (pick one in implementation lock; prefer **explicit list in run config** for freeze clarity).  
- Pipeline:  
  1. Restrict scores to train units → slacks → \(M^*_{\mathrm{select}}\)  
  2. On holdout units only, recompute slacks for same \(R\), same θ/δ → per-measure holdout compliance  
  3. Define sets (names locked):  
     - `M_star_select`  
     - `M_star_holdout` (admissible if evaluated only on holdout units — diagnostic)  
     - `M_star_robust` = intersection (default headline survivors for paper-shaped runs)  
- **Headline range policy (decision card #2; default):**  
  \([L,U]\) from \(\beta\) on \(M^*_{\mathrm{robust}}\).  
  Additive panels: select-only range, holdout-only range.  
  Empty robust set = success (informative).  
- Cold equality includes holdout verdict payload.

#### 4.3 Freeze discipline

- Holdout split spec enters existing freeze **`config`** key (or documented sub-key) so split changes ⇒ `run_id` changes.  
- **No silent new top-level preimage keys** without docs/12 + tests.  
- Coverage settings stay out of preimage (D1).

#### 4.4 TDD

1. RED: stage field ignored/rejected  
2. GREEN schema + back-compat parse  
3. RED: holdout-fail survivors raise today → must become findings  
4. GREEN units-split composition + report blocks  
5. Synth `holdout_valid` + `holdout_invalid_test` + cold H4 on extended core  

**Files:** `schemas/network.py`, `schemas/run.py` or roles, `restrict/`, `identify/pipeline.py`, `pipeline.py`, `report/` + template, `cli.py`, tests, synth.

**Exit:** holdout is merge-blocker for “paper support”; both D7 layers green; HTML panel exists; empty paths render (`format(None)` safe).

---

### P5 — WP-I Coverage (bounded D1 first cut)

**In scope (ship)**

- Module e.g. `inference/coverage.py` (or extend bootstrap with `CoverageResult`).  
- When bootstrap enabled (or `--inference coverage`):  
  - per-side \(\alpha/2\) quantiles over non-empty replicates (default \(\alpha=0.10\))  
  - empty_rate, degenerate counts  
  - boundary attribution: measures with slack margin \(\le \kappa\cdot\mathrm{SE}\) (default \(\kappa=2\)); SE from bootstrap or simple analytic — pick one in docs/12, keep thin  
  - honest label: **“uncertainty band”**, never “CI” / “coverage guarantee”  
  - optional conservative projection cross-check (per-measure envelope) if cheap  
  - optional \(\hat p_m\) admission frequency (T28) if low cost after core  
- Headline \([L,U]\) **unchanged**; band additive.  
- Report JSON: coverage block present when enabled; structured nulls if all-empty.  
- **Excluded from freeze preimage.**

**Out of scope (defer post-v3.0.0 / methods companion)**

- Formal coverage theorem under arbitrary selection coupling  
- m-out-of-n bootstrap as primary  
- Replacing headline with band  

**Synth:** `coverage_boundary` + regression that min/max \(B^*\) identity holds.

**Docs:** METHODOLOGY §5 inference stance rewrite (one honest paragraph).

**Exit:** coverage green; abstract-safe wording; no freeze key creep.

---

### P6 — WP-K Benchmark kit + WP-E Tao/IVS infrastructure

**Without authoring Augusto’s empirical network:**

1. **Versioned synthetic common-benchmark bundle**  
   `evals/benchmarks/measurement_selection_v1/` (name flexible):  
   scores + roles + network (convergent + discriminant + holdout stages) + beta + holdout split + expected gates README.  
   Demonstrates paper Table-2 *discipline*, not a claim.

2. **`evals/ivs_cultural/` harness scaffold (T30 shape)**  
   - Prompt-baseline scoring **stubs** + projection onto pinned loadings  
   - Snapshot pin interface  
   - Leakage/process checklist (protocol flags only; engine does not prove country-blindness)  
   - **No LLM client importable from `src/`**  
   - Real model calls optional later; tag only needs dry-run path that writes synthetic-like scores

3. **`tools/verify_ivs_cultural.py`**  
   Pattern of `verify_h5_trust.py`: strict JSON, FA=0, freeze-core equality, loadings/item-code checks, positive-control gate.  
   **Green on synthetic IVS-shaped frozen run** (5–8 pseudo-countries, 9–10 IW-like items; Y003 disposition = fixture note, not Gate B).

4. **Teaching notebook**  
   Synthetic IVS-shaped walkthrough: four inputs, holdout three-block report, coverage panel, `map_distance`.  
   Wheel-only execute path (`env -u PYTHONPATH`).

5. **`run_many` example manifest**  
   Multi-β or multi-construct profile shape for paper appendix workflows.

6. **Docs**  
   USER_GUIDE holdout + new registry; ARCHITECTURE module map; `docs/18` stays Augusto-owned fields; ROADMAP/MANIFEST point at Rev 3.

**Exit**

- [ ] Verifier exit 0 on synthetic IVS freeze  
- [ ] Import-graph AST still forbids LLM in `src/`  
- [ ] Tutorial executes under wheel  
- [ ] Benchmark README states non-claims  

---

### P7 — Integration, RC, tag prep (Gate C)

1. Full v3 synth battery + optional MC seed list (document seeds; allow-list `reports/summaries/v3_0_package_synth_summary.json`).  
2. Independent audit tool(s) exit 0 on synth proofs.  
3. Docs close-out: METHODOLOGY, ARCHITECTURE, USER_GUIDE, ROADMAP, MANIFEST, README posture.  
4. **`docs/16` dated amendment:** package baseline `3.0.0`; status language: **v3.0.0 = infrastructure release**; IVS empirical box still Gate B; H5 historical.  
5. Atomic version bump `2.0.1a1` → `3.0.0` + golden refresh + CI CLI-smoke literal + all version literals (same-commit discipline).  
6. Local battery: ruff, mypy, pytest, import-graph, wheel-smoke, `v0.1` peel, `git diff --check`.  
7. **STOP for Augusto Gate C:** tag `v3.0.0`, push, PyPI (`UV_PUBLISH_TOKEN` in owner shell only).  
8. Optional post-tag: cold re-verify H5 under 3.0.0 as **regression witness only**.

**Not required for tag:** Joint microdata download completion, Augusto network, live open-weight scoring, paper-lock.

---

## 4. Acceptance checklist — “supports the position paper” at v3.0.0

On the tagged tree, a referee can:

- [ ] Declare \(M, R, \theta, \delta, \beta\) including **discriminant** and **monotone** restrictions  
- [ ] Run **units-split holdout** and read selection / holdout-slacks / verdict blocks  
- [ ] Obtain \(\Theta^*\) as survivors-only \([L,U]\) (robust set policy documented); empty = success  
- [ ] Use `diff_means` and `map_distance` for paper-shaped estimands  
- [ ] See additive bootstrap + **uncertainty band** with empty-rate and boundary flags  
- [ ] Reproduce synthetic gates from allow-listed summary under installed wheel  
- [ ] Follow IVS/Tao **setup** docs (harness, loadings IO, verifier) without LLM-in-engine  
- [ ] Read METHODOLOGY non-claims: no sharp PI; generation upstream; SCA not validated by construction  

---

## 5. Acceptance checklist — “Tao replication infrastructure”

- [ ] Synthetic IVS-shaped scores + frozen fake loadings → full SCORE→REPORT  
- [ ] `map_distance` β against target IW-style point  
- [ ] Holdout countries (pseudo) units-split verdict  
- [ ] Verifier exit 0; item-code list documented (9/10 verified real codes; Y003 fixture-noted)  
- [ ] Harness lives in `evals/ivs_cultural/`; open-weight policy documented  
- [ ] README: “same evaluation setup under open-weight policy,” not “Tao table reproduced”  

---

## 6. Explicit deferrals (still address the audit grade — staged)

| Item | Audit ref | Disposition | Owner |
|---|---|---|---|
| Real IVS / Tao empirical run + paper-lock | F2 / C23 | **Post-tag Gate B** | Augusto |
| Coverage theorem / sharp PI | F4 | **Methods companion / non-claim** | Paper narrative |
| `stability` evaluator | C12 | **Defer** unless card overrides | — |
| MTMM full panel (T29) | F5 polish | **Optional** if time after P5 | Agent |
| DPO / proprietary APIs | D5/D6 | **Closed** | — |
| Fresh PCA loadings fit | D3 | **Not authorized** | — |
| Engine multi-construct joint admissibility | non-goal | **Out** (`run_many` only) | — |
| IRT / sensemakr inside engine | non-goal | **Tutorials only** | — |

Every deferred item is **named**, not silently dropped.

---

## 7. Risk register (sprint-specific)

| # | Risk | Mitigation |
|---|---|---|
| 1 | Tag blocked on Gate B authorship | Rev 3 decoupling; checklist §1.1 |
| 2 | Scope creep full math_spec §2 | Bounded P5 only |
| 3 | Silent freeze-preimage change | Config-key discipline; tests; docs/12 |
| 4 | Headline replaced by band | Hard test: headline == min/max \(B^*\) |
| 5 | LLM leak into `src/` | AST import-graph; harness in `evals/` |
| 6 | Synth gates don’t hit new paths | Scenario-per-WP mandatory |
| 7 | Parallel docs agent drift | Rev 3 is authority; stop on conflict |
| 8 | Overclaim Tao | Anti-overclaim §1.2 in README + docs/18 |
| 9 | `stability` / extra evaluators boil ocean | Defer list |
| 10 | H5 cited as current evidence | docs/16 amendment + demotion |
| 11 | Version literal / golden miss on bump | P7 checklist + CI smoke |
| 12 | Holdout range policy ambiguity | Decision card #2 before P4 code |

---

## 8. Decision card (Augusto — required before P1 code)

| # | Decision | Recommendation | Default if silent |
|---|---|---|---|
| **1** | v3.0.0 vs Gate B | Tag = infra + synth proofs; IVS empirical **post-tag** | **Adopt rec** |
| **2** | Holdout headline range | \(\beta\) on \(M^*_{\mathrm{robust}}=M^*_{\mathrm{select}}\cap M^*_{\mathrm{holdout}}\); select/holdout-only ranges additive | **Adopt rec** |
| **3** | Holdout split in freeze | Split spec inside existing `config` preimage key | **Adopt rec** |
| **4** | `stability` evaluator | Defer (schema-only) | **Defer** |
| **5** | Coverage strength | Mandatory uncertainty band + empty_rate + boundary flags; **no CI language** | **Adopt rec** |
| **6** | Tao models | Open-weight prompts only; no DPO/proprietary (Gate A) | **Gate A default** |
| **7** | `diff_means` in v3.0.0 | **Ship** (audit B− registry; low cost) | **Ship** |
| **8** | MTMM panel (T29) | Optional after P5; not tag-blocking | **Optional** |
| **9** | First engine go | After card: **P1**, then **P4 holdout + P2 evaluators** on critical path | **Wait for explicit “go P1”** |
| **10** | Commit this plan now | Docs-only commit of Rev 3 + pointer | **Ask** (yes recommended) |
| **11** | Push / tag / PyPI | Never without task-specific go | **No** |

### Sign-off block

```text
Accepted:  [x] yes  (all recommendations)
Overrides: none
Engine go: [x] P1–P5 only (synthetic-first; docs at end of P5)
           P6/P7/Gate B empirical and tag deferred
Commit Rev 3: [x] yes
Date / initials: 2026-08-08 / Augusto (chat acceptance)
```

---

## 9. What I will not do until the card returns

- No `src/` edits  
- No version bump  
- No tag / push / PyPI  
- No empirical network authorship  
- No treating Rev 2 inventory rows as implemented  

---

## 10. Immediate next step after “go P1”

1. Write `reports/synth_v3_gate_spec.md` (freeze tables in §P1).  
2. Extend synth DGP + RED tests for holdout + discriminant scenarios first (longest pole).  
3. Checkpoint: pytest RED count + gate ids listed — then open P4/P2 implementation commits.

---

## 11. Document control

| Version | Date | Change |
|---|---|---|
| Rev 3 draft | 2026-08-08 | Infrastructure sprint from position-paper audit; synthetic-first; tag≠Gate B |
| Rev 2 | 2026-08-07 | Historical; Gate A planning; IVS redirect — **not execution authority** |

**Authority order when docs conflict during this sprint:**  
`AGENTS.md` locks → `docs/16` amendments → **this Rev 3** → METHODOLOGY/ARCHITECTURE → Rev 2 inventory as cross-walk only.
