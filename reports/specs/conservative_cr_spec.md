# Conservative confidence region for $[L,U]$, plus bring-your-own β

**Status: APPROVED 2026-10-20 (D1–D12 as recommended; `logs/DECISIONS.md`) and implemented on branch `claude/mystifying-swirles-f3c434` (unreleased, post-3.0.2).** The proposal text below is kept as approved; implementation notes are in the DECISIONS implementation record.
Decision entry: `logs/DECISIONS.md`, "2026-10-20 — PROPOSAL: conservative confidence region (Bonferroni) + bring-your-own β".
Monte Carlo script: `reports/runs/conservative_cr_mc/mc.py` (git-ignored). Results are in §12.

---

## 0. Summary

- **What.** An additive inference layer that reports a confidence region $\mathrm{CR}$ for the *population* construct-identified range $[L_0,U_0]$, with $P([L_0,U_0]\subseteq \mathrm{CR}) \ge 1-\alpha_1-\alpha_2$. It also reports a three-way status for every menu measure: certainly admissible, possibly admissible, certainly rejected.
- **How.** Bonferroni. One-sided confidence bounds on every select-stage slack give an outer set $M^+$ and an inner set $M^-$. Per-measure confidence intervals for $\beta(m)$ are then unioned over $M^+$. No new theory is needed. The guarantee holds under any dependence between the slack estimates and the β estimates. That dependence is the admission–endpoint coupling that Dell & Rambachan flag (§1).
- **Bring-your-own β.** A new β type, `external`, reads `beta_estimates.csv` (`measure, beta_hat, se`, plus optional `df` / cluster information) computed in the user's own pipeline (fixest, pyfixest, Stata, …). The engine still never fits a model.
- **What does not change.** The headline $[L,U]=[\min B^*,\max B^*]$ for every existing β type. The freeze preimage keys and every existing `run_id`. `bootstrap.json` and `coverage.json`. The uncertainty band keeps its "not a CI" label. CR knobs ($\alpha_1,\alpha_2$, variant, SE method) are excluded from the preimage, like `alpha`/`kappa`.
- **Monte Carlo (§12).** 2000 replications × 74 cells. The recommended CR covers at $\ge0.924$ in every Gaussian cell (nominal $\ge0.90$), including when the range-defining measures sit exactly on the boundary. At that knife-edge the current uncertainty band covers only 0.48–0.61 once $n\ge480$. The CR is 1.06× (n = 2000) to 1.45× (n = 41) the band's width.
- **One finding beyond the brief (§3.4, Theorem 3).** The brief's construction (Bonferroni over $K=|M|\cdot|R_S|$ slack bounds and over $|M|$ β intervals) is valid. For covering the *range*, however, the $|M|$ factor is unnecessary. The range endpoints are attained at two fixed but unknown population measures, so Bonferroni over $\min(2,|M|)\cdot|R_S|$ slack bounds and level-$\alpha_2$ β intervals already gives the same $1-\alpha_1-\alpha_2$ guarantee, with a strictly narrower CR whenever $|M|\ge 3$. I recommend this **endpoint** variant for the CR (decision D2). The brief's **simultaneous** variant remains available, because it alone gives menu-wide statements such as "every truly admissible measure is in $M^+$".

---

## 1. Motivation and positioning

Dell & Rambachan, *Construct Validity: Credibility When Measurement Is Cheap*, NBER Summer Institute 2026 Methods Lectures (slides, `conference.nber.org/confer/2026/SI2026/ML/dell3.pdf`), slide 13, "Inference for the Construct-Identified Range". The text below was verified verbatim from the PDF text layer on 2026-10-20:

> For scalar targets, the goal is to estimate a confidence region for: $[L,U]=[\inf_{m\in M^*_{R,\theta}}\beta(m),\ \sup_{m\in M^*_{R,\theta}}\beta(m)]$.
> Valid inference must account for two sources of sampling uncertainty: uncertainty in $\hat\beta(m)$ for each candidate measure; uncertainty in the estimated moment inequalities that determine which measures are classified as admissible.
> These sources are coupled when the measures determining the plug-in endpoints are also near the admissibility boundary.
> Estimation is beyond today's scope, but existing partial-identification and endpoint-inference methods can be combined to estimate a valid, if conservative, confidence region.

This spec implements that sentence literally: existing methods (one-sided moment-inequality bounds, per-endpoint Wald intervals), combined by Bonferroni.

**Package context.** Today's uncertainty output is the P5 coverage band (`inference/coverage.py`, locked 2026-08-08). It reports per-side quantiles of $(L_b,U_b)$ over non-empty bootstrap replicates, carries no coverage claim, and is labeled "not a confidence interval". The paper triage (`paper/PREPRINT_SEP2026_TRIAGE.md`, item 2) calls "the band has no operating characteristics" the largest gap for a methods journal. §12 fills that gap. It also shows *why* the band cannot carry a CI label: at the knife-edge it under-covers badly.

**Not the paper's "fixed-$M^*$ Bonferroni".** Paper §3.5(iv) says, correctly, that "A Bonferroni union computed on a fixed $M^*$ measures interval conservatism, not coupling." The CR here does not condition on $M^*$. It takes its union over $M^+$, a confidence set for the admissible set, so admission uncertainty is part of the construction.

---

## 2. Setup and estimand

- Units $i=1,\dots,n$ are i.i.d. draws from a population $P$ (A1, §4). The menu $M$ ($J=|M|\ge1$), the select-stage restrictions $R_S$ ($Q=|R_S|\ge 0$) with thresholds $\theta$, the tolerance $\delta\ge0$, and β are fixed before the data are seen. Holdout-stage restrictions never vote on admission, so they play no role here.
- Population slack: $s^0_r(m)$ is the population analogue of the engine's sample slack $\hat s_r(m)$. For example, $\rho_P(m,V)-\theta_r$ for `corr_min`. The table in §3.1 gives one per evaluator.
- Population admissible set: $M^*_0=\{m\in M: s^0_r(m)\ge-\delta\ \forall r\in R_S\}$.
- Population target: $\beta_0(m)$, the probability limit of the engine's $\hat\beta(m)$ or of the user's external estimator.
- **Estimand:** $[L_0,U_0]=[\min_{m\in M^*_0}\beta_0(m),\ \max_{m\in M^*_0}\beta_0(m)]$ when $M^*_0\ne\emptyset$. When $M^*_0=\emptyset$ the estimand is the empty set (§5).
- **Extremal measures:** when $M^*_0\neq\emptyset$, fix $m_L\in\arg\min_{M^*_0}\beta_0$ and $m_U\in\arg\max_{M^*_0}\beta_0$. Break ties by menu order. These are deterministic population objects; nothing about them is random.
- The plug-in headline $[L,U]$ and $M^*$ are exactly what the engine computes today.

---

## 3. Construction

### 3.1 Per-pair one-sided slack bounds

For a pair $(m,r)$ and a level $a\in(0,\tfrac12)$, the layer computes $\mathrm{UCB}_r(m;a)$ and $\mathrm{LCB}_r(m;a)$ with
$P\{s^0_r(m)\le \mathrm{UCB}_r(m;a)\}\ge 1-a$ and $P\{s^0_r(m)\ge \mathrm{LCB}_r(m;a)\}\ge 1-a$ (exactly or asymptotically; A2).
Notation: $q_p=\Phi^{-1}(p)$; $z=\operatorname{atanh}(\hat r)$; $\sigma\in\{+1,-1\}$ is the declared sign.

| Type | Population slack | UCB at level $a$ | LCB at level $a$ |
|---|---|---|---|
| `corr_min` | $\rho-\theta$ | $\tanh(z+q_{1-a}\,se_z)-\theta$ | $\tanh(z-q_{1-a}\,se_z)-\theta$ |
| `corr_sign` | $\sigma\rho-\theta$ | $\sigma=+1$: as `corr_min`; $\sigma=-1$: $-\tanh(z-q_{1-a}se_z)-\theta$ | mirror image |
| `corr_zero` | $\theta-\lvert\rho\rvert$ | $\theta-\underline{\lvert\rho\rvert}$, where $[\ell,h]=\tanh(z\mp q_{1-a/2}se_z)$ and $\underline{\lvert\rho\rvert}=0$ if $\ell\le0\le h$, else $\min(\lvert\ell\rvert,\lvert h\rvert)$ | $\theta-\max(\lvert\tanh(z-q_{1-a}se_z)\rvert,\lvert\tanh(z+q_{1-a}se_z)\rvert)$ |
| `mean_order` | $\sigma(\mu_1-\mu_0)-\theta$ | $\sigma\hat d+t_{1-a,\nu}\,se_W-\theta$ (Welch $se_W$, Welch–Satterthwaite $\nu$) | $\sigma\hat d-t_{1-a,\nu}\,se_W-\theta$ |
| `rank_agree` | $\rho_S(m,m_\mathrm{ref})-\theta$ | as `corr_min` on Spearman $\hat r_S$, $se_z=\sqrt{(1+\hat r_S^2/2)/(n-3)}$ (Bonett & Wright 2000) | mirror |
| `monotone_rank` | $\sigma\rho_S(m,V)-\theta$ | as `corr_sign` with the Spearman $se_z$ above | mirror |
| `stability` | schema-only, no evaluator | fails loud (unchanged) | — |

Notes.
1. **Pearson $se_z$.** Two candidates. *Classical*: $1/\sqrt{n-3}$, exact under bivariate normality. *Robust* (kurtosis-adjusted): $se_z=\widehat{\mathrm{sd}}(\psi)/\{(1-\hat r^2)\sqrt{n-3}\}$, with $\psi_i=\tilde x_i\tilde y_i-\tfrac{\hat r}{2}(\tilde x_i^2+\tilde y_i^2)$ the influence function of Pearson's $r$ on standardized data (Devlin, Gnanadesikan & Kettenring 1975). It equals the classical SE under normality and stays valid asymptotically under non-normal fourth moments. The default is decision D4, informed by §12.
2. **`corr_zero` uses the two-sided interval at $a/2$ per side for its UCB.** At $\rho=0$ both tails can push $\underline{\lvert\rho\rvert}$ above $\lvert\rho\rvert$, so per-side $a$ would only control the error at $2a$. With $a/2$ per side the failure event is contained in $\{\ell>\rho\}\cup\{h<\rho\}$, which has probability at most $a$.
3. **Spearman.** The population target is the grade correlation. The Bonett–Wright SE is an approximation; at $n\approx 40$ the bounds are less reliable than the Pearson ones. The tests will pin the formula, not a coverage claim.
4. **Degenerate $\lvert\hat r\rvert=1$** (for example `rank_agree` whose reference is itself a menu member, evaluated on that measure): the statistic is treated as deterministic, so $se=0$ and the bound equals the estimate. This is documented, not silently clipped.
5. Every bound contains its point estimate ($\mathrm{LCB}\le\hat s\le\mathrm{UCB}$ for $a\le\tfrac12$). Proposition 4 relies on this.

### 3.2 Outer set, inner set, statuses

- **Outer set** at per-pair level $a_\mathrm{out}$: $M^+=\{m: \mathrm{UCB}_r(m;a_\mathrm{out})\ge-\delta\ \forall r\in R_S\}$.
- **Inner set** at per-pair level $a_\mathrm{in}$: $M^-=\{m: \mathrm{LCB}_r(m;a_\mathrm{in})\ge-\delta\ \forall r\in R_S\}$.
- **Statuses:** *certainly admissible* = $M^-$; *possibly admissible* = $M^+\setminus M^-$; *certainly rejected* = $M\setminus M^+$.
- Levels (§3.5): $a_\mathrm{in}=\alpha_1/J$. The brief proposed $\alpha_1/(JQ)$. Theorem 2 shows that a factor of $Q$ is not needed, because each truly rejected measure has a fixed violated restriction.

### 3.3 β intervals

Two-sided $[\mathrm{lo}(m),\mathrm{hi}(m)]$ at per-side level $b$:

| β type | Interval |
|---|---|
| `corr_y` | Fisher-z with the same Pearson $se_z$ as the slacks |
| `diff_means` | Welch: $\hat\beta\pm t_{1-b,\nu}\,se_W$ |
| `external` (new, §7) | $\hat\beta\pm c\cdot se$, with $c=t_{1-b,\mathrm{df}}$ if `df` is given (or derived from `n_clusters`), else $q_{1-b}$ |
| `ols_coef`, `map_distance` | **No native interval in v1.** Requesting the CR fails loud with "use β type `external` (compute β and its SE in your pipeline) or the bootstrap-SE mode (D9)". Standardized-coefficient and map-distance SEs need a delta method that the engine does not have today; shipping an approximate one silently would break the "valid" claim. |

### 3.4 The confidence region: two variants

$\mathrm{CR}=[\min_{m\in M^+}\mathrm{lo}(m),\ \max_{m\in M^+}\mathrm{hi}(m)]$ if $M^+\ne\emptyset$; $\mathrm{CR}=\emptyset$ otherwise.

| Variant | $a_\mathrm{out}$ (per slack pair) | $b$ (per β side) | Guarantees |
|---|---|---|---|
| **Endpoint (E), recommended** | $\alpha_1/(\min(2,J)\cdot Q)$ | $\alpha_2/2$ | $P([L_0,U_0]\subseteq\mathrm{CR})\ge1-\alpha_1-\alpha_2$ (Thm 3). Each truly admissible measure is individually in $M^+$ w.p. $\ge 1-\alpha_1/2$ ($J\ge2$). |
| **Simultaneous (S), the brief's** | $\alpha_1/(J\cdot Q)$ | $\alpha_2/(2J)$ | Same range guarantee (Thm 1). It adds two menu-wide statements: $P(M^*_0\subseteq M^+)\ge1-\alpha_1$, and, with probability $\ge 1-\alpha_1-\alpha_2$, every admissible measure is retained *and* its own $\beta_0(m)$ lies in its own interval. |

$\mathrm{CR}_E\subseteq\mathrm{CR}_S$ always: every quantile in E is less extreme than its counterpart in S when $J\ge2$, and the two coincide when $J=1$. With $Q=0$ (`empty_R`), $M^+=M^-=M$ and $\alpha_1$ goes unused. The CR is then a conservative CR for the specification-curve range $[\min_M\beta_0,\max_M\beta_0]$.

### 3.5 Level allocation (defaults, D3)

$\alpha_1=\alpha_2=0.05$, so nominal coverage is $\ge 0.90$. This matches the uncertainty band's default $\alpha=0.10$ and makes them directly comparable. The defaults, the variant and the SE method are recorded in `confidence_region.json` and excluded from the freeze preimage.

---

## 4. Assumptions and proofs

- **A1 (sampling).** Rows are i.i.d. from $P$. The menu, network, θ, δ and β specification are fixed independently of the sample. They are pre-registered or frozen; the θ-anchor audit documents θ.
- **A2 (bound validity).** For every $(m,r)$ and $a$, the bounds of §3.1 satisfy their one-sided coverage, either exactly or as $\liminf_{n}$. If A2 holds uniformly over a class $\mathcal P$, every conclusion below holds uniformly over $\mathcal P$.
- **A3 (β interval validity).** For every $m$ and $b$: $P\{\beta_0(m)<\mathrm{lo}(m)\}\le b$ and $P\{\beta_0(m)>\mathrm{hi}(m)\}\le b$ (exactly or asymptotically). For `external`, A3 is the user's claim about their estimator and SE. The engine records it but cannot verify it.

No assumption is made about the *joint* law of slack estimates and β estimates. That freedom is what lets Bonferroni absorb the coupling.

**Theorem 1 (simultaneous variant).** Under A1–A3, with $a_\mathrm{out}=\alpha_1/(JQ)$ and $b=\alpha_2/(2J)$: (i) $P(M^*_0\subseteq M^+)\ge1-\alpha_1$; (ii) if $M^*_0\ne\emptyset$, $P([L_0,U_0]\subseteq\mathrm{CR}_S)\ge1-\alpha_1-\alpha_2$.

*Proof.* (i) Suppose $m\in M^*_0$ but $m\notin M^+$. Then some $r$ has $\mathrm{UCB}_r(m)<-\delta\le s^0_r(m)$, a bound failure at $(m,r)$. Hence $P(M^*_0\not\subseteq M^+)\le\sum_{m\in M^*_0}\sum_{r\in R_S}a_\mathrm{out}\le JQ\cdot\alpha_1/(JQ)=\alpha_1$. (ii) Let $G=\{M^*_0\subseteq M^+\}\cap\{\beta_0(m)\in[\mathrm{lo}(m),\mathrm{hi}(m)]\ \forall m\in M\}$. By (i) and a union bound over $2J$ one-sided β events at $\alpha_2/(2J)$ each, $P(G^c)\le\alpha_1+\alpha_2$. On $G$: $\min_{M^+}\mathrm{lo}\le\min_{M^*_0}\mathrm{lo}\le\min_{M^*_0}\beta_0=L_0$, and symmetrically $\max_{M^+}\mathrm{hi}\ge U_0$. So $[L_0,U_0]\subseteq\mathrm{CR}_S$. $\square$

**Theorem 2 (inner set).** Under A1–A2 with $a_\mathrm{in}=\alpha_1/J$: $P(M^-\subseteq M^*_0)\ge1-\alpha_1$. Jointly with Theorem 1(i), $P(M^-\subseteq M^*_0\subseteq M^+_S)\ge1-2\alpha_1$.

*Proof.* For each $m\notin M^*_0$, fix a population-violated restriction $r_m$, with $s^0_{r_m}(m)<-\delta$. This choice is deterministic. If $m\in M^-$, then $\mathrm{LCB}_{r_m}(m)\ge-\delta>s^0_{r_m}(m)$, a lower-bound failure at the single pair $(m,r_m)$. A union bound over at most $J$ such measures gives $\le J\cdot\alpha_1/J$. The joint statement follows from the union bound. $\square$

**Theorem 3 (endpoint variant).** Under A1–A3 with $a_\mathrm{out}=\alpha_1/(\min(2,J)\,Q)$ and $b=\alpha_2/2$: if $M^*_0\neq\emptyset$, $P([L_0,U_0]\subseteq\mathrm{CR}_E)\ge1-\alpha_1-\alpha_2$.

*Proof.* Coverage fails only if $\min_{M^+}\mathrm{lo}>L_0$ or $\max_{M^+}\mathrm{hi}<U_0$. If $m_L\in M^+$ and $\mathrm{lo}(m_L)\le\beta_0(m_L)=L_0$, the first cannot happen; the same holds for $m_U$ and the second. So
$$\{\text{fail}\}\subseteq\{m_L\notin M^+\}\cup\{m_U\notin M^+\}\cup\{\mathrm{lo}(m_L)>\beta_0(m_L)\}\cup\{\mathrm{hi}(m_U)<\beta_0(m_U)\}.$$
Because $m_L,m_U\in M^*_0$ are fixed, the argument of Theorem 1(i) applied to these at most $\min(2,J)$ measures bounds the first two events by $\min(2,J)\,Q\,a_\mathrm{out}=\alpha_1$. The last two are single one-sided β events at $\alpha_2/2$ each. $\square$

*Why this is not a loophole.* The procedure does not know $m_L$ or $m_U$. It computes bounds for every measure. The probability calculation only needs the marginal coverage of the bounds at the two fixed extremal measures. The same logic explains why $\max_m \mathrm{hi}(m)$ is a valid upper confidence bound for $\max_m\beta_0(m)$ without Bonferroni over $m$; that is the "projection" bound that Andrews–Kitagawa–McCloskey (2024) sharpen.

**Proposition 4 (deterministic nesting).** On every sample, $M^-\subseteq M^*\subseteq M^+$ and, if $M^*\ne\emptyset$, $[L,U]\subseteq\mathrm{CR}$. *Proof:* every bound and interval contains its point estimate (§3.1 note 5), so admission by LCB implies admission by the point slack, which implies admission by UCB, and $\min_{M^+}\mathrm{lo}\le\min_{M^*}\hat\beta=L$. $\square$ The tests pin this property. It also means the CR can never contradict the headline.

**Remarks.**
- *No separation condition.* The consistency result in paper Appendix A needs measures to be bounded away from the admissibility boundary. Theorems 1–3 do not: a measure with $s^0_r(m)=-\delta$ exactly is in $M^+$ with probability $\ge 1-a_\mathrm{out}$. That knife-edge is where the plug-in and the band fail (§12, $d=0$).
- *Conservativeness has three sources:* Bonferroni over pairs; the outer set retains measures that a sharp procedure would drop; and the union takes the worst lower and upper β bounds over $M^+$ instead of a joint critical value. §6 lists methods that remove each.
- *Not covered:* clustered or dependent units (A1); data-dependent θ (A1); the units-split robust set $M^*_\mathrm{robust}$ (§8); θ-/δ-grid rows (the CR is computed at the declared θ, δ only).

---

## 5. Empty-set conventions

| Situation | Convention | Reading |
|---|---|---|
| $M^*_0=\emptyset$ (population) | Estimand is $\emptyset$; $\emptyset\subseteq\mathrm{CR}$ always, so coverage is vacuous | "Nothing admissible" is a population fact; there is no range to cover |
| $M^+=\emptyset$ (sample) | $\mathrm{CR}=\emptyset$, recorded as `CR_L=CR_U=null`, `empty_outer=true`; exit 0 | **Evidence that $M^*_0=\emptyset$.** Under E, if $M^*_0\ne\emptyset$ then $P(M^+=\emptyset)\le P(m\notin M^+)\le \alpha_1/2$ for any fixed $m\in M^*_0$ ($\le\alpha_1$ under S). So "$M^+=\emptyset$" is a level-$\alpha_1/2$ test of $H_0: M^*_0\ne\emptyset$. |
| $M^*=\emptyset$ but $M^+\neq\emptyset$ | Headline empty (unchanged); CR non-empty and reported | The data do not reject non-emptiness by the row-above test; the empty plug-in is a finding, not a verdict |
| $M^*\neq\emptyset$ | $[L,U]\subseteq\mathrm{CR}$ (Prop. 4) | — |
| $J=1$ or $M^+$ a singleton | CR is the β interval of that measure | — |

**Relation to Bugni, Canay & Shi (2015, *J. Econometrics* 185:259–282).** BCS study specification tests for moment-inequality models, that is, tests of $H_0$: the identified set is non-empty. The traditional "Test BP" rejects when the confidence set is empty. BCS propose tests (RS, RC) that control size uniformly and dominate Test BP in power. "$M^+=\emptyset$" is the finite-menu analogue of Test BP. Over a finite menu it is an intersection–union test: $H_0=\bigcup_m H_{0,m}$, and the test rejects only if every $H_{0,m}$ is rejected. So it needs no Bonferroni over measures, only over the $Q$ restrictions within a measure. A BCS-style improvement would replace the Bonferroni over $Q$ with a joint (max-$t$, bootstrap) critical value across a measure's restrictions. That is deferred (§6).

---

## 6. Sharper alternatives (deferred, not rejected)

- **Chernozhukov, Lee & Rosen (2013, *Econometrica* 81:667–737), intersection bounds.** $L_0=\min_{m\in M^*_0}\beta_0(m)$ is an intersection-type bound over a set that is itself estimated. CLR's precision-corrected estimators and critical values for $\min/\max$ of many estimated bounding functions would replace "max of upper bounds over $M^+$" with a half-median-unbiased endpoint estimator and a joint critical value.
- **Andrews, Kitagawa & McCloskey (2024, *QJE* 139:305–358), inference on winners.** The plug-in endpoint $\hat U=\max_{M^*}\hat\beta$ is a "winner". AKM give conditional and hybrid confidence intervals for the winner's parameter that are much shorter than projection. The complication here is that the selection event also involves the admission inequalities. A conditional-inference version would condition on both $\hat M^*$ and the argmax.
- **Romano, Shaikh & Wolf (2014, *Econometrica* 82:1979–2002), two-step moment-inequality testing.** This is the template for $\alpha_1+\alpha_2$: a first-step confidence region for the slacks at a small level, then a second step that uses it. Their bootstrap critical values would replace Bonferroni over $Q$.
- **Imbens & Manski (2004), Stoye (2009).** These cover the *point* $\beta_0(m^\dagger)$ of an unknown true measure, not the whole range. Such a region is shorter, but it answers a different question. The Dell–Rambachan target is the range, so this spec covers the set.
- **Joint critical values** (max-$t$ over all $(m,r)$ by bootstrap) would recover most of the Bonferroni slack when restrictions are positively correlated.

Each alternative needs its own dated decision, fixture and Monte Carlo. Bonferroni is the valid floor they must beat.

---

## 7. Bring-your-own β (`beta_estimates.csv`)

**Purpose.** Researchers estimate β in their own pipeline: fixed effects, IV, clustered or HAC standard errors, survey weights. The engine should consume those numbers without fitting anything, which keeps the model-free lock intact.

**File contract** (CSV or parquet, read with the same round-trip loader as scores):

| Column | Required | Type / rule |
|---|---|---|
| `measure` | yes | string; the set of rows must equal the menu exactly (no missing, extra or duplicate measures) |
| `beta_hat` | yes | finite float |
| `se` | yes | finite float, $>0$ |
| `df` | no | finite float $>0$; if present, the CR uses $t_\mathrm{df}$ critical values |
| `n_clusters` | no | int $\ge2$; if present and `df` is absent, $\mathrm{df}=n_\mathrm{clusters}-1$ (the default for cluster-robust inference in fixest and Stata) |
| `cluster_var`, `vcov`, `n_obs`, `estimator` | no | documentation strings/ints, hashed and echoed in the report, never used in arithmetic |

Unknown columns fail loud. Every violation fails loud at RESTRICT, before any slack is computed.

**β type `external`.** `beta.yaml`: `type: external`, `outcome: <label>`, `params: {}`. For this type `outcome` is a descriptive label (the user's model outcome) and is **not** bound to a SCORE column (D5). Semantics: $\hat\beta(m):=$ `beta_hat[m]`. Consequences:
- **Headline:** $[L,U]=[\min,\max]$ of `beta_hat` over $M^*$. Survivors-only semantics are unchanged. The headline then follows the user's estimator, which is the point: a CR built on one β and a headline built on another would describe different estimands.
- **CR:** β intervals are $\hat\beta\pm c\cdot se$ (§3.3). Slack bounds are still computed by the engine from `scores.csv`.
- **Bootstrap / coverage band (D6):** replicates re-run admission but cannot re-estimate an external β, so `beta_hat` is held fixed. The band then shows admission variability only. The payload notes say so, and `bootstrap.json` gains no keys: the note travels in `coverage.json`'s existing `note` field and in `confidence_region.json`.
- **θ-grid, δ-grid:** unchanged (β does not depend on θ or δ).
- **Same-units obligation.** The engine cannot check that the user's β was estimated on the same units as `scores.csv`, nor that their SE is valid. The report prints "β supplied externally (sha256 …); validity of `se` is the user's claim". A3 is explicitly the user's assumption.

**Freeze contract (hashing).**
1. Canonical bytes: columns in the fixed order `measure, beta_hat, se, df, n_clusters, cluster_var, vcov, n_obs, estimator`, keeping only columns that are present; rows sorted by `measure` (string sort); cells formatted with the existing `freeze._format_cell` rules (`.17g` floats, integers without decimals, CSV quoting, NaN/Inf fail loud); UTF-8 with a trailing newline. `beta_estimates_hash` is the bare SHA-256 hex of those bytes.
2. **Recommended (D5a):** fold the hash into `beta_hash`, and only for `type: external`:
   `beta_hash = hash_canonical_json({"beta": BetaSpec.model_dump(mode="json"), "beta_estimates_hash": <hex>})`.
   The preimage keys are unchanged, and every existing β type's `beta_hash` is unchanged byte for byte. Two runs that differ only in the estimate table get different `beta_hash` and therefore different `run_id`. That is required, because the table determines the headline.
   *Alternative (D5b):* `config["beta_estimates_hash"]`, the `holdout_units` precedent. It also leaves existing `run_id`s untouched, but `beta_hash` would then no longer identify β.
3. The file path is never hashed (paths are excluded from the preimage by the M1 lock). A new artifact, `beta_estimates.json`, echoes the canonical rows and the hash. `RunManifest` is **not** changed, so no existing manifest gains a key.

---

## 8. Engine contract (Step 3, after approval)

- **Module:** `src/cvprofiles/inference/confidence_region.py` (pure functions, no RNG in analytic mode); `src/cvprofiles/schemas/beta_estimates.py` (pydantic row model + loader); additive `BetaType` literal `"external"`; an optional `RestrictBundle.beta_estimates` field (default `None`); `evaluate_beta` reads external values. Each slack evaluator gains a raw-statistic helper (Pearson $r$, Spearman $r_S$, Welch difference), and a test pins that `evaluate_slack` stays bit-identical when recomputed from that statistic.
- **API:** `run_profile(..., confidence_region: bool = False, cr_alpha1=0.05, cr_alpha2=0.05, cr_variant="endpoint", cr_se=<D4>, beta_estimates: Path | None = None)`.
- **CLI (D10):** `--confidence-region`, `--cr-alpha1`, `--cr-alpha2`, `--cr-variant {endpoint,simultaneous}`, `--beta-estimates PATH` (implementation also exposes `--cr-se {robust,classical}`, mirroring the API's `cr_se`). Stdout stays machine-readable JSON; `summary_dict` gains an additive `confidence_region` key (null when off).
- **Artifact `confidence_region.json`** (present iff requested; removed when the layer is off on reuse of `out_dir`, as the pipeline already does for other layers):
  `schema_version`, `purpose="conservative_confidence_region"`, `label`, `variant`, `alpha1`, `alpha2`, `nominal_coverage`, `se_method`, `n_units`, `n_menu`, `n_select_restrictions`, `delta`, `levels {a_out, a_in, beta_per_side, K_out, K_in}`, `CR_L`, `CR_U`, `empty_outer`, `M_plus`, `M_minus`, `status {measure: certainly_admissible|possibly_admissible|certainly_rejected}`, `slack_bounds [{measure, restriction, statistic, se, slack_hat, ucb, lcb}]`, `beta_intervals [{measure, beta_hat, se, lo, hi, source, df}]`, `beta_estimates_hash`, `target="select_stage_population_range"`, `note`, `headline_note` ("Headline [L,U] remains min/max B* on the full sample; the confidence region is additive and never replaces it.").
- **Report:** a "Conservative confidence region" panel under the range box with the CR, the nominal level, and a status column per measure. The uncertainty band panel keeps its wording.
- **Freeze:** CR knobs are excluded from the preimage. Witness tests: same bundle with and without the CR, and with different $\alpha$, give the same `run_id`. Golden `run_id`s are unchanged. External β enters only through §7.
- **Incompatibilities that fail loud (D7, D8):** `holdout_units` together with the CR (the CR targets the select-stage full-frame population range, not $M^*_\mathrm{robust}$); `ols_coef`/`map_distance` together with the CR in analytic mode; $n<4$ (Fisher-z needs $n-3>0$); a `mean_order` or `diff_means` group with fewer than 2 units (Welch variance undefined); `stability` (already fails).

---

## 9. Scope, limitations, non-goals

- **i.i.d. units only.** Engine-native slack bounds assume independent rows. With clustered data (cells within countries), the CR is invalid unless the user aggregates to the cluster level. External β may carry cluster-robust SEs, but the slack side would still be i.i.d. A cluster-robust slack layer (summing influence functions within clusters, plus a declared cluster role that enters `scores_hash`) is a separate, later decision.
- **No percentile-bootstrap bounds.** Bonferroni quantiles are extreme: at $J=20$, $Q=2$ the simultaneous variant needs the $1-0.05/40$ quantile, which a percentile bootstrap would need $B\gg 10^4$ replicates to estimate. The optional bootstrap-SE mode (D9) uses bootstrap standard errors with normal critical values on the Fisher-z scale. It reuses the run's existing draws (same seed, no new RNG stream), collects statistics over **all** non-degenerate replicates (not only non-empty ones), and leaves `bootstrap.json` unchanged.
- **Non-goals:** CLR, AKM or joint-critical-value sharpening (§6); a CR for θ-/δ-grid rows; coverage of the units-split robust set; any automatic loosening of θ when $M^+=\emptyset$; CR-driven model selection.
- **Label discipline.** "Conservative confidence region" is used only for this object. The P5 band remains "uncertainty band — not a confidence interval". The headline remains the plug-in.

---

## 10. Decision points for Augusto

| # | Decision | Recommendation |
|---|---|---|
| D1 | Adopt the additive CR layer and the `confidence_region.json` artifact | Yes |
| D2 | CR variant | **Endpoint (E)** as default, with `simultaneous` (S) as an option. S is the brief's construction. E is valid at the same level and narrower (Thm 3; §12) |
| D3 | Defaults $\alpha_1=\alpha_2$ | 0.05 each (nominal 90%, matching the band's $\alpha=0.10$) |
| D4 | Pearson SE default | **Robust (influence-function) Fisher-z.** Same coverage as classical under normality; classical under-covers under $t_5$ tails (0.896 at $n=480$; §12 finding 6) |
| D5 | External β: β type `external` defines the headline; hash folded into `beta_hash` (D5a) | Yes, D5a; `outcome` is an unbound label for this type |
| D6 | External β with bootstrap on | Allowed, β held fixed, labeled in the notes (rather than failing loud) |
| D7 | CR with `holdout_units` | Fail loud in v1 |
| D8 | CR with `ols_coef` / `map_distance` | Fail loud in analytic mode; route through `external` (or D9) |
| D9 | Bootstrap-SE mode in the first implementation | Defer to a follow-up decision. v1 = analytic + external, to keep the first engine change thin; the MC shows no coverage gain over robust analytic SEs (§12 finding 6) |
| D10 | CLI flags in v1 | Yes (bring-your-own β is useless without a CLI path) |
| D11 | Where this spec lives | Tracked at `reports/specs/` on this branch; move to `docs/` or untrack under the 2026-08-21 hygiene rule if you prefer |
| D12 | Release | No version bump, tag, push or PyPI from this work; a later 3.1.0 is your call |

---

## 11. TDD plan (Step 3, after approval)

RED tests first, one behavior each, in `tests/test_confidence_region.py` and `tests/test_beta_external.py`:
1. Bound formulas per evaluator against hand-computed values (Fisher-z classical and robust; `corr_zero` straddle and non-straddle cases; Welch with $\nu$; Spearman Bonett–Wright; $\sigma=-1$ mirrors; $\lvert r\rvert=1$ degenerate).
2. Nesting (Prop. 4) on `mini_v1` and on synthetic scenarios: $M^-\subseteq M^*\subseteq M^+$, $[L,U]\subseteq\mathrm{CR}$.
3. Level bookkeeping: E uses $K_\mathrm{out}=\min(2,J)Q$; S uses $JQ$; $K_\mathrm{in}=J$; $\mathrm{CR}_E\subseteq\mathrm{CR}_S$.
4. Empty conventions: `all_invalid` synthetic gives $M^+=\emptyset$ → nulls + `empty_outer=true`, exit 0; `empty_R` gives $M^+=M$ and the CR equals the union of β intervals.
5. Freeze: same bundle with and without the CR, and with different $\alpha$, give identical `run_id`; golden `mini_v1` `run_id` unchanged; headline identity regression (extends the P5 pin).
6. Fail-loud: CR + `holdout_units`; CR + `ols_coef`; malformed `beta_estimates.csv` (missing, extra or duplicate measure; non-positive se; NaN; unknown column).
7. External β: headline = min/max of `beta_hat` over $M^*$; `beta_hash` changes with table content and not with row order; existing β types' `beta_hash` byte-identical; bootstrap holds β fixed.
8. Report/CLI: panel present iff requested; stale `confidence_region.json` removed; stdout is JSON; `summary_dict` key additive.
9. Monte Carlo smoke (small, seeded): coverage $\ge 1-\alpha_1-\alpha_2-$ MC tolerance on one knife-edge cell, using the package implementation.

Then the full battery (`ruff`, `mypy --strict`, `pytest`, `git diff --check`, the `v0.1` peel check) and a golden-run_id diff before the commit.

---

## 12. Monte Carlo of operating characteristics

This section fills the "the band has no operating characteristics" gap (paper triage item 2). It reports operating characteristics only. It claims no theorem and is not paper evidence until you place it.

### 12.1 Design

- **Script:** `reports/runs/conservative_cr_mc/mc.py` (git-ignored, as are `mc_results.json` and `mc_tables.md` next to it). One `SeedSequence(20261020)` tree: one child per cell, and one data/bootstrap pair per replication. 2000 replications per cell; `n_boot = 999`; 10 worker processes; 240 s wall clock.
- **Engine equivalence:** `mc.py --check` runs four cells through `run_identify`, `run_bootstrap` and `compute_coverage` from the package, with the same seeds. The vectorized MC path reproduces $M^*$, $[L,U]$, the empty-replicate rate, and both bands to a worst absolute difference of $4.4\times10^{-16}$. The band columns are therefore the engine's band, not a re-implementation of it.
- **DGP:** independent $C, W\sim N(0,1)$; $V=0.8C+0.6e_V$; $Y=0.5C+0.6W+\sqrt{0.39}\,e_Y$; $m_j=a_jC+b_jW+\sqrt{1-a_j^2-b_j^2}\,e_j$. Hence $\rho(m,V)=0.8a$, $\rho(m,W)=b$, and $\beta_0(m)=\rho(m,Y)=0.5a+0.6b$ (`corr_y`).
- **Network** ($Q=2$, $\delta=0$; an oracle network authored for this synthetic DGP only): `corr_min(V, 0.40)` and `corr_zero(W, 0.30)`.
- **Menu**, built to put the coupling regime in the target:
  - `edge_lo` has `corr_min` slack $=d$ and the *lowest* β;
  - `edge_hi` has `corr_zero` slack $=d$ and the *highest* β, because it is confounded with $W$, which also drives $Y$;
  - core measures sit 0.16–0.32 inside the `corr_min` floor and 0.25–0.30 inside the `corr_zero` bound;
  - invalid measures miss at least one restriction by 0.16–0.40;
  - $J=3$: 1 core + 2 edges. $J=6$: 3 core + 2 edges + 1 invalid. $J=20$: 12 core + 2 edges + 6 invalid.
- **Boundary distance** $d\in\{-0.10,-0.03,0,+0.03,+0.10\}$, in raw slack units. With $d\ge0$ the edges are admissible and *define* $[L_0,U_0]$. With $d<0$ they are near-miss rejections and $[L_0,U_0]$ is the core range. Column "d/SE" converts $d$ to sampling-SE units for `edge_lo`.
- **Coverage** means both endpoints are covered: $\mathrm{lo}\le L_0$ and $\mathrm{hi}\ge U_0$. A null interval (empty plug-in, all replicates empty, $M^+=\emptyset$) counts as non-coverage, because $M^*_0\ne\emptyset$ in every main cell.
- **Supplements:** standardized $t_5$ shocks (same population correlations, heavier fourth moments) to choose the SE; and an empty-population design to measure how often "$M^+=\emptyset$" fires.

### 12.2 Findings

1. **The CR delivers its guarantee, including at the knife-edge.** Endpoint variant: minimum coverage 0.924 over all 60 Gaussian cells (nominal $\ge0.90$), mean 0.973. Simultaneous variant: minimum 0.965. The worst cells are always $d=0$, the knife-edge, and the endpoint CR stays above nominal there at every $n$.
2. **The current uncertainty band is not a confidence set, and it fails where slide 13 says coupling bites.** At $d=0$ its coverage falls with $n$: 0.72–0.96 at $n=41$, 0.58–0.88 at $n=120$, and 0.48–0.61 at $n\in\{480,2000\}$. At $d=+0.03$ it is 0.73–0.93 for $n\ge120$, and 0.77–0.87 for $n\ge480$. Away from the boundary ($d=\pm0.10$, large $n$) it is roughly nominal. Its averages hide the failure (mean 0.881). The 95% `bootstrap.json` band shows the same pattern (minimum 0.666). This is a direct finite-sample demonstration of slide 13's coupling: the plug-in admits a knife-edge measure about half the time, and the band inherits that coin flip.
3. **The plug-in $[L,U]$ is a point estimate of a set.** Its coverage ranges from 0.00 to 0.67 (mean 0.20). In the $d\in\{0,+0.03\}$ cells it recovers $M^*_0$ exactly in only 14–89% of replications (Table E).
4. **What validity costs.** Endpoint CR width (robust SE) relative to band width: 1.41–1.45 at $n=41$, 1.25–1.31 at $n=120$, 1.14–1.17 at $n=480$, 1.06 at $n=2000$ (rows with $d=+0.03$). The population width there is 0.293. At $n=41$ the endpoint CR is 0.78–1.03 wide on a correlation scale. That is honest: at country-level $n$ a range of correlations cannot be pinned down once admission uncertainty is priced in.
5. **The endpoint variant is worth adopting (D2).** Relative to S it is 4–26% narrower ($\mathrm{CR}_E/\mathrm{CR}_S$ width ratio 0.74–0.96), with the largest gains at large $J$ and small $n$, and it still never under-covers.
6. **Robust SE should be the default (D4).** Under Gaussian data, robust and classical Fisher-z are indistinguishable (minimum 0.924 vs 0.925). Under $t_5$ tails, the classical endpoint CR drops *below nominal*: 0.896 at $n=480$, $d=0$. The robust and bootstrap-SE versions hold at 0.951–0.954. Bootstrap SEs add nothing over the robust analytic SE in this DGP, which supports deferring bootstrap-SE mode (D9).
7. **Status sets are valid and conservative.** $P(M^*_0\subseteq M^+_S)\ge0.976$ (nominal 0.95). $P(M^-\subseteq M^*_0)\ge0.988$ over the whole grid. However, **at $n=41$, $M^-$ is empty in every replication of every cell** (classical SE): no measure can be certified admissible at country-level sample sizes, not even core measures 0.16–0.32 inside the floor. The binding obstacle is the discriminant `corr_zero(W, 0.30)`. Certifying it needs an upper bound on $\lvert\rho\rvert$ below 0.30. At $n=41$, $J=3$ the upper bound is already $\approx0.33$ when $\hat\rho_W=0$. By $n=480$, $M^-$ recovers most core measures. Knife-edge measures are never certified, as they should not be.
8. **"$M^+=\emptyset$" is a valid but low-power test of $M^*_0\neq\emptyset$ (Table D).** When every measure misses its floor by 0.05, it fires 0% of the time at $n\le480$ and 14% at $n=2000$. At a miss of 0.15 it fires 63% at $n=480$ and 100% at $n=2000$. The plug-in empties much sooner but carries no error control. This is the kind of power loss Bugni–Canay–Shi document for by-product tests, and it is the first place a sharper method (§6) would pay off.

### 12.3 What the Monte Carlo does not show

- Only one network shape: Pearson `corr_min` + `corr_zero` with β = `corr_y`. Spearman, `mean_order`/Welch, `diff_means` and external-β paths are covered by unit tests, not by the MC.
- i.i.d. units only; no clustering.
- Exactly two near-boundary measures, both β-extreme. Designs with many near-boundary measures, or with near-boundary measures that are not β-extreme, were not run.
- Synthetic design authored by the agent for operating characteristics, not the flagship application. Running the CR on the WVS/GPS frozen inputs is a separate step that needs your go-ahead (the run gate).

### 12.4 Tables

Seed 20261020; 2000 replications per cell; n_boot = 999; α1 = α2 = 0.05 (CR nominal ≥ 0.90); band α = 0.1 (nominal 0.90, no guarantee); numpy 2.5.1; wall clock 240 s. MC standard error of a coverage near 0.90 is ≈ 0.007.

**A. Coverage of $[L_0,U_0]$ over the 60 Gaussian cells**

| Method | min | mean | min at $d=0$ | min at $d=+0.03$ |
|---|---|---|---|---|
| plug-in [L,U] | 0.000 | 0.202 | 0.022 | 0.047 |
| coverage band (α=0.10) | 0.483 | 0.881 | 0.483 | 0.734 |
| bootstrap.json band (95%) | 0.666 | 0.933 | 0.666 | 0.860 |
| CR, simultaneous, classical SE | 0.970 | 0.995 | 0.970 | 0.981 |
| CR, simultaneous, robust SE | 0.965 | 0.994 | 0.965 | 0.979 |
| CR, endpoint, classical SE | 0.925 | 0.975 | 0.925 | 0.945 |
| CR, endpoint, robust SE | 0.924 | 0.973 | 0.924 | 0.943 |
| CR, endpoint, bootstrap SE | 0.925 | 0.974 | 0.925 | 0.945 |

**B. Full Gaussian grid** (coverage; widths are means over replications with a non-empty interval; CR columns use the robust SE recommended in D4)

| n | J | d | d/SE | width₀ | plug-in | band .10 | band .05 | CR_S | CR_E | W band .10 | W CR_S | W CR_E | empty-rep |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | 3 | -0.10 | -0.70 | 0.000 | 0.220 | 0.988 | 0.996 | 1.000 | 0.998 | 0.541 | 0.967 | 0.869 | 0.122 |
| 41 | 3 | -0.03 | -0.22 | 0.000 | 0.349 | 0.991 | 0.997 | 1.000 | 1.000 | 0.554 | 0.925 | 0.828 | 0.102 |
| 41 | 3 | +0.00 | +0.00 | 0.330 | 0.036 | 0.718 | 0.850 | 0.986 | 0.953 | 0.555 | 0.906 | 0.809 | 0.093 |
| 41 | 3 | +0.03 | +0.24 | 0.293 | 0.047 | 0.809 | 0.905 | 0.992 | 0.970 | 0.551 | 0.876 | 0.779 | 0.080 |
| 41 | 3 | +0.10 | +0.85 | 0.208 | 0.112 | 0.898 | 0.952 | 0.993 | 0.972 | 0.541 | 0.820 | 0.720 | 0.070 |
| 41 | 6 | -0.10 | -0.70 | 0.080 | 0.429 | 0.995 | 1.000 | 1.000 | 1.000 | 0.629 | 1.140 | 0.980 | 0.026 |
| 41 | 6 | -0.03 | -0.22 | 0.080 | 0.458 | 0.996 | 0.998 | 1.000 | 1.000 | 0.632 | 1.106 | 0.942 | 0.024 |
| 41 | 6 | +0.00 | +0.00 | 0.330 | 0.058 | 0.875 | 0.940 | 0.998 | 0.981 | 0.629 | 1.090 | 0.923 | 0.026 |
| 41 | 6 | +0.03 | +0.24 | 0.293 | 0.085 | 0.919 | 0.962 | 0.997 | 0.985 | 0.625 | 1.081 | 0.907 | 0.024 |
| 41 | 6 | +0.10 | +0.85 | 0.208 | 0.196 | 0.967 | 0.989 | 0.999 | 0.990 | 0.618 | 1.050 | 0.872 | 0.021 |
| 41 | 20 | -0.10 | -0.70 | 0.133 | 0.641 | 0.999 | 1.000 | 1.000 | 1.000 | 0.737 | 1.323 | 1.066 | 0.003 |
| 41 | 20 | -0.03 | -0.22 | 0.133 | 0.665 | 1.000 | 1.000 | 1.000 | 1.000 | 0.731 | 1.307 | 1.046 | 0.004 |
| 41 | 20 | +0.00 | +0.00 | 0.330 | 0.138 | 0.959 | 0.980 | 1.000 | 0.994 | 0.728 | 1.300 | 1.034 | 0.004 |
| 41 | 20 | +0.03 | +0.24 | 0.293 | 0.205 | 0.980 | 0.993 | 1.000 | 0.995 | 0.728 | 1.298 | 1.028 | 0.004 |
| 41 | 20 | +0.10 | +0.85 | 0.208 | 0.423 | 0.993 | 0.995 | 1.000 | 0.995 | 0.727 | 1.293 | 1.017 | 0.004 |
| 120 | 3 | -0.10 | -1.20 | 0.000 | 0.135 | 0.982 | 0.994 | 1.000 | 0.996 | 0.389 | 0.720 | 0.648 | 0.013 |
| 120 | 3 | -0.03 | -0.38 | 0.000 | 0.404 | 0.996 | 1.000 | 1.000 | 1.000 | 0.435 | 0.693 | 0.632 | 0.009 |
| 120 | 3 | +0.00 | +0.00 | 0.330 | 0.028 | 0.584 | 0.746 | 0.974 | 0.947 | 0.439 | 0.668 | 0.606 | 0.007 |
| 120 | 3 | +0.03 | +0.40 | 0.293 | 0.048 | 0.734 | 0.860 | 0.979 | 0.948 | 0.442 | 0.640 | 0.578 | 0.006 |
| 120 | 3 | +0.10 | +1.46 | 0.208 | 0.154 | 0.911 | 0.956 | 0.993 | 0.966 | 0.421 | 0.563 | 0.501 | 0.003 |
| 120 | 6 | -0.10 | -1.20 | 0.080 | 0.329 | 0.993 | 0.998 | 1.000 | 0.999 | 0.452 | 0.815 | 0.688 | 0.001 |
| 120 | 6 | -0.03 | -0.38 | 0.080 | 0.507 | 1.000 | 1.000 | 1.000 | 1.000 | 0.474 | 0.771 | 0.660 | 0.000 |
| 120 | 6 | +0.00 | +0.00 | 0.330 | 0.026 | 0.726 | 0.852 | 0.993 | 0.957 | 0.474 | 0.745 | 0.632 | 0.000 |
| 120 | 6 | +0.03 | +0.40 | 0.293 | 0.068 | 0.845 | 0.921 | 0.998 | 0.964 | 0.472 | 0.724 | 0.609 | 0.000 |
| 120 | 6 | +0.10 | +1.46 | 0.208 | 0.195 | 0.936 | 0.971 | 0.998 | 0.968 | 0.455 | 0.666 | 0.549 | 0.000 |
| 120 | 20 | -0.10 | -1.20 | 0.133 | 0.509 | 1.000 | 1.000 | 1.000 | 1.000 | 0.519 | 0.943 | 0.726 | 0.000 |
| 120 | 20 | -0.03 | -0.38 | 0.133 | 0.618 | 1.000 | 1.000 | 1.000 | 1.000 | 0.526 | 0.909 | 0.699 | 0.000 |
| 120 | 20 | +0.00 | +0.00 | 0.330 | 0.041 | 0.877 | 0.936 | 0.999 | 0.973 | 0.524 | 0.893 | 0.679 | 0.000 |
| 120 | 20 | +0.03 | +0.40 | 0.293 | 0.089 | 0.927 | 0.963 | 1.000 | 0.972 | 0.521 | 0.880 | 0.652 | 0.000 |
| 120 | 20 | +0.10 | +1.46 | 0.208 | 0.279 | 0.983 | 0.994 | 1.000 | 0.992 | 0.508 | 0.850 | 0.612 | 0.000 |
| 480 | 3 | -0.10 | -2.41 | 0.000 | 0.011 | 0.944 | 0.979 | 0.996 | 0.980 | 0.186 | 0.396 | 0.341 | 0.000 |
| 480 | 3 | -0.03 | -0.76 | 0.000 | 0.272 | 0.991 | 0.997 | 1.000 | 0.997 | 0.336 | 0.523 | 0.486 | 0.000 |
| 480 | 3 | +0.00 | +0.00 | 0.330 | 0.025 | 0.483 | 0.667 | 0.965 | 0.924 | 0.367 | 0.498 | 0.466 | 0.000 |
| 480 | 3 | +0.03 | +0.81 | 0.293 | 0.090 | 0.767 | 0.872 | 0.979 | 0.943 | 0.373 | 0.467 | 0.435 | 0.000 |
| 480 | 3 | +0.10 | +2.92 | 0.208 | 0.190 | 0.895 | 0.949 | 0.985 | 0.950 | 0.324 | 0.384 | 0.352 | 0.000 |
| 480 | 6 | -0.10 | -2.41 | 0.080 | 0.223 | 0.972 | 0.990 | 1.000 | 0.988 | 0.260 | 0.496 | 0.399 | 0.000 |
| 480 | 6 | -0.03 | -0.76 | 0.080 | 0.408 | 0.994 | 1.000 | 1.000 | 0.999 | 0.360 | 0.548 | 0.491 | 0.000 |
| 480 | 6 | +0.00 | +0.00 | 0.330 | 0.022 | 0.550 | 0.715 | 0.988 | 0.936 | 0.377 | 0.519 | 0.470 | 0.000 |
| 480 | 6 | +0.03 | +0.81 | 0.293 | 0.092 | 0.796 | 0.892 | 0.993 | 0.945 | 0.379 | 0.486 | 0.437 | 0.000 |
| 480 | 6 | +0.10 | +2.92 | 0.208 | 0.199 | 0.925 | 0.963 | 0.994 | 0.960 | 0.332 | 0.407 | 0.357 | 0.000 |
| 480 | 20 | -0.10 | -2.41 | 0.133 | 0.262 | 0.991 | 0.997 | 1.000 | 0.996 | 0.316 | 0.582 | 0.426 | 0.000 |
| 480 | 20 | -0.03 | -0.76 | 0.133 | 0.473 | 0.999 | 1.000 | 1.000 | 1.000 | 0.378 | 0.581 | 0.497 | 0.000 |
| 480 | 20 | +0.00 | +0.00 | 0.330 | 0.029 | 0.612 | 0.762 | 0.997 | 0.951 | 0.390 | 0.548 | 0.470 | 0.000 |
| 480 | 20 | +0.03 | +0.81 | 0.293 | 0.092 | 0.844 | 0.918 | 0.998 | 0.955 | 0.385 | 0.514 | 0.437 | 0.000 |
| 480 | 20 | +0.10 | +2.92 | 0.208 | 0.209 | 0.956 | 0.978 | 1.000 | 0.972 | 0.344 | 0.442 | 0.364 | 0.000 |
| 2000 | 3 | -0.10 | -4.91 | 0.000 | 0.000 | 0.903 | 0.956 | 0.989 | 0.959 | 0.062 | 0.092 | 0.075 | 0.000 |
| 2000 | 3 | -0.03 | -1.55 | 0.000 | 0.075 | 0.980 | 0.993 | 0.999 | 0.994 | 0.223 | 0.390 | 0.360 | 0.000 |
| 2000 | 3 | +0.00 | +0.00 | 0.330 | 0.026 | 0.501 | 0.666 | 0.972 | 0.935 | 0.337 | 0.414 | 0.397 | 0.000 |
| 2000 | 3 | +0.03 | +1.65 | 0.293 | 0.170 | 0.861 | 0.929 | 0.981 | 0.947 | 0.344 | 0.380 | 0.364 | 0.000 |
| 2000 | 3 | +0.10 | +5.96 | 0.208 | 0.177 | 0.888 | 0.947 | 0.980 | 0.946 | 0.267 | 0.294 | 0.278 | 0.000 |
| 2000 | 6 | -0.10 | -4.91 | 0.080 | 0.188 | 0.921 | 0.964 | 0.994 | 0.960 | 0.146 | 0.186 | 0.158 | 0.000 |
| 2000 | 6 | -0.03 | -1.55 | 0.080 | 0.250 | 0.986 | 0.994 | 1.000 | 0.996 | 0.262 | 0.427 | 0.379 | 0.000 |
| 2000 | 6 | +0.00 | +0.00 | 0.330 | 0.028 | 0.510 | 0.680 | 0.988 | 0.941 | 0.344 | 0.423 | 0.398 | 0.000 |
| 2000 | 6 | +0.03 | +1.65 | 0.293 | 0.153 | 0.867 | 0.931 | 0.992 | 0.953 | 0.343 | 0.388 | 0.363 | 0.000 |
| 2000 | 6 | +0.10 | +5.96 | 0.208 | 0.192 | 0.912 | 0.965 | 0.995 | 0.963 | 0.268 | 0.304 | 0.280 | 0.000 |
| 2000 | 20 | -0.10 | -4.91 | 0.133 | 0.188 | 0.942 | 0.974 | 0.999 | 0.969 | 0.200 | 0.257 | 0.211 | 0.000 |
| 2000 | 20 | -0.03 | -1.55 | 0.133 | 0.263 | 0.997 | 1.000 | 1.000 | 0.999 | 0.289 | 0.461 | 0.388 | 0.000 |
| 2000 | 20 | +0.00 | +0.00 | 0.330 | 0.033 | 0.506 | 0.675 | 0.996 | 0.930 | 0.347 | 0.437 | 0.397 | 0.000 |
| 2000 | 20 | +0.03 | +1.65 | 0.293 | 0.140 | 0.866 | 0.940 | 0.999 | 0.957 | 0.344 | 0.402 | 0.364 | 0.000 |
| 2000 | 20 | +0.10 | +5.96 | 0.208 | 0.177 | 0.919 | 0.956 | 1.000 | 0.953 | 0.270 | 0.319 | 0.280 | 0.000 |

**C. Heavy tails (standardized t5 shocks; J = 6): SE choice**

| n | d | band .10 | CR_E classical | CR_E robust | CR_E bootstrap | CR_S classical | W CR_E robust |
|---|---|---|---|---|---|---|---|
| 41 | +0.00 | 0.841 | 0.964 | 0.968 | 0.974 | 0.996 | 0.944 |
| 41 | +0.03 | 0.880 | 0.980 | 0.976 | 0.979 | 0.997 | 0.928 |
| 120 | +0.00 | 0.741 | 0.932 | 0.951 | 0.949 | 0.989 | 0.658 |
| 120 | +0.03 | 0.830 | 0.951 | 0.960 | 0.964 | 0.986 | 0.633 |
| 480 | +0.00 | 0.567 | 0.896 | 0.951 | 0.954 | 0.974 | 0.488 |
| 480 | +0.03 | 0.795 | 0.926 | 0.960 | 0.961 | 0.980 | 0.455 |

**D. Empty population ($M^*_0=\emptyset$; J = 6, every measure misses the `corr_min` floor by $|d|$)**

| n | d | P(plug-in $M^*=\emptyset$) | mean band empty-rep | P($M^+_E=\emptyset$) robust | P($M^+_S=\emptyset$) robust |
|---|---|---|---|---|---|
| 41 | -0.05 | 0.140 | 0.136 | 0.000 | 0.000 |
| 41 | -0.15 | 0.420 | 0.309 | 0.000 | 0.000 |
| 120 | -0.05 | 0.216 | 0.141 | 0.000 | 0.000 |
| 120 | -0.15 | 0.819 | 0.564 | 0.005 | 0.001 |
| 480 | -0.05 | 0.561 | 0.351 | 0.000 | 0.000 |
| 480 | -0.15 | 1.000 | 0.972 | 0.632 | 0.405 |
| 2000 | -0.05 | 0.971 | 0.830 | 0.138 | 0.039 |
| 2000 | -0.15 | 1.000 | 1.000 | 1.000 | 1.000 |

**E. Status sets (Gaussian grid, robust SE)**

| n | J | d | $\lvert M^*_0\rvert$ | mean $\lvert M^+_S\rvert$ (classical) | mean $\lvert M^+_E\rvert$ (classical) | mean $\lvert M^-\rvert$ (classical) | P($M^*_0\subseteq M^+_S$) | P($M^-\subseteq M^*_0$) | P(plug-in $M^*=M^*_0$) |
|---|---|---|---|---|---|---|---|---|---|
| 41 | 3 | +0.00 | 3 | 2.98 | 2.98 | 0.00 | 0.976 | 1.000 | 0.235 |
| 41 | 3 | +0.03 | 3 | 2.99 | 2.99 | 0.00 | 0.987 | 1.000 | 0.324 |
| 41 | 6 | +0.00 | 5 | 5.78 | 5.63 | 0.00 | 0.987 | 1.000 | 0.190 |
| 41 | 6 | +0.03 | 5 | 5.78 | 5.65 | 0.00 | 0.993 | 1.000 | 0.270 |
| 41 | 20 | +0.00 | 14 | 17.77 | 16.37 | 0.00 | 0.997 | 1.000 | 0.142 |
| 41 | 20 | +0.03 | 14 | 17.77 | 16.36 | 0.00 | 0.995 | 1.000 | 0.197 |
| 120 | 3 | +0.00 | 3 | 2.99 | 2.98 | 0.79 | 0.985 | 1.000 | 0.261 |
| 120 | 3 | +0.03 | 3 | 3.00 | 2.99 | 0.79 | 0.996 | 1.000 | 0.415 |
| 120 | 6 | +0.00 | 5 | 5.25 | 5.13 | 1.43 | 0.990 | 1.000 | 0.243 |
| 120 | 6 | +0.03 | 5 | 5.28 | 5.15 | 1.50 | 0.999 | 1.000 | 0.406 |
| 120 | 20 | +0.00 | 14 | 15.20 | 14.43 | 3.33 | 0.995 | 1.000 | 0.236 |
| 120 | 20 | +0.03 | 14 | 15.24 | 14.46 | 3.26 | 0.999 | 1.000 | 0.411 |
| 480 | 3 | +0.00 | 3 | 2.99 | 2.98 | 1.03 | 0.983 | 1.000 | 0.255 |
| 480 | 3 | +0.03 | 3 | 3.00 | 3.00 | 1.18 | 0.999 | 1.000 | 0.595 |
| 480 | 6 | +0.00 | 5 | 4.99 | 4.98 | 3.00 | 0.993 | 1.000 | 0.242 |
| 480 | 6 | +0.03 | 5 | 5.00 | 5.00 | 3.09 | 1.000 | 1.000 | 0.613 |
| 480 | 20 | +0.00 | 14 | 14.00 | 13.98 | 11.92 | 0.996 | 1.000 | 0.275 |
| 480 | 20 | +0.03 | 14 | 14.00 | 14.00 | 11.96 | 1.000 | 1.000 | 0.593 |
| 2000 | 3 | +0.00 | 3 | 2.99 | 2.98 | 1.03 | 0.989 | 1.000 | 0.258 |
| 2000 | 3 | +0.03 | 3 | 3.00 | 3.00 | 1.56 | 1.000 | 1.000 | 0.879 |
| 2000 | 6 | +0.00 | 5 | 4.99 | 4.98 | 3.02 | 0.993 | 1.000 | 0.258 |
| 2000 | 6 | +0.03 | 5 | 5.00 | 5.00 | 3.40 | 1.000 | 1.000 | 0.892 |
| 2000 | 20 | +0.00 | 14 | 14.00 | 13.98 | 12.01 | 0.998 | 1.000 | 0.255 |
| 2000 | 20 | +0.03 | 14 | 14.00 | 14.00 | 12.21 | 1.000 | 1.000 | 0.876 |

