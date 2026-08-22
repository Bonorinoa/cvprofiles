# paper/

Source for the methods paper targeting **methodology journals** (Psychological
Methods first): *"Measuring What We Mean: Construct Validity When Measures Are
Cheap."* The paper is the journal-facing statement of the method this package
implements — construct-identified inference as a composition of construct
validity, specification-curve multiverse analysis, and partial identification.

## Contents

| File | Contents |
|---|---|
| `position_paper.tex` | Full LaTeX source (self-contained: inline bibliography, no external figures) |
| `CLAIM_BOUNDARY_BRIEF.md` | What the paper does and does not claim; evidence provenance boundaries |
| `REVISION_CHECKLIST.md` | Open revision items |

## Build

```bash
cd paper
pdflatex position_paper.tex && pdflatex position_paper.tex   # twice for refs
```

No bibliography tool or figure assets are required. Build side-products
(`*.aux`, `*.log`, `*.out`) are gitignored; **the compiled
[`position_paper.pdf`](position_paper.pdf) is tracked** so readers can download
it without a LaTeX toolchain. Rebuild it with the command above after editing
the source.

## Numbers provenance

All empirical numbers in the paper come from frozen runs in this repository:
frozen score matrices under `evals/` (flagship: `evals/wvs_gps_two_resolution/`
and `evals/wvs_gps_preferences/`), pinned networks and β files, fixed seeds,
and the package version pin recorded in each run's freeze contract. The proof
summaries under `reports/summaries/` are the compact fingerprints of those
runs. A companion Nature-track manuscript is maintained separately in the
lab's repository.
