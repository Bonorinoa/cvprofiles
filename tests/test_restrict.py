"""RESTRICT state contract tests (M3 / G3)."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from cvprofiles.restrict.pipeline import (
    RestrictError,
    load_beta,
    load_network,
    run_restrict,
    write_restrict_artifacts,
)
from cvprofiles.schemas.scores import ScoreColumnRoles


def test_restrict_mini_golden_hashes(
    mini_dir: Path,
    mini_roles: ScoreColumnRoles,
    mini_expected_freeze: dict,
) -> None:
    bundle = run_restrict(
        mini_roles,
        mini_dir / "network.yaml",
        mini_dir / "beta.yaml",
    )
    assert bundle.network_hash == mini_expected_freeze["network_hash"]
    assert bundle.beta_hash == mini_expected_freeze["beta_hash"]
    assert bundle.delta == 0.0
    assert len(bundle.network.restrictions) == 2
    assert bundle.beta.type == "corr_y"
    assert bundle.beta.outcome == "y"


def test_load_network_and_beta_from_yaml(mini_dir: Path) -> None:
    net = load_network(mini_dir / "network.yaml")
    beta = load_beta(mini_dir / "beta.yaml")
    assert net.name == "mini_v1_oracle"
    assert beta.type == "corr_y"


def test_restrict_missing_variable_fails(
    mini_roles: ScoreColumnRoles,
    mini_dir: Path,
) -> None:
    raw = yaml.safe_load((mini_dir / "network.yaml").read_text())
    raw["restrictions"][0]["params"]["variable"] = "not_a_column"
    with pytest.raises(RestrictError, match="not found"):
        run_restrict(mini_roles, raw, mini_dir / "beta.yaml")


def test_restrict_missing_outcome_fails(
    mini_roles: ScoreColumnRoles,
    mini_dir: Path,
) -> None:
    with pytest.raises(RestrictError, match="outcome"):
        run_restrict(
            mini_roles,
            mini_dir / "network.yaml",
            {"type": "corr_y", "outcome": "nope", "params": {}},
        )


def test_restrict_unknown_type_fails(
    mini_roles: ScoreColumnRoles,
    mini_dir: Path,
) -> None:
    raw = yaml.safe_load((mini_dir / "network.yaml").read_text())
    raw["restrictions"][0]["type"] = "not_real"
    with pytest.raises(RestrictError, match="invalid network"):
        run_restrict(mini_roles, raw, mini_dir / "beta.yaml")


def test_write_restrict_artifacts(
    mini_dir: Path,
    mini_roles: ScoreColumnRoles,
    tmp_path: Path,
    mini_expected_freeze: dict,
) -> None:
    bundle = run_restrict(
        mini_roles,
        mini_dir / "network.yaml",
        mini_dir / "beta.yaml",
    )
    paths = write_restrict_artifacts(bundle, tmp_path)
    assert paths["network_resolved.json"].is_file()
    assert paths["beta_resolved.json"].is_file()
    assert paths["restrict_bundle.json"].is_file()
    text = paths["restrict_bundle.json"].read_text()
    assert mini_expected_freeze["network_hash"] in text
