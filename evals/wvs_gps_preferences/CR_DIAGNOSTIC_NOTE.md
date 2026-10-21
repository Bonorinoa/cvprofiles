# Conservative CR on the WVS/GPS flagship: diagnostic note (2026-10-21)

**Status: DIAGNOSTIC ONLY. This is not paper evidence and not a run-gate decision.** The 2026-10-20 CR entries in `logs/DECISIONS.md` leave "running the CR on the WVS/GPS frozen inputs" to Augusto. This note records what the unreleased CR layer (commit `8a5f3a9`) says about the frozen country frame, so that he can decide whether and how to use it. Nothing was written under `reports/summaries/`, no allow-list changed, `paper/` and the frozen inputs are untouched, and the version stays 3.0.2.

- Script: `evals/wvs_gps_preferences/cr_diagnostic.py`. Run it with `uv run python evals/wvs_gps_preferences/cr_diagnostic.py`; it takes about 6 s.
- Outputs go to `reports/runs/wvs_gps_cr_diagnostic/`, which is git-ignored and regenerable. They are a reference `ols_coef` run, two `beta_estimates_*.csv` files, four CR runs and `cr_diagnostic_summary.json`.

## Route

The flagship β is `ols_coef`: the standardized coefficient on z(m) in z(log_gdp_pc) ~ 1 + z(q275_mean) + z(m). The CR layer has no native interval for that β type (D8), so β and its SE are computed upstream in the script and passed to the engine as β type `external`. The engine fits nothing.

1. **β.** The script uses the same numpy closed form as `identify/beta_fn.py::_ols_coef`. It agrees with a fresh v3.0.2 engine run to **0.0**, and with the frozen `data/runs_stage4/beta_values.json` to **5.6e-17** (tolerance 1e-12).
2. **SE, two choices:**
   - `hc1`: an HC1 sandwich on the z-scored regression, with `df = n − k = 38` (the Stata `vce(robust)` convention). It treats the z-scoring as fixed.
   - `boot`: a pairs bootstrap over countries. Each draw re-standardizes before refitting. B = 9999, seed 20260810, 0 degenerate draws. It uses normal critical values.
3. **Engine runs.** `run_profile` on the frozen `data/inputs/{scores.csv, roles.json, network.yaml}` with β `external`, `--confidence-region`, robust slack SE, and α1 = α2 = 0.05 (nominal ≥ 0.90). Both variants were run, endpoint and simultaneous. The runs use the full 41-country frame with no `holdout_units`, because the CR refuses a units-split (D7).

## Plug-in headline (unchanged)

All four runs give `M*_select = [m_gps_patience, m_prompt_a]` and `[L, U] = [0.3275, 0.4025]`. That is bit-identical to the reference `ols_coef` run, and it matches the frozen headline `[0.328, 0.402]`. On this frame the full-frame select-stage M* coincides with the posture-(a) "selected in all 5 folds" set.

## CR results

| SE | Variant | CR_L | CR_U | Width | M⁺ | M⁻ |
|---|---|---|---|---|---|---|
| hc1 | endpoint (default) | **−0.285** | **0.586** | 0.872 | gps, prompt_a, prompt_b, noise | ∅ |
| boot | endpoint (default) | **−0.270** | **0.615** | 0.885 | same | ∅ |
| hc1 | simultaneous | −0.409 | 0.661 | 1.070 | same | ∅ |
| boot | simultaneous | −0.378 | 0.694 | 1.072 | same | ∅ |

For comparison, the plug-in width is 0.075.

Bonferroni levels: endpoint `K_out = 4`, `a_out = 0.0125`, β per side 0.025; simultaneous `K_out = 14`, `a_out = 0.00357`, β per side 0.00357. In both, `K_in = 7` and `a_in = 0.00714`.

**Per-measure status.** The status is the same in all four runs.

| Measure | Status | Plug-in | conv_edu slack (ŝ, UCB endpoint) |
|---|---|---|---|
| m_gps_patience | possibly admissible | in M* | 0.275, 0.503 |
| m_prompt_a | possibly admissible | in M* | 0.185, 0.407 |
| m_prompt_b | possibly admissible | rejected (knife-edge) | −0.012, 0.248 |
| m_noise | possibly admissible | rejected | −0.266, **0.069** |
| m_wvs_q13 | certainly rejected | rejected | −0.533, −0.236 |
| m_wvs_q14 | certainly rejected | rejected | −0.777, −0.522 |
| m_composite | certainly rejected | rejected | −0.722, −0.456 |

**β (standardized OLS) and SEs.**

| Measure | β̂ | HC1 SE | Bootstrap SE | Ratio (boot / HC1) |
|---|---|---|---|---|
| m_gps_patience | 0.4025 | 0.0908 | 0.1083 | 1.19 |
| m_prompt_a | 0.3275 | 0.1036 | 0.1087 | 1.05 |
| m_prompt_b | 0.3739 | 0.0920 | 0.0982 | 1.07 |
| m_noise | 0.0199 | 0.1509 | 0.1478 | 0.98 |
| m_wvs_q13 | −0.1660 | 0.1622 | 0.1567 | 0.97 |
| m_wvs_q14 | −0.1948 | 0.1530 | 0.1540 | 1.01 |
| m_composite | −0.2187 | 0.1739 | 0.1685 | 0.97 |

## How to read it

- **What sets the ends.** In every run, CR_U is the upper β bound of `m_gps_patience` and CR_L is the lower β bound of **`m_noise`**. The negative control is plug-in rejected, but at n = 41 its conv_edu upper bound (endpoint, 0.069) does not fall below 0. The CR therefore cannot certify that rejection, and the noise measure's β interval sets the lower end.
- **A counterfactual, not a CR.** The lowest β bound among the other members of M⁺ is `m_prompt_a`'s: 0.118 (hc1, endpoint) or 0.114 (boot, endpoint).
- **disc_risk is non-binding for M⁺.** For every measure the two-sided interval for ρ(m, risktaking) covers 0, so the `corr_zero` UCB equals θ = 0.35. M⁺ is therefore set by conv_edu alone. It would be the same for any θ > 0, which means the CR does not depend on the 2026-08-10 θ re-anchoring (0.30 → 0.35).
- **M⁻ = ∅.** No measure is certainly admissible. Every measure has LCB < 0 on both select restrictions (for example `m_gps_patience` has conv_edu LCB −0.072). This is what the spec §12 Monte Carlo predicts at n = 41.
- **The SE choice matters little.** The bootstrap SE is 19% larger than HC1 for gps, because HC1 ignores the estimation of the z-scoring. It moves CR_U from 0.586 to 0.615. The HC1 file's t₃₈ critical value (2.024 vs 1.960) is a minor effect.
- **Bottom line.** At n = 41 the CR is informative about which measures are certainly out: the WVS Q13, Q14 and composite measures are certainly rejected. It says little about the range, though: it is about 12× the plug-in width and spans 0.

## Freeze and run_id

| Run | run_id | beta_hash |
|---|---|---|
| Frozen `runs_stage4` | `5a7a6e58…` | `40040c21…` |
| Reference `ols_coef`, v3.0.2, full frame | `405803ca…` | `40040c21…` |
| External β, hc1 | `7ca7d48f…` | `9d7d7e90…` |
| External β, boot | `ca4af7c6…` | `db3ba669…` |

The frozen run also differs from the reference run in three other ways:
- package version 3.0.0 vs 3.0.2;
- the frozen run has `config.holdout_units`;
- scores_hash `e3955779…` vs `92b0b1c5…`.

The frozen hash is that of the 3.0.0-parsed `S_frozen.csv`. It is reproduced exactly when v3.0.2 hashes that file. `data/inputs/scores.csv` under the v3.0.2 round-trip parser differs from it by at most 1 ulp in a few cells.

Against the like-for-like reference run, only `beta_hash` changes. That is by design: the `external` estimates hash folds into `beta_hash` (D5a). Within each SE choice, the endpoint and simultaneous runs share a run_id, because CR knobs are excluded from the preimage. The `network_hash` (`d1003f68…`) is identical everywhere.

## Caveats (read before citing anything)

- **i.i.d. countries (A1).** The 41 countries are the GPS ∩ WVS ∩ WDI overlap, not a random sample. Treating them as i.i.d. draws from a superpopulation is a modelling fiction. Spatial and cultural dependence between countries is ignored.
- **A3 is the script's claim.** The β intervals are only as valid as the HC1 or bootstrap SE at n = 41 with 3 regressors. The engine records the SE but cannot check it.
- **Estimand.** The CR covers the full-frame select-stage population range. It does not cover the K-fold "selected in all folds" object or M*_robust. Holdout-stage `mono_edu` never votes.
- **Width is expected.** The spec's Monte Carlo predicts a wide CR and an always-empty M⁻ at n = 41, and that is what happened.
- **Do not run this on the cell-level frames.** In `evals/wvs_gps_two_resolution/`, n = 480 cells are nested in countries, which violates i.i.d. units. The engine's slack bounds would be invalid there. A cluster-robust slack layer would need its own dated decision (spec §9).
- **Not paper evidence.** Using any of this in the paper (l.97, l.1144, App. A.5) needs Augusto's run decision. That decision covers frozen inputs, pinned network and β, the SE choice, seed, package version and audit.
