# H5 Trust evaluation — country-level generalized trust (docs/17)

**STATUS: FIRST FROZEN BUILD COMPLETE (2026-08-04) — dev gate + auditor exit 0.
NOT YET A PAPER CLAIM.** The construct, unit/universe, menu, network, θ, δ, β,
and claims boundary are locked in `docs/17_H5_Trust_Design.md`. Frozen inputs
(`data/scores.csv`, `score_manifest.json`, `proof_summary.json`) are committed.
First run: n=35 countries, M\* = {m_trust_general, m_trust_in_group},
[L,U] = [0.371, 0.624]; FA=0; θ-grid empties at λ≥1.5; bootstrap band
[0.174, 0.752] with 17.5% empty replicates (see `docs/13`). Paper-facing use
still requires Augusto's run decision (docs/16 §8).

## What this is

The SCORE stage of the first paper-facing (H5) empirical test: country-level
generalized trust measured through a menu of WVS Wave 7 facets, disciplined by
a nomological network anchored on the GPS behavioral trust item, institutional
quality (WGI), and income inequality (negative bar). Designed-invalid measures
(`m_noise`, `m_share_agriculture`) exist to exercise the false-admission
gate. Independent of the SCA2 validity lane: this builds from raw survey
files + public economic data, with its own freeze hashing.

## Files

| File | Role |
|---|---|
| `build_dataset.py` | raw files → `data/scores.csv` + `data/score_manifest.json` (freeze hash, universe counts) |
| `verify_audit.py` | dev gate: runs the installed pipeline, checks FA=0 / cold H4 / artifacts / empty-honesty, writes `proof_summary.json` |
| `data/roles_h5_trust.json` | design-locked menu/aux/outcome roles (docs/17) |
| `data/network_h5_trust.yaml` | pinned network (docs/17) |
| `data/beta_h5_trust.yaml` | β = `corr_y` on `log_gdp_pc` (docs/17) |
| `data/scores.csv`, `score_manifest.json` | **frozen inputs — produced by the builder, committed once built** |

## Reproduce (needs raw data + aux caches)

```bash
# 1. Raw survey files (WVS_wave7.dta, GPS country .dta). Either copy them under
#    data/h5_trust_raw/ (gitignored) or point --raw-root at the source folder.
# 2. Auxiliary caches under data/h5_trust_aux/ (gitignored):
#    - wdi.csv: World Bank WDI (NY.GDP.PCAP.PP.KD, SI.POV.GINI, SL.AGR.EMPL.ZS),
#      columns iso3,year,gdp_pc_ppp,gini,agri_empl — fetch with:
#        uv run python evals/h5_trust/build_dataset.py --fetch-wdi --aux-dir data/h5_trust_aux
#    - wgi.csv: World Bank WGI rule_of_law (`rl`), columns iso3,year,rule_of_law
#      (fetch with --fetch-wgi; WGI is a workbook download, not an API)
# 3. Build + gate + audit:
uv run python evals/h5_trust/build_dataset.py --raw-root <raw> --aux-dir data/h5_trust_aux
uv run python evals/h5_trust/verify_audit.py            # exit 0 required
uv run python tools/verify_h5_trust.py --proof evals/h5_trust/proof_summary.json \
    --roles evals/h5_trust/data/roles_h5_trust.json --out-root evals/h5_trust/runs_verify/default
```

Tests (no network, no raw data): `uv run pytest -q tests/test_h5_trust_build.py tests/test_h5_trust_verify.py tests/test_h5_trust_engine_smoke.py`

## Gates (verify_audit.py)

| Gate | Expectation |
|---|---|
| FA | `m_noise`, `m_share_agriculture` ∉ M\* |
| Cold H4 | freeze core identical across two runs |
| Artifacts | report/admissible/range/slacks/manifests present |
| Empty-honesty | empty M\* → L/U null, exit 0 |

## Capability boundaries (read before citing)

- The engine is score-agnostic and model-free; it does not call LLMs, impute
  missing values, or make causal claims.
- Survey means are unweighted by design (weighted as a diagnostic contrast);
  WVS negative codes and AB 88/98 are masked in the builder.
- The AmericasBarometer lane is a 2-country probe only (appendix), per its own
  dataset guide; it is not part of the main country-level table.
- Admission is a sample-dependent statement (n≈40; pre-registered floor ≥200).
- This scaffold is **not** a paper result; `docs/16` amendment authorizes the
  *design*, and runs remain gated on frozen inputs + audit + Augusto's decision.

## Provenance

Raw surveys: WVS Wave 7 (Haerpfer et al., JD Systems Institute & WVSA); GPS
(Falk et al. 2018, *QJE*); AmericasBarometer (LAPOP, Vanderbilt). Auxiliaries:
World Bank WDI/WGI. The SCA2 lab folder shares the same underlying surveys;
this build is independent and records SCA2 only as data provenance.
