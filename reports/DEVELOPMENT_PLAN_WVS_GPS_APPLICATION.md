# DEVELOPMENT_PLAN — WVS/GPS Patience Application (public-facing end-to-end example)

**Date:** 2026-08-10
**Status:** DECIDED — decision card D1–D10 returned 2026-08-10; promotion to **flagship empirical example** signed via `docs/16` §11 amendment + `docs/12` entry. Implementation may begin (monolith + verifier under TDD/gate discipline); **no frozen run, no paper-facing number, no commit without explicit go**.
**Authority:** `docs/16` §11 (2026-08-10 — flagship example; IVS deferred, RESERVED); §10 lane (opened 2026-08-09). Plan does NOT reopen D5/D6 (no adapters, no proprietary APIs for paper numbers).
**Owner:** Augusto owns construct definition, menu, empirical network `R`, θ/δ/β, holdout split, claims, amendment go.

---

## 0. One-sentence scope

A **public-facing, fully replicable application** of cvprofiles on real data — country-level patience (Falk et al. 2018 GPS) with a menu of seven measures (survey proxies, a researcher-specified composite, two open-weight local-LLM prompting measures, GPS as positive control, noise as negative control) — demonstrating SCORE → RESTRICT → IDENTIFY → REPORT with a country units-split holdout benchmarked against **random selection**, and an OLS estimand any trained reader can interpret.

## 1. Why this example (positioning)

- It is a **non-trivial, public-facing proof of the full knowledge-production loop**: measure generation (survey + prompting + composite) → validity gates (human-owned `R`, θ) → identified range `[L,U]` on survivors → simple OLS.
- It teaches the **measurement vs. identification** distinction: the range is over admissible operationalizations, not a single measure's point estimate.
- The **Goodhart story is the headline**: if an LLM could certify its own measures, validity would be circular. Here the network is human-owned and never references menu measures, so prompting measures must survive an external test. Expected outcomes: GPS patience survives comfortably (positive control), noise is rejected (negative control), and the prompting measures' fate is the interesting finding — either way exit 0.
- **Random-selection baseline** (not LLM-as-judge, not fancier): the holdout claim is falsifiable — does the tool's survivor set beat random subsets on held-out moments? This matches the paper's own null ("survivors do no better on held-out moments than random selection").

## 2. Construct and menu

### 2.1 Construct definition (Augusto-owned; draft for decision)

> **Patience** = time preference as operationalized by the Global Preference Survey (Falk et al. 2018): the degree to which an individual (here: the average member of a country) values delayed over immediate rewards. Defined independently of any single instrument; GPS patience is the field-standard validated operationalization.

### 2.2 Menu M (7 measures)

| id | Type | Source | Expected role |
|---|---|---|---|
| `m_gps_patience` | survey (validated) | GPS country level | **positive control** — should survive |
| `m_wvs_q13` | survey proxy | WVS7 Q13 thrift, country mean | candidate |
| `m_wvs_q14` | survey proxy | WVS7 Q14 perseverance, country mean | candidate |
| `m_composite` | **composite C = F(φ)** | z(Q13)+z(Q14) (explicit F, no PCA) | candidate — teaching C = F(φ) |
| `m_prompt_a` | prompting, open-weight model A | llama.cpp log-prob scoring | candidate — the science |
| `m_prompt_b` | prompting, open-weight model B | llama.cpp log-prob scoring | candidate — the science |
| `m_noise` | seeded Gaussian | RNG, fixed seed | **negative control** — must be rejected |

Menu is finite and researcher-supplied; the engine never generates measures.

### 2.3 Auxiliaries / outcome

| id | Role | Source |
|---|---|---|
| `risktaking` | aux (discriminant) | GPS country level |
| `q275_mean` | aux (convergent, education ISCED) | WVS7 Q275/Q275R |
| `q48_mean` | aux (optional convergent, agency) | WVS7 Q48 |
| `log_gdp_pc` | **outcome (β only, never in R)** | wbgapi WDI `NY.GDP.PCAP.PP.KD` |

**Design lock:** the outcome `log_gdp_pc` enters ONLY as the β target. It is NOT a network restriction (no selection-on-outcome; mirrors H5 discipline).

## 3. Data pipeline (monolith stage 1)

1. Load GPS country level (`country_gps.dta`, local SCA2 repo path; `CVPROFILES_WVS_GPS_DATA` overridable). Columns: `isocode`, `patience`, `risktaking`, `trust`.
2. Load WVS Wave 7 (`WVS_wave7.dta`, local). Country means for Q13/Q14/Q48/Q275/Q279; **missing codes `-1..-5` masked, never imputed**; respondent floor per country (e.g. ≥30 — Augusto decides).
3. `wbgapi` pull: `NY.GDP.PCAP.PP.KD` (and `SE.SEC.ENRR` if wanted), `mrv=5`; **snapshot to CSV + sha256** (frozen provenance; replication does not depend on API liveness).
4. Inner-join universe GPS ∩ WVS ∩ WDI-aux; record dropped countries and reasons in the manifest (never impute missing aux).
5. Write `scores.csv` (unit × measure + aux + outcome), `roles.json`, `network.yaml`, `beta.yaml` with full provenance record (paths, hashes, WVS item codes, GPS/GDP versions).

## 4. Prompting measure protocol (monolith stage 2 — llama.cpp)

- **Model choice (D8, decided 2026-08-10):** model A = **Meta-Llama-3.1-8B-Instruct Q8_0** (`bartowski/Meta-Llama-3.1-8B-Instruct-GGUF`, verified ungated 2026-08-10; the bare `Llama-3.1-8B-Instruct-GGUF` repo does not exist), model B = **Phi-4-mini 3.8B Q8_0** (`MaziyarPanahi/Phi-4-mini-instruct-GGUF`; Phi-4 itself is 14B — too heavy for the "smaller" arm; correction logged in docs/12). Quant **Q8_0 preferred** for fidelity; Q5_K_M acceptable fallback.
- **Hardware expectations (document in README):**
  - Apple Silicon (M-series, ≥16GB RAM): 7B Q8 runs fine with Metal offload (`n_gpu_layers=35`); 3–4B Q8 fits in ~4–5GB.
  - 8GB machines: use 3–4B Q8 or 7B Q4_K_M; CPU-only machines run but ~5–10× slower — same log-probs for a **pinned GGUF file**, so results are hardware-independent *because the file (sha) and sampling settings are frozen*.
  - Not everyone can run 7B: the README must say so plainly and give the 3B/4B fallback path.
- **Determinism:** temperature 0, fixed seed, fixed context; **pinned GGUF file (sha256) + pinned llama.cpp/llama-cpp-python version** are part of the freeze record.
- **Scoring:** for each country × item, prompt with the WVS-style item + response options; read log-prob over options; aggregate (mean over items) → country score column. Outputs enter scores.csv as ordinary columns. **No LLM client in `src/`** — the harness lives in `evals/` (AST import-graph test stays green).
- A `--subset N` smoke mode (tiny country subset, no frozen claims) exists for plumbing tests; the frozen run requires the full menu.

## 5. Nomological network R (Augusto-owned; candidate θ anchors with citations)

**Anti-circularity lock:** every restriction references an **aux/outcome column only**; no restriction references a menu measure. The network is theory-anchored, not GPS-anchored.

| id | type | spec | theory / citation | draft θ |
|---|---|---|---|---|
| `conv_edu` | `corr_min` | variable `q275_mean` | patience ↑ education (Dohmen et al. 2011; Falk et al. 2018) | 0.20 |
| `mono_edu` | `monotone_rank` | variable `q275_mean`, sign +1 | patience monotone in education (continuous) | 0.15 |
| `disc_risk` | `corr_zero` | variable `risktaking` | patience and risk-taking are separate GPS dimensions, near-zero country correlation (Falk et al. 2018) | 0.30 |

**Teaching note (write in README):** the negative control `m_noise` passes `disc_risk` (uncorrelated with risk) but **fails the convergent restrictions** (`conv_edu`, `mono_edu`). Discriminant-only networks would wrongly admit noise — a classic MTMM lesson; convergent + discriminant together do the work. Do not "tune" θ to make GPS pass; θ anchors are pre-data (the package's anchors machinery exists for exactly this).

δ: 0.0 (headline). β: `ols_coef`, outcome `log_gdp_pc`, controls `[q275_mean]` (simple OLS, interpretable).

## 6. Holdout and the random-selection baseline

### 6.1 Units-split (engine, P4b)

- Split (D6, decided 2026-08-10): **fixed-seed random 80/20 — 20% of countries held out** (units = countries). Frozen in `config.holdout_units`; train ≥2, hold ≥2.
- Stage assignment (D7, decided 2026-08-10): `conv_edu` + `disc_risk` = select-stage; `mono_edu` = holdout-stage (tier-3 moment).
- Engine semantics: select on train → `M*_select`; compliance on hold units → `M*_robust`; **headline [L,U] = β on `M*_robust`**; holdout verdicts are findings, exit 0.

### 6.2 Random-selection baseline (monolith stage 3 — harness logic, not engine)

Two falsifiable comparisons, both vs. random subsets of the menu (seeded draws; e.g. 500):

1. **Holdout moment pass-rate.** Some restrictions are `stage: holdout` (tier-3 moments, e.g. `mono_edu` on hold units — Augusto picks which restrictions are select vs. holdout). Compute: pass-rate of the tool's robust set vs. the distribution of pass-rates of random subsets of size `k = |M*_robust|` (and a k-grid 1..4). The paper's null is "survivors do no better than random on held-out moments"; the application's falsifiable claim is that **the tool's survivors beat the random baseline** on these moments.
2. **Range informativeness.** Width of tool `[L,U]_robust` vs. distribution of widths from random subsets of the same size. A narrower-but-nonempty tool range = the validity gates bought information; an empty robust set or a width ≈ random = honest negative finding.

**Explicit note for the reader:** `M*_robust` complies on the *selection* restrictions by construction (that is the definition). The non-trivial comparisons are the tier-3 holdout moments and the range, which are not guaranteed.

## 7. Verification / "works as intended"

`tools/verify_wvs_gps.py` (pattern: `tools/verify_h5_trust.py`):
- frozen inputs exist and hashes match (scores/network/beta/roles, WVS item codes, wbgapi snapshot sha);
- re-run engine from frozen inputs → same `run_id` (cold determinism);
- **G1 positive control:** `m_gps_patience ∈ M*_robust`;
- **G2 negative control:** `m_noise ∉ M*` (rejected, never in range);
- **G3 holdout payload:** verdict block present, exit 0 even if prompting measures fail;
- **G4 baseline computed:** random-selection distribution present with seeds recorded;
- **G5 headline identity:** `[L,U] == [min β(M*_robust), max β(M*_robust)]`;
- **G6 open-weight:** no proprietary API call in the harness; AST import-graph test green;
- exit 0 / non-zero with named failures; summary JSON allow-listed under `reports/summaries/`.

Also: full pytest + ruff + mypy battery unchanged; monolith smoke (`--subset`) runs in CI without a GPU/7B model.

## 8. Monolith script (deliberately one file)

`evals/wvs_gps_preferences/run_application.py` — single readable file, sectioned:

```text
stage 0: parse args / seeds          (stdout = JSON summary; stderr = human notes)
stage 1: build data (GPS/WVS/wbgapi) + provenance + frozen inputs
stage 2: prompting measures (llama.cpp, optional --subset N)
stage 3: engine run_profile (holdout_units, n_boot, coverage)
stage 4: random-selection baselines + tier-3 holdout moments
stage 5: summary JSON + README-facing report
```

Readability over abstraction first; refactor later only if it becomes dirty (owner's call). No new `src/` code; no new engine features.

## 9. Governance / amendment path (prerequisite for frozen runs)

1. **Decision card** (below) returned by Augusto.
2. **`docs/16` §11 dated amendment** — status upgrade: WVS/GPS patience application = **flagship empirical example** of the full knowledge-production loop; IVS/Gate B remains the separate paper headline lane; "what this does NOT authorize": no adapter training, no proprietary API for frozen numbers, no engine change, no tag/PyPI by implication, no extension to other constructs without further amendment.
3. `docs/12` entry (dated); ROADMAP/MANIFEST posture lines; lane README status flip from "intermediate demo" to flagship example.
4. Frozen run → `verify_wvs_gps.py` exit 0 → summary allow-listed → Augusto's run decision.

## 10. Decision card (Augusto — **RETURNED 2026-08-10, all accepted**)

| # | Decision | Decision | Default if silent |
|---|---|---|---|
| 1 | Status upgrade amendment (§11) | **Approve as flagship example; IVS deferred (RESERVED)** | No run |
| 2 | Construct definition sentence | §2.1 draft accepted | §2.1 |
| 3 | Menu (7 measures) | §2.2 accepted | §2.2 |
| 4 | Network R + θ (conv_edu 0.20, mono_edu 0.15, disc_risk 0.30) | **Frozen; references pinned (Dohmen et al. 2011; Falk et al. 2018)** | No run |
| 5 | β spec | ols_coef, outcome log_gdp_pc, controls [q275_mean] | No run |
| 6 | Holdout split | **fixed-seed random 80/20** (units = countries) | No run |
| 7 | select vs. holdout stage assignment | conv_edu, disc_risk select; mono_edu holdout | No run |
| 8 | Prompt models + quant | **Llama-3.1-8B + Phi-4-mini 3.8B, Q8_0** (Phi-4 = 14B, rejected for small arm) | No run |
| 9 | Random baseline draws | 500 seeds, k-grid 1..4 | No run |
| 10 | Respondent floor | ≥30 | ≥30 |

## 11. Risks

| # | Risk | Mitigation |
|---|---|---|
| 1 | Prompting measures all fail → empty robust set | Empty = honest finding, exit 0; README frames it; GPS + survey arms still demonstrate the loop |
| 2 | "M*_robust complies by construction" confusion | §6.2 explicit note; baselines target tier-3 moments and range, not selection compliance |
| 3 | wbgapi liveness / version drift | snapshot + sha at build time; frozen inputs are the evidence, API is only the pull |
| 4 | 7B too heavy for some readers | README hardware section + 3B/4B fallback; same frozen GGUF ⇒ hardware-independent results |
| 5 | θ tuning to make GPS pass | θ anchors pre-data, citations pinned, anchors machinery used |
| 6 | Scope creep to "automate all empirical economics" | Non-goals unchanged; this is one lane, one construct, one estimand |

## 12. Immediate next step after card returns

1. Draft `docs/16` §11 amendment text for approval (no commit without go).
2. Write monolith stage 1 (data build) + fixture test on a tiny synthetic slice (RED→GREEN per AGENTS.md).
3. Write stage 3/4 engine + baseline logic + smoke test; then stage 2 prompting harness on `--subset`.
4. Checkpoint: report to Augusto with measured outputs before the frozen run.
