# Literature memo — Discriminant threshold θ for |Corr(patience, risktaking)| at country level

**Question:** Is θ = 0.35 better supported by the literature than θ = 0.30 as the corr_zero (discriminant) bar for the GPS-based patience construct vs. risktaking?

## 1. Reported population correlations

- **Country level (GPS, n = 76).** Falk et al. (2018, *QJE*), main-text **Table IV** ("Pairwise correlations between preferences at the country level"): Corr(patience, risk taking) = **0.230** (p < .05). This is in the main text, not the appendix; the accompanying text notes the correlation is "positive and statistically significant at the country level." Your full-sample value (0.230) matches the published value to the decimal [1][2].
- **Sample sensitivity.** The 2016 preprint (Netspar DP051), footnote 14: "Excluding African countries, the positive correlation between risk taking and patience increases to **0.30**"; country-level item correlations: quantitative items 0.19, qualitative items 0.55. This footnote was dropped from the published version [3].
- **Replication.** Hanushek, Kinne, Lergetporer & Woessmann (2022, *Economic Journal*), using GPS data in a 49-country sample: cross-country Corr(patience, risk-taking) = **0.358** (p = 0.012) [4]. The country-level population correlation is thus sample-dependent, roughly **0.23–0.36**.
- **Individual level (GPS, ≈80,000 respondents).** Online Appendix C, Table 12 (partial correlations with country fixed effects): Corr(patience, risk taking) = **0.210** (p < .01) [2].
- **Dohmen et al. (2011, *JEEA*).** I could **not verify** a specific patience–risk correlation figure in this paper. It is citable here as the validation basis of the GPS risk item (representative SOEP; the survey risk question correlates ≈0.25 with incentivized lottery behavior, per Falk et al. 2016) [5][6].

## 2. Distinctness of time vs. risk preference

The two are treated as separate constructs throughout the literature: distinct primitives in discounted-expected-utility models (discount function vs. utility curvature), with distinct behavioral correlates in the GPS itself (patience → saving, education, income; risktaking → self-employment, smoking) [1]. Andreoni & Sprenger (2012, *AER*), using incentive-compatible experiments, conclude "the data suggest strongly a difference between risk and time preferences" [7]. Falk et al. (2018) construct the GPS as six conceptually distinct, separately validated dimensions (Table I); within-domain survey–experimental validation correlations run 0.4–0.7, far above the ~0.2–0.3 cross-domain correlations, so a modest positive patience–risk correlation is expected and compatible with distinctness (shared method variance, demographics, cognitive ability) [1][5].

## 3. Sampling noise at n = 33

With Fisher's z, SE_z = 1/√(n−3) = **0.183** at n = 33. Observed r = 0.335 → z = 0.348. Under ρ = 0.25 (merged frame): difference 0.093 = **0.51 SE** (two-sided P ≈ 0.61). Under ρ = 0.23 (full sample): **0.63 SE** (P ≈ 0.53). The train-subset estimate is squarely within sampling variation of a 0.23–0.25 population correlation; its 95% CI spans ≈ −0.01 to +0.61, and r = 0.335 is not even significant at 5% (t = 1.98). Relative to the bar: 0.335 sits **0.21 SE above θ = 0.30** and **0.09 SE below θ = 0.35**; the 0.05 gap between thresholds equals ~0.3 of an r-scale SE at n = 33. Under ρ = 0.25, a random n = 33 draw exceeds 0.30 with probability ≈ **0.38** and 0.35 with ≈ **0.27** — both bars fail frequently by pure noise at this n.

## 4. Verdict

**θ = 0.35 is better supported for this application**, with real caveats. Reasoning: (i) the canonical published population value is 0.23–0.25, and independent GPS-based constructions range up to 0.30 (excluding Africa) and 0.358 (Hanushek et al.), so **θ = 0.30 sits inside the literature's observed range** and would reject the instrument in legitimate samples built from the same data; (ii) θ = 0.30 rejects the train subset (0.335) on a **0.21-SE deviation** — a knife-edge that flips with the random holdout split and has ~38% chance of occurring by chance; (iii) θ = 0.35 admits all three project estimates (0.230, 0.253, 0.335) with margin while remaining a binding discriminant (it still rejects strong collinearity, r ≳ 0.6). Caveats: θ is a researcher choice, not a literature constant; 0.35 sits at the top of the credible range (Hanushek's 0.358 exceeds it); and at n = 33 even 0.35 fails ~27% of draws under ρ = 0.25. If the goal is a robust validity gate, the more principled fix than raising θ is to evaluate the corr_zero bar on the full/merged frames (n = 76/42; estimates 0.230–0.253, far below either bar) or to pool holdout splits rather than a single 33-country draw.

---

## Sources

[1] Falk, Becker, Dohmen, Enke, Huffman & Sunde (2018), "Global Evidence on Economic Preferences," *QJE* 133(4), 1645–1692, Table IV. https://academic.oup.com/qje/article/133/4/1645/5025666 (open PDF: https://www.hbs.edu/ris/Publication%20Files/Quarterly%20Journal%20of%20Economics_269d889b-69bb-4412-a7bf-e5dfa7d7bff7.pdf)

[2] NBER Working Paper 23943 (incl. Online Appendix C, Table 12). https://www.nber.org/system/files/working_papers/w23943/w23943.pdf

[3] Falk et al. (2016), "Global Evidence on Economic Preferences," Netspar DP051, footnote 14. https://www.netspar.nl/wp-content/uploads/P20161221_dp051_Falk.pdf

[4] Hanushek, Kinne, Lergetporer & Woessmann (2022), "Patience, Risk-Taking, and Human Capital Investment across Countries," *Economic Journal* 132(646); Online Appendix (correlation 0.358, Table A3). https://hanushek.stanford.edu/sites/default/files/publications/patience+risk%20210716%20online%20appendix.pdf

[5] Falk, Becker, Dohmen, Huffman & Sunde (2016), "The Preference Survey Module," HCEO WP (survey–experimental validation; Dohmen et al. 2011 risk correlation ≈0.25). http://humcap.uchicago.edu/RePEc/hka/wpaper/Falk_Becker_etal_2016_preference-survey-module.pdf

[6] Dohmen, Falk, Huffman, Sunde, Schupp & Wagner (2011), "Individual Risk Attitudes: Measurement, Determinants, and Behavioral Consequences," *JEEA* 9(3), 522–550. https://doi.org/10.1111/j.1542-4774.2011.01015.x

[7] Andreoni & Sprenger (2012), "Risk Preferences Are Not Time Preferences," *AER* 102(7), 3357–3376. https://www.aeaweb.org/articles?id=10.1257/aer.102.7.3357

*Verification note: all correlation figures above were read from the cited primary sources (published QJE PDF, NBER WP full text, Netspar PDF, Hanushek et al. online appendix). No figure is reported from memory. Dohmen et al. 2011's specific patience–risk correlation could not be verified and is flagged as such.*
