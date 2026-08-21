# Public-release hygiene audit — 2026-08-21

Sprint: `feat/public-release-hygiene` (branch), executed per the approved plan
in `.hermes/plans/2026-08-21_125348-public-release-hygiene.md`.

## Scope decisions (Augusto-approved)

| Decision | Outcome |
|---|---|
| D1 audits/ | Kept tracked (audit trail = observability thesis) |
| D2 reports/ | Split: math spec + final report + proof summaries tracked; dev plans/inventories local-only |
| D3 tools/ | Kept; dropped `convert_math_delims.py` (one-off, complete) |
| D4 docs/archive | Deleted from tracking (recoverable via `git show v3.0.2:docs/archive/<file>`) |
| D5 paper | New tracked `paper/` dir; Nature version stays in lab repo |
| D6 version | No bump from hygiene work |
| H5 | **Deleted entirely** (owner decision). Paper evidence unaffected: trust claims come from `evals/wvs_gps_two_resolution/`, not the H5 lane. Design record kept at `governance/H5_TRUST_DESIGN.md`, marked SUPERSEDED |

## Commits on the branch

1. H5 removal + reports split + convert_math_delims drop (`9e17f0e`)
2. Tutorials + CI: core notebook self-contained, all 5 notebooks verified, release.yml, py3.13 (`306712a`)
3. Paper move (`6c145e3`)
4. Docs reorg: public docs/, logs/, governance/, archive deleted (`ed81e5b`)

## Verification results

### Battery
- 338 tests passed (py3.11 and py3.13); ruff clean; mypy strict clean;
  version-consistency green at 3.0.2; math-delimiter scan green.

### Notebooks (execute-verified against the 3.0.2 checkout)
| Notebook | Result |
|---|---|
| core (now H5-free, fully self-contained) | exit 0 |
| diagnostics tour | exit 0 |
| IRT scoring | exit 0 |
| sensemakr | exit 0 |
| WVS/GPS inputs (flagship) | exit 0 |

### Wheel audit
- `uv build`: wheel contains only package code + `report.html.j2` template.
  No `__pycache__`, no tests/evals leakage. 42 files, ~193 KB uncompressed.

### Dead-code scan (vulture, advisory)
- Only hits are false positives by construction: Pydantic validators/`model_config`,
  Typer command functions, test-exercised helpers (`run_id_from_bundle`,
  `row_for`). No dead engine code found. No action taken.

### Stranger simulation (fresh clone of this branch to /tmp)
- `pip install -e .` in a fresh venv: OK
- `cvprofiles demo`: exit 0, correct M* = [m_good, m_weak], full artifact bundle written
- Own-file run via the four-file contract: exit 0, identical run_id (freeze contract stable)
- Core notebook executes from a bare clone with no extra setup: exit 0
- No "Augusto" in any public doc (only CITATION.cff author field, which is correct)
- No stale `docs/archive` references remain

## Known gaps (accepted for alpha posture)

1. **PyPI: 3.0.2 not yet published** (latest is 3.0.1). README's `pip install cvprofiles`
   quickstart therefore serves 3.0.1 until owner runs `uv build && uv publish`.
   The GitHub Release for v3.0.2 is also pending. Both close in Phase 7.
2. **AGENTS.md path-table update deferred**: file is write-protected; needs one
   interactive owner approval. Table currently points at pre-reorg paths
   (docs/12|13|16|17|18, docs/archive) — a historical-note patch is prepared.
3. No docs site (mkdocs etc.) — GitHub-rendered markdown judged adequate for alpha.
