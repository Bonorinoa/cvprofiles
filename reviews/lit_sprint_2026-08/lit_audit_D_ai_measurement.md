# Literature Audit D — "AI as Measurement" in Social Science, 2023–2026

**Auditor note:** every item below was located and its key numbers verified against the source page (arXiv abstract page, journal page, or repository README) during this session, unless flagged `[UNVERIFIED]`. The PolMeth 2026 data point given in the task brief was independently confirmed against the repo.

## 1. TREND MAP (verified examples, with numbers)

1. **Gilardi, Alizadeh & Kubli (2023), PNAS 120(30):e2305016120** — "ChatGPT outperforms crowd workers for text-annotation tasks." On 4 samples of tweets/news (n=6,183), ChatGPT's zero-shot accuracy beat crowd-workers on 4 of 5 tasks and its intercoder agreement exceeded both MTurk and trained annotators. ~2,400+ citations (PubMed). *The canonical LLM-as-annotator result that launched the labeling branch.*
2. **Argyle et al. (2023), Political Analysis 31(2):337–353** — "Out of One, Many: Using Language Models to Simulate Human Samples." GPT-3 conditioned on respondent profiles reproduced opinion distributions on 7 attitude dimensions (Pearson r ≈ 0.9+ vs. 2012 ANES) and proposed an explicit **algorithmic-fidelity validation standard** (Social Science Turing Test, Distribution Matching, Forward Continuity, Pattern Correspondence). 1,881 citations.
3. **Aher, Arriaga & Kalai (2023), ICML 2023 (PMLR v202); arXiv:2208.10264** — "Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies" ("Turing Experiments"). Replicated Ultimatum Game, Garden Path, and Wisdom of Crowds effects with LLMs as simulated subjects; also documented "hyper-accuracy" (too-perfect recall) artifacts.
4. **Ziems et al. (2024), Computational Linguistics 50(1):237–291** — "Can Large Language Models Transform Computational Social Science?" Systematic survey of LLM use across 67+ CSS tasks (annotation, generation, simulation); ~1,300 citations.
5. **Bisbee, Clinton, Dorff, Kenkel & Larson (2024), Political Analysis 32(4):401–416** — "Synthetic Replacements for Human Survey Data? The Perils of Large Language Models." 30 synthetic ChatGPT-3.5 personas per each of 7,530 ANES respondents → 3,614,400 responses. Averages matched, but 48% of regression coefficients differed significantly from ANES estimates (sign flipped in 32% of those); outputs shifted with prompt wording and over 3 months (Apr→Jul 2023).
6. **Park, O'Brien et al. (2024), arXiv:2411.10109** — "Generative Agent Simulations of 1,000 People." Interview-based agents of 1,052 real individuals; 85% accuracy on General Social Survey items in replication interviews. Flagship of the "digital twin / AI society" branch (cf. AgentSociety, arXiv:2502.08691).
7. **Horton, Filippas & Manning (2023), NBER w31122; arXiv:2301.07543** — "Large Language Models as Simulated Economic Agents: What Can We Learn from Homo Silicus?" LLMs as simulated experimental subjects in ultimatum/dictator games — the seed paper for LLM economics.
8. **Hall (2026), github.com/andybhall/polmeth-2026-ai (verified)** — PolMeth XLIII (Michigan State, Jul 16–18 2026): 175 presentations (60 panel papers + 115 posters); **45 (26%) core generative-AI**; primary uses: labeling/annotation 16 (36%), measurement beyond labeling 11 (24%) — **60% of core-AI work is measurement-related**; silicon sampling only 2 (4%). Companion sweep `andybhall/ai-in-political-science`: **86 AI papers across 17 top political-science journals, 2021–2026**.
9. **Landesvatter et al. (2026), accepted at Survey Research Methods; arXiv:2506.14634** — "Using Large Language Models for Coding Open-Ended Survey Responses." German GESIS panel data (5,072 expert-coded responses); off-the-shelf GPT-4o/Llama-3.2/Mistral-NeMo coding was poor; only a **fine-tuned** model reached macro-F1 0.87 — off-the-shelf LLM-coded open-ends can paint a different distribution than human coding.

*Growth claims are only made where sourced:* the PolMeth 26%-core-AI share, the 86-paper/17-journal sweep, and citation counts above. No other aggregate growth numbers were verified; `[UNVERIFIED]` any beyond these.

## 2. PERSONA-SKEPTICISM VERIFICATION

**(a) WVS >70,000 respondent-item study — CONFIRMED.** "Assessing the Reliability of Persona-Conditioned LLMs as Synthetic Survey Respondents," Taday Morocho, Cima, Fagni, Avvenuti & Cresci, arXiv:2602.18462 (subm. 6 Feb 2026). WVS US microdata, **>70K respondent-item instances**, two open-weight chat models + random-guesser baseline: "persona prompting does not yield a clear aggregate improvement in survey alignment and, in many cases, significantly degrades performance"; effects concentrated in a few items and underrepresented subgroups → subgroup fidelity undermined.

**(b) 57.4% GPT-4.1 modal-preference accuracy — CONFIRMED.** "Can Persona-Prompted LLMs Emulate Subgroup Values? An Empirical Analysis of Generalisability and Fairness in Cultural Alignment," arXiv:2604.12851; ACL 2026 (2026.acl-long.1127). "Even state-of-the-art models like GPT-4.1 achieve only 57.4% accuracy in predicting subgroup modal preferences"; simple fine-tuning on structured numerical preferences (20,000+ samples) yields "substantial gains," improving accuracy on unseen, out-of-distribution subgroups.

**(c) PNAS Nexus cultural prompting — CONFIRMED, year corrected to 2024.** Tao et al. (2024), "Cultural bias and cultural alignment of large language models," PNAS Nexus 3(9):pgae346. Models default to values of English-speaking/Protestant-European countries; cultural prompting improved alignment for ~71–81% of countries but not universally (figure as summarized by PNAS News; ~770 citations).

**(d) Demographic-probing instability — CONFIRMED.** "Different Demographic Cues Yield Inconsistent Conclusions About LLM Personalization and Bias," Tonneau, Seghal, Malhotra, Kazemi, Orozco-Olvera, Muñoz Boudet, Subramanian, Fraiberger, Guntuku & Hofmann (World Bank + academia), arXiv:2601.18486 (Jan 2026). Across **14.8M prompts** (race/gender, US), alternative cues for the same group produced "inconsistent conclusions about personalization" and "unstable" bias estimates (magnitude and direction vary across cues) — alternative operationalizations of the same demographic construct are *not* interchangeable.

## 3. PRIOR UPDATE — does a rigorous alternative to persona prompting exist?

**Verdict: yes — the economist's prior ("the whole field is persona-prompting-based") is outdated.** A rigorous alternative framework exists and is maturing fast (2023→2026). Strongest citations:

1. **Ludwig, Mullainathan & Rambachan (2025), NBER w33344; arXiv:2412.07031** — "Large Language Models: An Applied Econometric Framework." The most rigorous formalization: treating LLM outputs as automated **measurement** requires combining them with a small human-labeled validation sample to obtain consistent, precisely estimated downstream quantities (i.e., a measurement-error/calibration protocol, not prompt faith).
2. **Manning, Zhu & Horton (2024), arXiv:2404.11794; NBER w32381; Social Science Research** — "Automated Social Science: Language Models as Scientist and Subjects." Replaces ad-hoc persona prompting with **structural causal models** as "a blueprint for constructing LLM-based agents," including experimental design, hypothesis testing, and prediction; shows LLMs can predict effect *signs* but not magnitudes unless conditioned on the fitted SCM.
3. **Argyle et al. (2023)** — the four **algorithmic-fidelity criteria** (see §1.2) are an explicit validation protocol for LLM-generated data (social-science Turing test, distribution matching, forward continuity, pattern correspondence), later operationalized by Bisbee et al. (2024) and the 2026 wave.
4. **Wang, Deng & Yang (2026), arXiv:2605.11954** — treats **calibration as part of measurement validity** (not post-processing) and gives a mitigation (soft-label distillation, ECE −43.2%, Brier −34.0%). See Part 4.
5. **Fine-tuning/alignment as the substitute for prompting:** the ACL 2026 subgroup-values paper (§2b) and Landesvatter et al. (§1.9) both show fine-tuning on structured/human-coded targets outperforms any prompting configuration — the field is converging on "train the model to the construct," not "prompt the construct into the model." `[UNVERIFIED]` any DPO-for-culture claims: I found no specific verified DPO-cultural-alignment paper in this session.

## 4. CALIBRATION

**Found (the target paper):** Wang, Deng & Yang (2026), **"Assessing and Mitigating Miscalibration in LLM-Based Social Science Measurement," arXiv:2605.11954** (v1 12 May 2026, v2 2 Jun 2026). Exactly as claimed: audits calibration **across 14 social science constructs** (proprietary GPT-5-mini, DeepSeek-V3.2, and open-source models); FOMC case study shows confidence-based filtering changes downstream regression estimates when confidence is miscalibrated; concludes LLM pipelines "should treat calibration as part of measurement validity." **All elements of the claim verified** (title, authors, 14 constructs, calibration-as-validity framing).

**Other calibration-of-LLM-responses work found:** Bisbee et al. (2024) documented over-confidence (undersized variance) of synthetic survey responses — a substantive calibration failure even without ECE-style metrics; Wang et al. build the formal ECE/Brier treatment. No additional dedicated 2026 calibration paper was found beyond these; searches for "calibration LLM survey respondents" surfaced mostly the above.

## References (all verified this session)

1. Gilardi, Alizadeh & Kubli (2023). ChatGPT outperforms crowd workers for text-annotation tasks. PNAS 120(30):e2305016120; arXiv:2303.15056. — Zero-shot annotation > crowd workers; n=6,183.
2. Argyle et al. (2023). Out of One, Many: Using Language Models to Simulate Human Samples. Political Analysis. — GPT-3 simulates survey samples; algorithmic-fidelity criteria.
3. Aher, Arriaga & Kalai (2023). Using Large Language Models to Simulate Multiple Humans and Replicate Human Subject Studies. ICML; arXiv:2208.10264. — Turing Experiments; replicates ultimatum/wisdom-of-crowds.
4. Ziems et al. (2024). Can Large Language Models Transform Computational Social Science? Computational Linguistics 50(1):237–291. — Field survey of LLM×CSS tasks.
5. Bisbee, Clinton, Dorff, Kenkel & Larson (2024). Synthetic Replacements for Human Survey Data? Political Analysis 32(4):401–416. — 48% of coefficients differ from ANES; prompt/time instability.
6. Park et al. (2024). Generative Agent Simulations of 1,000 People. arXiv:2411.10109. — 1,052 interview-based agents; 85% GSS replication accuracy.
7. Horton, Filippas & Manning (2023). LLMs as Simulated Economic Agents: Homo Silicus. NBER w31122; arXiv:2301.07543. — LLMs as economic experimental subjects.
8. Hall (2026). PolMeth 2026 AI repo (github.com/andybhall/polmeth-2026-ai) + ai-in-political-science sweep. — 45/175 (26%) core genAI; 60% measurement-related; 86 AI papers in 17 journals.
9. Landesvatter et al. (2026). Using LLMs for Coding Open-Ended Survey Responses. arXiv:2506.14634; Survey Research Methods (in press). — Fine-tuned only: macro-F1 0.87.
10. Taday Morocho et al. (2026). Assessing the Reliability of Persona-Conditioned LLMs as Synthetic Survey Respondents. arXiv:2602.18462. — >70K WVS respondent-item instances; no aggregate persona gain.
11. [ACL 2026 subgroup values paper, arXiv:2604.12851 / 2026.acl-long.1127] "Can Persona-Prompted LLMs Emulate Subgroup Values?" — GPT-4.1 57.4% modal accuracy; fine-tuning helps OOD subgroups.
12. Tao et al. (2024). Cultural bias and cultural alignment of LLMs. PNAS Nexus 3(9):pgae346. — Cultural prompting helps 71–81% of countries, not all.
13. Tonneau et al. (2026). Different Demographic Cues Yield Inconsistent Conclusions About LLM Personalization and Bias. arXiv:2601.18486. — 14.8M prompts; cue-dependent bias conclusions.
14. Manning, Zhu & Horton (2024). Automated Social Science. arXiv:2404.11794; NBER w32381. — SCM-structured LLM scientists/subjects.
15. Ludwig, Mullainathan & Rambachan (2025). Large Language Models: An Applied Econometric Framework. NBER w33344; arXiv:2412.07031. — Validation-sample correction for LLM measurement.
16. Wang, Deng & Yang (2026). Assessing and Mitigating Miscalibration in LLM-Based Social Science Measurement. arXiv:2605.11954. — 14 constructs; calibration as validity; ECE −43.2%.

*Not found:* any 2026 persona-skepticism paper beyond (a)–(d); any verified DPO-for-cultural-alignment paper; verified aggregate growth statistics beyond the cited sources.
