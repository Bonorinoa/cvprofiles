# cvprofiles docs

Documentation for the construct-validity profiles methods package. This
directory holds the **public documentation only**, written from the shipped
state of the package.

## Public docs

| Doc | Purpose |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The method: menu, slacks, M\*, B\*, inference stance, registry rationale, positioning |
| [`USER_GUIDE.md`](USER_GUIDE.md) | How to prepare inputs, run a profile (CLI + API), read the report, hygiene checklists |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Four-state machine, module map, IO contracts, determinism, tech stack |
| [`ROADMAP.md`](ROADMAP.md) | Live roadmap |

## Tutorials

Run against the installed package; inputs generated inline (the flagship
input-builder uses frozen files from this checkout):

| Tutorial | What it covers |
|---|---|
| [`../tutorials/cvprofiles_tutorial.ipynb`](../tutorials/cvprofiles_tutorial.ipynb) | **Core.** Synthetic walk-through + empty-set contrast; fully self-contained (pip install is enough) |
| [`../tutorials/cvprofiles_diagnostics_tour.ipynb`](../tutorials/cvprofiles_diagnostics_tour.ipynb) | Measure-discipline tour: all evaluators + diagnostics |
| [`../tutorials/cvprofiles_irt_scoring_tutorial.ipynb`](../tutorials/cvprofiles_irt_scoring_tutorial.ipynb) | IRT as a SCORE-upstream scoring technology |
| [`../tutorials/cvprofiles_sensemakr_tutorial.ipynb`](../tutorials/cvprofiles_sensemakr_tutorial.ipynb) | OVB sensitivity (Cinelli–Hazlett) on a survivor |
| [`../tutorials/cvprofiles_wvs_gps_inputs.ipynb`](../tutorials/cvprofiles_wvs_gps_inputs.ipynb) | **Flagship inputs.** WVS/GPS patience input-builder + E2E |

## Elsewhere in the repository

- **[`logs/`](../logs/)** — append-only engineering/decision and evaluations logs.
  Internal working documents, kept public for auditability: they record how each
  scope and evidence decision was made and reversed over the project's life.
  Frozen through v3.0.2; new entries are appended below the relocation note at
  the top of each file.
- **[`governance/`](../governance/)** — project-state locks: paper protocol
  freeze, historical design containers, and the machine-readable project
  manifest. Also internal by design and labeled as such.
- **[`paper/`](../paper/)** — LaTeX source for the methods paper.
- **[`audits/`](../audits/)** — dated audit reports with findings and closure status.

## Rules

- If a design doc and the code disagree, update the doc and the decision log in
  the same change. Do not silently invent architecture in implementation.
- Paper numbers come only from frozen score matrices + pinned network + fixed seed.
