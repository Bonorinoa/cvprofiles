# Synthetic v3 gate specification (P1 freeze)

**Date:** 2026-08-08  
**Authority:** `reports/DEVELOPMENT_PLAN_v3_REV3.md` (accepted)  
**Status:** LOCKED for P1–P5. Gate IDs and acceptance rules are frozen; implementation may add fixtures but must not rename gates without a docs/12 entry.

## Principles

1. Labels and designed truth stay **outside** IDENTIFY (existing synth rule).
2. Every new WP lands with a named gate; missing evaluator/β ⇒ fail loud or explicit skip note — **never silent pass**.
3. Existing scenarios (`oracle_easy`, `oracle_with_slop`, `harsh_theta`, `all_invalid`) remain regression; v3 adds focused fixtures, not a forced rewrite of the v1 battery.
4. Package version stays `2.0.1a1` through P5.

## Existing regression (unchanged)

| Scenario | Gates (existing battery) |
|---|---|
| `oracle_easy` | H1a FA=0, anchor retention, H1b, cold H4 |
| `oracle_with_slop` | same |
| `harsh_theta` | empty honesty |
| `all_invalid` | empty honesty |

## New fixtures / gates (P2–P5)

| Gate id | WP | Fixture / scenario | Acceptance |
|---|---|---|---|
| `H_disc` | P2 | `discriminant_v1` fixture | Valid survives `corr_min` + `corr_zero`; discriminant-invalid rejected by `corr_zero` |
| `H_mono` | P2 | `monotone_rank_v1` fixture | Monotone measure admitted; anti-monotone rejected |
| `H_beta_dm` | P3 | `diff_means_v1` fixture | `diff_means` β matches hand golden; group fail-loud if not 0/1 |
| `H_beta_map` | P3 | `map_distance_v1` fixture | `map_distance` matches hand golden; loadings shape fail-loud; loadings affect beta_hash |
| `H_holdout_stage` | P4 | network with `stage: holdout` | Admission uses select-only; holdout verdict is finding (exit 0); back-compat default `stage=select` |
| `H_holdout_units` | P4 | units-split config | `M_star_robust = select ∩ holdout`; headline [L,U] on robust; empty robust = success |
| `H_holdout_reject` | P4 | designed select-pass / holdout-fail measure | Holdout verdict fails that measure; not an exception |
| `H_cov_payload` | P5 | bootstrap + coverage on | Coverage block present; empty_rate ∈ [0,1]; **headline L,U == min/max B\*** unchanged |
| `H_cov_preimage` | P5 | same bundle ± coverage | run_id identical (coverage not in freeze preimage) |

## Semantics locks (implement as-is)

### Holdout (P4)

- `RestrictionSpec.stage ∈ {select, holdout}`, default `select`.
- Admit on \(R_{\mathrm{select}}\) only; compute slacks for all restrictions.
- Units-split: holdout unit list in freeze **`config.holdout_units`** (JSON list of unit_id strings). Absent ⇒ no units-split.
- Sets: `M_star_select`, holdout compliance on holdout units, `M_star_robust = intersection`.
- Headline \([L,U]\) from β on \(M^*_{\mathrm{robust}}\) when units-split or holdout stages present; otherwise legacy full-menu select admission (identical to v2).
- Bootstrap (v1 lock): units bootstrap resamples rows and recomputes admission + β on the resampled frame; **holdout unit list is fixed in config** (not re-drawn). Holdout verdict remains a full-sample point audit unless later amended.

### Coverage (P5)

- Additive uncertainty band from bootstrap L/U samples at α/2 (default α=0.10).
- Report empty_rate, optional boundary flags (margin ≤ κ·SE, κ=2).
- Language: **uncertainty band**, never CI / coverage guarantee.
- Not in freeze preimage.

### Evaluators / betas

| Type | Slack / definition |
|---|---|
| `corr_zero` | \(θ - \|Corr(m,V)\|\) |
| `monotone_rank` | \(sign · Spearman(m, V_{cont}) - θ\) |
| `diff_means` | \(sign · (E[m\|G=1] - E[m\|G=0])\) (sign default +1; group binary 0/1) |
| `map_distance` | \(\|Ẑ(m) - z^{target}\|_2\); loadings pinned in beta params; no PCA |

### Deferred

- `stability` evaluator (schema-only)
- MTMM panel
- P6 harness / real IVS
- Version bump to 3.0.0

## Battery versioning

- Keep `BATTERY_VERSION = "v1_0_package_synth"` for the existing four-scenario runner until a dedicated v3 summary tool is authorized (P6/P7).
- New fixtures are **unit/integration tests** under `tests/` + `data/fixtures/*_v1/`; they are the control plane for P2–P5 merges.
