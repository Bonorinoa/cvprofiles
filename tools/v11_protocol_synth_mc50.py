"""Generate the provisional synthetic-only MC50 evidence summary.

This harness is deliberately thin: it calls the existing public package paths
``run_battery`` and ``run_profile``. It does not implement a second engine and
never imports the museum PoC.
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
from cvprofiles.synth.battery import SCENARIOS, run_battery
from cvprofiles.synth.dgp import make_dgp, roles_for_menu
from cvprofiles.synth.oracle_r import beta_corr_y, network_for

REPO_ROOT = Path(__file__).resolve().parents[1]
PROTOCOL_ID = "protocol-v1-synth-provisional-mc50"
SUMMARY_PATH = REPO_ROOT / "reports" / "summaries" / "v1_1_protocol_synth_mc50_summary.json"
RUN_ROOT = REPO_ROOT / "reports" / "runs" / "v1_1_protocol_synth_mc50"
SCENARIO_LIST = tuple(SCENARIOS)
SEEDS = tuple(range(50))
BATTERY_N = 1000
SCORE_POLICY = "none"
DELTA = 0.0
BETA = "corr_y"
INFERENCE_SEED = 7
N_BOOT = 80
THETA_GRID = [0.5, 1.0, 2.0]


def _museum_import_check() -> dict[str, Any]:
    """Run AST-level import hygiene over the installable package."""
    forbidden = ("openai", "anthropic", "httpx", "requests", "litellm")
    museum = ("v0_poc", "evals.synthetic")
    offenders: list[str] = []
    src = REPO_ROOT / "src" / "cvprofiles"
    for path in src.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue
            for module in modules:
                if any(module == name or module.startswith(name + ".") for name in forbidden):
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:{module}")
                if any(name in module for name in museum):
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
    """Materialize path-oriented public-pipeline inputs for inference probes."""
    root.mkdir(parents=True, exist_ok=True)
    roles = roles_for_menu()
    beta = beta_corr_y()
    paths = {
        "scores": root / "scores.csv",
        "roles": root / "roles.json",
        "network": root / "network.yaml",
        "beta": root / "beta.yaml",
    }
    make_dgp("oracle_easy", BATTERY_N, 0).to_csv(paths["scores"], index=False)
    paths["roles"].write_text(json.dumps(roles.model_dump(mode="json"), indent=2) + "\n")
    paths["beta"].write_text(yaml.safe_dump(beta.model_dump(mode="json"), sort_keys=False))
    paths["network"].write_text(
        yaml.safe_dump(network_for("oracle_easy").model_dump(mode="json"), sort_keys=False)
    )
    return paths


def _run_kwargs(paths: dict[str, Path], out_dir: Path) -> dict[str, Any]:
    return {
        "scores": paths["scores"],
        "roles": paths["roles"],
        "network": paths["network"],
        "beta": paths["beta"],
        "out_dir": out_dir,
        "policy": SCORE_POLICY,
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
    """Serialize non-finite floats as null so the proof JSON is strict."""
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, float) and (value != value or value in (float("inf"), float("-inf"))):
        return None
    return value


def _probe_inference() -> dict[str, Any]:
    fixture_root = RUN_ROOT / "fixture"
    paths = _write_fixture_files(fixture_root)
    oracle = run_profile(
        **_run_kwargs(paths, RUN_ROOT / "oracle_inference"),
        n_boot=N_BOOT,
        theta_grid_lambdas=THETA_GRID,
    )

    paths["network"].write_text(
        yaml.safe_dump(network_for("harsh_theta").model_dump(mode="json"), sort_keys=False)
    )
    harsh = run_profile(
        **_run_kwargs(paths, RUN_ROOT / "harsh_inference"),
        n_boot=N_BOOT,
        theta_grid_lambdas=THETA_GRID,
    )

    assert oracle.bootstrap is not None and oracle.theta_grid is not None
    assert harsh.bootstrap is not None and harsh.theta_grid is not None
    oracle_grid_row = oracle.theta_grid.row_for(1.0)
    harsh_grid_row = harsh.theta_grid.row_for(1.0)
    assert oracle_grid_row is not None and harsh_grid_row is not None
    assert _same_headline(oracle_grid_row, oracle.identify)
    assert _same_headline(harsh_grid_row, harsh.identify)
    assert harsh.identify.empty

    harsh_bootstrap = bootstrap_payload(harsh.bootstrap)
    if harsh.bootstrap.replicates_nonempty == 0:
        assert harsh.bootstrap.band_L is None and harsh.bootstrap.band_U is None
        assert harsh.bootstrap.note is not None

    return {
        "settings": {
            "scenario_oracle": "oracle_easy",
            "scenario_empty_contrast": "harsh_theta",
            "fixture_dgp_seed": 0,
            "seed": INFERENCE_SEED,
            "n_boot": N_BOOT,
            "theta_grid": THETA_GRID,
            "bootstrap_quantiles": [0.025, 0.975],
            "headline_rule": "full-sample min/max B*; diagnostics additive",
        },
        "oracle": {
            "run_id": oracle.run_id,
            "M_star": oracle.identify.admissible,
            "L": oracle.identify.range_L,
            "U": oracle.identify.range_U,
            "bootstrap": bootstrap_payload(oracle.bootstrap),
            "theta_grid": theta_grid_payload(oracle.theta_grid),
            "lambda_1_equals_headline": True,
        },
        "harsh_empty": {
            "run_id": harsh.run_id,
            "headline_empty": harsh.identify.empty,
            "headline_L": harsh.identify.range_L,
            "headline_U": harsh.identify.range_U,
            "bootstrap": harsh_bootstrap,
            "theta_grid": theta_grid_payload(harsh.theta_grid),
            "lambda_1_equals_headline": True,
        },
    }


def main() -> None:
    museum_check = _museum_import_check()
    assert museum_check["passed"], museum_check
    assert museum_check["museum_file_present"]

    battery = run_battery(
        scenarios=SCENARIO_LIST,
        seeds=SEEDS,
        n=BATTERY_N,
        check_cold=True,
    )
    # A failed gate is still an evidence result. Preserve the observed battery
    # and gate notes in the proof JSON; do not drop or relabel the run.
    inference = _probe_inference()

    summary = {
        "schema_version": "1",
        "protocol_id": PROTOCOL_ID,
        "generated_by": "tools/v11_protocol_synth_mc50.py",
        "package_version": __version__,
        "git_sha": _git_sha(),
        "protocol_document": "docs/16_Paper_Protocol_Freeze.md",
        "settings": {
            "scenarios": list(SCENARIO_LIST),
            "seeds": list(SEEDS),
            "n": BATTERY_N,
            "score_policy": SCORE_POLICY,
            "delta": DELTA,
            "beta": BETA,
            "check_cold": True,
            "network": "eval-only oracle R; harsh variant for empty contrast",
        },
        "battery": battery.to_dict(),
        "gates": battery.gates,
        "gate_notes": battery.gate_notes,
        "battery_passed": battery.passed,
        "inference": inference,
        "museum_import_check": museum_check,
        "artifact_paths": {
            "summary": str(SUMMARY_PATH.relative_to(REPO_ROOT)),
            "run_root": str(RUN_ROOT.relative_to(REPO_ROOT)),
        },
        "separate_package_evidence": "reports/summaries/v1_1_package_synth_summary.json",
        "scope_note": (
            "Provisional synthetic-only MC50 evidence; not H5, not an empirical result, "
            "and not a full paper protocol lock. Bootstrap and theta-grid are additive "
            "diagnostics, not sharp partial-identification claims."
        ),
    }
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.write_text(json.dumps(_json_safe(summary), indent=2, sort_keys=True) + "\n")
    print(
        json.dumps(
            {
                "summary": str(SUMMARY_PATH),
                "protocol_id": PROTOCOL_ID,
                "package_version": __version__,
                "git_sha": summary["git_sha"],
                "battery_passed": battery.passed,
                "seeds": len(SEEDS),
                "scenarios": list(SCENARIO_LIST),
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
