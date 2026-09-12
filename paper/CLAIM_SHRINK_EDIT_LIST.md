# Claim-shrink edit list — 2026-08-31

**Lock:** keep the frozen WVS/GPS application; shrink claims to match evidence.
**Not in scope:** move θ; new cell restrictions on this sample; LLM re-scoring; Nature-track data; silent rewrite of Table 3 plug-in `[L,U]`.

Headline `[L,U]` stays the freeze. New numbers (cluster band, diagnostics, falsification) are **additive**.

CLAIM_BOUNDARY needs a dated amendment: allowed sentence 5 still cites trust coverage `[-0.382,-0.240]` as if it were the sampling-robust object. After clustering it is not.

---

## Pass 1 — Front matter (highest leverage)

### 1.1 Abstract (ll. 90–98)

| Kill | Replace with |
|---|---|
| “Screening is prospective and falsifiable—restrictions can be held out” | “Screening is auditable under a stated freeze: networks and thresholds are hash-pinned before slacks are inspected. This study was not preregistered.” |
| (implicit: band as if it had coverage theory) | Keep “additive uncertainty band, not folded into a confidence set.” Add: “the band has no simultaneous-coverage theory; operating characteristics are reported in App. K / deferred.” (If MC is not in yet: “not a confidence set.”) |

Do **not** mention the trust “criterion it was meant to recover” in the abstract. Last two sentences stay: no preferred measure; disagreements are the point.

### 1.2 Statement of significance (l. 87)

Kill: “points against the trust criterion it was meant to recover.”

Replace with one of (Augusto already has the CLAIM_BOUNDARY allowed sentence; cluster addendum in brackets):

> Under a predeclared within-country education implication, the only admissible cheap trust score is negatively associated with GPS trust (plug-in $\beta=-0.317$). GPS trust itself fails the country-level network, so that association is recovery of a contested criterion, not a refutation of a validated one. A country-cluster band on that singleton crosses zero.

### 1.3 Plain-language abstract (ll. 106, 109)

| Kill | Replace |
|---|---|
| “pre-registered expectations” | “pre-stated expectations” (study was not preregistered) |
| “points against the criterion it was asked to recover” | same contested-criterion sentence as 1.2, in plain language |
| “the rule does real work” as the trust punchline | “the rule can fail: the education screen and GPS-trust recovery pull apart” |

### 1.4 Keywords

Keep `criterion-related validity` first among validity words. Optional: drop bare `construct validity` or keep both (App J already narrowed the claim). No new keywords.

### 1.5 Author block (ll. 66–76, 833–836, pdfauthor)

Replace Kseniia / Monica with Daniel J. Martin. Affiliation and CRediT are **placeholders** until he accepts T1–T4. Do not invent CRediT.

### 1.6 Contribution (ii) (ll. 239–240)

Kill: “Restrictions or units can be held out prospectively, and validity-guided selection can fail—against held-out evidence and against a random-selection baseline” as if both were executed at the powered resolution.

Replace:

> (ii) A selection rule that can fail. Leftover restrictions never vote on admission. On the frozen cell scores, construct-guided selection is compared with best-$\beta$, best-anchor, and size-matched random subsets. At cell resolution the leftover restriction is a rank transform of the selecting education correlation, so the patience comparison is weak; the trust comparison is not: best-$\beta$ picks a rejected composite, construct-guided picks Phi.

---

## Pass 2 — Section 5–6 (application voice)

### 2.1 §5.2 Networks (l. 651)

Add one sentence after “Cell networks keep only the education implication”:

> The powered cell screen is therefore a one-gate education floor plus a Spearman leftover on the same auxiliary, not a multi-implication nomological network in the Cronbach–Meehl sense. Multi-restriction screening is exercised at country level (underpowered) and in the nested Campbell–Fiske $2\times 2$.

### 2.2 §5.3 empty-$\mathcal{R}$ (l. 656)

Name the seven columns: GPS, Q13, Q14, composite, Llama, Phi, noise. Endpoints: composite / Phi. (Already computed; just name them.)

### 2.3 §5.4 / cells (ll. 696–701, 713)

Keep plug-in $\beta=-0.317$. Kill any sentence that treats GPS trust as a validated criterion the screen then refutes.

Add: GPS trust fails rule of law at country level ($r=0.12$ vs floor $0.30$); cell $\beta$ is criterion-recovery of that contested column. App H Finding 3 (education slack vs $\beta$ anti-aligned at $-0.80$ among human measures) is the methods result.

### 2.4 Table 3 / `tab:twores` (ll. 723–738)

- Rename column **Coverage** → **Cell-exchangeable band** (or “uncertainty band”).
- Add a column or a second row/note for **country-cluster band**: patience $[0.174,0.622]$; trust $[-0.400,0.195]$.
- Caption: band is not a CI; cluster unit is country with re-demeaning; empty-rep is cell-exchangeable unless labeled.
- Do **not** change plug-in $[L,U]$.

### 2.5 §5.6 / §6.6 “bite” (ll. 792–793)

Kill: “not a preliminary agenda waiting for future experiments to decide whether construct-identified inference has bite.”

Replace: the application is a stress test of the reporting rule. It does not decide what patience or trust *is*. What remains includes (already listed) plus: a Monte Carlo of the band; prompt-paraphrase of the LLM columns; a multi-implication cell network on **new** data.

### 2.6 §6.1 Preregistration (ll. 755–757)

Keep “not preregistered.” Kill the implication that freeze = prospectivity. Freeze = auditable-conditional-on-stated-moment.

### 2.7 Llama/Phi (already mostly honest, ll. 616, 694)

One extra sentence in §5.4: the patience range widens from the Q13 singleton $0.245$ to $[0.245,0.556]$ because **both** cheap columns clear one education bar under **identical** prompts. That is menu expansion under correlated generators, which §1.2 says is weak validity evidence. Confess; do not re-score.

### 2.8 Equation (12) causal composition (ll. 578–584)

One sentence: not instantiated; future work. Do not keep “composition with causal analysis is direct” as a capability claim.

### 2.9 CRT nesting (l. 480)

Soften to analogy, or one-sentence “a finite-menu image is not their identified set without an explicit mapping.” Do not leave “the identified set defined by (4)–(7) is their set.”

### 2.10 §1.2 “not evidence that $\mathcal{B}^*$ is empty” (l. 183)

Either define $\mathcal{B}^*$ before that sentence or rewrite: “those audits are not failed restrictions against a declared network.”

---

## Pass 3 — Numbers that are wrong or unsupported

From `paper/NUMBER_RECONCILIATION.md`. Fix or delete; do not leave.

| Location | Now | Do |
|---|---|---|
| Table 8 / synthesis row IV | Q14 “anti-aligned at both levels (−0.33)” | Q14 education: −0.59 / −0.53 / −0.36. −0.33 is Q13 country education. |
| App I Q13–Q14 $r=0.83/0.52$ | unsupported | Delete, or replace with computed values (country join 0.52; cell country-means 0.48; pooled 0.35; within −0.23) and say which frame. |
| App I Result 3 trust between-share 89–94% | not in `dif_level_dependence.json` | Recompute from trust cell frame and commit, or delete. |
| App H Finding 4 “every WVS facet 0.48–0.71” | false for institution (−0.12) and composite (0.40) | Restrict to {Q57, in-group, out-group}. |
| App H −0.82 | artifact −0.80 Spearman / −0.80 Pearson | Round honestly (−0.80) or report the exact statistic. |
| Unrestricted ranges | menus unnamed | State columns for every $[L,U]$ (see reconciliation §2). |
| CLAIM_BOUNDARY A5 | trust coverage entirely negative | Amend: plug-in −0.317; cell-exchangeable band entirely negative; **cluster band crosses 0**. |

Rounding FAILs (Q14 pooled −0.53 vs −0.525; grid −0.317 vs −0.318) are not prose edits.

---

## Pass 4 — Tables to *add* (computations already run)

Do not re-freeze. Copy from `preprint_audit/`.

### 4.1 Diagnostics table (mandatory §3.5, never exhibited)

One table, two panels (patience / trust cells): measure, in $M^*$, $\beta$, select slack, holdout slack, margin, bootstrap SE, $\kappa=2$ flag, $\hat p$ admission.

Load-bearing rows: Q13 knife-edge ($\hat p=0.83$); Llama-trust near-miss rejection ($\hat p=0.022$).

### 4.2 Frozen vs re-formed band (optional one-liner)

Cell-exchangeable frozen-M* vs re-formed bands are nearly the same width. Coupling is $\hat p$(Q13), not extra band width. Can be a sentence under 4.1, not its own table.

### 4.3 Comparative falsification (makes contribution (ii) true)

Two-row table: patience / trust; $\hat p_S$; best-$\beta$; best-anchor; random-$k$ mean; share of random $\ge \hat p_S$.

### 4.4 Leave-one-measure-out (short appendix)

Patience: drop both cheap columns → Q13 singleton (already in text). Trust: drop Phi → empty $M^*$. One table in an appendix is enough.

### 4.5 Cluster band

See 2.4. Source: `preprint_audit/cluster_bootstrap_cells.json`.

---

## Pass 5 — Appendix A (Refine; draft here, Daniel T1)

1. Split population vs sample: $s_r^0(m),\mathscr{M}_0^*,\mathscr{B}_0^*$ vs hats. §3.2 currently uses $s_r$ as sample slack to define $\mathscr{M}^*$ and then talks as if it were the PI object.
2. Prop A.1: define the empty-$\mathcal{R}$ case (max over empty index) and empty-$\mathscr{M}^*$ case ($[L,U]$ undefined).
3. Prop A.2: drop the expectation-over-measures unless a law is stated; report the finite-menu pass proportion; define empty selected sets.
4. $\delta>0$: one sentence that a common additive tolerance is not scale-invariant; application uses $\delta=0$.
5. Observed-score vs latent: two sentences pointing at DGP F — $M^*$ is observed-score suitability for a declared use unless a precision layer is applied. (Daniel T2 may rewrite these.)

---

## Pass 6 — Governance / contracts (not the tex)

- Dated CLAIM_BOUNDARY amendment (cluster band; contested criterion; one-gate cells).
- Dated DECISIONS entry: keep application, shrink claims, 2026-08-31.
- App J “remaining gaps”: add cluster result, unsupported App I co-movement, MC still missing.
- Author note: still “not posted as a preprint” until it is.

---

## Pass 7 — Needed for *submission*, not for the shrink pass

| Item | Why | When |
|---|---|---|
| DGP-B Monte Carlo | Largest methods-journal gap | Mid-September; spec in `SEP2026_COMPUTATION_SPECS.md` |
| Daniel T1–T4 | Psychometric sign-off on A / M* meaning / trust framing / one-gate | Send this week |
| Prompt paraphrase | Confess as limit; do not run for this preprint | R&R or Nature-track |

---

## Do not edit

- $\theta$ on any restriction.
- Plug-in $[0.245,0.556]$ or $-0.317$.
- Empty-$\mathcal{R}$ $[-0.219,0.565]$ or MTMM $0.825/0.284/-0.252/0.706$.
- Freeze hashes / run_ids.
- Recycle $[0.328,0.402]$.
- Call Phi a valid trust measure.
- Promote country ranges to abstract.
- Promote any grid $R_i\neq R_0$ to headline.
- New cell implications on this sample.
- Perwell as demo.
- Equation (12) as a worked causal application.

---

## Execution order

1. Pass 1 (you veto sentence-level diffs).
2. Pass 2 (same).
3. Pass 3 (mechanical; I can do against artifacts).
4. Pass 4 (mechanical tables from audit JSON).
5. Pass 5 draft → Daniel.
6. Pass 6 logs after you accept 1–2.
7. Pass 7 MC in parallel, not blocking 1–4.
