# 06 — Tech Stack

**Status:** scaffold v0 (2026-08-01) — **PROPOSED defaults** for a Python methods package  
**Constraint:** paper-reproducible; no proprietary API required for engine runs.

## Non-negotiables

| Rule | Implication |
|---|---|
| Engine model-free | No LLM client inside `score/restrict/identify/report` |
| Paper path offline-capable | Frozen parquet/csv + yaml sufficient |
| Simple > clever | Std scientific Python; avoid framework soup |
| Determinism | `numpy.random.Generator` only; no global RNG |

**Phronesis stack does not apply.** No Modal, Vercel, Pipecat, Pinecone, Deepgram, voice, or RAG.

## Two-tier estimation policy (LOCKED intent)

| Layer | Allowed | Forbidden in MVP |
|---|---|---|
| **Restriction slacks** \(s_r(m)\) | Sample means, correlations, simple group gaps, Spearman | Kernels, trained ML nuisances, LLM judges |
| **Target \(\beta(m)\)** | `corr`, OLS via **statsmodels** (or thin numpy lstsq) | Deep models as \(\beta\) without explicit reopen |

This is not “numpy only forever.” It is “no learned nuisances in the validity layer.”

## Proposed stack

| Layer | Choice | Notes |
|---|---|---|
| Language | Python **≥ 3.11** | Match user toolchain; PEP 668 → **uv** venv |
| Packaging | `pyproject.toml` + **uv** | Package name `cvprofiles` (provisional) |
| Arrays / tables | **NumPy**, **pandas** | Parquet via pyarrow |
| Stats | **SciPy**; **statsmodels** for `ols_coef` | Keep OLS out of hand-rolled numerics where possible |
| Config | **PyYAML** + **Pydantic v2** schemas | Validate network/beta/score manifests |
| CLI | **Typer** | One command family per state + `run` |
| Plots (report) | **matplotlib** | Optional plotly later; static first |
| Templates | **Jinja2** | HTML + LaTeX report |
| Tests | **pytest**, pytest-cov | Contract + oracle tests |
| Lint/type | **ruff**, **mypy** | Strict on `src/` |
| Docs site (later) | mkdocs-material *optional* | Not MVP-blocking; markdown in repo is source of truth |
| CI | GitHub Actions | pytest + ruff + mini smoke on 3.11/3.12 (M9; `.github/workflows/ci.yml`) |
| Notebooks | optional Jupyter | Demos only; not engine |

## Explicitly rejected for engine core

- Cloud LLM SDKs as dependencies of the installable package  
- Heavy orchestration (Airflow, Prefect)  
- GUI frameworks  
- DuckDB/Polars *as requirement* (may revisit for large \(n\); pandas first)

## Repo layout (target)

```
cvprofiles/
  pyproject.toml
  README.md
  src/cvprofiles/
    __init__.py
    score/
    restrict/
    identify/
    report/
    synth/          # DGP + metrics (extra/optional install ok)
    cli/
  tests/
  evals/synthetic/
  data/fixtures/
  data/synthetic/
  reports/          # gitignore run outputs; keep .gitkeep
  docs/
```

## Determinism policy

- Pass `seed: int` into IDENTIFY; construct `np.random.default_rng(seed)`.  
- Bootstrap uses that generator only.  
- Parallelism: either serial MVP or worker-local RNG with explicit spawn policy (document before enabling).  
- Float tolerance \(\delta\) is config, not ambient epsilon soup.

## Dependencies philosophy

`pip install cvprofiles` (or `uv sync`) must run SCORE→REPORT on frozen scores **without** API keys. Synthetic extras may live in `[project.optional-dependencies] synth`.

## Secrets

None required for core. `.env.example` stays comment-only unless a future *optional* upstream scorer recipe needs keys (never imported by engine).
