# 04 — Synthetic DGPs

**Status:** scaffold v0 (2026-08-01) — plan LOCKED in spirit; numeric knobs DRAFT
**Purpose:** learn what the engine captures **before** real baselines. Controllability > realism.

## Why synthetic first

Real text scores entangle construct error, prompt artifacts, and outcome confounding. A calibrated DGP with known latent $V^*$, known true $\beta^*$, and labeled valid/invalid $m_j$ is the only honest way to measure:

| Metric | Definition | Direction of good |
|---|---|---|
| **Coverage** | Fraction of runs where true $\beta^* \in [L,U]$ (when $M^*\ne\emptyset$ and $\beta^*$ is identified under oracle $M$) | High (calibrated, not 1.0-by-cheat) |
| **False-admission rate** | Fraction of *invalid* measures that enter $M^*$ | Low |
| **Empty-set rate** | Fraction of runs with $M^*=\emptyset$ | Context-dependent (high under intentionally harsh $R$; low under oracle-compatible $R$) |
| **Point-ID rate** | Fraction of runs with $|M^*|=1$ (or $U-L \le \varepsilon_\beta$) | Diagnostic, not always “good” |

These four are the **debug metrics**. They are not the paper’s only claims; they are how we know the system works.

## Design principles

1. **Known oracle labels** for every $m_j$: `valid` | `near_miss` | `invalid_confounded` | `invalid_noise` | `wrong_construct`.
2. **Small $J$** — default $J=10$ (range 8–12).
3. **Researcher network is part of the experiment** — DGP ships with a *recommended* oracle-compatible $R$, but evals may stress wrong/harsh/loose networks deliberately.
4. **Bootstrap over units only**; menu fixed.
5. **$\delta$ policy is part of the eval** — default $\delta=0$; always report a small $\delta$-grid sensitivity for false-admission.

## Default dimensions (DRAFT knobs)

| Knob | Default | Notes |
|---|---|---|
| $n$ units | 2000 | Also run 200 / 500 for finite-sample stress |
| $J$ measures | 10 | Fixed menu |
| Latent $V^*$ | scalar Gaussian or 2-factor | Start scalar |
| Outcome | $y = \beta^* V^* + \gamma W + \varepsilon$ | $W$ = confounder available to bad measures |
| Seeds | fixed list in harness | Paper-path seeds pinned in run manifest |
| Slack tolerance $\delta$ | 0 | Grid: `{0, 1e-6, 1e-4, 1e-2}` on correlations scale |
| $\beta$ target | `corr_y` first; `ols_coef` second | Same DGP family |

## Measure archetypes (menu slots)

Ship a standard cast. Not every DGP uses all slots; labels are mandatory.

| id | Archetype | Oracle label | Construction sketch |
|---|---|---|---|
| `m_dict` | Valid dictionary-style | valid | Monotone transform of $V^*$ + light noise |
| `m_llm_good` | Valid “LLM-style” | valid | $V^*$ + different noise; high corr with $V^*$ |
| `m_para` | Paraphrase / near-duplicate | valid or near_miss | High corr with `m_llm_good`; tests redundancy not validity |
| `m_slop` | AI-slop / confounded | invalid_confounded | Loads on $W$ (or $y$-leak), weak on $V^*$ |
| `m_noise` | Pure noise | invalid_noise | Independent of $V^*,W,y$ |
| `m_wrong` | Wrong construct | wrong_construct | Loads on $U \perp V^*$ that still correlates with some aux |
| `m_near` | Near-miss | near_miss | Mostly $V^*$ but fails one stated restriction by design |
| `m_aux_only` | Aux-correlated only | invalid_confounded | Tracks auxiliary $V_k$ used in $R$ without tracking $C$ |
| `m_heavy_tail` | Valid but messy | valid | $V^*$ + heavy-tail noise (robustness of corr slacks) |
| `m_floor` | Compressed / censored | near_miss or valid | Nonlinear squash of $V^*$ |

Exact generative equations live in `evals/synthetic/` when implemented; this doc owns **intent and labels**.

## DGP scenarios (eval suite)

Each scenario is a named fixture family under `data/synthetic/` + harness entry under `evals/synthetic/`.

| Scenario id | Intent | Expected qualitative behavior |
|---|---|---|
| `oracle_easy` | Compatible $R$, clear valids | High coverage; low false-admission; low empty-set; $M^*$ ≈ valids |
| `oracle_with_slop` | Same + strong confounded measures | Slop excluded; range not polluted by $\beta(m_{\mathrm{slop}})$ |
| `harsh_theta` | $\theta$ too strict | Empty-set rate ↑; report must explain binding $r$ |
| `loose_theta` | $\theta$ too weak | False-admission ↑; wide or wrong $[L,U]$ risk |
| `wrong_network` | $R$ targets wrong implications | Empty or misleading $M^*$; teaches humility, not “fix” |
| `n_small` | $n=200$ | Bootstrap width ↑; coverage still calibrated if inference honest |
| `point_id` | Single valid passes | Point-ID rate high; still emit diagnostics |
| `all_invalid` | No measure tracks $V^*$ | Empty $M^*$ is success |

## Network used in synthetic evals

- **Oracle-compatible $R$** is part of the DGP package for debugging (agent-authored OK here — this is not the paper’s empirical network).
- **Paper path** still forbids silent authorship on real constructs.
- Log which network hash was used in every eval row (`13_Evaluations_Log.md`).

Draft oracle restrictions (illustrative, not sacred):

1. `corr_min` with a clean auxiliary correlated with $V^*$
2. `corr_sign` vs a known signed correlate
3. Optional `rank_agree` with `m_dict` as soft ref (careful: can bake in dictionary privilege — flag in decision log if used in main synthetic claim)

## Harness outputs

Each eval run writes under `reports/runs/<run_id>/` plus a one-line summary appended to the evaluations log:

- four debug metrics
- $|M^*|$, member ids, false members
- $[L,U]$, $\beta^*$, coverage bit
- $\theta$, $\delta$, $n$, seed, package version

## Explicit non-goals for synthetic layer

- Photorealistic LLM token simulation
- Training a scorer
- Claiming external validity to any real domain from DGP alone

## Fixture placeholder (day-0)

Minimal hand fixture (for schema tests before full DGP code):

- path (planned): `data/fixtures/mini_3x200.csv`
- 200 units, 3 measures (`valid`, `slop`, `noise`), outcome $y$, aux $v_aux$
- Not generated until first implementation milestone; path reserved.

## Open knobs (see also `10_Open_Questions.md`)

- Exact $\beta^*$ default and noise scales
- Whether paraphrase counts as valid or near_miss under redundancy-sensitive networks
- Primary headline metric for CI gate (proposal: false-admission ≤ bound on `oracle_with_slop` + coverage ≥ bound on `oracle_easy`)
