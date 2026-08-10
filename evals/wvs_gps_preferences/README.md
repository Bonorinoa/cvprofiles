# WVS/GPS patience application: flagship public-facing empirical example (patience)

**Status:** flagship public-facing empirical example of the full knowledge-production loop (promoted 2026-08-10, `docs/16` §11, `docs/12`). Position-paper complement; evidence posture **frozen-run gated** (frozen inputs + `tools/verify_wvs_gps.py` exit 0 + Augusto's run decision). **Not** a substitute for a paper-locked estimand claim; IVS (`docs/18`) remains a separate RESERVED design container, deferred.
**Opened:** 2026-08-09, Augusto-directed (docs/12; docs/16 §10); promoted 2026-08-10 (docs/16 §11)
**Plan:** `reports/DEVELOPMENT_PLAN_WVS_GPS_APPLICATION.md`
**Engine:** installed `cvprofiles` package (`SCORE → RESTRICT → IDENTIFY → REPORT`)

## What this is

An intermediate empirical lane demonstrating the pipeline on two constructs — **patience** and **risk-taking** — using two **local** datasets:

- **GPS** — Falk et al. (2018) Global Preference Survey, country level (~80 countries; vars: `country`, `isocode`, `patience`, `risktaking`, `posrecip`, `negrecip`, `altruism`, `trust`) and individual level (~80k; same + `wgt`, `gender`, `age`, `subj_math_skills`, `region`, `language`). Files: `~/Desktop/Github_Repositories/SCA2_PofW/data/GPS/GPS_dataset_country_level/country_gps.dta` and `GPS_dataset_individual_level/individual_new.dta` (v11 variants also exist).
- **WVS Wave 7 (2017–2022)** — individual-level `.dta` at `~/Desktop/Github_Repositories/SCA2_PofW/data/WVS/WVS_wave7.dta`. Codebook-verified items: Q13 "thrift saving money and things" (patience proxy), Q14 "determination, perseverance" (persistence proxy), Q48 freedom of choice and control, 1–10 (agency proxy), Q49 life satisfaction (wellbeing outcome), Q275/Q275R education ISCED (convergent outcome/control), Q279 employment status incl. category 3 = self-employed (risk revealed-preference proxy). **WVS Wave 7 core has NO direct risk-taking item** — the risk menu leans on GPS `risktaking` + WVS self-employment + discriminant proxies. **Missing codes `-1..-5` are masked, never imputed.**

This lane is **not** paper headline evidence and **not** the v3 evidence base. The IVS cultural-values lane (`docs/18`, Gate B) remains the v3 paper headline.

## Data provenance & the risk-taking gap (record these; reviewers will probe)

- **Cross-repo data dependency.** The frozen-input build reads raw `.dta` files from inside the **SCA2_PofW** repository (paths in "What this is"; overridable via `CVPROFILES_WVS_GPS_DATA`, as in the input-builder notebook). Those files are not vendored in this lane. The frozen-input record must therefore carry provenance per source file — canonical path, content hash at freeze time, acquisition/export date, codebook version, and the exact WVS item list used — and `verify_wvs_gps.py` (the `tools/verify_h5_trust.py` pattern) must check the record against the raw files, failing loud on any drift.
- **WVS Wave 7 core has no direct risk-taking item** (codebook-verified; see "What this is"). The risk menu leans on GPS `risktaking` + the WVS self-employment proxy (Q279, category 3) + discriminant controls. Defensible as revealed-preference + behavioral-anchor triangulation, but reviewers will probe it: record the item-level rationale next to the provenance in the frozen-input record.

## Built artifacts (frozen run 2026-08-10; verifier exit 0)

- **Frozen inputs** `data/inputs/` (scores.csv n=41, roles.json, network.yaml θ=0.35, beta.yaml, score_manifest.json with sha-pinned model provenance). Raw GPS/WVS/WDI sources not vendored (cross-repo + API); provenance + hashes in the manifest.
- **Prompting harness** `run_application.py` — stages 1–5 monolith: data build → llama.cpp log-prob scoring (2 arms: Meta-Llama-3.1-8B Q8_0, Phi-4-mini 3.8B Q8_0, temperature 0, pinned GGUF sha) → pooled K=5 engine → random-selection baselines → summary writer.
- **Pooled K=5 run** `data/pool_runs/` — per-fold engine runs + `pooled_summary.json`. **Headline (posture a): `M*_select = [m_gps_patience, m_prompt_a]`, `[L,U] = [0.328, 0.402]`** — the open-weight prompt measure survives selection in all folds alongside the validated instrument. Holdout verdicts are power-limited diagnostics (per-fold n≈8; pooled-robust empty is a test-power limitation, not a construct verdict).
- **Verifier** `tools/verify_wvs_gps.py` — exit 0 on the frozen pooled run (G1 positive control, G2 noise rejected, G4 llama.cpp provenance, G5 strict JSON).
- **Allow-listed summary** `reports/summaries/wvs_gps_application_summary.json`.
- **Interactive input-builder notebook** `tutorials/cvprofiles_wvs_gps_inputs.ipynb` — teaching surface (supersedes "planned"; the frozen application now runs the monolith, not the notebook).
- **Not committed:** models/ (multi-GB GGUFs), smoke dirs, aux cache (gitignored). Frozen inputs untracked until Augusto's release decision.

## Authority note

Augusto owns construct definitions, menu, empirical network $R$, $\theta$, $\delta$, $\beta$, holdout split, and paper claims. The agent scaffolds the data build, verifier, tutorial, and oracle networks for synthetic checks ONLY. Do not cite this lane as paper evidence.
