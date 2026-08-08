# cvprofiles tutorials

Four independent notebooks. All run against the **installed package only** (`pip install cvprofiles`)
and need no repository files — every input is generated inline.

## 1. `cvprofiles_tutorial.ipynb` — the core walk-through

Two parts:

1. **Part 1 (synthetic):** builds a scores matrix inline, writes the SCORE/RESTRICT
   inputs to disk, runs a full profile, and shows the empty-set contrast. Needs no
   repository files — only the installed package.
2. **Part 2 (H5 replication):** reproduces the frozen country-level generalized-trust
   evaluation (n=35) from the committed frozen inputs
   (`evals/h5_trust/data/`), including the pinned network and the pre-data θ-anchor
   file. The final cell asserts `M* = {m_trust_general, m_trust_in_group}` and
   `[L,U] = [0.370754, 0.623891]` bit-identically.

## 2. `cvprofiles_diagnostics_tour.ipynb` — the v2.0 measure-discipline tour

A single synthetic construct with a designed menu of five measures exercises the full
**v2.0 diagnostic stack**:

- all four restriction evaluators in one network (`corr_min`, `corr_sign`, `mean_order`,
  `rank_agree`);
- a regression target functional (`ols_coef` with a control);
- all four additive diagnostics in one run: **bootstrap** over units, the **θ-grid**
  sensitivity surface, the **δ-grid** tolerance surface, and the **θ-anchor** pre-data audit;
- the wide-range-as-finding story (`m_good` and `m_weak` both admissible, β ≈ 0.45 vs 0.23);
- the CLI (`cvprofiles run …`, stdout is pure JSON);
- self-checking assertions on the package's core contracts (survivors-only range, anchors
  excluded from the run_id, monotone δ-grid, θ-grid empty under tightening, fail-loud anchors).

## 3. `cvprofiles_irt_scoring_tutorial.ipynb` — IRT as a SCORE-upstream scorer

The engine is score-agnostic: any scalar column per unit can be a candidate measure,
however it was built. This notebook shows item response theory as one principled upstream
scoring technology:

- simulate a latent trait and 1PL item responses;
- fit a **hand-rolled 1PL (Rasch)** model (numpy + scipy only, auditable) to recover
  person scores θ̂;
- feed θ̂, a naive sum score, and a noisy measure into a cvprofiles profile;
- see IRT and sum scores both survive the network while the noisy measure is rejected.

## 4. `cvprofiles_sensemakr_tutorial.ipynb` — OVB sensitivity on a survivor

cvprofiles answers *which measures are admissible and what range follows*; a different,
downstream question is *how much unobserved confounding would overturn one fixed
coefficient*. This notebook applies the **Cinelli–Hazlett (2020)** omitted-variable-bias
framework (the `sensemakr` method) to a survivor's standardized OLS coefficient:

- a DGP with an unobserved confounder affecting both the measure and the outcome;
- a hand-rolled CH implementation: partial R², the exact OVB identity (impact × imbalance),
  and the robustness value RV_q — numpy only;
- confirms the exact identity recovers the full-model coefficient, and the partial-R²
  reparameterization matches it.

## Why "independent"

The verification installs the **published wheel** (not the source tree) into a fresh
virtual environment, then executes the notebook. Part 2 of the core tutorial needs the
checkout for the frozen H5 inputs, so point it at the repo via `CVPROFILES_REPO`:

```bash
# fresh venv, wheel-only install (PYTHONPATH unset so the src tree cannot leak in)
uv venv /tmp/cvp_tutorial_venv --python 3.11
uv pip install --python /tmp/cvp_tutorial_venv/bin/python \
    cvprofiles==2.0.0 jupyter nbconvert ipykernel

# execute a copy of a notebook (the committed notebook stays clean)
cp tutorials/cvprofiles_diagnostics_tour.ipynb /tmp/cvp_tour_exec.ipynb
env -u PYTHONPATH /tmp/cvp_tutorial_venv/bin/python -m jupyter nbconvert \
    --to notebook --execute /tmp/cvp_tour_exec.ipynb \
    --output /tmp/cvp_tour_exec_out.ipynb
```

For the core tutorial's H5 part, add `CVPROFILES_REPO=/path/to/cvprofiles` to the nbconvert
command (nbconvert kernels start in the notebook's folder, so relative data paths fail
outside the checkout).

The Phase-3 notebooks (IRT scoring, sensemakr) are regenerated from
`tools/build_tutorials.py`:

```bash
python tools/build_tutorials.py   # emits both notebooks into tutorials/
```

## Notes

- Empty `M*` and wide `[L,U]` are scientific features, not crashes.
- The engine is score-agnostic and model-free; the menu and network are researcher-owned.
- IRT and OVB-sensitivity code is intentionally hand-rolled and self-contained — the point
  is auditable upstream/downstream patterns, not new dependencies.
- The H5 replication is *preliminary paper-facing evidence* (owner-approved 2026-08-04);
  it is not a final paper lock.
