# cvprofiles

**Construct-validity profiles for cheap multi-measure AI operationalizations.**

Open, high-observability research tooling that treats construct validity as **partial identification over a menu of measurement functions**, disciplined by a researcher-authored nomological network. The engine returns an admissible measurement set M\* and a construct-identified range [L,U] for a target functional β(·). Empty sets and wide ranges are scientific features, not product failures.

| | |
|---|---|
| **Version** | **3.0.2** — reproducibility patch (2026-08-18): round-trip CSV parsing, audit F1–F8 closeout; 3.0.1 (2026-08-14) added the named `empty_R` unrestricted-multiverse special case |
| **Status** | Public methods package (Alpha). Latest tag `v3.0.2`. |
| **License** | MIT |
| **GitHub** | https://github.com/Bonorinoa/cvprofiles |
| **CI** | [![ci](https://github.com/Bonorinoa/cvprofiles/actions/workflows/ci.yml/badge.svg)](https://github.com/Bonorinoa/cvprofiles/actions/workflows/ci.yml) |

## Install

```bash
pip install cvprofiles
```

Requires Python ≥ 3.11. No GPU, no model weights, no API keys — the engine is a pure Python/numpy/pandas computation over the score columns you supply.

The published 3.0.1 wheel is the engine. The one-command demo below lives in this source tree (install the checkout).

### Install from source (this checkout)

```bash
git clone https://github.com/Bonorinoa/cvprofiles.git
cd cvprofiles
pip install -e .
```

`main` is development; version tags are the paper anchors. Clone a tag (`-b v3.0.1`) when you need a frozen paper run.

## Quickstart

```bash
cvprofiles demo
```

Writes the four-file teaching bundle into `./cvprofiles_demo/` and runs it. Open `cvprofiles_demo/report.html` for the human artifact. stdout is one JSON summary:

```json
{
  "empty": false,
  "M_star": ["m_good", "m_weak"],
  "L": 0.9908,
  "U": 0.9930,
  "scores_hash": "c20f0e67...",
  "network_hash": "3540790e...",
  "beta_hash": "d94474e8..."
}
```

**What these numbers mean.** `M*` is the admissible set — the measures that survived the researcher-authored network. `[L,U]` is the image of β on **survivors only**. Rejected measures are reported (here `m_slop` fails the aux-correlation restrictions) but never enter the range.

**Empty M\* is a finding.** If theory + data reject every candidate, the engine exits 0 and writes a clean report. That is success, not a crash. This demo fixture is non-empty so you can see a range; the empty-set contrast is in the core tutorial.

A profile is always the same four plain-text files:

| File | Contents |
|---|---|
| `scores.csv` (or `.parquet`) | One row per unit; one column per candidate measure, plus optional auxiliary/outcome columns |
| `roles.json` | Which columns are measures, auxiliaries, outcome, unit id |
| `network.yaml` | Your nomological network: restrictions with thresholds θ |
| `beta.yaml` | The target functional β(·) you want a range for |

`cvprofiles demo` emits a known-hash copy of that contract. To run your own files:

```bash
cvprofiles run \
  --scores scores.csv \
  --roles roles.json \
  --network network.yaml \
  --beta beta.yaml \
  --out my_first_profile --seed 0
```

For a fully self-contained walkthrough that builds its inputs inline, see the tutorials (below).

## What this package does

Researcher supplies unit×measure scores (**SCORE**). Researcher authors a nomological network R with thresholds θ and a target β(·) (**RESTRICT**). Engine computes sample slacks, keeps admissible measures M\*, maps survivors through β, and reports the image B\* as the range [L,U] = [min B\*, max B\*] (**IDENTIFY**). Bootstrap, the coverage uncertainty band, the θ-grid, and the δ-grid are additive diagnostics that never replace the headline range (**REPORT**). A P4b units-split holdout is not a diagnostic: when `holdout_units` is set, selection runs on train units, compliance on held-out units, and the headline becomes the robust set M\*_robust.

The engine is **score-agnostic and model-free**: it does not generate measures, does not search prompt space, and contains no learned model. LLM-based or dictionary-based scoring happens upstream, when you decide how to fill score columns.

**Model-free by design.** The engine never fits a model inside the validity layer: a p-value requires a null distribution, a Bayes factor requires priors, a likelihood ratio requires a model — all of which smuggle in distributional assumptions the engine refuses to own. It computes transparent sample moments against researcher-declared thresholds.

**Diagnostic surfaces.** θ-grid and δ-grid show how $M^*$ and $[L,U]$ move with threshold and tolerance choices — the specification-curve (Simonsohn et al. 2020) / multiverse (Steegen et al. 2016) idea applied to measurement admissibility. Descriptive by design: they reveal *where* admissibility flips; they make no inferential claim about the surface.

**Honest inference posture.** The range is a fragility audit over sample-admissible measures, not a confidence set — no coverage theorem is claimed. Bootstrap output is an uncertainty band, never a CI. The units-split holdout is the out-of-sample check: select on train units, verdict on held-out units.

## When to use cvprofiles (and when not to)

| You want… | Use |
|---|---|
| Which operationalizations are admissible under a stated theory, and what range of downstream estimates follows | **cvprofiles** |
| How much conclusions move across regression specifications (Leamer extreme bounds) | Closest ancestor; cvprofiles moves the discipline to the *measurement* layer |
| Whether unobserved confounding could kill β for a *fixed* regressor (OVB) | OVB sensitivity packages (e.g. sensemakr) — orthogonal, downstream of measurement choice |
| Which inputs drive output variance (variance-based GSA) | Display cousin; different question |

Full positioning in the methodology doc (`docs/METHODOLOGY.md`).

## Reproducibility contracts

- **Frozen runs.** A run_id is derived from the frozen score matrix, pinned network, and β spec — same inputs ⇒ same id, bit-stable within the documented float policy.
- **Hashes everywhere.** `scores_hash`, `network_hash`, `beta_hash` travel with every report; paper numbers require frozen scores + pinned network + fixed seed + package version.
- **Survivors-only range.** The headline [L,U] is the image of β on admissible measures only. Rejected measures are reported diagnostically but never enter the range.
- **Empty M\* is success.** If theory + data reject every candidate measure, that is a finding — exit 0, clean report.
- **Diagnostics are additive.** Bootstrap bands, the coverage uncertainty band (α/κ), and θ-grid/δ-grid sensitivity surfaces never replace the headline range; band values and the α/κ knobs are excluded from the freeze preimage.
- **Holdout is in the run_id.** `holdout_units` is normalized to an order-independent sorted-unique list, stored in the freeze `config`, and hashed into the freeze preimage — same bundle with a different holdout list ⇒ different run_id.
- **Coverage knobs are not.** `alpha`/`kappa` shape the additive uncertainty band only and are excluded from the freeze preimage by design — same bundle ± α/κ ⇒ same run_id, different `coverage.json`.

## What it is not

- Not a scorer product: no measure generation, no prompt search, no LLM inside the engine.
- Not an automated theory-authoring system: the nomological network is researcher-authored.
- Not a generic causal-sensitivity package: it disciplines *measurement* given a stated β.
- Not “automate all of empirical economics”: it answers one question well.

## What's new in v3

- **Named `empty_R` unrestricted-multiverse special case (3.0.1).** When the researcher pins an empty nomological network `R = ∅`, the engine now returns the full menu as the admissible set `M* = M` and the spec-curve range over all β values. The accidental-empty case still fails loud — the named special case is opt-in via `empty_R: true` in the network YAML.
- **Flagship application: WVS/GPS patience (3.0.0).** Country-level patience measured through a menu of WVS Wave 7 facets + a GPS patience anchor, disciplined by a literature-anchored `disc_risk` bar (`θ = 0.35`). Accepted frozen run: `M*_select = [m_gps_patience, m_prompt_a]`, headline `[L, U] = [0.328, 0.402]`. See `evals/wvs_gps_preferences/` and the input-builder tutorial.
- **Posture (a) reporting discipline (3.0.0).** `M*_select` is the primary headline; empty `M*_robust` from a units-split is a power-limited diagnostic, not a paper failure. See `docs/16` §11.
- **Engine stays model-free and score-agnostic.** No LLM client in the import graph; LLM scoring is an upstream protocol, not an engine feature.

Upgrading from v2.x? v2.5.2 was the last PyPI release before v3; the v3.0.x API is a strict superset.

## Documentation

Start here, then follow in order:

| Doc | Purpose |
|---|---|
| [`docs/METHODOLOGY.md`](docs/METHODOLOGY.md) | The method: menu, slacks, M\*, B\*, inference stance |
| [`docs/USER_GUIDE.md`](docs/USER_GUIDE.md) | How to prepare inputs, run a profile, read the report |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Four-state machine, IO contracts, determinism |
| [`docs/ROADMAP.md`](docs/ROADMAP.md) | Live roadmap (maintained with the engineering log) |
| [`docs/README.md`](docs/README.md) | Doc index — public docs + governance/lock docs |

Tutorials (run against the installed package, inputs generated inline):

| Tutorial | What it covers |
|---|---|
| `tutorials/cvprofiles_tutorial.ipynb` | **Core.** Synthetic walk-through + empty-set contrast; Part 2 is a **historical** H5 Trust appendix (not the v3 flagship) |
| `tutorials/cvprofiles_diagnostics_tour.ipynb` | v2.0 measure-discipline tour: all evaluators + diagnostics |
| `tutorials/cvprofiles_irt_scoring_tutorial.ipynb` | IRT as a SCORE-upstream scoring technology |
| `tutorials/cvprofiles_sensemakr_tutorial.ipynb` | OVB sensitivity (Cinelli–Hazlett) on a survivor |
| `tutorials/cvprofiles_wvs_gps_inputs.ipynb` | **Flagship inputs.** WVS/GPS patience input-builder + E2E: synthetic oracle, then the four frozen inputs for the WVS Wave 7 × GPS lane |

Governance, decisions, and paper-protocol locks live in [`docs/README.md#governance`](docs/README.md). Pre-consolidation scaffold docs are in `docs/archive/` (historical reference only).

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) — maintained as a live document alongside the engineering log.

## Museum PoC

`evals/synthetic/v0_poc.py` is a historical monolith kept for reference. It is not part of the package and must not be imported from `src/`. See `AGENTS.md` for the contract.

## Citation

The canonical method statement is `docs/METHODOLOGY.md`. A paper citation block will be added once the v3 paper freeze is final (see `docs/16`).

## Acknowledgments

Development of cvprofiles is assisted by **Hermes Agent (Nous Research)** as an engineering and research collaboration tool — scaffolding, tests, packaging, and documentation review. Hermes is a development aid only; running cvprofiles requires nothing beyond Python and a personal computer.

## License

MIT. See `LICENSE` (or the project metadata on PyPI).
