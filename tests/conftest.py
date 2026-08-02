"""Shared fixtures for cvprofiles contract tests."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest
import yaml

from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.scores import ScoreColumnRoles

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_MINI = REPO_ROOT / "data" / "fixtures" / "mini_v1"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def mini_dir() -> Path:
    assert FIXTURE_MINI.is_dir(), f"missing mini fixture: {FIXTURE_MINI}"
    return FIXTURE_MINI


@pytest.fixture(scope="session")
def mini_roles(mini_dir: Path) -> ScoreColumnRoles:
    return ScoreColumnRoles.model_validate_json((mini_dir / "roles.json").read_text())


@pytest.fixture(scope="session")
def mini_scores_df(mini_dir: Path) -> pd.DataFrame:
    return pd.read_csv(mini_dir / "scores.csv")


@pytest.fixture(scope="session")
def mini_network(mini_dir: Path) -> NetworkConfig:
    raw = yaml.safe_load((mini_dir / "network.yaml").read_text())
    return NetworkConfig.model_validate(raw)


@pytest.fixture(scope="session")
def mini_beta(mini_dir: Path) -> BetaSpec:
    raw = yaml.safe_load((mini_dir / "beta.yaml").read_text())
    return BetaSpec.model_validate(raw)


@pytest.fixture(scope="session")
def mini_expected_freeze(mini_dir: Path) -> dict:
    return json.loads((mini_dir / "expected_freeze.json").read_text())


@pytest.fixture(scope="session")
def mini_freeze_columns(mini_roles: ScoreColumnRoles) -> list[str]:
    cols = [mini_roles.unit_id, *mini_roles.measures, *mini_roles.aux]
    if mini_roles.outcome is not None:
        cols.append(mini_roles.outcome)
    return cols
