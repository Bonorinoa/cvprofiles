"""Generate the v1.1 package-native synthetic evidence summary.

This is an evidence harness, not a second engine. It deliberately calls:

    run_battery -> run_score -> run_restrict -> run_identify

for the locked v1.0 package battery, then uses run_profile for the v1.1
inference-layer probes. The museum PoC is checked by AST and never imported.
"""

from __future__ import annotations

import ast
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml

from cvprofiles import __version__
from cvprofiles.inference.bootstrap import bootstrap_payload
from cvprofiles.inference.theta_grid import theta_grid_payload
from cvprofiles.pipeline import run_profile
from cvprofiles.synth.battery import DEFAULT_SEEDS, SCENARIOS, run_battery
from cvprofiles.synth.dgp import make_dgp, roles_for_menu
from cvprofiles.synth.oracle_r import beta_corr_y, network_for

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = REPO_ROOT / "reports" / "summaries" / "v1_1_package_synth_summary.json"
RUN_ROOT = REPO_ROOT / "reports" / "runs" / "v1_1_package_synth"
BATTERY_N = 1000
INFERENCE_SEED = 7
N_BOOT = 80
GRID = [0.5, 1.0, 2.0]
ALT_GRID = [0.75, 1.0, 2.5]


def _museum_import_check() -> dict[str, Any]:
    """Run the same AST-level import hygiene check used by CI."""
    forbidden = ("openai", "anthropic", "httpx", "requests", "litellm")
    museum = ("v0_poc", "evals.synthetic")
    offenders: list[str] = []
    src = REPO_ROOT / "src" / "cvprofiles"
    for path in src.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if any(alias.name == f or alias.name.startswith(f + ".") for f in forbidden):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:{alias.name}")
                    if any(m in alias.name for m in museum):
                        offenders.append(f"{path.relative_to(REPO_ROOT)}:museum:{alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if any(module == f or module.startswith(f + ".") for f in forbidden):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{module}")
                if any(m in module for m in museum):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:museum:{module}")
    return {
        "passed": not offenders,
        "offenders": offenders,
        "museum_file_present": (REPO_ROOT / "evals" / "synthetic" / "v0_poc.py").is_file(),
        "museum_imported": bool(offenders),
    }


def _git_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _write_fixture_files(root: Path) -> dict[str, Path]:
    """Materialize the synthetic frame/specs for the path-oriented pipeline."""
    root.mkdir(parents=True, exist_ok=True)
    roles = roles_for_menu()
    network = network_for("oracle_easy")
    beta = beta_corr_y()
    frame = make_dgp("oracle_easy", BATTERY_N, 0)
    scores_path = root / "scores.csv"
    roles_path = root / "roles.json"
    network_path = root / "network.yaml"
    beta_path = root / "beta.yaml"
    frame.to_csv(scores_path, index=False)
    roles_path.write_text(json.dumps(roles.model_dump(mode="json"), indent=2) + "\n")
    network_path.write_text(yaml.safe_dump(network.model_dump(mode="json"), sort_keys=False))
    beta_path.write_text(yaml.safe_dump(beta.model_dump(mode="json"), sort_keys=False))
    return {
        "scores": scores_path,
        "roles": roles_path,
        "network": network_path,
        "beta": beta_path,
    }


def _run_kwargs(paths: dict[str, Path], out_dir: Path) -> dict[str, Any]:
    return {
        "scores": paths["scores"],
        "roles": paths["roles"],
        "network": paths["network"],
        "beta": paths["beta"],
        "out_dir": out_dir,
        "policy": "none",
        "seed": INFERENCE_SEED,
        "write_parquet": False,
    }


def _same_headline(row: Any, headline: Any) -> bool:
    return (
        tuple(row.admissible) == tuple(headline.admissible)
        and row.empty == headline.empty
        and row.range_L == headline.range_L
        and row.range_U == headline.range_U
    )


def _json_safe(value: Any) -> Any:
    """Convert dataclass payloads' non-finite floats to strict JSON nulls."""
    if isinstance(value, dict):
        return {str(k): _json_safe(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_safe(v) for v in value]
    if isinstance(value, tuple):
        return [_json_safe(v) for v in value]
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        return None
    return value


def main() -> None:
    museum_check = _museum_import_check()
    assert museum_check["passed"], museum_check
    assert museum_check["museum_file_present"]

    battery = run_battery(
        scenarios=SCENARIOS,
        seeds=DEFAULT_SEEDS,
        n=BATTERY_N,
        check_cold=True,
    )
    assert battery.passed, battery.gate_notes

    fixture_root = RUN_ROOT / "fixture"
    paths = _write_fixture_files(fixture_root)
    default = run_profile(**_run_kwargs(paths, RUN_ROOT / "default"), n_boot=0)
    boot_a = run_profile(
        **_run_kwargs(paths, RUN_ROOT / "bootstrap_a"), n_boot=N_BOOT
    )
    boot_b = run_profile(
        **_run_kwargs(paths, RUN_ROOT / "bootstrap_b"), n_boot=N_BOOT
    )
    grid_a = run_profile(
        **_run_kwargs(paths, RUN_ROOT / "grid_a"),
        theta_grid_lambdas=GRID,
    )
    grid_same = run_profile(
        **_run_kwargs(paths, RUN_ROOT / "grid_same"),
        theta_grid_lambdas=GRID,
    )
    grid_alt = run_profile(
        **_run_kwargs(paths, RUN_ROOT / "grid_alt"),
        theta_grid_lambdas=ALT_GRID,
    )

    harsh_paths = dict(paths)
    harsh_paths["network"] = fixture_root / "network_harsh.yaml"
    harsh_network = network_for("harsh_theta")
    harsh_paths["network"].write_text(
        yaml.safe_dump(harsh_network.model_dump(mode="json"), sort_keys=False)
    )
    harsh = run_profile(
        **_run_kwargs(harsh_paths, RUN_ROOT / "harsh"),
        n_boot=40,
        theta_grid_lambdas=[1.0, 2.0],
    )

    assert default.run_manifest.freeze.n_boot is None
    assert boot_a.run_manifest.freeze.n_boot == N_BOOT
    assert default.run_id != boot_a.run_id
    assert boot_a.identify.range_L == default.identify.range_L
    assert boot_a.identify.range_U == default.identify.range_U
    assert boot_a.bootstrap is not None and boot_b.bootstrap is not None
    boot_a_payload = bootstrap_payload(boot_a.bootstrap)
    boot_b_payload = bootstrap_payload(boot_b.bootstrap)
    assert boot_a_payload == boot_b_payload

    assert grid_a.theta_grid is not None
    assert grid_same.theta_grid is not None
    assert grid_alt.theta_grid is not None
    assert grid_a.run_id == default.run_id == grid_same.run_id == grid_alt.run_id
    assert theta_grid_payload(grid_a.theta_grid) == theta_grid_payload(grid_same.theta_grid)
    assert theta_grid_payload(grid_a.theta_grid) != theta_grid_payload(grid_alt.theta_grid)
    row_one = grid_a.theta_grid.row_for(1.0)
    assert row_one is not None
    assert _same_headline(row_one, default.identify)

    assert harsh.identify.empty
    assert harsh.identify.range_L is None and harsh.identify.range_U is None
    assert harsh.bootstrap is not None and harsh.theta_grid is not None
    if harsh.bootstrap.replicates_nonempty == 0:
        assert harsh.bootstrap.band_L is None and harsh.bootstrap.band_U is None
        assert harsh.bootstrap.note is not None
    else:
        assert harsh.bootstrap.band_L is not None and harsh.bootstrap.band_U is not None

    summary = {
        "schema_version": "1",
        "generated_by": "tools/v11_synth_summary.py",
        "package_version": __version__,
        "git_sha": _git_sha(),
        "battery_version": battery.battery_version,
        "battery": battery.to_dict(),
        "battery_settings": {
            "scenarios": list(SCENARIOS),
            "seeds": list(DEFAULT_SEEDS),
            "n": BATTERY_N,
            "check_cold": True,
            "score_policy": "none",
            "delta": 0.0,
            "network": "eval-only oracle R; harsh variant for empty contrast",
            "beta": "corr_y",
        },
        "inference_settings": {
            "oracle_scenario": "oracle_easy",
            "seed": INFERENCE_SEED,
            "n_boot": N_BOOT,
            "bootstrap_quantiles": [0.025, 0.975],
            "theta_grid": GRID,
            "alternate_theta_grid": ALT_GRID,
            "headline_rule": "full-sample min/max B*; diagnostics additive",
        },
        "inference": {
            "default": {
                "run_id": default.run_id,
                "n_boot_in_freeze": default.run_manifest.freeze.n_boot,
                "M_star": default.identify.admissible,
                "L": default.identify.range_L,
                "U": default.identify.range_U,
            },
            "bootstrap": {
                "run_id": boot_a.run_id,
                "same_seed_payload_equal": True,
                "run_id_changes_when_enabled": boot_a.run_id != default.run_id,
                "headline_unchanged": (
                    boot_a.identify.range_L == default.identify.range_L
                    and boot_a.identify.range_U == default.identify.range_U
                ),
                "payload": boot_a_payload,
            },
            "theta_grid": {
                "run_id_same_as_default": grid_a.run_id == default.run_id,
                "same_grid_deterministic": True,
                "alternate_grid_changes_payload": True,
                "lambda_1_equals_headline": True,
                "payload": theta_grid_payload(grid_a.theta_grid),
                "alternate_payload": theta_grid_payload(grid_alt.theta_grid),
            },
            "harsh_empty": {
                "run_id": harsh.run_id,
                "headline_empty": harsh.identify.empty,
                "headline_L": harsh.identify.range_L,
                "headline_U": harsh.identify.range_U,
                "bootstrap": bootstrap_payload(harsh.bootstrap),
                "theta_grid": theta_grid_payload(harsh.theta_grid),
            },
        },
        "museum_import_check": museum_check,
        "artifact_paths": {
            "summary": str(SUMMARY_PATH.relative_to(REPO_ROOT)),
            "oracle_default_run": str((RUN_ROOT / "default").relative_to(REPO_ROOT)),
            "oracle_bootstrap_run": str((RUN_ROOT / "bootstrap_a").relative_to(REPO_ROOT)),
            "oracle_grid_run": str((RUN_ROOT / "grid_a").relative_to(REPO_ROOT)),
            "harsh_run": str((RUN_ROOT / "harsh").relative_to(REPO_ROOT)),
        },
        "scope_note": (
            "Package-native synthetic evidence only; oracle networks are eval-only. "
            "Bootstrap and theta-grid are diagnostic layers, not sharp PI claims. "
            "The spam audit remains intermediate and not H5."
        ),
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(_json_safe(summary), indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "summary": str(SUMMARY_PATH),
        "package_version": __version__,
        "git_sha": summary["git_sha"],
        "battery_passed": battery.passed,
        "default_run_id": default.run_id,
        "bootstrap_run_id": boot_a.run_id,
        "grid_run_id": grid_a.run_id,
        "harsh_empty": harsh.identify.empty,
        "harsh_bootstrap_nonempty": harsh.bootstrap.replicates_nonempty,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
