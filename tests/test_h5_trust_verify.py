"""TDD tests for the read-only H5 Trust proof auditor (tools/verify_h5_trust.py).

Auditor contract per docs/17 section 11: strict JSON (no NaN/Infinity),
FA=0 for designed-invalids, L<=U (or null when empty), freeze-core cold
equality recorded, artifact presence. Structural audit != paper acceptance.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import verify_h5_trust as va  # noqa: E402


def _proof(*, m_star: list[str], lower: float | None, upper: float | None) -> dict:
    return {
        "audit": "h5_trust_generalized",
        "settings": {
            "n_countries": 40,
            "floor": 200,
            "seed": 20260804,
            "policy": "none",
            "delta": 0.0,
            "package_version": "1.1.0a1",
            "parent_sha": "a" * 40,
            "scores_hash": "b" * 64,
            "network_hash": "c" * 64,
            "beta_hash": "d" * 64,
        },
        "gates": {"FA_zero": True, "cold_H4": True, "artifacts_present": True},
        "designed_valid": [
            "m_trust_general",
            "m_trust_in_group",
            "m_trust_out_group",
            "m_trust_institution",
        ],
        "designed_invalid": ["m_noise", "m_share_agriculture"],
        "M_star": m_star,
        "L": lower,
        "U": upper,
        "empty": lower is None and upper is None,
        "rejected": {},
        "cold_match": True,
        "failures": [],
    }


def _write(tmp_path: Path, name: str, payload: object) -> Path:
    p = tmp_path / name
    p.write_text(json.dumps(payload))
    return p


def _run(tmp_path: Path, payload: object, out_root: Path | None = None) -> dict:
    proof = _write(tmp_path, "proof_summary.json", payload)
    roles_payload = {
        "unit_id": "iso3",
        "measures": list(payload["designed_valid"]) + list(payload["designed_invalid"]),
        "aux": [],
        "outcome": None,
        "diagnostic": [],
    }
    roles = _write(tmp_path, "roles.json", roles_payload)
    root = out_root or tmp_path
    if out_root is None:
        # Clean-proof fixture: the expected run artifacts exist.
        for name in va.EXPECTED_ARTIFACTS:
            (root / name).touch()
    return va.audit(proof, roles, root)


def test_strict_json_rejects_nan() -> None:
    with pytest.raises(ValueError, match="non-finite"):
        va.strict_json_loads('{"x": NaN}')


def test_strict_json_rejects_infinity() -> None:
    with pytest.raises(ValueError, match="non-finite"):
        va.strict_json_loads('{"x": Infinity}')


def test_audit_passes_on_clean_proof(tmp_path: Path) -> None:
    payload = _proof(m_star=["m_trust_general", "m_trust_in_group"], lower=0.2, upper=0.6)
    res = _run(tmp_path, payload)
    assert res["passed"] is True
    assert res["errors"] == []


def test_audit_passes_on_empty_proof(tmp_path: Path) -> None:
    payload = _proof(m_star=[], lower=None, upper=None)
    res = _run(tmp_path, payload)
    assert res["passed"] is True  # empty M* is honest, not a failure


def test_audit_fails_when_designed_invalid_admitted(tmp_path: Path) -> None:
    payload = _proof(m_star=["m_trust_general", "m_noise"], lower=0.2, upper=0.6)
    res = _run(tmp_path, payload)
    assert res["passed"] is False
    assert any("m_noise" in e for e in res["errors"])


def test_audit_fails_when_l_greater_than_u(tmp_path: Path) -> None:
    payload = _proof(m_star=["m_trust_general"], lower=0.8, upper=0.2)
    res = _run(tmp_path, payload)
    assert res["passed"] is False


def test_audit_fails_when_cold_match_false(tmp_path: Path) -> None:
    payload = _proof(m_star=["m_trust_general"], lower=0.2, upper=0.6)
    payload["cold_match"] = False
    payload["gates"]["cold_H4"] = False
    res = _run(tmp_path, payload)
    assert res["passed"] is False


def test_audit_fails_when_nonempty_has_null_range(tmp_path: Path) -> None:
    payload = _proof(m_star=["m_trust_general"], lower=None, upper=None)
    res = _run(tmp_path, payload)
    assert res["passed"] is False


def test_audit_checks_artifact_presence(tmp_path: Path) -> None:
    payload = _proof(m_star=["m_trust_general"], lower=0.2, upper=0.6)
    empty_root = tmp_path / "no_artifacts"
    empty_root.mkdir()
    res = _run(tmp_path, payload, out_root=empty_root)
    assert res["passed"] is False
    assert any("report" in e for e in res["errors"])


def test_audit_validates_provenance_hashes(tmp_path: Path) -> None:
    payload = _proof(m_star=["m_trust_general"], lower=0.2, upper=0.6)
    payload["settings"]["scores_hash"] = "not-a-hash"
    res = _run(tmp_path, payload)
    assert res["passed"] is False
