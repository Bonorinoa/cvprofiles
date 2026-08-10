"""TDD tests for WVS/GPS patience application pooled K-fold holdout
(evals/wvs_gps_preferences/run_application.py, kfold_* / pooled_* functions).

Motivation (docs/12 2026-08-10 checkpoint; docs/16 §11 amendment): the single
80/20 split produced an uninformative n=8 hold frame — pure noise passed every
hold-frame bar, and GPS patience (positive control) failed convergent bars on
8 all-developing countries. The researcher's discretion: the test, not the
construct, was underpowered; redesign to pooled K-fold so every country is
held out exactly once and each measure gets K holdout evaluations.

Semantics:
  make_kfold_splits(units, k, seed) -> list of k holdout lists; each unit in
      exactly one list; each list >= 2 units (engine contract).
  pooled_stage3(...) -> runs the engine once per fold (holdout = that fold),
      pools: selected_in_all_folds  = m in M*_select^(f) for every f
             compliant_in_all_folds = m's holdout verdict empty in every f
             pooled_robust          = both.
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


# --- k-fold split -----------------------------------------------------------


def test_kfold_splits_each_unit_held_out_exactly_once() -> None:
    units = [f"C{i:02d}" for i in range(41)]
    folds = app.make_kfold_splits(units, k=5, split_seed=17)
    assert len(folds) == 5
    seen: list[str] = []
    for f in folds:
        assert len(f) >= 2, "each fold needs >=2 holdout units (engine contract)"
        assert f == sorted(set(f))
        seen.extend(f)
    assert sorted(seen) == sorted(units)  # every unit exactly once


def test_kfold_splits_deterministic_and_seed_sensitive() -> None:
    units = [f"C{i:02d}" for i in range(41)]
    a = app.make_kfold_splits(units, k=5, split_seed=17)
    b = app.make_kfold_splits(units, k=5, split_seed=17)
    assert a == b
    c = app.make_kfold_splits(units, k=5, split_seed=99)
    assert a != c


def test_kfold_splits_rejects_bad_k() -> None:
    with pytest.raises(ValueError, match="k"):
        app.make_kfold_splits([f"C{i:02d}" for i in range(5)], k=1, split_seed=1)
    with pytest.raises(ValueError, match="k"):
        app.make_kfold_splits([f"C{i:02d}" for i in range(5)], k=10, split_seed=1)


# --- pooled stage 3 ----------------------------------------------------------


def test_pooled_stage3_runs_and_pools(tmp_path: Path) -> None:
    _write_synth_inputs(tmp_path)
    summary = app.pooled_stage3(
        data_dir=tmp_path,
        out_dir=tmp_path / "pool_runs",
        seed=7,
        split_seed=17,
        k=3,
        n_boot=10,
    )
    assert summary["k"] == 3
    assert summary["n_folds"] == 3
    assert len(summary["folds"]) == 3
    # pooled robust is a subset of the menu
    assert set(summary["pooled_robust"]).issubset(app.MENU_MEASURES)
    # per-fold select sets recorded and are subsets of the menu
    assert len(summary["per_fold_select"]) == 3
    for sel in summary["per_fold_select"]:
        assert set(sel).issubset(app.MENU_MEASURES)


def test_pooled_robust_requires_selection_in_every_fold() -> None:
    # A measure selected in 2/3 folds must NOT be pooled-robust unless it is
    # also selected in the third; exercise the pooling helper directly.
    per_fold_select = [
        ["m_gps_patience", "m_noise"],
        ["m_gps_patience"],
        ["m_gps_patience"],
    ]
    per_fold_compliant = [
        ["m_gps_patience", "m_noise"],
        ["m_gps_patience"],
        ["m_gps_patience"],
    ]
    selected, compliant, robust = app.pool_holdout_verdicts(
        per_fold_select, per_fold_compliant
    )
    assert "m_noise" not in selected  # missing from fold 1 selection
    assert robust == ["m_gps_patience"]


def test_pool_holdout_verdicts_compliance_required_every_fold() -> None:
    per_fold_select = [["m_gps_patience"], ["m_gps_patience"], ["m_gps_patience"]]
    per_fold_compliant = [
        ["m_gps_patience"],
        [],  # fails compliance in fold 1
        ["m_gps_patience"],
    ]
    selected, compliant, robust = app.pool_holdout_verdicts(
        per_fold_select, per_fold_compliant
    )
    assert "m_gps_patience" in selected
    assert "m_gps_patience" not in compliant
    assert robust == []


def test_pooled_stage3_writes_run_artifacts(tmp_path: Path) -> None:
    _write_synth_inputs(tmp_path)
    app.pooled_stage3(
        data_dir=tmp_path,
        out_dir=tmp_path / "pool_runs",
        seed=7,
        split_seed=17,
        k=3,
        n_boot=10,
    )
    # pooled summary JSON written next to the per-fold runs
    assert (tmp_path / "pool_runs" / "pooled_summary.json").exists()
    payload = json.loads((tmp_path / "pool_runs" / "pooled_summary.json").read_text())
    assert payload["k"] == 3
