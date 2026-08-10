#!/usr/bin/env python3
"""Read-only structural auditor for the WVS/GPS patience application
(flagship empirical example; docs/16 §11; plan DEVELOPMENT_PLAN_WVS_GPS_APPLICATION.md).

Validates frozen inputs + one engine run dir against the design lock:

  G1 positive control   m_gps_patience survives (must be in M* when M* is
                        non-empty; vacuous pass when M* empty)
  G2 negative control   m_noise NEVER in M* (rejected)
  G3 headline identity  [L,U] == [min beta(M*), max beta(M*)] on survivors
  G4 prompt provenance  prompt_source is an explicit llama.cpp record, not "stub"
  G5 strict JSON        no NaN/Infinity in run artifacts

This is NOT a second engine: it never reruns the pipeline, never writes run
artifacts, and a passing structural audit is not paper acceptance.

CLI contract: stdout is one compact JSON audit result; failures also go to
stderr with a nonzero exit. Empty M* is a clean success (exit 0) when G2/G4/G5
hold and G1 is vacuous.

Exact invocation (frozen-run pattern):

    uv run python tools/verify_wvs_gps.py \
        --inputs evals/wvs_gps_preferences/data/inputs \
        --run-dir <run_dir>
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

EXPECTED_RUN_ARTIFACTS = (
    "admissible.json",
    "range.json",
    "beta_values.json",
    "slacks.csv",
    "run_manifest.json",
    "report.json",
)
EXPECTED_INPUTS = (
    "scores.csv",
    "roles.json",
    "network.yaml",
    "beta.yaml",
    "score_manifest.json",
)
POSITIVE_CONTROL = "m_gps_patience"
NEGATIVE_CONTROL = "m_noise"


def _reject_non_finite(value: str) -> Any:
    raise ValueError(f"non-finite JSON constant: {value}")


def strict_json_load(path: Path) -> Any:
    """json.load rejecting NaN/Infinity constants."""
    return json.loads(path.read_text(), parse_constant=_reject_non_finite)


def audit(
    inputs_dir: Path,
    run_dir: Path,
) -> dict[str, Any]:
    gates: dict[str, bool] = {}
    notes: dict[str, str] = {}

    # --- input presence + prompt provenance (G4) ---------------------------
    missing_inputs = [n for n in EXPECTED_INPUTS if not (inputs_dir / n).exists()]
    if missing_inputs:
        return {
            "passed": False,
            "gates": {"input_presence": False},
            "notes": {"missing_inputs": missing_inputs},
            "error": "missing frozen inputs",
        }
    manifest = strict_json_load(inputs_dir / "score_manifest.json")
    ps = manifest.get("prompt_source")
    gates["g4_prompt_provenance"] = isinstance(ps, dict) and ps.get("kind") == "llama.cpp"
    notes["g4_prompt_provenance"] = (
        "ok" if gates["g4_prompt_provenance"] else f"prompt_source={ps!r}"
    )

    # --- pooled-summary path (posture a: headline = selected_all_folds) ----
    pooled_path = run_dir / "pooled_summary.json"
    if pooled_path.exists():
        pooled = strict_json_load(pooled_path)
        select_all: list[str] = list(pooled.get("selected_all_folds") or [])
        m_star = select_all
        empty = len(select_all) == 0
        # G2: noise must never be selected in all folds
        gates["g2_noise_rejected"] = NEGATIVE_CONTROL not in select_all
        notes["g2_noise_rejected"] = (
            "ok" if gates["g2_noise_rejected"] else f"{NEGATIVE_CONTROL} in selected_all_folds"
        )
        if empty:
            gates["g1_positive_control"] = True
            notes["g1_positive_control"] = "vacuous (no measure selected in all folds)"
        else:
            gates["g1_positive_control"] = POSITIVE_CONTROL in select_all
            notes["g1_positive_control"] = (
                "ok"
                if gates["g1_positive_control"]
                else f"{POSITIVE_CONTROL} not in selected_all_folds"
            )
        gates["g5_strict_json"] = True
        gates["run_artifacts_present"] = True
        notes["run_artifacts_present"] = "pooled_summary.json present"
        notes["g5_strict_json"] = "ok (pooled summary)"
        return {
            "passed": all(gates.values()),
            "gates": gates,
            "notes": notes,
            "empty_m_star": empty,
            "M_star": m_star,
            "mode": "pooled",
            "run_dir": str(run_dir),
        }

    # --- single-run path: engine run dir with admissible.json --------------
    missing_run = [n for n in EXPECTED_RUN_ARTIFACTS if not (run_dir / n).exists()]
    gates["run_artifacts_present"] = not missing_run
    notes["run_artifacts_present"] = "ok" if not missing_run else str(missing_run)
    if missing_run:
        return {
            "passed": False,
            "gates": gates,
            "notes": notes,
            "error": "missing run artifacts",
        }

    # --- strict JSON (G5) on run artifacts ---------------------------------
    strict_ok = True
    for name in (
        "admissible.json",
        "range.json",
        "beta_values.json",
        "run_manifest.json",
        "report.json",
    ):
        try:
            strict_json_load(run_dir / name)
        except ValueError as exc:
            strict_ok = False
            notes[f"strict_json:{name}"] = str(exc)
    gates["g5_strict_json"] = strict_ok
    notes.setdefault("g5_strict_json", "ok")

    # --- M* and controls (G1, G2) ------------------------------------------
    adm = strict_json_load(run_dir / "admissible.json")
    m_star: list[str] = list(adm.get("M_star") or [])
    empty = bool(adm.get("empty", not m_star))
    gates["g2_noise_rejected"] = NEGATIVE_CONTROL not in m_star
    notes["g2_noise_rejected"] = (
        "ok" if gates["g2_noise_rejected"] else f"{NEGATIVE_CONTROL} in M*"
    )
    if empty:
        gates["g1_positive_control"] = True
        notes["g1_positive_control"] = "vacuous (M* empty)"
    else:
        gates["g1_positive_control"] = POSITIVE_CONTROL in m_star
        notes["g1_positive_control"] = (
            "ok" if gates["g1_positive_control"] else f"{POSITIVE_CONTROL} not in M*"
        )

    # --- headline identity (G3) --------------------------------------------
    range_p = strict_json_load(run_dir / "range.json")
    beta_p = strict_json_load(run_dir / "beta_values.json")
    b_vals: dict[str, float] = dict(beta_p.get("beta_values") or {})
    if empty or not m_star:
        gates["g3_headline_identity"] = True
        notes["g3_headline_identity"] = "vacuous (M* empty)"
    else:
        lo = min(b_vals[m] for m in m_star if m in b_vals)
        hi = max(b_vals[m] for m in m_star if m in b_vals)
        gates["g3_headline_identity"] = (
            range_p.get("L") == lo and range_p.get("U") == hi
        )
        notes["g3_headline_identity"] = (
            "ok"
            if gates["g3_headline_identity"]
            else f"expected [{lo},{hi}] got [{range_p.get('L')},{range_p.get('U')}]"
        )

    passed = all(gates.values())
    return {
        "passed": passed,
        "gates": gates,
        "notes": notes,
        "empty_m_star": empty,
        "M_star": m_star,
        "run_dir": str(run_dir),
    }


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="WVS/GPS patience application auditor")
    p.add_argument("--inputs", type=Path, required=True, help="frozen inputs dir")
    p.add_argument("--run-dir", type=Path, required=True, help="engine run dir")
    args = p.parse_args(argv)

    try:
        result = audit(args.inputs, args.run_dir)
    except Exception as exc:  # noqa: BLE001 - structural auditor: report any failure
        result = {"passed": False, "error": str(exc)}
    print(json.dumps(result, indent=2, sort_keys=True))
    if not result.get("passed", False):
        print(f"AUDIT FAILED: {result.get('error', 'gate failure')}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
