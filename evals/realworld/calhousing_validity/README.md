# California housing — intermediate real-world audit

**STATUS: INTERMEDIATE / NOT MAIN PATH / NOT H5 / NOT A PAPER RESULT**

## What this is

A domain-agnostic stress of the installable `cvprofiles` spine on a **tabular**
public dataset (California housing, `sklearn.datasets.fetch_california_housing`,
20,640 units). The previous intermediate audit (`spam_validity`) was text-only;
this one tests the engine's score-agnostic claim on non-text, skewed features
and a larger menu.

The construct **"housing quality / desirability"** and the network `R` are
**agent-authored and incidental** — they exist only to stress the engine and
are explicitly **not** a scientific claim about housing markets. Augusto owns
all paper-facing empirical constructs and networks.

## Measures (designed roles)

| Role | Measure | Operationalization |
|---|---|---|
| valid | `m_afford` | income proxy (MedInc) |
| valid | `m_space` | log size proxy (AveRooms) |
| valid | `m_uncrowded` | low-occupancy proxy (−log1p AveOccup) |
| valid | `m_spacious_uncrowded` | hand composite of size + uncrowded |
| valid | `m_age_pref` | newer-home preference proxy (−HouseAge) |
| valid | `m_composite_quality` | hand-weighted "AI-style" composite (income+size+uncrowded) — **not an LLM output** |
| invalid | `m_noise` | pure noise |
| invalid | `m_geo_dict` | longitude-only geo proxy; dictionary-privileged, fails the quality-based R |

Aux: `v_aux` = size + uncrowdedness signal (clean, not the outcome drivers only).
Outcome: `y` = noisy latent (income + size + uncrowded + noise). β = `corr_y`.

Network (incidental, agent-authored): `corr_min(v_aux, 0.15)` +
`corr_sign(v_aux, +, 0.05)`; harsh contrast `corr_min(v_aux, 0.99)`.

## Verified gates (`verify_audit.py`)

- FA = 0: designed invalids never enter `M*`
- designed valids ⊆ `M*` under the oracle network
- `[L,U]` finite with L ≤ U (min/max B* on survivors only)
- harsh network → empty `M*`, exit 0, first-class empty report callout
- cold H4: freeze core identical across two runs
- `scores_hash` identical for oracle vs harsh (same scores)
- artifact presence (report/admissible/range/slacks/manifests)

## Capability probes (new in this audit)

- **Small-n run (n=200):** engine completes cleanly; oracle nonempty, harsh
  empty; range finite. Documents behavior under thin samples.
- **Fail-loud missingness:** `run_score` rejects a NaN in a measure column with
  `ScoreError` — the engine does **not** impute; upstream cleaning is the
  researcher's job.

## Capability boundaries (read before citing this audit)

- The engine is score-agnostic and model-free; it **does not** call LLMs,
  impute missing values, or make causal claims.
- Composite measures here are hand-weighted labels, **not** real AI/LLM scores.
- Wide `[L,U]` is measurement fragility, not a product failure.
- **Small-n admission can flip:** `m_geo_dict` is rejected at n=20640 but
  admitted at n=200. Admission is a sample-dependent statement; pre-register
  sample-size posture before using real evidence.
- This audit is package confidence only: **not** H5, **not** external validity,
  **not** a paper result. Do not promote it.

## Reproduce

```bash
uv run python evals/realworld/calhousing_validity/build_dataset.py   # fetches California housing once (~2 MB), then cached
uv run python evals/realworld/calhousing_validity/verify_audit.py    # exit 0 only if all gates hold
```

Bulk run dumps live under `runs_verify/` (gitignored); `proof_summary.json` is committed.
