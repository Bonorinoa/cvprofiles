"""TDD tests for WVS/GPS patience application stage 3 — engine wiring
(evals/wvs_gps_preferences/run_application.py, stage3_* functions).

Covered with synthetic fixtures (no real data, no network, no models):
  make_holdout_split  — fixed-seed random 80/20 country split, deterministic,
                        >=2 units per frame (engine contract)
  stage3_engine       — reads stage-1 inputs, runs run_profile with the split,
                        bootstrap + coverage, returns summary with headline
                        [L,U] on M*_robust

Frozen specs under test (docs/16 §11 D5-D7, 2026-08-10):
  beta       = ols_coef, outcome log_gdp_pc, controls [q275_mean]
  holdout    = fixed-seed random 80/20 country units-split
  coverage   = additive uncertainty band (alpha/kappa); headline unchanged
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "evals" / "wvs_gps_preferences")
)

import run_application as app  # noqa: E402

from test_wvs_gps_application import build_base  # noqa: E402

# --- holdout split ---------------------------------------------------------


def test_holdout_split_is_deterministic_given_seed() -> None:
    units = [f"C{i:02d}" for i in range(41)]
    s1 = app.make_holdout_split(units, split_seed=17)
    s2 = app.make_holdout_split(units, split_seed=17)
    assert s1 == s2
    assert len(s1) == len(s2)


def test_holdout_split_different_seed_gives_different_split() -> None:
    units = [f"C{i:02d}" for i in range(41)]
    s1 = app.make_holdout_split(units, split_seed=17)
    s2 = app.make_holdout_split(units, split_seed=99)
    assert s1 != s2


def test_holdout_split_is_about_20_percent_and_min_2_each() -> None:
    units = [f"C{i:02d}" for i in range(41)]
    hold = app.make_holdout_split(units, split_seed=17)
    train = [u for u in units if u not in hold]
    frac = len(hold) / len(units)
    assert 0.15 <= frac <= 0.25
    assert len(hold) >= 2
    assert len(train) >= 2


def test_holdout_split_sorted_unique() -> None:
    units = [f"C{i:02d}" for i in range(41)]
    hold = app.make_holdout_split(units, split_seed=17)
    assert hold == sorted(set(hold))


# --- stage-3 engine wiring (synthetic inputs dir) ---------------------------


def _write_synth_inputs(tmp_path: Path, seed: int = 7) -> Path:
    frame, drops = build_base(seed=seed)
    app.write_frozen_inputs(
        out_dir=tmp_path / "inputs",
        frame=frame,
        drops=drops,
        seed=seed,
        prompt_source={
            "kind": "llama.cpp",
            "model_a": {"file": "synth_a.gguf"},
            "model_b": {"file": "synth_b.gguf"},
        },
    )
    return tmp_path


def test_stage3_engine_writes_run_dir_and_summary(tmp_path: Path) -> None:
    data_dir = _write_synth_inputs(tmp_path)
    summary = app.stage3_engine(
        data_dir=data_dir,
        out_dir=tmp_path / "runs",
        seed=7,
        split_seed=17,
        n_boot=20,
        alpha=0.10,
        kappa=2.0,
    )
    assert summary["run_id"]
    assert summary["n_units"] == len(build_base()[0])
    assert set(summary["M_star_robust"]).issubset(app.MENU_MEASURES)
    # headline is min/max beta on robust survivors
    if summary["M_star_robust"]:
        assert summary["L"] <= summary["U"]
    # run dir exists with the four-state artifacts (run_profile writes
    # directly INTO out_dir when an explicit path is given)
    run_dir = tmp_path / "runs"
    for name in (
        "admissible.json",
        "range.json",
        "slacks.csv",
        "run_manifest.json",
        "report.json",
    ):
        assert (run_dir / name).exists(), name


def test_stage3_engine_rejects_bad_split_fraction() -> None:
    with pytest.raises(ValueError, match="fraction"):
        app.make_holdout_split([f"C{i:02d}" for i in range(10)], split_seed=1, fraction=0.9)


def test_stage3_engine_coverage_block_present_when_boot_on(tmp_path: Path) -> None:
    data_dir = _write_synth_inputs(tmp_path)
    app.stage3_engine(
        data_dir=data_dir,
        out_dir=tmp_path / "runs",
        seed=7,
        split_seed=17,
        n_boot=20,
        alpha=0.10,
        kappa=2.0,
    )
    run_dir = tmp_path / "runs"
    coverage = json.loads((run_dir / "coverage.json").read_text())
    assert 0.0 <= coverage["empty_replicate_rate"] <= 1.0
    assert coverage["alpha"] == 0.10
    assert coverage["kappa"] == 2.0
