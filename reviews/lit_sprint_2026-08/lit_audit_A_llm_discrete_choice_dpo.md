# Literature Audit A — LLMs as Discrete Choice Models · DPO/Bradley-Terry Lineage · Novelty of Survey-Anchored Synthetic Preferences

All entries verified by live fetch (arXiv API/Crossref), 2026-08-07, unless tagged [UNVERIFIED].

## 1. ANNOTATED BIBLIOGRAPHY

**A. LLMs as discrete choice / random utility models**
- Buchanan & Foster (2026). *The Innate Economic Preferences of Language Models.* arXiv:2607.26288. Shows LM generation rule is isomorphic to the random utility model (RUM) of discrete choice; structurally identifies risk attitudes from internal logits; finds IIA violations. **Anchor citation.**
- Mahajan et al. (2026). *Mind the Gap: How Elicitation Protocols Shape the Stated-Revealed Preference Gap in Language Models.* arXiv:2601.21975. Stated-vs-revealed preference gap across 24 LMs; protocol dependence.
- Wang, Pawlak & Sivakumar (2025). *Can LLMs Simulate Human Responses? Stated Preference Experiments (Heating Choices).* arXiv:2503.10652. LLM respondents in energy SP surveys.
- Song et al. (2025). *Can LLMs Capture Human Risk Preferences? A Cross-Cultural Study.* arXiv:2506.23107.
- Ye & Yoganarasimhan (2026). *Rectification Difficulty and Optimal Sample Allocation in LLM-Augmented Surveys.* arXiv:2604.17267. Econometrics of LLM survey data.
- Lu et al. (2026). *Generative Augmented Inference of LLM-generated Data for Market Research.* arXiv:2604.14575.

**B. DPO / Bradley-Terry lineage**
- Bradley & Terry (1952). *Rank Analysis of Incomplete Block Designs: I. The Method of Paired Comparisons.* Biometrika 39(3/4). DOI:10.1093/biomet/39.3-4.324.
- Rafailov et al. (2023). *Direct Preference Optimization: Your Language Model is Secretly a Reward Model.* arXiv:2305.18290. DPO = closed-form BT-implied reward optimization.
- Azar et al. (2023). *A General Theoretical Paradigm to Understand Learning from Human Preferences* (IPO). arXiv:2310.12036. Analyzes DPO's BT/transitivity assumptions.
- Munos et al. (2023). *Nash Learning from Human Feedback.* arXiv:2312.00886. Generalizes past BT to non-transitive preferences.
- Liu et al. (2025). *A Survey of Direct Preference Optimization.* arXiv:2503.11701. DPO's BT grounding now textbook.
- KTO (2024). arXiv:2402.01306. Pair-free (pointwise) preference learning from binary labels.

**C. Econ applications / simulated agents**
- Horton, Filippas & Manning (2023). *Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?* NBER WP 31122; arXiv:2301.07543.
- Argyle et al. (2023). *Out of One, Many: Using Language Models to Simulate Human Samples.* Political Analysis. DOI:10.1017/pan.2023.2.
- Aher, Arriaga & Kalai (2022/23). *Using LLMs to Simulate Multiple Humans and Replicate Human Subject Studies.* arXiv:2208.10264.
- Manning, Zhu & Horton (2024). *Automated Social Science: Language Models as Scientist and Subjects.* NBER WP 32381; arXiv:2404.11794.
- Lee et al. (2023). *Can LLMs Capture Public Opinion about Global Warming?* arXiv:2311.00217.

**D. Cultural alignment / fine-tuning**
- Li et al. (2024). *CultureLLM: Incorporating Cultural Differences into LLMs.* arXiv:2402.10946. Semantic-data fine-tuning from cultural seeds; no DPO, no survey moments.
- CulturePark (2024). arXiv:2405.15145. Multi-agent cross-cultural dialogue fine-tuning.
- Jung & Kim (2026). *Korean Culture into LLM Alignment: Toward Cultural Coherence.* arXiv:2606.06797. DPO on Korean harm-taxonomy triplets; **not** survey-anchored.
- Agarwal et al. (2026). *PLURAL: A Global Dataset for Value Alignment.* arXiv:2607.08034. IVS survey responses → ~500k synthetic preference triplets (20 countries); training improves country alignment.
- Dey et al. (2026). *PALMs: Multi Construct-Grounded Rationales for Modeling Population Preferences.* arXiv:2608.01458. Per-country preference-tuned models (USA/India/Brazil/France/Italy).
- LKValues (2026). arXiv:2607.20410. Sri Lankan value-alignment data.

**E. Aggregate-preference learning / survey simulation**
- Santurkar et al. (2023). *Whose Opinions Do Language Models Reflect?* arXiv:2303.17548.
- Durmus et al. (2023). *Towards Measuring the Representation of Subjective Global Opinions in LMs.* arXiv:2306.16388. WVS-anchored measurement of opinion alignment.
- Kim, Zhang, Ozdaglar & Parrilo (2025/26). *Beyond RLHF and NLHF: Population-Proportional Alignment.* arXiv:2506.05619. Infers population preference distribution **from** pairwise data (SCA2's direction reversed).
- Ozkan (2026). *Distribution-First Population Simulation: Collapse, Calibration, Recall in Non-WEIRD LLM Persona Modeling.* arXiv:2607.18310. WVS microdata; collapse diagnosis; prompting-level correction, no training.
- Choi et al. (2026). *Beyond the Mean: Three-Axis Fidelity for Aligning LLM-Based Survey Simulators from Small Pilot Data.* arXiv:2606.28963. Fine-tuning on small pilot samples for distributional fidelity.
- Lin et al. (2025). *AlignSurvey: Benchmark for Human Preferences Alignment in Social Surveys.* arXiv:2511.07871.
- Grief-Albert et al. (2026). *Emulate or Estimate? Base vs Post-Trained LMs for Opinion Simulation.* arXiv:2608.03044. Base models emulate, post-trained estimate; Pew data.
- Binz et al. (2026). *Post-training makes LLMs less human-like.* arXiv:2605.07632. RLHF/post-training reduces behavioral alignment.

**F. Synthetic preference data**
- Differentially Private Preference Data Synthesis for LLM Alignment (2026). arXiv:2605.30808. Synthetic-preference methods exist; none survey-anchored.

**Searched, not found:** "Callaway et al. on LLMs as economic agents" (only Brantly Callaway's DiD papers); "What do LLMs know about consumer choice?"; "choice set confounded"; "On the Statistical Properties of DPO" (closest: Azar et al. 2310.12036); "HumanValues" benchmark (empty arXiv queries) [UNVERIFIED].

## 2. VERDICT A — ESTABLISHED. Cite, do not defend.

Yes. The DPO≡Bradley-Terry and LLM-as-discrete-choice readings are now settled enough that the paper needs only a citation paragraph. Supporting works: Rafailov et al. 2023; Bradley & Terry 1952; Azar et al. 2023 (IPO); Munos et al. 2023; Buchanan & Foster 2026 (explicit RUM isomorphism); Liu et al. 2025 (DPO survey); Horton, Filippas & Manning 2023; Argyle et al. 2023; Aher et al. 2022. **Caveat:** 2026 work disputes the interpretation's *reliability* — IIA violations (Buchanan & Foster), elicitation-protocol effects (Mahajan et al. 2026), post-training human-likeness declines (Binz et al. 2026; Grief-Albert et al. 2026). Treat it as a modeling assumption with testable failures, not an empirical fact.

## 3. VERDICT B — NOT YET PUBLISHED IN EXACT FORM, BUT THE CELL IS FILLING FAST

**Not found:** any paper doing aggregate population moments (e.g., GPS z-scores) → synthetic pairwise-choice data → DPO policy, with no individual-level preference labels.

**Three closest priors and precise differences:**

1. **PLURAL** (Agarwal et al., arXiv:2607.08034, 2026-07-09) — survey responses (IVS, 92 countries) → two-stage generation of ~500k synthetic preference *triplets* → training improves country-level cultural alignment. **Differences:** (i) anchors on survey *item responses* and generates scenario content (content-design); SCA2 anchors only on *aggregate moments* and generates pairwise choices to match them (identification design); (ii) one shared dataset, not country-conditioned adapters; (iii) evaluates cultural-profile alignment, not out-of-sample WVS item prediction; (iv) no construct-validity-as-partial-identification framing (cvprofiles).
2. **PALMs** (Dey et al., arXiv:2608.01458, 2026-08-02) — per-country aligned models via preference tuning (5 countries). **Differences:** preferences are latent supervision from LLM-synthesized *psychological-construct rationales*, not survey moments; no moment-matching, no WVS out-of-sample evaluation.
3. **Population-Proportional Alignment** (Kim, Zhang, Ozdaglar & Parrilo, arXiv:2506.05619) — infers the population distribution of evaluator preferences *from pairwise comparison data*, then aligns proportionally (social-choice axioms). **Differences:** identification direction is reversed (pairs → population), no survey anchors, no per-country latent-preference policy from moments.

Adjacent but distinct: Beyond the Mean (Choi et al. 2026 — pilot *individual* data, not moments); KTO (2024 — pair-free but binary human labels, not moments); Durmus et al. 2023 and Santurkar et al. 2023 (measure, never train); Ozkan 2026 (prompting-level correction, no DPO).

**Loud flag:** PLURAL (July 2026) and PALMs (Aug 2026) already occupy the "survey/preference-derived → alignment training for country-specific values" cell. SCA2's defensible remaining novelty is precisely: **moment-level (z-score) anchors instead of item-level triplets; explicit discrete-choice/BT identification of the latent preference policy; country-conditioned adapters; out-of-sample WVS prediction; and construct validity as partial identification.** Gemini's claim (2) is confirmed — but the novelty window is narrow and time-sensitive; move fast.

## 4. [UNVERIFIED] ITEMS
- KTO author list; "HumanValues" benchmark existence; "On the Statistical Properties of DPO" title; NBER page-level metadata (verified via Crossref DOI + arXiv instead); Argyle et al. volume/pages.
