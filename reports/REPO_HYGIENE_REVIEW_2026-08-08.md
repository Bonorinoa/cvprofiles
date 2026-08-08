# Repo Hygiene Review — 2026-08-08

**Purpose:** holistic pre-release review of cvprofiles as a *scientific tool package* (per Augusto's request): tracked-vs-ignored discipline, doc tiering (public vs internal), source schema/bloat, README honesty. Measurements taken from the working tree on 2026-08-08; no destructive changes made — recommendations only.

## 1. Tracked vs ignored — verdict: **excellent discipline, minor trims**

The repo already follows the "commit evidence, ignore bulk outputs" contract correctly:

| Area | Tracked | Ignored (correct) |
|---|---|---|
| `data/` | fixtures only (84K — needed for tests/CI/tutorials) | `synthetic/generated/`, `h5_trust_raw/`, `h5_trust_aux/` (4.1M on disk) |
| `reports/` | allow-listed proof summaries (6 JSON + README) + 5 planning docs | `reports/runs/*` (bulk per-seed dumps) |
| `evals/` | h5_trust data/manifests/proofs, realworld data/proofs, `verify_audit.py` | `runs_verify/`, `runs_*/`, `*.parquet` |
| `audits/` | one post-release audit (2026-08-06) | — |

**Recommendations (low priority, non-blocking):**
1. `tools/convert_math_delims.py` is a one-shot conversion utility with **zero references** (only `scan_math_delims.py` is CI-wired). Remove it or move to `docs/archive/`-style scratch. `scan_math_delims.py` stays (CI uses it).
2. `reports/FINAL_ENGINEERING_REPORT.md` and `reports/cvprofiles_scan.md` are session working docs. They are honest and harmless on GitHub (hatchling ships only `src/`, so they never reach PyPI). Keep them, but they are **internal**, not referenced from README.
3. `audits/2026-08-06_post_release_audit.md` has mode `-rw-------`. Git does not reliably carry Unix perms; if you want it private-by-convention, note it in `AGENTS.md`, don't rely on chmod.

## 2. Documentation tiering — **all 26 docs have a role; split is clear**

| Tier | Docs | Notes |
|---|---|---|
| **Public** (PyPI/GitHub consumers) | `README.md`, `docs/METHODOLOGY.md`, `docs/USER_GUIDE.md`, `docs/ARCHITECTURE.md`, `docs/ROADMAP.md`, `docs/README.md`, 4 tutorials + README, `CHANGELOG.md`, `LICENSE` | Researcher voice; no local paths, no Hermes-profile rows (already compliant) |
| **Internal governance** (keep in repo, not for consumers) | `docs/12` (append-only decisions), `docs/13` (eval log), `docs/16` (paper protocol), `docs/17` (H5 design, historical), `docs/18` (IVS design), `docs/PROJECT_MANIFEST.md`, `AGENTS.md`, `reports/DEVELOPMENT_PLAN.md`, `reports/VERIFIED_TASK_INVENTORY.md`, `reports/math_spec.md` | These are the audit trail; do not delete |
| **Historical archive** | `docs/archive/` (15 docs) | Already marked historical; keep for provenance, cheap |

**Answer:** yes, we need essentially all docs — they are either public-facing or the governance trail. No doc is dead weight. The one hygiene item is the one-shot tool (#1 above), not the docs.

## 3. Source schema — **clean; 3,569 LOC, no bloat**

State-machine layout is exactly right and auditable:

```
score/ restrict/ identify/ report/   ← the four states
inference/ (bootstrap, delta_grid, theta_grid)   ← additive diagnostics
anchors/ (pre-data θ audit)
schemas/ (scores, network, beta, run)
synth/ (DGP, oracle, battery, metrics)  ← synthetic harness
freeze.py, pipeline.py, cli.py
```

- CI enforces: ruff, mypy strict, import-graph hygiene (no openai/anthropic/httpx/requests/litellm in `src/`), museum PoC present but unimported.
- **One structural question (low priority):** `src/cvprofiles/synth/` ships in the wheel (hatchling includes all of `src/cvprofiles`). It is test-support code. Either (a) accept it as documented synthetic-DGP harness (current stance), or (b) rename to `cvprofiles/_synth`/private submodule. No action required for a methods package; note only.
- No orphan modules, no duplicated logic, no dead code found in `src/`.

## 4. README — **honest and useful; two enhancements**

The README is already strong: install-first, real quickstart against `data/fixtures/mini_v1/`, machine-JSON example, "what it is / is not", reproducibility contracts, positioning table, doc map, Hermes acknowledgment, MIT. Status row is honest ("protocol provisional synthetic-only; H5 re-graded; v3 lane run-gated").

**Suggested enhancements (for the replication-evidence step, pending Gate B):**
1. Split the Status row into **Package status** vs **Protocol/evidence status** so a consumer reading "protocol provisional synthetic-only" isn't confused with the package being alpha.
2. Add a **Replication section** once the IVS-shaped tutorial runs end-to-end: a deterministic, synthetic cultural-values walkthrough (clearly labeled synthetic) plus a link to the data-acquisition runbook. Real-data IVS numbers remain **Gate B gated** — they must NOT appear as README headline evidence until Augusto's run decision (docs/16 §9, docs/18).

## 5. T32 data acquisition (started same day)

- Item-code verification of the 10 PROVISIONAL IW codes (A008, A165, E018, E025, F063, F118, F120, G006, Y002, Y003) against a real dictionary — **first step**.
- Joint EVS/WVS 2017–2022 v5.0 acquisition (free/no-registration per plan) with provenance manifest; raw files stay out of git.
- `evals/ivs_cultural/` scaffold + synthetic IVS-shaped slice (5–8 pseudo-countries) for the T22 replication tutorial.

## Status

Review complete. No destructive changes made. Commit this artifact + T32 outputs as they land; push requires an explicit go (AGENTS.md rule 6).
