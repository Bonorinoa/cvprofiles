# User Guide

How to prepare inputs, run a profile, and read the report. This supersedes the earlier `14_Researcher_Input_Guide.md` scaffold (archived) and reflects the shipped v3.0.2 package (reproducibility patch: round-trip CSV parsing; 3.0.1 added the empty_R unrestricted-multiverse special case; 3.0.0 remains the flagship-application release): the P2 evaluators `corr_zero` / `monotone_rank`, the P3 betas `diff_means` / `map_distance`, P4 holdout (restriction `stage` split + country-level units-split + pooled K-fold application), and the P5 coverage uncertainty band.

## 1. The four input files

A profile needs exactly four input files, all plain text:

| File | Contents | Who authors |
|---|---|---|
| `scores.csv` / `scores.parquet` | One row per unit; one column per candidate measure, plus optional auxiliary/outcome columns | Researcher (upstream scorers OK) |
| `roles.json` | Which columns are measures, auxiliaries, outcome, unit id | Researcher |
| `network.yaml` | Nomological network: restrictions with thresholds | Researcher (main path) |
| `beta.yaml` | Target functional declaration | Researcher chooses; engine evaluates |

### 1.1 scores

Minimal shape (from the repo's `data/fixtures/mini_v1/scores.csv`):

```csv
unit_id,m_good,m_weak,m_slop,v_aux,y,V_star
u01,1.20,0.80,-0.40,1.10,1.00,1.30
u02,0.90,0.50,0.20,0.70,0.60,0.90
```

- One row = one unit (person, firm-year, country, …). Same unit index across scores/aux/outcome.
- One column = one scalar measure, already coded so "higher = more of C", or polarity declared before freeze.
- Missingness handled upstream (drop, impute with audit, or exclude that measure for incomplete units). The engine does not impute and fails loud on NaN where it matters.
- `diagnostic` columns (e.g. `V_star`) may exist for eval diagnostics but are never used inside IDENTIFY.

### 1.2 roles.json

```json
{
  "unit_id": "unit_id",
  "measures": ["m_good", "m_weak", "m_slop"],
  "aux": ["v_aux"],
  "outcome": "y",
  "diagnostic": ["V_star"]
}
```

`measures` defines the menu order. Roles must not overlap; the engine rejects ambiguous columns.

### 1.3 network.yaml

```yaml
schema_version: "1"
name: mini_v1_oracle
delta: 0.0
restrictions:
  - id: r_corr_min_aux
    type: corr_min
    theta: 0.35
    params:
      variable: v_aux
  - id: r_corr_sign_aux
    type: corr_sign
    theta: 0.10
    params:
      variable: v_aux
      sign: 1
  - id: r_corr_min_hold
    type: corr_min
    stage: holdout
    theta: 0.25
    params:
      variable: v_aux
```

Restriction types and their params are documented in the [Methodology](METHODOLOGY.md). `delta` is the global slack tolerance (default 0). Each restriction may declare a `stage`: omit it (or write `select`) for an admission filter that gates M\*, or write `holdout` for a *finding* restriction — its slacks are computed and reported, but a holdout-stage failure never rejects a measure from M\* (P4). A network with holdout-stage restrictions and no select-stage restriction is rejected as degenerate (vacuous admit-all). Explicit `stage` values enter the network hash; an omitted `stage` hashes as absent, so pre-P4 networks keep bit-stable hashes.

`empty_R: true` with `restrictions: []` is a named special case: every menu measure is admitted and `[L,U]` is the unrestricted specification-curve range. An empty restriction list without the flag still fails loud. Default `empty_R: false` is omitted from the network hash so pre-3.0.1 networks stay bit-stable.

### 1.4 beta.yaml

```yaml
schema_version: "1"
type: corr_y
outcome: y
params: {}
```

`ols_coef` requires `params.controls` (non-empty list of control columns).

## 2. Running a profile

### CLI

```bash
cvprofiles run \
  --scores data/fixtures/mini_v1/scores.csv \
  --roles data/fixtures/mini_v1/roles.json \
  --network data/fixtures/mini_v1/network.yaml \
  --beta data/fixtures/mini_v1/beta.yaml \
  --out my_first_profile --seed 0
```

Options:

| Flag | Meaning | Default |
|---|---|---|
| `--scores`, `--roles`, `--network`, `--beta` | Input paths (required) | — |
| `--out` | Output directory | `reports/runs/<run_id>/` |
| `--policy` | SCORE normalization: `none` \| `zscore_measures` | `none` |
| `--seed` | RNG seed (bootstrap) | `0` |
| `--n-boot` | Bootstrap replicates over units; `0` disables | `0` |
| `--theta-grid` | Comma-separated positive λ scale multipliers | off |
| `--delta-grid` | Comma-separated non-negative absolute δ values | off |
| `--anchors` | Pre-data θ-anchor YAML (documentation; excluded from run_id) | off |
| `--holdout-units` | Comma-separated unit ids to hold out (select on train units, verdict on held-out units; headline = M*_robust) | off (no units-split) |
| `--alpha` | Coverage band tail probability: per-side α/2 quantiles over non-empty bootstrap replicates (requires `--n-boot` > 0) | `0.10` |
| `--kappa` | Boundary-attribution rule: \|margin_m\| ≤ κ·SE_m (requires `--n-boot` > 0) | `2.0` |
| `--title` | Report title | "Construct-validity profile" |

**Contract:** stdout is always a single JSON summary (machine-clean). Human status messages go to stderr only. Empty `M*` exits 0 — it is a clean success.

### Python API

```python
from cvprofiles.pipeline import run_profile, summary_dict

result = run_profile(
    scores="scores.csv",
    roles="roles.json",
    network="network.yaml",
    beta="beta.yaml",
    out_dir="my_first_profile",
    seed=0,
    n_boot=200,
    theta_grid_lambdas=[0.5, 1.0, 2.0],
    # P4b units-split: select on train units, verdict on held-out units.
    # Unit ids are raw values of the unit_id column (country iso codes here);
    # at least two units must be held out (train and holdout frames each need
    # >= 2 rows). List order is irrelevant — the engine sorts + dedupes.
    holdout_units=["USA", "MEX"],
    # P5 coverage band knobs (defaults shown). alpha/kappa never enter the
    # run_id — same bundle ± these ⇒ same run_id, different coverage.json.
    alpha=0.10,
    kappa=2.0,
)
print(summary_dict(result))
```

## 3. What comes out

Every run directory contains machine-readable artifacts plus the human report:

| Artifact | Contents |
|---|---|
| `report.html` | Primary human audit trail (see below) |
| `report.json` | Machine-complete dump of the same payload |
| `range.json` | `L`, `U`, `empty`, `point_id` |
| `admissible.json` | `M*` members + rejection reasons; under a units-split also `M_star_select`, `M_star_robust`, and the `holdout` verdict block (units, frames, per-measure compliance) |
| `beta_values.json` | β(m) for every measure, survivors flagged |
| `slacks.csv` / `slacks.parquet` | Full slack matrix (measures × restrictions, including holdout-stage columns) |
| `S_frozen.csv` / `.parquet` | Frozen, validated score matrix |
| `run_manifest.json` | Hashes, seed, versions, settings (incl. the normalized `holdout_units` when a units-split is used) |
| `bootstrap.json`, `theta_grid.json`, `delta_grid.json`, `anchors.json` | Only when the corresponding layer is enabled |
| `coverage.json` | Uncertainty band: α, κ, quantiles, band, empty-replicate rate, boundary attribution, admission frequency p̂_m (only when bootstrap is enabled) |

### Report anatomy

`report.html` is a single-page, self-contained audit trail. It answers, for a non-coder:

1. **What was the construct menu?** — title, roles, measure ids.
2. **Which restrictions bit?** — slack matrix (satisfied vs violation magnitudes); failed restrictions named per measure.
3. **Who is in M* and who failed which bar?** — survivors listed; non-survivors with binding restrictions named.
4. **What is [L,U]?** — headline range block; empty-set panel when M* is empty (with an explanatory note, not a stack trace).
5. **How does the range move on the θ-grid / δ-grid?** — sensitivity tables, when enabled.
6. **What is the uncertainty band?** — when bootstrap is on, a coverage panel shows α, κ, the per-side α/2 quantiles, the band, the empty- and degenerate-replicate rates, **boundary attribution** (|margin_m| ≤ κ·SE_m, with margin/SE per measure), and admission frequency p̂_m.
7. **Did survivors hold out of sample?** — under a units-split, the HTML M* is the robust set (M*_select ∩ holdout-compliant); the per-measure holdout verdict is machine-readable in the `admissible.json` `holdout` block and the stdout summary (there is no dedicated HTML holdout panel).

The report is generated from the same machine payload as `report.json` (Jinja2 template), so the HTML and JSON can never disagree about numbers.

## 4. Preparing inputs: research hygiene

### 4.1 Composites vs split measures

| Situation | Default |
|---|---|
| Items are near-synonyms of one facet | Composite OK (mean / PCA-1 / sum), plus optionally a flagship item |
| Items differ by object (strangers vs family vs police) | **Split** — separate columns |
| Items differ by response technology (binary vs 1–10 vs membership) | **Split** |
| Map tags say `clean` vs `bridge` vs `stretch` | Do not pool across tags into one m |
| You trained on instrument family A, evaluate on family B | Separate LLM columns per family |
| Only one item available | Single column; do not invent fillers |

**Test question:** if two items can move in opposite directions for theoretically respectable reasons, they are not one measure.

### 4.2 Anchors

Three roles are overloaded under "anchor":

- **Criterion measure (P1 posture):** one measure is the standard others must recover (e.g. LLM vs GPS). Label the run criterion-validity, not a symmetric profile.
- **Peer candidate (P2 posture):** no measure is sacred; all face the same external R.
- **Reference for rank agreement:** `rank_agree(m, m_ref)` — useful as a soft check, dangerous as the only gate.

### 4.3 Choosing units

| Design | Unit |
|---|---|
| Cross-walk surveys / GPS country z / country-conditioned LLM | Country (or region) |
| Single microdata survey | Person |
| Text scored at document level | Document |
| Panel | Entity-time (only if every m is defined on that index) |

**Hard rule:** do not row-bind different surveys' respondents into one SCORE matrix. Join at the moment level (country means, etc.) when instruments sample different people.

### 4.4 Building network.yaml without smuggling β

1. Write one paragraph defining C (prose).
2. List testable implications as inequalities in plain language.
3. Only then pick restriction types and θ.
4. Choose β last (what economic number you track). Do not reverse-engineer R so your favorite regression survives.

### 4.5 θ-anchor discipline

Thresholds are where "literature-grounded, not data-mined" is won or lost. Ship a pre-data `anchors.yaml` with one entry per restriction:

- `restriction_id` — must match the network exactly (engine checks completeness).
- `citation_key` — stable reference key.
- `source_phrase` — the published/derived number the θ sits at or below.
- `anchor_kind` — `literature` | `derived` | `author`.
- `pre_data: true` — your commitment that the anchor predates the frozen run (the engine cannot verify timing; the verifier requires it for the H5 lane).

Anchors are documentation: hashed for provenance but **excluded from run_id**.

### 4.6 Single construct per run, batch many

One construct per profile. Six GPS dimensions ⇒ six networks / six runs. The engine itself stays single-construct; the thin batch orchestrator (`tools/run_many.py`) makes the six-run workflow mechanical against one shared score matrix.

Batch manifest (`batch.yaml`):

```yaml
profiles:
  - id: trust
    network: networks/trust.yaml
    beta: betas/trust.yaml
  - id: patience
    network: networks/patience.yaml
    beta: betas/patience.yaml
```

Relative `network`/`beta` paths resolve against the manifest file's directory. All profiles share the same scores/roles/seed and any additive diagnostic flags you pass.

```bash
python tools/run_many.py \
  --scores scores.csv --roles roles.json \
  --manifest batch.yaml --out profiles/ --seed 0
```

Each profile gets its own frozen run directory (`profiles/<id>/`) with the usual artifacts, plus a machine-readable `batch_summary.json`. stdout is one JSON summary (same contract as `cvprofiles run`); empty M\* in any profile is a clean success. Multi-construct joint networks remain out of scope (see Roadmap).

## 5. Worked pattern: criterion recovery first (LLM vs GPS)

*Illustrative workflow — not an authored empirical network for any specific study.*

| Step | Action |
|---|---|
| 1. Unit | Country (GPS coverage) |
| 2. Menu | `m_gps_d`, `m_llm_d` (+ distractors: noise, wrong-dim LLM score) |
| 3. Score LLM | Same instrument family as training first (GPS-style scenarios); WVS stems are a second column/run |
| 4. Posture | P1 criterion — GPS is standard |
| 5. Core restrictions | `corr_min(m_llm_d, m_gps_d) ≥ θ`; optional sign checks on shared external aux |
| 6. β | Optional for pure recovery audit; use `corr_y` only if a downstream claim exists |
| 7. Success language | "Under θ-grid, m_llm admissible as GPS-recovery at θ≤…" — not "LLM measures true culture" |
| 8. Failure language | "Fails GPS recovery at prereg θ" — then diagnose scenario stem, country slice, dim contamination — not silent θ drop |

## 6. Checklists

### Before freeze (SCORE)

- [ ] Unit definition written in one sentence
- [ ] Every column has source, formula/composite recipe, polarity, missingness rule
- [ ] Split vs composite decisions recorded with the "opposite movement" test
- [ ] Instrument families not silently pooled
- [ ] No outcome y leakage into measure columns (especially LLM judges that see y)
- [ ] Scoring notes path stored next to data

### Before claims (RESTRICT / IDENTIFY)

- [ ] Posture labeled: P1 criterion vs P2 peer vs synthetic oracle
- [ ] C paragraph ≠ dimension marketing label alone
- [ ] R not copied from the regression spec that defines β
- [ ] θ prereg or explicitly exploratory
- [ ] θ values are on the RAW sample-statistic scale (correlations or mean gaps, not t-stats); slacks are intentionally unstandardized, so θ is directly comparable to the reported slack numbers
- [ ] Anchor roles named
- [ ] One construct per run
- [ ] Empty M* acceptable; no auto-loosen plan in default path

### Paper / thesis citation

- [ ] Run id / hashes for scores, network, beta, seed, package version
- [ ] Menu J and identities of survivors / failures
- [ ] Binding restrictions named
- [ ] θ-sensitivity shown for membership-critical gates
