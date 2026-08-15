"""Rerun the two cell profiles on country-demeaned scores.

Same networks, θ, seed, n_boot, λ-grid as the pooled contrast.
Does not touch country runs or overwrite application_summary.json.
"""

from __future__ import annotations

import json
from pathlib import Path

from run_profiles import PROFILES, ROOT, SEED, N_BOOT, _json, run_one
from cvprofiles import __version__

DEMEANED = [
    {
        **next(p for p in PROFILES if p["id"] == "patience_cells"),
        "id": "patience_cells_demeaned",
        "scores": ROOT / "data/cells_demeaned/patience.csv",
        "title": "Patience — cells (country-demeaned)",
    },
    {
        **next(p for p in PROFILES if p["id"] == "trust_cells"),
        "id": "trust_cells_demeaned",
        "scores": ROOT / "data/cells_demeaned/trust.csv",
        "title": "Trust — cells (country-demeaned)",
    },
]


def main() -> None:
    print("package", __version__, "cell estimand=country-demeaned")
    summaries = []
    for spec in DEMEANED:
        print("running", spec["id"], "...")
        summaries.append(run_one(spec))
        s = summaries[-1]
        print(
            " ",
            s["id"],
            "n=",
            s["n_units"],
            "M*=",
            s["M_star"],
            "L,U=",
            s["L"],
            s["U"],
            "empty_rep=",
            s["empty_replicate_rate"],
        )
    _json(
        ROOT / "demeaned_application_summary.json",
        {
            "package_version": __version__,
            "seed": SEED,
            "n_boot": N_BOOT,
            "estimand": "country_demeaned_cells",
            "amendment": "2026-08-14 18:03 MST",
            "profiles": summaries,
        },
    )


if __name__ == "__main__":
    main()
