"""Independent, read-only audit tests for the provisional synthetic-only MC50 proof."""

from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from types import ModuleType

REPO_ROOT = Path(__file__).resolve().parents[1]
SUMMARY_PATH = REPO_ROOT / "reports" / "summaries" / "v1_1_protocol_synth_mc50_summary.json"
TOOL_PATH = REPO_ROOT / "tools" / "verify_v11_protocol_synth_mc50.py"


def _load_tool() -> ModuleType:
    spec = importlib.util.spec_from_file_location("verify_v11_protocol_synth_mc50", TOOL_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_summary() -> dict[str, object]:
    return json.loads(SUMMARY_PATH.read_text())


def test_tracked_mc50_summary_passes_independent_audit() -> None:
    tool = _load_tool()

    assert tool.validate_summary(_load_summary()) == []


def test_audit_rejects_tampered_protocol_id() -> None:
    tool = _load_tool()
    summary = _load_summary()
    summary["protocol_id"] = "protocol-v1-not-the-locked-artifact"

    assert "protocol_id" in "\n".join(tool.validate_summary(summary))


def test_audit_rejects_battery_passed_mismatch() -> None:
    tool = _load_tool()
    summary = _load_summary()
    summary["battery_passed"] = False

    assert "battery_passed" in "\n".join(tool.validate_summary(summary))


def test_audit_rejects_duplicate_seed_and_missing_per_seed_row() -> None:
    tool = _load_tool()
    summary = _load_summary()
    settings = summary["settings"]
    assert isinstance(settings, dict)
    settings["seeds"] = [*range(49), 48]
    battery = summary["battery"]
    assert isinstance(battery, dict)
    scenarios = battery["scenarios"]
    assert isinstance(scenarios, dict)
    oracle = scenarios["oracle_easy"]
    assert isinstance(oracle, dict)
    rows = oracle["per_seed"]
    assert isinstance(rows, list)
    rows.pop()

    errors = "\n".join(tool.validate_summary(summary))

    assert "settings.seeds" in errors
    assert "oracle_easy.per_seed" in errors


def test_audit_recomputes_aggregate_from_per_seed_rows() -> None:
    tool = _load_tool()
    summary = _load_summary()
    battery = summary["battery"]
    assert isinstance(battery, dict)
    scenarios = battery["scenarios"]
    assert isinstance(scenarios, dict)
    oracle = scenarios["oracle_easy"]
    assert isinstance(oracle, dict)
    oracle["mean_abs_M"] = 99.0

    assert "oracle_easy.mean_abs_M" in "\n".join(tool.validate_summary(summary))


def test_audit_rejects_nonfinite_and_invalid_inference_counts() -> None:
    tool = _load_tool()
    summary = _load_summary()
    summary["git_sha"] = float("nan")
    inference = summary["inference"]
    assert isinstance(inference, dict)
    harsh = inference["harsh_empty"]
    assert isinstance(harsh, dict)
    bootstrap = harsh["bootstrap"]
    assert isinstance(bootstrap, dict)
    bootstrap["replicates_empty"] = 79
    bootstrap["band_L"] = 0.1

    errors = "\n".join(tool.validate_summary(summary))

    assert "non-finite" in errors
    assert "replicate counts" in errors
    assert "null bootstrap band" in errors


def test_cli_reports_machine_readable_success() -> None:
    result = subprocess.run(
        [sys.executable, str(TOOL_PATH)],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout)
    assert payload == {
        "errors": [],
        "passed": True,
        "protocol_id": "protocol-v1-synth-provisional-mc50",
        "scenario_seed_cells": 200,
    }


def test_strict_loader_rejects_json_nan_constant(tmp_path: Path) -> None:
    tool = _load_tool()
    path = tmp_path / "nonfinite.json"
    path.write_text('{"bad": NaN}\n')

    try:
        tool.load_summary(path)
    except ValueError as exc:
        assert "non-finite JSON constant" in str(exc)
    else:
        raise AssertionError("expected strict loader to reject JSON NaN")


def test_audit_does_not_mutate_summary() -> None:
    tool = _load_tool()
    summary = _load_summary()
    before = copy.deepcopy(summary)

    assert tool.validate_summary(summary) == []
    assert summary == before
