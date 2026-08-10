# cvprofiles

**Construct-validity profiles for cheap multi-measure AI operationalizations.**

Open, high-observability research tooling that treats construct validity as **partial identification over a menu of measurement functions**, disciplined by a researcher-authored nomological network. The engine returns an admissible measurement set M\* and a construct-identified range [L,U] for a target functional β(·). Empty sets and wide ranges are scientific features, not product failures.

| | |
|---|---|
| **Version** | **2.5.2** — PyPI release 2026-08-09 (WVS/GPS tutorial milestone: input-builder + E2E notebook, GPS-only individual level, corrected placeholder networks) |
| **Status** | Public repo; tags `v0.1`, `v1.1.0`, `v2.0.0`, `v2.5.0`, `v2.5.1`, `v2.5.2` frozen; protocol provisional synthetic-only; H5 Trust evidence **re-graded to historical/regression witness** (2026-08-07, Gate A); v3 IVS cultural-values lane opened (`docs/18`), run gated; P6+ deferred |
| **License** | MIT |
| **GitHub** | https://github.com/Bonorinoa/cvprofiles |
| **CI** | [![ci](https://github.com/Bonorinoa/cvprofiles/actions/workflows/ci.yml/badge.svg)](https://github.com/Bonorinoa/cvprofiles/actions/workflows/ci.yml) |
| **Proof summary** | `reports/summaries/v1_1_package_synth_summary.json`, `v1_1_protocol_synth_mc50_summary.json` (provisional synthetic-only protocol table; not a paper result) |

## Install

```bash
pip install cvprofiles
```

Requires Python ≥ 3.11. No GPU, no model weights, no API keys — the engine is a pure Python/numpy/pandas computation over the score columns you supply.

### Install from source (pinned)

`main` is development; the version tags are the paper anchors. Clone the tag that matches your paper run:

```bash
git clone -b v2.5.2 --depth 1 https://github.com/Bonorinoa/cvprofiles.git
cd cvprofiles
pip install -e .
```

## Quickstart

A profile needs exactly four input files, all plain text:

| File | Contents |
|---|---|
| `scores.csv` (or `.parquet`) | One row per unit; one column per candidate measure, plus optional auxiliary/outcome columns |
| `roles.json` | Which columns are measures, auxiliaries, outcome, unit id |
| `network.yaml` | Your nomological network: restrictions with thresholds θ |
| `beta.yaml` | The target functional β(·) you want a range for |

Minimal example (from the repo's `data/fixtures/mini_v1/`):

```bash
cvprofiles run \
  --scores data/fixtures/mini_v1/scores.csv \
  --roles data/fixtures/mini_v1/roles.json \
  --network data/fixtures/mini_v1/network.yaml \
  --beta data/fixtures/mini_v1/beta.yaml \
  --out my_first_profile --seed 0
```

The CLI prints one JSON summary to stdout (machine-clean) and writes `report.html` plus machine-readable artifacts into `my_first_profile/`:

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

## Positioning and inference stance

**Model-free by design.** The engine never fits a model inside the validity layer: a p-value requires a null distribution, a Bayes factor requires priors, a likelihood ratio requires a model — all of which smuggle in distributional assumptions the engine refuses to own. It computes transparent sample moments against researcher-declared thresholds.

**Diagnostic surfaces.** θ-grid and δ-grid show how $M^*$ and $[L,U]$ move with threshold and tolerance choices — the specification-curve (Simonsohn et al. 2020) / multiverse (Steegen et al. 2016) idea applied to measurement admissibility. Descriptive by design: they reveal *where* admissibility flips; they make no inferential claim about the surface.

**Honest inference posture.** The range is a fragility audit over sample-admissible measures, not a confidence set — no coverage theorem is claimed. Bootstrap output is an uncertainty band, never a CI. The units-split holdout is the out-of-sample check: select on train units, verdict on held-out units.

## Documentation

Start here, then follow in order:

| Doc | Purpose |
|---|---|
| `docs/METHODOLOGY.md` | The method: menu, slacks, M\*, B\*, inference stance |
| `docs/USER_GUIDE.md` | How to prepare inputs, run a profile, read the report |
| `docs/ARCHITECTURE.md` | Four-state machine, IO contracts, determinism |
| `docs/16_Paper_Protocol_Freeze.md` | Paper-facing locks and open fields |
| `docs/18_IVS_Cultural_Map.md` | v3 IVS cultural-values lane design container (Augusto-authored; run gated) |
| `docs/17_H5_Trust_Design.md` | H5 Trust design lock — **historical** (re-graded 2026-08-07) |
| `tutorials/cvprofiles_tutorial.ipynb` | Synthetic walk-through + H5 replication |
| `tutorials/cvprofiles_diagnostics_tour.ipynb` | v2.0 measure-discipline tour: all evaluators + diagnostics |
| `tutorials/cvprofiles_irt_scoring_tutorial.ipynb` | IRT as a SCORE-upstream scoring technology |
| `tutorials/cvprofiles_sensemakr_tutorial.ipynb` | OVB sensitivity (Cinelli–Hazlett) on a survivor |
| `tutorials/cvprofiles_wvs_gps_inputs.ipynb` | WVS/GPS input-builder + E2E (patience + risk-taking): synthetic oracle walk-through, then authoring the four frozen inputs for the WVS Wave 7 × GPS lane, incl. the country-level units-split holdout |
| `docs/PROJECT_MANIFEST.md` | Machine-readable project state |

Live internal logs (append-only): `docs/12_Decision_Engineering_Log.md`, `docs/13_Evaluations_Log.md`. Pre-consolidation scaffold docs live in `docs/archive/` (historical reference only).

## Roadmap

See [`docs/ROADMAP.md`](docs/ROADMAP.md) — maintained as a live document alongside the engineering log.

## Museum PoC

`evals/synthetic/v0_poc.py` is a historical monolith kept for reference. It is not part of the package and must not be imported from `src/`.

## Acknowledgments

Development of cvprofiles is assisted by **Hermes Agent (Nous Research)** as an engineering and research collaboration tool — scaffolding, tests, packaging, and documentation review. Hermes is a development aid only; running cvprofiles requires nothing beyond Python and a personal computer.

## License

MIT. See `LICENSE` (or the project metadata on PyPI).
