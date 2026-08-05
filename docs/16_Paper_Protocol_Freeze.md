# 16 — Paper Protocol Freeze

**Status:** `protocol-v1-draft` — Gate B open; not locked for paper claims

**Package baseline:** `cvprofiles==1.1.0a1`

**Release posture:** verified development artifact on `main`; no v1.1 tag or PyPI publication

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
| State machine | **LOCKED** | SCORE → RESTRICT → IDENTIFY → REPORT. | `docs/01`, `docs/02`, `docs/03` |
| Engine posture | **LOCKED** | Score-agnostic and model-free; no LLM in the engine or installable import graph. | `docs/01`, `docs/03`, `docs/12` |
| Measurement menu | **LOCKED** | Finite, researcher-supplied menu of score columns; no prompt-space search in the engine. | `docs/03`, `docs/14` |
| Restrictions | **LOCKED** | Researcher-stated nomological restrictions with sample slacks; admit when all restrictions satisfy the declared tolerance. | `docs/03`, `docs/12` |
| Admissible set | **LOCKED** | Canonically, \(M^* = \{m \in M: s_r(m) \ge 0 \ \forall r\}\); with the package tolerance policy, admit when \(s_r(m) \ge -\delta\), which coincides with the canonical rule at \(\delta=0\). | `docs/03`, `src/cvprofiles/identify/pipeline.py` |
| Downstream object | **LOCKED** | \(B^* = \{\beta(m):m\in M^*\}\); headline range is \([L,U]=[\min B^*,\max B^*]\) for nonempty \(M^*\). | `docs/03`, `docs/12` |
| Rejected measures | **LOCKED** | β values may be reported diagnostically for rejected measures, but rejected measures never enter the headline range. | `docs/03`, `docs/12` |
| Empty set | **LOCKED** | Empty \(M^*\) is a valid scientific output: the data and stated theory admit no candidate measure. No automatic θ loosening. | `docs/03`, `docs/12` |
| Freeze identity | **LOCKED** | Paper numbers require frozen scores, pinned network/β, fixed seed, package version, and the documented freeze/run-id contract. | `docs/03`, `docs/12`, freeze contract |

## 2. Shipped inference semantics

These are package semantics, not yet a complete paper interpretation.

| Item | Status | Current package contract | Source |
|---|---|---|---|
| Bootstrap | **LOCKED** | Units-only resampling with replacement; menu fixed; one seeded RNG stream; headline \([L,U]\) unchanged. | `docs/12`, `docs/13` |
| Bootstrap band | **LOCKED** | Pointwise percentile endpoints over non-empty replicates; all-empty gives a null band with an explanatory note; degenerate replicates are counted and excluded. | `docs/12`, `docs/13` |
| θ-grid | **LOCKED** | Diagnostic viewport over declared positive λ values; λ scales threshold magnitudes only; direction/sign and δ are not scaled. | `docs/12`, `docs/13` |
| θ-grid headline | **LOCKED** | No λ is auto-selected; λ=1.0 is the declared headline; the grid is excluded from `run_id`. | `docs/12`, `docs/13` |
| Paper interpretation of inference | **AWAITING AUGUSTO** | Decide whether bootstrap output is appendix-only diagnostics, a conservative uncertainty summary, or another explicitly bounded interpretation. | Q2 in `docs/10` |

## 3. Researcher-owned paper inputs

No values are supplied here by the agent.

| Input | Status | Required decision |
|---|---|---|
| Construct \(C\) | **AWAITING AUGUSTO** | One-paragraph construct definition, including the target population and unit of analysis. |
| Unit and universe | **AWAITING AUGUSTO** | Unit index, inclusion/overlap rule, and sample universe. |
| Score matrix | **AWAITING AUGUSTO** | Frozen score file and scoring protocol; source, recipe, polarity, missingness, and leakage checks for every column. |
| Menu \(M\) | **AWAITING AUGUSTO** | Candidate measure IDs and the reason each represents a distinct measurement hypothesis. |
| Network \(R\) | **AWAITING AUGUSTO** | Restrictions, auxiliaries/anchors, direction, and substantive justification. The empirical network is not agent-authored. |
| Thresholds \(\theta\) | **AWAITING AUGUSTO** | Threshold for each restriction and its pre-data substantive anchor. |
| Slack tolerance \(\delta\) | **AWAITING AUGUSTO** | Keep \(\delta=0\) or choose another value and its sensitivity/reporting policy. |
| Target functional \(\beta\) | **AWAITING AUGUSTO** | Keep `corr_y`, add a secondary functional, or reopen the target choice. |
| Paper claims | **AWAITING AUGUSTO** | What the paper will claim about admissibility, ranges, fragility, and downstream estimates. |

## 4. Synthetic evidence protocol — Gate B choices

The existing v1.1 summary is **package evidence**, not automatically the paper Monte Carlo table. It uses the package battery at \(n=1000\), seeds `0..4`, four scenarios, \(\delta=0\), SCORE policy `none`, and β=`corr_y`. A future protocol table must have its own artifact name, exact settings, parent SHA, and protocol identifier.

| Item | Status | Decision required |
|---|---|---|
| Evidence scope | **AWAITING AUGUSTO** | Approve a provisional synthetic-only protocol, or specify the broader paper evidence posture. |
| Scenario set | **AWAITING AUGUSTO** | Keep the four implemented scenarios or add `loose_theta`, `wrong_network`, `n_small`, or `point_id`. |
| Sample size | **AWAITING AUGUSTO** | Keep \(n=1000\) or specify finite-sample stress values. |
| Seed list | **AWAITING AUGUSTO** | Keep `0..4` and label it package-level, or approve a broader predeclared list such as `0..49`. |
| Gate bars | **AWAITING AUGUSTO** | Confirm H1a/H1b/H3/H4 bars and whether H2 remains a separately named false-admission gate or is reported as the H1a/H2 false-admission component. |
| Synthetic β | **AWAITING AUGUSTO** | Keep `corr_y` for this table or specify another target. |
| Bootstrap `n_boot` | **AWAITING AUGUSTO** | Specify the replicate count and interpretation; do not choose it after seeing results. |
| θ-grid | **AWAITING AUGUSTO** | Specify whether the existing diagnostic grid is included in the table and which λ values are declared. |

**Current recommendation, not a lock:** provisional synthetic-only protocol with the existing four scenarios, \(n=1000\), \(\delta=0\), β=`corr_y`, H1a/H1b/H3/H4 as gates, H2 reported as the false-admission component unless Augusto keeps it separate, H1_latent/bootstrap/θ-grid as diagnostics, and a seed list explicitly chosen before execution. If `0..4` is retained, call the result package-level evidence rather than a broad Monte Carlo claim. A broader seed list such as `0..49` is preferable only if Augusto accepts the additional scope and runtime.

## 5. Reporting boundary

| Item | Status | Required decision |
|---|---|---|
| Main text | **AWAITING AUGUSTO** | Decide which identification objects and evidence summaries belong in the main paper. |
| Appendix | **AWAITING AUGUSTO** | Decide whether full slacks, rejected-measure reasons, θ surfaces, and bootstrap diagnostics live here. |
| Machine artifacts | **LOCKED** | Preserve JSON/HTML audit artifacts with hashes, run ID, settings, and provenance. | `docs/08`, `docs/12` |
| LaTeX report | **DEFERRED** | Candidate later polish; not required for the protocol or next evidence table. |

## 6. Explicit deferrals and exclusions

| Item | Status | Boundary |
|---|---|---|
| H5 empirical baseline | **DEFERRED** | Blocked until Augusto chooses the construct, score matrix, baseline, empirical network, θ, δ, and β. | `docs/05`, `docs/09` |
| Empirical network authorship | **DEFERRED** | Agent may author oracle networks for synthetic debugging only. | `docs/01`, `docs/03`, `docs/14` |
| Sharp partial-identification theory | **DEFERRED** | Optional garnish, not load-bearing for the package claim. | `docs/03` |
| δ-grid implementation | **DEFERRED** | Separate engineering decision; current v1.1 θ-grid does not scale δ. | `docs/10`, `docs/12` |
| Measure generation / prompt search | **DEFERRED** | Upstream researcher workflow; outside the engine and thesis core. | `docs/01`, `docs/03` |
| New annotation campaign | **DEFERRED** | Hard non-goal unless explicitly reopened. | README / profile scope |
| Tag and PyPI publication | **DEFERRED** | Release-review and Augusto-owned; this protocol draft does not publish. | `docs/15`, `docs/12` |
| GUI, SaaS, and heavy infrastructure | **DEFERRED** | Low-ROI until paper protocol and evidence are complete. | `docs/01`, `docs/09` |

## 7. Gate B questionnaire

Please answer the fields below, or approve the bundled provisional option. Answers can be concise; “same as package default” is acceptable where explicitly intended.

1. **Construct / unit / universe:** What construct, unit, population, and overlap rule should the paper-facing protocol use?
2. **Scores / menu:** Which frozen score matrix and menu \(M\) are in scope? If empirical inputs are not yet ready, should this remain explicitly synthetic-only?
3. **Empirical network:** Is H5 blocked for now, with no empirical \(R\) in this protocol? If not, supply the restrictions and anchors; the agent will not author them.
4. **θ and δ:** What thresholds and tolerance are intended? The package default is \(\delta=0\), but that is not a paper lock.
5. **β:** Keep `corr_y`, add a secondary functional, or reopen the target?
6. **Bootstrap interpretation and count:** Appendix diagnostic or stronger uncertainty summary? What predeclared `n_boot` should the evidence table use?
7. **Synthetic battery:** Four current scenarios or an expanded set? Keep \(n=1000\)? Use seeds `0..4` (package-level) or approve `0..49` (broader table)? Confirm H1a/H1b/H3/H4 gate bars and whether H2 remains separate from H1a.
8. **Reporting boundary:** Main text vs appendix vs machine artifacts.
9. **H5 timing:** Keep the empirical baseline blocked until the construct and network are authored?

## Gate B response

To authorize the next phase, reply with either:

- **`LOCKED`**, after filling the researcher-owned fields; or
- **`LOCKED AS PROVISIONAL SYNTHETIC-ONLY PROTOCOL`**, with the desired synthetic settings stated or the recommendation above explicitly accepted.

No Monte Carlo table will be run before that response.

## Provenance rule

`reports/summaries/v1_1_package_synth_summary.json` remains the shipped package-evidence artifact. A future protocol table must use a distinct summary path, record the protocol ID, package version, parent SHA, exact settings, and seed list, and be audited independently before any `docs/13` claim is written.

## References

- `docs/01_Project_Overview.md`
- `docs/02_System_Architecture.md`
- `docs/03_Methodology.md`
- `docs/04_Synthetic_DGPs.md`
- `docs/05_Pre_Registration.md`
- `docs/08_Observability_and_Evaluations.md`
- `docs/09_MVP_Plan.md`
- `docs/10_Open_Questions.md`
- `docs/12_Decision_Engineering_Log.md`
- `docs/13_Evaluations_Log.md`
- `docs/14_Researcher_Input_Guide.md`
- `docs/15_MVP_Release_Checklist.md`
- `docs/PROJECT_MANIFEST.md`
- Freeze/run-id contract in the research-methods-package-spine skill
