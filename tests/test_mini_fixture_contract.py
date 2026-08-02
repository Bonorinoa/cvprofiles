"""End-to-end mini_v1 load through schemas + freeze only (no SCORE/IDENTIFY)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yaml

from cvprofiles import __version__
from cvprofiles.freeze import compute_run_id, hash_beta, hash_network, hash_scores_frame
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.run import FreezeBundle, RunManifest
from cvprofiles.schemas.scores import ScoreColumnRoles, ScoreManifest


def test_mini_fixture_files_present(mini_dir: Path) -> None:
    for name in (
        "scores.csv",
        "roles.json",
        "network.yaml",
        "beta.yaml",
        "expected_freeze.json",
        "README.md",
    ):
        assert (mini_dir / name).is_file(), name


def test_mini_end_to_end_freeze_only(
    mini_dir: Path,
    mini_expected_freeze: dict,
) -> None:
    roles = ScoreColumnRoles.model_validate_json((mini_dir / "roles.json").read_text())
    df = pd.read_csv(mini_dir / "scores.csv")
    network = NetworkConfig.model_validate(yaml.safe_load((mini_dir / "network.yaml").read_text()))
    beta = BetaSpec.model_validate(yaml.safe_load((mini_dir / "beta.yaml").read_text()))

    freeze_cols = [roles.unit_id, *roles.measures, *roles.aux]
    if roles.outcome:
        freeze_cols.append(roles.outcome)

    assert set(roles.measures).issubset(df.columns)
    assert roles.outcome in df.columns
    assert "V_star" in df.columns  # diagnostic present on disk
    assert "V_star" not in freeze_cols

    scores_hash = hash_scores_frame(df, freeze_cols, unit_id_col=roles.unit_id)
    network_hash = hash_network(network)
    beta_hash = hash_beta(beta)

    manifest = ScoreManifest(
        roles=roles,
        n_rows=len(df),
        n_measures=len(roles.measures),
        measure_columns=list(roles.measures),
        scores_hash=scores_hash,
        normalization={"policy": "none", "zscore_measures": False},
    )
    assert manifest.n_rows == 10

    run_id = compute_run_id(
        scores_hash=scores_hash,
        network_hash=network_hash,
        beta_hash=beta_hash,
        package_version=__version__,
        seed=0,
        delta=float(network.delta),
        n_boot=None,
        config={},
    )
    freeze = FreezeBundle(
        scores_hash=scores_hash,
        network_hash=network_hash,
        beta_hash=beta_hash,
        package_version=__version__,
        seed=0,
        delta=float(network.delta),
        n_boot=None,
        config={},
    )
    run = RunManifest(
        run_id=run_id,
        freeze=freeze,
        created_at="1970-01-01T00:00:00Z",  # wall clock must not affect run_id
        artifact_paths={"scores": "scores.csv"},
    )
    assert run.run_id == mini_expected_freeze["run_id"]
    assert run.freeze.scores_hash == mini_expected_freeze["scores_hash"]
    # created_at lives only on RunManifest, not FreezeBundle / run_id
    assert not hasattr(run.freeze, "created_at") or "created_at" not in freeze.model_dump()
