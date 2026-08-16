# Codex prompt — public-surface sprint (cut B)

Paste the block below into Codex. Do not add engine work. Do not bump the version.

---

```text
/goal Land a 3-commit public-surface sprint for cvprofiles on the current branch.

This is a surface-honesty sprint, not an engine sprint. Do not add restriction types, beta functionals, inference layers, a sixth notebook, python -m cvprofiles.demo, or a version bump. Package version stays 3.0.1.

Read before editing:
- AGENTS.md (locks: score-agnostic engine, survivors-only range, empty M* is success, no LLM in import graph)
- README.md (current first screen; Quickstart currently points at repo-only data/fixtures/mini_v1/)
- src/cvprofiles/cli.py (Typer app; stdout = one JSON summary; human crumbs on stderr)
- src/cvprofiles/pipeline.py (run_profile, summary_dict)
- data/fixtures/mini_v1/ (scores.csv, roles.json, network.yaml, beta.yaml, expected_freeze.json)
- tests/test_cli_holdout.py (CLI test style: subprocess -m cvprofiles)
- tests/conftest.py (mini_dir fixture)
- tools/check_version_consistency.py (README Version-row regex MUST keep matching)
- tutorials/README.md and the opening markdown cells of tutorials/cvprofiles_tutorial.ipynb
- docs/README.md tutorial table
- audits/2026-08-16_public_surface_decision.md (this sprint’s locks)

Objectives (in order). One commit per objective. Do not squash.

1. feat(cli): cvprofiles demo
   Add `cvprofiles demo` to the existing Typer app in src/cvprofiles/cli.py.
   Behavior:
   - Write the four existing mini_v1 input files (scores.csv, roles.json, network.yaml, beta.yaml) into --out (default: ./cvprofiles_demo/). Copy bytes from a package-data copy of those four files shipped under src/cvprofiles/ (importlib.resources). Keep data/fixtures/mini_v1/ as the repo golden; the packaged copy must be byte-identical.
   - Then run the same run_profile path as `cvprofiles run` with seed 0, policy none, n_boot 0, no grids, no holdout, no anchors. Write report artifacts into the same --out dir (or --out/run if mixing inputs+outputs is messy — pick one and document it; prefer same dir with the four inputs + report.html).
   - stdout: exactly one JSON summary via summary_dict, same contract as `run`.
   - stderr: short teaching crumbs — M* members, rejected measures with failing restriction ids (from identify.rejected), [L,U], and one line that empty M* is a scientific finding (even though this fixture is non-empty).
   - Fail loud if --out exists and is non-empty, unless --force.
   - Do not add python -m cvprofiles.demo. Do not generate a new DGP. Do not import evals/synthetic/v0_poc.py.
   Tests (new file tests/test_cli_demo.py, same subprocess style as test_cli_holdout.py):
   - demo writes the four files and they match data/fixtures/mini_v1/ byte-for-byte (or csv/json/yaml-equivalent if you must normalize newlines — prefer exact bytes).
   - stdout JSON run_id, scores_hash, network_hash, beta_hash equal expected_freeze.json.
   - rejected includes m_slop; M* is the non-empty survivor set the fixture already produces; empty is false; exit 0.
   - running demo does not require the repo’s data/fixtures path (invoke via python -m cvprofiles from a tmp cwd).
   - --out existing non-empty without --force → exit 2, no summary JSON.
   Expected: uv run pytest tests/test_cli_demo.py -q --tb=short GREEN; existing tests/test_cli_holdout.py still GREEN.
   If freeze hashes drift, STOP. Do not “fix” expected_freeze.json. The demo must replay mini_v1, not fork it.

2. docs: README cold-start
   Reorder README.md first screen:
   - Keep the one-sentence purpose.
   - Keep the header table’s Version row EXACTLY in the shape check_version_consistency.py matches: `| **Version** | **3.0.1** | …`
   - Slim or move the Status row’s gate archaeology (H5 re-graded, IVS deferred, P6, protocol provisional) out of the first screen. Local paths like reports/summaries/… do not belong on the PyPI page.
   - Install → Quickstart becomes `cvprofiles demo` (plus a one-liner that the four files land in ./cvprofiles_demo/ and report.html is the human artifact).
   - Keep the four-file table. Keep “When to use / when not” and “What it is not.” Tighten, do not invent a new essay.
   - Immediately after the example JSON, one short “What these numbers mean” note and “Empty M* is a finding.”
   - Do not claim `pip install cvprofiles && cvprofiles demo` works on the already-published 3.0.1 wheel. Version stays 3.0.1. Phrase the quickstart as the command on this package / this checkout.
   Expected: python tools/check_version_consistency.py exits 0.

3. docs(tutorials): H5 is historical, not the live flagship
   - tutorials/README.md: Part 2 of the core notebook is a historical H5 Trust replication (re-graded 2026-08-07), not the v3 flagship. Flagship pointer = evals/wvs_gps_preferences/ and tutorials/cvprofiles_wvs_gps_inputs.ipynb. Drop the cvprofiles==2.0.0 pin; say “installed package matching this checkout.” Add audience-level labels: core / diagnostics / upstream-downstream / flagship inputs.
   - tutorials/cvprofiles_tutorial.ipynb: edit OPENING MARKDOWN CELLS ONLY. Relabel Part 2 as historical. Point at the WVS/GPS flagship. Do NOT re-execute, regenerate, or clear cell outputs. Do not edit code cells.
   - docs/README.md and root README tutorial table: same honesty. Core notebook = synthetic walk-through + historical H5 appendix; flagship inputs notebook is separate.
   Expected: grep the four surfaces above for claims that H5 is the v3 headline / live flagship — none remain. Notebook code cells and outputs unchanged (git diff on the .ipynb should be markdown-cell text only).

After each commit, run:
  uv run ruff check src tests tools
  uv run mypy src
  uv run pytest -q --tb=short
  uv run python tools/check_version_consistency.py
  uv run cvprofiles --version
  git diff --check

If any gate fails, stop and report. Do not push, tag, publish, or rewrite history.

Constraints (non-negotiable):
- Engine stays score-agnostic and model-free. No LLM client in the import graph.
- Headline range remains survivors-only [L,U]=[min B*, max B*].
- Empty M* stays a clean exit-0 success. Demo must not loosen thresholds.
- Do not bump __version__, pyproject version, or expected_freeze.json.
- Do not touch evals/, reports/summaries/, docs/16, docs/17, docs/18.
- Do not delete tools/ files.
- Public docs: no local machine paths, no Hermes-profile rows, no owner-as-primary-user tables.
- Leave tutorial cell outputs. Relabel, don’t rebuild.
- Thin implementation. No plugin system, no demo framework, no new dependencies.
- Three commits, messages as above (feat(cli) / docs / docs(tutorials)). No extra drive-by refactors.

Final response must include:
- Pass/fail per objective
- The three commit SHAs and subjects
- Exact test commands and whether they were green
- Files touched
- Confirmation that expected_freeze.json and package version are unchanged
- Anything you deferred or were tempted to “improve”
```
