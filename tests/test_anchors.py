"""θ-anchor documentation discipline tests (v2.0 thread c, M-c1; docs/12 D4/D6).

Semantics: anchors.yaml is a schema'd pre-data artifact — one anchor per
restriction id, hashed for provenance (anchors_hash), and EXCLUDED from the
freeze preimage (witness at the wiring level, M-c2). "Pre-data" is a process
commitment; the engine enforces completeness + hash, never timing.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from cvprofiles.anchors.pipeline import (
    AnchorError,
    AnchorsConfig,
    anchors_hash,
    anchors_payload,
    parse_anchors,
    validate_completeness,
)
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.run import RunManifest

_HEX64 = re.compile(r"^[0-9a-f]{64}$")


@pytest.fixture
def mini_anchors_path(mini_dir: Path) -> Path:
    return mini_dir / "anchors.yaml"


def test_parse_anchors_valid(mini_anchors_path: Path, mini_network: NetworkConfig) -> None:
    config = parse_anchors(mini_anchors_path)
    assert isinstance(config, AnchorsConfig)
    assert len(config.anchors) == 2
    ids = {a.restriction_id for a in config.anchors}
    assert ids == {r.id for r in mini_network.restrictions}


def test_parse_anchors_duplicate_restriction_fails() -> None:
    raw = {
        "schema_version": "1",
        "anchors": [
            {
                "restriction_id": "r1",
                "citation_key": "a",
                "source_phrase": "p",
                "anchor_kind": "literature",
                "pre_data": True,
            },
            {
                "restriction_id": "r1",
                "citation_key": "b",
                "source_phrase": "q",
                "anchor_kind": "derived",
                "pre_data": True,
            },
        ],
    }
    with pytest.raises(AnchorError, match="unique"):
        parse_anchors(raw)


def test_parse_anchors_bad_kind_fails() -> None:
    raw = {
        "schema_version": "1",
        "anchors": [
            {
                "restriction_id": "r1",
                "citation_key": "a",
                "source_phrase": "p",
                "anchor_kind": "made_up",  # type: ignore[dict-item]
                "pre_data": True,
            }
        ],
    }
    with pytest.raises(AnchorError):
        parse_anchors(raw)


def test_parse_anchors_missing_file_fails(tmp_path: Path) -> None:
    with pytest.raises(AnchorError, match="not found"):
        parse_anchors(tmp_path / "nope.yaml")


def test_completeness_ok_on_mini(mini_anchors_path: Path, mini_network: NetworkConfig) -> None:
    config = parse_anchors(mini_anchors_path)
    validate_completeness(config, mini_network)  # must not raise


def test_completeness_missing_anchor_fails(mini_network: NetworkConfig) -> None:
    raw = {
        "schema_version": "1",
        "anchors": [
            {
                "restriction_id": mini_network.restrictions[0].id,
                "citation_key": "a",
                "source_phrase": "p",
                "anchor_kind": "derived",
                "pre_data": True,
            }
        ],
    }
    config = parse_anchors(raw)
    with pytest.raises(AnchorError, match="missing"):
        validate_completeness(config, mini_network)


def test_completeness_unknown_restriction_fails(mini_network: NetworkConfig) -> None:
    raw = {
        "schema_version": "1",
        "anchors": [
            {
                "restriction_id": r.id,
                "citation_key": "a",
                "source_phrase": "p",
                "anchor_kind": "derived",
                "pre_data": True,
            }
            for r in mini_network.restrictions
        ]
        + [
            {
                "restriction_id": "r_ghost",
                "citation_key": "b",
                "source_phrase": "q",
                "anchor_kind": "derived",
                "pre_data": True,
            }
        ],
    }
    config = parse_anchors(raw)
    with pytest.raises(AnchorError, match="not in the network"):
        validate_completeness(config, mini_network)


def test_anchors_hash_is_canonical_and_sensitive(mini_anchors_path: Path) -> None:
    a = parse_anchors(mini_anchors_path)
    h1 = anchors_hash(a)
    assert _HEX64.match(h1)
    # same content -> same hash
    assert anchors_hash(parse_anchors(mini_anchors_path)) == h1
    # different source phrase -> different hash
    tweaked = a.model_copy(
        deep=True,
        update={
            "anchors": [
                anchor.model_copy(update={"source_phrase": "changed"})
                if anchor.restriction_id == "r_corr_min_aux"
                else anchor
                for anchor in a.anchors
            ]
        },
    )
    assert anchors_hash(tweaked) != h1


def test_anchors_payload_shape(mini_anchors_path: Path) -> None:
    config = parse_anchors(mini_anchors_path)
    payload = anchors_payload(config)
    assert payload["n_anchors"] == 2
    assert _HEX64.match(payload["anchors_hash"])
    assert payload["anchors"][0]["restriction_id"] == "r_corr_min_aux"
    assert payload["anchors"][0]["pre_data"] is True


def test_run_manifest_accepts_anchors_hash(mini_network: NetworkConfig) -> None:
    manifest = RunManifest(
        run_id="a" * 64,
        freeze={
            "scores_hash": "b" * 64,
            "network_hash": "c" * 64,
            "beta_hash": "d" * 64,
            "package_version": "2.0.0a1",
        },
        anchors_hash="e" * 64,
    )
    assert manifest.anchors_hash == "e" * 64
