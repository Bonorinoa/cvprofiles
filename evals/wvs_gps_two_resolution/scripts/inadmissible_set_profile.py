"""Inadmissible-set profile (paper §6 / deliverable iii).

Reads the four frozen runs' slacks + betas and profiles M \\ M*:
which restrictions failed, how failures cluster (restriction vs measure
families), and whether the rejects carry criterion-relevant signal
(structured beta disagreement vs scattered noise).

Read-only over runs/: writes inadmissible_set_profile.json.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RUNS = ROOT / "runs"

PROFILES = [
    "patience_cells_demeaned_llm",
    "trust_cells_demeaned_llm",
    "patience_country_llm",
    "trust_country_llm",
]


def profile_run(tag: str) -> dict:
    run_dir = RUNS / tag
    slacks = pd.read_csv(run_dir / "slacks.csv").set_index("measure")
    bv = json.loads((run_dir / "beta_values.json").read_text())
    adm_flags = bv["admissible_flag"]
    betas = bv["beta_values"]
    net = json.loads((run_dir / "network_resolved.json").read_text())
    sel_ids = [r["id"] for r in net["restrictions"] if r.get("stage") in ("select", None)]
    hold_ids = [r["id"] for r in net["restrictions"] if r.get("stage") == "holdout"]

    rejected = [m for m, ok in adm_flags.items() if not ok]
    admitted = [m for m, ok in adm_flags.items() if ok]

    # Per-rejected-measure failure profile.
    fail_rows = []
    for m in rejected:
        fails_sel = [r for r in sel_ids if float(slacks.loc[m, r]) < 0]
        fails_hold = [r for r in hold_ids if float(slacks.loc[m, r]) < 0]
        margins = {r: round(float(slacks.loc[m, r]), 3) for r in fails_sel + fails_hold}
        fail_rows.append({
            "measure": m,
            "beta": round(betas[m], 3),
            "fails_select": fails_sel,
            "fails_holdout": fails_hold,
            "n_fail_select": len(fails_sel),
            "margins": margins,
            "sign_of_beta": "+" if betas[m] > 0 else "-",
        })

    # Restriction-level rejection rates over the menu.
    rej_rate = {}
    for r in sel_ids:
        rej_rate[r] = round(float((slacks.loc[rejected, r] < 0).mean()), 3) if rejected else 0.0

    # Coherence: sign agreement of beta among rejects vs menu base rate.
    if rejected:
        rej_signs = [1 if betas[m] > 0 else -1 for m in rejected]
        maj = max(set(rej_signs), key=rej_signs.count)
        rej_sign_agree = round(abs(sum(rej_signs)) / len(rej_signs), 3)
        menu_signs = [1 if betas[m] > 0 else -1 for m in adm_flags if m != "m_noise"]
        menu_maj_agree = round(abs(sum(1 if s > 0 else -1 for s in menu_signs)) / len(menu_signs), 3)
    else:
        rej_sign_agree, menu_maj_agree, maj = None, None, None

    # Beta gap: do rejects separate from admits in beta?
    if rejected and admitted:
        b_rej = [betas[m] for m in rejected]
        b_adm = [betas[m] for m in admitted if m != "m_noise"]
        gap = round(float(np.mean(b_rej) - np.mean(b_adm)), 3)
    else:
        gap = None

    return {
        "profile": tag,
        "n_menu": len(adm_flags),
        "n_admitted": len(admitted),
        "n_rejected": len(rejected),
        "admitted": admitted,
        "rejected_profiles": fail_rows,
        "rejection_rate_by_restriction": rej_rate,
        "reject_beta_sign_agreement": rej_sign_agree,
        "menu_beta_sign_agreement": menu_maj_agree,
        "reject_majority_sign": maj,
        "mean_beta_gap_rejected_minus_admitted": gap,
    }


def main() -> None:
    out = {}
    for tag in PROFILES:
        res = profile_run(tag)
        out[tag] = res
        print(f"\n== {tag} ==  (menu {res['n_menu']}, rejected {res['n_rejected']})")
        print(f"  rejection rate by restriction: {res['rejection_rate_by_restriction']}")
        print(f"  reject beta-sign agreement: {res['reject_beta_sign_agreement']} "
              f"(menu base rate {res['menu_beta_sign_agreement']}); "
              f"mean beta gap (rej - adm): {res['mean_beta_gap_rejected_minus_admitted']}")
        for f in res["rejected_profiles"]:
            print(f"    {f['measure']:>24s}  beta={f['beta']:+.3f}  "
                  f"fails={f['fails_select']}{' +' + ','.join(f['fails_holdout']) if f['fails_holdout'] else ''}")

    dest = ROOT / "inadmissible_set_profile.json"
    dest.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(f"\nwrote {dest}")


if __name__ == "__main__":
    main()
