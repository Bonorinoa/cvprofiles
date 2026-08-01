# Synthetic evaluation harness

Scenario specs: `docs/04_Synthetic_DGPs.md`.  
Eval narrative: `docs/13_Evaluations_Log.md`.  
Method metrics: `docs/03_Methodology.md`, `docs/05_Pre_Registration.md`.

## Historical PoC (keep — do not import into `src/`)

| File | Role |
|---|---|
| `v0_poc.py` | **Monolith** SCORE→REPORT proof. `POC_VERSION=v0_1_poc`. Museum piece. |

### Run

```bash
# from project root
uv venv --python 3.11 .venv   # once
uv pip install --python .venv/bin/python numpy pandas
.venv/bin/python evals/synthetic/v0_poc.py
# expect: ALL GATES PASSED, exit 0
```

### Artifacts

| Path | Git |
|---|---|
| `reports/summaries/v0_1_poc_summary.json` | committed proof |
| `reports/runs/v0_1_poc_*.json` | local only (ignored) |

### v0.1 gates (locked)

- H1a: FA=0; anchor `m_dict` in \(M^*\) on oracle scenarios  
- H1b: \(\beta(\mathrm{anchor})\in[L,U]\) when anchor survives (construction invariant)  
- H1_latent: \(\mathrm{Corr}(V^*,y)\in[L,U]\) — **diagnostic only** (attenuation)  
- H3: empty \(M^*\) on `harsh_theta` and `all_invalid`  
- H4: cold independent double-run equality  
- Distinct `oracle_with_slop` vs `oracle_easy` via \(\beta(m_{\mathrm{slop}})\)  
- Near-miss fails ≥1 standard oracle restriction by design  

### Known non-goals of this file

- Bootstrap / \(\theta\)-grid  
- Package API  
- Real-data H5  
