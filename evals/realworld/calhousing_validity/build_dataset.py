"""Build a real-world, tabular multi-measure dataset from California housing.

Offline-deterministic after one sklearn fetch (bundled fetch_california_housing;
the small CSV is cached under ~/scikit_learn_data). Constructs a multi-measure
"housing quality / desirability" menu plus a clean auxiliary (`v_aux`) and a
noisy outcome `y`.

This is NOT the main path and NOT H5. It is an intermediate audit to stress the
package spine on a NON-TEXT matrix with skewed features, a larger menu, and
designed valid/invalid columns. No paper claims here.

Measure labels are truthful: composites are hand-weighted and explicitly named;
nothing here is an LLM output.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.datasets import fetch_california_housing

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RANDOM_SEED = 20260804


def z(x: np.ndarray) -> np.ndarray:
    s = x.std(ddof=0)
    if s == 0:
        return np.zeros_like(x, dtype=float)
    return (x - x.mean()) / s


def build() -> None:
    print("[1/4] Fetching California housing...")
    housing = fetch_california_housing()
    X = np.asarray(housing.data, dtype=float)
    target = np.asarray(housing.target, dtype=float)  # MedHouseVal in $100k
    n = len(target)
    print(f"      n={n}, features={housing.feature_names}")

    print("[2/4] Building feature families (multi-measure menu)...")
    RANDOM = np.random.default_rng(RANDOM_SEED)

    med_inc = X[:, 0]
    house_age = X[:, 1]
    ave_rooms = X[:, 2]
    ave_occup = X[:, 5]
    longitude = X[:, 7]

    # --- Designed VALID operationalizations of "quality / desirability" ---
    m_afford = z(med_inc)                                  # affordability / income proxy
    m_space = z(np.log1p(ave_rooms))                       # size proxy (log for skew)
    m_uncrowded = z(-np.log1p(ave_occup))                  # low-occupancy proxy
    m_spacious_uncrowded = z(0.5 * m_space + 0.5 * m_uncrowded)  # hand composite
    m_age_pref = z(-house_age)                             # newer-home preference proxy
    m_composite_quality = z(                               # "AI-style" hand composite
        0.40 * med_inc
        + 0.30 * np.log1p(ave_rooms)
        + 0.30 * (-np.log1p(ave_occup))
    )

    # --- Designed INVALID operationalizations ---
    m_noise = RANDOM.standard_normal(n) * 0.5              # pure noise
    m_geo_dict = z(longitude)                              # dictionary-privileged geo proxy;
                                                           # weakly correlated with price but
                                                           # must fail the quality-based R

    # Clean auxiliary: size + uncrowdedness signal (NOT the outcome drivers only).
    v_aux = z(0.5 * np.log1p(ave_rooms) + 0.5 * (-np.log1p(ave_occup)))

    # Outcome: noisy latent the valid measures should track.
    m_label = 0.55 * z(med_inc) + 0.30 * z(np.log1p(ave_rooms)) + 0.15 * m_uncrowded
    outcome = m_label + 0.10 * RANDOM.standard_normal(n)

    print("[3/4] Assembling unit×measure matrix...")
    df = pd.DataFrame(
        {
            "unit_id": [f"u{i:06d}" for i in range(n)],
            "m_afford": m_afford,
            "m_space": m_space,
            "m_uncrowded": m_uncrowded,
            "m_spacious_uncrowded": m_spacious_uncrowded,
            "m_age_pref": m_age_pref,
            "m_composite_quality": m_composite_quality,
            "m_noise": m_noise,
            "m_geo_dict": m_geo_dict,
            "v_aux": v_aux,
            "y": outcome,
        }
    )
    DATA.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA / "scores.csv", index=False)

    roles = {
        "unit_id": "unit_id",
        "measures": [
            "m_afford",
            "m_space",
            "m_uncrowded",
            "m_spacious_uncrowded",
            "m_age_pref",
            "m_composite_quality",
            "m_noise",
            "m_geo_dict",
        ],
        "aux": ["v_aux"],
        "outcome": "y",
        # Keep empty: SCORE requires declared diagnostics to exist on the score frame.
        "diagnostic": [],
    }
    with (DATA / "roles.json").open("w") as f:
        json.dump(roles, f, indent=2)

    network_oracle = {
        "schema_version": "1",
        "name": "calhousing_oracle_incidental",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_corr_min_aux",
                "type": "corr_min",
                "theta": 0.15,
                "params": {"variable": "v_aux"},
            },
            {
                "id": "r_corr_sign_aux",
                "type": "corr_sign",
                "theta": 0.05,
                "params": {"variable": "v_aux", "sign": 1},
            },
        ],
    }
    network_harsh = {
        "schema_version": "1",
        "name": "calhousing_harsh_empty",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_corr_min_aux",
                "type": "corr_min",
                # Above the max sample corr with v_aux (≈0.999 for
                # m_spacious_uncrowded), so the harsh contrast empties by design.
                "theta": 0.9999,
                "params": {"variable": "v_aux"},
            },
        ],
    }
    beta = {"schema_version": "1", "type": "corr_y", "outcome": "y", "params": {}}
    with (DATA / "network_oracle.yaml").open("w") as f:
        yaml.safe_dump(network_oracle, f, sort_keys=False)
    with (DATA / "network_harsh.yaml").open("w") as f:
        yaml.safe_dump(network_harsh, f, sort_keys=False)
    with (DATA / "beta.yaml").open("w") as f:
        yaml.safe_dump(beta, f, sort_keys=False)

    print("[4/4] Sanity check (oracle R at delta=0):")
    for m in roles["measures"]:
        c_aux = float(np.corrcoef(df[m], df["v_aux"])[0, 1])
        c_y = float(np.corrcoef(df[m], df["y"])[0, 1])
        adm = (c_aux >= 0.15) and (c_aux >= 0.05)
        print(f"  {m:20s}: corr_aux={c_aux:+.3f} corr_y={c_y:+.3f}  adm={adm}")
    print(f"  v_aux_std={float(df['v_aux'].std()):.4f}  y_std={float(df['y'].std()):.4f}")
    lon_corr_y = float(np.corrcoef(df["m_geo_dict"], df["y"])[0, 1])
    print(f"  lon_corr_y={lon_corr_y:+.3f} (weak geo proxy; must fail R)")
    max_corr_aux = max(float(np.corrcoef(df[m], df["v_aux"])[0, 1]) for m in roles["measures"])
    print(f"  max_corr_aux={max_corr_aux:.4f} (harsh theta must exceed this)")


if __name__ == "__main__":
    build()
