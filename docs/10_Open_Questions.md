# 10 — Open Questions

**Status:** living inbox. Move resolutions to `12_Decision_Engineering_Log.md`.

## Method / identification

| ID | Question | Options / notes | Blocking? |
|---|---|---|---|
| Q1 | Default slack tolerance δ | `0` vs small positive; always grid-report → **v2.0: absolute δ-grid decided** (`docs/18`, `docs/12` 2026-08-05) | Soft for code; hard for H2 claims |
| Q2 | Paper interpretation of the bootstrap band | Package semantics are locked in v1.1: pointwise percentile endpoints over non-empty replicates; all-empty ⇒ null band; degenerate replicates counted and excluded. Paper interpretation remains open. | Soft; paper protocol |
| Q3 | First \(\beta\) in demos | **closed default:** `corr_y` | Soft reopen |
| Q4 | Spearman / rank restrictions in MVP | Include vs defer → **v2.0: `rank_agree` evaluator** (`docs/18`) | Soft |
| Q5 | Reference-measure restrictions | Risk of dictionary privilege | Design taste → v2.0 `rank_agree` ref_measure semantics (`docs/18`) |
| Q6 | Sharp PI theory | Garnish vs postpone entirely | Soft |
| Q7 | Multiple testing across menu | Ignore (menu fixed, descriptive) vs adjust | Soft |

## Synthetic / eval

| ID | Question | Notes | Blocking? |
|---|---|---|---|
| Q8 | Headline CI metric thresholds | \(f_{\max}=0.05\) working; PoC FA=0. Paper threshold and any bootstrap reporting bar remain open. | Soft; paper protocol |
| Q9 | Paraphrase label | **closed:** valid | Soft reopen |
| Q10 | Seed count for metric MC | `0..49` locked for the provisional synthetic-only MC50 table; a future different paper protocol needs an amendment, not post-hoc expansion | Soft; paper protocol |
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
| Q19 | PyPI publication | **published 2026-08-06 (`2.0.0`)**; name live; future releases via the user-owned token flow | Resolved |
| Q20 | `AGENTS.md` timing | **present** (2026-08-04) — root handoff contract created; future agents should read it | Resolved |
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
| v1.1 inference semantics | Units-only bootstrap and diagnostic θ-grid are shipped and locked; headline range remains \([L,U]=\min/\max B^*\) | 2026-08-04 |
| Q19 name availability | `https://pypi.org/pypi/cvprofiles/json` returned HTTP 404; no publication attempted | 2026-08-04 |
| Q19 PyPI publication | cvprofiles `2.0.0` published on PyPI (2026-08-06); user-owned token flow; independent verification chain (JSON API + sha256 + fresh-venv notebook) | 2026-08-06 |
| δ-grid semantics | **Absolute δ grid** — thread (a) of v2.0 measure discipline; grid excluded from freeze preimage; headline = declared δ | 2026-08-05 |
