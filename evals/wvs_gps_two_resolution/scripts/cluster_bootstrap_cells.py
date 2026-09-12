"""Country-cluster bootstrap with re-demeaning (Coarse item 4).

Read-only over committed undemeaned cell LLM tables. Does not overwrite
frozen runs. Writes preprint_audit/cluster_bootstrap_cells.json.

Resampling unit = country (iso3). Each replicate: draw 42 countries with
replacement, stack their cells, country-demean inside the replicate
(groupby original iso3, so two copies of ARG share ARG's mean — equivalent
to block-resampling already-demeaned countries), then run_identify
(select-stage only).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles

ROOT = Path(__file__).resolve().parents[1]
EVAL = ROOT
NET = EVAL / "networks"
BETAS = EVAL / "betas"
DATA = EVAL / "data" / "cells"
OUT = EVAL / "preprint_audit"
SEED = 20260814
N_BOOT = 1000

PROFILES = {
    "patience_cells": {
        "scores": DATA / "patience_llm_extension.csv",
        "network": NET / "patience_cells_llm.yaml",
        "beta": BETAS / "patience_cells.yaml",
        "roles": {
            "unit_id": "unit_id",
            "measures": [
                "m_wvs_q13",
                "m_wvs_q14",
                "m_composite",
                "m_llm_patience_llama",
                "m_llm_patience_phi",
                "m_noise",
            ],
            "aux": ["q275_cell"],
            "outcome": "gps_patience_cell",
            "diagnostic": [],
        },
        "demean_cols": [
            "m_wvs_q13",
            "m_wvs_q14",
            "m_composite",
            "m_llm_patience_llama",
            "m_llm_patience_phi",
            "m_noise",
            "q275_cell",
            "gps_patience_cell",
        ],
        "paper_band": [0.179, 0.614],
        "paper_LU": [0.245, 0.556],
        "paper_Mstar": ["m_wvs_q13", "m_llm_patience_llama", "m_llm_patience_phi"],
    },
    "trust_cells": {
        "scores": DATA / "trust_llm_extension.csv",
        "network": NET / "trust_cells_llm.yaml",
        "beta": BETAS / "trust_cells.yaml",
        "roles": {
            "unit_id": "unit_id",
            "measures": [
                "m_trust_general",
                "m_trust_in_group",
                "m_trust_out_group",
                "m_trust_institution",
                "m_trust_composite",
                "m_llm_trust_llama",
                "m_llm_trust_phi",
                "m_noise",
            ],
            "aux": ["q275_cell"],
            "outcome": "gps_trust_cell",
            "diagnostic": [],
        },
        "demean_cols": [
            "m_trust_general",
            "m_trust_in_group",
            "m_trust_out_group",
            "m_trust_institution",
            "m_trust_composite",
            "m_llm_trust_llama",
            "m_llm_trust_phi",
            "m_noise",
            "q275_cell",
            "gps_trust_cell",
        ],
        "paper_band": [-0.382, -0.240],
        "paper_LU": [-0.317, -0.317],
        "paper_Mstar": ["m_llm_trust_phi"],
    },
}


def country_demean(df: pd.DataFrame, cols: list[str], iso: pd.Series) -> pd.DataFrame:
    out = df.copy()
    means = out.groupby(iso, sort=False)[cols].transform("mean")
    out[cols] = out[cols] - means
    return out


def run_profile(name: str, spec: dict, rng: np.random.Generator) -> dict:
    raw = pd.read_csv(spec["scores"])
    raw["iso"] = raw["unit_id"].str.split("|").str[0]
    countries = raw["iso"].unique()
    n_c = len(countries)
    roles = ScoreColumnRoles.model_validate(spec["roles"])
    bundle = run_restrict(roles, spec["network"], spec["beta"])
    # headline on once-demeaned full sample (sanity vs freeze)
    full = country_demean(raw, spec["demean_cols"], raw["iso"])
    head = run_identify(full, roles, bundle, include_holdout_verdict=False)

    L_s, U_s = [], []
    n_empty = 0
    n_deg = 0
    admit_counts = {m: 0 for m in spec["roles"]["measures"]}
    nonempty = 0
    for b in range(N_BOOT):
        draw = rng.choice(countries, size=n_c, replace=True)
        parts = []
        for i, cty in enumerate(draw):
            block = raw.loc[raw["iso"] == cty].copy()
            block["unit_id"] = block["unit_id"].astype(str) + f"#{i}"
            parts.append(block)
        stacked = pd.concat(parts, ignore_index=True)
        iso_b = stacked["unit_id"].str.split("|").str[0]
        dem = country_demean(stacked, spec["demean_cols"], iso_b)
        try:
            res = run_identify(dem, roles, bundle, include_holdout_verdict=False)
        except Exception as exc:
            n_deg += 1
            if n_deg == 1:
                print(f"first degenerate {name} b={b}: {type(exc).__name__}: {exc}", flush=True)
            continue
        if res.empty or res.range_L is None or res.range_U is None:
            n_empty += 1
            continue
        nonempty += 1
        L_s.append(float(res.range_L))
        U_s.append(float(res.range_U))
        for m in res.admissible:
            admit_counts[m] += 1

    p_hat = {m: (admit_counts[m] / nonempty if nonempty else None) for m in admit_counts}
    return {
        "profile": name,
        "n_countries": int(n_c),
        "n_cells": int(len(raw)),
        "n_boot": N_BOOT,
        "seed": SEED,
        "headline_M_star": list(head.admissible),
        "headline_L": None if head.range_L is None else round(float(head.range_L), 3),
        "headline_U": None if head.range_U is None else round(float(head.range_U), 3),
        "paper_Mstar": spec["paper_Mstar"],
        "paper_LU": spec["paper_LU"],
        "paper_cell_exchangeable_band": spec["paper_band"],
        "cluster_band_alpha10": [
            round(float(np.quantile(L_s, 0.05)), 3) if L_s else None,
            round(float(np.quantile(U_s, 0.95)), 3) if U_s else None,
        ],
        "empty_replicate_rate": n_empty / N_BOOT,
        "degenerate_replicate_rate": n_deg / N_BOOT,
        "replicates_nonempty": nonempty,
        "p_hat_m": {m: (None if v is None else round(v, 3)) for m, v in p_hat.items()},
        "M_star_matches_freeze": set(head.admissible) == set(spec["paper_Mstar"]),
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)
    out = {"n_boot": N_BOOT, "seed": SEED, "profiles": {}}
    for name, spec in PROFILES.items():
        print(f"running {name} ...", flush=True)
        out["profiles"][name] = run_profile(name, spec, rng)
        print(json.dumps(out["profiles"][name], indent=2), flush=True)
    dest = OUT / "cluster_bootstrap_cells.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
