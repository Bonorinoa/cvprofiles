# Two-resolution application — patience and trust

**Status:** FROZEN as design 2026-08-14, before any new slack inspection of these four networks. Amended 2026-08-14 18:03 MST (cell estimand only; θ unchanged).
**Engine:** cvprofiles 3.0.1.
**Authority:** Augusto locked constructs (patience + trust), country β (`ols_coef` on log GDP pc | education), and “literature-anchored if I do not author θ/β.” `.tex` rewrite remains held until the *within-country* cell profiles exist.

This is the paper’s confirmatory application. The 2026-08-10 \(K=5\) patience freeze is a **pilot / appendix**. LLM columns are not in the confirmatory menus.

## Constructs

> **Patience** is time preference: the disposition to value future relative to present outcomes, observable in delayed-reward choices. Operationalization follows the GPS intertemporal module (Falk et al. 2018). A valid measure should rise with human capital (education) and should not collapse into risk preference.

> **Trust** is the belief that other people have good intentions / that most people can be trusted. GPS trust is a single experimentally validated item; WVS Q57 is the canonical survey item; in-group, out-group, and institution facets are distinct objects of trust. A valid measure should co-move with institutional quality and move opposite income inequality (Algan–Cahuc / Aghion–Shleifer / Bjørnskov). GPS trust is a **peer candidate**, not a bar, whenever it sits in the menu.

## Units

| Profile | Unit | Frame |
|---|---|---|
| patience country | `iso3` | GPS ∩ WVS ∩ WDI, WVS floor ≥ 30 |
| trust country | `iso3` | same overlap, plus WGI rule of law and WDI gini |
| patience cells | `iso3\|sex\|age_band` | GPS individual and WVS individual aggregated separately, inner-joined; cell \(n\ge 20\); ≥ 6 cells/country |
| trust cells | same | same |

Age bands: 18–24, 25–34, 35–44, 45–54, 55–64, 65+. Sex: female = 1 following GPS (`gender==1`) and WVS Q260==2. Do **not** row-bind GPS and WVS respondents. Country-level auxiliaries that do not vary within country (GDP, gini, rule of law) are **not** used as cell restrictions.

## Menus

**Patience country (P2 peer).** `m_gps_patience`, `m_wvs_q13`, `m_wvs_q14`, `m_composite` \(=z(Q13)+z(Q14)\), `m_noise`. Frozen Llama/Phi columns may be joined later as appendix-only; they are not confirmatory.

**Trust country (P2 peer).** `m_gps_trust`, `m_trust_general` (Q57), `m_trust_in_group`, `m_trust_out_group`, `m_trust_institution`, `m_trust_composite` (mean of in/out/institution; **Q57 excluded**), `m_noise`.

**Patience cells (P1 recovery of GPS structure).** `m_wvs_q13`, `m_wvs_q14`, `m_composite`, `m_noise`. GPS patience cell mean is the **outcome** for \(\beta\), not a menu member (avoids \(\beta=1\) tautology).

**Trust cells (P1).** `m_trust_general`, `m_trust_in_group`, `m_trust_out_group`, `m_trust_institution`, `m_trust_composite`, `m_noise`. GPS trust cell mean is the outcome for \(\beta\).

## Networks (prose → types → θ)

### Patience country

| Implication | Type | Stage | θ | Anchor |
|---|---|---|---|---|
| Patience rises with education | `corr_min(q275_mean)` | select | 0.20 | Falk 2018: patience–years of schooling \(\rho=0.65\); individual education/cognitive gradient \(+\) in >90% of countries |
| Patience is not risk | `corr_zero(risktaking)` | select | 0.35 | Falk Table IV \(r=0.230\); Hanushek et al. 2022 \(r=0.358\); memo `patience_risk_theta_memo.md` |
| Rank-monotone in education | `monotone_rank(q275_mean, +)` | holdout | 0.15 | Same human-capital implication; leftover test (GPS failed this bar in the pilot — that remains a finding) |

\(\beta\): `ols_coef` of standardized \(m\) on `log_gdp_pc`, control `q275_mean`. Falk: patience is the robust GDP correlate; education is controlled so \(\beta\) is not the admission bar.

### Trust country

GPS trust is **in the menu**. Therefore **no** `corr_min(gps_trust)` restriction (circular for that column).

| Implication | Type | Stage | θ | Anchor |
|---|---|---|---|---|
| Trust co-moves with rule of law | `corr_min(rule_of_law)` | select | 0.30 | Aghion–Algan–Cahuc–Shleifer 2010 typical \(r\ge 0.4\); H5 historical floor 0.30 |
| Trust moves opposite inequality | `corr_sign(gini, −)` | select | 0.10 | Bjørnskov 2008; H5 historical |
| Trust rises with education | `corr_min(q275_mean)` | holdout | 0.20 | Falk Table 5: trust \(+\) cognitive skills in almost all countries; leftover implication |

\(\beta\): same `ols_coef` on `log_gdp_pc` | `q275_mean` (Augusto lock). GDP is not in \(\mathcal R\). Falk’s result that trust loses significance once patience is in a joint GDP regression is a **claim about \(\beta\)**, not a reason to drop the trust–development estimand.

### Patience cells

Within-country human-capital test. No country-constant aux. **Amendment 2026-08-14 18:03 MST:** every column that enters \(\mathcal R\) or \(\beta\) on a cell profile is **country-demeaned** before SCORE (iso3 = first `|` field of `unit_id`). Pooled (undemeaned) cell runs remain on disk as a contrast only; they are not the confirmatory cell estimand. \(\theta\) is unchanged. The amendment was written after a diagnostic pooled-vs-demeaned correlation check, not after a new slack inspection of a moved network.

| Implication | Type | Stage | θ | Anchor |
|---|---|---|---|---|
| More-educated cells more patient | `corr_min(q275_cell)` | select | 0.20 | Same education implication, now within country |
| Rank-monotone in education | `monotone_rank(q275_cell, +)` | holdout | 0.15 | Leftover |

\(\beta\): `corr_y` with `gps_patience_cell`. This is the ecological-control estimand: do surviving WVS items recover GPS patience **inside** countries? GDP cannot be \(\beta\) (constant within country).

### Trust cells

| Implication | Type | Stage | θ | Anchor |
|---|---|---|---|---|
| More-educated cells more trusting | `corr_min(q275_cell)` | select | 0.20 | Falk Table 5 cognitive \(+\) on trust, almost all countries |
| Rank-monotone in education | `monotone_rank(q275_cell, +)` | holdout | 0.15 | Leftover |

\(\beta\): `corr_y` with `gps_trust_cell`. Gender is **not** a gate (Falk & Hermle: women more trusting in only ~2/3 of countries).

## Holdout posture (locked before slacks)

Restriction-stage split is the **headline**. Country \(K\)-fold / units-split is diagnostic only and will be labeled power-limited at \(n\approx 40\). Do not amend this after seeing slacks.

## Baselines (all four profiles)

1. Random subset, 500 draws, sizes 1–3.
2. Single canonical item: Q13 (patience), Q57 (trust).
3. Best in-sample predictor of \(\beta\).

Comparative claim: construct-guided selection has lower holdout-stage loss than each baseline.

## Diagnostics

`--n-boot 1000 --alpha 0.10 --kappa 2` on every confirmatory run. \(\theta\)-grid \(\lambda\in\{0.5,1.0,1.5,2.0\}\). Empty \(M^*\) and wide bands are results.

## Score reuse rule

Rebuild country WVS means from `WVS_wave7.dta` with the same recipes (mask \(-1\ldots-5\), no imputation). Compare to frozen `evals/wvs_gps_preferences/data/inputs/scores.csv` (patience items) and `evals/h5_trust/data/scores.csv` (trust facets). If max \(|\mathrm{diff}|\) on overlapping cells is \(\sim 10^{-12}\), **reuse** those columns. If not, the rebuild is canonical and the comparison is recorded.

## Claim boundaries

Allowed: \(M^*\) and \([L,U]\) under the stated network at each resolution; Q13/Q14 failing country and/or cells; Q57 vs composite disagreement; empty sets.

Forbidden: “culture”; promoting the 2026-08-10 posture-(a) freeze as confirmatory; moving \(\theta\) after slacks; treating GPS failing monotonicity as a software error; cell-level GDP claims; citing the 2026-08-14 *pooled* cell \(M^*\) as the within-country conclusion.

## Amendment 2026-08-14 18:03 MST — cell country-demeaning

The 2026-08-14 cell networks were authored as a within-country test. The first engine run applied `corr_min` / `monotone_rank` / `corr_y` to the **pooled** 480-row table, so between-country level differences remained in every slack. That is not the estimand the design claimed.

**Change (estimand only).** For `patience_cells` and `trust_cells`, subtract the country mean from every numeric column that enters \(\mathcal R\) or \(\beta\): the menu measures (including `m_noise` and `m_composite` as already-built columns), `q275_cell`, and the GPS cell outcome. Country tables are not remade. \(\theta\), stages, seed `20260814`, \(n_{\mathrm{boot}}=1000\), and \(\lambda\)-grid are unchanged.

**Not changed.** Country-profile networks, menus, \(\beta\), or any threshold. No new construct. No LLM columns.

**Labeling.** `runs/patience_cells` and `runs/trust_cells` = pooled contrast. `runs/patience_cells_demeaned` and `runs/trust_cells_demeaned` = confirmatory cell profiles.
