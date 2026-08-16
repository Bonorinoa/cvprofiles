"""Build country and cell-mean score tables for the two-resolution lane.

Reuse frozen country columns when a rebuild matches to ~1e-12.
Never inspect slacks. Not imported from src/.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SCA2 = Path("/Users/bonorinoa/Desktop/Github_Repositories/SCA2_PofW")
GPS_C = SCA2 / "data/GPS/GPS_dataset_country_level/country_gps.dta"
GPS_I = SCA2 / "data/GPS/GPS_dataset_individual_level/individual_new.dta"
WVS = SCA2 / "data/WVS/WVS_wave7.dta"
PATIENCE_FROZEN = ROOT.parents[1] / "evals/wvs_gps_preferences/data/inputs/scores.csv"
H5_FROZEN = ROOT.parents[1] / "evals/h5_trust/data/scores.csv"
WDI = ROOT.parents[1] / "evals/wvs_gps_preferences/data/aux/wdi.csv"
DATA = ROOT / "data"
DATA.mkdir(parents=True, exist_ok=True)

MISSING = {-1, -2, -3, -4, -5}
FLOOR = 30
CELL_MIN_N = 20
MIN_CELLS = 6
AGE_BINS = [18, 25, 35, 45, 55, 65, 200]
AGE_LABELS = ["18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
SEED = 20260814

TRUST_ITEMS = {
    "m_trust_general": ["Q57"],
    "m_trust_in_group": ["Q58", "Q60"],
    "m_trust_out_group": ["Q61", "Q62", "Q63"],
    "m_trust_institution": ["Q64", "Q69", "Q70", "Q71"],
}


def mask(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce")
    return x.where(x >= 0)


def zscore(s: pd.Series) -> pd.Series:
    v = s.to_numpy(dtype=float)
    return pd.Series((v - v.mean()) / v.std(ddof=0), index=s.index)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def load_wvs() -> pd.DataFrame:
    return pd.read_stata(WVS, convert_categoricals=False)


def wvs_country_col(df: pd.DataFrame) -> str:
    for c in ("B_COUNTRY_ALPHA", "country", "COUNTRY_ALPHA"):
        if c in df.columns:
            return c
    raise ValueError(f"no country column in WVS: {list(df.columns)[:20]}")


def rebuild_patience_country(wvs: pd.DataFrame) -> pd.DataFrame:
    cc = wvs_country_col(wvs)
    tmp = wvs[[cc, "Q13", "Q14", "Q275"]].copy()
    for c in ("Q13", "Q14", "Q275"):
        tmp[c] = mask(tmp[c])
    counts = tmp.groupby(cc)[["Q13", "Q14", "Q275"]].count()
    keep = counts[counts.min(axis=1) >= FLOOR].index
    means = tmp[tmp[cc].isin(keep)].groupby(cc)[["Q13", "Q14", "Q275"]].mean()
    out = means.rename_axis("unit_id").reset_index()
    out = out.rename(columns={"Q13": "m_wvs_q13", "Q14": "m_wvs_q14", "Q275": "q275_mean"})
    return out


def rebuild_trust_country(wvs: pd.DataFrame) -> pd.DataFrame:
    cc = wvs_country_col(wvs)
    cols = [cc] + [i for items in TRUST_ITEMS.values() for i in items]
    tmp = wvs[cols].copy()
    for c in tmp.columns:
        if c == cc:
            continue
        tmp[c] = mask(tmp[c])
    # Q57: 1 = most people can be trusted → share
    tmp["m_trust_general"] = (tmp["Q57"] == 1).where(tmp["Q57"].notna())
    for name, items in TRUST_ITEMS.items():
        if name == "m_trust_general":
            continue
        recoded = []
        for it in items:
            recoded.append((5.0 - tmp[it]) / 4.0)
        tmp[name] = pd.concat(recoded, axis=1).mean(axis=1, skipna=True)
    use = ["m_trust_general", "m_trust_in_group", "m_trust_out_group", "m_trust_institution"]
    counts = tmp.groupby(cc)[use].count()
    keep = counts[counts.min(axis=1) >= FLOOR].index
    means = tmp[tmp[cc].isin(keep)].groupby(cc)[use].mean()
    n = tmp[tmp[cc].isin(keep)].groupby(cc)[use].count().add_prefix("n_")
    out = means.join(n).rename_axis("unit_id").reset_index()
    return out


def max_abs_diff(a: pd.DataFrame, b: pd.DataFrame, on: str, cols: list[str]) -> dict:
    m = a.merge(b, on=on, suffixes=("_a", "_b"))
    out = {}
    for c in cols:
        d = (m[f"{c}_a"] - m[f"{c}_b"]).abs()
        out[c] = {"n": int(d.notna().sum()), "max_abs": float(d.max()) if len(d) else None}
    return out


def age_band(age: pd.Series) -> pd.Series:
    return pd.cut(age, bins=AGE_BINS, right=False, labels=AGE_LABELS)


def build_cells() -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    gps = pd.read_stata(GPS_I)
    wvs = load_wvs()
    cc = wvs_country_col(wvs)

    g = gps[["isocode", "gender", "age", "patience", "trust"]].copy()
    g["age"] = pd.to_numeric(g["age"], errors="coerce")
    g = g[g["age"] >= 18]
    g["sex"] = pd.Series(pd.NA, index=g.index, dtype="string")
    g.loc[g["gender"] == 1, "sex"] = "F"
    g.loc[g["gender"] == 0, "sex"] = "M"
    g["band"] = age_band(g["age"])
    g = g.dropna(subset=["isocode", "sex", "band"])
    gps_cells = (
        g.groupby(["isocode", "sex", "band"], observed=True)
        .agg(
            gps_patience_cell=("patience", "mean"),
            gps_trust_cell=("trust", "mean"),
            n_gps=("patience", "size"),
        )
        .reset_index()
    )
    gps_cells = gps_cells[gps_cells["n_gps"] >= CELL_MIN_N]

    w = wvs[[cc, "Q260", "Q262", "Q275", "Q13", "Q14", "Q57", "Q58", "Q60",
             "Q61", "Q62", "Q63", "Q64", "Q69", "Q70", "Q71"]].copy()
    w["age"] = mask(w["Q262"])
    w = w[w["age"] >= 18]
    w["sex"] = pd.Series(pd.NA, index=w.index, dtype="string")
    w.loc[w["Q260"] == 2, "sex"] = "F"
    w.loc[w["Q260"] == 1, "sex"] = "M"
    w["band"] = age_band(w["age"])
    w["m_wvs_q13"] = mask(w["Q13"])
    w["m_wvs_q14"] = mask(w["Q14"])
    w["q275_cell"] = mask(w["Q275"])
    w["m_trust_general"] = (mask(w["Q57"]) == 1).where(mask(w["Q57"]).notna())
    for name, items in TRUST_ITEMS.items():
        if name == "m_trust_general":
            continue
        recoded = [(5.0 - mask(w[it])) / 4.0 for it in items]
        w[name] = pd.concat(recoded, axis=1).mean(axis=1, skipna=True)
    w = w.dropna(subset=[cc, "sex", "band"])
    wvs_cells = (
        w.groupby([cc, "sex", "band"], observed=True)
        .agg(
            m_wvs_q13=("m_wvs_q13", "mean"),
            m_wvs_q14=("m_wvs_q14", "mean"),
            q275_cell=("q275_cell", "mean"),
            n_wvs=("m_wvs_q13", "size"),
            m_trust_general=("m_trust_general", "mean"),
            m_trust_in_group=("m_trust_in_group", "mean"),
            m_trust_out_group=("m_trust_out_group", "mean"),
            m_trust_institution=("m_trust_institution", "mean"),
        )
        .reset_index()
        .rename(columns={cc: "isocode"})
    )
    wvs_cells = wvs_cells[wvs_cells["n_wvs"] >= CELL_MIN_N]

    cells = gps_cells.merge(wvs_cells, on=["isocode", "sex", "band"], how="inner")
    n_per = cells.groupby("isocode").size()
    keep = n_per[n_per >= MIN_CELLS].index
    cells = cells[cells["isocode"].isin(keep)].copy()
    cells["unit_id"] = (
        cells["isocode"].astype(str) + "|" + cells["sex"].astype(str) + "|" + cells["band"].astype(str)
    )
    cells["m_composite"] = zscore(cells["m_wvs_q13"]) + zscore(cells["m_wvs_q14"])
    cells["m_trust_composite"] = cells[
        ["m_trust_in_group", "m_trust_out_group", "m_trust_institution"]
    ].mean(axis=1)
    rng_p = np.random.default_rng(SEED + 2)
    rng_t = np.random.default_rng(SEED + 3)
    cells["m_noise_patience"] = rng_p.normal(size=len(cells))
    cells["m_noise_trust"] = rng_t.normal(size=len(cells))
    meta = {
        "n_cells": int(len(cells)),
        "n_countries": int(cells["isocode"].nunique()),
        "min_cell_n": CELL_MIN_N,
        "min_cells_per_country": MIN_CELLS,
    }
    return cells, gps_cells, meta


def main() -> None:
    wvs = load_wvs()
    gps_c = pd.read_stata(GPS_C)
    wdi = pd.read_csv(WDI)
    h5 = pd.read_csv(H5_FROZEN)
    pat_f = pd.read_csv(PATIENCE_FROZEN)

    pat_r = rebuild_patience_country(wvs)
    tru_r = rebuild_trust_country(wvs)

    cmp_pat = max_abs_diff(
        pat_r,
        pat_f.rename(columns={"unit_id": "unit_id"}),
        "unit_id",
        ["m_wvs_q13", "m_wvs_q14", "q275_mean"],
    )
    h5_cmp = h5.rename(columns={"iso3": "unit_id"})
    cmp_tru = max_abs_diff(
        tru_r,
        h5_cmp,
        "unit_id",
        ["m_trust_general", "m_trust_in_group", "m_trust_out_group", "m_trust_institution"],
    )
    def _close(cmp: dict) -> bool:
        return all(
            v["max_abs"] is not None and v["max_abs"] < 1e-10 for v in cmp.values()
        )

    reuse_pat = _close(cmp_pat)
    reuse_tru = _close(cmp_tru)

    gps_s = gps_c[["isocode", "patience", "risktaking", "trust"]].rename(
        columns={"isocode": "unit_id", "patience": "m_gps_patience", "trust": "m_gps_trust"}
    )
    wdi_s = wdi.rename(columns={"iso3": "unit_id"})
    h5_aux = h5.rename(columns={"iso3": "unit_id"})[["unit_id", "rule_of_law", "gini"]]

    # Country patience: reuse frozen human columns if they match; always drop LLM arms.
    if reuse_pat:
        country_p = pat_f[["unit_id", "m_gps_patience", "m_wvs_q13", "m_wvs_q14",
                           "m_composite", "m_noise", "risktaking", "q275_mean", "log_gdp_pc"]].copy()
        source_p = "reused_frozen_patience_inputs"
    else:
        merged = gps_s.merge(pat_r, on="unit_id").merge(wdi_s, on="unit_id")
        merged["m_composite"] = zscore(merged["m_wvs_q13"]) + zscore(merged["m_wvs_q14"])
        merged["m_noise"] = np.random.default_rng(SEED).normal(size=len(merged))
        country_p = merged[["unit_id", "m_gps_patience", "m_wvs_q13", "m_wvs_q14",
                            "m_composite", "m_noise", "risktaking", "q275_mean", "log_gdp_pc"]]
        source_p = "rebuilt"

    # Country trust
    if reuse_tru:
        country_t = h5_cmp[["unit_id", "m_trust_general", "m_trust_in_group",
                            "m_trust_out_group", "m_trust_institution",
                            "gps_trust", "rule_of_law", "gini", "log_gdp_pc"]].copy()
        country_t = country_t.rename(columns={"gps_trust": "m_gps_trust"})
        country_t = country_t.merge(country_p[["unit_id", "q275_mean"]], on="unit_id", how="inner")
        source_t = "reused_h5_plus_q275"
    else:
        country_t = tru_r.merge(gps_s[["unit_id", "m_gps_trust"]], on="unit_id")
        country_t = country_t.merge(h5_aux, on="unit_id", how="inner")
        country_t = country_t.merge(country_p[["unit_id", "q275_mean", "log_gdp_pc"]], on="unit_id")
        source_t = "rebuilt"
    country_t["m_trust_composite"] = country_t[
        ["m_trust_in_group", "m_trust_out_group", "m_trust_institution"]
    ].mean(axis=1)
    if "m_noise" not in country_t.columns:
        country_t["m_noise"] = np.random.default_rng(SEED + 1).normal(size=len(country_t))

    cells, _, cell_meta = build_cells()
    pat_cells = cells[[
        "unit_id", "m_wvs_q13", "m_wvs_q14", "m_composite",
        "q275_cell", "gps_patience_cell",
    ]].copy()
    pat_cells["m_noise"] = cells["m_noise_patience"]
    tru_cells = cells[[
        "unit_id", "m_trust_general", "m_trust_in_group", "m_trust_out_group",
        "m_trust_institution", "m_trust_composite", "q275_cell", "gps_trust_cell",
    ]].copy()
    tru_cells["m_noise"] = cells["m_noise_trust"]

    DATA.mkdir(parents=True, exist_ok=True)
    (DATA / "country").mkdir(exist_ok=True)
    (DATA / "cells").mkdir(exist_ok=True)
    country_p.to_csv(DATA / "country/patience.csv", index=False)
    country_t.to_csv(DATA / "country/trust.csv", index=False)
    pat_cells.to_csv(DATA / "cells/patience.csv", index=False)
    tru_cells.to_csv(DATA / "cells/trust.csv", index=False)

    manifest = {
        "seed": SEED,
        "respondent_floor": FLOOR,
        "reuse_patience": reuse_pat,
        "reuse_trust": reuse_tru,
        "source_patience": source_p,
        "source_trust": source_t,
        "compare_patience": cmp_pat,
        "compare_trust": cmp_tru,
        "n_patience_country": int(len(country_p)),
        "n_trust_country": int(len(country_t)),
        "cells": cell_meta,
        "n_patience_cells": int(len(pat_cells)),
        "n_trust_cells": int(len(tru_cells)),
        "sources": {
            "gps_country": str(GPS_C),
            "gps_individual": str(GPS_I),
            "wvs": str(WVS),
            "wdi": str(WDI),
            "h5": str(H5_FROZEN),
            "patience_frozen": str(PATIENCE_FROZEN),
        },
        "hashes": {
            "patience_country": sha256_file(DATA / "country/patience.csv"),
            "trust_country": sha256_file(DATA / "country/trust.csv"),
            "patience_cells": sha256_file(DATA / "cells/patience.csv"),
            "trust_cells": sha256_file(DATA / "cells/trust.csv"),
        },
    }
    (DATA / "score_manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: manifest[k] for k in (
        "reuse_patience", "reuse_trust", "n_patience_country", "n_trust_country",
        "n_patience_cells", "n_trust_cells", "cells", "compare_patience", "compare_trust",
    )}, indent=2))


if __name__ == "__main__":
    main()
