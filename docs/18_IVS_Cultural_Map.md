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

- **Joint EVS/WVS 2017–2022 v5.0** (ZA7505; 92 countries / 102 surveys = 36 EVS + 66 WVS with 10 dual-wave countries; 156,658 cases; 231 variables; GESIS doi:10.4232/1.14320; WVSA doi:10.14281/18241.26). Raw files stay out of git (gitignored + sha256 manifest); only derived scores enter the repo; publication license for derived scores checked at Gate B (T32).
- WVS7 (SCA2 read-authorized) is the upstream analog and uses **Q\*** item codes, **not** the Joint Common Dictionary `A/E/F/G/Y*` codes — standalone WVS7 cannot verify Tao item codes. Standalone EVS ZA7500 is GESIS-registration-gated — use the Joint file.
- **Access note (2026-08-08):** WVSA page claims free / no registration; GESIS mirror requires login. Automated download of the full microdata was **not completed** this session (JS/form download endpoint). Full-file sha256 + derived-score publication license remain open at T32.

### T32 item-code verification (2026-08-08) — dictionary only

**Source:** Joint EVS/WVS v5.0 Variable Report / Codebook (public GESIS access PDF, 382 pp; labels extracted 2026-08-08). **Not** the full microdata file.

| Code | Joint Variable Report label | Status |
|---|---|---|
| A008 | Feeling of happiness | **VERIFIED** |
| A165 | Most people can be trusted | **VERIFIED** |
| E018 | Future changes: Greater respect for authority | **VERIFIED** |
| E025 | Political action: signing a petition | **VERIFIED** |
| F063 | How important is God in your life | **VERIFIED** |
| F118 | Justifiable: Homosexuality | **VERIFIED** |
| F120 | Justifiable: Abortion | **VERIFIED** |
| G006 | How proud of nationality | **VERIFIED** |
| Y002 | Post-Materialist index 4-item (constructed from E003, E004) | **VERIFIED** |
| Y003 | — | **NOT IN JOINT DICTIONARY** |

**Y003 finding:** In standalone WVS7 codebook, Y003 is the **Autonomy Index** (constructed from Q8/Q14/Q15/Q17). The Joint Common Dictionary lists **only Y002** among `Y###` codes — Y003 does not appear. Treat the Tao et al. §4.1 list of "10 items including Y003" as **provisionally discrepant** until Augusto's T21 transcription audit decides whether Y003 was (a) a paper-side slip, (b) a WVS-only construct not carried into the Joint file, or (c) replaced by another Common Core item.

**Stance:** 9/10 codes dictionary-verified; the set is **no longer "all 10 unexamined"**. Full T32 exit (raw file presence + sha256 + license note + T22 mirror on verified codes) remains **open** until microdata lands. Y003 + loadings PC2′ stay **hard Gate B** items.

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
| 2026-08-08 | T32 dictionary verification (Variable Report only): 9/10 IW codes verified; Y003 absent from Joint Common Dictionary (WVS7-only Autonomy Index); full microdata download deferred; access-path note recorded |
