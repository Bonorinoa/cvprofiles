# 10 — Open Questions

**Status:** living inbox. Move resolutions to `12_Decision_Engineering_Log.md`.

## Method / identification

| ID | Question | Options / notes | Blocking? |
|---|---|---|---|
| Q1 | Default slack tolerance \(\delta\) | `0` vs small positive; always grid-report | Soft for code; hard for H2 claims |
| Q2 | Bootstrap endpoint procedure | Percentile on \(L,U\); projection; other conservative | **v1.1** (bootstrap deferred; not blocking v1.0) |
| Q3 | First \(\beta\) in demos | **closed default:** `corr_y` | Soft reopen |
| Q4 | Spearman / rank restrictions in MVP | Include vs defer | Soft |
| Q5 | Reference-measure restrictions | Risk of dictionary privilege | Design taste |
| Q6 | Sharp PI theory | Garnish vs postpone entirely | Soft |
| Q7 | Multiple testing across menu | Ignore (menu fixed, descriptive) vs adjust | Soft |

## Synthetic / eval

| ID | Question | Notes | Blocking? |
|---|---|---|---|
| Q8 | Headline CI metric thresholds | \(f_{\max}=0.05\) working; PoC FA=0. Bootstrap \(c_{\min}\) later | Soft; bootstrap layer is **v1.1** |
| Q9 | Paraphrase label | **closed:** valid | Soft reopen |
| Q10 | Seed count for metric MC | 50 vs 200 | Soft |
| Q11 | Mini fixture generation now vs M1 | Path reserved; content at M1 (v1.0 spine sprint) | In progress at M1 |

## Empirical H5

| ID | Question | Notes | Blocking? |
|---|---|---|---|
| Q12 | Which public baseline? | EPU-style vs LM-tone vs other; criterion locked, choice open | Blocks M10 only |
| Q13 | Who authors first real \(R\)? | **Augusto only** for main path | Principle locked; content open |
| Q14 | Menu construction protocol for real text | Pre-register prompts/dicts before scoring | Before H5 freeze |

## Engineering

| ID | Question | Options | Blocking? |
|---|---|---|---|
| Q15 | Schema stack | Pydantic v2 (proposed) vs JSON Schema only | Soft |
| Q16 | Parquet required vs CSV OK | Both; parquet preferred | No |
| Q17 | CLI name | `cvprofiles` / `cvp` | Soft |
| Q18 | License | **MIT locked** (2026-08-01) | — |
| Q19 | Package name on PyPI | `cvprofiles` availability unknown | Before publish |
| Q20 | `AGENTS.md` timing | After M1 vs with first code | Soft |
| Q21 | Parallel bootstrap | Serial MVP vs joblib later | No |

## Scope police (reopen only via decision log)

- PPI/MARS co-deliverable  
- SAE / hypothesis generation core  
- Hosted SaaS  
- LLM-in-engine “assistant for network elicitation” as required path  

## Resolved → leave breadcrumbs

| ID | Resolution | Date |
|---|---|---|
| Spine / 4-state / no LLM in engine | Locked in SOUL + project docs | 2026-08-01 |
| Stack, MIT, package name `cvprofiles` | User confirmed | 2026-08-01 |
| Q3 first \(\beta\) | `corr_y` primary | 2026-08-01 |
| Q9 paraphrase label default | `valid` | 2026-08-01 |
| Q18 license | MIT | 2026-08-01 |
| Q22 H1 / attenuation | H1a+H1b gates; H1_latent diagnostic only; reject C on reported range | 2026-08-01 |
| Q23 near_miss | Fail ≥1 restriction by DGP design under oracle \(R\); not FA | 2026-08-01 |
| Q24 v0.1 before M1/git | Hygiene first; v0.1 exit 0 → local git OK | 2026-08-01 |
| Git remote / public repo | **LIVE:** https://github.com/Bonorinoa/cvprofiles ; tag `v0.1` @ `fb62b48` | 2026-08-01 |
| v1.0 scope / M6 | Thin spine; bootstrap/θ-grid deferred to v1.1; no M10 this sprint | 2026-08-01 |
