# 03 — Methodology

**Status:** scaffold v0 (2026-08-01)  
**Markers:** LOCKED = spine from profile SOUL / thesis; DRAFT = implementable default awaiting Augusto; USER OWNS = not agent-authored for main results.

## Framework (LOCKED)

Measurement is a disciplined projection of high-dimensional reality, not passive observation (Dell–Rambachan frame).

Construct validity for latent concept \(C\) under cheap multi-measure AI is cast as **partial identification over a menu of measurement functions**, not as:

| Tradition | Question | Relation to us |
|---|---|---|
| Variance GSA (Helton et al.) | Which inputs drive output variance? | Display cousin only |
| OVB (Cinelli–Hazlett) | Could unobserved confounding kill \(\beta\) on a **fixed** \(X\)? | Orthogonal; downstream of measurement choice |
| Leamer / extreme bounds | How much do conclusions move across specs? | **Closest ancestor** |
| Partial identification | What is learned under weak assumptions? | **Formal home** for \(M^*\) and \(B^*\) |

Primary question:

> Which operationalizations are admissible under a stated nomological network, and what set of downstream estimates follows?

## Statement of methodology (v2.0 — B4, LOCKED 2026-08-06)

**Statement.** cvprofiles treats construct validity as **partial identification over a finite menu of measurement functions**. The researcher supplies unit×measure scores and a nomological network R with thresholds θ; the engine computes sample slacks s_r(m), retains the admissible set M*, and reports the construct-identified range [L,U] = [min β(M*), max β(M*)] for a researcher-chosen target functional β. Empty M* and wide ranges are findings under the stated theory, not failures. Bootstrap, θ-grid, and δ-grid are additive diagnostics that never replace the headline range.

**Positioning.** The closest methodological ancestor is Leamer-style specification uncertainty, moved from regression specifications to measurement functions and disciplined by a stated nomological network rather than a kitchen-sink search. The engine is score-agnostic and model-free: it does not generate measures, does not search prompt space, and contains no learned model. Sharp new partial-identification theory is optional garnish; transparent slacks plus the reported image of β is the load-bearing claim.

**Inference stance.** Deliberately conservative. The bootstrap band is over units (menu fixed), conditional on admission, and additive; empty and degenerate replicates are counted and reported. Threshold sensitivity (θ-grid) and tolerance sensitivity (δ-grid) are diagnostic viewports, excluded from the freeze preimage.

## Compact formalization (LOCKED — single source of truth)

\[
\begin{align*}
M &= \{m_j\}_{j=1}^{J} \\
r \in R &: \quad \mathbb{E}[g_r(m(X), V; \theta_r)] \ge 0 \\
s_r(m_j) &= \text{sample analogue of left-hand side (slack)} \\
M^* &= \{ m \in M : s_r(m) \ge 0\ \forall r \in R \} \\
B^* &= \{ \beta(m) : m \in M^* \} \\
[L,U] &= \text{reported range for } B^* \text{ with honest conservative inference}
\end{align*}
\]

Sharp new PI theory is **optional garnish**, not the load-bearing claim. Finite menu + transparent slacks + reported image of \(\beta\) is enough for the tool MVP.

## Separation: network vs \(\beta\) (LOCKED)

| Object | Answers | Owner |
|---|---|---|
| Nomological network \(R,\theta\) | What must a valid measure of construct \(C\) do? | **USER OWNS** (main path) |
| Target \(\beta(\cdot)\) | What economic conclusion do we track under alternative measures? | USER OWNS choice; engine owns evaluation |

Same \(C\) can feed many \(\beta\)s. Same regression can use different \(C\)s. **Do not hard-code \(R\) as a derivative of \(\beta\)** in software. Pair them only for demos.

Strict paper path: agent may **suggest** example networks when asked; agent must **never silently author** the network used in main results.

## Menu \(M\) (LOCKED policy)

- Finite, researcher-supplied.  
- Each \(m_j\) is already a **score column** at SCORE time (dictionary, LLM prompt variant, PCA factor, human rater, …).  
- Engine does not search prompt space.  
- Keep \(J\) small in synthetic work (\(\sim 8\)–\(12\)); controllability > realism.

## Restrictions and slacks (DRAFT catalog)

MVP restriction types (implement as a small registry, not an open expression language):

| Type id | Meaning (sketch) | Typical \(g_r\) |
|---|---|---|
| `corr_sign` | \(\mathrm{Corr}(m, V_k)\) has stated sign | \(\mathrm{sign}\cdot\mathrm{Corr} - \theta\) |
| `corr_min` | Corr(m, V_k) ≥ θ — signed lower bound (NOT absolute; corrected 2026-08-06, docs/12) | Corr − θ |
| `mean_order` | \(\mathbb{E}[m \mid G=1] \ge \mathbb{E}[m \mid G=0] + \theta\) | group mean gap \(-\theta\) |
| `rank_agree` | Spearman\((m, m_{\mathrm{ref}}) \ge \theta\) | Spearman \(-\theta\) |
| `stability` | Agreement across split halves \(\ge \theta\) | agreement \(-\theta\) |

**Slack sign convention (LOCKED):** \(s_r(m) \ge 0\) means restriction \(r\) is satisfied by measure \(m\). Negative slack = violation magnitude.

**Tolerance (DRAFT):** admit if \(s_r(m) \ge -\delta\) with \(\delta \ge 0\) default `0` for exact; document any \(\delta > 0\) in manifest. Prefer explicit \(\delta\) over hidden float fuzz.

Sample analogues: simple means/correlations first. No kernel / ML nuisances in MVP.

## Target \(\beta(\cdot)\) (DRAFT defaults)

Registry of named functionals:

| id | Definition (MVP) |
|---|---|
| `corr_y` | \(\mathrm{Corr}(m, y)\) |
| `ols_coef` | Coefficient on \(m\) in OLS of \(y\) on \(m\) + optional controls |
| `diff_means` | \(\mathbb{E}[y \mid m \ge c] - \mathbb{E}[y \mid m < c]\) (threshold declared) |

First synthetic demos use `corr_y` or `ols_coef` with no controls — boring on purpose.

## Identification mapping (LOCKED)

1. Compute full slack matrix \(s_r(m_j)\).  
2. \(M^* = \{m : s_r(m) \ge 0\ \forall r\}\) (with \(\delta\) policy).  
3. Evaluate \(\beta(m)\) for all \(m \in M\) (report non-survivors too, marked).  
4. \(B^* = \{\beta(m): m \in M^*\}\).  
5. Point range: \(L = \min B^*\), \(U = \max B^*\) when \(M^* \ne \emptyset\); else empty.  
6. Inference: bootstrap **over units** (not over measures — menu is fixed). DRAFT: percentile interval on \((L,U)\) endpoints and/or on \(\beta(m)\) for survivors; conservative reporting preferred over flashy sharp bounds.  
7. \(\theta\)-grid: recompute \(M^*,[L,U]\) on a declared grid; emit sensitivity surface.

## Empty sets and wide ranges (LOCKED aesthetics)

| Outcome | Interpretation | Report tone |
|---|---|---|
| \(M^*=\emptyset\) | Theory + data reject all candidate measures | Feature: “we don’t know / nothing admissible” |
| Large \(U-L\) | Conclusion fragile to measurement | Feature: wide construct-identified range |
| Singleton + tight bootstrap | Point-ID under this network | OK, still show which restrictions bind |

Never auto-relax \(\theta\) to “fix” emptiness in the default path.

## Synthetic oracle metrics vs reported range (LOCKED 2026-08-01)

Reported scientific object is always the **image** of \(\beta\) on \(M^*\):

\[
[L,U] = \bigl[\min B^*,\, \max B^*\bigr] \quad (M^*\ne\emptyset),\qquad
\text{empty otherwise.}
\]

Do **not** widen \([L,U]\) or loosen \(\theta\) to chase a latent target.

Under \(\beta=\mathrm{corr}_y\), classical attenuation implies noisy admissible \(m\) satisfy \(\mathrm{Corr}(m,y) < \mathrm{Corr}(V^*,y)\) in standard DGPs. Therefore **coverage of latent** \(\beta^{\mathrm{lat}}=\mathrm{Corr}(V^*,y)\) is **not** an engine pass/fail gate.

| Metric | Definition | Role |
|---|---|---|
| **H1a** (gate) | False-admission of `invalid_*` / `wrong_construct`; plus diagnostics on valid retention | Engine correctness under oracle \(R\) |
| **H1b** (gate, synthetic) | \(\beta(m_{\mathrm{anchor}})\in[L,U]\) when \(M^*\ne\emptyset\), where \(m_{\mathrm{anchor}}\) is a designated **feasible** clean measure expected in \(M^*\) (default: `m_dict`) | Range covers the best feasible operationalization’s \(\beta\) |
| **H1_latent** (diagnostic only) | \(\beta^{\mathrm{lat}}\in[L,U]\) | Documents attenuation gap; not a CI gate |
| H2 | False-admission rate (see prereg) | Gate |
| H3 | Empty-set honesty under harsh / all-invalid | Gate |
| H4 | Cold reproducibility of \((M^*,L,U,\mathrm{slacks})\) | Gate |

Near-miss measures are **not** false admissions unless labeled `invalid_*` / `wrong_construct`. Under a well-calibrated oracle \(R\), near-misses should typically fail ≥1 restriction (design intent, not a silent post-hoc label flip).

## What we are not doing (methodology)

- Treating one preferred \(m\) as the regressor and only running OVB on it.  
- Variance decomposition across prompts as the main validity claim.  
- Claiming set identification of structural causal effects solely from measurement menus.  
- Continuous optimization over infinite function classes in MVP.

## Paper numbers discipline (LOCKED)

Paper / thesis numbers come only from:

1. Frozen score matrix (hash),  
2. Pinned network + \(\theta\) (hash),  
3. Fixed seed + package version.

Anything else is exploratory.
