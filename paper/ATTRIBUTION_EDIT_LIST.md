# Attribution edit list — 2026-10-19 (rev. 2)

**Purpose:** proposed edits to `paper/position_paper.tex` (v9, 1574 lines at commit `0524aa8`) for Augusto to accept, edit, or veto one item at a time. Nothing in the `.tex` has been changed, and `pdflatex` has not been run.

**Framing (Augusto, 2026-10-19):** the framework has credited Dell & Rambachan from the start. Their lecture was a call to action for new methods. This paper's contribution is to compose three methods (construct validation, multiverse reporting, and partial identification) into one practice that reliable empirical work needs, and to provide software that makes the best practices Dell and Rambachan emphasize easy to adopt anywhere in the inference pipeline. None of the individual methods is claimed. **Pass A therefore makes the existing credit precise:** it names the objects the deck defines, cites the deck itself, and softens only the claims a reader comparing the two texts would dispute. It does not restate the contributions.

**Lock:** frozen scores, networks, θ, run_ids, and every plug-in `[L,U]` stay as they are. Every number below is either already in the paper or was recomputed from committed data with the commands in §G.

**Not in scope:** moving θ; new restrictions; re-scoring; changing Table 3's plug-in values; logging decisions (these go into `logs/DECISIONS.md` after you accept items, as in `CLAIM_SHRINK_EDIT_LIST.md` Pass 6).

**Line numbers** refer to the current file. Each item quotes the current text verbatim. If several items are accepted, apply them bottom-up so the line numbers stay valid.

---

## Background

### Credit already in place

- The repo's first commit (`bc56870`, 2026-08-01) says "(Dell–Rambachan frame)" at `docs/03_Methodology.md:8`.
- Augusto's Substack post "Construct-Identified Inference" (2026-08-30) credits Dell & Rambachan for linking nomological networks to moment inequalities. This was verified by the session that commissioned this list; I did not re-check it.
- The paper cites them at §2.3 (l. 295), §3.1 (l. 391), and in the Tradition 3 box of the synthesis figure (l. 1535).

### What the deck defines, so the paper can name it

Dell & Rambachan, *Construct Validity: Credibility When Measurement Is Cheap*, NBER Methods Lecture slides (15 slides; the PDF metadata shows it was created 2026-07-30 and authored by Melissa Dell and Ashesh Rambachan; https://conference.nber.org/confer/2026/SI2026/ML/dell3.pdf). Checked on 2026-10-19 against the extracted slide text:

| Slide | Slide title (verbatim) | Content |
|---|---|---|
| 5 | AI Raises Important Construct Validity Concerns | Sala-i-Martin specification search moves to "searching across representations"; a construct-definition analogue of Goodhart's law |
| 6 | Construct Validity as Partial Identification | formalizing construct validity is "largely an open question"; outlines the Cronbach–Meehl network as partial identification |
| 8 | Candidate Measurement Functions | menu `M = (m_j(·))_{j∈J}`; β(m) defined consistently across candidates |
| 9 | Nomological Restrictions | convergent, discriminant, and known-groups restrictions with thresholds |
| 10 | The Admissible Set of Measures | `E[g_r(m(X),V;θ_r)] ≥ 0`; `M*_{R,θ}` ("a population object") |
| 11 | Construct-Validity Profiles | slacks `s_r(m;θ_r)` |
| 12 | The Construct-Identified Set | `B*_{R,θ} = {β(m) : m ∈ M*_{R,θ}}` |
| 13 | Inference for the Construct-Identified Range | `[L,U]`; admission and endpoint uncertainty are coupled near the boundary; "Estimation is beyond today's scope" |
| 14 | How Credible Are the Auxiliary Measures? | auxiliary credibility; Campbell–Fiske |

The companion review is NBER WP 35744 (September 2026, doi 10.3386/w35744). It gives the partial-identification analogy in prose (§2.2, p. 8). The call to action the software answers is in §3.2 (pp. 13–14): "We are now building toolkits that provide the same discipline for AI-generated measurements." The WP has no formal M\*, profiles, or B\*.

### What needs fixing

- The bib entry cites the lecture-series title, not the deck.
- §1.4 presents the deck's objects without saying that the deck names them.
- Two §2.3 sentences ("nearest formal neighbor"; "None performs menu-level validation with a surviving set") would be disputed by a reader who also knows Ogut & Yin.
- The sentence at l. 295 contains a phrase I could not find in the deck: "principled, widely accepted methods for construct validity".

### Reviewer notes (not edits; your call)

- WP 35744 §2.2 uses trust as its example and says a trust measure should not "simply reproduc[e] institutional quality". The country trust network uses rule of law as a *convergent* floor (l. 654). One sentence at l. 654–655 explaining why rule of law is convergent evidence rather than contamination would head off the comparison.
- Title echo (optional): "When Measures Are Cheap" sits close to the deck's "When Measurement Is Cheap". With A1 in place I do not think this is a real risk. Rename only if you want distance.

### Notation map (for the optional item A-opt1)

| Object | Dell–Rambachan | Paper now | Package |
|---|---|---|---|
| Threshold | `θ_r` | `τ_r` | `theta`, `theta_grid.json` |
| Known-groups threshold | `δ` (inside `θ`) | — | — |
| Admission tolerance | — | `δ` | `delta` |
| Admissible set | `M*_{R,θ}` (population) | `M*` (sample); `𝓜*_0` (population, App A) | `admissible.json` |
| Slack | `s_r(m;θ_r)` | `s_r(m)`, `s_r^0(m)` | `slacks.csv` |
| Image | construct-identified set `B*_{R,θ}` | robust result set / admissible-result set `B*` | `range.json` |

---

## Pass A — Precise attribution (required item 1)

### A1. Abstract (l. 92)

**Current**
```tex
This paper develops \emph{construct-identified inference}, a reporting discipline for that abundance.
```
**Proposed**
```tex
This paper develops \emph{construct-identified inference}, a reporting discipline for that abundance that builds on Dell and Rambachan's formalization of construct validity as partial identification over a menu of measures (2026 NBER Methods Lecture).
```
**Why:** a reader who knows the lecture looks for the link in the abstract first. One clause supplies it. Psychological Methods abstracts carry no `\cite`, so the source is named in prose.

### A2. §1.4 "Four objects" — name the deck's objects (ll. 209, 220, 225, 230)

**l. 209 — current**
```tex
The framework needs four objects.
```
**Proposed**
```tex
The framework needs four objects; the menu, admissible set, slack profiles, and construct-identified set and range below follow the definitions in Dell and Rambachan's Methods Lecture~\cite{dellrambachan2026}, restated with sample slacks.
```
**l. 220 — current**
```tex
Remaining measurement choice is then propagated into the result: the robust result set is the image of the estimand over survivors,
```
**Proposed**
```tex
Remaining measurement choice is then propagated into the result: the robust result set (Dell and Rambachan's construct-identified set) is the image of the estimand over survivors,
```
**l. 225 — current**
```tex
summarized for a scalar estimand by its range,
```
**Proposed**
```tex
summarized for a scalar estimand by its range (their construct-identified range),
```
**l. 230 — current**
```tex
Equations~\eqref{eq:admissible-set}--\eqref{eq:headline-range} define the admissible set, the robust result set, and the headline range.
```
**Proposed**
```tex
Equations~\eqref{eq:admissible-set}--\eqref{eq:headline-range} define the admissible set, the robust result set, and the headline range; the per-restriction slacks $s_r(m)$ are what Dell and Rambachan call construct-validity profiles.
```
**Why:** §1.4 is where a reader compares the two frameworks object by object. Naming the objects the way the deck does makes that comparison immediate. The paper's own terms ("robust result set", "headline range") stay.

### A3. §1.5 contributions (i) and (iv) (ll. 240, 248)

**l. 240 — current**
```tex
$\Bset^*$ is the image of the estimand over measures that survive a declared validity argument, not an unrestricted multiverse; fragility and robustness are therefore attributed to the right cause.
```
**Proposed**
```tex
$\Bset^*$, Dell and Rambachan's construct-identified set~\cite{dellrambachan2026}, is reported as the image of the estimand over measures that survive a declared validity argument, beside the unrestricted multiverse; fragility and robustness are therefore attributed to the right cause.
```
**l. 248 — current**
```tex
The method ships in the released package \cvp{}~3.0.2~\cite{cvprofiles}.
```
**Proposed**
```tex
The method ships in the released package \cvp{}~3.0.2~\cite{cvprofiles}, which turns the Dell--Rambachan objects into a frozen, auditable workflow.
```
**Why:** both contributions stay as they are: the composition (the screened image reported beside the multiverse) and the software. Each now says which object it builds on.

### A4. §2.2 extreme-bounds paragraph (l. 289, opening clause)

**Current**
```tex
This paper's screen is the admissibility test EBA lacked, moved from specifications to measurement functions: ...
```
**Proposed**
```tex
Dell and Rambachan draw the same parallel to specification search~\cite{dellrambachan2026,dellrambachan2026wp}; this paper's screen is the admissibility test EBA lacked, moved from specifications to measurement functions: ...
```
**Why:** slide 5 and the WP's introduction both make the Sala-i-Martin parallel. A reader who has seen either will notice if it goes uncredited.

### A5. §2.3 — the core sentences (ll. 295–299)

**l. 295 — current**
```tex
In the 2026 NBER Summer Institute Methods Lectures, \emph{Estimation and Inference with AI-Generated Data}, Dell and Rambachan frame the nomological network as partial identification under theoretically motivated moment restrictions---Dell on measurement and construct validity, Rambachan on multiple measurements and data fusion---and explicitly call for principled, widely accepted methods for construct validity~\cite{dellrambachan2026}.
```
**Proposed**
```tex
In their 2026 NBER Methods Lecture, \emph{Construct Validity: Credibility When Measurement Is Cheap}, Dell and Rambachan formalize the nomological network as partial identification under theoretically motivated moment restrictions: they define the candidate menu, the admissible set $\M^*_{\Rset,\theta}$, construct-validity profiles of slacks, and the construct-identified set and range $[L,U]$, note that admission and endpoint uncertainty are coupled, and leave estimation beyond the lecture's scope~\cite{dellrambachan2026}; their companion review calls for toolkits that give AI-generated measurement the discipline causal-inference toolkits gave specification choice~\cite{dellrambachan2026wp}.
```
**Why:**
- This names the deck and lists the specific objects it defines.
- It replaces "principled, widely accepted methods", which I could not find in the deck, with the WP's verifiable call to action (§3.2, p. 14). If that phrase comes from the talk or another deck, cite that source and keep it.
- It drops "Dell on …, Rambachan on …", because this deck is co-authored. If the split describes the lecture series, it belongs to a different citation.

**l. 296 — current**
```tex
The nearest formal neighbor is Chen, Rambachan, and Tamer, whose restrictions are benchmark-informed bounds on error correlation for a downstream parameter~\cite{chenrttamer2026}.
```
**Proposed**
```tex
A closely related formal treatment is Chen, Rambachan, and Tamer, whose restrictions are benchmark-informed bounds on error correlation for a downstream parameter~\cite{chenrttamer2026}.
```
**l. 297 — current**
```tex
The present framework differs in the object of inference: our restrictions are menu-level nomological moment inequalities, the surviving set $\M^*$ is the object, and the selection rule is held-out falsifiable.
```
**Proposed**
```tex
The present framework differs in the object of inference: following Dell and Rambachan, the restrictions are menu-level nomological moment inequalities and the surviving set $\M^*$ is the object; the selection rule is in addition held-out falsifiable.
```
**l. 298 — current (first clause)**
```tex
Other recent work occupies adjacent territory without a surviving set: Ogut and Yin derive curvature bounds from multiple nonlinear measurements~\cite{ogutyin2026}; Messing shows ...
```
**Proposed**
```tex
Ogut and Yin are the nearest empirical analogue: six AI-exposure measures, an ex ante factor-analytic rule that retains five, and Imbens--Manski confidence intervals with the Stoye critical value that attain uniform coverage over their curvature class~\cite{ogutyin2026}; their screen is a measurement-model rule rather than a declared nomological network, and their inference is stronger than the additive band used here.
Other recent work occupies adjacent territory without a surviving set: Messing shows ...
```
(The rest of l. 298, from "Messing shows" onward, is unchanged.)

**l. 299 — current**
```tex
None performs menu-level validation with a surviving set and a falsifiable selection rule.
```
**Proposed**
```tex
To our knowledge none combines a declared nomological screen, a held-out stage that can fail, and the unrestricted image reported beside the screened one.
```
**Why:** these are the two claims a comparing reader would dispute. Ogut–Yin *do* screen a menu down to survivors (five of six measures), and they report uniform-coverage inference. Also, "nearest formal neighbor" undersells the deck, which is nearer than Chen–Rambachan–Tamer. The new l. 299 still states what is distinctive here, which is the composition.

### A6. §2.7 synthesis (l. 316)

**Current**
```tex
The composition those traditions do not jointly supply is the map $\Rset(C)\to\M^*(\Rset)\to\Bset^*(\Rset)$, drawn with a return arrow: observed disagreement among measures can motivate revision of $C$ or $\Rset$ for future studies.
```
**Proposed**
```tex
Dell and Rambachan formalize the map $\Rset(C)\to\M^*(\Rset)\to\Bset^*(\Rset)$~\cite{dellrambachan2026}; the composition the three traditions do not jointly supply is that map reported beside the unrestricted multiverse and drawn with a return arrow: observed disagreement among measures can motivate revision of $C$ or $\Rset$ for future studies.
```
**Why:** the map itself is slides 10–12, so a reader comparing the texts would dispute "do not jointly supply the map". What the paper adds is the composition: the map placed beside the multiverse, with the return arrow. Ll. 317–318, which state the composition as the contribution, are unchanged.

### A7. §3.1 notation sentence (l. 391, end)

**Current**
```tex
... following the classical validation tradition~\cite{cronbach1955,campbell1959} and its recent partial-identification reading~\cite{dellrambachan2026}.
```
**Proposed**
```tex
... following the classical validation tradition~\cite{cronbach1955,campbell1959} and Dell and Rambachan's partial-identification formalization of it~\cite{dellrambachan2026}, whose objects and names this paper follows.
```

### A8. §3.5 coupling (ll. 559, 574)

**l. 559 — current**
```tex
The fixed-selection literature takes the admissible set as given~\cite{imbensmanski2004,stoye2009}; here selection is estimated.
```
**Proposed**
```tex
The fixed-selection literature takes the admissible set as given~\cite{imbensmanski2004,stoye2009}; here selection is estimated, the coupling Dell and Rambachan flag when they note that partial-identification and endpoint-inference methods could be combined into a valid, if conservative, region~\cite{dellrambachan2026}.
```
**l. 574 — current**
```tex
The documented failure regime is coupling: a near-boundary measure that is also $\beta$-extreme couples admission with the endpoints, because its inclusion or exclusion moves the range directly.
```
**Proposed**
```tex
The failure regime is coupling, as Dell and Rambachan note: a near-boundary measure that is also $\beta$-extreme couples admission with the endpoints, because its inclusion or exclusion moves the range directly.
```
**Why:** "documented" asks the reader to supply a source, and the source is slide 13.

### A9. §4 implementation (l. 597)

**Current**
```tex
\cvp{} is the open Python implementation of the measurement-selection layer~\cite{cvprofiles}.
```
**Proposed**
```tex
\cvp{} is the open Python implementation of the measurement-selection layer~\cite{cvprofiles}: it computes Dell and Rambachan's objects---construct-validity profiles, the admissible set, and the construct-identified range---from a frozen score table.
```
**Why:** this states the positioning directly: the tool that operationalizes their objects. The package name comes from slide 11.

### A10. Appendix A opening (insert after l. 1031)

**Proposed insertion** (new first line of `\section{First-principles formalization}`):
```tex
Definitions~A.1--A.3 restate Dell and Rambachan's objects with sample analogues~\cite{dellrambachan2026}.
```

### A11. Bibliography — fix one entry, add one

**l. 935 — current**
```tex
\bibitem{dellrambachan2026} Dell, M., \& Rambachan, A. (2026). \textit{Estimation and inference with AI-generated data} [Paper presentation]. NBER Summer Institute 2026 Methods Lectures.
```
**Proposed**
```tex
\bibitem{dellrambachan2026} Dell, M., \& Rambachan, A. (2026a). \textit{Construct validity: Credibility when measurement is cheap} [Lecture slides]. NBER Summer Institute 2026 Methods Lectures. https://conference.nber.org/confer/2026/SI2026/ML/dell3.pdf

\bibitem{dellrambachan2026wp} Dell, M., \& Rambachan, A. (2026b). \textit{The measurement revolution? Credible measurement and inference in the age of AI} (NBER Working Paper No. 35744). National Bureau of Economic Research. https://doi.org/10.3386/w35744
```
**Why:** the deck title on the title slide and in the PDF metadata is "Construct Validity: Credibility When Measurement Is Cheap". APA 7 requires the a/b suffixes for same-author, same-year works, ordered by title ignoring "The": "Construct…" comes before "Measurement…". Verified: WP title, authors, September 2026, No. 35744, and the DOI (NBER page and Crossref).

### Optional (one line each; skip freely)

- **A-opt1. Notation τ → θ.** 23 occurrences of `\tau` (`grep -n '\\tau' paper/position_paper.tex`). This would match the deck and the package's `theta`. If you do it, add a footnote at l. 434: "Dell and Rambachan use $\delta$ for the known-groups threshold; here $\delta$ is the admission tolerance."
- **A-opt2. Rename "robust result set" to "construct-identified set"** at ll. 153, 220, 230, 360, 598, 1169. With A2's parentheticals this is cosmetic.
- **A-opt3. Goodhart (l. 852).** Prepend "Dell and Rambachan name a construct-definition analogue of Goodhart's law~\cite{dellrambachan2026};" (slide 5).
- **A-opt4. Synthesis table row III (l. 1565), Key Literature cell.** Add `Dell \& Rambachan~\cite{dellrambachan2026};` before Imbens & Manski.

---

## Pass B — Missing literature (required item 2)

Every DOI and arXiv ID was resolved on 2026-10-19 (commands in §G.2). Insert each bib entry at the alphabetical position given.

### B0. Bib entries

| Key (new) | Insert after line | Entry |
|---|---|---|
| `akm2024` | 913 (after `aghion2010`) | `\bibitem{akm2024} Andrews, I., Kitagawa, T., \& McCloskey, A. (2024). Inference on winners. \textit{Quarterly Journal of Economics, 139}(1), 305--358. https://doi.org/10.1093/qje/qjad043` |
| `bcs2015` | 921 (after `borsboom2004`) | `\bibitem{bcs2015} Bugni, F.~A., Canay, I.~A., \& Shi, X. (2015). Specification tests for partially identified models defined by moment inequalities. \textit{Journal of Econometrics, 185}(1), 259--282. https://doi.org/10.1016/j.jeconom.2014.10.013` |
| `clr2013` | 929 (after `chenrttamer2026`) | `\bibitem{clr2013} Chernozhukov, V., Lee, S., \& Rosen, A.~M. (2013). Intersection bounds: Estimation and inference. \textit{Econometrica, 81}(2), 667--737. https://doi.org/10.3982/ECTA8718` |
| `desai2026bench` | 937 (after `desai2026`) | `\bibitem{desai2026bench} Desai, M., Truong, S.~T., Wallach, H., Chouldechova, A., Cooper, A.~F., Garcia-Gathright, J., Ho, D.~E., Jacobs, A.~Z., Koyejo, S., Pangakis, N., \& Wang, A. (2026). \textit{What AI benchmarks actually measure: Adapting convergent and discriminant validity to interrogate fifty-six AI benchmarks} [Preprint]. arXiv. https://arxiv.org/abs/2609.08812` |
| `frd2019` | 947 (after `falkhermle2018`) | `\bibitem{frd2019} Fisher, A., Rudin, C., \& Dominici, F. (2019). All models are wrong, but many are useful: Learning a variable's importance by studying an entire class of prediction models simultaneously. \textit{Journal of Machine Learning Research, 20}(177), 1--81. https://jmlr.org/papers/v20/18-760.html` |
| `mastenpoirier2020` | 991 (after `manski2003`) | `\bibitem{mastenpoirier2020} Masten, M.~A., \& Poirier, A. (2020). Inference on breakdown frontiers. \textit{Quantitative Economics, 11}(1), 41--111. https://doi.org/10.3982/QE1288` |
| `mastenpoirier2021` | 991 (after the 2020 entry) | `\bibitem{mastenpoirier2021} Masten, M.~A., \& Poirier, A. (2021). Salvaging falsified instrumental variable models. \textit{Econometrica, 89}(3), 1449--1469. https://doi.org/10.3982/ECTA17969` |
| `okubo2026` | 1001 (after `ogutyin2026`) | `\bibitem{okubo2026} Okubo, S. (2026). \textit{A multiverse of good and bad controls: Candidate causal graphs for interpreting model robustness analysis} [Preprint]. arXiv. https://arxiv.org/abs/2609.16618` |
| `westenrosenthal2003` | 1019 (after `wallach2025`) | `\bibitem{westenrosenthal2003} Westen, D., \& Rosenthal, R. (2003). Quantifying construct validity: Two simple measures. \textit{Journal of Personality and Social Psychology, 84}(3), 608--618. https://doi.org/10.1037/0022-3514.84.3.608` |

Notes:
- **Key collision.** `desai2026` already exists (Desai, Card & Jacobs, arXiv 2607.07915, cited at l. 183). The benchmark paper therefore needs its own key, `desai2026bench`. APA orders the two by second author (Card before Truong).
- **AKM year.** Crossref gives an online date of 2023 and a print issue of January 2024. APA cites the issue year, 2024.
- **CLR authors.** Crossref's record has no author field. The authors were confirmed from the Econometric Society page and arXiv 0907.3503.
- **Ogut–Yin spelling.** The bib (l. 1001) has `O\u{g}ut, B.`, but arXiv metadata gives "Burhan Ogut". Check the PDF byline and match it.
- **Concurrency.** Okubo (posted 2026-09-15) and Desai et al. (2026-09-08) appeared after the v9 draft (August 2026). Cite them as concurrent work.

### B1. §2.3 — inference toolkit for ranges (insert after l. 293)

**l. 293 — current (end)**
```tex
... confidence sets for partially identified parameters extend the logic to sampling uncertainty~\cite{imbensmanski2004,stoye2009}.
```
**Proposed insertion after it**
```tex
Inference on ranges of this kind has a developed toolkit: inference on intersection bounds treats extrema of estimated functions and shows that plug-in extrema are biased in finite samples~\cite{clr2013}; the estimand of the candidate that attains an endpoint is a selected winner, for which conditional and hybrid corrections exist~\cite{akm2024}; and the weakest assumptions under which a conclusion survives define a breakdown frontier~\cite{mastenpoirier2020}.
```
**Why:** these are the endpoint-inference and partial-identification methods that slide 13 says "can be combined". An econometrics referee will expect them. One note for you, not for the text: over a fixed admissible set, the plug-in max is biased up and the plug-in min biased down (E max ≥ max E), so the plug-in `[L,U]` tends to be too wide, not too narrow.

### B2. §3.2 — empty admissible set as a specification-test event (l. 440)

**Current**
```tex
An empty admissible set is a valid finding: it rejects the pair $(\M,\Rset)$ as an operationalization of $C$, not $C$ itself.
```
**Proposed**
```tex
An empty admissible set is a valid finding: it rejects the pair $(\M,\Rset)$ as an operationalization of $C$, not $C$ itself.
Read with the menu index as the parameter, $\M^*$ is the identified set of a moment-inequality model, and $\M^*=\emptyset$ is the event a specification test for such models targets~\cite{bcs2015}; the plug-in screen reports that event without the test's size control.
```

### B3. §3.3 — the range as a Rashomon-set object (after l. 480)

**Proposed insertion after l. 480**
```tex
Structurally, $[L,U]$ resembles model class reliance: the range of a functional over the Rashomon set of models whose loss clears a threshold~\cite{frd2019}; here admission is by declared validity restrictions rather than predictive loss.
```

### B4. §2.2 — licensed versus pooled multiverse (after l. 283)

**Proposed insertion after l. 283**
```tex
Okubo makes the same separation for control sets, reporting robustness within the specifications each candidate causal graph licenses and splitting pooled dispersion into within- and between-graph parts~\cite{okubo2026}; the unrestricted and screened images here are the measurement-layer analogue.
```

### B5. §2.1 — quantified nomological fit (after l. 263)

**Proposed insertion after l. 263**
```tex
Westen and Rosenthal quantified that logic, scoring how closely a measure's observed correlations track a predicted pattern~\cite{westenrosenthal2003}; the restrictions here keep the predicted pattern but replace a single fit index with per-implication thresholds and a surviving set.
```
**Why:** Psychological Methods reviewers will know Westen & Rosenthal. Leaving it out invites the comment "this already exists in our field".

### B6. App G (`app:netsens`) — breakdown points (after l. 1374)

**Proposed insertion after l. 1374**
```tex
The floors at which a conclusion changes---between $0.25$ and $0.30$ for the patience lower endpoint, between $0.10$ and $0.15$ for the sign of the trust range, and between $0.30$ and $0.40$ for trust admissibility---are breakdown points in the sense of Masten and Poirier~\cite{mastenpoirier2020}, reported here descriptively without their inference.
```
(These are read off Table 9 (`tab:netsens`) rows $\Rset_0$–$\Rset_5$; there are no new numbers.)

### B7. §6.2 — principled relaxation versus rescue (l. 833)

**Current**
```tex
All of these outcomes are scientifically interpretable, and none should be tuned away by relaxing $\delta$ after seeing the result.
```
**Proposed**
```tex
All of these outcomes are scientifically interpretable, and none should be tuned away by relaxing $\delta$ after seeing the result.
Masten and Poirier show how to relax jointly falsified assumptions in a principled way, by reporting the frontier of least relaxations that are not refuted~\cite{mastenpoirier2021}; a pre-declared report of that kind is compatible with this policy, while loosening $\delta$ or $\theta$ to rescue the current set is not.
```

### B8. App C — benchmarks (after l. 1251)

**Proposed insertion after l. 1251**
```tex
Desai et al.\ run the convergent--discriminant half of that design on 56 capability and safety benchmarks across 53 models, finding weak convergence among benchmarks assigned the same safety concept and poor discrimination among capability concepts~\cite{desai2026bench}.
```

### B9. Ogut & Yin (already cited)

Their description is corrected in A5. Accurate summary from the arXiv abstract: six exposure measures; a sign change in the post-2022 employment coefficient between the language-model measures and the Webb patent-text measure; an ex ante factor-analytic rule that sets Webb apart as a distinct construct; a consensus coefficient from the five retained measures; and Imbens–Manski CIs with the Stoye critical value, with uniform coverage over the curvature class including the point-identified boundary.

---

## Pass C — Trust criterion self-consistency (required item 3)

**Recomputed** (§G.1, cvprofiles 3.0.2, committed `data/cells_demeaned/*_llm_extension.csv`, frozen networks `networks/{patience,trust}_cells_llm.yaml`). Each criterion was scored as if it were a menu member:

| Criterion (β outcome, not in M) | Corr with `q275_cell` | Select slack (`corr_min`, θ=0.20) | Holdout slack (`monotone_rank`, θ=0.15) | Would pass? |
|---|---|---|---|---|
| `gps_patience_cell` | +0.475 | +0.275 | +0.315 | yes |
| `gps_trust_cell` | −0.235 | −0.435 | −0.386 | **no** |

For menu members the same script reproduces the frozen runs' `slacks.csv` and `beta_values.json` to three decimals (patience run_id `02005bf2…`, trust run_id `9461b368…`).

### C1. §5.4 sentence (insert after l. 708)

**l. 708 — current**
```tex
\GPS{} trust itself fails rule of law at country level ($r=0.12$ versus floor $0.30$), so the cell $\beta$ is criterion-recovery of that contested column, not a refutation of a validated criterion.
```
**Proposed insertion after it**
```tex
The criterion also fails the cell screen it is used to calibrate: scored as if it were a menu member under the frozen cell network, \GPS{} trust correlates $-0.235$ with demeaned cell education (select slack $-0.435$; leftover $-0.386$), whereas \GPS{} patience correlates $+0.475$ and passes (slack $+0.275$; leftover $+0.315$; Table~\ref{tab:celldiag}).
```
**Optional second sentence** (heads off a "mechanical artifact" reading):
```tex
The education channel alone would imply a Phi $\beta$ of only $0.349\times(-0.235)=-0.082$; holding cell education fixed, Phi's association with \GPS{} trust is still $-0.258$, so the floor does not by itself produce the negative sign.
```

### C2. Table cell — `tab:celldiag` (two rows; after l. 773 and after l. 783)

**After l. 773** (`noise` row, patience panel):
```tex
\GPS{} patience (criterion, not in $\M$) & --- & --- & $0.275$ & $0.315$ & --- & --- & --- & --- \\
```
**After l. 783** (`noise` row, trust panel):
```tex
\GPS{} trust (criterion, not in $\M$) & --- & --- & $-0.435$ & $-0.386$ & --- & --- & --- & --- \\
```
**Caption addendum** (end of l. 761, before `}`):
```tex
Criterion rows score the $\beta$ outcome against the same network for reference; it is not a menu member and enters no range.
```
**Why:**
1. The paper's only evidence that the trust criterion is contested is currently a country-level number (r = 0.12 against rule of law). This adds the same finding at the powered resolution, under the exact network that produced the headline.
2. It explains App H (`app:inadmissible`) Finding 3 (education slack and β anti-aligned at −0.80) at the level of design: the auxiliary that admits measures and the criterion that scores them point in opposite directions inside countries. Any measure that tracks the criterion inherits a negative education association.
3. The patience criterion passes, so the design is internally coherent for patience and not for trust. That is the clean contrast between the two constructs.
4. It follows WP 35744 §2.2: when theory is weak, misalignment can count against the theory rather than the measure.

**Alternative placement:** a column in Table 3 (`tab:twores`) headed "\GPS{} criterion vs.\ bar", with values `$0.475$ (passes)` and `$-0.235$ (fails)`. Table 3 is the headline table under the CLAIM_SHRINK lock, so I recommend `tab:celldiag` instead.

---

## Pass D — Education-proxy objection (required item 4)

**Recomputed** (§G.1; patience cells, n = 480; corr of the criterion with education = 0.475):

| Measure | In M\* | Corr(m, `q275_cell`) | Cell β | β implied by education alone (corr_edu × 0.475) | Partial corr(m, GPS \| `q275_cell`) |
|---|---|---|---|---|---|
| Phi | yes | 0.640 | 0.556 | 0.304 | 0.373 |
| Llama | yes | 0.522 | 0.417 | 0.248 | 0.225 |
| Q13 | yes | 0.251 | 0.245 | 0.119 | 0.148 |
| Q14 | no | −0.364 | −0.326 | −0.173 | −0.186 |
| composite | no | −0.050 | −0.027 | −0.024 | −0.004 |
| noise | no | −0.031 | −0.003 | −0.015 | 0.013 |
| GPS anchor (criterion) | — | 0.475 | — | — | — |

Pooled sex-by-age-band dummies explain R² = **0.590** of demeaned cell education. Cells are sex × age band within country, and the persona names sex and age band (App E, l. 1274).

### D1. §5.4 paragraph (insert after l. 702)

**l. 702 — current**
```tex
The patience range widens from the Q13 singleton $0.245$ to $[0.245,0.556]$ because both cheap columns clear one education bar under identical prompts---menu expansion under correlated generators, which Section~1.2 already flags as weak validity evidence.
```
**Proposed insertion after it**
```tex
A natural objection is that the cheap columns clear the education bar because they encode education rather than patience.
The persona names sex and age band, and a sex-by-age pattern shared across countries explains 59\% of the variance in demeaned cell education, so a model that knows cohort education gradients can pass the gate without tracking patience.
The data support part of the objection: Phi and Llama correlate with cell education at $0.640$ and $0.522$, above the $0.475$ of the \GPS{} patience criterion itself, and a one-gate education screen rewards exactly that loading.
They do not support all of it: holding cell education fixed, the partial correlations with \GPS{} patience stay positive and keep their order (Phi $0.373$, Llama $0.225$, Q13 $0.148$), against zero-order $\beta$ of $0.556$, $0.417$, and $0.245$.
The upper part of $[0.245,0.556]$ therefore includes an education-shared component; the partials are a diagnostic, not a replacement for the frozen estimand.
```
**Why:** a reviewer will raise this objection first, because the only cell gate is education and the LLM persona carries the cohort. Conceding the part the data support (the cheap columns load on education more heavily than the criterion does) and showing the part they do not (the partials stay positive and ordered) is stronger than leaving the objection unaddressed. Nothing frozen moves: the partials are reported beside the plug-in β, not in its place.

---

## Pass E — Monotonicity proposition for Appendix A (required item 5)

### E1. New subsection after Prop. A.3 (insert after l. 1138)

Inserting it after `prop:holdout` keeps Props. A.1–A.3 and Definitions A.1–A.4 numbered as they are. The main text cites "Definitions~A.1--A.3" (l. 304) and "Assumption~A.2" (ll. 442, 668) by hard-coded number.

```tex
\subsection{Monotonicity in the menu and the network}
Fix the units, the tolerance $\delta$, and a universe $\mathcal{U}$ of candidate measures.
Call $\Rset$ \emph{menu-separable} if every $g_r$ depends on the data only through the candidate's own score $m(X)$ and auxiliaries $V$ that are not members of $\mathcal{U}$, so that $s_r(m)$ is defined without reference to any other candidate and $\Rset$ does not change when the menu does.
Write $\M^*(\M,\Rset)$ and $\Bset^*(\M,\Rset)$ for the admissible set and its image.

\begin{proposition}[Monotonicity and single-entry breakdown]
\label{prop:monotone}
Let $\Rset\subseteq\Rset'$ be menu-separable and $\M\subseteq\M'\subseteq\mathcal{U}$.
\begin{enumerate}[label=(\roman*)]
\item \emph{Menu monotonicity:} $\M^*(\M,\Rset)=\M^*(\M',\Rset)\cap\M$; hence $\M^*(\M,\Rset)\subseteq\M^*(\M',\Rset)$.
\item \emph{Network antitonicity:} $\M^*(\M,\Rset')\subseteq\M^*(\M,\Rset)\subseteq\M^*(\M,\emptyset)=\M$.
Tightening any threshold (raising a floor or lowering a ceiling) or lowering $\delta$ likewise weakly shrinks $\M^*$.
\item \emph{Range nesting:} $\Bset^*$ inherits (i)--(ii).
Whenever the smaller admissible set is non-empty,
$[L,U](\M,\Rset)\subseteq[L,U](\M',\Rset)$ and
$[L,U](\M,\Rset')\subseteq[L,U](\M,\Rset)\subseteq\bigl[\min_{m\in\M}\beta(m),\max_{m\in\M}\beta(m)\bigr]$;
so $U-L$ is non-decreasing as the menu grows and non-increasing as restrictions are added.
\item \emph{Single-entry breakdown:} for any $b\in\mathbb{R}$, adding one measure $m^+$ with $\min_{r}s_r(m^+)\ge-\delta$ and $\beta(m^+)=b$ gives
$[L,U](\M\cup\{m^+\},\Rset)=[\min(L,b),\max(U,b)]$, or $\{b\}$ when $\M^*(\M,\Rset)=\emptyset$.
The screen constrains which entries are admitted, not where an admitted entry places the endpoints.
\end{enumerate}
The same statements hold for $\mathscr{M}_0^*$ and $\mathscr{B}_0^*$ with $s_r^0$ in place of $s_r$.
\end{proposition}
\begin{proof}
Under separability, $m\in\M^*(\M,\Rset)$ if and only if $m\in\M$ and $\min_{r\in\Rset}s_r(m)\ge-\delta$ (a minimum over $\Rset=\emptyset$ is $+\infty$, as in Proposition~\ref{prop:empty}).
The condition involves no other menu member, which gives (i); a minimum over a larger index set is weakly smaller, and each slack is monotone in its own threshold, which gives (ii).
Images of nested sets are nested, and a minimum or maximum over a superset is weakly more extreme, which gives (iii).
(iv) is (i) with $\M'=\M\cup\{m^+\}$.
\end{proof}

\begin{remark}[When separability fails]
If restrictions name menu members as partners---the Campbell--Fiske cells of Section~\ref{sec:app-special}, or a rank-agreement restriction against an in-menu anchor---adding an instrument adds restrictions that name it, so the menu and the network grow together, (i) and (ii) pull in opposite directions, and under the engine's global $\M^*$ an existing survivor can be ejected by a new member.
Menu growth that changes the unit set, for example an inner join that drops units lacking the new column, changes every slack and is likewise not covered.
\end{remark}

\begin{remark}[What the proposition implies for protocol]
By (i) and (iv), the menu is a researcher degree of freedom with no counterweight inside the screen: adding admissible columns can only widen $[L,U]$, and one admitted column can move either endpoint anywhere.
The freeze must therefore pin the score matrix---hence the menu---together with $\Rset$ and the thresholds, before $\beta$ is inspected; the run-id hash of Section~\ref{sec:impl} does so.
By (ii), held-out restrictions can only remove survivors, so $\Rset_H$ is the one place where an entry admitted on $\Rset_S$ can be challenged, and a generator must not see it.
A generator trained against a known $\Rset_S$ produces columns admissible by construction; by (iv) it can place either endpoint arbitrarily (the Goodharting failure of Section~\ref{sec:discussion}).
Leave-one-measure-out (Appendix~\ref{app:loo}) and boundary attribution measure exactly the single-entry dependence in (iv): dropping Phi empties the trust set and moves the patience upper endpoint from $0.556$ to $0.417$.
The patience range widening from the Q13 singleton to $[0.245,0.556]$ when the two cheap columns enter (Section~\ref{sec:app-cells}) is an instance of (iii), and the nested sets of Table~\ref{tab:netsens} are an instance of (ii).
\end{remark}
```
**Why:** the brief asks for it. It also does three useful things.
- It makes the "unrestricted beside screened" contrast exact: [L,U] ⊆ the unrestricted range, by (iii).
- It explains the pattern already reported in App G (`tab:netsens`), where sets shrink monotonically as θ_edu rises, and in the LOMO table of App I (`tab:loo`).
- It turns the freeze and Goodharting paragraphs from procedural advice into consequences of a stated result.

(ii) is the formal version of WP 35744 §2.2's remark that added restrictions narrow the set of plausible measures. Cite it there if you want: `\cite{dellrambachan2026wp}`.

**Engine check behind the separability claim:** `src/cvprofiles/identify/slacks.py` computes every slack column by column, from the candidate and one named frame column (`slack_matrix`, l. 138). Admission is `min slack ≥ −δ` (`identify/pipeline.py` l. 209). In the engine, therefore, separability fails only when a restriction's partner column is itself a menu member, as in `evals/composition_special_cases/networks/mtmm_patience_trust.yaml`.

**Numbers in the remark:** these are already in the paper: the LOMO table (`tab:loo`, App I) rows "Phi" give `[0.245,0.417]` and `empty`, and Table 9 (`tab:netsens`) gives the nesting.

### E2. Connect to the freeze/holdout discussion (§3.4, after l. 531)

**l. 531 — current (end)**
```tex
... the freeze/run-id contract hash-pins the network, anchors, stage split, and holdout unit list before holdout scoring~\cite{cvprofiles}.
```
**Proposed insertion after it**
```tex
The freeze has to pin the menu as well as the network: under menu-separable restrictions, adding admissible columns can only widen $[L,U]$, and a single admitted column can move either endpoint anywhere (Proposition~\ref{prop:monotone}).
```

### E3. Connect to Goodharting (§6.4, l. 853, and App D, l. 1262)

**l. 853 — current**
```tex
The defenses are procedural rather than magical---freeze the network and thresholds before final scoring, preserve negative controls, reserve restrictions or units, and keep generator provenance separate from validity evidence.
```
**Proposed**
```tex
The defenses are procedural rather than magical---freeze the menu, network, and thresholds before final scoring, preserve negative controls, reserve restrictions or units, and keep generator provenance separate from validity evidence.
They are needed because the screen bounds admission, not endpoints: one admissible column can set either end of $[L,U]$ (Proposition~\ref{prop:monotone}(iv)).
```
**l. 1262 — current (fragment)**
```tex
... the defenses are procedural---freeze $\Rset$ and $\tau$ before final scoring, ...
```
**Proposed (fragment)**
```tex
... the defenses are procedural---freeze $\M$, $\Rset$, and $\tau$ before final scoring (Proposition~\ref{prop:monotone}), ...
```

---

## Pass F — Follow-ups outside the `.tex` (not edits here)

- `README.md` and `docs/METHODOLOGY.md` no longer mention Dell or Rambachan. The "(Dell–Rambachan frame)" line in the first commit's `docs/03_Methodology.md` was dropped in the 2026-08-21 docs reorganization (`ed81e5b`). Restoring it is a separate change.
- After you accept items, add a dated `logs/DECISIONS.md` entry (attribution made precise; contributions unchanged) and amend `paper/CLAIM_BOUNDARY_BRIEF.md` if A3 changes an allowed contribution sentence.

---

## Do not edit

- θ on any restriction; δ; any network file.
- Plug-in `[0.245,0.556]`, `−0.317`, `[−0.219,0.565]`, MTMM `0.825/0.284/−0.252/0.706`.
- Freeze hashes and run_ids.
- The cell β estimand. The partial correlations in D1 are a diagnostic beside it, not a replacement.
- Any claim that Phi is a valid trust measure (C1 makes the opposite reading more precise).

---

## G. Commands (run from the repo root)

### G.1 Recompute Pass C and Pass D

Requires `uv sync --extra dev`. Output below is from cvprofiles 3.0.2 on 2026-10-19.

```bash
uv run python - <<'PY'
# Recompute §5.4 criterion self-consistency and education-proxy numbers
# from committed cell data, using the engine's own slack code.
import numpy as np
import pandas as pd

from cvprofiles import __version__
from cvprofiles.identify.slacks import evaluate_slack, pearson_corr
from cvprofiles.restrict.pipeline import load_network

D = "evals/wvs_gps_two_resolution"
print("cvprofiles", __version__)


def partial_corr(x, y, z):
    """Pearson partial corr of x and y given z (first-order formula)."""
    rxy, rxz, ryz = pearson_corr(x, y), pearson_corr(x, z), pearson_corr(y, z)
    return (rxy - rxz * ryz) / np.sqrt((1 - rxz**2) * (1 - ryz**2))


for construct, crit in [("patience", "gps_patience_cell"), ("trust", "gps_trust_cell")]:
    df = pd.read_csv(f"{D}/data/cells_demeaned/{construct}_llm_extension.csv")
    net = load_network(f"{D}/networks/{construct}_cells_llm.yaml")
    measures = [c for c in df.columns if c.startswith("m_")]
    edu = df["q275_cell"].to_numpy(float)
    y = df[crit].to_numpy(float)
    r_crit_edu = pearson_corr(y, edu)
    print(f"\n== {construct} cells (n={len(df)}), network {net.name} ==")
    print(f"{'column':22s} {'corr_edu':>8s} {'sel_slk':>8s} {'hold_slk':>8s} "
          f"{'beta':>7s} {'edu_rte':>7s} {'pc|edu':>7s}")
    for col in measures + [crit]:
        v = df[col].to_numpy(float)
        s = {r.id: evaluate_slack(v, df, r) for r in net.restrictions}
        r_edu = pearson_corr(v, edu)
        if col == crit:
            beta = route = pc = float("nan")
        else:
            beta = pearson_corr(v, y)          # cell beta (corr_y)
            route = r_edu * r_crit_edu         # beta implied by the education channel alone
            pc = partial_corr(v, y, edu)       # corr with criterion holding education fixed
        print(f"{col:22s} {r_edu:8.3f} {s['conv_edu_cell']:8.3f} {s['mono_edu_cell']:8.3f} "
              f"{beta:7.3f} {route:7.3f} {pc:7.3f}")

    # How much of within-country cell education is a sex-by-age-band pattern?
    parts = df["unit_id"].str.split("|", expand=True)
    X = pd.get_dummies(parts[1] + "|" + parts[2], drop_first=True).to_numpy(float)
    X = np.column_stack([np.ones(len(df)), X])
    fit = X @ np.linalg.lstsq(X, edu, rcond=None)[0]
    r2 = 1 - ((edu - fit) ** 2).sum() / ((edu - edu.mean()) ** 2).sum()
    print(f"R^2 of q275_cell on pooled sex-by-age-band dummies: {r2:.3f}")
PY
```

Output:
```text
cvprofiles 3.0.2

== patience cells (n=480), network patience_cells_llm_extension ==
column                 corr_edu  sel_slk hold_slk    beta edu_rte  pc|edu
m_wvs_q13                 0.251    0.051    0.060   0.245   0.119   0.148
m_wvs_q14                -0.364   -0.564   -0.499  -0.326  -0.173  -0.186
m_composite              -0.050   -0.250   -0.222  -0.027  -0.024  -0.004
m_noise                  -0.031   -0.231   -0.165  -0.003  -0.015   0.013
m_llm_patience_llama      0.522    0.322    0.358   0.417   0.248   0.225
m_llm_patience_phi        0.640    0.440    0.523   0.556   0.304   0.373
gps_patience_cell         0.475    0.275    0.315     nan     nan     nan
R^2 of q275_cell on pooled sex-by-age-band dummies: 0.590

== trust cells (n=480), network trust_cells_llm_extension ==
column                 corr_edu  sel_slk hold_slk    beta edu_rte  pc|edu
m_trust_general           0.023   -0.177   -0.131   0.052  -0.005   0.060
m_trust_in_group         -0.068   -0.268   -0.233   0.224   0.016   0.214
m_trust_out_group        -0.075   -0.275   -0.225   0.211   0.018   0.200
m_trust_institution      -0.427   -0.627   -0.552   0.285   0.101   0.210
m_trust_composite        -0.274   -0.474   -0.414   0.318   0.064   0.271
m_noise                   0.028   -0.172   -0.119   0.015  -0.007   0.022
m_llm_trust_llama         0.123   -0.077   -0.066   0.179  -0.029   0.216
m_llm_trust_phi           0.349    0.149    0.133  -0.317  -0.082  -0.258
gps_trust_cell           -0.235   -0.435   -0.386     nan     nan     nan
R^2 of q275_cell on pooled sex-by-age-band dummies: 0.590
```

Cross-check against the frozen runs (menu-member slacks and β agree to three decimals):
```bash
cat evals/wvs_gps_two_resolution/runs/patience_cells_demeaned_llm/slacks.csv
cat evals/wvs_gps_two_resolution/runs/trust_cells_demeaned_llm/slacks.csv
cat evals/wvs_gps_two_resolution/runs/patience_cells_demeaned_llm/beta_values.json
cat evals/wvs_gps_two_resolution/runs/trust_cells_demeaned_llm/beta_values.json
```

### G.2 Source verification

Slides and working paper (text extraction; requires poppler):
```bash
mkdir -p /tmp/dr_check && curl -sL https://conference.nber.org/confer/2026/SI2026/ML/dell3.pdf -o /tmp/dr_check/dell3.pdf
pdfinfo /tmp/dr_check/dell3.pdf && pdftotext -layout /tmp/dr_check/dell3.pdf - | less
curl -sL https://www.nber.org/system/files/working_papers/w35744/w35744.pdf -o /tmp/dr_check/w35744.pdf
pdftotext -layout /tmp/dr_check/w35744.pdf - | grep -n -i "nomological\|partial identif\|specification search\|upstream"
```

DOIs (Crossref metadata):
```bash
for d in 10.3386/w35744 10.3982/ECTA8718 10.1093/qje/qjad043 10.1016/j.jeconom.2014.10.013 10.3982/QE1288 10.3982/ECTA17969 10.1037/0022-3514.84.3.608; do curl -s "https://api.crossref.org/works/$d" | python3 -I -c "import sys,json; m=json.load(sys.stdin)['message']; print(m['DOI'],'|',m['title'][0],'|',[a.get('given','')+' '+a.get('family','') for a in m.get('author',[])],'|',m.get('container-title'),m.get('volume'),m.get('issue'),m.get('page'))"; sleep 2; done
```

arXiv IDs:
```bash
curl -s "https://export.arxiv.org/api/query?id_list=1801.01489,2609.16618,2609.08812,2607.12219,2607.07915" | grep -E "<title>|<name>|<published>|journal_ref"
```

JMLR page for Fisher–Rudin–Dominici:
```bash
curl -sL https://jmlr.org/papers/v20/18-760.html | grep -o "<title>[^<]*</title>\|(177):1&minus;81, 2019"
```

---

## Execution order

1. Pass A (you veto sentence by sentence). A1, A2, A5, A6, and A11 carry the attribution. A3, A4, and A7–A10 are one-clause follow-through. The optional items can wait.
2. Pass B bib entries (mechanical once A11 is in), then the placement sentences B1–B8.
3. Pass C and Pass D (one sentence plus two table rows; one paragraph).
4. Pass E (send the proposition to Daniel with CLAIM_SHRINK Pass 5 if you want psychometric sign-off on the wording).
5. Recompile, then Pass F follow-ups and the DECISIONS entry.
