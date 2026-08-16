# DECISION: Public-surface sprint (personal-network readiness)

**Date:** 2026-08-16
**Status:** Draft, for founder review
**Author:** Hermes (cvprofiles collaborator)
**Sprint window:** one focused session after founder "go"
**Reference:** independent audit memo 2026-08-16 (Downloads) + local tree check on `main` @ `be19d41`

**Acceptance for sprint close:** a stranger can `pip install` the branch (editable or a 3.0.2 wheel), run one command, get a real \(M^*\) / \([L,U]\), and not be told that H5 Trust is the live flagship.

## Context

v3.0.1 is released. The engine, freeze contract, empty-\(M^*\) honesty, and scientific non-goals are not the bottleneck. The next move is public-facing: personal network first, socials after.

An independent audit correctly said the limiting factor is first-run friction, then proposed a punch list that overstates README archaeology and understates two real bugs on `main` today:

1. README Quickstart points at `data/fixtures/mini_v1/`, which is **repo-only**. The wheel packages `src/cvprofiles` only. `pip install cvprofiles` + paste-the-README fails.
2. `docs/README.md` / root README advertise the core notebook as synthetic + **WVS/GPS flagship**. `tutorials/README.md` and `tutorials/cvprofiles_tutorial.ipynb` still sell Part 2 as **H5 Trust** and pin a verify recipe to `cvprofiles==2.0.0`. H5 was re-graded historical on 2026-08-07 (`docs/16` §9/§11).

Founder chose cut **B**: demo command + README cold-start + tutorial honesty. Not a new notebook. Not a vibe-coder path. Not engine expansion.

## Decision

### This is a surface-honesty sprint, not an engine sprint.

Three commits, in order. No restriction types, no β, no inference, no sixth notebook.

### Work (in order)

1. **`cvprofiles demo`**
   - **Goal:** After install, one command writes the four-file contract and runs a profile.
   - **Design lock:** Emit the existing `mini_v1` four files (scores/roles/network/beta) into `--out` (default `./cvprofiles_demo/`), then call the same `run_profile` path as `cvprofiles run`. Do **not** invent a second teaching DGP. Do **not** add `python -m cvprofiles.demo`.
   - **CLI contract:** stdout remains one JSON summary (same shape as `run`). Teaching crumbs (what \(M^*\) means, which measures failed and why, empty \(M^*\) is a finding) go to **stderr**.
   - **Acceptance:** hermetic test: files land, `run_id` / piece hashes match `data/fixtures/mini_v1/expected_freeze.json`, rejected map names `m_slop`, exit 0. Fresh venv path does not need the repo tree.
   - **Risk:** low. Reuses golden fixture + existing Typer app.
   - **Owner:** coding agent, then Hermes review.

2. **README first-screen**
   - **Goal:** Cold reader hits purpose → `pip install` → `cvprofiles demo` → four-file table → what the numbers mean, without H5/IVS/P6 archaeology in the first screen.
   - **Constraint:** keep the version-consistency row exactly: `| **Version** | **3.0.1** | …` (`tools/check_version_consistency.py`). Move gate language / local `reports/summaries/…` paths down or out. Do not invent a new positioning essay; tighten the existing who/when table.
   - **Acceptance:** `python tools/check_version_consistency.py` exit 0; Quickstart no longer depends on a checkout.
   - **Risk:** low.
   - **Owner:** coding agent.

3. **Tutorial honesty**
   - **Goal:** Stop selling H5 as the live replication.
   - **Design lock:** Relabel markdown lead cells only. **Do not re-execute or regenerate notebooks.** Leave cell outputs. Part 2 stays in the file as a **historical** appendix; pointer to flagship = `evals/wvs_gps_preferences/` + `tutorials/cvprofiles_wvs_gps_inputs.ipynb`. Fix `tutorials/README.md` (drop `cvprofiles==2.0.0`; add audience-level labels: core / diagnostics / upstream-downstream / flagship inputs). Align `docs/README.md` tutorial blurb with that.
   - **Acceptance:** no remaining “H5 is the v3 headline / live flagship” claim in `README.md`, `docs/README.md`, `tutorials/README.md`, or the core notebook’s opening markdown cells.
   - **Risk:** low if we do not touch outputs; medium if the agent “helpfully” re-runs notebooks.
   - **Owner:** coding agent.

4. **Log close (only after 1–3)**
   - One dated `docs/12` entry. No ROADMAP rewrite beyond a one-line current-backlog note if the agent touches it at all. Prefer not touching ROADMAP this sprint.

### Deferred

- New zero-setup notebook / `python -m cvprofiles.demo`
- Vibe-coder onboarding, X/Twitter copy, positioning essay
- Engine: evaluators, β functionals, inference, empty_R follow-ons
- Rebuilding WVS/GPS or H5 notebooks
- Shipping `mini_v1` as a *silent* hidden run with no files on disk
- GitHub Release notes / PyPI 3.0.2 **until founder authorizes a version bump**
- P6 / IVS / paper freeze

## Consequences

### If accepted

- Personal-network send becomes: install this branch (or 3.0.2, if you publish) → `cvprofiles demo` → open `cvprofiles_demo/report.html`.
- PyPI 3.0.1 remains the live wheel until you explicitly bump. Colleagues on `pip install cvprofiles` will **not** see `demo` until 3.0.2.
- H5 remains in the tree as historical evidence; it stops being the teaching headline.

### If rejected

Need to know whether you want a docs-only send (cut A) or a 3.0.2 publish in the same session.

## Open questions for the founder

1. **3.0.2 publish after 1–3?** Recommended: land on `main` first, then a separate founder-gated bump. Do not mix the version bump into the three feature commits.
2. **Install instruction for this week’s emails?** Until 3.0.2: `pip install git+https://github.com/Bonorinoa/cvprofiles.git` (or a commit pin). I will not write “pip install cvprofiles && cvprofiles demo” as the public one-liner until the wheel has the command.
3. **H5 Part 2:** locked as *relabel, do not delete, do not re-run*. Amend if you want it stripped from the core notebook entirely.

## Sign-off

This decision is a draft. No commits until you say **go** (or amend). The paste-ready Codex prompt is `audits/2026-08-16_public_surface_codex_prompt.md`.

— Hermes, 2026-08-16
