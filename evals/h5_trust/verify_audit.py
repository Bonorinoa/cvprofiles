#!/usr/bin/env python3
"""Dev gate for the H5 Trust evaluation (docs/17).

Runs the installed cvprofiles pipeline on the built scores with the
design-locked roles/network/beta, checks FA=0 for designed-invalids, cold
freeze-core equality, artifact presence, and empty-honesty, then writes
``proof_summary.json`` in the schema the read-only auditor
(tools/verify_h5_trust.py) validates. Exit 0 only if all gates hold.

NOT a paper acceptance step: a passing audit is structural consistency;
Gate C-style acceptance remains Augusto's decision.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import cvprofiles
from cvprofiles.pipeline import run_profile, summary_dict

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RUNS = ROOT / "runs_verify"
SUMMARY = ROOT / "proof_summary.json"

DESIGNED_VALID = {
    "m_trust_general",
    "m_trust_in_group",
    "m_trust_out_group",
    "m_trust_institution",
}
DESIGNED_INVALID = {"m_noise", "m_share_agriculture"}
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
EXPECTED_ARTIFACTS = (
    "report.html",
    "report.json",
    "admissible.json",
    "range.json",
    "slacks.csv",
    "run_manifest.json",
    "score_manifest.json",
)


def _core(summary: dict) -> dict:
    return {k: summary[k] for k in FREEZE_KEYS}


def _run(out_name: str, title: str, seed: int = 0) -> dict:
    out = RUNS / out_name
    if out.exists():
        for p in out.iterdir():
            if p.is_file():
                p.unlink()
    result = run_profile(
        scores=DATA / "scores.csv",
        roles=DATA / "roles_h5_trust.json",
        network=DATA / "network_h5_trust.yaml",
        beta=DATA / "beta_h5_trust.yaml",
        out_dir=out,
        policy="none",
        seed=seed,
        title=title,
        write_parquet=False,
    )
    return summary_dict(result)


def main() -> int:
    if not (DATA / "scores.csv").exists():
        print("scores.csv missing — run build_dataset.py first", file=sys.stderr)
        return 2

    summary = _run("default", "H5 Trust — country-level generalized trust")
    summary_cold = _run("cold", "H5 Trust — cold rerun")

    m_star = set(summary["M_star"])
    fa = sorted(m_star & DESIGNED_INVALID)
    cold_match = _core(summary) == _core(summary_cold)
    artifacts_ok = all((RUNS / "default" / a).exists() for a in EXPECTED_ARTIFACTS)

    failures: list[str] = []
    if fa:
        failures.append(f"designed-invalid measure(s) admitted: {fa}")
    if not cold_match:
        failures.append("cold freeze-core mismatch between two runs")
    if not artifacts_ok:
        failures.append("missing expected run artifacts")

    empty_honesty = summary["empty"] and summary["L"] is None and summary["U"] is None
    if summary["empty"] and not empty_honesty:
        failures.append("empty M* with non-null range")

    gates = {
        "FA_zero": not fa,
        "cold_H4": cold_match,
        "artifacts_present": artifacts_ok,
        "empty_honesty": empty_honesty,
    }

    manifest = {}
    manifest_path = DATA / "score_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text())

    proof = {
        "audit": "h5_trust_generalized",
        "settings": {
            "n_countries": manifest.get("n_countries"),
            "floor": manifest.get("settings", {}).get("floor"),
            "seed": manifest.get("settings", {}).get("seed"),
            "policy": "none",
            "delta": 0.0,
            "package_version": cvprofiles.__version__,
            "parent_sha": manifest.get("parent_sha"),
            "scores_hash": summary.get("scores_hash"),
            "network_hash": summary.get("network_hash"),
            "beta_hash": summary.get("beta_hash"),
        },
        "gates": gates,
        "designed_valid": sorted(DESIGNED_VALID),
        "designed_invalid": sorted(DESIGNED_INVALID),
        "M_star": summary.get("M_star"),
        "L": summary.get("L"),
        "U": summary.get("U"),
        "empty": summary.get("empty"),
        "rejected": summary.get("rejected"),
        "cold_match": cold_match,
        "failures": failures,
    }
    SUMMARY.write_text(json.dumps(proof, indent=2) + "\n")
    print(json.dumps({"passed": not failures, "failures": failures, "gates": gates}, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
