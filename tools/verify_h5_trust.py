#!/usr/bin/env python3
"""Read-only structural auditor for the H5 Trust proof (docs/17 section 11).

Validates ``proof_summary.json`` (written by evals/h5_trust/verify_audit.py)
against the design lock: strict JSON (no NaN/Infinity), FA=0 for
designed-invalids, L<=U (or null when empty), cold freeze-core equality,
artifact presence, and provenance hash shapes.

This is NOT a second engine: it never reruns the pipeline, never writes run
artifacts, and a passing structural audit is not paper acceptance.

CLI contract: stdout is one compact JSON result; failures also go to stderr
with a nonzero exit.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

EXPECTED_ARTIFACTS = (
    "report.html",
    "report.json",
    "admissible.json",
    "range.json",
    "slacks.csv",
    "run_manifest.json",
    "score_manifest.json",
)
HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")


def _reject_non_finite(value: str) -> Any:
    raise ValueError(f"non-finite JSON constant: {value}")


def strict_json_loads(text: str) -> Any:
    """json.loads rejecting NaN/Infinity constants."""
    return json.loads(text, parse_constant=_reject_non_finite)


def _check_finite(obj: Any, path: str, errors: list[str]) -> None:
    if isinstance(obj, float) and (obj != obj or obj in (float("inf"), float("-inf"))):
        errors.append(f"non-finite value at {path}")


def strict_json_load(path: Path) -> Any:
    text = path.read_text()
    obj = strict_json_loads(text)
    errors: list[str] = []
    _walk_finite(obj, "", errors)
    if errors:
        raise ValueError(f"{path.name}: {errors[0]}")
    return obj


def _walk_finite(obj: Any, path: str, errors: list[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _walk_finite(v, f"{path}.{k}", errors)
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            _walk_finite(v, f"{path}[{i}]", errors)
    else:
        _check_finite(obj, path, errors)


def audit(
    proof_path: Path,
    roles_path: Path,
    out_root: Path,
    anchors_path: Path | None = None,
    network_path: Path | None = None,
) -> dict:
    """Run all structural checks; return {"passed": bool, "errors": [...]}.

    ``anchors_path`` + ``network_path`` (optional, M-c3): assert the θ-anchor
    transcription is complete against the pinned network and all anchors
    declare ``pre_data=True`` (docs/17 §6 transcription).
    """
    errors: list[str] = []

    try:
        proof = strict_json_load(proof_path)
    except (ValueError, OSError) as exc:
        return {"passed": False, "errors": [f"proof load failed: {exc}"], "n_errors": 1}

    try:
        roles = strict_json_load(roles_path)
    except (ValueError, OSError) as exc:
        return {"passed": False, "errors": [f"roles load failed: {exc}"], "n_errors": 1}

    menu = set(roles.get("measures", []))
    designed_invalid = set(proof.get("designed_invalid", []))
    m_star = set(proof.get("M_star", []))
    empty = proof.get("empty", None)
    l_val = proof.get("L", None)
    u_val = proof.get("U", None)

    if "audit" not in proof or proof.get("audit") != "h5_trust_generalized":
        errors.append("proof.audit must be h5_trust_generalized")

    settings = proof.get("settings", {})
    for key in ("scores_hash", "network_hash", "beta_hash"):
        if not HEX64.match(str(settings.get(key, ""))):
            errors.append(f"settings.{key} is not a 64-char lowercase hex hash")
    parent = settings.get("parent_sha")
    if parent is not None and not HEX40.match(str(parent)):
        errors.append("settings.parent_sha is not a 40-char lowercase hex SHA")

    if not m_star.issubset(menu):
        errors.append(f"M_star contains measures outside the menu: {sorted(m_star - menu)}")

    fa = sorted(m_star & designed_invalid)
    if fa:
        errors.append(f"designed-invalid measure(s) admitted: {fa}")

    if proof.get("gates", {}).get("FA_zero", False) != (not fa):
        errors.append("gates.FA_zero disagrees with M_star")

    cold_match = proof.get("cold_match", None)
    if cold_match is not True:
        errors.append("cold_match must be true (freeze-core equality across two runs)")
    if proof.get("gates", {}).get("cold_H4", False) != (cold_match is True):
        errors.append("gates.cold_H4 disagrees with cold_match")

    if bool(empty) != (len(m_star) == 0):
        errors.append(f"empty flag {empty} disagrees with |M_star|={len(m_star)}")

    if empty:
        if l_val is not None or u_val is not None:
            errors.append("empty proof must have L=null and U=null")
    else:
        if l_val is None or u_val is None:
            errors.append("non-empty proof must have finite L and U")
        elif l_val > u_val:
            errors.append(f"L={l_val} exceeds U={u_val}")

    if proof.get("failures"):
        errors.append(f"proof.failures is non-empty: {proof['failures']}")

    missing = [name for name in EXPECTED_ARTIFACTS if not (out_root / name).exists()]
    if missing:
        errors.append(f"missing artifacts under {out_root}: {missing}")

    if anchors_path is not None:
        try:
            from cvprofiles.anchors.pipeline import parse_anchors, validate_completeness
            from cvprofiles.schemas.network import parse_network
        except ImportError as exc:
            errors.append(f"anchors check requires cvprofiles importable: {exc}")
        else:
            if network_path is None:
                errors.append("--network required when --anchors is provided")
            else:
                try:
                    config = parse_anchors(anchors_path)
                    network = parse_network(yaml.safe_load(network_path.read_text()))
                    validate_completeness(config, network)
                    if not all(a.pre_data for a in config.anchors):
                        errors.append("all anchors must declare pre_data=True")
                except Exception as exc:  # AnchorError / ValidationError / OSError
                    errors.append(f"anchors audit failed: {exc}")

    return {"passed": not errors, "errors": errors, "n_errors": len(errors)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, required=True, help="proof_summary.json path")
    parser.add_argument("--roles", type=Path, required=True, help="roles_h5_trust.json path")
    parser.add_argument("--out-root", type=Path, required=True, help="run output directory")
    parser.add_argument(
        "--anchors",
        type=Path,
        required=False,
        help="θ-anchor YAML (docs/17 §6 transcription); completeness audited when provided",
    )
    parser.add_argument(
        "--network",
        type=Path,
        required=False,
        help="pinned network YAML (required with --anchors)",
    )
    args = parser.parse_args(argv)

    result = audit(
        args.proof,
        args.roles,
        args.out_root,
        anchors_path=args.anchors,
        network_path=args.network,
    )
    print(json.dumps(result, sort_keys=True))
    if not result["passed"]:
        for e in result["errors"]:
            print(f"ERROR: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
