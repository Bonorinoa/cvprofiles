# Attribution edit list — 2026-10-19

**Purpose:** proposed edits to `paper/position_paper.tex` (v9, 1574 lines at commit `0524aa8`) for Augusto to accept, edit, or veto one item at a time. Nothing in the `.tex` has been changed, and `pdflatex` has not been run.

**Lock:** frozen scores, networks, θ, run_ids, and every plug-in `[L,U]` stay as they are. Every number below is either already in the paper or was recomputed from committed data with the commands in §G.

**Not in scope:** moving θ; new restrictions; re-scoring; changing Table 3's plug-in values; logging decisions (these go into `logs/DECISIONS.md` after you accept items, as in `CLAIM_SHRINK_EDIT_LIST.md` Pass 6).

**Line numbers** refer to the current file. Each item quotes the current text verbatim. If several items are accepted, apply them bottom-up so the line numbers stay valid.

---

## Why this list exists (read first)

Dell & Rambachan's NBER Methods Lecture deck, *Construct Validity: Credibility When Measurement Is Cheap* (15 slides; PDF metadata shows it was created 2026-07-30 and authored by Melissa Dell and Ashesh Rambachan; https://conference.nber.org/confer/2026/SI2026/ML/dell3.pdf), defines the paper's core objects under the same names. I re-checked this on 2026-10-19 against the extracted slide text:

| Slide | Slide title (verbatim) | What it defines |
|---|---|---|
| 5 | AI Raises Important Construct Validity Concerns | Sala-i-Martin specification search moves to "searching across representations"; a construct-definition analogue of Goodhart's law |
| 6 | Construct Validity as Partial Identification | formalizes the Cronbach–Meehl nomological network as partial identification |
| 7 | What the Formalization Does—and Does Not—Do | identified set relative to a researcher-specified menu and moment restrictions; cites Borsboom et al. (2004) for the limits |
| 8 | Candidate Measurement Functions | menu `M = (m_j(·))_{j∈J}`; normalization; β(m) defined consistently across candidates |
| 9 | Nomological Restrictions | auxiliaries `V=(Z,W,G,Q)`; convergent, discriminant, and known-groups restrictions with thresholds |
| 10 | The Admissible Set of Measures | `θ=(c_1..c_K, d_1..d_L, δ)`; `E[g_r(m(X),V;θ_r)] ≥ 0`; `M*_{R,θ}`, "a population object" |
| 11 | Construct-Validity Profiles | slacks `s_r(m;θ_r)`; report the full profile; thresholds grounded in prior evidence |
| 12 | The Construct-Identified Set | `B*_{R,θ} = {β(m) : m ∈ M*_{R,θ}}` |
| 13 | Inference for the Construct-Identified Range | `[L,U]` = inf/sup over `M*_{R,θ}`; two coupled sources of uncertainty, coupled near the admissibility boundary; "Estimation is beyond today's scope" |
| 14 | How Credible Are the Auxiliary Measures? | auxiliary credibility; Campbell–Fiske; sparse, well-measured restrictions over dense networks |

The companion review, Dell & Rambachan, *The Measurement Revolution? Credible Measurement and Inference in the Age of AI*, NBER WP 35744 (September 2026, doi 10.3386/w35744), develops this in prose rather than formally. Its §2.2 ("Construct Definition", p. 8) compares the nomological network to partial identification and says that adding restrictions narrows the set of plausible measures. The same section says that when theory is weak, a failed alignment may count against the theory rather than the measure (p. 9). Its introduction (pp. 4–5) makes the Sala-i-Martin analogy: AI moves specification search upstream into measurement. Searching the extracted text found no formal `M*`, slack profile, `B*`, or `[L,U]` in the WP. The formal objects are in the slides.

**Repository provenance agrees with this list.** The repo's first commit (`bc56870`, 2026-08-01, two days after the deck's creation date) says in `docs/03_Methodology.md` "(Dell–Rambachan frame)". Its README already uses "construct-validity profiles" and "construct-identified range". The package name is the title of slide 11. Explicit attribution in the paper therefore matches the project's own history. Without it, a reviewer who knows the lecture will likely conclude the paper renamed someone else's objects. That is the paper's largest reviewer risk.

**Notation map** (used in A13):

| Object | Dell–Rambachan | Paper now | Package (YAML / artifacts) |
|---|---|---|---|
| Threshold | `θ_r` (with `θ` collecting all) | `τ_r` | `theta`, `theta_grid.json` |
| Known-groups threshold | `δ` (inside `θ`) | — | — |
| Admission tolerance | — | `δ` | `delta` |
| Admissible set | `M*_{R,θ}` (population) | `M*`, `M*(R)` (sample, §1.4/§3.2); `𝓜*_0` (population, App A) | `admissible.json` |
| Slack | `s_r(m;θ_r)` (population) | `s_r(m)` (sample), `s_r^0(m)` (population) | `slacks.csv` |
| Image | "construct-identified set" `B*_{R,θ}` | "robust result set" / "admissible-result set" `B*` | `range.json` |

**Two reviewer-risk notes (not edits; your call):**
- WP 35744 §2.2 uses trust as its example and says a trust measure should not "simply reproduc[e] institutional quality". The paper's country trust network uses rule of law as a *convergent* floor (`Corr ≥ 0.30`, l. 654). "Co-moves with" and "simply reproduces" can both hold, but a reviewer who reads both texts will notice. One sentence at l. 654–655 explaining why rule of law is convergent evidence rather than contamination would close this.
- Slide 14 recommends separating "well-anchored" restrictions from exploratory ones. The one-gate cell network (l. 656–657) is a sparse network of the kind slide 14 recommends, so citing it there helps. Item C1 below shows, however, that the β criterion for trust fails that same gate. Decide whether education counts as well-anchored for trust before citing slide 14.

---

## Pass A — Attribution to Dell & Rambachan (required item 1)

### A1. Statement of significance (l. 80)

**Current**
```tex
We answer with a reporting discipline assembled from three existing traditions: construct validation, multiverse analysis, and partial identification.
```
**Proposed**
```tex
Dell and Rambachan recently formalized construct validation for this setting as partial identification over a researcher-declared menu of measures~\cite{dellrambachan2026}.
We implement that formalization in open software, add a protocol under which the screen can fail, and report its result beside the unrestricted multiverse.
```
**Why:** the significance statement is the first place a reader meets the claim. As written, it presents the composition as the authors' own.

### A2. Abstract (ll. 92–93)

**Current**
```tex
This paper develops \emph{construct-identified inference}, a reporting discipline for that abundance.
The researcher declares a menu of candidate measures and a validity argument---pre-stated convergent and discriminant expectations with researcher-owned thresholds---which screens the menu into an admissible set.
```
**Proposed**
```tex
Dell and Rambachan's 2026 NBER Methods Lecture formalizes construct validation for that abundance as partial identification: a researcher declares a menu of candidate measures and thresholded convergent, discriminant, and known-groups restrictions, which screen the menu into an admissible set whose image under the downstream estimand is the construct-identified set.
The lecture leaves estimation aside.
This paper supplies, to our knowledge, the first open implementation of that framework and a reporting protocol for using it.
```
**Why:** this names the source of the objects in the abstract. Psychological Methods abstracts carry no `\cite`, so the authors are named in prose. **Check before accepting:** "first open implementation" is a priority claim. Search GitHub and PyPI for other implementations at submission time, or soften it to "an open implementation".

### A3. Plain-language abstract (l. 108, opening clause only)

**Current**
```tex
This paper proposes a reporting rule: researchers declare a menu of candidate measures ...
```
**Proposed**
```tex
Building on a framework proposed in 2026 by the economists Melissa Dell and Ashesh Rambachan, this paper implements a reporting rule: researchers declare a menu of candidate measures ...
```
**Why:** the plain-language summary is widely read and is often quoted in press coverage. It should not imply that the authors invented the rule.

### A4. Title (l. 65) and `pdftitle` (l. 42) — flag

**Current**
```tex
\title{Measuring What We Mean:\\[2pt] Construct-Identified Inference When Measures Are Cheap}
```
**Issue:** "When Measures Are Cheap" echoes their title "Credibility When Measurement Is Cheap", and "Construct-Identified" echoes their slide 12 "The Construct-Identified Set". Either echo is acceptable with attribution. Together they read as a variant of their title.

**Alternative 1** (keeps the hook and credits the object):
```tex
\title{Measuring What We Mean:\\[2pt] Construct-Identified Sets in Practice, with an Application to Patience and Trust}
```
**Alternative 2** (protocol-forward, no echo):
```tex
\title{A Screen That Can Fail:\\[2pt] Held-Out Validity Screening and Two-Set Reporting for Competing Measures}
```
If you keep the current title, A2 and A9 become more important. Update `pdftitle` (l. 42) to match whichever title you choose. The coined frame name "construct-identified inference" can stay if A7 attributes the underlying set.

### A5. §1.3 heading and opening (ll. 193–195)

**Current**
```tex
\subsection{The missing composition}
The audits above share a feature: each documents a failure inside a single stage of the pipeline.
What is missing is the composition---an account of how measurement, validation, and estimation combine into a scientific conclusion, and of what a robustness claim means once measures are cheap.
```
**Proposed**
```tex
\subsection{From formal objects to practice}
The audits above share a feature: each documents a failure inside a single stage of the pipeline.
What they lack is the composition---an account of how measurement, validation, and estimation combine into a scientific conclusion, and of what a robustness claim means once measures are cheap.
Dell and Rambachan's 2026 Methods Lecture supplies its formal objects~\cite{dellrambachan2026}; what has been missing is an implementation researchers can run, a protocol under which the screen can fail, and evidence on how it behaves on data.
```
**Why:** "What is missing is the composition" claims a gap that their lecture fills.

### A6. §1.4 "Four objects" — opening (l. 209)

**Current**
```tex
The framework needs four objects.
```
**Proposed**
```tex
The framework uses the objects of Dell and Rambachan's formalization~\cite[slides 8--13]{dellrambachan2026}, under their names where they have one; this section restates them with the sample slacks the software computes (their definitions are population objects, which Appendix~\ref{app:formal} separates from the sample analogues).
```
**Why:** §1.4 is where the objects are defined, and it currently credits no one. The population/sample note also lines up with CLAIM_SHRINK Pass 5.1.

### A7. §1.4 — restrictions, image, range, and closing sentence (ll. 212, 220, 225, 230)

**l. 212 — current (end of sentence)**
```tex
... written as moment inequalities $\E[g_r(m,V;\tau_r)]\ge 0$ over auxiliary variables $V$, with researcher-owned thresholds $\tau_r$.
```
**Proposed**
```tex
... written, following Dell and Rambachan, as moment inequalities $\E[g_r(m,V;\tau_r)]\ge 0$ over auxiliary variables $V$, with researcher-owned thresholds $\tau_r$ (their $\theta_r$; convergent, discriminant, and known-groups forms are theirs).
```
(If A13 is accepted, drop "(their $\theta_r$ ...)" and use $\theta_r$ throughout.)

**l. 220 — current**
```tex
Remaining measurement choice is then propagated into the result: the robust result set is the image of the estimand over survivors,
```
**Proposed**
```tex
Remaining measurement choice is then propagated into the result: Dell and Rambachan's \emph{construct-identified set} is the image of the estimand over survivors,
```

**l. 225 — current**
```tex
summarized for a scalar estimand by its range,
```
**Proposed**
```tex
summarized for a scalar estimand by its range---their construct-identified range, for which they note that admission and endpoint uncertainty are coupled near the admissibility boundary and leave estimation beyond the lecture's scope,
```

**l. 230 — current**
```tex
Equations~\eqref{eq:admissible-set}--\eqref{eq:headline-range} define the admissible set, the robust result set, and the headline range.
```
**Proposed**
```tex
Equations~\eqref{eq:admissible-set}--\eqref{eq:headline-range} restate Dell and Rambachan's admissible set, construct-identified set, and range with sample slacks; the per-restriction slacks $s_r(m)$ are their construct-validity profiles, from which the software takes its name.
```
**Why:** these four sentences carry the objects the slides define. "Robust result set" gives their B\* a new name. See A14 for the global rename.

### A8. §1.5 contributions (ll. 237–249) — restate as six

**Current**
```tex
\subsection{Four contributions}
The contributions follow in deliberately conservative order.
\textit{(i) Validity-constrained measurement robustness.}
$\Bset^*$ is the image of the estimand over measures that survive a declared validity argument, not an unrestricted multiverse; fragility and robustness are therefore attributed to the right cause.
\textit{(ii) A selection rule that can fail.}
Leftover restrictions never vote on admission.
On the frozen cell scores, construct-guided selection is compared with best-$\beta$, best-anchor, and size-matched random subsets (Table~\ref{tab:falsify}).
At cell resolution the leftover restriction is a rank transform of the selecting education correlation, so the patience comparison is weak; the trust comparison is not: best-$\beta$ picks a rejected composite, construct-guided picks Phi.
\textit{(iii) Separation of headline from diagnostics.}
The headline range is reported separately from additive sampling diagnostics: an uncertainty band (selection uncertainty, not a confidence set), an empty-replicate rate, and boundary attribution.
\textit{(iv) An auditable, score-agnostic implementation and a two-resolution application.}
The method ships in the released package \cvp{}~3.0.2~\cite{cvprofiles}.
The confirmatory application places human measures of patience and of trust under one contract at two resolutions, with leftover restrictions, additive sampling diagnostics, and two nested special cases computed on the same objects.
```
**Proposed**
```tex
\subsection{Contributions relative to Dell and Rambachan}
The menu, the thresholded nomological restrictions, the admissible set, the slack profiles, the construct-identified set and range, and the coupling concern are Dell and Rambachan's~\cite{dellrambachan2026}.
This paper contributes six things, in deliberately conservative order.
\textit{(i) An open implementation.}
To our knowledge \cvp{}~3.0.2~\cite{cvprofiles} is the first open, score-agnostic implementation of those objects, with the additive diagnostics the coupling concern calls for: an uncertainty band (selection uncertainty, not a confidence set), an empty-replicate rate, and boundary attribution.
\textit{(ii) A held-out selection rule that can fail.}
Leftover restrictions never vote on admission.
On the frozen cell scores, construct-guided selection is compared with best-$\beta$, best-anchor, and size-matched random subsets (Table~\ref{tab:falsify}).
At cell resolution the leftover restriction is a rank transform of the selecting education correlation, so the patience comparison is weak; the trust comparison is not: best-$\beta$ picks a rejected composite, construct-guided picks Phi.
\textit{(iii) A freeze/run-id protocol.}
Scores (hence the menu), network, thresholds, and target are hash-pinned before slacks are inspected, so every reported range re-verifies from committed inputs (Section~\ref{sec:impl}).
\textit{(iv) Two-set reporting.}
The unrestricted image over $\M$---the specification curve, recovered as the named case $\Rset=\emptyset$---is reported beside the screened image as a standing requirement, so that homogeneity created by the screen is distinguishable from homogeneity that survives it.
\textit{(v) An executed reciprocal reading of rejected measures.}
The principle that a failed restriction can indict the network rather than the measure is Cronbach and Meehl's, restated by Dell and Rambachan~\cite{cronbach1955,dellrambachan2026wp}; Appendix~\ref{app:inadmissible} executes it by profiling $\M\setminus\M^*$.
\textit{(vi) A two-resolution application.}
Human measures of patience and of trust, with two open-weight columns, are screened under one contract at country and within-country cell resolution, with leftover restrictions, additive diagnostics, and two nested special cases computed on the same objects.
```
**Why:** this is the restatement the brief asks for. The current (i) claims B\*, which is their object. The current (iii) folds into the new (i). The current (ii) text is kept word for word.

### A9. §1.6 roadmap (l. 253)

**Current**
```tex
Novelty is claimed only in the operational composition of three existing traditions, in a selection rule that can fail, and in a released implementation.
```
**Proposed**
```tex
The composition of construct validation and partial identification at the measurement layer is Dell and Rambachan's~\cite{dellrambachan2026}; novelty is claimed only in the implementation, the held-out selection rule, the freeze protocol, two-set reporting, the executed reading of rejected measures, and the application.
```

### A10. §2 heading (l. 257) — optional

**Current:** `\section{Three traditions, one missing layer}`
**Proposed:** `\section{Three traditions and their recent composition}`
**Why:** the "missing layer" is the layer their lecture supplies.

### A11. §2.2 extreme-bounds paragraph (l. 289)

**Current**
```tex
This paper's screen is the admissibility test EBA lacked, moved from specifications to measurement functions: the unrestricted multiverse over $\M$ is the named special case, and robustness is judged over the survivors $\M^*$, with the validity argument itself held-out falsifiable (Section~\ref{sec:falsify}).
```
**Proposed**
```tex
Dell and Rambachan draw the same analogy: AI moves specification search upstream, from regressions to representations of reality~\cite{dellrambachan2026,dellrambachan2026wp}.
The screen is the admissibility test EBA lacked, moved from specifications to measurement functions: the unrestricted multiverse over $\M$ is the named special case, and robustness is judged over the survivors $\M^*$, with the validity argument itself held-out falsifiable (Section~\ref{sec:falsify}).
```
**Why:** slide 5 and WP pp. 4–5 make the Sala-i-Martin analogy that this paragraph presents as its own.

### A12. §2.3 — the core attribution paragraph (ll. 294–299)

**Current**
```tex
The connection to measurement is recent and explicit.
In the 2026 NBER Summer Institute Methods Lectures, \emph{Estimation and Inference with AI-Generated Data}, Dell and Rambachan frame the nomological network as partial identification under theoretically motivated moment restrictions---Dell on measurement and construct validity, Rambachan on multiple measurements and data fusion---and explicitly call for principled, widely accepted methods for construct validity~\cite{dellrambachan2026}.
The nearest formal neighbor is Chen, Rambachan, and Tamer, whose restrictions are benchmark-informed bounds on error correlation for a downstream parameter~\cite{chenrttamer2026}.
The present framework differs in the object of inference: our restrictions are menu-level nomological moment inequalities, the surviving set $\M^*$ is the object, and the selection rule is held-out falsifiable.
Other recent work occupies adjacent territory without a surviving set: Ogut and Yin derive curvature bounds from multiple nonlinear measurements~\cite{ogutyin2026}; Messing shows that naive standard errors in LLM evaluation pipelines can be 40--60\% too small---a diagnosis about evaluation scores, not construct measures~\cite{messing2026}; Canen and Enamorado correct regressor measurement error by split-sample procedures---a correction, not a selection~\cite{canenenamorado2026}.
None performs menu-level validation with a surviving set and a falsifiable selection rule.
```
**Proposed**
```tex
The connection to measurement is recent and explicit, and the formal objects used in this paper are Dell and Rambachan's.
In their 2026 NBER Methods Lecture, \emph{Construct Validity: Credibility When Measurement Is Cheap}~\cite{dellrambachan2026}, they formalize the Cronbach--Meehl nomological network as partial identification: a researcher-specified menu $\M$ of candidate measurement functions; convergent, discriminant, and known-groups restrictions written as population moment inequalities with thresholds $\theta$; the admissible set $\M^*_{\Rset,\theta}$; construct-validity profiles of slacks $s_r(m;\theta_r)$; the construct-identified set $\Bset^*_{\Rset,\theta}$ of downstream parameters; and its range $[L,U]$, for which they note that admission and endpoint uncertainty are coupled near the admissibility boundary and leave estimation beyond the lecture's scope (slides 7--13).
Their companion review develops the partial-identification reading in prose~\cite{dellrambachan2026wp}.
This paper implements those objects, adds a held-out selection rule, a freeze protocol, and two-set reporting, and applies them; it does not propose them.
Among formal treatments with inference, Chen, Rambachan, and Tamer bound a downstream parameter under benchmark-informed restrictions on error correlation~\cite{chenrttamer2026}.
The nearest empirical twin is Ogut and Yin: six AI-exposure measures, an ex ante factor-analytic rule that sets one measure apart as a distinct construct and retains five, and Imbens--Manski confidence intervals with the Stoye critical value that attain uniform coverage over their curvature class~\cite{ogutyin2026,imbensmanski2004,stoye2009}.
Relative to Chen--Rambachan--Tamer, the restrictions here are nomological inequalities on each measure rather than bounds on error correlation; relative to Ogut--Yin, the screen is a declared set of thresholded restrictions with a held-out stage rather than a factor-analytic rule, and the range carries an additive band rather than a confidence interval with coverage theory---on inference, theirs is the stronger result.
Other recent work occupies adjacent territory without a surviving set: Messing shows that naive standard errors in LLM evaluation pipelines can be 40--60\% too small---a diagnosis about evaluation scores, not construct measures~\cite{messing2026}; Canen and Enamorado correct regressor measurement error by split-sample procedures---a correction, not a selection~\cite{canenenamorado2026}.
To our knowledge none of this work combines a declared, thresholded screen with a held-out stage that can fail and an unrestricted image reported beside the screened one; that combination, not the objects, is what this paper adds.
```
**Why:**
- The slides formalize all six objects. "Frame" understates this.
- The current sentence names the lecture series instead of the deck, and assigns topics to each author ("Dell on …, Rambachan on …"), but the deck is co-authored.
- I could not find "principled, widely accepted methods for construct validity" in the slide text. The closest is slide 6: formalizing construct validity is "largely an open question". If that phrase comes from the talk or another deck, cite that source. Otherwise drop it, as the proposal does.
- Ogut–Yin *do* screen a menu down to a surviving set (five of six measures, via an ex ante factor-analytic rule), and they have uniform-coverage inference. "Without a surviving set" and "None performs menu-level validation with a surviving set" are therefore false as written.

### A13. Notation: `τ_r` → `θ_r` (global, 23 occurrences of `\tau`) — optional but recommended

**Lines:** 212, 356, 363, 374, 391, 412, 427, 430, 432, 485, 569, 626, 670, 678, 725, 854, 1040, 1062, 1160, 1262, 1374, 1530, 1563 (from `grep -n '\\tau' paper/position_paper.tex`).

**Proposed:** replace `\tau` with `\theta` throughout, and rename "$\tau$-grid" to "$\theta$-grid". Add a footnote at l. 434, where δ is introduced:
```tex
\footnote{Dell and Rambachan use $\delta$ for the known-groups threshold inside $\theta$; here $\delta$ is the admission tolerance, as in the software's \texttt{delta} field.}
```
**Why:** the paper is currently the odd one out. Dell–Rambachan use θ, the package YAML uses `theta` and writes `theta_grid.json`, and App G and Table 9 (`tab:netsens`) already use `\theta_{\mathrm{edu}}`. Matching their notation makes the attribution visible on every equation. The δ collision is real: their δ is a threshold, while yours is a tolerance.

### A14. "Robust result set" → "construct-identified set" (global) — optional but recommended

**Lines:** 153 (Fig. 1 node `robust result set`), 220 and 230 (covered by A7), 360 (Fig. 2 node `Robust result`), 598 ("the robust result set"), 1169 (notation table: "Admissible-result set (construct-identified)").

**Proposed:** use "construct-identified set" for B\* everywhere. In Fig. 2 use `\textbf{Construct-identified}\\\scriptsize $\Bset^*$, $[L,U]$`. In the l. 1169 notation table use `Construct-identified set (Dell--Rambachan)`.

**Why:** a second name for their object looks like relabeling. "Robust" also overstates what the set guarantees, which is consistent with CLAIM_SHRINK's direction.

### A15. §2.7 synthesis (ll. 316–318)

**Current**
```tex
The composition those traditions do not jointly supply is the map $\Rset(C)\to\M^*(\Rset)\to\Bset^*(\Rset)$, drawn with a return arrow: observed disagreement among measures can motivate revision of $C$ or $\Rset$ for future studies.
A holdout that makes screening prospectively falsifiable, and a freeze that makes it auditable, are protocol commitments; they are not implied by the map.
That composition---the ordering of established ideas rather than a new taxonomy---is the contribution of this paper.
```
**Proposed**
```tex
Dell and Rambachan compose those pieces into the map $\Rset(C)\to\M^*(\Rset)\to\Bset^*(\Rset)$~\cite{dellrambachan2026}; the return arrow---observed disagreement among measures can motivate revision of $C$ or $\Rset$ for future studies---is Cronbach and Meehl's.
A holdout that makes screening prospectively falsifiable, and a freeze that makes it auditable, are protocol commitments; they are not implied by the map.
Those commitments, an implementation that executes them, and an application that tests them are the contribution of this paper.
```
**Why:** the current sentence claims the map as the paper's contribution, and the map is slides 10–12.

### A16. §3.1 notation sentence (l. 391)

**Current**
```tex
The \emph{nomological network} $\Rset(C)$ encodes those implications as moment restrictions with substantive thresholds $\tau_r$, following the classical validation tradition~\cite{cronbach1955,campbell1959} and its recent partial-identification reading~\cite{dellrambachan2026}.
```
**Proposed**
```tex
The \emph{nomological network} $\Rset(C)$ encodes those implications as moment restrictions with substantive thresholds $\tau_r$, following the classical validation tradition~\cite{cronbach1955,campbell1959} and Dell and Rambachan's partial-identification formalization of it~\cite{dellrambachan2026}, whose objects Table~\ref{tab:objects} collects.
```

### A17. Table 1 caption (ll. 400–402) — append one sentence

**Current (last sentence)**
```tex
The engine computes consequences of commitments; it does not author the construct, the menu, the restrictions, or the thresholds.}
```
**Proposed**
```tex
The engine computes consequences of commitments; it does not author the construct, the menu, the restrictions, or the thresholds.
$\M$, $\Rset(C)$ with thresholds, $\M^*$, the slacks, $\Bset^*$, and $[L,U]$ follow Dell and Rambachan~\cite{dellrambachan2026}; $G(D,C)$, the owner column, and the tolerance $\delta$ are this paper's.}
```

### A18. §3.5 coupling (ll. 559, 574)

**l. 559 — current**
```tex
The fixed-selection literature takes the admissible set as given~\cite{imbensmanski2004,stoye2009}; here selection is estimated.
```
**Proposed**
```tex
The fixed-selection literature takes the admissible set as given~\cite{imbensmanski2004,stoye2009}; here selection is estimated.
Dell and Rambachan flag this coupling and suggest that existing partial-identification and endpoint-inference methods can be combined into a valid, if conservative, confidence region~\cite{dellrambachan2026}; this paper does not construct that region.
```
**l. 574 — current**
```tex
The documented failure regime is coupling: a near-boundary measure that is also $\beta$-extreme couples admission with the endpoints, because its inclusion or exclusion moves the range directly.
```
**Proposed**
```tex
The failure regime Dell and Rambachan identify is coupling: a near-boundary measure that is also $\beta$-extreme couples admission with the endpoints, because its inclusion or exclusion moves the range directly.
```
**Why:** "documented" leaves the source unstated, and the source is slide 13.

### A19. §4 implementation (l. 597)

**Current**
```tex
\cvp{} is the open Python implementation of the measurement-selection layer~\cite{cvprofiles}.
```
**Proposed**
```tex
\cvp{} is an open Python implementation of Dell and Rambachan's construct-validity profiles and construct-identified set~\cite{dellrambachan2026,cvprofiles}; its name follows their terminology.
```

### A20. §6.4 Goodharting (l. 852) — see also E3

**Current**
```tex
The most direct failure mode is Goodharting: a generator trained explicitly against the known restrictions.
```
**Proposed**
```tex
Dell and Rambachan name a construct-definition analogue of Goodhart's law for measures embedded in decisions~\cite{dellrambachan2026}; the most direct generator-side failure is a generator trained explicitly against the known restrictions.
```

### A21. Conclusion (l. 891)

**Current**
```tex
The novelty is not construct validity, multiverse analysis, partial identification, or sampling inference in isolation; it is their operational composition at the measurement layer.
```
**Proposed**
```tex
The objects are Dell and Rambachan's, and the novelty is not their composition of construct validity and partial identification; it is an open implementation, and a protocol under which that composition can fail on data.
```

### A22. Appendix A opening (after l. 1031) — one sentence

**Proposed insertion** (new first line of `\section{First-principles formalization}`):
```tex
Definitions~A.1--A.3 restate Dell and Rambachan's objects~\cite[slides 8--12]{dellrambachan2026} with sample analogues; Definition~A.4 and Propositions~A.1--A.4 are this paper's.
```
(The reference to Proposition A.4 assumes E1 is accepted.)

### A23. Smaller touch points (accept or skip as a block)

| Line | Current | Proposed |
|---|---|---|
| 838 | "The claim is compositional: construct validity determines ..." | "The claim, following Dell and Rambachan's formalization~\cite{dellrambachan2026}, is compositional: construct validity determines ..." |
| 1510 | "... framing construct-identified inference as a formal bridge across psychometrics, multiverse reporting, and partial identification." | "... implementing Dell and Rambachan's construct-identified set~\cite{dellrambachan2026} as a bridge across psychometrics, multiverse reporting, and partial identification." |
| 1565 (`tab:synthesis_contributions`, row III, Key Literature cell) | `Imbens \& Manski~\cite{imbensmanski2004}; Stoye~\cite{stoye2009}` | `Dell \& Rambachan~\cite{dellrambachan2026}; Imbens \& Manski~\cite{imbensmanski2004}; Stoye~\cite{stoye2009}` |
| 1559 (`tab:synthesis_contributions` header) | `\textbf{Claimed Contribution}` | `\textbf{Component}` (rows I–II are recoveries, not contributions relative to D–R) |

### A24. Bibliography — fix one entry, add one

**l. 935 — current**
```tex
\bibitem{dellrambachan2026} Dell, M., \& Rambachan, A. (2026). \textit{Estimation and inference with AI-generated data} [Paper presentation]. NBER Summer Institute 2026 Methods Lectures.
```
**Proposed**
```tex
\bibitem{dellrambachan2026} Dell, M., \& Rambachan, A. (2026a). \textit{Construct validity: Credibility when measurement is cheap} [Lecture slides]. NBER Summer Institute 2026 Methods Lectures. https://conference.nber.org/confer/2026/SI2026/ML/dell3.pdf

\bibitem{dellrambachan2026wp} Dell, M., \& Rambachan, A. (2026b). \textit{The measurement revolution? Credible measurement and inference in the age of AI} (NBER Working Paper No. 35744). National Bureau of Economic Research. https://doi.org/10.3386/w35744
```
**Why:** the deck title on the title slide and in the PDF metadata is "Construct Validity: Credibility When Measurement Is Cheap". APA 7 requires the a/b suffixes for same-author, same-year works, ordered alphabetically by title ignoring "The": "Construct…" comes before "Measurement…". Verified: WP title, authors, September 2026, No. 35744, and the DOI (NBER page and Crossref).

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

Their description is corrected in A12. Accurate summary from the arXiv abstract: six exposure measures; a sign change in the post-2022 employment coefficient between the language-model measures and the Webb patent-text measure; an ex ante factor-analytic rule that sets Webb apart as a distinct construct; a consensus coefficient from the five retained measures; and Imbens–Manski CIs with the Stoye critical value, with uniform coverage over the curvature class including the point-identified boundary.

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

- `README.md` and `docs/METHODOLOGY.md` do not mention Dell or Rambachan, although the first commit's `docs/03_Methodology.md` did. The public docs need the same attribution as the paper. This is a separate change.
- After you accept items, add a dated `logs/DECISIONS.md` entry (attribution restated, contributions narrowed) and amend `paper/CLAIM_BOUNDARY_BRIEF.md` if A8 changes the allowed contribution sentences.

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

1. Pass A (you veto sentence by sentence). A2, A7, A8, A12, A15, A21, and A24 carry the attribution. The rest are follow-through.
2. Pass B bib entries (mechanical once A24 is in), then the placement sentences B1–B8.
3. Pass C and Pass D (one sentence plus two table rows; one paragraph).
4. Pass E (send the proposition to Daniel with CLAIM_SHRINK Pass 5 if you want psychometric sign-off on the wording).
5. Recompile, then Pass F follow-ups and the DECISIONS entry.
