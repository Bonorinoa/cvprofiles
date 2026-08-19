"""Commit the MTMM partial-correlation computation behind the paper's r = 0.706.

Paper claim (position_paper_cvprofiles.tex, Section 5.3): partialling log GDP
per capita and education leaves the Q57--GPS patience association at 0.706.
This script makes that number a committed, reproducible artifact instead of a
hand calculation: it reads the frozen MTMM frame and writes the partial r.

Run:  uv run python evals/composition_special_cases/compute_partial_r.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "partial_r_patience_trust.json"

PAIR = ("m_trust_general", "gps_patience")  # WVS Q57 vs GPS patience
CONTROLS = ["q275_mean", "log_gdp_pc"]  # education, log GDP per capita


def _resid(v: np.ndarray, Z: np.ndarray) -> np.ndarray:
    A = np.column_stack([np.ones(len(v)), Z])
    coef, *_ = np.linalg.lstsq(A, v, rcond=None)
    return v - A @ coef


def main() -> None:
    df = pd.read_csv(ROOT / "scores_mtmm.csv")
    x = df[PAIR[0]].to_numpy(dtype=float)
    y = df[PAIR[1]].to_numpy(dtype=float)
    Z = df[CONTROLS].to_numpy(dtype=float)
    rx, ry = _resid(x, Z), _resid(y, Z)
    r = float(np.corrcoef(rx, ry)[0, 1])
    n = int(len(df))
    k = len(CONTROLS)
    se = float(np.sqrt((1.0 - r * r) / (n - k - 2)))
    t = float(r / se)
    payload = {
        "package_version": "3.0.2",
        "note": "2026-08-18 closeout: commits the partial-r computation behind the paper's 0.706 claim.",
        "construct_pair": list(PAIR),
        "controls": CONTROLS,
        "n": n,
        "partial_r": r,
        "se": se,
        "t": t,
        "rounded_3dp": round(r, 3),
    }
    OUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(f"partial r({PAIR[0]}, {PAIR[1]} | {', '.join(CONTROLS)}) = {r:.6f} (n={n})")
    print(f"written -> {OUT}")


if __name__ == "__main__":
    main()
