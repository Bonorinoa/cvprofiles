# Preprint triage — 2026-08-31

**Status:** working memo (not a freeze, not a contract amendment).
**Reviews absorbed:** Refine (2026-08-29) + Coarse.ink / Fable 5 (2026-08-30), both on current v9+ (Apps G–J present). No version drift.
**Horizon:** public methods preprint by 2026-09-30. Methods-journal submission 2026. Nature/PNAS-class empirical paper = different primary result on different data, early 2027. Dual-track lock unchanged.

**Internal grade (stricter than prior self-eval):** promising composition paper; not freeze-ready for Psychological Methods / Political Analysis as currently claimed. Coarse’s “major revision” is the right grade. The appendices (G, H, I, J) are stronger than the abstract.

---

## 0. What the reviews got right (do not bargain)

1. **Prospectivity is self-attested.** Abstract: “Screening is prospective and falsifiable.” §6.1: “This study was not preregistered.” App J documents that the confirmatory apparatus (demeaned cells, sensitivity grid, inadmissible-set profiling) was built after seeing how measures behave. A freeze hash pins a contract at a stated moment; it does not prove authorship was blind. Those two sentences cannot both stand at full strength.

2. **The band has no operating characteristics.** §3.5 makes it mandatory; App A.5 defers coverage theory. Synthetic DGPs are population-limit; “finite-sample engine check” is mentioned with no numbers. This is the largest methods-journal gap.

3. **The powered cell screen is one gate.** §5.2: cell networks “keep only the education implication”; holdout is rank-monotonicity in the same auxiliary. That is Pearson/Spearman of the same association. Proposition A.2’s “predictive content for unseen implications” is then nearly unfailable. Headline patience `{Q13, Llama, Phi}` / `[0.245, 0.556]` turns on that one implication. A one-restriction screen is not a Cronbach–Meehl nomological network.

4. **Trust headline fights App H Finding 4.** Cell β = Corr(m, GPS trust) after demeaning. GPS trust fails the country network (rule of law r = +0.12 vs 0.30; leftover education). Abstract still says Phi “points against the trust criterion it was meant to recover.” A negative correlation with an inadmissible column is not a failure of Phi. CLAIM_BOUNDARY already forbids calling Phi a valid trust measure; it does not yet forbid treating GPS trust as a validated criterion in the abstract.

5. **Contribution (ii) is not executed on real data.** Comparative claim (11) / Prop A.2 vs random, anchor-fit, predictive baselines: DGP D only, population limit. Section 5 reports leftover verdicts per measure, never the contrast.

6. **Mandatory §3.5 diagnostics are incomplete in the applications.** Boundary attribution (κ = 2) and frozen-vs-reformed M* contrast are defined, not tabled. Coupling is the paper’s named failure mode; Q13 is plausibly both near-boundary and range-defining.

7. **Cell bootstrap unit is wrong.** 480 cells nested in 42 countries; demeaning uses estimated country means; LLM columns share country-prompt components. Exchangeable-cell bootstrap + empty-rep = 0.000 is consistent with an optimistic scheme. CLAIM_BOUNDARY already desk-rejects “empty-rep = 0 means precise.”

8. **Two same-prompt open-weight columns are treated as menu expansion the paper warns against.** Patience range widens from Q13 singleton 0.245 to [0.245, 0.556] because both cheap columns clear one education bar. Baumann et al. are cited; no paraphrase study exists.

9. **Table 8 / synthesis row IV is internally false.** “Perseverance is anti-aligned at both levels (−0.33)” — −0.33 is App I’s Q13 country figure; Q14 is −0.59 / −0.53 / −0.36. For a paper that sells auditability, this is damaging.

10. **CRT nesting and causal composition (12) are asserted, not shown.** Campbell–Fiske and empty-R *are* computed. CRT and the union of identified sets are not.

Refine’s five detailed comments (population vs sample M*; Prop A.2 has no probability law over measures; δ not scale-invariant; Prop A.1 silent on empty R / empty M*; CRT) are correct and cheap to fix in Appendix A.

---

## 1. Ranking rule

Time pressure = (blocks September preprint) × (claim–evidence mismatch) × (cannot be parked as “companion / future”).
New scoring, new R, new microdata, and Nature-track work do **not** rank as September-preprint-blocking unless we reopen the freeze (we should not).

| Pri | Item | Why it is pressing | Lane | Owner |
|---|---|---|---|---|
| P0 | Downgrade “prospective / falsifiable” to auditable-conditional-on-the-stated-freeze; say not preregistered in abstract-adjacent prose | Abstract currently overclaims vs §6.1 | This week, prose | Augusto + agent |
| P0 | Relabel trust estimand: criterion-recovery of a *contested* criterion; soften abstract “points against the trust criterion”; align §5.4 / §6.6 with App H | Internal contradiction; CLAIM_BOUNDARY lock already points this way | This week, prose | Augusto (sentence lock) |
| P0 | Rescope cell application: one-gate screen; multi-restriction machinery is country-level (underpowered) | Contribution (ii) and “nomological network” currently overclaim | This week, prose | Augusto + agent |
| P0 | Reconcile every reported statistic; state menu composition behind every unrestricted range; fix Table 8 row IV | Auditability claim | This week, audit | Agent (verify vs freeze artifacts), Augusto signs |
| P0 | Author block: drop Monica / Kseniia; add Daniel J. Martin; CRediT as PLACEHOLDER until he agrees | Preprint cannot ship with wrong authors | This week, 1 email | Augusto |
| P1 | Population vs sample objects in §3.2 / App A (`s_r^0`, `M_0*`, `B_0*` vs hats) | Refine #1; load-bearing for any later MC | This week, notation | Agent draft, Daniel reviews |
| P1 | Prop A.1 empty-R / empty-M*; Prop A.2 finite-menu pass proportion + empty-set convention; δ-scale note | Refine #2–#4; math hygiene | This week, App A | Agent draft, Daniel reviews |
| P1 | Rename Table 3 “Coverage” → bootstrap-quantile / uncertainty band | Paper already disclaims CI; label fights the disclaimer | This week, 1 word | Agent |
| P1 | Mandatory diagnostics table on frozen cell profiles (slack margin, boot SE, κ=2 flag, reformed vs frozen-M* bands) | §3.5 promises it; coupling is Q13 | This week if artifacts exist; else next | Agent |
| P1 | Comparative falsification (11) on frozen cell scores vs random size-matched + best-β + single-anchor | Makes contribution (ii) true or converts it to a finding | This week design; run by mid-Sep | Agent compute, Augusto interprets |
| P2 | Country-cluster bootstrap, re-demeaning per replicate; report beside current band | Table 3 credibility | Spec this week; run mid-Sep | Agent |
| P2 | Small Monte Carlo under DGP B (coupling), n ∈ {50, 480}: empirical coverage of the band, empty-rep, vs Bonferroni union and sample-splitting | Largest methods-journal gap; does **not** require companion theory | Spec this week; execute Sep 8–21 | Agent |
| P2 | Leave-one-measure-out images of B* and unrestricted set (menu-sensitivity analog of App G) | A.1 does not guard curation; cheap on frozen scores | Mid-Sep | Agent |
| P2 | Soften CRT nesting to analogy **or** 1-page worked two-measure example; drop (12) to “future” **or** 1-page Manski union on {Q13, Llama, Phi} | Do not promise capabilities undemonstrated | Mid-Sep, one of each not both | Augusto chooses |
| P3 | Prompt-paraphrase + extra model family | Would unfreeze LLM columns that drive both headlines | **Not for Sept preprint.** New freeze. Park for methods R&R or Nature-track | — |
| P3 | Distinct held-out cell implications (age gradient, sex gap, discriminant vs cell risk) | Legitimate only if Augusto authors *before* seeing slacks, and preferably on **new** data; same-data add is circular | Daniel advises shape; Augusto authors; **not** same-freeze rescue | — |
| P3 | Public preregistration of a *fresh* application (WVS W8 / GPS micro / within-country trust R′) | Cannot retroactively preregister this freeze; OSF one-pager is a September *asset* only if Augusto authors R′ first | Nature-track / follow-up, not this preprint’s evidence | Augusto |
| P3 | Reliability-aware / precision layer in the engine | Named roadmap; DGP F already in paper; do not pretend it is done | Daniel specs; v3.1 | Daniel + agent later |
| P3 | Item-level multi-group invariance | App I already flags this; needs licensed microdata | Nature / extension | — |
| P3 | Causal composition (12) as a real application | Different paper (H-AIPW/Ghana is already parked outside the engine) | 2027 sibling | — |
| — | Social media / package marketing | Real, but not until P0 claim-alignment; do not market the current abstract | After preprint text is honest | Augusto |
| — | Seminar talks from the methods preprint | Fine in Q4 2026; do not wait for Nature | After preprint | Augusto |
| — | Nature/PNAS payload | Locked: new data, preregistered multi-op, live debate. Finding 3 still fails C1/C2/C5 | 2027 | Augusto authors R′ |

Forbidden (unchanged): move θ; recycle `[0.328, 0.402]`; call Phi a valid trust measure; promote country ranges to abstract; promote any grid R_i ≠ R0 to headline; costume-change this freeze into a Nature paper.

---

## 2. This week (2026-09-01 … 09-07)

Four outcomes, not a kitchen sink.

1. **Claim-alignment pass** on title-block, abstract, significance, contribution (ii), §5.2, §5.6, §6.6, Table 3 caption. Target: a psychometrician can read the abstract without catching us in a lie we already confess in §6.1 / App H / App J.
2. **Number-and-menu audit** against frozen run artifacts. Fix Table 8 row IV. State which columns sit in each unrestricted range.
3. **Daniel brief sent** (tasks below). Author-block placeholder in tex; CRediT not finalized.
4. **Spec sheets** (not necessarily executed) for: (a) comparative falsification on frozen cells, (b) country-cluster bootstrap with re-demeaning, (c) DGP-B Monte Carlo at n ∈ {50, 480}. Execution is mid-September.

Do **not** this week: re-score models, author a new cell network, implement the precision layer, draft Nature prose, start a marketing calendar.

---

## 3. Concrete tasks for Daniel J. Martin

He asked for concrete tasks. These are psychometric, bounded, and do not silently author the empirical R (Augusto owns every restriction and θ).

**T1 — Objects and propositions (week 1–2).** Review the population/sample split and Props A.1–A.2 after our notation patch. Specific questions: (i) is uniform weighting over a finite menu an acceptable law for the holdout claim, or should we drop the expectation and report only the finite-menu pass proportion? (ii) what should `[L,U]` be defined as when `M*=∅`? (iii) should δ>0 be forbidden unless slacks are normalized?

**T2 — What M* is allowed to mean (week 2).** Short memo (≤2 pages): given DGP F and identical θ applied to single items, composites, cell means, and deterministic LLM profiles, is the preprint’s honest interpretation “observed-score suitability for a declared use” rather than “latent construct alignment”? If yes, draft the two sentences that belong in §3.2 and §6.7. If no, say what bounded sensitivity would be required before Tables 3 and 6 can keep their current claims.

**T3 — One-gate screen (week 2).** Is a powered application that is explicitly a one-restriction education floor publishable as a demonstration of the *machinery*, provided we stop calling it a nomological network in the Cronbach–Meehl sense? If not, what is the cheapest *statistically distinct* holdout implication he would accept *in principle* (he does not author it; Augusto does, and not on this freeze).

**T4 — Trust application framing (week 2).** Choose one and write the abstract sentence: (A) criterion-recovery of a contested criterion (GPS trust is in β, and is itself inadmissible under R at country level); or (B) failed validity-argument stress test (cell education implication vs GPS recovery are anti-aligned, App H Finding 3). Not both. Not “the framework has bite” as the headline of that table.

**T5 — Precision-layer spec (October, not preprint-blocking).** Restriction-level note: how a reliability-aware slack should be defined so that θ remains researcher-owned and is not estimated by the engine. This is v3.1 / R&R material.

Out of scope for him: scoring new LLM columns; moving θ; Perwell as empirical demo; Nature-track R′; CRediT finalization until he accepts T1–T4.

---

## 4. Mid-September computations (agent-owned, freeze-preserving)

All three run on existing freezes or synthetic DGPs. No new empirical R. No θ change.

- Comparative falsification on cell scores: `p̂` for `M*_S` vs best-β, single-anchor, and 1,000 size-matched random subsets. If construct-guided selection does not beat the floor, that is a finding the framework claims to welcome — report it.
- Cluster bootstrap at country level, re-demean within replicate, n_boot = 1000, same seed family. Flag which of `[0.245, 0.556]`, empty-rep = 0, and Phi singleton survive.
- DGP-B Monte Carlo: coverage of the band for population `[L,U]`, empty-replicate rate, vs fixed-selection Bonferroni and sample-splitting, at n ∈ {50, 480}. Report operating characteristics; do not claim a theorem.

Prompt-paraphrase / third model family: **park**. It is the right robustness check and it is a new freeze. Doing it in September either delays the preprint or produces an unregistered sensitivity that App J will have to confess again.

---

## 5. What a September preprint is allowed to be

A methods preprint that:

- claims a **reporting composition** (CV × multiverse × PI) with a released engine;
- demonstrates the composition on two constructs at two resolutions, **including structured failure**;
- reports additive sampling diagnostics **without** simultaneous-coverage theory;
- is explicit that the powered screen is one gate, the freeze is auditable not blind, GPS trust is a contested criterion, and Llama/Phi are not two methods.

It is **not** allowed to claim: a new inferential theory; a Cronbach–Meehl network at cell level; prospective preregistration; that Phi refutes GPS trust; that empty-rep = 0 is precision.

That preprint can support Q4 2026 seminar talks and package-facing posts. It cannot support a Nature abstract. Nature still requires new data under a preregistered multi-operationalization design (standing scorecard: Finding 3 fails C1/C2/C5).
