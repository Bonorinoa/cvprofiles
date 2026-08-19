# Reproducibility audit closeout — 2026-08-18

External audit (2026-08-16, "Fable 5") findings F1–F8 and their status at the paper-freeze tag `paper-2026-08-18`.

| Finding | Status | Closeout |
|---|---|---|
| F1 — run_id not reproducible from committed inputs (CSV float parsing) | **CLOSED** | `float_precision="round_trip"` pinned in `src/cvprofiles/score/pipeline.py`; all confirmatory runs re-frozen under the fixed parser; new run_ids committed |
| F2 — bibliography errors (self-citation, Wallach venue) | **CLOSED** (paper) | `capra2025` and `wallach2025` corrected in `position_paper_cvprofiles.tex` |
| F3 — no tag contains the paper's runs | **CLOSED** | tag `paper-2026-08-18` cut at this commit; paper cites it |
| F4 — no CITATION.cff / DOI / data statement | **CLOSED (partial)** | `CITATION.cff` added; Zenodo DOI pending deposit at acceptance; data/code-availability statement added to paper |
| F5 — golden float equality across platforms | **CLOSED** | `pytest.approx` tolerance in `test_cli_demo.py` |
| F6 — LLM-lane driver requires gitignored raw generations | **CLOSED** | `--skip-build` path consumes committed `*_llm_extension.csv` frames |
| F7 — abstract empty-R range not frozen (superseded menu) | **CLOSED** | `empty_R` re-run on the current seven-measure menu → `[-0.219, 0.565]`; recovery JSON + DESIGN.md updated with dated amendment |
| F8 — PyPI release date wording | **CLOSED** (paper) | status box and §4 note "2026-08-14 local / 2026-08-15 UTC" |

**Verification.** All 10 two-resolution profiles + MTMM special case + empty_R + partial r reproduce the paper's displayed numbers exactly (1e-5 or better); the only deltas are last-ulp float differences and new run_ids. Test suite: 369 passed, ruff/mypy clean.
