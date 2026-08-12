# Literature Audit C — Novelty Frontier: Construct Validity as Partial Identification over a Menu of Measurement Functions (M → M* → [L,U])

**Date:** 2026-08-07 · **Auditor:** subagent · All URLs verified by live retrieval this session unless flagged `[UNVERIFIED]`.

---

## 1. CLOSEST PRIOR ART

**1. Ogut & Yin (2026). "Partial Identification with Multiple Nonlinear Measurements of a Latent Regressor." arXiv:2607.12219 (econ.EM), submitted 13 Jul 2026.** ← *The single closest paper; also the July 2026 paper (see §3).* Linear regression with a latent regressor observed only through multiple smooth, possibly nonlinear noisy measurements; a scale normalization (consensus measurement function linear) plus a bound on curvature heterogeneity yields a **closed-form interval for the structural coefficient**, invariant to unknown source loadings; ≥4 measurements make the bound estimable via a split-instrument auxiliary regression; Imbens–Manski CIs with Stoye critical values give uniform coverage. Application: six AI-exposure measures (incl. LLM language-model measures and a Webb patent-text measure) on an ACS panel; a factor-analytic rule **drops the Webb measure as a distinct construct**; five retained sources give a loading-invariant consensus coefficient with a partial-ID half-width of ~1.2%. **How close:** it delivers [L,U] for a downstream β over a *collection of measurement sources*, with a measurement-selection step (factor-analytic separation) and full econometric inference. **Remaining gap:** the interval is produced by smoothness/curvature bounds under a linear-consensus normalization — not by *testing* candidate measures against a researcher-specified nomological network. There is no finite menu M, no admissible set M* defined by passing/failing moment restrictions, and no role for theory-derived restrictions as the selection device. Measures are noisy functions of one latent (a measurement-error model), not rival operationalizations of a construct admitted or rejected by theory.

**2. Chen, Rambachan & Tamer (2026). "Partial Identification from LLM Prompts." arXiv:2606.15031 (econ.EM), v2 24 Jun 2026.** LLM binary reports as measurements of a latent label; partial identification of prevalence θ from prompt-replication designs; weak stochastic-ordering restrictions leave the set at [0,1]; external calibrated scores/events discipline the mixture; an extension derives **bounds on regression coefficients when the latent is an unobserved regressor**. **Gap:** no menu/admissibility logic, no nomological network; measures are error-prone signals of one latent, and restrictions are distributional (stochastic ordering, calibration), not theory-validity restrictions.

**3. Moosavi Ramezanzadeh & Beresteanu (2026). "Partial Identification with Auxiliary Moment Restrictions." arXiv:2607.21807 (econ.EM), 23 Jul 2026.** Restricts the **set of admissible completions** of interval-coarsened data to those consistent with published aggregates; characterizes the sharp identification region for the **best linear predictor**; closed-form identifying-value measures. **Gap:** the admissible set is over data completions, not measurement functions; the restrictions are aggregate moments, not nomological testable restrictions. Conceptually the closest to "restriction → admissible set → region for an estimand," but on a different object.

**4. Simonsohn, Simmons & Nelson (2020). "Specification Curve Analysis." Nature Human Behaviour 4, 1208–1214.** **Gap:** enumerates *all* defensible specifications (including different operationalizations/measures) and reports the full distribution of estimates; there is no admissibility filtering by theory tests, no formal identified set [L,U], and no treatment of selection uncertainty. `[UNVERIFIED — canonical; not re-verified this session]`

**5. Steegen, Tuerlinckx, Gelman & Vanpaemel (2016). "Increasing Transparency Through a Multiverse Analysis." Perspectives on Psychological Science 11(5), 702–712; and Patel, Burford & Ioannidis (2015), "Assessment of Vibration of Effects Due to Model Specification Can Demonstrate the Instability of Observational Associations," J. Clinical Epidemiology 68(9), 1043–1050; and Leamer (1983), "Let's Take the Con Out of Econometrics," AER 73(1), 31–43.** The family tree: many operationalizations → many estimates; communicate the spread. **Gap:** descriptive, not inferential; no admissible-set structure; no propagation of a *restricted* set into a downstream estimand with coverage guarantees. `[UNVERIFIED]`

**6. Hu & Schennach (2008). "Instrumental Variable Treatment of Nonclassical Measurement Error Models." Econometrica 76(1), 195–216; Hu (2017), "The Instrumental Variable Approach to Measurement Error," survey chapter; Schennach (2021/22), "Measurement Systems," J. Economic Literature 59(4) — verified URL: doi.org/10.1257/jel.20211355.** Multiple measurements + instruments identify latent models, often nonparametrically. **Gap:** *point* identification under completeness/instrument assumptions; no menu of candidate measures, no nomological restrictions, no partial-ID reporting when restrictions fail. `[Econometrica/Hu-chapter details UNVERIFIED; JEL verified]`

**7. Licht, Sarkar, Wu, Goel, Stoehr, Ash & Hoyle (2025). "Measuring Scalar Constructs in Social Science with LLMs." EMNLP 2025; arXiv:2509.03116.** Empirically compares four LLM measurement families (direct prompting, pairwise comparisons, token-probability scoring, fine-tuning) for scalar constructs. **Gap:** exactly the M menu — but comparative psychometrics (reliability/validity ranking), no admissible set, no propagation to downstream estimands.

**8. LLM-validity cluster (context, not the move):** Bean et al. (2025/26), "Measuring What Matters: Construct Validity in LLM Benchmarks," NeurIPS 2025 D&B, arXiv:2511.04703 (systematic review of 445 benchmarks; 8 recommendations); Freiesleben (2026), "Establishing Construct Validity in LLM Capability Benchmarks Requires Nomological Networks," PhilSci-Archive 29807 (argues nomological networks are *needed* — conceptually the closest to using N as identifying structure, but non-formal/philosophical); Coston (2026), "Falsifying Discriminant Validity of Predictive Algorithms," FAccT 2026, arXiv:2601.17146 (statistical falsification test for discriminant validity; multiple permissible proxies); Wang, Deng & Yang (2026), "Assessing and Mitigating Miscalibration in LLM-Based Social Science Measurement," arXiv:2605.11954 (calibration as part of measurement validity across 14 constructs; confidence filtering changes downstream regression estimates). None formalizes M → M* → [L,U].

*Not found:* any psychometric paper doing "construct validity as set inference" or "admissible measurement sets"; no specification-curve/multiverse variant that filters operationalizations by nomological restriction tests before propagating. (Freyberger 2015, as named in the brief: **not located**; the nearest identified is Freyberger (2017), "Normalizations and Misspecification in Skill Formation Models," Econometrica `[UNVERIFIED]`.)

---

## 2. NOVELTY VERDICT

**Does the exact move exist in print?** The *full* package — (i) a finite menu of measurement functions; (ii) an admissible subset M* defined by *passing researcher-specified, theory-derived (nomological) moment restrictions with thresholds*; (iii) propagation of the image of a downstream estimand over M* into [L,U]; (iv) audit-trail tooling — **was not found in print.** Every component exists separately: menus (Licht et al. 2025), restriction-testing of measures (Coston 2026; classical MTMM/validity tests), partial identification of β over multiple measurements (Ogut & Yin 2026; Chen-Rambachan-Tamer 2026), set-restricted estimands (Moosavi Ramezanzadeh & Beresteanu 2026), and specification enumeration (Simonsohn et al. 2020). The conjunction is novel, but **narrowly**: Ogut & Yin is one move away.

**Minimal novel core that survives attack:**
1. **Nomological restrictions as the selection device** — theory-restricted admissible measurement sets (admission/rejection of candidate operationalizations by testable restrictions derived from a stated nomological network), in contrast to Ogut & Yin's curvature bounds or factor-analytic separation, and to multiverse enumeration.
2. **Propagation to downstream estimands with honest inference** — reporting [L,U] over M* (not just per-measure coefficients), with coverage that accounts for the random admissibility of M* (projection/Imbens–Manski-type regions over the selection step).
3. **The construct-validity bridge** — recasting psychometric validity theory (nomological networks as identifying restrictions; validity as an identification question rather than a correlation checklist) in partial-identification language, spanning economics, psychometrics, and LLM measurement.
4. **cvprofiles tooling** — reproducible audit trail making the menu, restrictions, thresholds, and [L,U] auditable (scientific-software contribution, not just a paper).

**Weakest points a reviewer will attack:**
- **Pre-testing/selection bias:** M* is data-dependent (restrictions tested, then conditioned on). Naive [L,U] over the realized M* understates uncertainty; the paper must deliver simultaneous coverage over (admission decisions, β range) or explicit post-selection inference. This is the methodological crux.
- **Degrees of freedom relocated:** the researcher now chooses the nomological network, restrictions, and thresholds — the same arbitrariness moves one level up ("who audits the audit?"). Thresholds are especially vulnerable: admissible-set boundaries can be knife-edge in J.
- **Empty/degenerate M***: finite-sample power and multiple-testing issues can empty the set or admit everything; the framework needs a decision rule for these cases.
- **Ogut–Yin overlap:** a reviewer can argue the destination ([L,U] for β over competing measures) is already published (Jul 2026) and that the novelty reduces to the admissibility filter and the LLM-construct framing — differentiation must be explicit and early.

---

## 3. THE JULY 2026 PAPER — **FOUND**

**Ogut, Burhan & Yin, Michelle (2026). "Partial Identification with Multiple Nonlinear Measurements of a Latent Regressor." arXiv:2607.12219 [econ.EM, cs.AI], submitted Mon, 13 Jul 2026.** doi:10.48550/arXiv.2607.12219. Details in §1.1. This is the paper Gemini referenced. It is *not* the cvprofiles move (no nomological-restriction admissible set), but it occupies the same conceptual territory and **must be cited and differentiated** in any novelty claim.

---

## 4. REFERENCES

1. Ogut, B. & Yin, M. (2026). Partial Identification with Multiple Nonlinear Measurements of a Latent Regressor. arXiv:2607.12219. https://arxiv.org/abs/2607.12219
2. Chen, X., Rambachan, A. & Tamer, E. (2026). Partial Identification from LLM Prompts. arXiv:2606.15031. https://arxiv.org/abs/2606.15031
3. Moosavi Ramezanzadeh, B. & Beresteanu, A. (2026). Partial Identification with Auxiliary Moment Restrictions. arXiv:2607.21807. https://arxiv.org/abs/2607.21807
4. Simonsohn, U., Simmons, J.P. & Nelson, L.D. (2020). Specification Curve Analysis. Nature Human Behaviour 4, 1208–1214. `[UNVERIFIED]`
5. Steegen, S., Tuerlinckx, F., Gelman, A. & Vanpaemel, W. (2016). Increasing Transparency Through a Multiverse Analysis. Perspectives on Psychological Science 11(5), 702–712. `[UNVERIFIED]`
6. Patel, C.J., Burford, B. & Ioannidis, J.P.A. (2015). Assessment of Vibration of Effects… J. Clinical Epidemiology 68(9), 1043–1050. `[UNVERIFIED]`
7. Leamer, E.E. (1983). Let's Take the Con Out of Econometrics. AER 73(1), 31–43. `[UNVERIFIED]`
8. Hu, Y. & Schennach, S.M. (2008). Instrumental Variable Treatment of Nonclassical Measurement Error Models. Econometrica 76(1), 195–216. `[UNVERIFIED]`
9. Hu, Y. (2017). The Instrumental Variable Approach to Measurement Error. `[UNVERIFIED]`
10. Schennach, S.M. (2021/22). Measurement Systems. JEL. https://doi.org/10.1257/jel.20211355 (verified)
11. Licht, H., Sarkar, R., Wu, P., Goel, P., Stoehr, N., Ash, E. & Hoyle, A. (2025). Measuring Scalar Constructs in Social Science with LLMs. EMNLP 2025. arXiv:2509.03116. https://arxiv.org/abs/2509.03116
12. Bean, A.M. et al. (2025/26). Measuring What Matters: Construct Validity in LLM Benchmarks. NeurIPS 2025 D&B. arXiv:2511.04703. https://arxiv.org/abs/2511.04703
13. Freiesleben, T. (2026). Establishing Construct Validity in LLM Capability Benchmarks Requires Nomological Networks. https://philsci-archive.pitt.edu/29807/
14. Coston, A. (2026). Falsifying Discriminant Validity of Predictive Algorithms. FAccT 2026. arXiv:2601.17146. https://arxiv.org/abs/2601.17146
15. Wang, J., Deng, N. & Yang, Y. (2026). Assessing and Mitigating Miscalibration in LLM-Based Social Science Measurement. arXiv:2605.11954. https://arxiv.org/abs/2605.11954
16. Freyberger, J. (2015, as named in brief): **not found.** Nearest: Freyberger (2017), Normalizations and Misspecification in Skill Formation Models, Econometrica. `[UNVERIFIED]`
