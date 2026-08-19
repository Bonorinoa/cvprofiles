"""Join fresh LLM columns onto human frames and run the four extension profiles.

Does not overwrite the 2026-08-14 confirmatory human runs.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from demean_cells import country_demean  # noqa: E402
from run_profiles import N_BOOT, SEED, _json, run_one  # noqa: E402
from score_llm_measures import aggregate  # noqa: E402
from cvprofiles import __version__

PROFILES = [
    {
        "id": "patience_country_llm",
        "scores": ROOT / "data/country/patience_llm_extension.csv",
        "roles": ROOT / "roles/patience_country_llm.json",
        "network": ROOT / "networks/patience_country_llm.yaml",
        "beta": ROOT / "betas/patience_country.yaml",
        "anchors": ROOT / "networks/patience_country_anchors.yaml",
        "canonical": "m_wvs_q13",
        "title": "Patience — country + LLM",
    },
    {
        "id": "trust_country_llm",
        "scores": ROOT / "data/country/trust_llm_extension.csv",
        "roles": ROOT / "roles/trust_country_llm.json",
        "network": ROOT / "networks/trust_country_llm.yaml",
        "beta": ROOT / "betas/trust_country.yaml",
        "anchors": ROOT / "networks/trust_country_anchors.yaml",
        "canonical": "m_trust_general",
        "title": "Trust — country + LLM",
    },
    {
        "id": "patience_cells_demeaned_llm",
        "scores": ROOT / "data/cells_demeaned/patience_llm_extension.csv",
        "roles": ROOT / "roles/patience_cells_llm.json",
        "network": ROOT / "networks/patience_cells_llm.yaml",
        "beta": ROOT / "betas/patience_cells.yaml",
        "anchors": ROOT / "networks/patience_cells_anchors.yaml",
        "canonical": "m_wvs_q13",
        "title": "Patience — cells demeaned + LLM",
    },
    {
        "id": "trust_cells_demeaned_llm",
        "scores": ROOT / "data/cells_demeaned/trust_llm_extension.csv",
        "roles": ROOT / "roles/trust_cells_llm.json",
        "network": ROOT / "networks/trust_cells_llm.yaml",
        "beta": ROOT / "betas/trust_cells.yaml",
        "anchors": ROOT / "networks/trust_cells_anchors.yaml",
        "canonical": "m_trust_general",
        "title": "Trust — cells demeaned + LLM",
    },
]


def _join(human: Path, llm: pd.DataFrame, dest: Path) -> pd.DataFrame:
    base = pd.read_csv(human)
    out = base.merge(llm, on="unit_id", how="left", validate="one_to_one")
    missing = out[llm.columns.drop("unit_id")].isna().sum().to_dict()
    if any(v > 0 for v in missing.values()):
        raise RuntimeError(f"{dest.name} unmatched LLM cells: {missing}")
    dest.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(dest, index=False)
    return out


def build_frames() -> None:
    pat_c = aggregate("patience", "country")
    tru_c = aggregate("trust", "country")
    pat_k = aggregate("patience", "cell")
    tru_k = aggregate("trust", "cell")
    _join(ROOT / "data/country/patience.csv", pat_c, ROOT / "data/country/patience_llm_extension.csv")
    _join(ROOT / "data/country/trust.csv", tru_c, ROOT / "data/country/trust_llm_extension.csv")
    pat_cells = _join(ROOT / "data/cells/patience.csv", pat_k, ROOT / "data/cells/patience_llm_extension.csv")
    tru_cells = _join(ROOT / "data/cells/trust.csv", tru_k, ROOT / "data/cells/trust_llm_extension.csv")
    pat_num = [
        "m_wvs_q13",
        "m_wvs_q14",
        "m_composite",
        "m_llm_patience_llama",
        "m_llm_patience_phi",
        "q275_cell",
        "gps_patience_cell",
        "m_noise",
    ]
    tru_num = [
        "m_trust_general",
        "m_trust_in_group",
        "m_trust_out_group",
        "m_trust_institution",
        "m_trust_composite",
        "m_llm_trust_llama",
        "m_llm_trust_phi",
        "q275_cell",
        "gps_trust_cell",
        "m_noise",
    ]
    country_demean(pat_cells, pat_num).to_csv(
        ROOT / "data/cells_demeaned/patience_llm_extension.csv", index=False
    )
    country_demean(tru_cells, tru_num).to_csv(
        ROOT / "data/cells_demeaned/trust_llm_extension.csv", index=False
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--skip-build",
        action="store_true",
        help="use committed *_llm_extension.csv frames; do not rebuild from raw LLM JSONL",
    )
    args = parser.parse_args()
    if args.skip_build:
        missing = [
            str(spec["scores"]) for spec in PROFILES if not Path(spec["scores"]).is_file()
        ]
        if missing:
            raise SystemExit(f"--skip-build: missing committed extension frames: {missing}")
        print("using committed extension frames (skip-build)")
    else:
        print("building extension frames...")
        build_frames()
    print("package", __version__)
    summaries = []
    for spec in PROFILES:
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
        ROOT / "llm_extension_summary.json",
        {
            "package_version": __version__,
            "seed": SEED,
            "n_boot": N_BOOT,
            "profiles": summaries,
        },
    )


if __name__ == "__main__":
    main()
