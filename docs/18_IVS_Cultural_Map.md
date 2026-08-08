# 18 — IVS Cultural Map: v3 empirical lane design (skeleton)

**Status:** `RESERVED — IVS DESIGN; run gated` (created 2026-08-07, Gate A bundle). This document is the **design container** for the v3 empirical lane: a Tao et al. (2024)-style evaluation of LLM cultural alignment on the Joint EVS/WVS 2017–2022 dataset, with Inglehart–Welzel axes as the target.

**Design authorship: Augusto-owned** (AGENTS.md:37 — agents never author empirical networks). All researcher-authored fields below remain **AWAITING AUGUSTO**. The agent's role is scaffolding only: this skeleton, the design template, schema smoke, and the data-acquisition runbook.

## Authority and bounds

- Opened by `docs/16` §9 (dated amendment 2026-08-07) — the **IVS designated-evaluation box**.
- Supersedes H5 Trust as the v3 headline (H5 stays a historical design, `docs/17`).
- **Open-weight policy:** all evidence-generating computation uses open-weight local models and fully interpretable artifacts; no proprietary APIs, no DPO adapters (T27/T31 NOT reopened).
- **Loadings provenance:** Tao et al. published human PCA loadings reused verbatim (incl. PC2′ = 1.61·PC2 − 0.01, **PROVISIONAL — verify at T21 transcription audit, hard Gate B item**); fresh empirical PCA fit NOT authorized (D3).
- **Preimage carve-out:** `map_distance` β-registry extension changes `beta_hash` by design inside the v3 major bump (D3).

## Data

- **Joint EVS/WVS 2017–2022 v5.0** (92 countries = 36 EVS + 66 WVS; free, no registration). Raw files stay out of git (gitignored + sha256 manifest); only derived scores enter the repo; publication license for derived scores checked at Gate B (T32).
- WVS7 (SCA2 read-authorized) is the upstream analog; standalone EVS ZA7500 is GESIS-registration-gated — use the Joint file.
- The 10 Inglehart–Welzel item codes (A008, A165, E018, E025, F063, F118, F120, G006, Y002, Y003) are **PROVISIONAL** (from Tao et al. §4.1); dictionary verification against the actual Joint file is a hard Gate B exit item (T32/T33).

## Fields Augusto will author (AWAITING AUGUSTO)

| Field | Status |
|---|---|
| Construct definition + unit/universe (country-level IW map placement) | AWAITING AUGUSTO |
| Score matrix + measurement menu (items, model families under open-weight policy) | AWAITING AUGUSTO |
| Nomological network `R` (restrictions, directions, anchors) | AWAITING AUGUSTO |
| θ anchors + δ tolerance policy | AWAITING AUGUSTO |
| β choice (`map_distance` per D3; targets/benchmarks) | AWAITING AUGUSTO |
| Stage split + holdout countries (country-level units-split core, D7) | AWAITING AUGUSTO |
| Positive-control item selection (known-valid items admissible) | AWAITING AUGUSTO |
| Item-code + loadings transcription sign-off | AWAITING AUGUSTO |

## Scaffolding (agent-executable, post-Gate A)

- T21 — design-doc template, schema smoke on synthetic IVS-shaped scores, data-acquisition runbook (inventory row T21).
- T22 — teaching walkthrough notebook on a synthetic IVS-shaped slice (5–8 pseudo-countries); informs the design authorship.
- T30 — upstream score-generation harness in `evals/ivs_cultural/` (open-weight prompt baselines; leakage audit; snapshot pinning). **No LLM client in `src/` import graph.**
- T33 — independent auditor `tools/verify_ivs_cultural.py` (strict JSON, FA=0, freeze-core equality, loadings/item-code verification).

## Run gate (Gate B)

No run, no paper number, no `docs/13` claim until: frozen scores + pinned network/β (incl. frozen loadings) + fixed seed + package version; independent audit exit 0; **Augusto's explicit run decision**. Paper-lock checkpoint mirrors the H5 n=35 flow (`docs/16` §8/§9, `docs/16:133`).

## Change log

| Date | Change |
|---|---|
| 2026-08-07 | Created as skeleton (Gate A bundle, `docs/16` §9); design fields reserved for Augusto |
