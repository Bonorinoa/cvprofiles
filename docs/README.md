# cvprofiles docs

Documentation for the construct-validity profiles methods package. Three public docs, written from shipped state; governance/lock docs live alongside.

## Public docs

| Doc | Purpose |
|---|---|
| [`METHODOLOGY.md`](METHODOLOGY.md) | The method: menu, slacks, M\*, B\*, inference stance, registry rationale, positioning |
| [`USER_GUIDE.md`](USER_GUIDE.md) | How to prepare inputs, run a profile (CLI + API), read the report, hygiene checklists |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Four-state machine, module map, IO contracts, determinism, tech stack |
| [`ROADMAP.md`](ROADMAP.md) | Live roadmap, maintained alongside the engineering log |

Tutorials (run against the installed package, inputs generated inline):

- [`../tutorials/cvprofiles_tutorial.ipynb`](../tutorials/cvprofiles_tutorial.ipynb) — synthetic walk-through + H5 replication
- [`../tutorials/cvprofiles_diagnostics_tour.ipynb`](../tutorials/cvprofiles_diagnostics_tour.ipynb) — v2.0 measure-discipline tour

## Governance and logs (append-only / locked)

| Doc | Role |
|---|---|
| [`12_Decision_Engineering_Log.md`](12_Decision_Engineering_Log.md) | Append-only engineering/scope decisions |
| [`13_Evaluations_Log.md`](13_Evaluations_Log.md) | Evidence interpretations and artifact pointers |
| [`16_Paper_Protocol_Freeze.md`](16_Paper_Protocol_Freeze.md) | Paper-facing locks, open fields, provenance rule |
| [`17_H5_Trust_Design.md`](17_H5_Trust_Design.md) | H5 Trust design lock — **historical** (re-graded 2026-08-07) |
| [`18_IVS_Cultural_Map.md`](18_IVS_Cultural_Map.md) | v3 IVS cultural-values lane design container (Augusto-authored; run gated) |
| [`PROJECT_MANIFEST.md`](PROJECT_MANIFEST.md) | Machine-readable project state and locks |

## Archive

Pre-consolidation scaffold docs moved to [`archive/`](archive/README.md) (2026-08-06). Historical reference only; not the current documentation.

## Rules

- If a design doc and the code disagree, update the doc and the decision log in the same change. Do not silently invent architecture in implementation.
- Paper numbers come only from frozen score matrices + pinned network + fixed seed.
