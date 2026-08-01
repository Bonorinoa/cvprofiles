# 05 — Pre-Registration (Draft)

**Status:** DRAFT scaffold v0 (2026-08-01) — **not frozen for paper until Augusto signs**  
**Rule:** Engine-property hypotheses (H1–H4) may be agent-drafted. **Empirical/theory hypotheses that need a real construct network (H5) are USER-OWNED templates only.**

This document is a *working prereg*. Freeze = dated entry in `12_Decision_Engineering_Log.md` + git tag later. Until freeze, treat as intent.

## Study aims

1. Show that a finite measurement menu + researcher network yields a transparent admissible set \(M^*\) and construct-identified range for \(\beta\).  
2. Characterize engine behavior on calibrated synthetic DGPs via four debug metrics.  
3. (Later, USER path) Apply to one public, boring, heavily documented baseline without silent network authorship.

## Analysis universe

| Layer | Data | Network author |
|---|---|---|
| Synthetic primary | DGP suite in `04_Synthetic_DGPs.md` | Oracle-compatible \(R\) shipped with DGP (eval-only) |
| Real baseline | TBD public dataset | **USER OWNS** |

## Hypotheses

### H1 — Split coverage (engine / synthetic) — LOCKED intent 2026-08-01

Reported \([L,U]\) is always \(\min/\max\) of \(\{\beta(m):m\in M^*\}\) (plus later bootstrap layer). It is **not** required to cover latent \(\mathrm{Corr}(V^*,y)\).

#### H1a — Admissible-set integrity (primary gate)

On `oracle_easy` and `oracle_with_slop` at \(\delta=0\):

- False-admission rate for labels in `{invalid_confounded, invalid_noise, wrong_construct}` ≤ **\(f_{\max}\)** (working default \(0.05\); PoC target \(0\)).  
- At least the designated anchor valid measure (`m_dict`) is in \(M^*\) on ≥ **\(a_{\min}\)** of seeds (working default \(0.90\)).  
- Near-miss admissions are logged separately; they do **not** count as FA.

**Falsifier:** confounded/noise/wrong measures systematically enter \(M^*\), or anchor valid is systematically excluded under oracle-compatible \(R\).

#### H1b — Feasible-anchor coverage (synthetic gate)

On the same scenarios, when \(M^*\ne\emptyset\):

- \(\beta(m_{\mathrm{anchor}})\in[L,U]\) on ≥ **\(c_{\min}\)** of nonempty seeds (working default \(0.90\); with min/max range and anchor \(\in M^*\), this is **1.0 by construction** if anchor survives — the real test is that anchor is in \(M^*\) and range is built only from survivors).  
- Anchor default: `m_dict`. If anchor \(\notin M^*\), H1b is a miss for that seed (do not swap anchors post hoc).

**Falsifier:** range construction excludes survivor \(\beta\) values, or silent use of non-survivors / latent targets.

#### H1_latent — Latent coverage (diagnostic only, not a gate)

- Fraction of nonempty seeds with \(\mathrm{Corr}(V^*,y)\in[L,U]\).  
- Expected to be **low** under noisy admissible measures + \(\beta=\mathrm{corr}_y\) (attenuation). Report the gap; do not “fix” via \(\theta\).

### H2 — False admission control (engine)

On `oracle_with_slop` and `all_invalid`:

- Same FA definition as H1a; ≤ **\(f_{\max}\)** (working \(0.05\); PoC target \(0\)).  
- Near-miss reported separately.

**Falsifier:** confounded measures systematically enter \(M^*\) under oracle \(R\).

### H3 — Empty-set honesty (engine)

On `harsh_theta` and `all_invalid`:

- Empty-set rate ≥ **0.8** of seeds (PoC target **1.0**).  
- REPORT / payload names binding failures.  
- Default path **does not** auto-loosen \(\theta\).

**Falsifier:** non-empty \(M^*\) via silent rule relaxation, leftover valid trackers in `all_invalid`, or crash on empty.

### H4 — Freeze reproducibility (engine)

Cold independent runs with identical `(scenario, n, seed, δ, R, β_id, poc_version)` ⇒ identical `slacks`, \(M^*\), \([L,U]\) (float equality on computed values).

**Falsifier:** flaky outputs under pinned seeds.

### H5 — Real-data construct profile (USER OWNS — template only)

> **Do not fill baseline, network, or \(\theta\) here without Augusto’s explicit authorship.**

Template:

| Field | Value |
|---|---|
| Construct \(C\) | TBD — USER |
| Dataset | TBD — USER (candidates listed below, not chosen) |
| Menu \(M\) construction | TBD — USER (must be frozen scores; no midstream prompt search) |
| Network \(R,\theta\) | TBD — USER authored; agent may critique, not ghostwrite main path |
| Target \(\beta\) | TBD — USER |
| Primary claim | Under stated \(R\), \(M^*\) and \([L,U]\) for \(\beta\); empty/wide outcomes allowed |
| Comparison | Single preferred measure point estimate vs construct-identified range (descriptive, not a horse race hack) |
| Success (scientific) | Audit trail complete; claims match identification; not “narrower is better” |

**Owner:** Augusto.  
**Agent role:** scaffolding, scoring recipes if asked, engine correctness — **not** inventing \(R\) for main results.

## Candidate real baselines (not selected)

Selection criterion (LOCKED intent): **boring, heavily documented, debuggable association** — not maximum economic sexiness; not private admin data.

| Candidate | Why consider | Why hesitate |
|---|---|---|
| BBD-style EPU ↔ macro/financial association | Canonical text-as-measure; rich public replication culture | Construct network must still be authored carefully |
| Loughran–McDonald tone ↔ returns | Dictionary menu natural; well trodden | Easy to overfit narrative; markets are brutal |
| Other public text-measure papers | Flexibility | Must meet documentation + freeze bar |

**Decision deferred** until synthetic H1–H4 gates pass. Record choice only in decision log when made.

## Four debug metrics (operational definitions)

See `04_Synthetic_DGPs.md`. Prereg freezes:

- scenarios in primary battery: `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`, `n_small`  
- default \(\delta=0\) with reporting on \(\delta\)-grid  
- seeds: list to be pinned at freeze (placeholder: `0..49` for metric Monte Carlo if used; single-seed demos separate)

## Inference stance for prereg (DRAFT)

- Bootstrap **units**, \(B\) replicates TBD (proposal 999).  
- Conservative reporting of \([L,U]\) preferred to sharp PI claims.  
- Sharp theory optional; if absent, say so in REPORT.

## What we will not claim if prereg freezes as-is

- Global superiority of LLM measures over dictionaries  
- Causal identification from measurement menus alone  
- That empty \(M^*\) means the construct is unreal  

## Amendments

Any post-freeze change = new dated decision-log entry + amendment note here. No silent edits.
