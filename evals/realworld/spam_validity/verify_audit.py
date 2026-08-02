#!/usr/bin/env python3
"""Rigorous verification of the spam real-world audit via the installed package.

NOT main path / NOT paper. Exercises SCORE → RESTRICT → IDENTIFY → REPORT
on a free public text corpus (20newsgroups features). Exit 0 only if gates hold.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from cvprofiles.pipeline import run_profile, summary_dict

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RUNS = ROOT / "runs_verify"
SUMMARY = ROOT / "proof_summary.json"

# Design roles (outside the engine; for audit interpretation only).
DESIGNED_VALID = {
    "m_lexicon",
    "m_money_url",
    "m_caps_buy",
    "m_llm_full",
    "m_short_cap",
}
DESIGNED_INVALID = {"m_noise", "m_topic_leak"}
FREEZE_KEYS = (
    "empty",
    "M_star",
    "rejected",
    "L",
    "U",
    "point_id",
    "scores_hash",
    "network_hash",
    "beta_hash",
)


def _core(summary: dict) -> dict:
    return {k: summary[k] for k in FREEZE_KEYS}


def _run(network_name: str, out_name: str, title: str) -> dict:
    out = RUNS / out_name
    if out.exists():
        for p in out.iterdir():
            if p.is_file():
                p.unlink()
    result = run_profile(
        scores=DATA / "scores.csv",
        roles=DATA / "roles.json",
        network=DATA / network_name,
        beta=DATA / "beta.yaml",
        out_dir=out,
        policy="none",
        seed=0,
        title=title,
        write_parquet=False,
    )
    return summary_dict(result)


def main() -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    # --- Oracle network ---
    o1 = _run(
        "network_oracle.yaml",
        "oracle_a",
        "Spam validity (oracle R) verify A",
    )
    o2 = _run(
        "network_oracle.yaml",
        "oracle_b",
        "Spam validity (oracle R) verify B",
    )
    h = _run(
        "network_harsh.yaml",
        "harsh",
        "Spam validity (harsh empty) verify",
    )

    # H4: freeze cores identical across cold double run (paths may differ)
    if _core(o1) != _core(o2):
        failures.append(f"H4 cold core mismatch:\n  A={_core(o1)}\n  B={_core(o2)}")

    m_star = set(o1["M_star"])
    rejected = set(o1["rejected"].keys())

    # FA: designed invalids never in M*
    fa = sorted(m_star & DESIGNED_INVALID)
    if fa:
        failures.append(f"FA: designed invalids in M*: {fa}")

    # Valids expected under this incidental network
    missing_valid = sorted(DESIGNED_VALID - m_star)
    if missing_valid:
        failures.append(f"expected valids missing from M*: {missing_valid}")

    if o1["empty"]:
        failures.append("oracle run unexpectedly empty")
    if o1["L"] is None or o1["U"] is None:
        failures.append("oracle range L/U null")
    elif not (o1["L"] <= o1["U"]):
        failures.append(f"oracle L>U: {o1['L']} > {o1['U']}")
    else:
        # Range is image of survivors only: check β of rejected not required inside
        # (package already builds min/max B*; verify noise β is outside if negative)
        pass

    # Rejected should include both designed invalids
    if not DESIGNED_INVALID.issubset(rejected):
        failures.append(
            f"designed invalids not fully rejected: rejected={sorted(rejected)}"
        )

    # H3 harsh empty
    if not h["empty"] or h["M_star"] or h["L"] is not None or h["U"] is not None:
        failures.append(f"H3 harsh not empty: {h}")

    # Report aesthetics
    harsh_html = (RUNS / "harsh" / "report.html").read_text()
    if "Empty admissible set" not in harsh_html:
        failures.append("harsh report.html missing empty-M* callout")
    if "success, not a crash" not in harsh_html:
        failures.append("harsh report.html missing success-not-crash copy")

    oracle_html = (RUNS / "oracle_a" / "report.html").read_text()
    if "Empty admissible set" in oracle_html:
        failures.append("oracle report.html incorrectly shows empty callout")
    for m in sorted(DESIGNED_VALID):
        if m not in oracle_html:
            failures.append(f"oracle HTML missing measure {m}")

    # Artifact presence
    for name in ("oracle_a", "harsh"):
        for art in (
            "report.html",
            "report.json",
            "admissible.json",
            "range.json",
            "slacks.csv",
            "run_manifest.json",
            "score_manifest.json",
        ):
            p = RUNS / name / art
            if not p.is_file():
                failures.append(f"missing artifact {p}")

    # scores_hash stable across oracle/harsh (same scores)
    if o1["scores_hash"] != h["scores_hash"]:
        failures.append("scores_hash differs between oracle and harsh (same scores.csv)")

    proof = {
        "audit": "spam_validity_20newsgroups_features",
        "path": "intermediate_not_main_path",
        "package": "cvprofiles",
        "n_units": None,
        "oracle": _core(o1),
        "harsh": _core(h),
        "cold_match": _core(o1) == _core(o2),
        "designed_valid": sorted(DESIGNED_VALID),
        "designed_invalid": sorted(DESIGNED_INVALID),
        "false_admissions": fa,
        "gates": {
            "FA_zero": not fa,
            "oracle_nonempty": not o1["empty"],
            "harsh_empty": bool(h["empty"]),
            "cold_H4": _core(o1) == _core(o2),
            "harsh_html_empty_callout": "Empty admissible set" in harsh_html,
            "same_scores_hash": o1["scores_hash"] == h["scores_hash"],
        },
        "passed": len(failures) == 0,
        "failures": failures,
    }
    # n from scores
    import pandas as pd

    proof["n_units"] = int(len(pd.read_csv(DATA / "scores.csv")))
    SUMMARY.write_text(json.dumps(proof, indent=2, sort_keys=True) + "\n")

    print(json.dumps(proof, indent=2, sort_keys=True))
    if failures:
        print("FAILED:", file=sys.stderr)
        for f in failures:
            print(" -", f, file=sys.stderr)
        return 1
    print("ALL GATES PASSED", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
