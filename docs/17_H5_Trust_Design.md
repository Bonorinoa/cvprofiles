# 17 — H5 Trust Design (country-level generalized trust)

**Status:** `LOCKED AS H5 DESIGN` (2026-08-04) — construct, unit/universe, menu/roles, network, θ, δ, β, and claims boundary are fixed as design. **Empirical run gated:** no run, no paper number, no `docs/13` claim until frozen scores + pinned seed + package version exist and an independent audit passes.

**Package baseline:** `cvprofiles==1.1.0a1`

**Owner:** Augusto owns the final wording of every researcher-authored field. The construct paragraph below was drafted by the agent at Augusto's explicit one-off delegation (2026-08-04) and **approved verbatim** by Augusto; the network was proposed by the agent with literature anchors and **pinned by Augusto** the same day.

**Independence:** this design is built from raw public survey files and public economic data. It does **not** reuse the SCA2 validity lane (`scores_trust.csv`, its minimal engine, or its pilot network); SCA2 provenance is recorded only as data provenance in the frozen manifest.

---

## 1. Construct (approved paragraph)

> Generalized trust — the belief that most people can be trusted — is a central but elusive input to economic development: cross-country evidence links it to growth, trade, and financial market participation, yet every available instrument is an imperfect operationalization of the latent belief, and leading measures agree only weakly (country-level correlations of roughly 0.3 between survey and behavioral measures). We treat this measurement problem as an identification problem rather than a nuisance. For a sample of roughly 40 countries we assemble a menu *M* of candidate measures from three independent survey families — the World Values Survey (generalized, in-group, out-group, and institutional facets), the Global Preference Survey (a behaviorally validated single item), and the AmericasBarometer — and impose a pre-registered nomological network *R* that requires admissible measures to co-move with a behaviorally validated trust anchor and institutional quality, and to move opposite income inequality, at thresholds anchored in published findings. The object of inference is the construct-identified range [L,U] of the correlation between admissible trust measures and economic development (log GDP per capita), quantifying how much of the trust–development relationship is attributable to measurement choice rather than to any single instrument. Empty admissible sets are reported as honest findings, not resolved by loosening thresholds.

## 2. Unit and universe

| Field | Locked value |
|---|---|
| Unit | country (`iso3`) |
| Universe | WVS Wave 7 countries ∩ GPS country-level coverage, per-item respondent floor ≥ 200 (pre-registered), fieldwork ~2017–2021 |
| Expected n | ≈ 40 (exact overlap verified at scaffold time; recorded in frozen manifest) |
| Sample-size posture | admission statements are sample-dependent (documented capability boundary); bootstrap resamples units (countries) |

## 3. Score input (SCORE spec)

Frozen wide table `S_frozen.csv`, columns:

| Column | Role | Source | Construction |
|---|---|---|---|
| `iso3` | unit_id | — | standard codes |
| `m_trust_general` | measure (valid) | WVS7 Q57 | share "most people can be trusted" |
| `m_trust_in_group` | measure (valid) | WVS7 Q58,Q60 | mean, reversed to 0–1 |
| `m_trust_out_group` | measure (valid) | WVS7 Q61–63 | mean, reversed to 0–1 |
| `m_trust_institution` | measure (valid) | WVS7 Q64,Q69–71 | mean, reversed to 0–1 |
| `m_noise` | measure (**invalid_noise**) | seeded RNG (seed pinned) | Gaussian — must fail all bars |
| `m_share_agriculture` | measure (**invalid_confounded**) | WDI `SL.AGR.EMPL.ZS` | plausible "traditional society" proxy — theory says wrong signs vs institutions/inequality |
| `gps_trust` | aux | GPS country-level | standardized country mean (behavioral anchor) |
| `rule_of_law` | aux | WGI `rq`, avg 2015–2019 | institutional quality |
| `gini` | aux | WDI `SI.POV.GINI`, avg 2015–2019 | income inequality (negative bar) |
| `log_gdp_pc` | **outcome** | WDI `NY.GDP.PCAP.PP.KD`, avg 2015–2019 | β target; **not** in network |
| `n_*` counts | diagnostic | per item | merged into frame; declared in roles |

Missingness: mask WVS negative codes and AB 88/98 in the builder; any residual NaN → fail loud (engine does not impute). Country means **unweighted** by default; weighted means are a diagnostic contrast.

## 4. Menu and design roles

- Designed **valid**: the four WVS facets (`m_trust_general`, `m_trust_in_group`, `m_trust_out_group`, `m_trust_institution`).
- Designed **invalid**: `m_noise` (invalid_noise), `m_share_agriculture` (invalid_confounded). False admission of either is a failed gate.
- AmericasBarometer (`IT1` community trust) is a **2-country probe (USA/MEX), appendix only** — not part of the main menu (n=2 is degenerate for corr-based restrictions; per `DATASET_GUIDE.md`, do not row-stack WVS with AB).

## 5. Nomological network R (pinned 2026-08-04)

```yaml
name: h5_trust_generalized
delta: 0.0
restrictions:
- {id: r_corr_min_gps_trust,   type: corr_min,   variable: gps_trust,     theta: 0.3}
- {id: r_corr_min_rule_of_law, type: corr_min,   variable: rule_of_law,   theta: 0.3}
- {id: r_corr_sign_gini_neg,   type: corr_sign,  variable: gini, sign: -1, theta: 0.1}   # engine schema uses params.sign (corrected 2026-08-06, docs/12)
```

Admission rule (package canonical): admit `m` when `s_r(m) >= -delta` for all `r`, with `delta = 0`.

## 6. θ anchors (pre-data, literature-grounded)

| Restriction | θ | Anchor |
|---|---|---|
| `corr_min(gps_trust, 0.3)` | 0.3 | OECD (2017): country-level survey↔behavioral trust r ≈ 0.29; SCA2 pilot corr range 0.28–0.35 |
| `corr_min(rule_of_law, 0.3)` | 0.3 | trust–institutions correlations typically ≥ 0.4 (Aghion–Algan–Cahuc–Shleifer 2010; Martinangeli et al. 2024) |
| `corr_sign(gini, −, 0.1)` | 0.1 | Bjørnskov (2008): negative trust–inequality relationship |

All three sit at or below published bounds → conservative, not data-mined.

## 7. δ policy

**δ = 0** (canonical; matches provisional synthetic lock). Any future tolerance requires a dated amendment + reporting policy.

## 8. β and outcome

**β = `corr_y`** with `y = log_gdp_pc` (avg 2015–2019). GDP per capita is deliberately **not** in the network (avoids circularity); the range `[L,U] = [min B*, max B*]` is over admissible survivors only.

## 9. Claims boundary

| Allowed | Forbidden |
|---|---|
| M\* under stated network; [L,U] on survivors only | causal claim trust→development (network is sign-restricted correlations; Algan–Cahuc et al. justify directions, not engine estimates) |
| Which facets fail which bars, at which λ | "true trust level" of any country / rankings |
| Measurement fragility of the trust–development correlation | interchangeability of instruments |
| Empty M\* as an honest finding | automatic θ loosening |

Diagnostics (appendix only): units-only bootstrap (pinned seed), θ-grid λ ∈ {0.5, 1.0, 1.5, 2.0} with λ=1.0 headline; both additive, headline range unchanged.

## 10. Auxiliary data sources (public, no proprietary API)

| Auxiliary | Source | Access |
|---|---|---|
| `log_gdp_pc` | World Bank WDI `NY.GDP.PCAP.PP.KD` | API, free, no key |
| `rule_of_law` | WGI (World Bank) `rl` (Rule of Law estimate) | free download |
| `gini` | WDI `SI.POV.GINI` | API |
| `m_share_agriculture` | WDI `SL.AGR.EMPL.ZS` | API |

Values averaged 2015–2019 to align with WVS7 fieldwork; exact indicator IDs and dates pinned in the builder manifest.

## 11. Independent audit tool

`tools/verify_h5_trust.py` — read-only verifier (pattern: `tools/verify_v11_protocol_synth_mc50.py`):
- strict JSON (reject NaN/Infinity; null only for structurally empty range);
- assert designed-invalids ∉ M\* (FA=0), designed valids subject to bars;
- freeze-core equality across two cold runs (M\*, L, U, hashes, empty, rejected);
- finite values; provenance fields (parent SHA, protocol id, package version, seed list);
- structural audit ≠ paper acceptance; Gate C-style decision remains Augusto's.

## 12. Run gate / lock flags

- This document is a **design lock**, not a run authorization.
- Executing the H5 trust evaluation requires, in order: (1) frozen `S_frozen.csv` + manifest built from raw files; (2) pinned seed + package version recorded; (3) independent audit exit 0; (4) Augusto's explicit run/go decision for any paper-facing claim.
- No engine change, tag, push, or PyPI publication is authorized by this design.
- `docs/16` amendment (2026-08-04) opens the empirical box **for this designated evaluation only**; the provisional synthetic-only MC50 protocol and its table are unaffected.

## References

- WVS Wave 7 (Haerpfer et al., JD Systems Institute & WVSA); GPS (Falk et al. 2018, *QJE*); AmericasBarometer (LAPOP, Vanderbilt).
- Algan & Cahuc 2010 (*AER*); Guiso, Sapienza & Zingales 2004 (*JF*), 2008 (*JF*), 2009 (*QJE*); Aghion, Algan, Cahuc & Shleifer 2010 (*QJE*); Bjørnskov 2008; Butler, Giuliano & Guiso 2016 (*JEEA*); Martinangeli et al. 2024 (*AJPS*); OECD (2017) Guidelines on Measuring Trust; Johnson & Mislin 2012 (*Economics Letters*); Sapienza, Toldrà-Simats & Zingales 2013 (*EJ*).
