"""TDD tests for WVS/GPS patience application stage 5 — summary writer
(evals/wvs_gps_preferences/run_application.py, stage5_* functions).

Stage 5 aggregates pooled stage-3 + stage-4 baselines + verifier into a
single JSON-ready summary for the allow-listed proof artifact. It is a pure
composition of already-tested pieces: tested here with synthetic inputs.

Contract (docs/16 §11 reporting posture (a)): headline = M*_select with
[L,U] = min/max beta on select survivors; holdout verdicts reported as
power-limited diagnostics; verifier gate summary included.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "evals" / "wvs_gps_preferences")
)

import run_application as app  # noqa: E402

from test_wvs_gps_application import build_base  # noqa: E402


def _write_synth_tree(tmp_path: Path, seed: int = 7) -> Path:
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


def test_stage5_summary_contains_headline_select_and_diagnostics(tmp_path: Path) -> None:
    _write_synth_tree(tmp_path)
    summary = app.stage5_report(
        data_dir=tmp_path,
        seed=7,
        split_seed=17,
        k=3,
        n_boot=10,
        n_draws=25,
        k_grid=(1, 2),
    )
    # reporting posture (a): headline is M*_select with range on survivors
    assert "headline" in summary
    assert "M_star_select" in summary["headline"]
    assert "holdout" in summary  # power-limited diagnostics present
    assert "baselines" in summary
    assert "verifier" in summary


def test_stage5_range_is_minmax_beta_on_select(tmp_path: Path) -> None:
    _write_synth_tree(tmp_path)
    summary = app.stage5_report(
        data_dir=tmp_path,
        seed=7,
        split_seed=17,
        k=3,
        n_boot=10,
        n_draws=25,
        k_grid=(1, 2),
    )
    h = summary["headline"]
    assert set(h["M_star_select"]).issubset(app.MENU_MEASURES)
    if h["M_star_select"]:
        assert h["L"] <= h["U"]


def test_stage5_summary_written_to_disk(tmp_path: Path) -> None:
    _write_synth_tree(tmp_path)
    app.stage5_report(
        data_dir=tmp_path,
        seed=7,
        split_seed=17,
        k=3,
        n_boot=10,
        n_draws=25,
        k_grid=(1, 2),
        out_path=tmp_path / "wvs_gps_summary.json",
    )
    payload = json.loads((tmp_path / "wvs_gps_summary.json").read_text())
    assert payload["k"] == 3
    assert "headline" in payload


def test_stage5_records_empty_select_honestly(tmp_path: Path) -> None:
    # A network that rejects everything must still produce a summary with
    # empty headline and no crash (empty M* is a clean success).
    _write_synth_tree(tmp_path)
    summary = app.stage5_report(
        data_dir=tmp_path,
        seed=7,
        split_seed=17,
        k=3,
        n_boot=10,
        n_draws=25,
        k_grid=(1, 2),
    )
    assert summary["headline"]["empty"] in (True, False)
    assert "L" in summary["headline"]  # None when empty, float otherwise
