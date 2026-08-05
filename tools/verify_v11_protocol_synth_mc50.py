"""Independently validate the tracked provisional synthetic-only MC50 proof.

This tool audits the committed JSON artifact only. It neither reruns the package
battery nor writes run artifacts.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections.abc import Mapping
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SUMMARY_PATH = (
    REPO_ROOT / "reports" / "summaries" / "v1_1_protocol_synth_mc50_summary.json"
)
EXPECTED_PROTOCOL_ID = "protocol-v1-synth-provisional-mc50"
EXPECTED_SCENARIOS = ["oracle_easy", "oracle_with_slop", "harsh_theta", "all_invalid"]
EXPECTED_SEEDS = list(range(50))
EXPECTED_GATES = {
    "H1a_anchor_oracle_easy",
    "H1a_anchor_oracle_with_slop",
    "H1a_fa_all_invalid",
    "H1a_fa_harsh_theta",
    "H1a_fa_oracle_easy",
    "H1a_fa_oracle_with_slop",
    "H1b_oracle_easy",
    "H1b_oracle_with_slop",
    "H3_all_invalid",
    "H3_harsh_theta",
    "H4_cold",
}
SHA40 = re.compile(r"^[0-9a-f]{40}$")


def _as_mapping(value: object, label: str, errors: list[str]) -> Mapping[str, object]:
    if isinstance(value, Mapping):
        return value
    errors.append(f"{label} must be an object")
    return {}


def _as_list(value: object, label: str, errors: list[str]) -> list[object]:
    if isinstance(value, list):
        return value
    errors.append(f"{label} must be a list")
    return []


def _number(value: object, label: str, errors: list[str]) -> float | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        errors.append(f"{label} must be numeric")
        return None
    return float(value)


def _close(actual: object, expected: float, label: str, errors: list[str]) -> None:
    observed = _number(actual, label, errors)
    if observed is not None and not math.isclose(observed, expected, rel_tol=0.0, abs_tol=1e-12):
        errors.append(f"{label}={actual!r}, expected {expected!r}")


def _reject_nonfinite(value: object, path: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            _reject_nonfinite(item, f"{path}.{key}", errors)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_nonfinite(item, f"{path}[{index}]", errors)
    elif isinstance(value, float) and not math.isfinite(value):
        errors.append(f"{path} is non-finite")


def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _validate_identity(summary: Mapping[str, object], errors: list[str]) -> None:
    expected = {
        "schema_version": "1",
        "protocol_id": EXPECTED_PROTOCOL_ID,
        "generated_by": "tools/v11_protocol_synth_mc50.py",
        "package_version": "1.1.0a1",
        "protocol_document": "docs/16_Paper_Protocol_Freeze.md",
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            errors.append(f"{key}={summary.get(key)!r}, expected {value!r}")
    git_sha = summary.get("git_sha")
    if not isinstance(git_sha, str) or SHA40.fullmatch(git_sha) is None:
        errors.append("git_sha must be a lowercase 40-character commit SHA")
    paths = _as_mapping(summary.get("artifact_paths"), "artifact_paths", errors)
    for key, value in {
        "summary": "reports/summaries/v1_1_protocol_synth_mc50_summary.json",
        "run_root": "reports/runs/v1_1_protocol_synth_mc50",
    }.items():
        if paths.get(key) != value:
            errors.append(f"artifact_paths.{key}={paths.get(key)!r}, expected {value!r}")


def _validate_settings(summary: Mapping[str, object], errors: list[str]) -> None:
    settings = _as_mapping(summary.get("settings"), "settings", errors)
    expected = {
        "scenarios": EXPECTED_SCENARIOS,
        "seeds": EXPECTED_SEEDS,
        "n": 1000,
        "score_policy": "none",
        "delta": 0.0,
        "beta": "corr_y",
        "check_cold": True,
    }
    for key, value in expected.items():
        if settings.get(key) != value:
            errors.append(f"settings.{key}={settings.get(key)!r}, expected {value!r}")
    scope_note = summary.get("scope_note")
    if (
        not isinstance(scope_note, str)
        or "synthetic-only" not in scope_note
        or "not H5" not in scope_note
    ):
        errors.append("scope_note must retain synthetic-only and not-H5 boundaries")


def _validate_rows(
    scenario: str,
    aggregate: Mapping[str, object],
    errors: list[str],
) -> None:
    rows = _as_list(aggregate.get("per_seed"), f"{scenario}.per_seed", errors)
    if aggregate.get("n_seeds") != len(EXPECTED_SEEDS):
        errors.append(f"{scenario}.n_seeds={aggregate.get('n_seeds')!r}, expected 50")
    if len(rows) != len(EXPECTED_SEEDS):
        errors.append(f"{scenario}.per_seed has {len(rows)} rows, expected 50")

    seeds: list[int] = []
    fa_values: list[float] = []
    anchor_values: list[float] = []
    h1b_values: list[float] = []
    latent_values: list[float] = []
    empty_values: list[float] = []
    cold_values: list[float] = []
    abs_m_values: list[float] = []
    widths: list[float] = []
    invalid_ever: set[str] = set()
    near_ever: set[str] = set()

    for index, raw_row in enumerate(rows):
        row = _as_mapping(raw_row, f"{scenario}.per_seed[{index}]", errors)
        seed = row.get("seed")
        if not isinstance(seed, int) or isinstance(seed, bool):
            errors.append(f"{scenario}.per_seed[{index}].seed must be an integer")
        else:
            seeds.append(seed)
        if row.get("scenario") != scenario:
            errors.append(f"{scenario}.per_seed[{index}].scenario does not match aggregate")
        if row.get("n") != 1000:
            errors.append(f"{scenario}.per_seed[{index}].n must be 1000")

        empty = row.get("empty")
        m_star = _as_list(row.get("M_star"), f"{scenario}.per_seed[{index}].M_star", errors)
        lo, hi = row.get("L"), row.get("U")
        if empty is True:
            if m_star or lo is not None or hi is not None:
                errors.append(
                    f"{scenario}.per_seed[{index}] empty row must have empty M_star and null L/U"
                )
        elif empty is False:
            lo_number = _number(lo, f"{scenario}.per_seed[{index}].L", errors)
            hi_number = _number(hi, f"{scenario}.per_seed[{index}].U", errors)
            if lo_number is not None and hi_number is not None and lo_number > hi_number:
                errors.append(f"{scenario}.per_seed[{index}] has L > U")
            if lo_number is not None and hi_number is not None:
                widths.append(hi_number - lo_number)
        else:
            errors.append(f"{scenario}.per_seed[{index}].empty must be boolean")

        fa = _number(row.get("fa_rate"), f"{scenario}.per_seed[{index}].fa_rate", errors)
        if fa is not None:
            fa_values.append(fa)
        anchor = row.get("anchor_in_M")
        if isinstance(anchor, bool):
            anchor_values.append(1.0 if anchor else 0.0)
        else:
            errors.append(f"{scenario}.per_seed[{index}].anchor_in_M must be boolean")
        if isinstance(row.get("h1b"), bool):
            h1b_values.append(1.0 if row["h1b"] else 0.0)
        if isinstance(row.get("h1_latent"), bool):
            latent_values.append(1.0 if row["h1_latent"] else 0.0)
        if isinstance(empty, bool):
            empty_values.append(1.0 if empty else 0.0)
        if isinstance(row.get("cold_match"), bool):
            cold_values.append(1.0 if row["cold_match"] else 0.0)
        abs_m_values.append(float(len(m_star)))
        invalids = _as_list(
            row.get("false_admissions"),
            f"{scenario}.per_seed[{index}].false_admissions",
            errors,
        )
        near_misses = _as_list(
            row.get("near_miss_admitted"),
            f"{scenario}.per_seed[{index}].near_miss_admitted",
            errors,
        )
        invalid_ever.update(str(item) for item in invalids)
        near_ever.update(str(item) for item in near_misses)

    if seeds != EXPECTED_SEEDS:
        errors.append(f"{scenario}.per_seed seeds must be unique, sorted, and equal settings.seeds")
    for key, values in {
        "fa_rate": fa_values,
        "anchor_rate": anchor_values,
        "empty_rate": empty_values,
        "cold_match_rate": cold_values,
        "mean_abs_M": abs_m_values,
    }.items():
        expected = _mean(values)
        if expected is not None:
            _close(aggregate.get(key), expected, f"{scenario}.{key}", errors)
    optional_aggregates = {
        "h1b_rate": h1b_values,
        "h1_latent_rate": latent_values,
        "mean_width": widths,
    }
    for key, values in optional_aggregates.items():
        expected = _mean(values)
        if expected is None:
            if aggregate.get(key) is not None:
                errors.append(f"{scenario}.{key} must be null when undefined")
        else:
            _close(aggregate.get(key), expected, f"{scenario}.{key}", errors)
    if aggregate.get("invalid_ever_admitted") != sorted(invalid_ever):
        errors.append(f"{scenario}.invalid_ever_admitted disagrees with per_seed rows")
    if aggregate.get("near_miss_ever_admitted") != sorted(near_ever):
        errors.append(f"{scenario}.near_miss_ever_admitted disagrees with per_seed rows")


def _validate_battery(summary: Mapping[str, object], errors: list[str]) -> None:
    battery = _as_mapping(summary.get("battery"), "battery", errors)
    if battery.get("package_version") != "1.1.0a1":
        errors.append("battery.package_version must match the locked package version")
    if battery.get("seeds") != EXPECTED_SEEDS:
        errors.append("battery.seeds must match settings.seeds")
    if battery.get("n") != 1000 or battery.get("delta") != 0.0 or battery.get("beta") != "corr_y":
        errors.append("battery settings disagree with the locked protocol")
    scenarios = _as_mapping(battery.get("scenarios"), "battery.scenarios", errors)
    if set(scenarios) != set(EXPECTED_SCENARIOS):
        errors.append("battery.scenarios must contain exactly the locked scenario set")
    for scenario in EXPECTED_SCENARIOS:
        _validate_rows(scenario, _as_mapping(scenarios.get(scenario), scenario, errors), errors)

    gates = _as_mapping(summary.get("gates"), "gates", errors)
    battery_gates = _as_mapping(battery.get("gates"), "battery.gates", errors)
    if gates != battery_gates:
        errors.append("gates and battery.gates must agree exactly")
    if set(gates) != EXPECTED_GATES:
        errors.append("gates must contain exactly the declared H1a/H1b/H3/H4 keys")
    if not all(value is True for value in gates.values()):
        errors.append("all declared gates must be true for this locked proof")
    passed = all(value is True for value in gates.values())
    if summary.get("battery_passed") is not passed:
        errors.append("battery_passed must equal the conjunction of declared gates")
    if battery.get("passed") is not passed:
        errors.append("battery.passed must equal the conjunction of declared gates")


def _validate_bootstrap(bootstrap: Mapping[str, object], label: str, errors: list[str]) -> None:
    if bootstrap.get("n_boot") != 80 or bootstrap.get("seed") != 7:
        errors.append(f"{label} bootstrap must use locked n_boot=80 and seed=7")
    counts: list[int] = []
    for key in ("replicates_nonempty", "replicates_empty", "replicates_degenerate"):
        value = bootstrap.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            errors.append(f"{label}.{key} must be a nonnegative integer")
        else:
            counts.append(value)
    if len(counts) == 3 and sum(counts) != bootstrap.get("replicates_total"):
        errors.append(f"{label} replicate counts must sum to replicates_total")
    if bootstrap.get("replicates_total") != 80:
        errors.append(f"{label}.replicates_total must equal n_boot")
    if counts and counts[0] == 0 and (
        bootstrap.get("band_L") is not None or bootstrap.get("band_U") is not None
    ):
        errors.append(f"{label} all-empty bootstrap must have null bootstrap band")


def _validate_inference(summary: Mapping[str, object], errors: list[str]) -> None:
    inference = _as_mapping(summary.get("inference"), "inference", errors)
    settings = _as_mapping(inference.get("settings"), "inference.settings", errors)
    expected = {"fixture_dgp_seed": 0, "seed": 7, "n_boot": 80, "theta_grid": [0.5, 1.0, 2.0]}
    for key, value in expected.items():
        if settings.get(key) != value:
            errors.append(f"inference.settings.{key}={settings.get(key)!r}, expected {value!r}")
    for key in ("oracle", "harsh_empty"):
        probe = _as_mapping(inference.get(key), f"inference.{key}", errors)
        if probe.get("lambda_1_equals_headline") is not True:
            errors.append(f"inference.{key}.lambda_1_equals_headline must be true")
        bootstrap_label = f"inference.{key}.bootstrap"
        bootstrap = _as_mapping(probe.get("bootstrap"), bootstrap_label, errors)
        _validate_bootstrap(bootstrap, bootstrap_label, errors)
    harsh = _as_mapping(inference.get("harsh_empty"), "inference.harsh_empty", errors)
    if (
        harsh.get("headline_empty") is not True
        or harsh.get("headline_L") is not None
        or harsh.get("headline_U") is not None
    ):
        errors.append("inference.harsh_empty must preserve the empty headline contrast")


def _validate_museum(summary: Mapping[str, object], errors: list[str]) -> None:
    museum = _as_mapping(summary.get("museum_import_check"), "museum_import_check", errors)
    if (
        museum.get("passed") is not True
        or museum.get("museum_file_present") is not True
        or museum.get("museum_imported") is not False
    ):
        errors.append("museum import check must pass with museum present and unimported")


def validate_summary(summary: Mapping[str, object]) -> list[str]:
    """Return all structural/provenance errors found in an MC50 proof payload."""
    errors: list[str] = []
    _reject_nonfinite(summary, "summary", errors)
    _validate_identity(summary, errors)
    _validate_settings(summary, errors)
    _validate_battery(summary, errors)
    _validate_inference(summary, errors)
    _validate_museum(summary, errors)
    return errors


def _reject_json_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is forbidden: {value}")


def load_summary(path: Path) -> dict[str, object]:
    """Load strict JSON without accepting JSON NaN/Infinity constants."""
    loaded: object = json.loads(path.read_text(), parse_constant=_reject_json_constant)
    if not isinstance(loaded, dict):
        raise ValueError("summary root must be a JSON object")
    return loaded


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--summary", type=Path, default=DEFAULT_SUMMARY_PATH)
    args = parser.parse_args()
    try:
        summary = load_summary(args.summary)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"MC50 audit input error: {exc}", file=sys.stderr)
        return 2
    errors = validate_summary(summary)
    if errors:
        print("MC50 audit failed:\n- " + "\n- ".join(errors), file=sys.stderr)
        return 1
    result = {
        "errors": [],
        "passed": True,
        "protocol_id": summary["protocol_id"],
        "scenario_seed_cells": 200,
    }
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
