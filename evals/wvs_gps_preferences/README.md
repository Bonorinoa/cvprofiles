# WVS/GPS preferences: intermediate demo lane (patience + risk-taking)

**Status:** intermediate demo · position-paper complement · **NOT** paper H5 · **NOT** the v3 evidence base
**Opened:** 2026-08-09, Augusto-directed (docs/12; docs/16 §10 amendment)
**Engine:** installed `cvprofiles` package (`SCORE → RESTRICT → IDENTIFY → REPORT`)

## What this is

An intermediate empirical lane demonstrating the pipeline on two constructs — **patience** and **risk-taking** — using two **local** datasets:

- **GPS** — Falk et al. (2018) Global Preference Survey, country level (~80 countries; vars: `country`, `isocode`, `patience`, `risktaking`, `posrecip`, `negrecip`, `altruism`, `trust`) and individual level (~80k; same + `wgt`, `gender`, `age`, `subj_math_skills`, `region`, `language`). Files: `~/Desktop/Github_Repositories/SCA2_PofW/data/GPS/GPS_dataset_country_level/country_gps.dta` and `GPS_dataset_individual_level/individual_new.dta` (v11 variants also exist).
- **WVS Wave 7 (2017–2022)** — individual-level `.dta` at `~/Desktop/Github_Repositories/SCA2_PofW/data/WVS/WVS_wave7.dta`. Codebook-verified items: Q13 "thrift saving money and things" (patience proxy), Q14 "determination, perseverance" (persistence proxy), Q48 freedom of choice and control, 1–10 (agency proxy), Q49 life satisfaction (wellbeing outcome), Q275/Q275R education ISCED (convergent outcome/control), Q279 employment status incl. category 3 = self-employed (risk revealed-preference proxy). **WVS Wave 7 core has NO direct risk-taking item** — the risk menu leans on GPS `risktaking` + WVS self-employment + discriminant proxies. **Missing codes `-1..-5` are masked, never imputed.**

This lane is **not** paper headline evidence and **not** the v3 evidence base. The IVS cultural-values lane (`docs/18`, Gate B) remains the v3 paper headline.

## Data provenance & the risk-taking gap (record these; reviewers will probe)

- **Cross-repo data dependency.** The frozen-input build reads raw `.dta` files from inside the **SCA2_PofW** repository (paths in "What this is"; overridable via `CVPROFILES_WVS_GPS_DATA`, as in the input-builder notebook). Those files are not vendored in this lane. The frozen-input record must therefore carry provenance per source file — canonical path, content hash at freeze time, acquisition/export date, codebook version, and the exact WVS item list used — and `verify_wvs_gps.py` (the `tools/verify_h5_trust.py` pattern) must check the record against the raw files, failing loud on any drift.
- **WVS Wave 7 core has no direct risk-taking item** (codebook-verified; see "What this is"). The risk menu leans on GPS `risktaking` + the WVS self-employment proxy (Q279, category 3) + discriminant controls. Defensible as revealed-preference + behavioral-anchor triangulation, but reviewers will probe it: record the item-level rationale next to the provenance in the frozen-input record.

## Planned artifacts (scaffold only — no data files committed yet)

- Frozen data build (GPS + WVS proxies)
- Interactive input-builder notebook: walks through authoring the four inputs (`scores.csv`, `roles.json`, `network.yaml`, `beta.yaml`) with validation, generating frozen input files (no form-based GUI)
- Two profiles: **patience** (menu = GPS `patience` + Q13 + Q14) and **risk** (menu = GPS `risktaking` + self-employment)
- Network $R$ + $\beta$ authored by Augusto (agent scaffolds + oracle synthetic checks only)
- Units-split holdout by country (the D7 falsifiable core on real data)
- `verify_wvs_gps.py` auditor (following the `tools/verify_h5_trust.py` pattern)
- E2E tutorial notebook

## Authority note

Augusto owns construct definitions, menu, empirical network $R$, $\theta$, $\delta$, $\beta$, holdout split, and paper claims. The agent scaffolds the data build, verifier, tutorial, and oracle networks for synthetic checks ONLY. Do not cite this lane as paper evidence.
