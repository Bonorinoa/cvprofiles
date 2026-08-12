# Position Paper v8 — Outline, Figure Plan, and Section Map

**Planning artifact for co-authors.** Review-only; edit choices remain Augusto's.
**Companion:** `reviews/v8_review_notes.md` (claim audit, venue assessment, landmines).
**Grounding:** `docs/16` §11 (flagship = WVS/GPS patience, IVS deferred), `docs/12` D1–D10 (2026-08-10), `evals/wvs_gps_preferences/` (DESIGN.md, README.md), v7 PDF text layer, verified citation bank.

---

## 0. Modularity contract ("v8 should be indexed")

- Each main section is **self-contained**: states its own problem, uses only objects defined in §3.1, and carries its own takeaway. Cross-references are minimal (one pointer, never a dependency).
- **Objects are defined once** (§3.1 notation box) and referenced everywhere else by symbol — no re-derivation in later sections.
- Appendices **mirror main-text sections** (A↔§3, B↔§3.4/§4, C↔§6.3, D↔§6.4, E↔§5.2) so any subsection can be lifted with its appendix intact.
- Sections can be reordered without breaking the argument: §1 and §2 are positioning; §3–§5 are the method; §6–§7 are the envelope. The only hard ordering is inside §3.

---

## 1. Front matter

**Title (keep):** "Measuring What We Mean: Construct Validity When Measures Are Cheap"
**Byline:** Gonzalez-Bonorino · Biriukova · Capra · August 2026 · Position paper v8
**Status box (rewrite):** The package is **released** — cvprofiles 2.5.2 on PyPI (2026-08-09) — and this paper *uses* it; package development is a parallel project. Empirical cells in this version are **specified but not yet run**: the flagship patience application (§5) is gated on frozen inputs + `tools/verify_wvs_gps.py` exit 0 + run decision. Synthetic illustrations (Appendix B) demonstrate the decision rule under known truth. Custom LLM scoring adapters are upstream measurement generators, open-sourced separately, not engine features.

**Significance (≤120 words):** Keep the v7 framing (cheap measures → selection problem → menu discipline), add the operational bridge sentence, name the applied example (patience across GPS/WVS/LLM log-prob measures), and the falsifiable core (held-out countries, random-selection floor).

**Abstract (~250 words):** Update the last third: applied example = patience (time preference), 7-measure menu spanning a validated survey instrument, WVS proxies, a composite, two open-weight LLM log-prob arms (Llama-3.1-8B, Phi-4-mini), and a negative control, evaluated under one common nomological network; downstream target = OLS of patience on log GDP per capita (wbgapi) with robustness to measurement choice; 80/20 country units-split as the falsifiable design.

---

## 2. Main text (target: ≤ 12 pp total, references outside the count)

### §1 Introduction — "When measures become cheap" (2.0 pp)

| Subsection | Content | Reader takeaway |
|---|---|---|
| **1.1 The system's view of knowledge production** | Figure 1 (landscape): social-science knowledge production as a pipeline — hypothesis generation → measurement generation → construct & measure validation → estimation & inference → scientific conclusions; where each toolkit lives; the Theory/Empirically split. | Science is a pipeline; each stage has its own tools; the scarce stage moved when measures became cheap. |
| **1.2 Cheap measurement, invalid constructs** | Baumann et al. (~31% incorrect conclusions under prompt paraphrase); Desai–Card–Jacobs (validation inconsistent in flagship journals); Hall (PolMeth AI use); Kim et al. (correlated LLM errors); Dell–Rambachan ("p-hacking with AI slop" without construct validity). | Abundance without validity is the measured failure mode — this is a real, current problem. |
| **1.3 The menu-selection problem** | C → M → R → M* → B* in words; the object of inference is the *surviving set*, not a favorite measure. | The paper formalizes a selection problem, not a scoring problem. |
| **1.4 Contribution and roadmap** | Three bullets: (i) operational bridge between construct-validity psychometrics and partial-identification econometrics, closing the gap Dell–Rambachan (2026) explicitly named; (ii) a falsifiable selection rule (held-out tests, baseline floor); (iii) a released open implementation + open measurement adapters. One roadmap paragraph. | One paragraph a reviewer can quote back. |
| **1.5 AI as a measurement generator** | Generators (prompts, log-prob elicitation, composites, fine-tuned policies) expand the menu; they do not adjudicate it. Human and AI measures face the same standard. Introduces the patience example teaser. | "Generators expand the menu; they do not adjudicate it" — the paper's spine in one sentence. |

### §2 Literature review — "Three traditions, one missing layer" (2.0 pp)

| Subsection | Content | Reader takeaway |
|---|---|---|
| **2.1 Psychometrics: the nomological network and its heirs** | Cronbach–Meehl (1955); Campbell–Fiske MTMM (convergent/discriminant); Messick (1995); Kane (2013); Borsboom et al. (2004). | Validity = defensibility of interpretation; the theoretical taxonomy exists and is mature. |
| **2.2 Econometrics: from measurement error to partial identification** | Classical/nonclassical ME models; Manski, Molinari, Schennach; **Dell–Rambachan NBER SI 2026** (nomological network as moment inequalities; the explicit call for principled construct-validity methods — cite series title + parts 1 & 4); **Chen–Rambachan–Tamer 2026 near-neighbor contrast** (their restrictions = benchmark-informed error-correlation bounds on a downstream parameter; ours = nomological-network inequalities over the menu, object of inference = M*, selection rule held-out-falsifiable). | The machinery exists; the operational gap is *named* by the most relevant recent work. |
| **2.3 CSS/NLP: from proxy presumption to codebook discipline** | Li et al. ACL 2026 (Proxy Presumption, CVP, Counterfactual Neutralization); Halterman–Keith Codebook LLMs; Licht et al. (elicitation protocols); Bean et al. (benchmark construct validity); Wallach et al. 2025 (evaluation as measurement — one sentence, neighbor only). | Confounder-neutralization tools exist; they validate *measures*, not *menus*. |
| **2.4 The synthesis** | Closing paragraph: no prior work does menu-level validation with a falsifiable selection rule; cvprofiles unifies the three traditions into an integrated, auditable workflow for human surveys and AI-generated proxies. | The contribution sentence, stated exactly once, load-bearing. |

### §3 Methodology — "A menu-level validation framework" (2.5 pp)

*Structure follows the mental DAG: primitives → construct & restrictions → generate measures → validate → falsify → infer.*

| Subsection | Content | Reader takeaway |
|---|---|---|
| **3.1 Primitives and notation (≤ 1 p box)** | C, m: X→ℝ (declared scalar reduction), M, V, R, τ_r, δ, s_r(m), M*, β(m), B*, [L,U], G(D,C); workflow arrow C→M→M*→B*; **Figure 2** (epistemic systems view, polished). | One page of vocabulary the whole paper uses; a clear reference for every symbol. |
| **3.2 Construct definition and identification assumptions** | The construct paragraph (prose, never a column); auxiliaries V; restrictions as moment inequalities E[g_r(m,V;τ_r)] ≥ 0; thresholds as researcher-owned commitments (justified, never estimated, never auto-tuned); maintained assumptions A1–A4 stated once. | Validity restrictions are assumptions with observable content; thresholds are commitments. |
| **3.3 Generating candidate measures** | Menu M; generators as contextual projections (prompt, persona, log-prob elicitation, fine-tuned policy); conventional and AI instruments on equal footing; "compatibility over finite scalarized menus" scope language. | Generators expand the menu; they do not adjudicate it (repeat of §1.5, now formal). |
| **3.4 Validating: from tests to the admissible set** | M*(C;M,R,δ); what passing means (conditional, use-specific); empty set as a finding (rejects the pair (M,R), not the construct); boundary measures as the fragile regime. | Survival is conditional, auditable, and can fail loudly. |
| **3.5 Falsifying: holdout and baselines** | Restriction-stage split R_S/R_H; units split (the empirical core); the holdout claim Eq. (9) (validity-guided selection beats a baseline on unseen validity); pre-data discipline; freeze/run-id as operational preregistration; baselines (random floor, anchor-fit). Compact 3-row table replaces deleted Figure 3. | The selection rule itself can fail — this is the paper's empirical claim, not decoration. |
| **3.6 Valid inference: robust set and uncertainty** | Plug-in range [L,U] = image of β on survivors; uncertainty band (selection uncertainty, honest label — not a CI); empty-replicate rate; boundary attribution (|margin| ≤ κ·SE); admission–endpoint coupling. | Selection uncertainty is reported, not assumed away. |

### §4 The open implementation — "cvprofiles: a released, auditable engine" (0.5 pp)

- State machine SCORE → RESTRICT → IDENTIFY → REPORT; compact registry table (restriction types + β-functionals: corr_min, corr_zero, mean_order, monotone_rank, rank_agree; corr_y, ols_coef, diff_means, map_distance).
- Model-free and score-agnostic; freeze/run-id contract; empty M* is an exit-success finding; CLI stdout is machine-readable JSON.
- **Paper ↔ package decoupling sentence:** the package is released (2.5.2, PyPI 2026-08-09) and used as an instrument here; LLM scoring adapters (Llama-3.1-8B, Phi-4-mini log-prob elicitation) are upstream generators, open-sourced separately, never engine features.
- Reader takeaway: the method is implemented, versioned, auditable, and decoupled from the paper's empirical work.

### §5 Applied example — "Validating patience measures across humans and LLMs" (1.5 pp, placeholder)

| Subsection | Content | Reader takeaway |
|---|---|---|
| **5.1 Construct and observation** | Patience = time preference (Falk et al. 2018 GPS operationalization; β-δ lineage); GPS country + individual frames; WVS Wave 7 items Q13 (thrift), Q14 (determination); wbgapi covariates (log GDP per capita as β outcome; q275_mean education as convergent aux); respondent floor ≥ 30; WVS missing codes −1..−5 masked, never imputed. | Patience is a well-validated construct with a strong instrument — the ideal anchor for a menu test. |
| **5.2 Menu and generators (7 measures)** | m_gps_patience (positive control), m_wvs_q13, m_wvs_q14, m_composite = z(Q13)+z(Q14) (composite-vs-latent lesson), m_prompt_a (Llama-3.1-8B), m_prompt_b (Phi-4-mini 3.8B), m_noise (negative control). LLM arms: basic prompts, **log-prob scoring at temperature 0**, pinned GGUF shas, open-weight only. Custom adapters open-sourced. | Human surveys and LLM log-prob measures enter the same menu and face the same screen. |
| **5.3 Validity network** | conv_edu corr_min(q275_mean) θ=0.20 (Dohmen 2011; Falk 2018); mono_edu monotone_rank(q275_mean, +1) θ=0.15; disc_risk corr_zero(risktaking) θ=0.30. Aux-only by design (no restriction references a menu measure; log_gdp_pc is β-only, never in R). Design alert worth one sentence: the framework caught Q49 (life satisfaction) as a confounded convergent criterion (co-moves with risk, −0.33) before freezing — education is the clean bar. | The network is theory-anchored, pre-data, and itself stress-tested by the framework. |
| **5.4 Holdout and falsifiable core** | Units = countries; fixed-seed 80/20 units-split; conv_edu + disc_risk select-stage, mono_edu holdout-stage (tier-3 moment); baseline = random selection (500 seeded draws, k-grid 1..4). The empirical headline is Eq. (9), not "a generator wins." | The claim is falsifiable: validity-guided selection must beat random selection on held-out countries. |
| **5.5 Downstream target and robust set** | β = ols_coef of measure on log_gdp_pc, control [q275_mean]. Report M*, B*, [L,U], uncertainty band, empty-replicate rate, boundary set. Empty or wide sets are admissible findings. | Measurement-robust development-outcome conclusions: the payoff of the framework. |
| **5.6 Status (placeholder box)** | This section is specified, not executed. Gate: frozen inputs + verify_wvs_gps.py exit 0 + Augusto's run decision (docs/16 §11; docs/12 D10). Nothing claimed yet; the box states exactly what will appear once the run lands. | Honest posture: specified-by-design, gated-by-discipline. |

### §6 Discussion — "What the framework does, does not, and why it matters" (1.5 pp)

| Subsection | Content | Reader takeaway |
|---|---|---|
| **6.1 Honest stylization** | What synthetic illustrations (App B) establish and what they do not; what the patience application will establish if it runs as specified; empty/wide sets as findings. | The paper's evidence posture is explicit and conservative. |
| **6.2 What the framework does not do** | Survivors ≠ construct; menu not exhaustive; restrictions are assumptions with observable content; validity is use-specific; AI agreement ≠ independent validation; the scope sentence: *for latent constructs the framework gates estimation and inference; for directly observable regressors it is (correctly) trivial*. | Scope is a feature, not an apology. |
| **6.3 Evals humans can understand** | The dotta-thread reframe: benchmark families as measurement menus; held-out task families; explicit nomological restrictions R that domain experts can audit. Defensible only via construct validity — never "general model interpretability." Pointers to App C. | The framework's evaluation-design claim is auditable, not mystical. |
| **6.4 Automated social science with human-owned gates** | Manning's causal-system connection; four-layer delegation; Goodharting defense: R, τ_r, M, V, holdout split are human-owned and frozen before the agent sees data; Baumann evidence as the Goodharting-by-paraphrase failure mode; Kirgis/Hullman/Lin caveats. Pointers to App D. | The framework enables agentic loops only if humans own the validity gates; it does not solve Goodharting, it makes it visible. |
| **6.5 Open implementation and community** | Known limitations (registry gaps: stability evaluator schema-only; no learned slacks by design; boundary-coupling theory deferred to companion paper) + a call for contribution: new restriction types, β-functionals, and measurement generators. Package CTA — not a registry/leaderboard (that idea remains out of scope). | Honest boundaries + an invitation to extend the open tool. |

### §7 Conclusion (0.5 pp)

- The five questions (What do we mean? How might we measure it? What should a credible measure do? Which survive? Which conclusions survive with them?) → C → M → M* → B*.
- Closing line (keep): "When measures are cheap, validity becomes the scarce resource."

**Page budget:** front 1.0 + §1 2.0 + §2 2.0 + §3 2.5 + §4 0.5 + §5 1.5 + §6 1.5 + §7 0.5 = **11.5 pp** (references outside the count). Figures: Figure 1 in §1.1, Figure 2 in §3.1.

---

## 3. Figure plan

### Figure 1 (NEW — from the hand-drawn sketch) — "The system's view: social science knowledge production and its toolkits"

**Where:** §1.1. **Purpose:** situate the toolkits the contribution complements/augments; dissolve the confusion among hypothesis generation, measurement generation, construct & measure validation, estimation & inference, hypothesis testing, sensitivity analysis, robustness checks — and show exactly what cvprofiles outputs.

**TikZ structure (epistemic, not UML — no Python module names):**
- **Four lanes left→right**, one per stage: ① Hypothesis generation → ② Measurement generation → ③ Construct & measure validation → ④ Estimation & inference → a final **Scientific conclusions** node.
- Each lane is a stacked trio: *who/what* (humans, AI/LLMs, surveys, sensors), *toolkits* (① research design, causal graphs; ② prompt design, ML/DL, PCA/EFA, survey calibration; ③ MTMM/CFA, nomological network, moment inequalities; ④ econometric models, hypothesis tests), *outputs*.
- **Theory / Empirically braces** as in the sketch: Theory spans ①② (conceptual production), Empirically spans ③④ (empirical adjudication).
- **Highlighted cvprofiles span** over lane ③ with its outputs listed: **M\* (admissible set), B\* (robust result set), [L,U] (range), uncertainty band, empty rate, holdout verdicts, boundary flags**.
- **Activity disambiguation tags** (the sketch's real purpose): *hypothesis testing* = sampling variability of β given m → lane ④; *sensitivity analysis* (θ/δ grids, uncertainty band) → dotted diagnostics under ③④; *robustness checks* (holdout, baselines) → dashed arrows into ③.
- Line grammar: solid = artifact/data flow; dashed = researcher-owned commitments; dotted = diagnostics. ≤ 1 page; small but legible labels.

**Wallach et al. 2025 (ICML):** you're right — the connection was only component count. The sketch is a **systems view**, not a four-level validity taxonomy, and the figure does not need Wallach. If cited at all (optional), it belongs in Appendix C as one of several "evaluation is a measurement problem" precedents.

### Figure 2 (POLISHED — epistemic systems view, who owns what)

**Where:** §3.1. **Answer to your question — yes, the downstream layer is missing, and the "Scientific outputs" label was overloading two different things.** In v7, the validity column contained "Network R,τ,δ + Holdout design M\*,B\* survivors-only range" (one box, colliding) and the outputs column squeezed "Uncertainty band / empty rate, boundary" next to it. B\* is not a validity-layer object; it is the *image of a downstream functional on survivors*. The overlap is structural.

**Polished flow (one box per object, one lane per stage):**
1. **Upstream:** Generators → Menu M (dashed = researcher/generator-owned).
2. **Validity layer:** Network R,τ,δ · Holdout design (dashed = researcher-owned commitments).
3. **Admissible set M\* — a distinct node** (the object of inference; empty set drawn as a valid exit).
4. **Downstream:** β on survivors → B\*, [L,U] (solid = engine compute).
5. **Diagnostics lane (dotted):** uncertainty band (labeled "selection uncertainty," never CI), empty-replicate rate, boundary attribution.
6. **Freeze/run-id pin** between researcher commitments and engine compute — the operational meaning of preregistration.
7. Dashed boxes = researcher- or generator-owned everywhere; the engine computes M\*, B\*, [L,U] + diagnostics and authors nothing.

### Deletions and moves
- **Delete Figure 3** (holdout workflow) → replaced by a 3-row compact table in §3.5.
- **Delete Figure 4** (AI as measurement generator) → content folds into §1.5, §3.3, and §5.2; Figure 1's lane ② covers the visual role.
- **Figure 5** (visual slack profile) → **Appendix B** with the DGP section.

---

## 4. Appendices (carry the weight)

| App | Content | Mirrors |
|---|---|---|
| **A. Formalization and proofs** | Definitions (measurement menu, restriction, admissible set, menu-level validity); maintained assumptions A1–A4; Prop A.1 (consistency of plug-in objects) + proof sketch; Prop A.2 (holdout null/claim); remarks (empty sets, consistency ≠ validity); edge cases (boundary measures, admission–endpoint coupling); notation table. | §3 |
| **B. Synthetic DGPs with cvprofiles code** | DGP A–D closed forms (population tables, hand-verifiable); finite-sample engine check (run_ids, seed, n); **code snippets at every step** (score → restrict → identify → report; CLI + Python API) so readers see the tool and the commands together; Figure 5 slack profile; "what the illustrations show and what they do not." | §3.4–§3.6, §4 |
| **C. Benchmark design as a measurement-menu application** | Benchmark families as menus; held-out task families; contamination/saturation evidence (HAI 2026, verified wording); Truong et al. public-vs-private tradeoffs; Wallach et al. and Bean et al. as neighbors; the "evals humans can understand" claim in full. | §6.3 |
| **D. Validation gates in automated social science** | Four-layer delegation; Manning's causal system; Goodharting failure modes (optimize-against-R, post-hoc R); Kirgis et al., Hullman et al., Lin et al. caveats; the community-registry idea kept out of main text. | §6.4 |
| **E. LLM log-prob measurement protocol** | Prompt templates; model cards (Llama-3.1-8B, Phi-4-mini 3.8B); GGUF pinning + sha; temperature-0 determinism; log-prob → score reduction as a *declared* scalarization; open-weight policy compliance (D6); adapter open-source note. | §5.2 |

---

## 5. v7 → v8 section map (the "indexed" trace)

| v7 | v8 | Note |
|---|---|---|
| §1 Intro | §1 (rewritten) | + Figure 1 landscape; evidence condensed |
| §2 Vocabulary | §3.1 notation box | Compressed to ≤ 1 p |
| §3 What should a valid measure do | §2.1 + §3.2–3.4 | History → lit review; machinery → methodology |
| §4 Can validation be tested | §3.5 | Figure 3 deleted → compact table |
| §5 Which conclusions survive | §3.6 | |
| §6 AI as a measurement generator | §1.5 + §3.3 | Figure 4 deleted; content promoted to intro |
| §7 Synthetic DGPs | Appendix B | + code snippets; Figure 5 moves with it |
| §8 Applied illustrations | §5 (patience, placeholder) | Flagship changed (docs/16 §11) |
| §9 Results | §5.6 status box | Honest gate language |
| §10 Implementation | §4 | Package decoupled/released framing |
| §11 What framework does/does not claim | §6.2 | |
| §12 Human-owned gate | §6.4 | |
| §13 Conclusion | §7 | Keep five-questions close |
| App A–E | App A–E (re-ordered) | E (notation) folds into §3.1 |

---

## 6. Open items for the co-author meeting

1. **§5 status language** — "specified, not executed" placeholder box approved? (Recommended: yes; matches docs/16 §11 gate.)
2. **β lock** — ols_coef on log_gdp_pc with q275_mean control (D5) confirmed as the paper's headline functional?
3. **θ anchors file** — literature anchors for conv_edu/mono_edu/disc_risk (Dohmen 2011; Falk 2018) need `anchors.yaml` entries before freeze.
4. **CRT 2026 contrast** — final wording in §2.2 (draft in `v8_review_notes.md` §0.3).
5. **Wallach 2025** — cite in Appendix C only (optional), not the figure.
6. **Figure 1 TikZ** — build from the sketch, two-pass compile, log-grep for `^!`; watch the reserved-pgfkey pitfall (`out` is a built-in — use `outbox`/`genbox`/`validbox` style names).
7. ~~H5/IVS history~~ **REMOVED by peer decision** — no mention anywhere in the paper. H5/IVS appear in no section, footnote, or appendix.
8. **Page budget sign-off** — 11.5 pp main text; if a section overruns, cut from §6 (Discussion) first, never from §3.

---

## 7. Post-approval delta (2026-08-10, second pass) — real-data results + SCA2 arm

**Source:** `evals/wvs_gps_preferences/` artifacts (run_id `005a05b0…`, package 2.5.2, seed 20260810, split_seed 17, n=41 countries), `docs/12` entries 2026-08-10 (θ re-anchor; pooled K-fold), `pooled_summary.json`.

### 7.1 What the first real-data read shows (verified)

- **Pipeline works end-to-end and is audited:** stage 1 (GPS country + WVS Wave 7 country means + WDI `log_gdp_pc`, respondent floor ≥ 30, missing −1..−5 masked) → stage 2 (real llama.cpp log-prob scoring: **Llama-3.2-1B** + **Phi-4-mini** Q4_K_M, temp 0 — note: D-card said Llama-3.1-8B; the shipped arm is 3.2-1B, paper must state what actually ran) → stage 3 (engine + holdout + bootstrap n_boot=50 + coverage) → stage 4 baselines. Auditor `tools/verify_wvs_gps.py` (G1–G5; empty M\* = exit 0 clean).
- **Two pre-freeze design amendments (docs/12), both paper-relevant:**
  1. `disc_risk` θ **0.30 → 0.35**, re-anchored on verified literature (Falk et al. 2018 Table IV ρ=0.230, n=76 — matches our full sample to the decimal; Hanushek et al. 2022 ρ=0.358; Netspar 0.30 excl. Africa; individual 0.210) after θ=0.30 rejected the positive control on a 0.21-SE knife-edge (|ρ|=0.335). θ=0.30 empty run **retained as motivating diagnostic**, not discarded.
  2. Single 80/20 split → **pooled K-fold (K=5)**: the first hold frame (n=8, all developing) was diagnosed underpowered — pure noise passed every holdout bar; the engine surfaced it, the researcher responded with design (the human-owned gate in action).
- **Headline results:** single-split run — `M*_select = {m_gps_patience}`, `M*_robust = ∅`. Pooled K=5 — gps selected **all 5 folds**, prompt_b **4/5**; held-out compliance gps **1/5**, prompt_b **1/5**; `m_noise` compliant in fold 0, `m_wvs_q13` in fold 1; **`pooled_robust = ∅`**. Slacks: WVS Q13/Q14 negative vs education (conv_edu −0.46/−0.73) and vs log_gdp_pc OLS (−0.17/−0.19); gps +0.30 / +0.40; prompt_b −0.010 (knife-edge) / +0.33; bootstrap p_hat gps 0.68, prompt_b 0.83; empty-replicate rate 6%; boundary flags on gps, prompt_a, prompt_b, noise.

### 7.2 Integration decision (recommended — Augusto to confirm)

**Report the empty set as the section's real-data finding, framed as the framework's falsification machinery working on real data.** Five paper-worthy elements:
1. **Empty M\* as a finding** — the paper's core epistemic claim (§3.4/§6.1) demonstrated with full diagnostics (which restrictions bind, boundary attribution, p_hat, empty-replicate rate).
2. **Threshold-discipline live case** — the θ re-anchor is exactly the "thresholds are researcher-owned, literature-anchored commitments; never post-hoc rescues" doctrine, executed before any frozen number, with the prior run retained.
3. **Holdout-power diagnosis** — noise passing the hold frame was the tell that the test lacked power; the K-fold pooling response is the researcher's judgment. "The tool surfaces the failure; the researcher decides whether the failure is the construct or the test."
4. **Substantive pattern (one careful paragraph)** — WVS thrift/determination items *invert* the patience–education–development association at country level (ecological caveats stated); the validated GPS instrument and the Phi-4-mini log-prob arm co-move with it.
5. **AI arm admission-competitive** (selected 4/5 folds, p_hat 0.83) — the natural bridge to the SCA2 extension.

**Claim boundaries (do not cross):** not "WVS proxies are invalid" (rejects the pair (M,R) at country aggregation); not "prompt_b is valid" (knife-edge margins, 1/5 compliance); no frozen-run language until `verify_wvs_gps.py` exit 0 + run decision; any revised network = new preregistered design (the θ re-anchor is the model), never silent retuning.

### 7.3 SCA2 arm (Augusto decision) — menu 7 → 8

- `m_sca2` joins the menu; the network **stays frozen** (conv_edu / mono_edu / disc_risk). This is "generators expand the menu" demonstrated on paper.
- **Training-pipeline contrast vs. DPO-based cultural-alignment literature** (PALMs arXiv:2608.01458; PLURAL arXiv:2607.08034; Kiet et al. persona disagreement arXiv:2605.10843; cultural fine-tuning cluster): (i) moment-anchored from **aggregate** GPS population moments, not item-level responses; (ii) **country never named** → indirect encoding, population structure must be learned; (iii) the trained policy is **one candidate under the same screen**, not a privileged structural truth; (iv) open-weight, documented adapter, open-sourced; (v) menu-level adjudication means DPO training is not self-validating — the screen can reject it (and has rejected everything so far).
- **Goodharting instance for §6.4:** an adapter could be *trained to pass R*; defenses = holdout-stage restrictions (mono_edu), pre-data freeze, random-selection floor. The K=5 result shows the screen is binding even for the positive control.
- **Where:** §5.2 menu table + new §5.3 subsection "Training pipeline: moment-anchored DPO vs. cultural-alignment DPO" (short; full protocol in Appendix E adapter card). Lit-review §2.3 gains the DPO neighbors as one sentence.

### 7.4 File location (Augusto directive)

- **v8 manuscript: `~/Desktop/Github_Repositories/SCA2_PofW/misc/position_paper/position_paper_v8.tex` / `.pdf`** (canonical SCA2 repo; v3–v7 pattern confirmed there). Not in the cvprofiles repo, not in the SCA2 Hermes project.
- Planning docs (`reviews/*.md`) stay in cvprofiles — review artifacts, not the manuscript.

### 7.5 New open items (replaces the old list where marked)

1. **Decision-log entry for the SCA2 arm** (docs/12 + docs/16 §12 amendment) — required by project governance before the menu changes.
2. **`anchors.yaml` freeze** — `anchors_hash` is still null; θ anchors (Dohmen 2011; Falk 2018; the 0.35 memo) must be pinned before the paper cites them.
3. **docs/13 evidence entry** for the smoke runs (not yet logged) — required before paper-facing.
4. **Frozen K=5 run** — full inputs + `verify_wvs_gps.py` exit 0 + Augusto's run decision; the paper either reports the smoke run as "first read" (recommended) or waits for the frozen run.
5. **Model identity in the paper** — Llama-**3.2-1B** (not 3.1-8B) + Phi-4-mini Q4_K_M, GGUF sha-pinned; the D-card correction must flow into Appendix E.
6. **§5 status language** — "first read on real data with real LLM scores; frozen run gated" — approved?

— Hermes, 2026-08-10 (post-approval delta)
