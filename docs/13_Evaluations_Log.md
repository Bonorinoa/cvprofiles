# Evaluations Log

This is a **live** document. Append a short entry after every meaningful synthetic battery, golden-oracle stress, or (later) frozen real-baseline run.

Do **not** paste raw bootstrap draws here. Point to `reports/runs/<run_id>/` for full artifacts.

Machine-readable summaries may later live under `reports/summaries/`; this file remains the human narrative of what we learned.

---

## How to log a run

```markdown
## YYYY-MM-DD — <short title>

- **run_id(s):** …
- **package / git:** … (when available)
- **scenario(s):** …
- **n, J, seed(s), δ, θ notes:** …
- **network hash / label:** … (oracle_* vs user)
- **β:** …

| Metric | Value |
|---|---|
| H1a (FA / anchor retention) | |
| H1b (anchor β in [L,U]) | |
| H1_latent (diagnostic only) | |
| H2 False-admission | |
| H3 Empty-set rate | |
| H4 Cold repro | |
| Point-ID rate | |
| \|M*| (mean or per-seed) | |
| [L,U] vs β(anchor) | |

Package-battery rows name **H1a / H1b / H1_latent / H2 / H3 / H4** (do not revive bare “Coverage” as a gate).

**Interpretation:**
- …

**Follow-ups:**
- …
```

---

## Metric definitions (pointer)

See `04_Synthetic_DGPs.md` and `05_Pre_Registration.md` (H1–H4). Do not redefine metrics ad hoc in a log row; if definitions change, add a decision-log entry first.

---

## 2026-08-01 — Log initialized (no runs yet)

- **run_id(s):** none  
- **status:** scaffold v0; engine not implemented  
- **note:** H5 real-data evaluations are blocked until (1) synthetic H1–H4 gates pass directionally and (2) Augusto authors the empirical network. Agent must not fill H5 network content “to get a row.”

**Interpretation:**
- Eval discipline exists before code so M8 harness has a place to write.

**Follow-ups:**
- First expected rows: mini fixture oracle after M4–M5; full four-metric battery after M8.

---

## 2026-08-01 — v0_poc first battery (monolith)

- **run_id(s):** `v0_poc_<scenario>_seed{0..4}.json` + `v0_poc_summary.json` under `reports/runs/`
- **script:** `evals/synthetic/v0_poc.py` (monolith; not package)
- **package / git:** none (no git yet); env `.venv` Python 3.11 + numpy/pandas
- **scenario(s):** `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`
- **n, J, seed(s), δ, θ notes:** \(n=1000\), \(J=10\), seeds `0..4`, \(\delta=0\); oracle \(R\): `corr_min(v_aux,0.35)`, `corr_sign(v_aux,+1,0.10)`, `mean_order(g,0.10)`; harsh: \(\theta\in\{0.85,0.50,0.80\}\)
- **network hash / label:** oracle synthetic (agent-authored OK); not user empirical network
- **β:** `corr_y` headline; `ols_coef` stored secondary; **no bootstrap** — \([L,U]=\) min/max over \(M^*\) only
- **determinism:** re-run `oracle_with_slop` seed0 reported identical \(M^*/L/U\) (see caveats below)

| Scenario | empty-set rate | mean FA | coverage (nonempty) | point-ID rate | mean width | invalid ever admitted |
|---|---:|---:|---:|---:|---:|---|
| `oracle_easy` | 0.00 | 0.000 | **0.00** | 0.00 | 0.061 | none |
| `oracle_with_slop` | 0.00 | 0.000 | **0.00** | 0.00 | 0.061 | none |
| `harsh_theta` | **1.00** | 0.000 | n/a | 0.00 | n/a | none |
| `all_invalid` | 0.00 | 0.000 | 0.00 | **1.00** | 0.000 | none |

Typical oracle nonempty cell (seed0): \(M^*=\{m\_dict,m\_llm\_good,m\_para,m\_heavy\_tail,m\_floor\}\), \([L,U]\approx[+0.41,+0.46]\), \(\beta^*=\mathrm{Corr}(V^*,y)\approx +0.47\); `m_slop` / noise / wrong rejected on `r_corr_aux`.

**Interpretation:**
1. **Engine path works.** Slacks → \(M^*\) → range → JSON/report; empty \(M^*\) on `harsh_theta` is clean (feature, not crash); invalid confounded measures never entered \(M^*\) (FA=0).
2. **Coverage=0 is mostly attenuation, not a broken admissible set.** Under \(\beta=\mathrm{corr}_y\), any noisy \(m=V^*+\varepsilon\) has \(\mathrm{Corr}(m,y)<\mathrm{Corr}(V^*,y)\) in this DGP. Survivors cluster below \(\beta^*\); min/max range therefore misses \(\beta^*\). Do **not** “fix” by loosening \(\theta\). H1 metric needs bias-aware definition before prereg freeze.
3. **`m_floor` (near_miss) is admitted** under oracle \(R\) — floor/censor still clears `corr_min`/`mean_order`. Either strengthen \(R\), re-label, or treat near_miss admission as expected under weak networks.
4. **PoC DGP bugs (not engine bugs):**
   - `oracle_with_slop` ≡ `oracle_easy` (same generator path; no extra slop stress).
   - `all_invalid` does **not** destroy `m_floor`/`m_near` → singleton \(M^*=\{m\_floor\}\), point-ID rate 1.0; scenario name overclaims.
   - Determinism check re-reads the JSON it just wrote (weak smoke); needs cold second process or in-memory double call without overwrite confusion.

**Follow-ups:**
- Decision on H1 coverage operator (attenuation-aware) — see decision log + Q22.
- v0.1 PoC: differentiate `oracle_with_slop`; fully kill valid trackers in `all_invalid`; honest determinism check.
- Optional: reclassify or redesign `m_floor` near_miss under oracle \(R\).
- Do not freeze H1–H4 on this battery alone.

---

## 2026-08-01 — v0.1 PoC hygiene battery (GATES GREEN)

- **run_id(s):** `v0_1_poc_<scenario>_seed{0..4}.json` under `reports/runs/`; proof summary `reports/summaries/v0_1_poc_summary.json`
- **script:** `evals/synthetic/v0_poc.py` (`POC_VERSION=v0_1_poc`; monolith museum piece)
- **package / git:** none at run time; local git authorized after this green exit
- **scenario(s):** `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`
- **n, J, seed(s), δ:** \(n=1000\), \(J=10\), seeds `0..4`, \(\delta=0\); standard \(R\): `corr_min(v_aux,0.35)`, `corr_sign(v_aux,+1,0.10)`, `mean_order(g,0.10)`; harsh \(\theta\in\{0.85,0.50,0.80\}\)
- **network:** oracle synthetic only
- **β:** `corr_y` headline; `ols_coef` secondary; **no bootstrap** — \([L,U]=\min/\max B^*\)
- **exit code:** `0` — `evaluate_gates` ALL PASSED
- **labels note:** static LABELS are **design roles** (valid / near_miss / invalid_*), not post-hoc truth after `all_invalid` knobs destroy columns. FA uses design-role invalids only.

| Scenario | empty | FA | anchor in \(M^*\) | H1b | H1_latent | mean width | mean \(\beta(m_{\mathrm{slop}})\) | cold | invalid | near_miss |
|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|
| `oracle_easy` | 0.00 | 0.000 | **1.00** | **1.00** | 0.00 | 0.048 | +0.481 | True | none | none |
| `oracle_with_slop` | 0.00 | 0.000 | **1.00** | **1.00** | 0.00 | 0.048 | **+0.547** | True | none | none |
| `harsh_theta` | **1.00** | 0.000 | 0.00 | n/a | n/a | n/a | +0.481 | True | none | none |
| `all_invalid` | **1.00** | 0.000 | 0.00 | n/a | n/a | n/a | +0.517 | True | none | none |

Typical oracle nonempty cell: \(M^*=\{m\_dict,m\_llm\_good,m\_para,m\_heavy\_tail\}\); near_miss and invalids fail `r_corr_aux` (or more).

**Interpretation:**
1. **v0 bugs closed.** `oracle_with_slop` distinct (\(\bar\beta(m_{\mathrm{slop}})\): 0.481 → 0.547); `all_invalid` true empty; cold independent double-run equality holds.
2. **H1a / H3 / H4 green.** FA=0; anchor always retained under oracle \(R\); empty honesty on harsh + all_invalid; cold determinism True.
3. **H1b=1.0 is a construction invariant** once anchor \(\in M^*\) and \([L,U]=\min/\max B^*\) — do not oversell as deep empirical discovery. Primary scientific bite is H1a + H3 + H4.
4. **H1_latent=0 expected** (attenuation). Not a gate. No \(\theta\)-loosening.
5. **Near-miss by design (Q23):** `m_near` / `m_floor` never enter \(M^*\) under standard oracle \(R\).

**Follow-ups:**
- Local git init (no remote) authorized by green exit + user prerequisite.
- M1 package spine next when Augusto says go — do not import this monolith into `src/`.

---

## 2026-08-01 — Package path note (M1; no battery yet)

- **status:** G1 schemas + freeze contracts green under `tests/`; no package synthetic battery row yet.
- **museum:** `evals/synthetic/v0_poc.py` remains historical proof only.
- **next eval log row expected:** after M8 package harness re-impl (H1a / H1b / H1_latent / H2 / H3 / H4).

---

## 2026-08-01 — Package path M7 e2e (mini_v1; not full Monte Carlo)

- **run_id(s):** golden freeze `f0f989992ad68099140a3ff9fbfe619eb5faabdf05315aa8c7beccfb2231ccac` (oracle, seed 0, `1.0.0a1`); harsh demo under `reports/runs/demo_mini_v1_harsh/` (gitignored)
- **package / git:** `cvprofiles==1.0.0a1`; package path SCORE→REPORT (not museum)
- **scenario(s):** mini_v1 oracle network; mini_v1 harsh (`corr_min` θ=0.999)
- **n, J, seed(s), δ:** n=10, J=3 (`m_good`,`m_weak`,`m_slop`), seed 0, δ=0; β=`corr_y`
- **network:** oracle synthetic fixture (agent-OK); not USER empirical R
- **β:** `corr_y`; **no bootstrap** — `[L,U]=min/max B*`

| Metric | Oracle | Harsh |
|---|---:|---:|
| H1a FA (`m_slop` admitted) | **0** | 0 |
| Anchor / valids in M* | `m_good`,`m_weak` | none |
| H1b (survivor β in [L,U]) | 1 by construction | n/a (empty) |
| H1_latent diagnostic | not gated (n=10 toy) | n/a |
| H3 empty-set honesty | 0 | **1** (exit 0) |
| H4 cold double-run | True (`run_id`/M*/[L,U]) | True |

Typical oracle cell: M*={m_good, m_weak}; m_slop fails `r_corr_min_aux` + `r_corr_sign_aux`; [L,U] ≈ [0.9908, 0.9930] (image of survivors only; slop β≈−0.98 never enters).

**Interpretation:**
1. Thin package spine works end-to-end without museum import.
2. FA=0 and empty-M* beauty hold on the hand fixture (directional G7).
3. **Not** a full H1–H4 Monte Carlo battery — that is **M8**.

**Follow-ups:**
- M8: re-impl synth harness under package/tests; append full battery row.
- Do not tag `v1.0.0` from this chat; sibling release chat evaluates candidates.

---

## 2026-08-01 — Package path M8 battery GREEN (v1_0_package_synth)

- **proof:** `reports/summaries/v1_0_package_synth_summary.json`
- **package / git:** `cvprofiles==1.0.0a1`; battery drives real spine `run_score` → `run_restrict` → `run_identify` (not a parallel identify)
- **museum:** `evals/synthetic/v0_poc.py` present, **unimported** (AST import-graph checks)
- **scenario(s):** `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`
- **n, J, seed(s), δ:** \(n=1000\), \(J=10\), seeds `0..4`, \(\delta=0\); SCORE policy `none`
- **network:** eval-only oracle \(R\): `corr_min(v_aux,0.35)` + `corr_sign(v_aux,+,0.10)`; harsh: `corr_min` \(\theta=0.95\), `corr_sign` \(\theta=0.50`
- **β:** `corr_y`; **no bootstrap** — \([L,U]=\min/\max B^*\)
- **passed:** `True` — all named gates green

| Scenario | FA | anchor in \(M^*\) | empty | H1b | H1_latent (diag) | cold | mean \(\|M^*\|\) | mean width |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `oracle_easy` | **0.000** | **1.000** | 0.000 | **1.0** | **0.0** | **1.000** | 4.00 | ≈0.048 |
| `oracle_with_slop` | **0.000** | **1.000** | 0.000 | **1.0** | **0.0** | **1.000** | 4.00 | ≈0.048 |
| `harsh_theta` | 0.000 | 0.000 | **1.000** | n/a | n/a | **1.000** | 0.00 | n/a |
| `all_invalid` | 0.000 | 0.000 | **1.000** | n/a | n/a | **1.000** | 0.00 | n/a |

Typical oracle nonempty cell: \(M^*=\{m\_dict,m\_llm\_good,m\_para,m\_heavy\_tail\}\); near_miss + invalids fail `r_corr_min_aux` (and/or sign); slop \(\beta\) does not enter \([L,U]\).

**Interpretation:**
1. **Package path earns H1a / H1b / H3 / H4** on the real engine — not museum numbers.
2. **FA=0** on designed invalids; **anchor retained**; **empty honesty** on harsh + all_invalid; **cold double-run** True.
3. **H1_latent=0** expected under attenuation (\(\beta=\mathrm{corr}_y\)); diagnostic only — **not** a gate; no \(\theta\)-loosening.
4. `oracle_with_slop` is a distinct DGP path (higher \(\beta(m_{\mathrm{slop}})\)); FA still 0.
5. Mini battery (5 seeds × 4 scenarios) is **sufficient for v1.0 first-principles confidence**, not a paper Monte Carlo freeze.

**Follow-ups:**
- M9 minimal CI only after this green exit.
- Do not tag `v1.0.0` from this chat; sibling release chat evaluates candidates.
- Do not import museum; do not move tag `v0.1`.

---

## 2026-08-01 — Intermediate real-world audit: spam_validity (20newsgroups features)

- **branch:** `feat/realworld-spam` → merged to `main` @ `3be6367` (intermediate, not H5); branch deleted
- **proof:** `evals/realworld/spam_validity/proof_summary.json` (from `verify_audit.py`)
- **package / git:** `cvprofiles==1.0.0a1` @ `29bdea1` spine; real `run_profile` path
- **data:** sklearn `fetch_20newsgroups` train (4 cats) → n=2192 multi-measure matrix; free, offline-cached
- **construct:** incidental “spamminess / promo pressure” (domain-agnostic engine stress — **not** paper H5)
- **network:** agent-authored intermediate only — `corr_min(v_aux,0.15)` + `corr_sign(v_aux,+,0.05)`; harsh θ=0.99
- **β:** `corr_y`; no bootstrap
- **verify_audit.py exit:** **0**

| Check | Result |
|---|---|
| FA (`m_noise`, `m_topic_leak` in M*) | **0** |
| Oracle M* | `{m_lexicon, m_money_url, m_caps_buy, m_llm_full, m_short_cap}` |
| Oracle [L,U] | **[0.1873, 0.8460]** (min/max B* only) |
| Harsh empty | **True** (exit 0; HTML empty callout) |
| Cold H4 freeze core | **True** |
| Same scores_hash oracle/harsh | **True** |

**Interpretation:**
1. Package spine works on a non-toy real-text feature matrix without museum code.
2. Designed invalids excluded; designed valids retained under incidental oracle R.
3. Wide construct-identified range (~0.66 width) is a feature — measurement fragility under multi-measure spamminess ops.
4. **Not** a scientific claim about spam detection or 20newsgroups labels.
5. **Not** H5; intermediate only per user authorization.

**Follow-ups:**
- Review before any merge to `main`.
- M9 CI still open.
- Paper path still requires Augusto-authored R.

---

## 2026-08-04 — v1.1 package synthetic battery + inference diagnostics

- **proof:** `reports/summaries/v1_1_package_synth_summary.json`
- **regenerator:** `uv run python tools/v11_synth_summary.py`
- **package / generation parent:** `cvprofiles==1.1.0a1`; evidence generated against parent SHA `098e2fa` (the evidence commit records this honestly)
- **path:** package-native `run_battery` → `run_score` → `run_restrict` → `run_identify`, plus real `run_profile` inference wiring; museum PoC present and unimported
- **battery:** `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`; `n=1000`, `J=10`, seeds `0..4`, `δ=0`, SCORE policy `none`, β=`corr_y`
- **network:** eval-only oracle `R`: `corr_min(v_aux,0.35)` + `corr_sign(v_aux,+,0.10)`; harsh empty contrast; no USER empirical network
- **scope:** bootstrap and θ-grid are additive diagnostics, not sharp-PI claims; headline remains full-sample `[L,U]=min/max B*`; spam audit remains intermediate and **not H5**

| Scenario | FA | anchor in \(M^*\) | empty | H1b | H1_latent (diag) | cold | mean \(\|M^*\|\) | mean width |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `oracle_easy` | **0.000** | **1.000** | 0.000 | **1.0** | **0.0** | **1.000** | 4.00 | 0.048374 |
| `oracle_with_slop` | **0.000** | **1.000** | 0.000 | **1.0** | **0.0** | **1.000** | 4.00 | 0.048374 |
| `harsh_theta` | 0.000 | 0.000 | **1.000** | n/a | n/a | **1.000** | 0.00 | n/a |
| `all_invalid` | 0.000 | 0.000 | **1.000** | n/a | n/a | **1.000** | 0.00 | n/a |

**Inference probes (`oracle_easy`, seed 7):**

- Units-only bootstrap, `n_boot=80`: percentile band `[0.364486, 0.506321]`; 80 non-empty, 0 empty, 0 degenerate replicates; same-seed payloads identical; enabling bootstrap changes `run_id` but leaves headline `[L,U]` unchanged.
- θ-grid `λ=[0.5,1.0,2.0]`: deterministic; alternate grid changes only the diagnostic payload; `run_id` remains equal to the default; the `λ=1.0` row equals the headline (`|M*|=4`, `[L,U]=[0.419477,0.469777]`). No auto-selection or threshold loosening.
- Harsh inference contrast: headline `M*=∅`, `L=U=null`; all 40 bootstrap replicates empty, so the bootstrap band is null with an explanatory note; exit/report path remains clean.

**Interpretation:**
1. H1a/H1b/H3/H4 package gates remain green under `1.1.0a1`; H1_latent remains diagnostic only and is 0 under attenuation.
2. The inference layer adds observability without changing the construct-identified headline range or researcher-authored restrictions.
3. This is package-native synthetic evidence, not a paper Monte Carlo freeze. The existing spam audit remains version-agnostic intermediate stress evidence, not H5.

**Follow-ups:**
- Release-review chat owns any v1.1.0 tag and PyPI publication decision.
- Do not import the museum PoC, author a USER empirical network, or promote the spam stress to H5.

---

## 2026-08-04 — Provisional synthetic-only MC50 evidence table

- **protocol:** `protocol-v1-synth-provisional-mc50`; `docs/16_Paper_Protocol_Freeze.md`
- **proof:** `reports/summaries/v1_1_protocol_synth_mc50_summary.json`
- **tool:** `uv run python tools/v11_protocol_synth_mc50.py`
- **package / generation parent:** `cvprofiles==1.1.0a1`; generated against parent SHA `5bfea25` (Gate B lock); the evidence commit is separate
- **path:** package-native `run_battery` → `run_score` → `run_restrict` → `run_identify`, with real `run_profile` inference probes; museum PoC present and unimported
- **battery:** `oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`; \(n=1000\), \(J=10\), seeds `0..49`, \(\delta=0\), SCORE policy `none`, β=`corr_y`, cold check on
- **network:** eval-only oracle \(R\), with the harsh-threshold empty contrast; no USER empirical network
- **scope:** provisional synthetic-only evidence; not H5, not a paper result, and not a full paper protocol lock. The shipped `v1_1_package_synth_summary.json` with seeds `0..4` remains separate package smoke evidence.
- **H2:** folded into the H1a false-admission component for this protocol; not reported as a separate gate.

| Scenario | FA | anchor in \(M^*\) | H1b | H1_latent (diag) | empty | cold | mean \(\lvert M^*\rvert\) | mean width | invalid ever | near-miss ever |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| `oracle_easy` | **0.000** | **1.000** | **1.000** | 0.020 | 0.000 | **1.000** | 4.12 | 0.070732 | none | `m_floor` |
| `oracle_with_slop` | **0.000** | **1.000** | **1.000** | 0.020 | 0.000 | **1.000** | 4.12 | 0.070732 | none | `m_floor` |
| `harsh_theta` | 0.000 | 0.000 | n/a | n/a | **1.000** | **1.000** | 0.00 | n/a | none | none |
| `all_invalid` | 0.000 | 0.000 | n/a | n/a | **1.000** | **1.000** | 0.00 | n/a | none | none |

**Load-bearing gates:** H1a false-admission and anchor retention, H1b, H3 empty-set honesty, and H4 cold reproducibility are all green. H1_latent is diagnostic only.

**Inference diagnostics:**
- Oracle probe (fixture DGP seed 0, inference seed 7, `n_boot=80`): headline \([L,U]\) = `[0.419477, 0.469777]`; bootstrap percentile band = `[0.364486, 0.506321]`; 80 non-empty, 0 empty, 0 degenerate replicates.
- Harsh contrast: headline \(M^*=\varnothing\), \(L=U=\) `null`; all 80 bootstrap replicates empty, 0 degenerate; band is null with the explanatory all-empty note.
- θ-grid \(\lambda\in\{0.5,1.0,2.0\}\): λ=1.0 equals the headline; no auto-selection or threshold loosening.

**Interpretation:**
1. All declared load-bearing gates pass across 200 scenario-seed cells; empty \(M^*\) is handled as a clean scientific output.
2. Under the broader seed list, the near-miss `m_floor` is admitted in the oracle scenarios at least once, and mean \(\lvert M^*\rvert\) is 4.12 rather than 4.00. This is not an H1a failure because designed invalids were never admitted; it is a useful reminder that near-miss behavior is not invariant across seeds.
3. H1b=1.0 remains partly construction-invariant once the anchor survives and the headline range is defined as min/max over survivors; it should not be oversold.
4. Bootstrap and θ-grid results are additive diagnostics only; they do not replace the headline range or establish a sharp partial-identification result.

**Follow-ups:**
- Keep this synthetic-only table separate from the package smoke artifact.
- Do not promote it to H5 or a paper claim without Augusto-owned empirical inputs and a dated protocol amendment.

---

## 2026-08-04 — MC50 proof independently audited (read-only verifier)

- **tool:** `uv run python tools/verify_v11_protocol_synth_mc50.py`
- **artifact:** `reports/summaries/v1_1_protocol_synth_mc50_summary.json`
- **result:** exit 0; `{"errors": [], "passed": true, "protocol_id": "protocol-v1-synth-provisional-mc50", "scenario_seed_cells": 200}`
- **scope:** provenance/identity fields, locked settings (scenarios, seeds `0..49`, `n=1000`, `delta=0`, `beta=corr_y`), per-seed structural invariants, recomputed aggregates, gate agreement, strict JSON non-finite rejection, bootstrap count/band semantics, harsh-empty contrast, and museum hygiene.
- **note:** This is an internal consistency audit of the committed table, not empirical validation and not paper acceptance. Gate C acceptance remains an owner decision.

---

## 2026-08-04 — Intermediate real-world audit: calhousing_validity (tabular)

- **branch:** `feat/intermediate-calhousing` (review pending; not merged)
- **proof:** `evals/realworld/calhousing_validity/proof_summary.json` (from `verify_audit.py`, exit **0**)
- **package / git:** `cvprofiles==1.1.0a1`
- **data:** sklearn `fetch_california_housing` (n=20640, tabular; offline-cached after one fetch)
- **construct:** incidental "housing quality / desirability" (agent-authored; **NOT** paper H5)
- **network:** incidental oracle `corr_min(v_aux,0.15)` + `corr_sign(v_aux,+,0.05)`; harsh `corr_min` θ=0.9999 (above max sample corr ≈0.9985)
- **β:** `corr_y`; bootstrap/θ-grid off
- **menu:** 6 designed valid measures + 2 designed invalid (`m_noise`, `m_geo_dict` longitude proxy)

| Check | Result |
|---|---|
| FA (`m_noise`, `m_geo_dict` in M*) | **0** |
| Oracle M* | all 6 designed valids |
| Oracle [L,U] | **[0.1658, 0.9514]** (min/max B* only) |
| Harsh empty | **True** (exit 0; HTML empty callout) |
| Cold H4 freeze core | **True** |
| Same scores_hash oracle/harsh | **True** |
| Small-n (n=200) clean run | **True** (oracle nonempty; harsh empty) |
| NaN fail-loud | **True** (`ScoreError`: non-finite measure column) |

**Interpretation:**
1. The spine works on a non-text, skewed-feature matrix with a larger menu — domain-agnostic claim supported at package level.
2. `[L,U]` width ≈0.79 is measurement fragility, a feature not a failure.
3. **Small-n admission flips:** `m_geo_dict` (longitude proxy) is admitted at n=200 but rejected at n=20640. Sampling variation changes admission; near-miss behavior is not sample-size-invariant. Not an engine failure; pre-register sample-size posture before real evidence.
4. Missingness fails loud at SCORE — the engine does not impute; upstream cleaning is researcher-owned.
5. **Not H5 / not a paper result.** Composite measures are hand-weighted, not LLM outputs.

---

## 2026-08-04 — calhousing probe supplements (thin samples, z-score, raw skew)

Same branch and audit; `verify_audit.py` extended pre-merge with three probes
(exit **0**; all gates true).

- **Thin-sample ladder (n=200, n=50):** clean runs; harsh empty holds at both;
  admission shrinks and flips with n. n=200 admits `m_geo_dict` (longitude
  proxy) and n=50 additionally drops `m_age_pref`; both are rejected at full n.
  Range narrows with fewer survivors (n=50 → [0.768, 0.973]).
- **z-score policy:** `M*` and `[L,U]` identical to the `none` run within 1e-9.
  Normalization is identification-invariant on this matrix.
- **Raw heavy-skew variant (no log):** clean run, valid range, but `m_afford_raw`
  is rejected (corr_aux 0.057 vs θ=0.15) because raw AveOccup outliers dominate
  the aux composite. Transform choice changes admission.
- **Interpretation:** admission depends on sample size AND upstream feature
  transformation, not only on the network. Pre-register both for real evidence.
  These are capability boundaries, not engine failures.

---

## Index of scenarios (planned)

| Scenario | First expected log era |
|---|---|
| `oracle_easy` | M5–M8 |
| `oracle_with_slop` | M5–M8 |
| `harsh_theta` | M6–M8 |
| `loose_theta` | M8 |
| `wrong_network` | M8 |
| `n_small` | M8 |
| `point_id` | M5+ |
| `all_invalid` | M5–M8 |
| real baseline (H5) | M10 only, USER network |

---

## 2026-08-04 — H5 Trust: first frozen build + dev gate (country-level generalized trust)

- **run:** `evals/h5_trust/` (docs/17 design lock); dev gate `verify_audit.py` exit 0; auditor `tools/verify_h5_trust.py` exit 0, 0 errors.
- **package / git:** `1.1.0a1`; frozen inputs built from raw WVS7 + GPS country + WDI/WGI (public); generation parent SHA `cd6455d`.
- **universe:** WVS7 ∩ GPS ∩ aux coverage, floor ≥ 200 → n=35 (from 66 WVS; 7 dropped for missing Gini/GDP coverage: GTM, IND, IRQ, JOR, MAR, NIC, VEN).
- **network (pinned):** corr_min(gps_trust, 0.3) + corr_min(rule_of_law, 0.3) + corr_sign(gini, −1, 0.1); δ=0; β=corr_y on log_gdp_pc. Network hash `0dab2afa…`.
- **θ anchors:** literature-grounded (OECD 0.29 country-level survey↔behavioral; trust–institutions ≥0.4; Bjørnskov negative inequality).

| Metric | Value |
|---|---|
| FA (designed-invalids admitted) | 0 — `m_noise`, `m_share_agriculture` rejected on all three bars |
| M\* | `{m_trust_general, m_trust_in_group}` |
| Rejected (binding bars) | `m_trust_out_group` (GPS corr 0.2987 < 0.3, knife-edge), `m_trust_institution` (rule-of-law corr −0.125) |
| β on survivors | general 0.624, in_group 0.371 |
| **[L,U]** | **[0.371, 0.624]** (min/max B\* on survivors only) |
| Cold H4 | identical freeze core across two runs |
| θ-grid (λ 0.5/1.0/1.5/2.0) | 3 measures at 0.5; 2 at 1.0 (headline); **∅ at 1.5 and 2.0** |
| Bootstrap (n_boot=80, seed 0) | band [0.174, 0.752]; **17.5% empty replicates**; 0 degenerate |

**Interpretation:**
- The classic WVS generalized-trust item (Q57) is admitted and carries the largest trust–development correlation (0.624) — the SCA2 pilot's rejection (0.278 vs GPS) does **not** replicate on this frozen sample; admission flipped with sample/construction (documented fragility, cf. calhousing thin-sample lesson).
- Out-group trust is a knife-edge survivor: 0.2987 vs the 0.3 GPS bar; it enters at λ=0.5 and the headline set empties entirely at λ=1.5 — the construct-identified range is fragile to the stated threshold.
- Institutional confidence is *negatively* correlated with rule of law (−0.125): the network discriminates a distinct construct, as designed.
- Bootstrap: 1 in ~6 country resamples yields an empty admissible set — honest measurement uncertainty.

**Status (2026-08-04):** **preliminary paper-facing evidence** — owner-approved
checkpoint per docs/12 + docs/16 §8. `reports/summaries/h5_trust_evidence_summary.json`
is the tracked summary. Final paper lock and submission claims remain Augusto's.

---

## 2026-08-05 — v2.0 thread (a): δ-grid tolerance surface (H5 Trust run)

- **package / git:** `cvprofiles==1.1.0a1`; commits `11e5179`, `a44e65f`, `ab30d18` (M-a1..M-a3)
- **run:** frozen H5 inputs (`evals/h5_trust/data/*`), seed 0, δ-grid `[0, 0.005, 0.01, 0.05, 0.1, 0.25, 0.5]`; artifacts `reports/runs/h5_trust_delta_grid/` (gitignored, reproducible); run_id equals the original frozen build (grid excluded from the preimage by design); network/beta hashes `0dab2afa…` / `1959ede5…` unchanged
- **headline (declared δ=0):** M\*={m_trust_general, m_trust_in_group}, [L,U]=[0.370754, 0.623891] — **bit-identical to the first frozen build**

| δ | M\* | [L,U] |
|---|---:|---|
| 0.0 (headline) | {general, in_group} | [0.371, 0.624] |
| 0.005 | + out_group | [0.371, 0.624] |
| 0.01 / 0.05 / 0.1 / 0.25 | same 3 measures | [0.371, 0.624] |
| 0.5 | + institution, **+ m_noise** | **[−0.319, 0.624]** |

**Interpretation:**
1. **Out-group trust is knife-edge at δ=0:** its GPS slack is −0.0013 (corr 0.2987 vs the 0.3 bar); δ ≥ 0.005 admits it. The range endpoints do not move because its β sits inside the headline interval — range robustness ≠ admissible-set robustness.
2. **Tolerance discipline is load-bearing:** at δ=0.5 the designed-invalid `m_noise` is admitted and L collapses to −0.319. The construct-identified range has its stated meaning only at the declared δ; this is the engine demonstrating why "never auto-loosen δ" is a hard rule.
3. **FA stays 0 at the headline** (δ=0 unchanged); the δ-grid is a diagnostic viewport, never an alternative admission rule.

**Status:** thread (a) of v2.0 measure discipline complete (M-a1..M-a4). Diagnostic only; headline range unchanged; no paper claim added.

---

## 2026-08-05 — v2.0 thread (b): evaluator registry growth (mean_order / rank_agree / ols_coef)

- **package / git:** `cvprofiles==1.1.0a1`; commits `910ee0d`, `83cd1a7`, `15720c1` (M-b1..M-b3)
- **path:** package-native `run_identify` through the real spine; new fixtures `data/fixtures/{mean_order_v1, rank_agree_v1, ols_v1}/`; full suite **196 passed**
- **registry now implemented:** `corr_min`, `corr_sign`, `mean_order`, `rank_agree` (restrictions) + `corr_y`, `ols_coef` (β). `stability` and `diff_means` remain schema-only fail-loud (no fixture demands them).

| Evaluator | Semantics (docs/12 D3/D4/D5) | Fixture golden | Discriminator |
|---|---|---|---|
| mean_order | sign·(mean(m\|g=1) − mean(m\|g=0)) − θ; binary 0/1 group | m_high 0.30 admitted; m_low −0.26, m_slop −1.10 rejected | sign=−1 flips admission (m_slop 0.50) |
| rank_agree | Spearman ρ(m, ref) − θ; ties averaged | ok/ok2 ρ=1.0 admitted (θ=0.8); mid ρ=−0.7576, bad ρ=−1.0 rejected | ties convention pinned (ρ 0.5643) |
| ols_coef | standardized OLS β on m with controls (z ddof=0; numpy closed form) | m_conf β≈0.85227 (exact-recovery DGP); point-ID | confound adjustment: marginal corr 0.9994 > β; singular / zero-variance fail loud |

**Interpretation:**
1. The registry grows only under fixture demand; each evaluator has a hand-computed golden and a locked semantics entry before code.
2. `ols_coef` gives a unit-free, confound-adjusted β comparable across measures — the natural secondary target for the construct-identified range when `corr_y` is too coarse.
3. `mean_order` is the "known-valid subgroup" anchor: a measure must separate the validated group from the rest by at least θ, with direction.

**Status:** thread (b) of v2.0 measure discipline complete (M-b1..M-b4). Feature layer; headline semantics unchanged; no paper claim added.
