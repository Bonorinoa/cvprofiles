"""TDD tests for the batch orchestrator (tools/run_many.py).

Contract: one shared score matrix + roles, N (network, beta) profiles from a
YAML manifest, each run via run_profile into <out_root>/<profile_id>/, plus a
batch summary JSON artifact and a machine-clean stdout JSON. Empty M* in any
profile is a clean success (exit-0 semantics preserved). Fail loud on missing
manifest files or unknown profiles.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import run_many as rm  # noqa: E402


def _write_manifest(tmp_path: Path, payload: object) -> Path:
    p = tmp_path / "manifest.yaml"
    p.write_text(yaml.safe_dump(payload))
    return p


def test_run_many_two_profiles_mini(tmp_path: Path, mini_dir: Path) -> None:
    """Non-empty (network.yaml) and empty (network_harsh.yaml) profiles in one batch."""
    manifest = _write_manifest(
        tmp_path,
        {
            "profiles": [
                {
                    "id": "good",
                    "network": str(mini_dir / "network.yaml"),
                    "beta": str(mini_dir / "beta.yaml"),
                },
                {
                    "id": "harsh",
                    "network": str(mini_dir / "network_harsh.yaml"),
                    "beta": str(mini_dir / "beta.yaml"),
                },
            ]
        },
    )
    result = rm.run_many(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        manifest=manifest,
        out_root=tmp_path / "batch",
        seed=0,
    )

    assert set(result.profile_ids) == {"good", "harsh"}
    good = result.by_id["good"]
    harsh = result.by_id["harsh"]

    # Non-empty profile: same M* as the single-run mini fixture contract.
    assert good.summary["empty"] is False
    assert set(good.summary["M_star"]) == {"m_good", "m_weak"}
    assert good.summary["L"] <= good.summary["U"]

    # Empty profile is a clean success, not a crash.
    assert harsh.summary["empty"] is True
    assert harsh.summary["M_star"] == []
    assert harsh.summary["L"] is None
    assert harsh.summary["U"] is None

    # Distinct run ids per profile; report artifacts written for both.
    assert good.summary["run_id"] != harsh.summary["run_id"]
    for pid in ("good", "harsh"):
        out_dir = tmp_path / "batch" / pid
        assert (out_dir / "report.html").is_file()
        assert (out_dir / "range.json").is_file()

    # Batch summary artifact on disk, machine-clean JSON.
    summary_path = tmp_path / "batch" / "batch_summary.json"
    assert summary_path.is_file()
    payload = json.loads(summary_path.read_text())
    assert {p["id"] for p in payload["profiles"]} == {"good", "harsh"}


def test_run_many_manifest_relative_paths(tmp_path: Path, mini_dir: Path) -> None:
    """Network/beta paths resolve relative to the manifest file location."""
    (tmp_path / "nets").mkdir()
    (tmp_path / "bets").mkdir()
    (tmp_path / "nets" / "n.yaml").write_text((mini_dir / "network.yaml").read_text())
    (tmp_path / "bets" / "b.yaml").write_text((mini_dir / "beta.yaml").read_text())
    manifest = _write_manifest(
        tmp_path,
        {"profiles": [{"id": "rel", "network": "nets/n.yaml", "beta": "bets/b.yaml"}]},
    )
    result = rm.run_many(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        manifest=manifest,
        out_root=tmp_path / "batch",
        seed=0,
    )
    assert set(result.profile_ids) == {"rel"}
    assert result.by_id["rel"].summary["empty"] is False


def test_run_many_missing_profile_file_fails_loud(tmp_path: Path, mini_dir: Path) -> None:
    """A manifest pointing at a missing network/beta raises BatchError, never silence."""
    manifest = _write_manifest(
        tmp_path,
        {
            "profiles": [
                {
                    "id": "broken",
                    "network": "does_not_exist.yaml",
                    "beta": str(mini_dir / "beta.yaml"),
                }
            ]
        },
    )
    with pytest.raises(rm.BatchError):
        rm.run_many(
            scores=mini_dir / "scores.csv",
            roles=mini_dir / "roles.json",
            manifest=manifest,
            out_root=tmp_path / "batch",
            seed=0,
        )


def test_run_many_manifest_missing_profiles_key_fails_loud(tmp_path: Path, mini_dir: Path) -> None:
    manifest = _write_manifest(tmp_path, {"unexpected": []})
    with pytest.raises(rm.BatchError):
        rm.run_many(
            scores=mini_dir / "scores.csv",
            roles=mini_dir / "roles.json",
            manifest=manifest,
            out_root=tmp_path / "batch",
            seed=0,
        )


def test_run_many_bad_policy_fails_loud(tmp_path: Path, mini_dir: Path) -> None:
    """Unknown SCORE policy must raise through the batch, never be swallowed."""
    manifest = _write_manifest(
        tmp_path,
        {
            "profiles": [
                {
                    "id": "good",
                    "network": str(mini_dir / "network.yaml"),
                    "beta": str(mini_dir / "beta.yaml"),
                }
            ]
        },
    )
    with pytest.raises(ValueError):
        rm.run_many(
            scores=mini_dir / "scores.csv",
            roles=mini_dir / "roles.json",
            manifest=manifest,
            out_root=tmp_path / "batch",
            seed=0,
            policy="bogus",
        )
