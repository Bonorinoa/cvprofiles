"""Country-demean the existing cell tables (amendment 2026-08-14 18:03 MST).

Does not rebuild from microdata. Does not touch country tables or pooled
cell CSVs. Not imported from src/.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "cells"
DST = ROOT / "data" / "cells_demeaned"
DST.mkdir(parents=True, exist_ok=True)

PATIENCE_NUM = [
    "m_wvs_q13",
    "m_wvs_q14",
    "m_composite",
    "q275_cell",
    "gps_patience_cell",
    "m_noise",
]
TRUST_NUM = [
    "m_trust_general",
    "m_trust_in_group",
    "m_trust_out_group",
    "m_trust_institution",
    "m_trust_composite",
    "q275_cell",
    "gps_trust_cell",
    "m_noise",
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def country_demean(df: pd.DataFrame, cols: list[str]) -> pd.DataFrame:
    out = df.copy()
    iso = out["unit_id"].str.split("|").str[0]
    if iso.isna().any() or (iso == "").any():
        raise ValueError("unit_id must be iso3|sex|band")
    means = out.groupby(iso, sort=False)[cols].transform("mean")
    out[cols] = out[cols] - means
    # within-country columns must have country means ~ 0
    check = out.groupby(iso)[cols].mean().abs().max().max()
    if check > 1e-12:
        raise RuntimeError(f"demean failed: max |country mean| = {check}")
    return out


def main() -> None:
    pat = pd.read_csv(SRC / "patience.csv")
    tru = pd.read_csv(SRC / "trust.csv")
    pat_d = country_demean(pat, PATIENCE_NUM)
    tru_d = country_demean(tru, TRUST_NUM)
    if list(pat_d["unit_id"]) != list(pat["unit_id"]):
        raise RuntimeError("patience unit_id order changed")
    if list(tru_d["unit_id"]) != list(tru["unit_id"]):
        raise RuntimeError("trust unit_id order changed")
    pat_d.to_csv(DST / "patience.csv", index=False)
    tru_d.to_csv(DST / "trust.csv", index=False)
    manifest = {
        "amendment": "2026-08-14 18:03 MST country-demean cell estimand",
        "source_pooled": {
            "patience": sha256_file(SRC / "patience.csv"),
            "trust": sha256_file(SRC / "trust.csv"),
        },
        "hashes": {
            "patience_cells_demeaned": sha256_file(DST / "patience.csv"),
            "trust_cells_demeaned": sha256_file(DST / "trust.csv"),
        },
        "n_patience": int(len(pat_d)),
        "n_trust": int(len(tru_d)),
        "n_countries_patience": int(pat_d["unit_id"].str.split("|").str[0].nunique()),
        "n_countries_trust": int(tru_d["unit_id"].str.split("|").str[0].nunique()),
        "columns_demeaned_patience": PATIENCE_NUM,
        "columns_demeaned_trust": TRUST_NUM,
        "note": "Same 480 rows / unit_ids as pooled cells; numeric columns country-demeaned.",
    }
    (DST / "score_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    )
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    main()
