# Two-resolution application — results memo

**Date:** 2026-08-14
**Engine:** cvprofiles 3.0.1
**Seed:** 20260814 · **n_boot:** 1000 · **θ-grid:** λ ∈ {0.5, 1.0, 1.5, 2.0}
**Posture (locked before slacks):** restriction-stage split is headline; units-split not used.
**Claim promotion:** not executed. These are frozen-run facts, not a paper abstract.

Country WVS columns were rebuilt and matched the frozen patience / H5 tables at max |diff| ≤ 2.2×10⁻¹⁶, then **reused**. Cells are new: 480 sex×age cells, 42 countries, min cell n = 20.

---

## Headline table

| Profile | n | M* | [L, U] | Coverage band (α=0.10) | Empty-rep. rate |
|---|---:|---|---|---|---:|
| Patience country | 41 | {GPS patience} | [0.402, 0.402] | [0.079, 0.563] | 0.297 |
| Trust country | 35 | {Q57, in-group, out-group, composite} | [0.107, 0.391] | [−0.016, 0.639] | 0.002 |
| Patience cells | 480 | ∅ | undefined | undefined | 1.000 |
| Trust cells | 480 | {Q57, in-group, out-group} | [0.251, 0.317] | [0.170, 0.372] | 0.000 |

β country = standardized OLS of *m* on log GDP pc, education control.
β cells = Corr(*m*, GPS cell mean). GDP cannot be a within-country estimand.

---

## Patience

Country: only GPS patience clears education-correlation (slack +0.275) and the risk discriminant (slack +0.075). Q13, Q14, and the composite fail `conv_edu` hard (slacks −0.533 / −0.777 / −0.722) and have **negative** β on log GDP (−0.166 / −0.195 / −0.219). GPS β = +0.402, matching the 2026-08-10 pilot table.

On the **full** 41-country frame GPS **passes** leftover `mono_edu` (slack +0.233). The pilot fold-0 failure (slack −0.383) was a train-split artifact, not a full-sample fact. That is worth stating when the old freeze is demoted.

Cells: every WVS patience column fails `corr_min(q275_cell)` (Q13 −0.371, Q14 −0.725, composite −0.624) and leftover monotonicity. All 1,000 bootstrap replicates are empty. Cell β vs GPS patience is **negative** (Q13 −0.133, Q14 −0.247, composite −0.232).

**Interpretation allowed by the design.** The Q13/Q14 rejection is not merely ecological. Country aggregates of thrift/perseverance point against education and GDP; the same items, inside countries, still fail the education bar and fail to recover GPS patience. The pair (WVS child-qualities menu, this network) is rejected at both resolutions.

**Fragility.** The country singleton is selection-fragile: 29.7% of country bootstraps empty M*, and the coverage band [0.079, 0.563] is much wider than the plug-in point 0.402. θ-grid: λ=0.5 *empties* M* because the discriminant bar tightens (θ_disc=0.175) and GPS |r| with risk (~0.275) no longer clears it. Headline λ=1 is knife-edge on that discriminant.

---

## Trust

Country: GPS trust fails `corr_min(rule_of_law)` (slack −0.176) and leftover education. Institution trust fails the same rule-of-law bar (slack −0.425) and has **negative** β (−0.092). Survivors: Q57, in-group, out-group, composite. Plug-in range [0.107, 0.391] is the image of those four βs (composite 0.107 … Q57 0.391). Leftover education holdout: Q57 / in-group / out-group pass; composite fails (slack −0.052). Tool holdout pass rate = 0.75, vs random-k=1 mean 0.52 (tool percentile 0.48 — the leftover test is not a strong win over random at k=1).

Coverage band **crosses zero** [−0.016, 0.639]. Do not write “narrow positive trust–GDP range” from the plug-in interval alone.

Cells: Q57, in-group, and out-group survive education and leftover monotonicity; composite and institution fail `conv_edu_cell`. Survivors recover GPS trust inside countries: β ∈ [0.251, 0.317], coverage [0.170, 0.372], empty-replicate rate 0. Best in-sample |β| is the **rejected** composite (0.449) — predictive-selection and validity-selection disagree, which is the comparative claim working.

Q57 is **not** the country-level failure it was in the older P1 GPS-recovery screen. Here Q57 survives both resolutions under *external* bars (rule of law / gini / education), while GPS trust itself fails rule of law. That is the opposite of a “GPS is the criterion” posture, and it is what the peer menu was supposed to allow.

---

## Special-case recoveries (already computed)

**Empty R** on the seven-measure patience menu (cvprofiles 3.0.1):
M* = full menu, [L, U] = [−0.21875, 0.40246] = min/max β, paper rounding [−0.219, 0.402]. Composition claim (i) is now a computed result.

**Campbell–Fiske patience × trust** (n=41, τ_conv=0.30, τ_disc=0.35):
classical retain set = ∅; engine global M* = ∅; they match. Binding facts:

- GPS patience vs WVS child-qualities r = **−0.252** (convergent fails; Falk Table II 0.09 already warned)
- GPS trust vs Q57 r = **0.284** (just below 0.30; slack −0.016)
- Q57 vs GPS *patience* r = **0.825** (heterotrait–heteromethod fails the discriminant badly)

The psychometric bridge is **formally** recovered (the inequalities are Campbell–Fiske cells). Substantively the 2×2 rejects every instrument: WVS Q57 tracks GPS patience more than GPS trust at country level. That is a named special-case finding, not a reason to lower τ after the fact.

---

## What this is allowed to mean

1. Unrestricted item-multiverse for patience sign-switches ([−0.219, 0.402]); the validity screen leaves a singleton GPS point that is sampling-fragile.
2. WVS thrift/perseverance are not admissible representations of GPS-style patience at country *or* cell resolution.
3. Several WVS trust facets are admissible under external institutional/inequality/education bars and recover GPS trust *inside* countries; GPS trust itself is not admissible under the rule-of-law bar.
4. Empty cell-patience M* is a result, not a crash.

## Still not a paper rewrite

The kill-point was “hold `.tex` until cells exist.” Cells exist. The rewrite is now *unblocked*, not *done*. Augusto still owns claim promotion. I will not write the abstract until asked.

## Artifacts

- Design: `evals/wvs_gps_two_resolution/DESIGN.md`
- Scores + hashes: `evals/wvs_gps_two_resolution/data/score_manifest.json`
- Runs: `evals/wvs_gps_two_resolution/runs/{patience,trust}_{country,cells}/`
- Combined: `evals/wvs_gps_two_resolution/application_summary.json`
- Empty-R: `evals/composition_special_cases/empty_R_patience_recovery.json`
- MTMM: `evals/composition_special_cases/mtmm_patience_trust_recovery.json`
