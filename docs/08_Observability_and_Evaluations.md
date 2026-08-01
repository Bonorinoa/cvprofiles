# 08 — Observability and Evaluations

**Status:** scaffold v0 (2026-08-01)

## Philosophy

Observability beats cleverness. Progress is read from **artifacts**, not vibes:

- slack matrices  
- admissible sets  
- ranges  
- `report.html`  
- eval log rows  

Traces of chat sessions are secondary.

## Run directory contract

Every full or partial engine run writes:

```
reports/runs/<run_id>/
  run_manifest.json      # hashes, seed, versions, config
  slacks.parquet         # if IDENTIFY reached
  admissible.json
  beta_values.json
  range.json
  bootstrap.json         # summary
  theta_grid.json        # summary
  report.html
  report.json
  report.tex             # optional until G7
  logs/
    score.jsonl
    restrict.jsonl
    identify.jsonl
    report.jsonl
```

`run_id` derives from content hashes (see architecture). Colliding ids with different outputs = critical bug.

## Structured logs

- JSON lines; one event per step with `state`, `event`, `ts`, `run_id`.  
- Errors include schema path and restriction id when relevant.  
- No emoji progress as the only record.

## Human primary surface

`report.html` must let a non-coder answer:

1. What was the construct menu?  
2. Which restrictions bit?  
3. Who is in \(M^*\) and who failed which \(r\)?  
4. What is \([L,U]\) and is the set empty?  
5. How does the range move on the \(\theta\)-grid?  

Failure aesthetics: empty \(M^*\) gets a clear panel, not a stack trace.

## Evaluation system

| Track | Location | Log |
|---|---|---|
| Synthetic battery | `evals/synthetic/` | `13_Evaluations_Log.md` + machine CSV/JSON summary (later) |
| Fixture/golden | `tests/` + `data/fixtures/` | pytest CI |
| Real baseline | frozen data path TBD | eval log + paper freeze tag |

### Four debug metrics

Defined in `04_Synthetic_DGPs.md`; every synthetic summary row includes them.

### CI bar (proposal, not frozen)

On PR: unit + contract + mini oracle (`n` small, 1–2 seeds).  
Nightly/full: broader seed grid (when CI exists).  
Do not gate CI on H5.

## Evaluations log discipline

`13_Evaluations_Log.md` is the **narrative** source of truth for what we learned. Each entry:

- date, run_id(s), scenario, git/package version (when available)  
- metrics table  
- interpretation (1–3 bullets)  
- follow-ups  

Do not dump raw bootstrap draws into the markdown log.

## What we do not build for MVP

- LangSmith / hosted trace products (optional later; not core)  
- Real-time multi-user dashboards  
- Automatic “significance stars” that overclaim set identification  

## Link to prereg

H1–H4 success/fail is declared from eval log + frozen metrics, not from cherry-picked HTML screenshots.
