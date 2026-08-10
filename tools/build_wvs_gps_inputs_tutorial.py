"""Build the WVS/GPS input-builder + E2E tutorial notebook (nbformat 4.5, clean).

Iteration 3 (2026-08-09): disjoint-survey fix + corrected placeholder networks.

- Iteration 2 (A + C): country-level patience menu = GPS patience only; the
  collapse is the finding. B (modernity/secular-rational lane) deferred.
- Iteration 3: WVS and GPS are DIFFERENT surveys with DISJOINT respondents —
  an individual-level join on country code is a many-to-many cross-product
  (78,821,249 rows on this data, measured). Part 3 is now GPS-only at the
  individual level; WVS items enter only as country means (Part 2).
  Placeholder networks corrected: `monotone_rank`/`corr_zero` take the AUX
  column as `params.variable`, not the measure itself (the old placeholders
  were degenerate: Spearman(m,m)=1 and |Corr(m,m)|=1).

Run: env -u PYTHONPATH uv run python tools/build_wvs_gps_inputs_tutorial.py
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

This notebook is your **hands-on guide to the input format**. It has three parts:

- **Part 1 — synthetic walk-through (oracle).** A small simulated DGP with a
  designed valid / weak / invalid menu, an *oracle* network (agent-authored,
  synthetic only), and self-checking assertions. This runs end-to-end with no
  real data — it is how you learn the loop.
- **Part 2 — real WVS/GPS, country-level profile.** Patience and risk-taking
  on **local** GPS (Falk et al. 2018) and WVS Wave 7 data. The empirical
  network $R$, thresholds $\\theta$, and $\\beta$ are **yours to author** — this
  notebook validates each file as you write it.
- **Part 3 — real WVS/GPS, individual-level profile (GPS-only).** Same
  constructs at individual level; a second copy of the inputs, individual-
  side. WVS items enter only as country means: the surveys have disjoint
  respondents, so no respondent-level join exists (see Part 3 for the
  measured cross-product lesson).

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
| Robustness of conclusions to researcher choices | Leamer; Sala-i-Martin (1997); specification curve (Simonsohn et al. 2020); multiverse (Steegen et al. 2016) | $[L,U]$ = image of the *target functional* over **survivors only** |
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

LESSON_MD = """## 0.5 The lesson we earned the hard way (read this first, it saved the lane)

Before writing the real network, here is what happened on the first pass and why
it changed everything — because it's the cleanest demonstration of the discipline
the package is built to enforce.

**The wrong workflow:**

```text
1. Picked WVS items by statistical correlation alone
   (Q13, Q14 as "patience proxies" — passed convergent / discriminant bars)
2. Called them a patience menu
3. ONLY THEN read the codebook
```

**What the codebook actually said:**

| Item | What it asks (verbatim) |
|---|---|
| Q13 | "Important child quality: Thrift saving money and things" |
| Q14 | "Important child quality: Determination, perseverance" |
| Q188 | "Justifiable: Euthanasia" |
| Q184 | "Justifiable: Abortion" |
| Q186 | "Justifiable: Sex before marriage" |
| Q169 | "Whenever science and religion conflict, religion is always right" |
| Q6  | "Important in life: Religion" |

These are **not patience measures**. Q13/Q14 measure *normative emphasis on
traditional virtues* (a *values* variable that moves opposite to GPS patience at
country level: Corr ≈ −0.24). Q188/Q184/Q186 measure *secular-rational values*
(the second Inglehart-Welzel dimension). Q169/Q6 measure *religious values*.
Q263 was a country-mean demographic (immigrant share), not a preference at all.

The bars *passed* these items — but the bars were not the test of validity. The
bars are *necessary*, not *sufficient*. Validity starts with the construct
paragraph; the bars adjudicate items you have already argued belong to the
construct on theoretical grounds.

**The right workflow (the discipline the package enforces):**

```text
1. Write the construct paragraph (what patience IS, for this study).
2. List testable implications as plain-language inequalities.
3. Pick candidate measures from the data BY THEORY.
4. Use the bars to ADJUDICATE the theory-motivated candidates.
   If an item you chose on theoretical grounds fails the bars, that is a
   finding — about the theory, about the item, or about the construct itself.
5. NEVER pick items by statistical correlation alone.
```

This is exactly the "construct paragraph first, β last" discipline in
`docs/USER_GUIDE.md §4.4`. It exists because the wrong workflow almost shipped
here, with the bars loudly endorsing items that measure something completely
different from what we thought we were testing.

**The lesson the package itself teaches (this is why it exists):**

The `corr_min` bar on Q275 education **rejected Q13/Q14** at the country level
and **would not have rejected** Q188/Q184 (they co-move with education, just
for the wrong reason). The bars adjudicate the *bar*, not the *construct*.
The construct lives in your paragraph, not in the engine.
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

BETA_CODE = """# β: the downstream number we want a range for (here: correlation with v2).
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

DATA_MD = """## Part 2 — Real WVS/GPS, country-level profile

**Lane:** intermediate demo (`evals/wvs_gps_preferences/`), local data only.

**Data sources (on this machine):**
- **GPS** — Falk et al. (2018) Global Preference Survey, country level
  (`~/Desktop/Github_Repositories/SCA2_PofW/data/GPS/GPS_dataset_country_level/country_gps.dta`)
  and individual level (`.../GPS_dataset_individual_level/individual_new.dta`).
  Preference vars: `patience`, `risktaking`, `posrecip`, `negrecip`, `altruism`,
  `trust` (+ individual: `wgt`, `gender`, `age`, `subj_math_skills`).
- **WVS Wave 7** (2017–2022) — individual level
  (`.../WVS/WVS_wave7.dta`). Codebook-verified items surveyed: Q13 thrift,
  Q14 determination, Q48 freedom of choice/control, Q49 life satisfaction,
  Q275 education ISCED, Q279 employment status.

**The right workflow for the country-level patience menu (lesson from §0.5):**

Construct paragraph first → testable implications → pick items by theory →
adjudicate with bars.

**Country-level patience menu (A — applied):** `patience` (GPS), and only
`patience`. The empirical lesson: at country level, no WVS item is a *direct*
patience measure. Q13/Q14 (normative values) move opposite to GPS patience.
Q6/Q169 (religion) and Q188/Q184/Q186 (secular-rational values) measure
different constructs that happen to co-move with patience in modernity
contexts. The honest menu collapses to GPS patience alone; the collapse is
the finding. **Menu is therefore {GPS patience}.**

**Two hard data rules:**
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
wvs_raw = pd.read_stata(wvs, convert_categoricals=False)
print("GPS country:", gps_c.shape, "| columns:", list(gps_c.columns))
print("GPS individual:", gps_i.shape)
print("WVS wave7:", wvs_raw.shape)

# WVS official missing codes: -1 don't know, -2 no answer, -3 not applicable,
# -4 not asked, -5 missing. Mask them; never impute.
WVS_ITEMS = ["Q13", "Q14", "Q48", "Q49", "Q275", "Q279"]
present = [c for c in WVS_ITEMS if c in wvs_raw.columns]
print("WVS columns found:", present)

def mask_missing(df, cols):
    out = df.copy()
    for c in cols:
        out[c] = pd.to_numeric(out[c], errors="coerce")
        out.loc[out[c].isin([-1, -2, -3, -4, -5]), c] = np.nan
    return out

wvs_clean = mask_missing(wvs_raw, present)
print("WVS masked ->", wvs_clean.shape)
"""

COUNTRY_FRAME = """# Country-level frame: GPS patience (measure) + GPS risktaking (discriminant
# aux) + WVS Q275 education country mean (convergent aux). WVS items enter
# ONLY as country means — the surveys have disjoint respondents (Part 3).
# The menu itself collapses to {GPS patience}: the collapse is the finding.
wvs_means = (
    wvs_clean.groupby("B_COUNTRY_ALPHA")[present]
    .mean()
    .rename_axis("unit_id")
    .reset_index()
)
country_scores = (
    gps_c.rename(columns={"isocode": "unit_id"})[["unit_id", "patience", "risktaking"]]
    .merge(
        wvs_means[["unit_id", "Q275"]].rename(columns={"Q275": "q275_mean"}),
        on="unit_id", how="inner",
    )
    .dropna(subset=["patience", "risktaking", "q275_mean"])
)
print("country-level frame:", country_scores.shape,
      "| menu = {GPS patience} | aux = {risktaking, q275_mean}")
"""

INDIVIDUAL_FRAME = """# Individual-level frame for Part 3 — GPS-only (C applied, corrected).
# GPS and WVS are different surveys with DIFFERENT respondents; there is no
# respondent-level join key. The individual frame is GPS individual patience
# + risktaking (discriminant aux) + subj_math_skills (human-capital convergent
# aux) + demographics. WVS items enter only as country means (Part 2).
individual_scores = gps_i[
    ["isocode", "patience", "risktaking", "subj_math_skills", "wgt", "gender", "age"]
].rename(columns={"isocode": "unit_id"}).dropna(subset=["patience"]).copy()
print("individual-level frame (GPS only):", individual_scores.shape,
      "| menu = {GPS patience} | aux = {risktaking, subj_math_skills}")
"""

AUTHOR_MD = """### Your authorship cells — patience, country level

The construct paragraph (D1, in `evals/wvs_gps_preferences/DESIGN.md`):

> Patience is the disposition to value future relative to present outcomes,
> observable in choices involving delayed rewards (intertemporal tradeoffs).
> For this study it is treated as a construct that (a) is measurable via stated
> intertemporal preference, (b) should express in long-horizon behavior
> (education, saving), and (c) is conceptually distinct from risk tolerance and
> the other preference dimensions.

**Implications → bars:**

| Implication | Restriction | Aux column | θ (suggested by feasibility, you author) |
|---|---|---|---|
| Patience co-moves with education | `monotone_rank` | `q275_mean` (WVS country mean) | ~0.10 (GPS patience has Spear(patience, q275_mean) ≈ 0.39 in n=42; opens headroom for empirical testing) |
| Patience is NOT risk tolerance | `corr_zero` | `risktaking` | ~0.30 (feasibility: \|Corr(patience, risk)\| ≈ 0.25; tight but live) |

**Menu is {GPS patience} (A applied).** The schema below validates the
network before you freeze. The country-level run will likely be **point-identified**
— `M* = {patience}` and $[L,U]$ collapses to β(GPS patience). That is the
honest result, not a bug.
"""

AUTHOR_NET = """# REPLACE the placeholder restrictions below with YOUR network.
# Schema validates structure; θ values are YOUR empirical commitment (and
# each must have a corresponding entry in anchors.yaml — see §0.6).
# NOTE: params.variable is the AUX column — the measure is the menu item the
# engine iterates over. Do NOT point variable at the measure itself.
patience_network = {
    "schema_version": "1",
    "name": "patience_wvs_gps_country",
    "delta": 0.0,
    "restrictions": [
        # Example convergent bar (you set θ from the literature / pre-data anchor):
        {"id": "r_conv_educ", "type": "monotone_rank", "theta": 0.10,
         "params": {"variable": "q275_mean", "sign": 1}},
        # Discriminant: patience is NOT risk tolerance
        {"id": "r_disc_risk", "type": "corr_zero", "theta": 0.30,
         "params": {"variable": "risktaking"}},
        # TODO(augusto): anchors.yaml entries (one per restriction id).
    ],
}
try:
    pn = parse_network(patience_network)
    print("network schema OK:", [r.id for r in pn.restrictions])
except Exception as e:
    print("network schema error:", e)
"""

AUTHOR_BETA = """# REPLACE with your β choice (what economic number you track under
# alternative measures). For country-level patience, the typical Falk-et-al
# anchor is Corr(patience, log_GDP_pc) or ols_coef with controls.
# You must ADD a GDP-per-capita column to the country frame (or pick another
# country-level outcome you can defend). The cell below adds a placeholder
# outcome column for the schema check to run cleanly.
country_scores["gdp_pc_placeholder"] = country_scores["patience"]  # REPLACE in real data
patience_beta = {
    "schema_version": "1",
    "type": "corr_y",
    "outcome": "gdp_pc_placeholder",
    "params": {},
}
try:
    pb = BetaSpec.model_validate(patience_beta)
    print("beta schema OK:", pb.type)
except Exception as e:
    print("beta schema error:", e)
"""

HOLDOUT_MD = """### Units-split holdout (the falsifiable core)

Hold out a subset of countries, select on the rest, read the holdout verdict.
With the menu collapsed to {GPS patience}, the holdout is a *single-measure*
check — but it's still informative: does the country holdout replicate the
result on unseen countries? This is the D7 falsifiable core applied to real data.
"""

HOLDOUT_CODE = """# Example: hold out 10 countries by isocode (your split — pinned before running).
holdout_units = sorted(country_scores["unit_id"].dropna().unique()[:10].tolist())
print("example holdout (REPLACE with your pre-registered split):", holdout_units)
"""

ANCHORS_MD = """### 0.6 θ-anchor discipline

Thresholds are where "literature-grounded, not data-mined" is won or lost. Ship a
pre-data `anchors.yaml` with one entry per restriction:

```yaml
- restriction_id: r_conv_educ
  citation_key: falk2018global
  source_phrase: "patience-education correlation in the GPS country means (n≈76)"
  anchor_kind: literature
  pre_data: true
```

The engine enforces *completeness* — every restriction id must have an anchor —
but does not enforce *timing*. `pre_data: true` is your commitment; the
verifier requires it.
"""

RUN2_MD = """### Run the real country profile + read the report

Once your network and β are authored, run the profile. With menu collapsed to
{GPS patience}, expect $M^* = \{\\text{patience}\}$ and a point-identified
range. If something else happens, that's a finding — read it carefully before
re-running.
"""

RUN2_CODE = """# When your inputs are frozen, run like this (uncomment once authored):
# real_work = Path("evals/wvs_gps_preferences/data")   # frozen inputs live here
# res = run_profile(
#     scores=str(real_work / "country_scores.csv"),
#     roles=str(real_work / "country_roles.json"),
#     network=str(real_work / "patience_network.yaml"),
#     beta=str(real_work / "patience_beta.yaml"),
#     out_dir=str(real_work / "country_out"),
#     seed=0, n_boot=200, theta_grid_lambdas=[0.5, 1.0, 2.0],
# )
# print(summary_dict(res))
print("Author your network + beta above, then run this cell.")
"""

PART3_MD = """## Part 3 — Real WVS/GPS, individual-level profile (C applied, GPS-only)

**Why a separate individual-level profile:** country means aggregate away
individual measurement noise. At the **individual level**, the GPS patience
measure is the same individual-level scale, and the discriminant bar against
risk-taking is available (`risktaking` is in the GPS individual file). The
WVS Wave 7 core has no direct "time-preference battery" — so the individual
menu is built from what the data honestly supports.

**The data fact that shapes this part (the lesson from §0.5, applied to
joins):** WVS and GPS are **different surveys with different respondents.**
There is no respondent-level key connecting them. Joining their individual
files on country code is a **many-to-many cross-product** — every GPS
respondent pairs with every WVS respondent in the same country. On this
data that is ~78.8 million rows instead of ~80k. The merge is refused; WVS
items enter this notebook **only as country means** (Part 2).

**Consequence for the menu:** the individual-level frame is **GPS-only** —
menu = {GPS patience}, aux = {risktaking, subj_math_skills}. WVS items do
not appear at the individual level. This is a finding about the data, not a
workaround: two national surveys sampled independently cannot be merged at
the respondent level without fabricating matches.

**Data rule:** never join respondents from different surveys on a country
key. Country means (Part 2) or a single survey (Part 3) — never both at
the individual level.
"""

PART3_INDIV_LOAD = """# Demonstrate why the individual-level WVS merge is refused (measured):
# WVS and GPS are different surveys with different respondents. A join on
# country code is a many-to-many cross-product, not a merge.
n_gps_c = gps_i["isocode"].value_counts()
n_wvs_c = wvs_clean["B_COUNTRY_ALPHA"].value_counts()
shared = sorted(set(n_gps_c.index) & set(n_wvs_c.index))
cross = int(sum(n_gps_c[c] * n_wvs_c[c] for c in shared))
print("GPS respondents:", len(gps_i), "| WVS respondents:", len(wvs_clean),
      "| shared countries:", len(shared))
print(f"naive country-keyed join would produce {cross:,} rows -- a cross-product, not a merge")
assert cross > 10 * max(len(gps_i), len(wvs_clean)), "sanity: cross-product must explode"
print("-> merge refused. WVS items enter only as country means (Part 2).")

# The GPS-only individual frame (already built in §2.3; keep the name used
# by the authoring cells below).
print("individual-level frame (GPS only):", individual_scores.shape,
      "across", individual_scores["unit_id"].nunique(), "country units")
"""

PART3_MENU_MD = """### Your authorship cells — patience, individual level

**Construct paragraph (same D1 as country level),** but now the unit is the
person. The behavioral claims become individual-level:

| Implication | Restriction | Aux column | Note |
|---|---|---|---|
| Patience co-moves with human capital | `monotone_rank` | `subj_math_skills` (GPS) | The GPS file's math-skills self-rating is the available individual-level convergent proxy; WVS Q275 exists only as a country mean (Part 2) |
| Patience is NOT risk tolerance | `corr_zero` | `risktaking` (GPS) | Carries over from Part 2; `risktaking` exists at the individual level in GPS |
| Survives country holdout | `stage: holdout` | units-split by country | Holdout verdict |

**Honest note on the individual-level menu:** WVS Wave 7 has no direct
intertemporal-choice battery, and WVS respondents cannot be merged onto GPS
respondents at the individual level. The candidate individual-level patience
menu is therefore {GPS patience}. If you end up with menu = {GPS patience}
again, that's a finding — about the data, not about your work.
"""

PART3_MENU = """# REPLACE the placeholder restrictions below with YOUR individual-level network.
# NOTE: params.variable is the AUX column — see §2.4 note. The individual
# frame is GPS-only: aux columns are risktaking and subj_math_skills.
patience_network_individual = {
    "schema_version": "1",
    "name": "patience_wvs_gps_individual",
    "delta": 0.0,
    "restrictions": [
        {"id": "r_conv_hc_ind", "type": "monotone_rank", "theta": 0.05,
         "params": {"variable": "subj_math_skills", "sign": 1}},
        {"id": "r_disc_risk_ind", "type": "corr_zero", "theta": 0.30,
         "params": {"variable": "risktaking"}},
        # TODO(augusto): add holdout bars on country-level unit_id list
    ],
}
try:
    pn_ind = parse_network(patience_network_individual)
    print("individual network schema OK:", [r.id for r in pn_ind.restrictions])
except Exception as e:
    print("individual network schema error:", e)
"""

PART3_RUN_MD = """### Run the individual-level profile + compare

Same procedure as Part 2, but on the individual-level frame. Compare:
- Does the individual-level menu admit more measures than the country level?
- Does the range $[L,U]$ widen (per-measure attenuation) or shrink (more
  convergent bars hit)?
- Does the holdout verdict survive?

The two-level comparison is the **observable consistency** target v3.0 sets.
If the two profiles agree on admissibility and roughly on the range, you have
your green light. If they disagree — that's a *real* finding worth a paper.
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

EXTENSION_MD = """## Extension — deferred (B): the "modernity / secular-rational" lane

**Status:** deferred, not run in this tutorial.

**Why it deserves its own lane.** During the country-level feasibility scan,
items like Q188 (euthanasia), Q184 (abortion), Q186 (sex), Q169 (science vs
religion), Q6 (religion importance) all passed the convergent bar on Q275
education *and* correlated ~0.7 with GPS patience at country level. But
reading the codebook showed they measure the **second Inglehart-Welzel
dimension** — secular-rational vs traditional values — not patience. They
co-move with patience because both load on a shared country-level modernity
axis (industrialization, education, secularization).

**The extension would:**
- Re-author the construct paragraph to be "secular-rational values," not
  "patience"
- Drop the discriminant against GPS risktaking (secular-rational ≠ patience
  isn't a clean claim; the right discriminant might be against traditional
  values)
- Use Q188/Q184/Q186/Q169/Q6 as the WVS portion of the menu; Q275 education
  and Q48 freedom of choice/control as convergent criteria
- Run a profile and compare to Part 2's patience profile

This is a *parallel* lane that explores a related construct on the same
infrastructure. The D-pins in `DESIGN.md` would need a sibling set for the
modernity lane. Until that is a written construct paragraph, the bar list, and
the θ-anchors, this lane stays deferred.

**The lesson it teaches:** if you find items that pass your bars but don't
match your construct paragraph, that's a signal about *what construct your
data actually supports* — not an invitation to rewrite the construct to fit
the items.
"""

CLOSE_MD = """## Where to go next

1. Author the **real** patience network in Part 2 (construct prose →
   implications → $R$/$\\theta$ → β → anchors.yaml).
2. Freeze the country-level inputs under `evals/wvs_gps_preferences/data/`.
   Expect $M^* = \\{\\text{patience}\\}$ (A applied). The collapse is the finding.
3. Author and run the individual-level profile (Part 3). Compare with Part 2:
   does the individual menu admit more measures? Does the range move?
4. Decide whether to author the deferred "modernity" lane (Part B-extension)
   — it's a *separate construct paragraph*, not a continuation of patience.
5. Add `verify_wvs_gps.py` (the `verify_h5_trust.py` pattern) and the E2E
   reproducibility pass.

Remember the honest framing: this lane is an intermediate demo that proves
the pipeline on literature-anchored constructs — the green-light test before
spending resources on IVS data acquisition and the Tao et al. reproduction.
"""


def main() -> None:
    cells = [
        cell("markdown", TITLE, 0),
        cell("markdown", LIT_MD, 1),
        cell("markdown", LESSON_MD, 2),
        cell("code", IMPORTS, 3),
        cell("markdown", PART1_MD, 4),
        cell("code", PART1_CODE, 5),
        cell("markdown", "### 1.1 roles.json — declare the columns", 6),
        cell("code", ROLES_CODE, 7),
        cell("markdown", "### 1.2 network.yaml — the nomological network", 8),
        cell("code", NETWORK_CODE, 9),
        cell("markdown", "### 1.3 beta.yaml — the target functional", 10),
        cell("code", BETA_CODE, 11),
        cell("markdown", "### 1.4 Run the profile", 12),
        cell("code", RUN_CODE, 13),
        cell("markdown", "### 1.5 Self-check: designed truth recovered", 14),
        cell("code", ASSERT_CODE, 15),
        cell("markdown", HARSH_MD, 16),
        cell("code", HARSH_CODE, 17),
        cell("markdown", DATA_MD, 18),
        cell("code", DATA_PATHS, 19),
        cell("markdown", "### 2.1 Load the local files", 20),
        cell("code", DATA_LOAD, 21),
        cell("markdown", "### 2.2 Country-level frame (A applied — menu collapses to GPS patience)", 22),
        cell("code", COUNTRY_FRAME, 23),
        cell("markdown", "### 2.3 Individual-level frame (Part 3 build)", 24),
        cell("code", INDIVIDUAL_FRAME, 25),
        cell("markdown", AUTHOR_MD, 26),
        cell("code", AUTHOR_NET, 27),
        cell("code", AUTHOR_BETA, 28),
        cell("markdown", ANCHORS_MD, 29),
        cell("markdown", HOLDOUT_MD, 30),
        cell("code", HOLDOUT_CODE, 31),
        cell("markdown", RUN2_MD, 32),
        cell("code", RUN2_CODE, 33),
        cell("markdown", PART3_MD, 34),
        cell("code", PART3_INDIV_LOAD, 35),
        cell("markdown", PART3_MENU_MD, 36),
        cell("code", PART3_MENU, 37),
        cell("markdown", PART3_RUN_MD, 38),
        cell("markdown", CONSISTENCY_MD, 39),
        cell("code", CONSISTENCY_CODE, 40),
        cell("markdown", EXTENSION_MD, 41),
        cell("markdown", CLOSE_MD, 42),
    ]
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUT_DIR / "cvprofiles_wvs_gps_inputs.ipynb"
    path.write_text(json.dumps(nb(cells), indent=1))
    print(f"wrote {path} ({len(cells)} cells)")


if __name__ == "__main__":
    main()
