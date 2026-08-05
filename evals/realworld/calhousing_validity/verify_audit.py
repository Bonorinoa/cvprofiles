#!/usr/bin/env python3
"""Rigorous verification of the California-housing real-world audit.

NOT main path / NOT paper / NOT H5. Exercises SCORE → RESTRICT → IDENTIFY →
REPORT on a tabular public dataset (California housing features) with designed
valid/invalid columns. Adds two capability probes the text audit did not cover:
a small-n run and a fail-loud missingness check. Exit 0 only if gates hold.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd

from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.score.pipeline import NormPolicy, ScoreError, run_score

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
RUNS = ROOT / "runs_verify"
SUMMARY = ROOT / "proof_summary.json"

DESIGNED_VALID = {
    "m_afford",
    "m_space",
    "m_uncrowded",
    "m_spacious_uncrowded",
    "m_age_pref",
    "m_composite_quality",
}
DESIGNED_INVALID = {"m_noise", "m_geo_dict"}
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


def _run(
    network_name: str,
    out_name: str,
    title: str,
    scores: Path | None = None,
    roles: Path | None = None,
    policy: NormPolicy = "none",
) -> dict:
    out = RUNS / out_name
    if out.exists():
        for p in out.iterdir():
            if p.is_file():
                p.unlink()
    result = run_profile(
        scores=scores if scores is not None else DATA / "scores.csv",
        roles=roles if roles is not None else DATA / "roles.json",
        network=DATA / network_name,
        beta=DATA / "beta.yaml",
        out_dir=out,
        policy=policy,
        seed=0,
        title=title,
        write_parquet=False,
    )
    return summary_dict(result)


def _thin_sample_probe(n: int, tag: str) -> dict:
    """Deterministic thin-sample probe: first n units, oracle + harsh networks.

    Admission is diagnostic here (it can flip with n); the gate is clean exit,
    valid range contract, and a harsh empty contrast.
    """
    small = RUNS / f"small_{tag}_scores.csv"
    df = pd.read_csv(DATA / "scores.csv")
    df.head(n).to_csv(small, index=False)
    oracle = _run(
        "network_oracle.yaml",
        f"small_{tag}_oracle",
        f"Calhousing n={n} oracle",
        scores=small,
    )
    harsh = _run(
        "network_harsh.yaml",
        f"small_{tag}_harsh",
        f"Calhousing n={n} harsh",
        scores=small,
    )
    return {
        "n": n,
        "oracle_nonempty": not oracle["empty"],
        "oracle_M_star": oracle["M_star"],
        "oracle_range": [oracle["L"], oracle["U"]],
        "harsh_empty": bool(harsh["empty"]),
        "range_ok": (
            (oracle["L"] is None and oracle["U"] is None)
            or (oracle["L"] is not None and oracle["U"] is not None and oracle["L"] <= oracle["U"])
        ),
    }


def _zscore_probe(o_none: dict) -> dict:
    """z-score normalization on real data must leave M* and [L,U] invariant."""
    zs = _run(
        "network_oracle.yaml",
        "oracle_zscore",
        "Calhousing validity (oracle R, zscore policy) verify",
        policy="zscore_measures",
    )
    same_m = zs["M_star"] == o_none["M_star"]
    same_range = (
        zs["L"] is not None
        and o_none["L"] is not None
        and abs(zs["L"] - o_none["L"]) < 1e-9
        and abs(zs["U"] - o_none["U"]) < 1e-9
    )
    return {
        "exit_clean": True,
        "M_star_equal": same_m,
        "range_equal": same_range,
        "M_star": zs["M_star"],
        "range": [zs["L"], zs["U"]],
    }


def _skew_probe() -> dict:
    """Raw heavy-skew variant: clean run + valid range; membership diagnostic."""
    s = _run(
        "network_oracle.yaml",
        "skew_oracle",
        "Calhousing raw-skew variant (oracle R) verify",
        scores=DATA / "scores_skew.csv",
        roles=DATA / "roles_skew.json",
    )
    return {
        "exit_clean": True,
        "empty": s["empty"],
        "M_star": s["M_star"],
        "range": [s["L"], s["U"]],
        "range_ok": (
            (s["L"] is None and s["U"] is None)
            or (s["L"] is not None and s["U"] is not None and s["L"] <= s["U"])
        ),
    }


def _nan_probe() -> dict:
    """Honest capability boundary: SCORE must fail loud on non-finite measures."""
    df = pd.read_csv(DATA / "scores.csv").head(50).copy()
    df.loc[0, "m_afford"] = float("nan")
    roles_path = DATA / "roles.json"
    try:
        run_score(df, roles_path, policy="none")
    except ScoreError as exc:
        return {"passed": True, "message": str(exc)}
    return {"passed": False, "message": "run_score accepted NaN in a measure column"}


def main() -> int:
    RUNS.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []

    # --- Oracle network (full data, cold double run) ---
    o1 = _run("network_oracle.yaml", "oracle_a", "Calhousing validity (oracle R) verify A")
    o2 = _run("network_oracle.yaml", "oracle_b", "Calhousing validity (oracle R) verify B")
    h = _run("network_harsh.yaml", "harsh", "Calhousing validity (harsh empty) verify")

    if _core(o1) != _core(o2):
        failures.append(f"H4 cold core mismatch:\n  A={_core(o1)}\n  B={_core(o2)}")

    m_star = set(o1["M_star"])
    rejected = set(o1["rejected"].keys())

    fa = sorted(m_star & DESIGNED_INVALID)
    if fa:
        failures.append(f"FA: designed invalids in M*: {fa}")
    missing_valid = sorted(DESIGNED_VALID - m_star)
    if missing_valid:
        failures.append(f"expected valids missing from M*: {missing_valid}")

    if o1["empty"]:
        failures.append("oracle run unexpectedly empty")
    if o1["L"] is None or o1["U"] is None:
        failures.append("oracle range L/U null")
    elif not (o1["L"] <= o1["U"]):
        failures.append(f"oracle L>U: {o1['L']} > {o1['U']}")

    if not DESIGNED_INVALID.issubset(rejected):
        failures.append(f"designed invalids not fully rejected: rejected={sorted(rejected)}")

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
        for art in EXPECTED_ARTIFACTS:
            p = RUNS / name / art
            if not p.is_file():
                failures.append(f"missing artifact {p}")

    # scores_hash stable across oracle/harsh (same scores)
    if o1["scores_hash"] != h["scores_hash"]:
        failures.append("scores_hash differs between oracle and harsh (same scores.csv)")

    # --- Capability probes ---
    thin_samples = [_thin_sample_probe(n, f"n{n}") for n in (200, 50)]
    for probe in thin_samples:
        if not probe["harsh_empty"]:
            failures.append(f"thin-sample n={probe['n']} harsh run not empty")
        if not probe["range_ok"]:
            failures.append(f"thin-sample n={probe['n']} oracle range invalid")

    zscore_probe = _zscore_probe(o1)
    if not zscore_probe["M_star_equal"]:
        failures.append("zscore policy changed M*")
    if not zscore_probe["range_equal"]:
        failures.append("zscore policy changed [L,U]")

    skew_probe = _skew_probe()
    if not skew_probe["range_ok"]:
        failures.append("raw-skew variant range invalid")

    nan_probe = _nan_probe()
    if not nan_probe["passed"]:
        failures.append(f"NaN probe failed: {nan_probe['message']}")

    proof = {
        "audit": "calhousing_validity_tabular",
        "path": "intermediate_not_main_path",
        "package": "cvprofiles",
        "n_units": int(len(pd.read_csv(DATA / "scores.csv"))),
        "oracle": _core(o1),
        "harsh": _core(h),
        "cold_match": _core(o1) == _core(o2),
        "designed_valid": sorted(DESIGNED_VALID),
        "designed_invalid": sorted(DESIGNED_INVALID),
        "false_admissions": fa,
        "thin_sample_probes": thin_samples,
        "zscore_probe": zscore_probe,
        "skew_probe": skew_probe,
        "nan_fail_loud_probe": nan_probe,
        "capability_notes": {
            "engine_does_not_impute_missing_values": True,
            "engine_does_not_call_llms": True,
            "correlations_are_descriptive_only": True,
            "composite_measures_are_hand_weighted_not_llm_scores": True,
            "no_causal_claim": True,
        },
        "gates": {
            "FA_zero": not fa,
            "oracle_nonempty": not o1["empty"],
            "harsh_empty": bool(h["empty"]),
            "cold_H4": _core(o1) == _core(o2),
            "harsh_html_empty_callout": "Empty admissible set" in harsh_html,
            "same_scores_hash": o1["scores_hash"] == h["scores_hash"],
            "thin_samples_clean": all(
                p["harsh_empty"] and p["range_ok"] for p in thin_samples
            ),
            "zscore_m_star_invariant": bool(zscore_probe["M_star_equal"]),
            "zscore_range_invariant": bool(zscore_probe["range_equal"]),
            "skew_clean": bool(skew_probe["range_ok"]),
            "nan_fail_loud": bool(nan_probe["passed"]),
        },
        "passed": len(failures) == 0,
        "failures": failures,
    }
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
