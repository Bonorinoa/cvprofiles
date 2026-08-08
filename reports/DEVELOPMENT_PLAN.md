# DEVELOPMENT_PLAN — cvprofiles v3.0.0 (paper-driven, phase-gated) — REV 2

**Date:** 2026-08-07 (Rev 2: Augusto redirect absorbed) · **Author:** cvprofiles lead engineer · **Checkpoint target:** Nature/PNAS position paper (valid estimation of latent constructs, cultural applications / SCA2)
**Inputs:** `reports/VERIFIED_TASK_INVENTORY.md` (T01–T33), `reports/FINAL_ENGINEERING_REPORT.md`, `reports/math_spec.md`, `AGENTS.md`, `docs/16`, `docs/17`
**Supersedes:** Rev 1 (2026-08-07) — H5 Trust is no longer the v3 headline; the IVS/Tao cultural-values lane replaces it (T21–T33). This supersession is a record of the user's redirect, not a silent scope change.

**Governing rules (from AGENTS.md + the spine skill):**
- Amendments and semantics locks **precede** implementation. No engine task (T06+) starts before its lock (T04/T05/T26/T27/T31).
- The H5 n=35 run is **historical evidence with demotion pending Gate A (T24/T05e)** — never the v3 demo. **Two distinct synthetic lanes:** the coverage worked example (T08, P2) runs on the existing self-contained mini-fixture with a boundary measure added; the teaching walkthrough (T22, P5a) runs on a synthetic IVS-shaped slice (5–8 pseudo-countries, deterministic DGP, item columns mirroring the 10 Inglehart–Welzel items). Real IVS data only after Gate B's run decision.
- **No empirical network is authored by the engineer** (AGENTS.md:37). IVS network/anchors/θ/δ/β/loadings/stage split/holdout are Augusto-owned (Gate B).
- D1 is **decided** (additive-but-mandatory coverage; **no freeze-preimage change for the coverage layer**); the dated docs/12 entry + docs/16 amendment text are the remaining lock work. **Preimage scope is layer-specific:** D1's no-preimage-change applies to coverage (α, κ, p̂_m are additive); the β-registry extension under T26 (`map_distance`) *does* change `beta_hash` by design, inside the v3 major bump and governed by the same amendment — never silently.
- Paper numbers come only from frozen scores + pinned network + fixed seed + package version + **frozen PCA loadings** (IVS lane). Battery before every commit.

---

## 0. Feedback disposition (2026-08-07, Augusto + Gemini)

| Feedback item | Disposition | Where it lands |
|---|---|---|
| Deprecate H5 Trust demo → IVS/Tao cultural-values lane | **Adopt, gated** | T21, T05(d), T24; docs/17 stays historical |
| Teach me: build inputs, interpret outputs | **Adopt** | T22 (synthetic slice walkthrough, before design authorship) |
| "Adapters beat cultural prompting while hiding country?" | **Gate B hypothesis**, not engine task | T23 holdout + T27 adapter policy |
| Let math guide methodological decisions | **Adopt as convention** | P1: math_spec notes resolve ambiguities before code (T26) |
| Declarative Nomological DSL | **Adopt as sugar** | YAML schema already is the DSL; two-sided interval semantic maps to `corr_zero`+`corr_min` composition |
| PartialIdentificationSolver module | **Push back (rename)** | = existing IDENTIFY state; no new module |
| MTMM matrix generator | **Adopt as diagnostic, gated** | T29 (report/tools diagnostic; not an engine state) |
| IRT engine inside cvprofiles | **Push back — out of scope** | Stays an upstream scoring tutorial; violates score-agnosticism |
| sensemakr bounds integration | **Push back — out of scope** | Orthogonal question; stays a tutorial |
| AdapterRunner/PromptRunner/BenchmarkData | **Gated as upstream harness** | T30 in `evals/`, never `src/` (AST-tested) |
| Probability-weighted admissibility p(m∈M*\|restrictions) | **Adopt — additive layer** | T28 (p̂_m from bootstrap replicates; no preimage change) |
| Empty-set refutation as PNAS framing | **Adopt as paper narrative, gated** | Paper-narrative owned by Augusto; engine already reports ∅ honestly |
| DPO adapter training | **Non-goal reopen — Gate A** | T27 (AGENTS.md "foundation-model training") |
| Proprietary-API scoring | **Non-goal reopen — Gate A** | T31 (AGENTS.md "proprietary APIs") |

---

## 1. Structure at a glance

```
P0 baseline hygiene ──────────────► P1 semantics locks + math + policy ── GATE A (Augusto, 6 decisions + T24 sign-off)
                                        │
                ┌───────────────────────┼───────────────────────┐
                ▼                       ▼                       ▼
          P2 WP1 coverage       P3 WP2 holdout          P4 WP3 evaluators
          + p̂_m + MTMM          (falsifiable core —     (monotone_rank,
          (methods-paper        critical path)          corr_zero)
           inference claim)
                └───────────────────────┼───────────────────────┘
                                        ▼
                                 P5a IVS design + teaching + harness
                                        ▼
                                 P5b IVS run + audit ── GATE B (Augusto)
                                        ▼
                                 P6 v3.0.0 release ── GATE C (Augusto)
```

7 phases (P0–P6, P5 split into P5a/P5b). Three Augusto gates: **Gate A** (6 decisions, end P1), **Gate B** (IVS design + run decision, end P5b), **Gate C** (release decision, end P6).

---

## 2. Phase P0 — Baseline hygiene (agent-executable)

**Scope (inventory):** T01 (docs/17 `rq`→`rl`), T02 (docs/16 baseline re-baseline), T03 (ROADMAP v3 box + manifest wiring, **reserving `docs/18`** for the IVS design doc so the manifest needs no second amendment).
**Order:** T01 → T02 → T03, one commit.
**TDD steps:** docs-only; no RED/GREEN cycle. Verification is grep + battery (factual transcription, not behavior).
**Governance gates:** none requiring Augusto. Append a dated docs/12 row noting the hygiene sweep.
**Verification:** `grep -n 'rq\|rl' docs/17` (no `rq` for rule_of_law); `grep -n '1.1.0a1' docs/16` (baseline == pyproject); doc-map wiring grep (ROADMAP/manifest/docs-README/AGENTS truth table incl. `docs/18`); `git diff --check`; battery.
**Exit criterion:** both doc tensions fixed, v3 box + docs/18 reservation wired, battery green, one commit.

---

## 3. Phase P1 — Semantics locks, math, policy ⛔ GATE A (6 decisions + T24 sign-off)

**Scope (inventory):** T04 (dated docs/12 D1 lock: coverage = additive-but-mandatory; α default 0.10, κ=2; honest "uncertainty band" language; no preimage change), T05 (docs/16 amendment bundle: coverage mandate; holdout stage split; `monotone_rank`/`corr_zero` registry positions; **IVS empirical-box clause superseding H5 as v3 headline; H5 close-out clause; leakage claim boundary — "country not provided in the evaluation protocol" is a process claim the engine flags but never proves (parallel to `pre_data` anchors)**; explicit non-authorizations), T26 (β-functional choice: `map_distance` vs per-axis corr — **frozen loadings provenance also Augusto's call**: reuse Tao's published loadings incl. PC2′ = 1.61·PC2 − 0.01 rescaling verbatim, or fresh fit; a fresh empirical fit is an empirical modeling claim), T27 (adapter-training non-goal reopen), T31 (proprietary-API non-goal reopen, joint with T27), T24 (H5 re-grade sign-off — approve at Gate A; **docs/13 re-grade executed immediately after Gate A; full mechanical reversal in P6**).
**Order:** draft all texts in one docs commit → **stop for Augusto**.
**TDD steps:** n/a (governance text). Quality gate: every amendment claim traceable to math_spec §2c/§3/§4; "silence is not consent" vocabulary; non-authorizations listed.
**Governance gates:** **Gate A — Augusto approves the amendment bundle + dated docs/12 entries.** The 6 decisions are: (1) coverage mandate text, (2) IVS empirical-box + H5 close-out clause, (3) `map_distance` β-functional + loadings provenance, (4) `monotone_rank`/`corr_zero` registry positions, (5) adapter-training reopen, (6) proprietary-API policy. **Default posture — open-weight prompt-based baselines are already permitted under AGENTS.md; only DPO adapters (5) and proprietary APIs (6) need dated reopens. Silence on (5)/(6) ⇒ no adapters, no proprietary APIs — the harness runs open-weight local models.** (docs/16 "silence is not consent" rule working correctly: non-goals persist by default under AGENTS.md.)

**Gate A split proposal (recommended to cut human latency):** the 6 decisions are not equal in blocking power. **A1-blocking** (approve first): (1) coverage text, (2) IVS/H5 clause, (4) registry positions — these unblock P2–P4 engine work. **A2-parallel** (can follow): (3) loadings provenance, (5) adapter reopen, (6) API policy — needed only by P5a/P5b. **Implementation as two dated amendments (§8-pattern), not a partial bundle:** amendment #1 carries A1; amendment #2 carries A2. Two self-contained dated entries preserve the "silence is not consent" pattern — a single partially-approved bundle creates exactly the ambiguity docs/16 exists to kill. This is a proposal, not a lock — the plan's default remains a single Gate A bundle unless Augusto picks the split.
**Verification:** amendment dated; docs/16 status consistent; `git diff --check`; battery.
**Exit criterion:** Gate A signed. **No engine code starts before this.** Long-lead data acquisition (T32) may start in parallel — it needs no lock.

---

## 4. Phase P2 — WP1 coupled inference layer + additive layers (parallel)

**Scope (inventory):** T06 (coverage core), T07 (pipeline/CLI/REPORT wiring), T08 (worked example on the **existing self-contained mini-fixture** `reports/runs/v1_1_package_synth/fixture/scores.csv` + `network.yaml` with a boundary measure added — no artifact dependency on P5a's T22 slice; H5 n=35 coverage numbers are regression/illustrative only), T28 (p̂_m per-measure admission probability), T29 (MTMM trait×method panel, **dummy outputs only until Gate B's run decision** — the panel cannot become a de-facto empirical claim pre-run).
**Order:** T06 → T07 → T08; T28/T29 after (independent, same phase).
**TDD steps (per AGENTS.md RED→GREEN):**
1. Fixture: small synthetic DGP with a measure **exactly at the δ-boundary** (math_spec §2d). RED test: `CoverageResult` missing → observe RED.
2. Implement minimal `coverage.py`: per-side quantiles at α/2 over non-empty replicates; Bonferroni-joint labeling; empty-replicate rate; boundary attribution (margin ≤ κ·SE, κ=2); conservative-projection cross-check.
3. GREEN on: band contains truth at nominal rate in a small MC; empty-rate counting exact (nonempty + empty + degenerate = n_boot); determinism under fixed seed; all-empty ⇒ band null + note.
4. T28: p̂_m = fraction of replicates where m ∈ M*; denominator = non-empty (matches band); null band ⇒ p̂_m null + note; descriptive, not a coverage statement.
5. T29: MTMM panel via `tools/mtmm.py` (2 traits × 2 methods fixture; empty M* ⇒ "no admissible measures" string, exit 0) — **additive report diagnostic, no engine state change**.
6. Wiring tests RED first: CLI `--inference coverage --alpha 0.1`; JSON stdout pure machine JSON; empty-M\* exit 0; HTML/JSON Coverage section renders (guard `format(None)` on null band).
7. Full battery + commit.
**Governance gates:** docs/12 dated entry recording shipped semantics (α, κ, Bonferroni reading, p̂_m, MTMM scope); METHODOLOGY §5 inference-stance update (T17 partial — do the stance prose here so docs and code move together).
**Verification:** ruff, mypy strict, pytest (new coverage/p̂_m/MTMM tests + full suite), `git diff --check`, `v0.1` peel; determinism witness.
**Exit criterion:** coverage core + wiring + worked example (T06/T07/T08) green, worked example on the self-contained mini-fixture documented in docs/13 as **directional, not paper evidence**. T28/T29 are **parallel** work with a "merge before P6" constraint — they do not block the P2 gate.

---

## 5. Phase P3 — WP2 holdout-restriction workflow (critical path)

**Scope (inventory):** T09 (schema `stage: select|holdout`), T10 (pipeline: admit on R_select; three-block REPORT; holdout verdict as named findings), T11 (METHODOLOGY/USER_GUIDE/docs-12).
**Order:** T09 → T10 → T11.
**TDD steps:**
1. RED: network schema rejects/ignores `stage` today — write a parse test asserting `stage` field with enum `select|holdout`, default `select`; observe failure.
2. Schema GREEN (backward compatible: existing networks all-select behave identically; `network_hash` changes by design inside the v3 major bump — documented in docs/12).
3. RED: pipeline test — survivors that fail a holdout restriction are **reported, not raised**; empty R_select ⇒ exit 0. Observe RED.
4. GREEN: bind both stages at RESTRICT; IDENTIFY computes all slacks but admits on R_select only; REPORT emits selection block, holdout-slacks block, holdout-verdict block.
5. Full battery + commit.
**Governance gates:** docs/16 amendment clause already approved in T05(b); docs/12 dated entry for shipped stage semantics; METHODOLOGY registry/notation updated (T11).
**Verification:** battery; backward-compat witness (old network YAML parses identically); holdout-failure path exits 0 and names failing restriction + slack; `git diff --check`.
**Exit criterion:** holdout workflow green, documented, battery green.

---

## 6. Phase P4 — WP3 evaluators (`monotone_rank`, `corr_zero`)

**Scope (inventory):** T12 (`monotone_rank`), T13 (`corr_zero`), T14 (`stability` decision).
**Order:** T12 → T13 → T14 (decision only).
**TDD steps (per-evaluator recipe, one commit each):**
1. Semantics lock already in T05(c) (Gate A). Write hand-computed-golden fixture first (monotone_rank: sign·Spearman(m,V_cont)−θ; corr_zero: θ−|Corr(m,V)|, two-sided).
2. RED: schema + evaluator tests fail ("no evaluator in the v2.0 registry" fail-loud path — migrate the unimplemented-example test to `stability` if it was the example).
3. GREEN: minimal evaluator branch in slacks.py + schema entry + param validation. Reuse the rank_agree Spearman path (pandas `Series.rank(method='average')`, no scipy).
4. Measure actual slack values with an independent one-liner before trusting hand goldens (rank direction/tie conventions are the classic error).
5. Full battery + commit per evaluator.
**Governance gates:** T14 — record the `stability` decision in docs/12 (ship split-half **only** if the paper's evidence profile demands a reliability surface; otherwise keep schema-only fail-loud). Registry table in METHODOLOGY updated.
**Verification:** battery; registry fail-loud test still green (points at `stability`); hand goldens verified; `git diff --check`.
**Exit criterion:** both evaluators green with fixtures + goldens; `stability` decision recorded.

---

## 7. Phase P5a — WP4a IVS design + teaching + harness

**Scope (inventory):** T32 (data acquisition — **starts at P1, long-lead**), T22 (teaching walkthrough), T21 (design authorship), T30 (upstream harness).
**Order (explicit):** T22 → T21 → T30. The walkthrough (T22) informs the network design (T21); both precede the harness (T30).
**TDD steps:** n/a for authorship. Engine-side: schema smoke (run the pinned roles/network/β on a synthetic scores frame first — retires schema risk before any real-data run); verifier re-run; freeze-core equality across two cold runs.
**Teaching lane (T22):** worked notebook on a **synthetic IVS-shaped slice** — 5–8 pseudo-countries, deterministic DGP, item columns mirroring the 10 Inglehart–Welzel items (**PROVISIONAL codes from Tao et al. §4.1: A008, A165, E018, E025, F063, F118, F120, G006, Y002, Y003 — pending dictionary verification against the actual Joint file at T32/T21; the Joint file uses the Common EVS/WVS Dictionary and may renumber vs WVS7 codes, so the synthetic schema follows the T21-verified codes**), no real-data dependency (real IVS data only after Gate B's run decision). Teaches: authoring the four inputs (scores/roles, network with `stage`, β, anchors), running the CLI, reading the three-block report (selection / holdout slacks / holdout verdict), reading the coverage band + boundary set. Published tutorial re-run on the frozen lane post-T25 is illustrative only.
**Design (T21):** Augusto authors scores/menu from IVS (Joint EVS/WVS 2017–2022 v5.0, 92 countries = 36 EVS + 66 WVS; WVS7 read-authorized in SCA2 folder; Joint file free/no registration, standalone EVS ZA7500 is GESIS-registration-gated), Inglehart–Welzel axes as target (varimax PCA of the 10 canonical items, **human loadings frozen** — provenance per T26), network, θ, δ, β, stage split, holdout countries. Agent scaffolds: design-doc template, schema smoke, data-acquisition runbook.
**Harness (T30):** model calls, prompt templates, projection on frozen loadings; DPO adapter stub ONLY if T27 reopens. Lives in `evals/ivs_cultural/`; **no LLM client in src/ import graph** (AST-tested). Exit includes **leakage audit** (prompt-template audit enforcing the country-blind protocol flag **and, for any T27-reopened adapter path, a training-corpus country-marker check — orthography/dialect carry country signals even when the prompt never names the country**) and **model-snapshot pinning** so the run reproduces even if upstream weights/APIs change.
**Governance gates:** T30 starts only after T27/T31 decision; T21 is Augusto-authored; T22 is agent-executable post-Gate A.
**Verification:** schema smoke on dummy projected scores; `src/` import-graph still LLM-free (AST test); T30 leakage audit + snapshot pinning; battery.
**Exit criterion:** teaching notebook reproducible under wheel; design locked + transcription audited; harness scaffold green with leakage audit + snapshot pinning; import-graph lock intact.

---

## 8. Phase P5b — WP4b IVS run + audit + paper lock ⛔ GATE B

**Scope (inventory):** T23 (holdout applied: same frozen network + same β; unseen-country holdout verdict — the paper's falsifiable core), T33 (IVS independent auditor), T25 (run + audit + paper-lock checkpoint).
**Order:** T23 → T33 → T25.
**TDD steps:** n/a for run. Engine-side: schema smoke; verifier re-run; freeze-core equality across two cold runs.
**Governance gates:** **Gate B — Augusto authors/pins the IVS network, anchors, θ, δ, loadings, stage split, and holdout countries** (AGENTS.md:37; one-off delegation possible but never silent authorship). Dated docs/16 amendment opening the box **for this designated IVS evaluation only** + docs/18 status `LOCKED AS IVS DESIGN; run gated`. Augusto's explicit run/go decision after audit exit 0.
**Verification:** `tools/verify_ivs_cultural.py` (T33) exit 0 (strict JSON; FA=0; freeze core; provenance incl. loadings + model-family policy; positive-control gate: known-valid items admissible; loadings/item-code dictionary verification: the 10 IW codes vs the actual Joint file — hard Gate B exit item); battery; both proof verifiers exit 0; `git diff --check`; `v0.1` peel.
**Exit criterion:** audit exit 0 + **Augusto's run decision**; evidence summary allow-listed; docs/13 row written **only after** audit (mirroring the n=35 → paper-lock flow, docs/16:133).

---

## 9. Phase P6 — v3.0.0 release ⛔ GATE C

**Scope (inventory):** T17 (docs close-out), T18 (v3 gate battery), T19 (atomic bump + golden refresh), T24 (H5 close-out — **docs/13 re-grade executed right after Gate A; this phase is the full mechanical reversal + battery**), T20 (release decision).
**Order:** T24 (mechanical) → T17 → T18 → T19 → **stop for Augusto** → T20 (tag/PyPI by Augusto).
**TDD steps:** T19 is mechanical — bump checklist (pyproject, `__init__`, uv.lock, test literals incl. bad-input `package_version=`, CI CLI-smoke literal, README/AGENTS current-posture lines, manifest `dev_version`); golden refresh in the **same commit**; report the new golden `run_id`. Historical proof artifacts and their verifiers keep the generation version.
**Governance gates:** **Gate C — Augusto's explicit release decision; Augusto executes the PyPI upload** (token never enters the agent session; `uv publish --dry-run` first). Tag/push are separate explicit decisions.
**Verification:** full v3 gate battery — ruff, mypy strict, pytest (≥222 + new), both proof verifiers exit 0, `git diff --check`, `v0.1` peel, import-graph, wheel build + fresh-venv wheel smoke (`env -u PYTHONPATH`), tutorial/replication notebook re-run under the installed wheel. Post-publish: PyPI JSON API + local-vs-PyPI sha256 + fresh-venv `pip install cvprofiles==3.0.0` reproduction.
**Exit criterion:** v3.0.0 published and independently verified; docs/12 + docs/13 + CHANGELOG current.

---

## 10. Critical-path view (what blocks the paper's headline evidence)

The paper's headline evidence = the IVS run's admissible set, holdout verdict, construct-identified range, and cultural-map placement **with the inference claim attached** (abstract: "inference that remains valid despite the data-dependent screening step"; falsifiable core: "selection guided by construct validity predicts held-out validity evidence").

```
BLOCKING (longest chain):   P0 → P1 (Gate A: 6 decisions + T24 sign-off) → max(P3 holdout, P4 evaluators) → P5a (T22 teaching → T21 design → T30 harness) → P5b (T23 holdout + T33 auditor + T25 run + Gate B) → P6 (Gate C)
PARALLEL (merge before P6): P2 (coverage + p̂_m + MTMM) — needed for the inference claim and the worked-example numbers the methods paper reports; P3 and P4 are also parallel to each other given Gate A (both feed P5a)
LONG-LEAD (start at P1):     T32 IVS data acquisition (Joint EVS/WVS v5.0) — runs in parallel, must complete before T25
```

- **P1 is the first blocker:** no engine task starts before the amendment bundle is signed (T04/T05/T26/T27/T31). This is deliberate — the docs/16 contract (docs/16:21 "Silence is not consent") makes any headline-path change without the dated amendment a governance break (Risk 5).
- **The Gate A policy decisions (T27/T31) are the schedule's largest human-latency risk:** the default posture is already permissive — open-weight prompt-based baselines are AGENTS.md-permitted, so **silence on T27/T31 ⇒ no DPO adapters, no proprietary APIs, harness runs open-weight local models**. The reopen decisions are needed only for the stronger experimental arms (adapters; specific frontier-model families). They are *decisions*, not assumptions.
- **P4 (evaluators) and P3 (holdout) are the second blocker, and they run in parallel:** the IVS network uses `monotone_rank` (income gradients) and `corr_zero` (discriminant/MTMM), and the paper's falsifiable core *is* the holdout verdict. Both must land before P5a; neither blocks the other given Gate A. Serializing them (as Rev 1 did) is a scheduling choice, not a dependency — the plan schedules them in parallel.
- **P5a is the third blocker and now includes the harness:** the model-run chain is load-bearing for the headline run — T30's leakage audit + snapshot pinning are its real exit, not just scaffold green.
- **P5b (Gate B) is the dominant human-latency item:** Augusto must author/pin the network, loadings provenance, and positive-control item selection, then grant the run decision after audit. The n=35 precedent (2026-08-04) is the template: design lock → frozen inputs → dev gate → independent audit → run decision → paper-lock checkpoint.
- **P2 (coverage) does not block the empirical run** but is load-bearing for the paper's §2 framework and the methods-paper claim; it must land before P6.

**Estimated critical path:** ~10–14 engineer-days of work across P1→P6 (P3/P4 in parallel compresses the chain vs Rev 1's serialized 12–16; an estimate, not a commitment), plus **three Augusto decision points** (Gate A: 6 decisions; Gate B: network + run; Gate C: release). Human latency dominates: Gate A is the decision cluster (approve quickly and the rest unblocks), Gate B is the long-lead item (network authorship + loadings provenance + run decision), Gate C is the release call. P2 runs fully parallel and adds ~2–3 engineer-days of total work without lengthening the wall-clock chain.

---

## 11. Risk register (top 5, from engineering report §5, annotated with pivot deltas)

| # | Risk | Where it bites | Mitigation (built into this plan) |
|---|---|---|---|
| 1 | **Boundary coupling** — measures near the δ-boundary flip admission across replicates; band widest exactly when most informative | P2/P5b | Mandatory boundary attribution (margin ≤ κ·SE, κ=2) in CoverageResult; band + boundary set reported together (math_spec §2c.4). IVS pivot: n≈92 countries improves precision but per-country model-response error adds noise — report empty rate + boundary set as primary |
| 2 | **Empty M\*** — H5 had 17.5% empty replicates; coverage conditional on non-empty | P2/P5b | Empty-rate is a headline finding, not noise; all-empty ⇒ null band + note; exit 0; P5b reports empty rate + boundary set as primary. IVS pivot: larger menu (10 items × model families) lowers empty-M\* probability but makes the empty-set refutation framing (paper narrative) a real possibility |
| 3 | **Small-n bootstrap** — H5 n≈35; IVS n≈92 improves | P2/P5b | Band secondary; empty rate + boundary set primary; m-out-of-n documented as future work, not shipped. IVS pivot: per-country model-response error (prompt variance, model stochasticity) replaces some of the small-n concern — mitigate with pinned seeds, frozen loadings, snapshot pinning |
| 4 | **Multiple testing across evaluators** — per-restriction pass/fail ≠ hypothesis tests; now multiplied by MTMM + map_distance | P5b/paper | Restrictions are descriptive screens; no family-wise control; docs/16 claims boundary + paper language must say so. MTMM panel is diagnostic, never a gate |
| 5 | **Governance** — headline-path change without dated amendment breaks the docs/16 contract; now 6 decisions at Gate A | All | Amendments first (Gate A, as two dated amendments if split); every semantics change gets a dated docs/12 entry before code; Gate B/C explicit run + release decisions; no tag/PyPI by implication. T27/T31 default: open-weight prompt-based baselines permitted; silence ⇒ no adapters, no proprietary APIs |

**Pivot-specific risks (new in Rev 2):**
| # | Risk | Mitigation |
|---|---|---|
| 6 | **PCA-loadings provenance** — who fits the human varimax loadings (Tao's published incl. PC2′ rescaling vs fresh fit); a fresh empirical fit is an empirical modeling claim | Augusto's decision at Gate A (T26); frozen loadings artifact; transcription audit |
| 7 | **"Replicating Tao et al." trap** — different model families/providers make their numbers unreproducible | Reframe as "same evaluation setup, model families chosen under policy" (T31); paper language says so |
| 8 | **Country-blind leakage** — "country never mentioned" is a process claim the engine cannot verify | Prompt-template audit (T30) + protocol flag; engine enforces flag, never timing/leakage |
| 9 | **Model deprecation / API drift** — proprietary models change; numbers not reproducible | Snapshot pinning (T30); open-weight local models preferred (T31a) |
| 10 | **β-functional preimage discipline** — `map_distance` extends the beta registry; `beta_hash` is in the run_id preimage | T26 amendment text says the registry extension is in-scope for v3 and governed by the freeze rule; no silent preimage change |
| 11 | **Evaluator-fit mismatch (math-first)** — IW axes are PCA axes; `monotone_rank` fits only if the network restricts on a continuous covariate (e.g. self-expression ↑ with GDP pc). Authoring a PCA-axis restriction into `monotone_rank` would be a category error | T26 math note records the fit decision at Gate A; the IVS network (T21) is authored after that note; `corr_zero` covers the discriminant/axis-separation logic the map actually needs |
| 12 | **Adapter-comparison overclaim** — "adapters beat cultural prompting while hiding country" is a falsifiable hypothesis, not a designed result; Tao et al. shows cultural prompting improves most but worsens some countries | Plan frames it as "we measure whether it holds" (T23 holdout on unseen countries); the claim never enters the paper without the run + audit + Gate B paper-lock flow |

---

## 12. The three gates that need Augusto

| Gate | When | What Augusto decides | Blocks |
|---|---|---|---|
| **Gate A** | End of P1 | **6 decisions + the T24 H5 re-grade sign-off:** (1) coverage mandate text (D1), (2) IVS empirical-box + H5 close-out clause, (3) `map_distance` β-functional + loadings provenance, (4) `monotone_rank`/`corr_zero` registry positions, (5) adapter-training reopen (T27), (6) proprietary-API policy (T31). T24 re-grade is a separate sign-off (re-grading docs/13 evidence claims is Augusto's), executed immediately after Gate A; full mechanical reversal in P6. **Split proposal: A1 = decisions (1)(2)(4) → dated amendment #1 (unblocks P2–P4); A2 = (3)(5)(6) → dated amendment #2 (needed by P5a/P5b). Default posture: open-weight prompt-based baselines permitted; silence on (5)/(6) ⇒ no adapters, no proprietary APIs** | All engine work (P2–P4), P5a design/harness |
| **Gate B** | End of P5b | Author/pin the IVS network, anchors, θ, δ, loadings, stage split, holdout countries; grant the run/go decision after independent audit; paper-lock checkpoint | The paper's headline evidence |
| **Gate C** | End of P6 | Release decision: tag v3.0.0 + PyPI upload (Augusto executes; token never in agent session) | Publication |

**Agent-executable without a gate:** P0, P2 (after Gate A), P3 (after Gate A), P4 (after Gate A), P6 docs/battery/bump (up to the release call), T32 data acquisition (starts at P1), T22 teaching walkthrough (after Gate A). The worked-example reruns (T08 on the mini-fixture, T22 on the synthetic IVS-shaped slice) make **no new empirical claims**.

---

## 13. Posture note

`DEVELOPMENT_PLAN.md` schedules **v3.0.0 as the target**; **v2.0.0 is on PyPI** (2026-08-06, tag `v2.0.0` @ `6abb6e4`), dev cycle at `2.0.1a1`. Nothing in this plan implies a release claim.
