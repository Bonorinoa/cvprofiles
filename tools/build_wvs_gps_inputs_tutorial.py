"""Build the WVS/GPS input-builder + E2E tutorial notebook (nbformat 4.5, clean).

A: synthetic walk-through first — the full input-authoring loop on a small
   synthetic DGP with an ORACLE network (agent-authorized for synthetic), so
   every step is runnable and self-checking without any real data.
B: real WVS/GPS input-builder — loads the local GPS (Falk et al. 2018) and
   WVS Wave 7 files, scaffolds scores/roles/network/beta authoring. The real
   empirical network R/θ/β is AUTHORED BY AUGUSTO; cells carry placeholders
   and validation helpers, never pre-authored empirical theory.

Intermediate demo lane (docs/12 2026-08-09, docs/16 §10): patience + risk-
taking, local data, NOT paper evidence.

Run: uv run python tools/build_wvs_gps_inputs_tutorial.py
"""

from __future__ import annotations

import json
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "tutorials"

KERNEL = {
    "display_name": "Python 3",
    "language": "python",
    "name": "python3",
}
LANG = {"name": "python", "version": "3.11"}


def cell(kind: str, src: str, i: int) -> dict:
    lines = [ln + "\n" for ln in src.split("\n")]
    c = {
        "cell_type": kind,
        "metadata": {},
        "source": lines,
        "id": f"cell-{i}",
    }
    if kind == "code":
        c["execution_count"] = None
        c["outputs"] = []
    return c


def nb(cells: list[dict]) -> dict:
    return {
        "cells": cells,
        "metadata": {"kernelspec": KERNEL, "language_info": LANG},
        "nbformat": 4,
        "nbformat_minor": 5,
    }


TITLE = """# cvprofiles — WVS/GPS input-builder & E2E tutorial (patience + risk-taking)

The package takes **four plain-text inputs** and returns an admissible measurement
set $M^*$ and a construct-identified range $[L,U]$:

```text
SCORE   scores.csv    unit x measure scores (+ aux / outcome)
RESTRICT roles.json   which columns are unit_id / measures / aux / outcome
        network.yaml  nomological network R with thresholds θ
        beta.yaml     target functional β(·)
IDENTIFY slacks -> M* -> [L,U]
REPORT  JSON / HTML audit trail
```

This notebook is your **hands-on guide to the input format** — and to the
measurement-theory logic behind each input. It has two parts:

- **Part 1 — synthetic walk-through (oracle).** A small simulated DGP with a
  designed valid / weak / invalid menu, an *oracle* network (agent-authored,
  synthetic only), and self-checking assertions. This runs end-to-end with no
  real data — it is how you learn the loop.
- **Part 2 — real WVS/GPS input-builder.** Loads the **local** GPS (Falk et al.
  2018 Global Preference Survey) and WVS Wave 7 files and scaffolds the four
  inputs for the **patience** and **risk-taking** constructs. The empirical
  network $R$, thresholds $\\theta$, and $\\beta$ are **yours to author** — this
  notebook validates each file as you write it.

Lane status: intermediate demo + position-paper complement (docs/12 2026-08-09,
docs/16 §10). NOT paper headline evidence; the IVS cultural-values lane remains
the v3 headline.
"""

IMPORTS = """from __future__ import annotations
import json
import os
import tempfile
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

import cvprofiles
from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.schemas.network import NetworkConfig, parse_network
from cvprofiles.schemas.beta import BetaSpec

print("cvprofiles", cvprofiles.__version__)
"""

LIT_MD = """## 0. Where this package sits in the literature

Every engine component maps onto a named scientific tradition. The **novelty is
placement, not new math**: specification uncertainty moved from regression
specs to the *measurement layer*, and construct validity made machine-checkable.

| Engine move | Literature ancestors | What is novel here |
|---|---|---|
| Construct validity as a **set-valued object** | Cronbach & Meehl (1955) construct validity + nomological network; Manski (2003) partial identification | "Which operationalizations of $C$ are admissible" becomes a partial-ID problem: the object is a **set**, not a point |
| Leamer-style uncertainty at the **measurement layer** | Leamer (1983) specification uncertainty; extreme bounds | Leamer disciplined regression *specs*; cvprofiles disciplines the *measurement functions* feeding the regression, against a stated network |
| Moment inequalities as admissibility | Tamer (2010); Andrews & Soares (2010) | **Honest boundary:** transparent sample slacks, not formal set inference with coverage theorems |
| Convergent / discriminant validity made operational | Campbell & Fiske (1959) MTMM | `corr_min` / `corr_sign` / `corr_zero` *are* convergent/discriminant checks as machine-checkable inequalities |
| Robustness of conclusions to researcher choices | Leamer; Sala-i-Martin (1997); specification curve (Simonsohn et al. 2020); multiverse (Steegen et al. 2016) | `[L,U]` = image of the *target functional* over **survivors only** |
| Bootstrap / sensitivity diagnostics | Efron; Imbens & Manski (2004) | **Honest label only** — "uncertainty band", never "CI" or "coverage guarantee" |
| Out-of-sample validation applied to measurement selection | cross-validation logic | Units-split holdout (select on train units, verdict on held-out units) — the falsifiable core |
| Preregistration for thresholds | Simmons et al. (2011); Nosek et al. (2018) | θ-anchor artifact: pre-data anchors, machine-checked completeness (engine flags, never proves timing) |

**What the package is NOT** (positioning): not an OVB/sensemakr replacement
(that asks about a *fixed* regressor); not variance-based GSA (display cousin);
not a latent-variable/IRT model (that is upstream scoring); not a causal
estimator (it disciplines measurement given a stated β).

**Honest boundaries a referee will probe** (state them before they do):
1. `[L,U]` is the sample min/max of β over a *sample-selected* $M^*$ — no
   coverage theorem. The methodology doc says it plainly: *"sharp new
   partial-identification theory is optional garnish, not the load-bearing
   claim."*
2. The evaluator catalog is deliberately small — each entry is a *position on
   what validity means*, not a convenience function.
3. Data-selected admission is sample-dependent: small-n flips are fragility to
   report, not stability to hide.
"""

PART1_MD = """## Part 1 — Synthetic walk-through (oracle network)

We simulate a latent construct $C$ (call it *patience* for concreteness), an
external auxiliary $V$ that a valid measure must co-move with, and three
candidate measures: a **valid** one ($m_1$: high loading on $C$), a **weak** one
($m_2$: lower loading, still valid), and an **invalid** one ($m_3$: pure noise).
The oracle network encodes what any valid patience measure must satisfy:
co-move with $V$ and co-move with a second criterion $V_2$. Self-checking
assertions run the loop and confirm the designed truth is recovered.
"""

PART1_CODE = """rng = np.random.default_rng(20260809)
n = 400

C = rng.normal(size=n)
V = 0.7 * C + 0.7 * rng.normal(size=n)     # external auxiliary: valid patience ↑ V
V2 = 0.5 * C + 0.9 * rng.normal(size=n)    # second criterion

def z(x):
    x = np.asarray(x, float)
    return (x - x.mean()) / x.std(ddof=0)

m_valid = z(0.85 * C + 0.5 * rng.normal(size=n))
m_weak  = z(0.40 * C + 0.9 * rng.normal(size=n))
m_noise = z(rng.normal(size=n))

scores = pd.DataFrame({
    "unit_id": [f"u{i:03d}" for i in range(n)],
    "m_valid": m_valid,
    "m_weak": m_weak,
    "m_noise": m_noise,
    "v": V,
    "v2": V2,
})
print(scores.shape)
"""

ROLES_CODE = """roles = {
    "unit_id": "unit_id",
    "measures": ["m_valid", "m_weak", "m_noise"],
    "aux": ["v", "v2"],
    "outcome": None,
    "diagnostic": [],
}
parsed_roles = ScoreColumnRoles.model_validate(roles)
print("roles OK:", parsed_roles.measures)
"""

NETWORK_CODE = """# ORACLE network (synthetic DGP only — agent-authored; real networks are YOURS).
# Every restriction is a moment inequality: slack = sample statistic - θ.
network = {
    "schema_version": "1",
    "name": "patience_synth_oracle",
    "delta": 0.0,
    "restrictions": [
        {"id": "r_conv_v",   "type": "corr_min", "theta": 0.30, "params": {"variable": "v"}},
        {"id": "r_conv_v2",  "type": "corr_min", "theta": 0.15, "params": {"variable": "v2"}},
    ],
}
parsed_network = parse_network(network)
print("network OK:", [r.id for r in parsed_network.restrictions])
"""

BETA_CODE = """# β: the downstream number we want a range for (here: correlation with v).
beta = {
    "schema_version": "1",
    "type": "corr_y",
    "outcome": "v2",
    "params": {},
}
parsed_beta = BetaSpec.model_validate(beta)
print("beta OK:", parsed_beta.type)
"""

RUN_CODE = """work = Path(tempfile.mkdtemp(prefix="cvp_wvsgps_synth_"))
(work / "scores.csv").write_text(scores.to_csv(index=False))
(work / "roles.json").write_text(json.dumps(roles))
(work / "network.yaml").write_text(yaml.safe_dump(network))
(work / "beta.yaml").write_text(yaml.safe_dump(beta))

result = run_profile(
    scores=str(work / "scores.csv"),
    roles=str(work / "roles.json"),
    network=str(work / "network.yaml"),
    beta=str(work / "beta.yaml"),
    out_dir=str(work / "out"),
    seed=0,
)
s = summary_dict(result)
print("M*:", s.get("M_star"))
print("L,U:", s.get("L"), s.get("U"))
print("empty:", s.get("empty"))
"""

ASSERT_CODE = """# Self-check: designed truth recovered by the oracle network.
assert s.get("M_star") == ["m_valid", "m_weak"], s.get("M_star")
assert "m_noise" not in s.get("M_star", [])
assert s.get("L") is not None and s.get("U") is not None
assert s.get("L") <= s.get("U")
print("Part 1 assertions PASSED")
"""

HARSH_MD = """### Empty M* is a clean scientific output

Raise the threshold above the valid measures' correlations and the admissible
set collapses to $\\emptyset$. The engine exits 0 and reports the empty set —
that is a **feature** (theory + data reject all candidates), never a crash and
never a reason to silently loosen $\\theta$.
"""

HARSH_CODE = """harsh = {
    "schema_version": "1",
    "name": "patience_synth_harsh",
    "delta": 0.0,
    "restrictions": [
        {"id": "r_conv_v",   "type": "corr_min", "theta": 0.99, "params": {"variable": "v"}},
        {"id": "r_conv_v2",  "type": "corr_min", "theta": 0.99, "params": {"variable": "v2"}},
    ],
}
(work / "network_harsh.yaml").write_text(yaml.safe_dump(harsh))
res_h = run_profile(
    scores=str(work / "scores.csv"),
    roles=str(work / "roles.json"),
    network=str(work / "network_harsh.yaml"),
    beta=str(work / "beta.yaml"),
    out_dir=str(work / "out_harsh"),
    seed=0,
)
sh = summary_dict(res_h)
print("empty:", sh.get("empty"), "| M*:", sh.get("M_star"), "| L,U:", sh.get("L"), sh.get("U"))
assert sh.get("empty") is True
print("Empty-set honesty PASSED")
"""

DATA_MD = """## Part 2 — Real WVS/GPS input-builder (patience + risk-taking)

**Lane:** intermediate demo (`evals/wvs_gps_preferences/`), local data only.

**Data sources (on this machine):**
- **GPS** — Falk et al. (2018) Global Preference Survey, country level
  (`~/Desktop/Github_Repositories/SCA2_PofW/data/GPS/GPS_dataset_country_level/country_gps.dta`)
  and individual level (`.../GPS_dataset_individual_level/individual_new.dta`).
  Preference vars: `patience`, `risktaking`, `posrecip`, `negrecip`, `altruism`,
  `trust` (+ individual: `wgt`, `gender`, `age`, `subj_math_skills`).
- **WVS Wave 7** (2017–2022) — individual level
  (`.../WVS/WVS_wave7.dta`). Codebook-verified items for this lane:
  Q13 thrift (patience proxy), Q14 determination/perseverance (persistence),
  Q48 freedom of choice/control 1–10 (agency), Q49 life satisfaction, Q275/
  Q275R education ISCED, Q279 employment status (incl. self-employed).

**Two hard data rules** (this is where most empirical mistakes live):
1. **WVS missing codes are `-1..-5` — mask them, never impute.** The engine
   fails loud on NaN where it matters.
2. **Never row-bind respondents from different surveys into one scores frame.**
   GPS individuals and WVS respondents are *different people*; you may join at
   the **country level** (country means), or keep a single survey at the
   individual level. The cells below enforce this by construction.
"""

DATA_PATHS = """# Resolve the raw-data root: override with env var, else the default local path.
data_root = Path(os.environ.get(
    "CVPROFILES_WVS_GPS_DATA",
    str(Path.home() / "Desktop/Github_Repositories/SCA2_PofW/data"),
))
gps_country = data_root / "GPS/GPS_dataset_country_level/country_gps.dta"
gps_individual = data_root / "GPS/GPS_dataset_individual_level/individual_new.dta"
wvs = data_root / "WVS/WVS_wave7.dta"

for label, p in [("GPS country", gps_country), ("GPS individual", gps_individual), ("WVS wave7", wvs)]:
    print(label, "->", p, "EXISTS" if p.exists() else "MISSING")
"""

DATA_LOAD = """gps_c = pd.read_stata(gps_country, convert_categoricals=False)
gps_i = pd.read_stata(gps_individual, convert_categoricals=False)
print("GPS country:", gps_c.shape, "| columns:", list(gps_c.columns))
print("GPS individual:", gps_i.shape)
"""

WVS_MASK = """# WVS missing-code discipline: mask -1..-5 to NaN on the items we use, never impute.
def mask_wvs_missing(df, cols):
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
        out.loc[out[c].isin([-1, -2, -3, -4, -5]), c] = np.nan
    return out

wvs_raw = pd.read_stata(wvs, convert_categoricals=False)
wvs_items = ["Q13", "Q14", "Q48", "Q49", "Q275", "Q279"]  # verify exact codes in codebook
present = [c for c in wvs_items if c in wvs_raw.columns]
print("WVS columns found:", present)
print("WVS rows:", len(wvs_raw))
"""

COUNTRY_LEVEL = """# Country-level frame: join GPS country preferences + WVS country means.
# (One row per country; different surveys joined at the aggregate level — OK.)
wvs_clean = mask_wvs_missing(wvs_raw, present)
wvs_c = wvs_clean.groupby("B_COUNTRY_ALPHA")[present].mean().reset_index()

# Rename WVS columns so measure ids are descriptive (your choice; keep a recipe note).
country_scores = gps_c.rename(columns={"isocode": "unit_id"})[["unit_id", "patience", "risktaking"]].copy()
country_scores = country_scores.merge(
    wvs_c.rename(columns={"B_COUNTRY_ALPHA": "unit_id", "Q13": "wvs_q13_thrift", "Q14": "wvs_q14_determination"}),
    on="unit_id", how="inner",
)
print("country-level frame:", country_scores.shape)
print(country_scores.head(3))
"""

INDIVIDUAL_LEVEL = """# Individual-level frame (WVS respondents only — same survey, no row-binding).
individual_scores = wvs_clean.rename(columns={
    "B_COUNTRY_ALPHA": "unit_id",
    "Q13": "wvs_q13_thrift",
    "Q14": "wvs_q14_determination",
    "Q48": "wvs_q48_freedom",
    "Q49": "wvs_q49_lifesat",
    "Q275": "wvs_q275_educ",
    "Q279": "wvs_q279_selfemp",
})[["unit_id", "wvs_q13_thrift", "wvs_q14_determination", "wvs_q48_freedom",
    "wvs_q49_lifesat", "wvs_q275_educ", "wvs_q279_selfemp"]].dropna(subset=["wvs_q13_thrift", "wvs_q14_determination"])
print("individual-level frame (WVS):", individual_scores.shape)
print(individual_scores.head(3))
"""

AUTHOR_MD = """### Your authorship cells (patience profile)

Now **you** author the empirical network. The scaffolding below validates your
YAML as you go. Three discipline notes:

1. Write the construct paragraph in prose first (one paragraph: what patience
   is, for this study).
2. List testable implications as plain-language inequalities, *then* pick
   restriction types and $\\theta$.
3. Choose $\\beta$ last — do not reverse-engineer $R$ so a favorite regression
   survives (USER_GUIDE §4.4).

**Menu candidate (country level):** `patience` (GPS), `wvs_q13_thrift`,
`wvs_q14_determination`. **Risk profile** mirrors this with `risktaking` (GPS)
+ `wvs_q279_selfemp` (+ discriminant proxies).
"""

AUTHOR_NET = """# REPLACE the placeholder restrictions below with YOUR network.
# The schema validates structure; θ values are YOUR empirical commitment.
patience_network = {
    "schema_version": "1",
    "name": "patience_wvs_gps_country",
    "delta": 0.0,
    "restrictions": [
        # Example convergent bar (you set θ from the literature / pre-data anchor):
        {"id": "r_pat_v", "type": "corr_min", "theta": 0.20, "params": {"variable": "patience"}},
        # TODO(augusto): add discriminant / criterion bars, stage:'holdout' bars,
        # and anchors.yaml entries (one per restriction id).
    ],
}
try:
    pn = parse_network(patience_network)
    print("network schema OK:", [r.id for r in pn.restrictions])
except Exception as e:
    print("network schema error:", e)
"""

AUTHOR_BETA = """# REPLACE with your β choice (what economic number you track under alternative measures).
patience_beta = {
    "schema_version": "1",
    "type": "corr_y",
    "outcome": "wvs_q49_lifesat",  # example; you may prefer ols_coef with controls
    "params": {},
}
try:
    pb = BetaSpec.model_validate(patience_beta)
    print("beta schema OK:", pb.type)
except Exception as e:
    print("beta schema error:", e)
"""

HOLDOUT_MD = """### Units-split holdout (the falsifiable core)

Hold out a subset of countries, select on the rest, and read the holdout
verdict: do survivors' slacks hold on **unseen** countries? This is the D7
falsifiable core applied to real data — the part a referee can re-run.
"""

HOLDOUT_CODE = """# Example: hold out 10 countries by isocode (your split — pinned before running).
holdout_units = sorted(country_scores["unit_id"].dropna().unique()[:10].tolist())
print("example holdout (REPLACE with your pre-registered split):", holdout_units)
"""

RUN2_MD = """### Run the real profile + read the report

Once your network and β are authored, run the profile (Python API here; the
CLI `cvprofiles run --scores ... --roles ... --network ... --beta ...` is the
equivalent command). Then read: $M^*$ and rejection reasons, $[L,U]$ on
survivors only, θ/δ surfaces, coverage band when bootstrap is on.
"""

RUN2_CODE = """# When your inputs are frozen, run like this (uncomment once authored):
# real_work = Path("evals/wvs_gps_preferences/data")   # frozen inputs live here
# res = run_profile(
#     scores=str(real_work / "scores.csv"),
#     roles=str(real_work / "roles.json"),
#     network=str(real_work / "network.yaml"),
#     beta=str(real_work / "beta.yaml"),
#     out_dir=str(real_work / "out"),
#     seed=0, n_boot=200, theta_grid_lambdas=[0.5, 1.0, 2.0],
# )
# print(summary_dict(res))
print("Author your network + beta above, then run this cell.")
"""

CONSISTENCY_MD = """### Pipeline-consistency checks (v3.0 honest target)

The v3.0 bar is *observable validation of consistency across the pipeline*:
- cold re-run of the same frozen inputs is **bit-identical** on the freeze core
  (hashes, $M^*$, $L$, $U$, empty flag);
- `package_version`, seed, and hashes travel with every report;
- the JSON/HTML report are generated from the same payload (they cannot
  disagree).
"""

CONSISTENCY_CODE = """# Bit-stability witness on the synthetic run (real runs use the same contract):
import subprocess, sys
out1 = subprocess.run(
    [sys.executable, "-m", "cvprofiles", "run",
     "--scores", str(work / "scores.csv"), "--roles", str(work / "roles.json"),
     "--network", str(work / "network.yaml"), "--beta", str(work / "beta.yaml"),
     "--out", str(work / "cold1"), "--seed", "0"],
    capture_output=True, text=True,
)
out2 = subprocess.run(
    [sys.executable, "-m", "cvprofiles", "run",
     "--scores", str(work / "scores.csv"), "--roles", str(work / "roles.json"),
     "--network", str(work / "network.yaml"), "--beta", str(work / "beta.yaml"),
     "--out", str(work / "cold2"), "--seed", "0"],
    capture_output=True, text=True,
)
assert out1.returncode == 0 and out2.returncode == 0, (out1.stderr, out2.stderr)
j1, j2 = json.loads(out1.stdout), json.loads(out2.stdout)
core = ("run_id", "scores_hash", "network_hash", "beta_hash", "package_version", "seed")
for k in core:
    assert j1.get(k) == j2.get(k), k
print("cold re-run bit-identical on freeze core: PASSED")
"""

CLOSE_MD = """## Where to go next

1. Author the **real** patience + risk networks in Part 2 (construct prose →
   implications → $R$/$\\theta$ → $\\beta$ → anchors).
2. Freeze the inputs under `evals/wvs_gps_preferences/data/`; run the
   **units-split holdout** with your pre-registered country split.
3. Add `verify_wvs_gps.py` (the `verify_h5_trust.py` pattern) and the E2E
   reproducibility pass.
4. Interpret: empty $M^*$ and wide $[L,U]$ are **findings**, not failures.

Remember the honest framing: this lane is an intermediate demo that proves the
pipeline on literature-anchored constructs — the green-light test before
spending resources on IVS data acquisition and the Tao et al. reproduction.
"""


def main() -> None:
    cells = [
        cell("markdown", TITLE, 0),
        cell("markdown", LIT_MD, 1),
        cell("code", IMPORTS, 2),
        cell("markdown", PART1_MD, 3),
        cell("code", PART1_CODE, 4),
        cell("markdown", "### 1.1 roles.json — declare the columns", 5),
        cell("code", ROLES_CODE, 6),
        cell("markdown", "### 1.2 network.yaml — the nomological network", 7),
        cell("code", NETWORK_CODE, 8),
        cell("markdown", "### 1.3 beta.yaml — the target functional", 9),
        cell("code", BETA_CODE, 10),
        cell("markdown", "### 1.4 Run the profile", 11),
        cell("code", RUN_CODE, 12),
        cell("markdown", "### 1.5 Self-check: designed truth recovered", 13),
        cell("code", ASSERT_CODE, 14),
        cell("markdown", HARSH_MD, 15),
        cell("code", HARSH_CODE, 16),
        cell("markdown", DATA_MD, 17),
        cell("code", DATA_PATHS, 18),
        cell("markdown", "### 2.1 Load the local files", 19),
        cell("code", DATA_LOAD, 20),
        cell("markdown", "### 2.2 WVS missing-code discipline + item inventory", 21),
        cell("code", WVS_MASK, 22),
        cell("markdown", "### 2.3 Country-level frame (join at the aggregate level)", 23),
        cell("code", COUNTRY_LEVEL, 24),
        cell("markdown", "### 2.4 Individual-level frame (single survey — no row-binding)", 25),
        cell("code", INDIVIDUAL_LEVEL, 26),
        cell("markdown", AUTHOR_MD, 27),
        cell("code", AUTHOR_NET, 28),
        cell("code", AUTHOR_BETA, 29),
        cell("markdown", HOLDOUT_MD, 30),
        cell("code", HOLDOUT_CODE, 31),
        cell("markdown", RUN2_MD, 32),
        cell("code", RUN2_CODE, 33),
        cell("markdown", CONSISTENCY_MD, 34),
        cell("code", CONSISTENCY_CODE, 35),
        cell("markdown", CLOSE_MD, 36),
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "cvprofiles_wvs_gps_inputs.ipynb"
    path.write_text(json.dumps(nb(cells), indent=1))
    print(f"wrote {path} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
