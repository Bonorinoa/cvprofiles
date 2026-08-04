"""Refresh data/fixtures/mini_v1/expected_freeze.json from the installed package.

Why: ``run_id`` pins ``package_version`` (docs/12 M1 lock). Any version bump
moves ``run_id``; the mini_v1 golden must be refreshed **in the same commit**.

Contract:
- Reads ``cvprofiles.__version__``; never hardcodes a version string.
- Recomputes scores_hash / network_hash / beta_hash / run_id with the exact
  same freeze functions the contract tests use.
- Fails loud if scores/network/beta hashes change vs. the existing golden:
  those are pinned by fixture contents, so a change means the freeze
  algorithm drifted (stop and investigate — docs/12), not a silent rewrite.
- Rewrites only ``package_version`` and ``run_id``; all other fields kept.

Usage: uv run python tools/refresh_mini_golden.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import yaml

from cvprofiles import __version__
from cvprofiles.freeze import compute_run_id, hash_beta, hash_network, hash_scores_frame
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.scores import ScoreColumnRoles

REPO_ROOT = Path(__file__).resolve().parents[1]
MINI = REPO_ROOT / "data" / "fixtures" / "mini_v1"
GOLDEN = MINI / "expected_freeze.json"


def main() -> None:
    roles = ScoreColumnRoles.model_validate_json((MINI / "roles.json").read_text())
    df = pd.read_csv(MINI / "scores.csv")
    network = NetworkConfig.model_validate(
        yaml.safe_load((MINI / "network.yaml").read_text())
    )
    beta = BetaSpec.model_validate(yaml.safe_load((MINI / "beta.yaml").read_text()))

    freeze_cols = [roles.unit_id, *roles.measures, *roles.aux]
    if roles.outcome:
        freeze_cols.append(roles.outcome)

    scores_hash = hash_scores_frame(df, freeze_cols, unit_id_col=roles.unit_id)
    network_hash = hash_network(network)
    beta_hash = hash_beta(beta)
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

    golden = json.loads(GOLDEN.read_text())

    # Invariants: fixture contents pin these hashes. If any moved, the freeze
    # algorithm drifted — investigate before refreshing (docs/12).
    for key, value in (
        ("scores_hash", scores_hash),
        ("network_hash", network_hash),
        ("beta_hash", beta_hash),
    ):
        if golden[key] != value:
            raise SystemExit(
                f"ABORT: {key} changed vs golden ({golden[key][:12]}... != "
                f"{value[:12]}...). Fixture content or freeze algorithm drifted."
            )
    if golden["freeze_columns"] != freeze_cols:
        raise SystemExit(f"ABORT: freeze columns changed: {freeze_cols}")

    old_version = golden["package_version"]
    golden["package_version"] = __version__
    golden["run_id"] = run_id

    GOLDEN.write_text(
        json.dumps(golden, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"refreshed {GOLDEN.relative_to(REPO_ROOT)}: {old_version} -> {__version__}")
    print(f"run_id: {run_id}")


if __name__ == "__main__":
    main()
