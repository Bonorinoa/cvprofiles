# 16 — Paper Protocol Freeze

**Status:** `protocol-v1-synth-provisional` — provisional synthetic-only lock; empirical/paper fields remain open. **§9 amendment (2026-08-07) opens the IVS designated-evaluation box** (run gated at Gate B); H5 Trust re-graded to historical.

**Package baseline:** `cvprofiles==2.5.0`

**Release posture:** `2.0.0` published on PyPI 2026-08-06; `2.5.0` tagged 2026-08-08 as post-P5 infrastructure checkpoint (not PyPI); v3.0.0 plan in progress (Gate A amendment bundle 2026-08-07, §9; Rev 3 P1–P5 engine go closed at `v2.5.0`).

**Owner:** Augusto owns all researcher-authored scientific choices in this document.

## Purpose and status vocabulary

This document is the single paper-facing protocol home. It organizes existing locks and identifies the choices required before paper-relevant evidence is generated. It does not replace the methodology or preregistration drafts.

| Status | Meaning |
|---|---|
| **LOCKED** | Already fixed by project decisions or package contracts; cite the source. |
| **AWAITING AUGUSTO** | Researcher-owned choice; intentionally not filled by the agent. |
| **DEFERRED** | Explicitly outside this freeze or reserved for a later decision. |

**Protocol rule:** A paper-facing lock requires an explicit dated decision-log entry and the response `LOCKED`, or `LOCKED AS PROVISIONAL SYNTHETIC-ONLY PROTOCOL`. Silence is not consent. Post-lock changes require a dated amendment.

## 1. Locked method spine

| Item | Status | Current protocol statement | Source |
|---|---|---|---|
| State machine | **LOCKED** | SCORE → RESTRICT → IDENTIFY → REPORT. | `docs/ARCHITECTURE.md`, `docs/METHODOLOGY.md` |
| Engine posture | **LOCKED** | Score-agnostic and model-free; no LLM in the engine or installable import graph. | `docs/METHODOLOGY.md`, `docs/12` |
| Measurement menu | **LOCKED** | Finite, researcher-supplied menu of score columns; no prompt-space search in the engine. | `docs/METHODOLOGY.md`, `docs/USER_GUIDE.md` |
| Restrictions | **LOCKED** | Researcher-stated nomological restrictions with sample slacks; admit when all restrictions satisfy the declared tolerance. | `docs/METHODOLOGY.md`, `docs/12` |
| Admissible set | **LOCKED** | Canonically, $M^* = \{m \in M: s_r(m) \ge 0 \ \forall r\}$; with the package tolerance policy, admit when $s_r(m) \ge -\delta$, which coincides with the canonical rule at $\delta=0$. | `docs/METHODOLOGY.md`, `src/cvprofiles/identify/pipeline.py` |
| Downstream object | **LOCKED** | $B^* = \{\beta(m):m\in M^*\}$; headline range is $[L,U]=[\min B^*,\max B^*]$ for nonempty $M^*$. | `docs/METHODOLOGY.md`, `docs/12` |
| Rejected measures | **LOCKED** | β values may be reported diagnostically for rejected measures, but rejected measures never enter the headline range. | `docs/METHODOLOGY.md`, `docs/12` |
| Empty set | **LOCKED** | Empty $M^*$ is a valid scientific output: the data and stated theory admit no candidate measure. No automatic θ loosening. | `docs/METHODOLOGY.md`, `docs/12` |
| Freeze identity | **LOCKED** | Paper numbers require frozen scores, pinned network/β, fixed seed, package version, and the documented freeze/run-id contract. | `docs/METHODOLOGY.md`, `docs/12`, freeze contract |

## 2. Shipped inference semantics

These are package semantics, not yet a complete paper interpretation.

| Item | Status | Current package contract | Source |
|---|---|---|---|
| Bootstrap | **LOCKED** | Units-only resampling with replacement; menu fixed; one seeded RNG stream; headline $[L,U]$ unchanged. | `docs/12`, `docs/13` |
| Bootstrap band | **LOCKED** | Pointwise percentile endpoints over non-empty replicates; all-empty gives a null band with an explanatory note; degenerate replicates are counted and excluded. | `docs/12`, `docs/13` |
| θ-grid | **LOCKED** | Diagnostic viewport over declared positive λ values; λ scales threshold magnitudes only; direction/sign and δ are not scaled. | `docs/12`, `docs/13` |
| θ-grid headline | **LOCKED** | No λ is auto-selected; λ=1.0 is the declared headline; the grid is excluded from `run_id`. | `docs/12`, `docs/13` |
| Paper interpretation of inference | **AWAITING AUGUSTO** | Decide whether bootstrap output is appendix-only diagnostics, a conservative uncertainty summary, or another explicitly bounded interpretation. | Q2 in `docs/archive/10_Open_Questions.md` |

## 3. Researcher-owned paper inputs

No values are supplied here by the agent.

| Input | Status | Required decision |
|---|---|---|
| Construct $C$ | **AWAITING AUGUSTO** | One-paragraph construct definition, including the target population and unit of analysis. |
| Unit and universe | **AWAITING AUGUSTO** | Unit index, inclusion/overlap rule, and sample universe. |
| Score matrix | **AWAITING AUGUSTO** | Frozen score file and scoring protocol; source, recipe, polarity, missingness, and leakage checks for every column. |
| Menu $M$ | **AWAITING AUGUSTO** | Candidate measure IDs and the reason each represents a distinct measurement hypothesis. |
| Network $R$ | **AWAITING AUGUSTO** | Restrictions, auxiliaries/anchors, direction, and substantive justification. The empirical network is not agent-authored. |
| Thresholds $\theta$ | **AWAITING AUGUSTO** | Threshold for each restriction and its pre-data substantive anchor. |
| Slack tolerance $\delta$ | **AWAITING AUGUSTO** | Keep $\delta=0$ or choose another value and its sensitivity/reporting policy. |
| Target functional $\beta$ | **AWAITING AUGUSTO** | Keep `corr_y`, add a secondary functional, or reopen the target choice. |
| Paper claims | **AWAITING AUGUSTO** | What the paper will claim about admissibility, ranges, fragility, and downstream estimates. |

## 4. Synthetic evidence protocol — Gate B choices

The existing v1.1 summary is **package evidence**, not automatically the paper Monte Carlo table. It uses the package battery at $n=1000$, seeds `0..4`, four scenarios, $\delta=0$, SCORE policy `none`, and β=`corr_y`. A future protocol table must have its own artifact name, exact settings, parent SHA, and protocol identifier.

| Item | Status | Protocol statement | Source |
|---|---|---|---|
| Evidence scope | **LOCKED PROVISIONAL** | Synthetic-only protocol; H5, empirical construct, empirical score matrix/menu, and empirical $R$ are deferred. | Gate B delegation |
| Scenario set | **LOCKED PROVISIONAL** | `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`. | Existing package battery |
| Sample size | **LOCKED PROVISIONAL** | $n=1000$; SCORE policy `none`. | Existing package battery |
| Seed list | **LOCKED PROVISIONAL** | Battery seeds `0..49`; the shipped `0..4` result remains package smoke evidence, not this protocol table. | Gate B delegation |
| Gate bars | **LOCKED PROVISIONAL** | H1a false-admission and anchor retention, H1b, H3, and H4. H2 is not separate: false admission is the H1a/H2 component. | Existing package gate implementation |
| Synthetic β | **LOCKED PROVISIONAL** | `corr_y`. | Existing package battery |
| Slack tolerance $\delta$ | **LOCKED PROVISIONAL** | $\delta=0$. | Existing package battery |
| Bootstrap posture | **LOCKED PROVISIONAL** | Appendix diagnostic only; not the headline range, sharp PI, or a stronger uncertainty claim. | Claims boundary |
| Bootstrap `n_boot` | **LOCKED PROVISIONAL** | `80` for the fixed inference probe with seed `7`; predeclared and not tuned after results. | Existing v1.1 probe |
| θ-grid | **LOCKED PROVISIONAL** | $\lambda \in \{0.5,1.0,2.0\}$; λ=1.0 is the headline; no auto-selection. | Existing v1.1 probe |

**Provisional synthetic lock:** synthetic-only protocol with the existing four scenarios, $n=1000$, $\delta=0$, SCORE policy `none`, β=`corr_y`, battery seeds `0..49`, H1a/H1b/H3/H4 as gates, H2 folded into the H1a false-admission component, and H1_latent/bootstrap/θ-grid as additive diagnostics. The fixed inference probe uses seed `7`, `n_boot=80`, and λ grid $\{0.5,1.0,2.0\}$. The shipped `0..4` result remains package-level evidence and will not be overwritten.

## 5. Reporting boundary

| Item | Status | Required decision |
|---|---|---|
| Main text | **AWAITING AUGUSTO** | Decide which identification objects and evidence summaries belong in the main paper. |
| Appendix | **AWAITING AUGUSTO** | Decide whether full slacks, rejected-measure reasons, θ surfaces, and bootstrap diagnostics live here. |
| Machine artifacts | **LOCKED** | Preserve JSON/HTML audit artifacts with hashes, run ID, settings, and provenance. | `docs/ARCHITECTURE.md`, `docs/12` |
| LaTeX report | **DEFERRED** | Candidate later polish; not required for the protocol or next evidence table. |

## 6. Explicit deferrals and exclusions

| Item | Status | Boundary |
|---|---|---|
| H5 empirical baseline | **DEFERRED** | Blocked until Augusto chooses the construct, score matrix, baseline, empirical network, θ, δ, and β. | `docs/archive/05_Pre_Registration.md`, `docs/archive/09_MVP_Plan.md` |
| Empirical network authorship | **DEFERRED** | Agent may author oracle networks for synthetic debugging only. | `docs/METHODOLOGY.md`, `docs/USER_GUIDE.md` |
| Sharp partial-identification theory | **DEFERRED** | Optional garnish, not load-bearing for the package claim. | `docs/METHODOLOGY.md` |
| δ-grid implementation | **DEFERRED → v2.0** | Separate engineering decision; current v1.1 θ-grid does not scale δ. Planned as thread (a) of measure discipline (absolute-δ grid, `docs/archive/18`). | `docs/archive/18_Measure_Discipline_Plan.md`, `docs/12` |
| Measure generation / prompt search | **DEFERRED** | Upstream researcher workflow; outside the engine and thesis core. | `docs/METHODOLOGY.md` |
| Tag and PyPI publication | **DEFERRED** | Release-review and Augusto-owned; this protocol draft does not publish. | `docs/archive/15_MVP_Release_Checklist.md`, `docs/12` |
| GUI, SaaS, and heavy infrastructure | **DEFERRED** | Low-ROI until paper protocol and evidence are complete. | `docs/README.md`, `docs/archive/09_MVP_Plan.md` |

## 7. Gate B questionnaire

Please answer the fields below, or approve the bundled provisional option. Answers can be concise; “same as package default” is acceptable where explicitly intended.

1. **Construct / unit / universe:** What construct, unit, population, and overlap rule should the paper-facing protocol use?
2. **Scores / menu:** Which frozen score matrix and menu $M$ are in scope? If empirical inputs are not yet ready, should this remain explicitly synthetic-only?
3. **Empirical network:** Is H5 blocked for now, with no empirical $R$ in this protocol? If not, supply the restrictions and anchors; the agent will not author them.
4. **θ and δ:** What thresholds and tolerance are intended? The package default is $\delta=0$, but that is not a paper lock.
5. **β:** Keep `corr_y`, add a secondary functional, or reopen the target?
6. **Bootstrap interpretation and count:** Appendix diagnostic or stronger uncertainty summary? What predeclared `n_boot` should the evidence table use?
7. **Synthetic battery:** Four current scenarios or an expanded set? Keep $n=1000$? Use seeds `0..4` (package-level) or approve `0..49` (broader table)? Confirm H1a/H1b/H3/H4 gate bars and whether H2 remains separate from H1a.
8. **Reporting boundary:** Main text vs appendix vs machine artifacts.
9. **H5 timing:** Keep the empirical baseline blocked until the construct and network are authored?

## Gate B response

Gate B has been authorized as **`LOCKED AS PROVISIONAL SYNTHETIC-ONLY PROTOCOL`** under delegated synthetic-scope authority. This is not a full paper lock. The empirical construct, unit/universe, score matrix/menu, empirical $R$, paper θ anchors, paper δ interpretation, paper β choice, paper claims, and reporting placement remain **AWAITING AUGUSTO** or **DEFERRED** as marked above.

Phase 3 may proceed only within the locked synthetic box. No empirical/H5 run, engine change, tag, PyPI publication, or push is authorized by this lock.

## 8. Amendment 2026-08-04 — H5 Trust design lock (dated amendment)

**Status update:** for the H5 Trust evaluation only, the researcher-owned fields in §3 are **LOCKED as design** per `docs/17_H5_Trust_Design.md`, approved by Augusto on 2026-08-04 (decision-log entry same date):

- Construct paragraph (approved verbatim), unit/universe (country `iso3`, WVS7 ∩ GPS, n≈40, floor ≥ 200), menu/roles (4 valid WVS facets + 2 designed-invalid), network `R` (gps_trust 0.3 / rule_of_law 0.3 / gini −0.1), θ anchors (pre-data, literature), δ=0, β=`corr_y` on `log_gdp_pc` (outcome not in network), claims boundary (admissibility + range + fragility only).

**What this opens:** the empirical box for this **designated evaluation**. `SCORE`/`RESTRICT`/`IDENTIFY`/`REPORT` runs for the trust design may proceed once (1) frozen scores + manifest built from raw public files, (2) pinned seed + package version, (3) independent audit exit 0, (4) Augusto's run decision.

**Run decision (2026-08-04):** Augusto granted **preliminary paper-facing evidence** approval for the first frozen build (n=35). Headline checkpoint: M\*={m_trust_general, m_trust_in_group}, [L,U]=[0.371,0.624], FA=0, cold H4; diagnostics: θ-grid empties at λ≥1.5, bootstrap band [0.174,0.752] with 17.5% empty replicates. Tracked summary: `reports/summaries/h5_trust_evidence_summary.json`. This is a checkpoint, not a release: final paper lock, tag, PyPI, and push remain Augusto's.

**What it does NOT authorize:** any other H5/empirical run, engine change, tag, PyPI publication, push, or a `docs/13` evidence claim by implication. The provisional synthetic-only protocol and the MC50 table (§4) are unchanged. All other §3 fields remain **AWAITING AUGUSTO** for any future design.

## 9. Amendment 2026-08-07 — v3 Gate A bundle: IVS cultural-values lane, coverage mandate, holdout semantics, evaluator registry, open-weight policy (dated amendment)

**Authority:** Augusto confirmed all seven Gate A decisions plus the T24 H5 re-grade on 2026-08-07 ("address all the tasks in Gate A as you proposed, everything should stay open-weight or easily interpretable"; decision-log entry same date). This amendment opens the empirical box **for the designated IVS cultural-values evaluation** and records the v3 scope locks.

> **Date provenance (2026-08-08, append-only):** the §9 stamp and docs/12 entry use the plan's date convention (`DEVELOPMENT_PLAN` Rev 2 header, 2026-08-07; the Gate A bundle was drafted with the plan). Git-verified execution and commit occurred **2026-08-08** (`b971708`). Execution date governs; no stamp was rewritten.

**D1 — Coverage mandate (additive-but-mandatory).** v3 headline reporting includes the coupled-inference coverage layer: per-side α/2 quantiles over non-empty bootstrap replicates (α default 0.10), Bonferroni-joint labeling, empty-replicate rate as a headline finding, boundary attribution (margin ≤ κ·SE, κ=2), conservative-projection cross-check. **Additive:** headline `[L,U] = min/max B*` unchanged; coverage settings excluded from the freeze preimage; reports use honest "uncertainty band" language. The dated docs/12 entry (2026-08-07) is the remaining lock work, executed with this amendment.

**D2 — IVS cultural-values evaluation is THE v3 empirical direction.** H5 Trust is superseded as the v3 headline. Lane: Tao et al. (2024)-style evaluation on the Joint EVS/WVS 2017–2022 v5.0 (92 countries = 36 EVS + 66 WVS), Inglehart–Welzel axes as target, model-generated scores from the upstream harness projected on **frozen human PCA loadings**. H5 Trust remains a valid historical design (docs/17, status re-graded); its n=35 run is re-graded to **historical/regression witness** (docs/13), not the v3 evidence base. The §3 row "H5 empirical baseline — DEFERRED" is **superseded for the IVS lane** by this amendment. **2026-08-07 correction (append-only):** "92 countries = 36 EVS + 66 WVS" is arithmetic shorthand; the Joint file contains ~102 national surveys (36 EVS + 66 WVS waves, heavily overlapping) covering ~92 unique countries. The unique-country count is verified at T32 against the actual dictionary.

**D3 — β-functional and loadings provenance.** `map_distance` (2D Euclidean distance on the IW cultural map) is approved as a v3 β-registry extension. Loadings provenance: **reuse Tao et al.'s published loadings verbatim**, including the PC2′ = 1.61·PC2 − 0.01 rescaling (**PROVISIONAL — transcribed from the cited paper; to be verified against Tao et al.'s actual text/table at the T21 transcription audit, a hard Gate B exit item**, same treatment as the 10 item codes). **A fresh empirical PCA fit is NOT authorized** (an empirical modeling claim; robustness appendix only if later reopened). **Preimage carve-out (explicit):** the β-registry extension changes `beta_hash` by design inside the v3 major bump; governed by this amendment, never silent.

**D4 — Evaluator registry positions.** `monotone_rank` (slack = sign·Spearman(m, V_cont) − θ) and `corr_zero` (slack = θ − |Corr(m, V)|, two-sided) are approved as v3 registry positions (measurement-theory additions). **Fit note:** the IW axes themselves are PCA axes, not monotone-in-covariate restrictions; `monotone_rank` is used by the IVS lane only if the network restricts on a continuous covariate (e.g. self-expression ↑ with GDP per capita).

**D5 — Adapter training NOT reopened for v3.** The AGENTS.md non-goal (foundation-model training) stands. v3 harness runs **open-weight prompt-based baselines only**; no DPO adapters.

**D6 — Proprietary APIs NOT reopened for v3.** The AGENTS.md non-goal (proprietary APIs for paper-reproducible work) stands. Paper-reproducible scoring uses **open-weight local models only**; no GPT-4o/Claude-class scoring for paper numbers. "Same evaluation setup, model families chosen under this policy" framing; never claims to reproduce their exact numbers with different models.

**D7 — Holdout semantics.** The paper's falsifiable core is the **country-level units-split**: select/admit on train-country scores, verdict on held-out-country scores (same frozen network + same β). The restriction-level `stage: select|holdout` split ships as WP2 machinery (same units; R_select predicts R_holdout compliance). Both are implementable; D7 fixes the core.

**D8 / T24 — H5 re-grade signed.** The n=35 run is re-graded from preliminary paper-facing evidence to **historical/regression witness**; executed in docs/13 (2026-08-07) and docs/17 (status re-grade). §8's run-decision paragraph remains a valid historical record.

**Open-weight policy (affirmative).** All v3 evidence-generating computation uses **open-weight local models and fully interpretable artifacts**. The engine remains score-agnostic and model-free; the model harness lives in `evals/`, never in `src/` (import graph enforced by AST test).

**Leakage claim boundary.** "Country not provided in the evaluation protocol" is a **process claim the engine flags, never proves** (parallel to `pre_data` anchors); enforced by the T30 prompt-template + score-level audit. The 10 Inglehart–Welzel item codes (A008, A165, E018, E025, F063, F118, F120, G006, Y002, Y003) were **PROVISIONAL** pending dictionary verification. **2026-08-08 (T32 dict step, append-only):** Joint Variable Report verifies 9/10; **Y003 is absent from the Joint Common Dictionary** (WVS7-only Autonomy Index). Full microdata still open. Detail and disposition options in `docs/18`. Y003 + PC2′ remain hard Gate B (T21/T33).

**What this opens:** the **IVS designated-evaluation box** under Gate B conditions — frozen scores + pinned network/beta (incl. frozen loadings) + fixed seed + package version, independent audit exit 0, Augusto's run decision.

**What it does NOT authorize:** any other empirical run; fresh PCA fit; proprietary-API scoring; adapter training; engine change; tag; PyPI publication; or push by implication. All §3 fields not listed here remain **AWAITING AUGUSTO** for any future design.

## Provenance rule

`reports/summaries/v1_1_package_synth_summary.json` remains the shipped package-evidence artifact. A future protocol table must use a distinct summary path, record the protocol ID, package version, parent SHA, exact settings, and seed list, and be audited independently before any `docs/13` claim is written.

## References

- `docs/METHODOLOGY.md`
- `docs/USER_GUIDE.md`
- `docs/ARCHITECTURE.md`
- `docs/12_Decision_Engineering_Log.md`
- `docs/13_Evaluations_Log.md`
- `docs/archive/04_Synthetic_DGPs.md`
- `docs/archive/05_Pre_Registration.md`
- `docs/archive/08_Observability_and_Evaluations.md`
- `docs/archive/10_Open_Questions.md`
- `docs/archive/14_Researcher_Input_Guide.md`
- `docs/PROJECT_MANIFEST.md`
- Freeze/run-id contract in the research-methods-package-spine skill
