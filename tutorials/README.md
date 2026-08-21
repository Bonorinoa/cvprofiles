# cvprofiles tutorials

Notebooks run against the **installed package** matching this checkout.
The core notebook and the diagnostics / IRT / sensemakr tours generate every
input inline — no repository files needed. The WVS/GPS flagship builder uses
the repository checkout for its frozen inputs.

## Audience levels

| Level | Notebook | Who it is for |
|---|---|---|
| **Core** | `cvprofiles_tutorial.ipynb` | First run: synthetic SCORE→REPORT + empty-set contrast. Fully self-contained (pip install is enough). |
| **Diagnostics** | `cvprofiles_diagnostics_tour.ipynb` | Next: full evaluator + bootstrap / θ-grid / δ-grid / anchors tour on one designed menu. |
| **Upstream / downstream** | `cvprofiles_irt_scoring_tutorial.ipynb`, `cvprofiles_sensemakr_tutorial.ipynb` | IRT as a SCORE-upstream scorer; Cinelli–Hazlett OVB on a survivor (orthogonal to the validity layer). |
| **Flagship inputs** | `cvprofiles_wvs_gps_inputs.ipynb` | Authoring the four frozen inputs for the WVS/GPS **patience** flagship (`evals/wvs_gps_preferences/`). |

## 1. `cvprofiles_tutorial.ipynb` — the core walk-through

Builds a scores matrix inline, writes the SCORE/RESTRICT inputs to disk, runs a
full profile, and shows the empty-set contrast. Needs only the installed
package.

## 2. `cvprofiles_diagnostics_tour.ipynb` — the v2.0 measure-discipline tour

A single synthetic construct with a designed menu of five measures exercises the full
diagnostic stack:

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

## 5. `cvprofiles_wvs_gps_inputs.ipynb` — flagship input builder

Synthetic oracle walk-through, then authoring the four frozen inputs for the
WVS Wave 7 × GPS **patience** flagship (including the country-level units-split
holdout). This is the public-facing empirical example.

## Why "independent"

Verification installs the package from **this checkout** (or a matching wheel) into a
fresh virtual environment, then executes the notebook:

```bash
# fresh venv, checkout install (PYTHONPATH unset so a different src tree cannot leak in)
uv venv /tmp/cvp_tutorial_venv --python 3.11
uv pip install --python /tmp/cvp_tutorial_venv/bin/python \
    -e . jupyter nbconvert ipykernel

# execute a copy of a notebook (the committed notebook stays clean)
cp tutorials/cvprofiles_diagnostics_tour.ipynb /tmp/cvp_tour_exec.ipynb
env -u PYTHONPATH /tmp/cvp_tutorial_venv/bin/python -m jupyter nbconvert \
    --to notebook --execute /tmp/cvp_tour_exec.ipynb \
    --output /tmp/cvp_tour_exec_out.ipynb
```

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
