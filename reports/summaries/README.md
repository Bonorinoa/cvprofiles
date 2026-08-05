# Eval proof summaries

Committed machine-readable battery summaries (small JSON).

| File | Role |
|---|---|
| `v0_1_poc_summary.json` | First green synthetic PoC gate (2026-08-01) |
| `v1_0_package_synth_summary.json` | Package-native synthetic smoke battery; seeds `0..4` |
| `v1_1_package_synth_summary.json` | v1.1 package smoke battery plus inference diagnostics; seeds `0..4` |
| `v1_1_protocol_synth_mc50_summary.json` | Provisional synthetic-only protocol table; seeds `0..49`; not H5 or a paper result |

Per-seed dumps live under `../runs/` and are gitignored.
Narrative lives in `docs/13_Evaluations_Log.md`.
