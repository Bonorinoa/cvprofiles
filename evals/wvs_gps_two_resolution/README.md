# WVS/GPS two-resolution application

**Status:** frozen 2026-08-15. v3.0.1 LLM extension under the locked
two-resolution design (`DESIGN.md`, `DESIGN_LLM_EXTENSION.md`).

Country-level (n ≈ 41) + cell-level (n = 480 sex×age cells, min cell n = 20)
patience and trust profiles built on the same human menu as
`../wvs_gps_preferences/`, with an LLM-extension menu added at both
resolutions (Llama-3.1-8B Q8_0 + Phi-4-mini Q8_0; GGUF sha256 verified).

## Files

| File | Role |
|---|---|
| `DESIGN.md` | 2026-08-14 parent design: country vs cells, freeze contract |
| `DESIGN_LLM_EXTENSION.md` | 2026-08-15 LLM-extension design: fresh LLM columns, cells as main text |
| `RESULTS.md` | 2026-08-14 country/cells results memo (human-only menu) |
| `LLM_RESULTS.md` | 2026-08-15 LLM-extension verified readout (human + LLM menu) |
| `CELL_DEMEAN_COMPARISON.md` | Cell-demeaning diagnostics |
| `application_summary.json` | Frozen application summary (human-only) |
| `demeaned_application_summary.json` | Frozen application summary (cells demeaned) |
| `llm_extension_summary.json` | Frozen LLM-extension summary |
| `betas/` | Frozen β specs (country + cells; human + LLM) |
| `networks/` | Frozen nomological networks (human + LLM columns) |
| `roles/` | Frozen role specs (measure / aux / outcome / unit) |
| `data/cells/`, `data/cells_demeaned/`, `data/country/` | Frozen score CSVs (human + LLM extension columns) |
| `data/score_manifest.json` | Frozen score-matrix manifest with hashes |
| `data/llm_raw/` | **Regenerable** raw LLM `.jsonl` outputs (gitignored) |
| `runs/` | Frozen cvprofiles run artifacts (per profile) |
| `scripts/` | Score-builder + profile-runner scripts |

## Provenance

- Human columns: 2026-08-14 freeze (`score_manifest.json`).
- LLM columns: 2026-08-15 fresh generation, GGUF sha256 verified, prompts per
  `DESIGN_LLM_EXTENSION.md`.
- Engine: `cvprofiles==3.0.1`.
- Posture (locked before slacks): restriction-stage split is headline;
  units-split is appendix-only.

## What this lane is not

Not the paper flagship. The flagship is `../wvs_gps_preferences/`. This lane
exists to (i) verify the same menu at two resolutions, (ii) extend the menu
with cheap LLM measures at both resolutions, and (iii) provide the empirical
material the v3 paper §5 §6 cite.

## Reading order

1. `DESIGN.md` — what the two-resolution exercise is.
2. `DESIGN_LLM_EXTENSION.md` — what changed 2026-08-15 and why.
3. `RESULTS.md` — human-only headline numbers.
4. `LLM_RESULTS.md` — human + LLM headline numbers.
