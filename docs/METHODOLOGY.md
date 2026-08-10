# Methodology

**Canonical methodology statement (locked 2026-08-06, B4).** This document states what cvprofiles does, why, and what it deliberately does not claim. It supersedes the earlier `03_Methodology.md` scaffold (archived). Package semantics are canonical where this doc and code disagree.

- Package version: `2.5.2` — the engine version this method statement describes; kept in sync by the version-consistency CI check.

## 1. The question

Empirical research increasingly fills regressors, text scores, and outcome proxies with cheap multi-measure AI operationalizations of latent constructs: sentiment, uncertainty, ideology, "AI exposure," soft skills, generalized trust. Typical practice is to pick a favorite prompt or dictionary, run a point estimate, and gesture at "robustness." That collapses measurement uncertainty into a single column and invites overclaiming.

cvprofiles treats **construct validity** as a **partial-identification problem over a finite menu of measurement functions**:

> Which operationalizations are admissible under a stated nomological network, and what set of downstream estimates follows?

The closest methodological ancestor is Leamer-style specification uncertainty, moved from regression specifications to measurement functions and disciplined by a researcher-stated network rather than a kitchen-sink search. The formal home is partial identification: the object of inference is a set, not a point.

**Non-claims.** cvprofiles does not claim that all of economics is inequalities. It does not claim new sharp partial-identification theory (sharp theory is optional garnish; transparent slacks plus the reported image of the target functional is the load-bearing claim). It does not put a learned model inside the engine. It does not author the researcher's nomological network for main results.

## 2. What the engine computes

Researcher supplies unit×measure scores (SCORE). Researcher authors a nomological network $R$ with thresholds $\theta$ and a target functional $\beta(\cdot)$ (RESTRICT). The engine:

1. Computes a sample slack $s_r(m)$ for every restriction $r$ and every measure $m$ (IDENTIFY).
2. Keeps the admissible set $M^* = \{m : s_r(m) \ge -\delta \ \forall r\}$, where $\delta \ge 0$ is a declared tolerance (default $0$).
3. Evaluates $\beta(m)$ for every measure, marks survivors, and reports the construct-identified range
   $$[L,U] = \left[\min_{m \in M^*} \beta(m),\ \max_{m \in M^*} \beta(m)\right]$$
   for nonempty $M^*$; empty otherwise.
4. Writes a JSON/HTML audit trail a non-coder can inspect (REPORT).

**Survivors only.** Rejected measures may appear diagnostically (which bars they failed, their $\beta$ values) but never enter the headline range.

**Score-agnostic and model-free.** The engine never generates measures, never searches prompt space, and contains no LLM client. Dictionary scores, LLM scores, PCA factors, human ratings — anything that lands as a scalar column per unit — is an admissible menu member. How columns are built is the researcher's upstream workflow, documented as a recipe next to the frozen inputs.

## 3. Restrictions registry

A restriction $r \in R$ is a stated testable implication of the construct definition, written as a sample moment inequality with threshold $\theta_r$. The registry is intentionally small: each evaluator is a transparent, auditable sample analogue of a first-order validity implication, and every one fails loud rather than silently returning garbage.

| Type | Slack (satisfied when $\ge -\delta$) | Typical use |
|---|---|---|
| `corr_min` | $\mathrm{Corr}(m, V) - \theta$ | Signed lower bound: measure must co-move with a criterion/auxiliary at least $\theta$ |
| `corr_sign` | $\mathrm{sign} \cdot \mathrm{Corr}(m, V) - \theta$ | Directed association with an auxiliary |
| `mean_order` | $\mathrm{sign}\cdot(\mathbb{E}[m\mid G{=}1] - \mathbb{E}[m\mid G{=}0]) - \theta$ | Monotone group ordering (binary 0/1 group) |
| `rank_agree` | $\mathrm{Spearman}(m, m_{\mathrm{ref}}) - \theta$ | Candidate orders units like a reference measure |
| `corr_zero` | $\theta - |\mathrm{Corr}(m, V)|$ | Two-sided discriminant: admit when the measure is (near-)uncorrelated with $V$ |
| `monotone_rank` | $\mathrm{sign}\cdot\mathrm{Spearman}(m, V_{\mathrm{cont}}) - \theta$ | Monotone-in-continuous-covariate: signed rank association with a continuous $V$ |
| `stability` | (schema-only; no evaluator yet) | Split-half agreement — fails loud until a fixture demands it |

Slack sign convention: $s_r(m) \ge 0$ means restriction $r$ is satisfied by measure $m$; negative slack is the violation magnitude.

### Why the registry is narrow (and why that is a feature)

- **Each evaluator is a claim about what validity means.** Adding an evaluator is adding a position on measurement theory, not adding a convenience function. A small registry keeps those positions explicit and auditable.
- **The target audience's economics is full of monotone structure.** Signed correlations (`corr_min`/`corr_sign`) capture "more of the construct ⇒ more of the correlate"; `mean_order` captures monotone group gaps; `rank_agree` captures ordinal agreement. Much of applied economic identification runs on exactly these.
- **More sophisticated tests — learned judges, ML-based slacks, kernel nuisances — live outside the engine.** They embed a fitted model inside the admissibility decision, which is precisely the epistemic move this package exists to make transparent. They are legitimate upstream scoring (a learned judge is just another way to fill a score column) or downstream robustness checks, but they do not belong in the validity layer while the engine is score-agnostic and model-free.
- **Known gaps (as shipped):** `stability` (split-half) is schema-only — no evaluator yet, fails loud until a fixture demands it. Learned/ML-based slacks are deliberately outside the engine (a fitted model inside the admissibility decision is the epistemic move this package exists to make transparent). A formal coverage theorem for the uncertainty band under arbitrary selection coupling is deferred — the band is an honest heuristic label, never a CI. *Monotone-in-continuous-covariate* is **no longer a gap**: v2.5.0 ships `monotone_rank` (signed Spearman against a continuous $V$; see the registry table above).

## 4. Target functionals

$\beta(\cdot)$ is the downstream economic number the researcher wants a range for. The registry ships:

| Type | Definition |
|---|---|
| `corr_y` | $\mathrm{Corr}(m, y)$ — association of the measure with the outcome |
| `ols_coef` | Standardized OLS coefficient on $m$ in a regression of $y$ on $m$ plus declared controls (numpy closed form; no statsmodels dependency) |
| `diff_means` | $\mathrm{sign}\cdot(\mathbb{E}[m\mid G{=}1] - \mathbb{E}[m\mid G{=}0])$ — group mean gap on a binary 0/1 group. **The contrast is on the measure itself: the declared $\beta$ outcome is ignored** |
| `map_distance` | $\|\bar z(m) - z_{\mathrm{target}}\|_2$, where $\bar z(m) = \frac{1}{n}\sum_i x_i(m)^\top L$ — 2-D Euclidean distance of the measure's mean projected item location from a target point; item columns resolve as `{measure}__{item_id}` |

More functionals can be added by extending the registry; the engine evaluates any declared, implemented functional over the menu.

**Separation of $R$ and $\beta$ (locked):** the network answers *what a valid measure of $C$ must do*; $\beta$ answers *what economic conclusion we track under alternative measures*. They are not hard-coded as derivatives of each other. The same $C$ can feed many $\beta$s; the same regression can use different $C$s. On the main paper path the researcher owns both.

## 5. Inference stance

Deliberately conservative. The headline range is the image of $\beta$ on survivors — no model, no shrinkage, no sharpening.

- **Bootstrap** (additive diagnostic): units-only resampling with replacement, menu fixed, one seeded RNG stream; pointwise percentile band over non-empty replicates. All-empty replicates are counted and reported. The headline $[L,U]$ is unchanged.
- **θ-grid** (additive diagnostic): recompute $M^*$ and $[L,U]$ on a declared grid of threshold scale multipliers $\lambda$; $\lambda=1.0$ is the headline; no $\lambda$ is auto-selected.
- **δ-grid** (additive diagnostic): recompute admission on a declared grid of absolute tolerances $\delta$.
- **θ-anchor audit** (additive): pre-data, literature-grounded anchors for every threshold, machine-checked for completeness. Anchors are documentation and provenance, excluded from the freeze preimage.
- **Uncertainty band** (additive diagnostic, v3): when bootstrap is on, per-side $\alpha/2$ quantiles over non-empty replicates (default $\alpha=0.10$), empty-replicate rate, boundary attribution $|\mathrm{margin}_m| \le \kappa\cdot\mathrm{SE}_m$ (default $\kappa=2$), and admission frequency $\hat p_m$. Honest label only — never a confidence interval or coverage guarantee. Selection uncertainty on the pooled sample; not a holdout-robustness band. Excluded from the freeze preimage ($\alpha$, $\kappa$ are diagnostic knobs).
- Diagnostics never replace the headline range and are excluded from the run-id preimage.

## 6. Empty sets and wide ranges are findings

| Outcome | Interpretation | Report tone |
|---|---|---|
| $M^* = \emptyset$ | Theory + data reject all candidate measures | Feature: "nothing admissible under this theory" |
| Large $U - L$ | Conclusion fragile to measurement choice | Feature: wide construct-identified range |
| Singleton + tight band | Point-identified under this network | OK; show which restrictions bind |

Never automatically loosen $\theta$ to "fix" emptiness. A wide range or an empty set is the honest answer.

## 7. When to use cvprofiles (and when not to)

| You want… | Tool |
|---|---|
| Which operationalizations are admissible under a stated theory, and what range of downstream estimates follows | **cvprofiles** |
| How much conclusions move across regression specs (Leamer extreme bounds) | Closest ancestor; cvprofiles moves the discipline to the measurement layer |
| Whether unobserved confounding kills $\beta$ for a *fixed* regressor (OVB) | OVB sensitivity packages (e.g. sensemakr) — orthogonal, downstream of measurement choice |
| Which inputs drive output variance (variance-based GSA) | Display cousin; different question |
| Causal identification of a structural effect | Not this package — cvprofiles disciplines measurement given a stated $\beta$, it does not design causal strategies |

## 8. Paper numbers discipline

Paper-facing numbers come only from: frozen score matrix (hash), pinned network + $\theta$ (hash), declared $\beta$ (hash), fixed seed, package version, and the documented freeze/run-id contract. Provenance fields travel with every report artifact.

## 9. Notation

| Symbol | Meaning |
|---|---|
| $C$ | Latent construct (researcher-defined, one paragraph of prose) |
| $M = \{m_j\}$ | Finite menu of candidate measures (score columns) |
| $V$ | Auxiliaries used in restrictions (not menu members, unless declared) |
| $R$, $\theta$ | Nomological network: restrictions with thresholds |
| $\delta$ | Slack tolerance (default 0) |
| $s_r(m)$ | Sample slack of restriction $r$ on measure $m$ |
| $M^*$ | Admissible set |
| $B^*$ | $\{\beta(m) : m \in M^*\}$ |
| $[L,U]$ | Reported construct-identified range |
| $y$ | Outcome used by $\beta$ |
