# Literature Map: Validating AI-Based Measures & Benchmarks (2025–2026)
**Prepared 2026-08-09 for a Nature/PNAS position paper: "Measuring What We Mean: Construct Validity When Measures Are Cheap" (menu-level construct validity, cvprofiles).**
Verification legend: [abs]=verified from arXiv abs page; [web]=verified via publisher/venue/Crossref; [snippet]=found via search snippet only (title/authors may be incomplete — re-verify before citing); [bank]=verified 2026-08-07 in prior-art bank (literature-novelty-audit skill); [digest]=reported in AI Evaluation Substack digest, arXiv ID not independently verified.

---

## 1. WHO is doing what (structured table)

### Thread 1 — LLM-era construct validity / validity frameworks
| Who | Year/Venue | URL | One-line contribution | Verif |
|---|---|---|---|---|
| Bean et al. (42 authors) | 2025, NeurIPS D&B | arXiv:2511.04703 | Systematic review of 445 LLM benchmarks by 29 experts; validity-undermining patterns; 8 recommendations | [abs] |
| Li, Huang, … , Koa | 2026, ACL (Oral+SAC) | arXiv:2605.07409 | "Proxy Presumption" — embeddings as entangled proxies; Construct Validity Protocol (CVP): counterfactual neutralization + validity suite (discriminant/incremental/predictive) | [abs] |
| Licht, Sarkar, Wu, Goel, Stoehr, Ash, Hoyle | 2025, EMNLP | arXiv:2509.03116 | Compares 4 LLM measurement families for scalar constructs (direct, pairwise, token-prob, fine-tune); pairwise+token-prob best — the empirical "menu" | [abs] |
| Halterman & Keith | 2025, Political Analysis 34 | doi:10.1017/pan.2025.10017 (arXiv:2407.10747) | Codebook LLMs: off-the-shelf LLMs vs real-world codebook operationalizations; accuracy evidence | [web] |
| Desai, Card & Jacobs | 2026 | arXiv:2607.07915 | Corpus audit of 8 flagship soc-sci journals: LLM-generated measurements central yet validation inconsistent; emerging norms | [abs] |
| Wallach, Desai, Cooper, Wang, … Jacobs | 2025, ICML position | PMLR 267:82232–51 (arXiv:2502.00561) | "GenAI evaluation is a social science measurement challenge": 4-level measurement framework, validity lenses | [web] |
| Salaudeen, Reuel, Ahmed, Bedi, Robertson, Sundar, Domingue, Wang, Koyejo | 2025 | arXiv:2505.10573 | "Measurement to Meaning": validity-centered framework mapping evaluative claims to evidence via psychometric validity facets; anchors AI Construct Lexis | [abs] |
| Freiesleben | 2026 | arXiv:2603.15121 (also PhilSci 29807) | Argues Cronbach–Meehl nomological account best foundation for LLM capability benchmarks (vs Messick/Kane, Borsboom); philosophical, non-formal | [abs] |
| Coston | 2026, FAccT | arXiv:2601.17146 | Falsification tests for discriminant validity of predictive algorithms (per-measure falsifiability) | [bank] |
| Wang, Deng & Yang | 2026 | arXiv:2605.11954 | Miscalibration as a validity threat across 14 constructs; confidence filtering changes downstream regressions (FOMC case) | [bank] |
| Ogut & Yin | 2026 | arXiv:2607.12219 | **Closest single competitor**: partial ID of β over multiple nonlinear measurements (curvature bounds, linear-consensus normalization); 6 AI/LLM occupation measures | [bank] |
| Messing | 2026 | arXiv:2604.11581 | "Hidden Measurement Error in LLM Pipelines": total evaluation error (TEE) from judge/temperature/prompt variance; naive SEs 40–60% too small; design-study projections | [abs] |
| Bao | 2026, Chinese Political Science Review | doi:10.1007/s41111-026-00351-4 | LLMs for social science measurement as an explicit measurement-framework problem | [snippet] |

### Thread 2 — Benchmark science / eval crisis / judges / private evals
| Who | Year/Venue | URL | One-line contribution | Verif |
|---|---|---|---|---|
| Akhtar et al. (37 authors) | 2026 | arXiv:2602.16763 | Systematic study of benchmark saturation (60 benchmarks); loss of discriminative power | [abs] |
| Eriksson et al. (JRC) | 2025, AIES | arXiv:2502.06559 | Interdisciplinary meta-review (~100 studies) of quantitative benchmarking shortcomings; "can we trust AI benchmarks" | [web] |
| Zhou, Pacchiardi, Martínez-Plumed, … (ADeLe) | 2026, **Nature 652:58–67** | doi:10.1038/s41586-026-10303-2 | General scales (demand+ability profiles, 18 rubrics, 63 tasks): "construct validity through benchmark sensitivity/specificity", instance-level prediction — top-venue claim on benchmark construct validity | [web] |
| Yuan, Zhang, Wen & Hu | 2025 | arXiv:2502.09670 | "The Science of Evaluating Foundation Models": formalized evaluation process + checklists | [abs] |
| Phan et al. (CAIS/Scale AI) | 2025 | arXiv:2501.14249 | Humanity's Last Exam: 2,500 hard questions, private holdout subset, HLE-Rolling (Oct 2025) | [web] |
| Bansal & Maini | 2025 | arXiv:2503.04756 | Risks of LLM evaluation by private data curators (open vs closed evals; gaming) | [snippet] |
| Kapoor, Kirgis, Schwartz, … Narayanan | 2026 | arXiv:2605.20520 | Open-world evaluations + CRUX: long-horizon real tasks vs benchmark-scale automation; benchmarks overstate AND understate capability | [abs] |
| Ishida, Lodkaew & Yamane | 2025 | arXiv:2505.18102 | CapBencher: built-in alarm for benchmark test-set overfitting (holdout logic at benchmark level) | [snippet] |
| Wang, Han, Shang, Tang, Liu | 2026 | arXiv:2607.28685 | "Safety, or Just Capability? A Validity Audit of Agent-Safety Benchmarks": treats 4 safety benchmarks (R-Judge, InjecAgent, AgentHarm, AgentDojo) as measures to be validated | [snippet] |
| Koren, Bar-Haim & Goldsteen | 2026 | arXiv:2608.06329 | "Benchmarking the Benchmarks" for conversational agents: reference quality criteria | [snippet] |
| Judge-bias cluster: Yang et al. (2604.22891); Chen et al. EMNLP'25 "Beyond the Surface" (2506.02592); Lehr, Cipperman & Banaji (2509.26464, extreme self-preference); Spiliopoulou et al. (2508.06709); Li et al. preference leakage (2502.01534); CalibraEval ACL'25; Lee et al. reporting guide (2511.21140); Feng et al. SAGE (2512.16041); Roytburg et al. "narcissists" sanity-check (2601.22548) | 2025–26 | as listed | Self-preference/position/verbosity bias measurement & mitigation; "judge-as-instrument" meta-evaluation matures | [snippet] |
| Choi, Park, Cho, Park & Kim | 2026, ICML | arXiv:2602.00521 | Diagnosing LLM-as-a-judge reliability via IRT-GRM: intrinsic consistency under prompt variation + human alignment — judges as measurement instruments | [abs] |
| Tseng et al. | 2025, ASRU | arXiv:2505.22251 | Speech eval contamination (LibriSpeech/CommonVoice) | [snippet] |
| METR | 2025–26 | metr.org (time-horizons; Frontier Risk Report 2026-05) | Task-completion time-horizon measurements; internal+public frontier evals | [web] |
| Toutou, Harb & Basta | 2026 | arXiv:2605.07453 | Contamination reproducibility study (hieroglyphic translation) | [snippet] |

### Thread 3 — Psychometrics for LLMs / measurement invariance
| Who | Year/Venue | URL | One-line contribution | Verif |
|---|---|---|---|---|
| Ye, Jin, Xie, Zhang & Song | 2025 (v3 2026) | arXiv:2505.08245 | "LLM Psychometrics": systematic review (400+ refs) of using psychometric instruments/theory to evaluate LLMs | [abs] |
| Zhuang, Liu, Pardos, Kyllonen, … | 2025, ICML position | openreview MxCJbuJhWG | "AI Evaluation Should Learn from How We Test Humans": adopt psychometrics for AI items | [web] |
| Zhou, Huang, Zhao, Han, … | 2026, AAAI Oral | doi:10.1609/aaai.v40i41.40814 | "Lost in Benchmarks?": IRT for LLM benchmarking — item-level rethinking | [web] |
| Li, Tang, Chen, Cheng, Metoyer, Hua & Chawla | 2026, ICML | arXiv:2511.04689 | ATLAS: IRT adaptive testing; 3–6% negative-discrimination items (annotation errors); 90% item reduction; rank shifts | [abs] |
| Jung, Lutz, Sen & Strohmaier | 2025, EACL | arXiv:2510.11254 | Do psychometric tests (sexism/racism/morality) work when applied to LLMs? | [snippet] |
| Zeinfeld, Strugatski, Bar-Dov & Blonder | 2026 | arXiv:2603.23682 | Method for items functioning differentially for humans vs chatbots (human-model DIF) | [snippet] |
| Xie | 2026, CSEDU | (no arXiv) | IRT-informed psychometric analysis of LLM essay scoring beyond agreement metrics | [snippet] |
| Maeda & Lu | 2025, J. Educ. Meas. | arXiv:2502.07017 | Predicting differential item functioning from item text with LLMs+XAI | [snippet] |
| AT-LLM scale teams | 2026 | Springer SN CS / ResearchGate | Arabic/Chinese adaptations of "Attitudes toward LLM" scales with full measurement-invariance testing (configural→strict) | [snippet] |
| Mousavi, Kitchens, Oliver & Abbasi | 2026, Info. Sys. Research | (journal) | Lexicons vs LLMs: holistic evaluation of psychometric text analysis in social science | [snippet] |
| Lin | 2025 | arXiv:2506.16697 | "From Prompts to Constructs": dual-validity framework for LLM research in psychology | [snippet] |

### Thread 4 — Cultural AI measurement & synthetic respondents
| Who | Year/Venue | URL | One-line contribution | Verif |
|---|---|---|---|---|
| Agarwal, Shukla, Goyal & Vashistha | 2026 | arXiv:2607.08034 | PLURAL: IVS-grounded preference triplets, 20 countries, ~500k; MAE −27.7%; human eval (176 raters, 3 countries) | [abs] |
| Dey, Joshi, Poddar, Zhao & Ferrara | 2026 | arXiv:2608.01458 | PALMs: construct-grounded rationale supervision for population alignment (5 countries); +8.59% over best baseline | [abs] |
| Kiet, Minh, Nguyen, Tran, …, Tran-Thanh | 2026 | arXiv:2605.10843 | DISCA: training-free cultural alignment via WVS persona panels + disagreement logit correction (20 countries) | [abs] |
| Gonzalez-Bonorino, Capra & Pantoja | 2025 | arXiv:2501.06834 | SCA: LLM synthetic cultural agents for non-WEIRD populations in classic behavioral experiments (user's own group) | [abs] |
| Neumann, De-Arteaga & Fazelpour | 2025, AAAI | arXiv:2504.08954 | Quality checks (not one-off benchmarks) for using LLMs to simulate opinions | [snippet] |
| Qiu, Brisebois & Sun | 2025, LREC | arXiv:2505.16164 | Can LLMs simulate human behavioral variability (phonemic fluency)? | [snippet] |
| Larooij & Törnberg | 2025 | arXiv:2504.03274 | Critical review of generative ABMs / LLM social simulation validity | [snippet] |
| Cultural benchmark vintage: CulturalBench (Chiu et al. 2024, arXiv:2410.02677; ACL 2025 red-team version), CultureBank (EMNLP 2024 Findings), WorldValuesBench (2404.16308), LLM-GLOBE (2411.06032); 2025–26: GIMMICK (2502.13766), CrossCult-KIBench (2605.06115), AVMeme (2601.17645), BLUCK (2505.21092) | 2024–26 | as listed | Cultural knowledge/value benchmarks proliferate; none validates candidate measures of a cultural construct via a shared validity argument | [web] |
| Zerhoudi et al. | 2026 | arXiv:2604.13052 | Moltbook: 1.3M-post agent social network; 3-layer evaluation of agent social behavior | [snippet] |
| ⚠️ GlobalBench | 2023, EMNLP | aclanthology (Song et al.) | **NOT a cultural-values benchmark** — global NLP progress across tasks/languages; do not cite as cultural | [web] |

### Thread 5 — Multi-measure / menu / selection / robustness language
| Who | Year/Venue | URL | One-line contribution | Verif |
|---|---|---|---|---|
| Linde, Sun, Balluff, Radovanović & Chan | 2026 | arXiv:2605.19745 | "Making Uncertainty Visible": multiverse analysis for CSS incl. LLM methods; documents computational-failure combinations | [abs] |
| Canen & Enamorado | 2026, econ.EM | arXiv:2608.02909 | Split-sample IV from multiple LLM-generated measures to correct measurement error in downstream regressions (no validity tests, no surviving set) | [abs] |
| Chen, Rambachan & Tamer | 2026, econ.EM | arXiv:2606.15031 | Partial ID of prevalence/regression from LLM prompt-replication designs; mixture misclassification bounds | [bank] |
| Moosavi Ramezanzadeh & Beresteanu | 2026, econ.EM | arXiv:2607.21807 | Partial ID with auxiliary moment restrictions (admissible completions) — conceptually closest "restriction→set" logic, different object | [bank] |
| Herderich, Lasser, Galesic & Aroyehun | 2026, Behav. Res. Methods | (journal) | Mixed-methods validation of LLM-based measurement of complex constructs in text | [snippet] |
| "menu of measures" exact phrase | — | search | Only found in EU CAP policy ("menu of measures"); **absent** from measurement-validity literature — vocabulary is uncontested | [web] |
| Robustness-analysis tradition | 2026, J. Management | doi:10.1177/01492063261440210 | Robustness analysis in management research incl. multiple measures to assess measurement variation | [snippet] |

---

## 2. CLOSEST PRIOR WORK to menu-level validation (M → validity tests → M* → Θ*)

Ranked by closeness to "multiple candidate measures facing one common validity argument → surviving set → robust downstream conclusions":

1. **Ogut & Yin (2026), arXiv:2607.12219** — same destination ([L,U] for a structural coefficient over multiple measurements of a latent), different engine (curvature bounds under a linear-consensus normalization, not nomological moment restrictions; measures = noisy functions of one latent, not rival operationalizations; no pass/fail admissible set). *Mandatory explicit differentiation.*
2. **Messing (2026), arXiv:2604.11581** — treats judge/temperature/prompt as design choices whose variance must propagate into eval error (TEE) with design-study projections and honest coverage. Closest on "operationalization uncertainty is real and quantifiable," but for eval scores, not construct measures; no theory-based admissibility.
3. **Licht et al. (2025), arXiv:2509.03116** — empirically the M menu (4 LLM families compared on scalar constructs) but comparative psychometrics only: no admissible set, no propagation, no selection rule.
4. **Salaudeen et al. (2025), arXiv:2505.10573** — validity-centered claim→evidence framework (which claims a benchmark score supports) + AI Construct Lexis nomological registry. Conceptual; no formal selection, surviving set, or downstream range.
5. **Canen & Enamorado (2026), arXiv:2608.02909** — multiple LLM measures + sample-splitting for downstream inference, but as measurement-error correction via IV, not as validity screening with holdout tests.
6. **Coston (2026), arXiv:2601.17146** — falsification tests for discriminant validity: per-measure falsifiability, not menu-level.
7. **Linde et al. (2026), arXiv:2605.19745** — multiverse over decisions (incl. LLM pipelines): range over arbitrary specifications; no theory-restricted survivors; failure cases documented descriptively.
8. **Freiesleben (2026), arXiv:2603.15121** — nomological networks as the right validity account for LLM benchmarks: the conceptual endorsement the framework needs, but no operationalization.

**Verdict**: The full conjunction (theory-restricted admissible measurement set + propagation to a downstream estimand + falsifiable selection + screening uncertainty) remains absent as of 2026-08-09. Every component exists separately; Ogut & Yin and Messing are the two papers a reviewer will put on the table.

---

## 3. What is GENUINELY MISSING (with closest existing work per gap)

**(a) Menu-level vs measure-level validation.** All current validity work is measure-level or framework-level: CVP (Li 2026) validates one embedding measure; Coston (2026) falsifies one algorithm's discriminant validity; Licht (2025) compares but never admits/rejects; Bean (2025) reviews benchmarks; Wallach (2025) and Salaudeen (2025) give frameworks; Freiesleben (2026) argues for nomological networks philosophically. **No one executes one shared validity argument (moment restrictions R with substantive thresholds) across a menu and reports the surviving set.** Closest: Licht 2025; Salaudeen 2025.

**(b) Falsifiable selection rule via holdout of validity tests (R_S/R_H).** Sample splitting across measures exists only as an IV correction (Canen & Enamorado 2026) and as a benchmark-level overfitting alarm (CapBencher, 2505.18102); design-choice validation-on-holdout exists for evals (Messing 2026 design-study projections). **No one partitions validity tests into selection/holdout to make measure screening itself falsifiable** — the closest formal literatures are classic pre-testing / moment selection (Andrews–Soares 2010; Leamer 1983 [UNVERIFIED classics]) and post-selection inference (Taylor & Tibshirani 2015 [UNVERIFIED]), which reviewers will invoke.

**(c) Measurement-robust inference (range over survivors) vs spec-curve/multiverse.** Specification curves (Simonsohn et al. 2020), multiverse (Steegen et al. 2016), CSS multiverse (Linde et al. 2026), vibration of effects (Patel et al. 2015), extreme bounds (Leamer 1983), model-averaging (Claeskens & Hjort 2008) all vary specifications **without a theory-justified filtering step**. Ogut & Yin (2026) bound β over measurement-error models, not over validity survivors. **Missing: the image of the estimand over validity survivors Θ* as the inferential object — spec-curve with a falsifiable admission gate.** Closest: Linde 2026; Ogut & Yin 2026.

**(d) Public validity registries / leaderboards for constructs.** AI Construct Lexis (Salaudeen et al.; Schmidt Sciences funded) is a *taxonomy* of constructs+instruments (in development, no validity test records); Evals-consensus (OSF 10.17605/OSF.IO/M7HPT) and PrepEval are *pre-registration protocols for evals*; Every Eval Ever aggregates eval *results*; benchmark leaderboards are model-level; HLE/private sets are closed. **Missing: a construct-level registry where validity-test records, surviving sets, and screening outcomes are public and comparable.** Closest: AI Construct Lexis (2025–26, active) — speed matters; this space is being occupied.

**(e) Benchmark construct validation with held-out tasks.** Bean (2025) gives recommendations; "Validity Audit of Agent-Safety Benchmarks" (2607.28685, Jul 2026) audits 4 benchmarks as measures but with no held-out task families and no selection rule; ATLAS (2511.04689) audits item quality (annotation errors) not construct validity; Akhtar (2602.16763) measures saturation; ADeLe Nature (10.1038/s41586-026-10303-2) claims construct validity via demand/ability scales. **Missing: a benchmark's construct validated by holding out task families and checking whether the selection rule transfers.** Closest: 2607.28685; ADeLe (2026) — high collision risk on framing.

**(f) Uncertainty quantification of the screening itself (empty-replicate rate, boundary attribution).** Messing (2026) is closest on "uncertainty from design choices" but for eval scores; Linde et al. (2026) document computational-failure combinations descriptively; Chen–Rambachan–Tamer (2606.15031) show weak restrictions collapse the ID set to [0,1] (an "admissible-empty-like" outcome, unquantified); CapBencher alarms on overfit. **Missing: formal empty-replicate rates, boundary attribution (which test kills which measure), and coverage guarantees for the two-step selection+inference procedure.** Closest: Messing 2026; Linde 2026.

---

## 4. Ranked candidate novel angles (Nature/PNAS, submit Dec 2026–Feb 2027)

**#1 — Falsifiable measure selection: holdout-validated validity tests (R_S/R_H) as a screening rule with a defined screening-failure rate.** For: nothing in print partitions validity tests into selection/holdout; the closest items serve different purposes (Canen & Enamorado = IV correction; CapBencher = benchmark alarm). Against: pre-testing/selection-bias and post-selection inference literatures are the obvious attack surface; needs formal two-step coverage/size results; Ogut & Yin will be cited as "partial ID already handles measurement multiplicity."

**#2 — Operationalization uncertainty as a first-class scientific quantity (empty-replicate rate, boundary attribution, Θ* bands).** For: strongest "new quantity" story; Messing (2026) proves the community is ready for design-choice uncertainty but stops at eval scores; the empty-replicate/boundary-attribution statistics exist nowhere. Against: Messing 2026 is a near-miss in spirit (40–60% SE inflation, coverage decay, design projections); multiverse failure cases (Linde 2026) partially anticipate.

**#3 — Menu-level construct validity: validity is a property of a family with a surviving set, not of a single instrument (Θ* = image of estimand over survivors).** For: this is the paper's core thesis and remains unclaimed as an operational procedure; no propagation-over-survivors exists. Against: Ogut & Yin (2026) is a same-destination/different-engine near-miss; psychometric tradition (Cronbach–Meehl; Messick) treats validity as property of a test+interpretation — expect disciplinary pushback; Freiesleben (2026) and Salaudeen (2025) own the conceptual framing and must be cited as the agenda-setters, not the machinery.

**#4 — A public construct-validity registry / leaderboard (pre-registered validity tests, public test records, screening audit trail) with cvprofiles as the open standard.** For: nothing like it exists; AI Construct Lexis is taxonomy-only; Evals-consensus/PrepEval are protocols for evals; a position paper can define the standard without building the full platform. Against: AI Construct Lexis (active, well-funded) could extend into test records quickly; registry papers are infra-heavy and reviewers may call it a proposal, not science — pair with #2 or #3 for substance.

**#5 — Benchmark-as-measure: apply the menu framework to benchmarks (each benchmark is one measure in M; construct validation via held-out task families).** For: "Validity Audit of Agent-Safety Benchmarks" (2026) shows the audit move is fresh; Bean's checklist is static; no selection rule exists for benchmark families. Against: highest collision risk — ADeLe Nature (2026) already occupies "construct validity of benchmarks" at the top venue; ATLAS + saturation literature crowd the space; positioning must be explicitly against ADeLe, not adjacent to it.

**Recommended core for the submission: #3 as the thesis, #1 as the sharpest technical novelty, #2 as the headline empirical contribution; #4 folded in as the companion-infrastructure section; #5 as one application section** — with explicit differentiation from Ogut & Yin (2026), Messing (2026), Salaudeen (2025), and ADeLe (2026) mandatory.

---

## 5. Caveats & flags
- arXiv full-text search returned noise for many quoted-phrase queries this session; "not found" claims rest on targeted Semantic Scholar/web exact-phrase searches plus two curated digests, not on exhaustive full-text coverage.
- Items marked [snippet] (Bao 2026; Mousavi 2026; Herderich 2026; several judge-bias papers; cultural benchmarks) were seen as search results only — re-verify metadata before citing.
- [digest] IDs (2601.21817, 2601.21816, 2601.19532, 2602.18182, moral-competence Nature perspective 10.1038/s41586-025-10021-1) come from the AI Evaluation Substack Feb/Apr 2026 digests — leads, not verified citations.
- GlobalBench is a 2023 EMNLP NLP-coverage benchmark, NOT a cultural-values benchmark — flagged to prevent a citation error.
- SCA (arXiv:2501.06834) is the user's own group's paper (Gonzalez-Bonorino, Capra, Pantoja).
- Canonical anchors (Simonsohn 2020; Steegen 2016; Leamer 1983; Andrews–Soares 2010; Taylor–Tibshirani 2015; Cronbach & Meehl 1955; Messick 1995; Campbell & Fiske 1959; Hu–Schennach 2008) cited from memory — [UNVERIFIED] this session.
