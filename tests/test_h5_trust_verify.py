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
            "package_version": "2.0.1a1",
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


# --- M-c3: θ-anchor completeness pass (docs/17 §6 transcription) ---

H5_ANCHORS = {
    "schema_version": "1",
    "anchors": [
        {
            "restriction_id": "r_corr_min_gps_trust",
            "citation_key": "oecd2017",
            "source_phrase": "OECD (2017) r≈0.29 country-level survey↔behavioral",
            "anchor_kind": "literature",
            "pre_data": True,
        },
        {
            "restriction_id": "r_corr_min_rule_of_law",
            "citation_key": "aac2010_martinangeli2024",
            "source_phrase": "trust–institutions correlations typically ≥ 0.4",
            "anchor_kind": "literature",
            "pre_data": True,
        },
        {
            "restriction_id": "r_corr_sign_gini_neg",
            "citation_key": "bjornskov2008",
            "source_phrase": "Bjørnskov (2008): negative trust–inequality relationship",
            "anchor_kind": "literature",
            "pre_data": True,
        },
    ],
}

H5_NETWORK = {
    "schema_version": "1",
    "delta": 0.0,
    "restrictions": [
        {
            "id": "r_corr_min_gps_trust",
            "type": "corr_min",
            "theta": 0.3,
            "params": {"variable": "gps_trust"},
        },
        {
            "id": "r_corr_min_rule_of_law",
            "type": "corr_min",
            "theta": 0.3,
            "params": {"variable": "rule_of_law"},
        },
        {
            "id": "r_corr_sign_gini_neg",
            "type": "corr_sign",
            "theta": 0.1,
            "params": {"variable": "gini", "sign": -1},
        },
    ],
}


def _write_yaml(tmp_path: Path, name: str, payload: object) -> Path:
    import yaml

    p = tmp_path / name
    p.write_text(yaml.safe_dump(payload))
    return p


def _run_with_anchors(tmp_path: Path, anchors: dict, network: dict) -> dict:
    payload = _proof(m_star=["m_trust_general", "m_trust_in_group"], lower=0.2, upper=0.6)
    proof = _write(tmp_path, "proof_summary.json", payload)
    roles_payload = {
        "unit_id": "iso3",
        "measures": list(payload["designed_valid"]) + list(payload["designed_invalid"]),
        "aux": [],
        "outcome": None,
        "diagnostic": [],
    }
    roles = _write(tmp_path, "roles.json", roles_payload)
    anchors_path = _write_yaml(tmp_path, "anchors.yaml", anchors)
    network_path = _write_yaml(tmp_path, "network.yaml", network)
    for name in va.EXPECTED_ARTIFACTS:
        (tmp_path / name).touch()
    return va.audit(
        proof, roles, tmp_path, anchors_path=anchors_path, network_path=network_path
    )


def test_audit_anchors_pass_on_transcription(tmp_path: Path) -> None:
    res = _run_with_anchors(tmp_path, H5_ANCHORS, H5_NETWORK)
    assert res["passed"] is True
    assert res["errors"] == []


def test_audit_anchors_missing_restriction_fails(tmp_path: Path) -> None:
    anchors = {
        "schema_version": "1",
        "anchors": H5_ANCHORS["anchors"][:2],
    }
    res = _run_with_anchors(tmp_path, anchors, H5_NETWORK)
    assert res["passed"] is False
    assert any("missing" in e for e in res["errors"])


def test_audit_anchors_unknown_restriction_fails(tmp_path: Path) -> None:
    anchors = {
        "schema_version": "1",
        "anchors": H5_ANCHORS["anchors"]
        + [
            {
                "restriction_id": "r_ghost",
                "citation_key": "x",
                "source_phrase": "y",
                "anchor_kind": "derived",
                "pre_data": True,
            }
        ],
    }
    res = _run_with_anchors(tmp_path, anchors, H5_NETWORK)
    assert res["passed"] is False
    assert any("not in the network" in e for e in res["errors"])


def test_audit_anchors_not_pre_data_fails(tmp_path: Path) -> None:
    anchors = {
        "schema_version": "1",
        "anchors": [
            {**a, "pre_data": False} if a["restriction_id"] == "r_corr_min_gps_trust" else a
            for a in H5_ANCHORS["anchors"]
        ],
    }
    res = _run_with_anchors(tmp_path, anchors, H5_NETWORK)
    assert res["passed"] is False
    assert any("pre_data" in e for e in res["errors"])
