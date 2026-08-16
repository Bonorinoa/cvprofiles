# Cell estimand correction — pooled vs country-demeaned

**Amendment:** 2026-08-14 18:03 MST (`DESIGN.md`). Estimand only. \(\theta\) unchanged.
**Engine:** cvprofiles 3.0.1 · seed `20260814` · \(n_{\mathrm{boot}}=1000\)
**Confirmatory cell runs:** `runs/patience_cells_demeaned`, `runs/trust_cells_demeaned`
**Pooled contrast (not confirmatory):** `runs/patience_cells`, `runs/trust_cells`

Country profiles were not rerun.

---

## Side-by-side

| | Patience cells | Trust cells |
|---|---|---|
| **Pooled \(M^*\)** | \(\emptyset\) | {Q57, in-group, out-group} |
| **Pooled \([L,U]\)** | undefined | [0.251, 0.317] |
| **Demeaned \(M^*\)** | {Q13} | \(\emptyset\) |
| **Demeaned \([L,U]\)** | 0.245 | undefined |
| **Demeaned coverage** | [0.174, 0.335] | undefined |
| **Demeaned empty-rep.** | 0.17 | 1.00 |

\(\beta\) on cells = Corr(\(m\), GPS cell mean), now on country-demeaned columns.

---

## Patience — item-level, not ecological

Q13 was rejected in the pooled table because richer countries have both more education and *lower* thrift endorsement. Inside countries the sign flips.

| measure | pooled slack `conv_edu` | demeaned slack | demeaned \(\beta\) vs GPS |
|---|---:|---:|---:|
| Q13 | −0.371 | **+0.051** | **+0.245** |
| Q14 | −0.725 | −0.564 | −0.326 |
| composite | −0.624 | −0.250 | −0.027 |

Q13 clears both the education bar and leftover monotonicity (slack +0.060) and recovers GPS patience at 0.245. Q14 stays anti-aligned after demeaning. The composite is Q13+Q14 and is pulled under the bar by Q14.

Knife-edges to report, not hide: Q13’s education slack is only +0.051 (sample \(r \approx 0.251\)). \(\lambda=1.5\) (\(\theta=0.30\)) empties \(M^*\). 17% of bootstraps are empty. This is a singleton, not a robust menu.

**Allowed sentence.** At the within-country resolution the design claimed, thrift (Q13) is an admissible weak representation of GPS patience; perseverance (Q14) is not. The country-level rejection of the WVS patience *menu* remains (Q13 still fails `corr_min(q275_mean)` across countries). Resolution disagreement is the result.

---

## Trust — education bar and GPS recovery come apart

Every trust facet fails `corr_min(q275_cell)` after demeaning, including at \(\lambda=0.5\) (\(\theta=0.10\)). The empty set is not a close call.

| measure | pooled slack | demeaned slack | demeaned \(\beta\) vs GPS |
|---|---:|---:|---:|
| Q57 | +0.246 | −0.177 | +0.052 |
| in-group | +0.043 | −0.268 | +0.224 |
| out-group | +0.205 | −0.275 | +0.211 |
| institution | −0.508 | −0.627 | +0.285 |
| composite | −0.119 | −0.474 | **+0.318** |

Q57’s pooled cell survival was between-country (demeaned vs GPS +0.05). In-group, out-group, institution, and the composite still recover GPS trust inside countries (0.21–0.32) **without** tracking within-country education. The stated admission bar and the GPS-recovery estimand disagree. That is what the method is for. Do not lower \(\theta\) to manufacture a nonempty \(M^*\).

**Allowed sentence.** Under the predeclared education restriction, no WVS trust measure is admissible at the within-country cell resolution. Several multi-item facets nonetheless co-move with GPS trust after country demeaning; Q57 does not. Country-level external bars (rule of law, gini) still admit Q57 / in-group / out-group / composite.

---

## What is now frozen for any later rewrite

1. Empty-\(\mathcal R\) patience span \([-0.219, 0.402]\).
2. MTMM 2×2 empty (Q57 tracks GPS patience, not GPS trust, at country level).
3. Country patience: singleton GPS, plug-in 0.402, coverage [0.079, 0.563], 30% empty bootstraps.
4. Country trust: {Q57, in, out, composite}, [0.107, 0.391], coverage crosses 0.
5. **Confirmatory cells = demeaned.** Patience {Q13} at 0.245. Trust \(\emptyset\).
6. Pooled cell \(M^*\) is a contrast that mislabels a between-country correlation as within-country.

No \(\theta\) was moved. No `.tex` was edited.
