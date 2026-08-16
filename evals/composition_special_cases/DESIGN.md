# Composition special cases (empty R + Campbell–Fiske MTMM)

**Status:** authored 2026-08-14, before any slack inspection of the MTMM network.
**Engine:** cvprofiles 3.0.1 (PyPI + local `main` at `08dee8a`).
**Authority:** Augusto locked MTMM = patience × trust; unauthored θ/β follow literature.

This lane is **not** the paper's confirmatory application. It recovers two nested special cases of construct-identified inference on already-frozen score columns.

## 1. Empty R — unrestricted multiverse

**Claim.** If \(\mathcal R=\emptyset\), then \(M^*=M\) and \([L,U]\) is the specification-curve range over the full menu.

**Inputs (frozen; do not rebuild).**

- scores: `evals/wvs_gps_preferences/data/inputs/scores.csv` (n=41)
- roles: same `roles.json` (seven patience measures)
- beta: same `beta.yaml` (`ols_coef` of standardized measure on `log_gdp_pc`, control `q275_mean`)
- network: `networks/empty_R.yaml` (`empty_R: true`, `restrictions: []`)

**Acceptance.** Engine \([L,U]\) equals min/max of the seven already-reported \(\beta\) values. Paper-facing rounding must be \([-0.219, 0.402]\).

## 2. Campbell–Fiske as ordinary restrictions (patience × trust)

**Constructs (prose).**

> **Patience** is time preference: the disposition to value future relative to present outcomes, as operationalized by the GPS intertemporal module (Falk et al. 2018).
>
> **Trust** is the belief that other people have good intentions / that most people can be trusted. GPS trust is a single experimentally validated item; WVS Q57 is the canonical survey item.

**Unit.** Country (`iso3`), GPS ∩ WVS coverage after dropping rows missing any of the four MTMM columns.

**2×2 menu (peer, not P1).** Every column is a measure. No column is sacred.

| | Method GPS | Method WVS |
|---|---|---|
| Trait patience | `gps_patience` | `m_patience_child_qualities` (Q13/Q14 child-qualities recipe; **bridge**) |
| Trait trust | `gps_trust` | `m_trust_general` (Q57; canonical WVS trust) |

**Restrictions (instances of the moment-inequality form).**

```text
monotrait–heteromethod (convergent)
  corr_min(gps_patience,  m_patience_child_qualities)  ≥ τ_conv
  corr_min(gps_trust,     m_trust_general)             ≥ τ_conv

heterotrait–monomethod (discriminant)
  corr_zero(gps_patience, gps_trust)                   θ = τ_disc
  corr_zero(m_patience_child_qualities, m_trust_general) θ = τ_disc

heterotrait–heteromethod (discriminant)
  corr_zero(gps_patience, m_trust_general)             θ = τ_disc
  corr_zero(gps_trust,    m_patience_child_qualities)  θ = τ_disc
```

Implementation note: `corr_min` / `corr_zero` take `params.variable` as the *partner* column. Each restriction is attached to one measure and names the other as `variable`. Because the engine evaluates every restriction on every measure, a `corr_min(m, partner)` restriction is only scientifically the Campbell–Fiske cell when `m` is one of the two named columns. To keep the screen identical to a classical MTMM inspection we therefore write **one restriction per directed cell**, and we interpret \(M^*\) as the set of measures that pass every restriction *that names them*. The engine's global \(M^*\) (pass *all* restrictions) is stricter than classical per-instrument inspection; both are reported.

**Classical retain rule (hand inspection, then compare).** A measure is retained iff it clears both convergent cells that involve it and every discriminant cell that involves it.

**Thresholds (pre-data).**

| Symbol | Value | Anchor | Kind |
|---|---|---|---|
| \(\tau_{\mathrm{conv}}\) | 0.30 | OECD 2017 survey↔behavioral trust \(r\approx 0.29\); Falk et al. 2018 Table II GPS–WVS trust Spearman \(=0.49\) (\(n=60\)). Floor sits at the published survey–behavioral bound, below the GPS–WVS trust correlation. | literature |
| \(\tau_{\mathrm{disc}}\) | 0.35 | Falk et al. 2018 Table IV country Corr(patience, trust) \(=0.190\). Distinct constructs may share modest method variance; \(0.35\) still rejects \(r\gtrsim 0.6\). Same numerical bar as the patience–risk discriminant memo. | literature |

Honesty: Falk Table II GPS patience vs WVS long-term orientation (thrift childrearing) is \(0.09\) (\(p=.52\), \(n=60\)). A \(\tau_{\mathrm{conv}}=0.30\) bar is therefore expected to **reject the WVS patience method** if that published relationship holds in this overlap. That is a finding about the named special case, not a reason to lower \(\tau_{\mathrm{conv}}\).

**\(\beta\).** Same functional as the patience application: `ols_coef` of the standardized measure on `log_gdp_pc` with `q275_mean` control, joined from the frozen patience inputs. Outcome is \(\beta\)-only; it is not in \(\mathcal R\).

**Allowed findings.** Empty \(M^*\); GPS-only survivors; WVS patience failing convergent while WVS trust passes. Forbidden: moving \(\tau\) after seeing slacks; claiming the MTMM “validates culture.”
