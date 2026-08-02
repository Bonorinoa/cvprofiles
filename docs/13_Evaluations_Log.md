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
