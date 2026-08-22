"""Level-dependence / DIF diagnostic (paper comment #29; deliverable iii+).

Question: is the pooled-vs-demeaned cell reversal (Q13) driven by
ecological aggregation alone, or does the measurement function itself
depend on level/population?

Design (no item-level microdata — derived frames only):

  A. Variance decomposition per measure: between-country vs within-country
     variance shares of the pooled cell frame.
  B. Country-slope heterogeneity: per-country corr(Q13, q275_cell) and
     corr(GPS patience, q275_cell); distribution + sign counts.
  C. Q13-vs-GPS alignment by level:
       - country level: Corr(Q13_country_mean, GPS_country_mean)
       - pooled cells:  Corr(Q13, gps_patience_cell)
       - within cells:  same after country-demeaning
     If the measurement function were level-invariant, the within-cell
     association should match the country association up to aggregation
     attenuation — a sign flip indicates the score means different things
     at different levels.
  D. Same triple for Q14 as contrast.

Read-only over runs/: writes dif_level_dependence.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"


def var_decomp(frame: pd.DataFrame, col: str, country: pd.Series) -> dict:
    """Between/within variance shares under country grouping."""
    overall = frame[col].var(ddof=1)
    grp = frame.groupby(country)[col]
    between = grp.mean().var(ddof=1)
    within = grp.var(ddof=1).mean()
    total = between + within
    return {
        "var_total": round(float(overall), 4),
        "between_share": round(float(between / total), 3),
        "within_share": round(float(within / total), 3),
    }


def main() -> None:
    pooled = pd.read_csv(RUNS / "patience_cells" / "S_frozen.csv")
    country = pooled["unit_id"].str.split("|").str[0]
    cmeans = pooled.assign(cty=country).groupby("cty")[
        ["m_wvs_q13", "m_wvs_q14", "m_composite", "gps_patience_cell", "q275_cell"]
    ].mean()

    out: dict = {"n_cells": int(len(pooled)), "n_countries": int(country.nunique())}

    # A. variance decomposition
    out["variance_decomposition"] = {
        m: var_decomp(pooled, m, country)
        for m in ["m_wvs_q13", "m_wvs_q14", "m_composite", "gps_patience_cell", "q275_cell"]
    }

    # B. country-slope heterogeneity (within-country corr with education aux)
    slopes = {}
    for m in ["m_wvs_q13", "m_wvs_q14"]:
        cs = []
        for cty, gdf in pooled.groupby(country):
            if len(gdf) >= 4 and gdf["q275_cell"].std() > 0:
                r = gdf[m].corr(gdf["q275_cell"])
                if not np.isnan(r):
                    cs.append(r)
        arr = np.asarray(cs)
        slopes[m] = {
            "n_countries": int(len(arr)),
            "mean": round(float(arr.mean()), 3),
            "median": round(float(np.median(arr)), 3),
            "share_positive": round(float((arr > 0).mean()), 3),
            "q10": round(float(np.quantile(arr, 0.10)), 3),
            "q90": round(float(np.quantile(arr, 0.90)), 3),
        }
    out["country_slopes_vs_education"] = slopes

    # C/D. Q13/Q14 vs GPS patience across levels
    levels = {}
    for m in ["m_wvs_q13", "m_wvs_q14", "m_composite"]:
        pooled_r = float(pooled[m].corr(pooled["gps_patience_cell"]))
        # proper within-cell correlation via country-demeaning
        dem = pooled.assign(cty=country)
        for c in [m, "gps_patience_cell"]:
            dem[c] = dem[c] - dem.groupby("cty")[c].transform("mean")
        within_r = float(dem[m].corr(dem["gps_patience_cell"]))
        country_r = float(cmeans[m].corr(cmeans["gps_patience_cell"]))
        levels[m] = {
            "country_level_corr": round(country_r, 3),
            "pooled_cell_corr": round(pooled_r, 3),
            "within_cell_corr": round(within_r, 3),
        }
    out["measure_vs_gps_by_level"] = levels

    # E. education slack inputs by level for Q13/Q14
    edu = {}
    for m in ["m_wvs_q13", "m_wvs_q14"]:
        country_e = float(cmeans[m].corr(cmeans["q275_cell"]))
        pooled_e = float(pooled[m].corr(pooled["q275_cell"]))
        dem = pooled.assign(cty=country)
        for c in [m, "q275_cell"]:
            dem[c] = dem[c] - dem.groupby("cty")[c].transform("mean")
        within_e = float(dem[m].corr(dem["q275_cell"]))
        edu[m] = {
            "country_level": round(country_e, 3),
            "pooled_cell": round(pooled_e, 3),
            "within_cell": round(within_e, 3),
        }
    out["education_assoc_by_level"] = edu

    dest = ROOT / "dif_level_dependence.json"
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")

    print(f"cells={out['n_cells']} countries={out['n_countries']}")
    print("\nvariance decomposition (between share):")
    for m, d in out["variance_decomposition"].items():
        print(f"  {m:>20s}  between {d['between_share']:.2f} / within {d['within_share']:.2f}")
    print("\ncountry-slope heterogeneity corr(m, q275):")
    for m, d in slopes.items():
        print(f"  {m:>12s} mean {d['mean']:+.3f} median {d['median']:+.3f} "
              f"+share {d['share_positive']:.2f} [{d['q10']:+.2f},{d['q90']:+.2f}] n={d['n_countries']}")
    print("\nmeasure vs GPS patience by level:")
    for m, d in levels.items():
        print(f"  {m:>12s} country {d['country_level_corr']:+.3f}  pooled {d['pooled_cell_corr']:+.3f}  within {d['within_cell_corr']:+.3f}")
    print("\neducation assoc by level:")
    for m, d in edu.items():
        print(f"  {m:>12s} country {d['country_level']:+.3f}  pooled {d['pooled_cell']:+.3f}  within {d['within_cell']:+.3f}")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
