"""TDD tests for WVS/GPS patience application stage 2 — prompting harness
(evals/wvs_gps_preferences/run_application.py, stage2_* functions).

The pure scoring math (logits -> option probabilities -> country score) is
tested here with synthetic logits — NO model, NO llama_cpp import, NO network.
The model-facing glue (load_llm / collect_item_logprobs) is opt-in and only
exercised by the real smoke / frozen run.

Frozen specs under test (docs/16 §11 D8, 2026-08-10):
  prompt arms  = m_prompt_a (Llama-3.1-8B), m_prompt_b (Phi-4-mini 3.8B)
  determinism  = temperature 0, fixed seed, pinned GGUF sha
  score        = per-item probability of the "patient" option, averaged over
                 items -> country score in [0,1]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "evals" / "wvs_gps_preferences")
)

import run_application as app  # noqa: E402

from test_wvs_gps_application import build_base  # noqa: E402

# --- option probabilities from synthetic logits -----------------------------


def test_option_probabilities_softmax_over_option_tokens() -> None:
    # vocab of 10 tokens; option labels map to token ids 2 ("a") and 5 ("b"),
    # plus a variant 7 ("A") that should merge into option A.
    logits = np.zeros(10, dtype=float)
    logits[2] = 2.0  # "a"
    logits[7] = 1.0  # "A" (variant)
    logits[5] = 0.0  # "b"
    options = {"A": [2, 7], "B": [5]}
    p = app.option_probabilities(logits, options)
    exp_a = np.exp(2.0) + np.exp(1.0)
    exp_b = np.exp(0.0)
    z = exp_a + exp_b
    assert p["A"] == pytest.approx(exp_a / z)
    assert p["B"] == pytest.approx(exp_b / z)
    assert abs(p["A"] + p["B"] - 1.0) < 1e-9


def test_option_probabilities_empty_option_raises() -> None:
    logits = np.zeros(5, dtype=float)
    with pytest.raises(ValueError, match="option"):
        app.option_probabilities(logits, {"A": []})


def test_option_probabilities_missing_token_id_ignored() -> None:
    logits = np.zeros(4, dtype=float)
    logits[0] = 3.0
    # token id 99 not in vocab: must be skipped, not crash
    p = app.option_probabilities(logits, {"A": [0], "B": [99]})
    assert p["B"] == pytest.approx(0.0)
    assert p["A"] == pytest.approx(1.0)


# --- country score aggregation -----------------------------------------------


def test_score_country_is_mean_of_patient_option_probability() -> None:
    item_probs = [
        {"A": 0.2, "B": 0.8},
        {"A": 0.4, "B": 0.6},
        {"A": 0.9, "B": 0.1},
    ]
    score = app.score_country(item_probs, patient_option="B")
    assert score == pytest.approx((0.8 + 0.6 + 0.1) / 3.0)
    assert 0.0 <= score <= 1.0


def test_score_country_requires_patient_option_present() -> None:
    with pytest.raises(ValueError, match="patient"):
        app.score_country([{"A": 1.0}], patient_option="B")


# --- prompt rendering ---------------------------------------------------------


def test_render_prompt_inserts_country() -> None:
    tmpl = "Consider a typical adult in {country}. Choose A or B."
    out = app.render_prompt(tmpl, "Argentina")
    assert "Argentina" in out
    assert "{country}" not in out


def test_item_prompts_have_stable_ids_and_country_slot() -> None:
    for item in app.PROMPT_ITEMS:
        assert item["id"].startswith("p")
        assert "{country}" in item["template"]
        assert set(item["options"]) == {"A", "B"}


# --- prompt column writer -----------------------------------------------------


def test_update_prompt_columns_replaces_stubs_and_rehashes(tmp_path: Path) -> None:
    frame, drops = build_base()
    app.write_frozen_inputs(
        out_dir=tmp_path, frame=frame, drops=drops, seed=7, prompt_source="stub"
    )
    old_hash = json.loads((tmp_path / "score_manifest.json").read_text())["scores_hash"]

    prompt_a = pd.Series(np.linspace(0.2, 0.9, len(frame)))
    prompt_b = pd.Series(np.linspace(0.1, 0.8, len(frame)))
    rec = app.update_prompt_columns(
        out_dir=tmp_path,
        prompt_a=dict(zip(frame["unit_id"], prompt_a, strict=True)),
        prompt_b=dict(zip(frame["unit_id"], prompt_b, strict=True)),
        prompt_source={
            "kind": "llama.cpp",
            "model": {"repo": "test/model", "file": "test.gguf", "sha256": "abc"},
        },
    )
    assert rec["prompt_source"]["kind"] == "llama.cpp"

    scores = pd.read_csv(tmp_path / "scores.csv")
    assert scores["m_prompt_a"].tolist() == pytest.approx(prompt_a.tolist())
    assert scores["m_prompt_b"].tolist() == pytest.approx(prompt_b.tolist())
    # stub values are gone
    assert not (scores["m_prompt_a"] == frame["m_prompt_a"]).all()

    man = json.loads((tmp_path / "score_manifest.json").read_text())
    assert man["scores_hash"] != old_hash  # real prompt columns changed the payload
    assert man["prompt_source"]["kind"] == "llama.cpp"


def test_update_prompt_columns_rejects_non_llama_source(tmp_path: Path) -> None:
    frame, drops = build_base()
    app.write_frozen_inputs(
        out_dir=tmp_path, frame=frame, drops=drops, seed=7, prompt_source="stub"
    )
    with pytest.raises(ValueError, match="llama.cpp"):
        app.update_prompt_columns(
            out_dir=tmp_path,
            prompt_a={},
            prompt_b={},
            prompt_source="stub",
        )


def test_update_prompt_columns_rejects_missing_country(tmp_path: Path) -> None:
    frame, drops = build_base()
    app.write_frozen_inputs(
        out_dir=tmp_path, frame=frame, drops=drops, seed=7, prompt_source="stub"
    )
    with pytest.raises(ValueError, match="missing"):
        app.update_prompt_columns(
            out_dir=tmp_path,
            prompt_a={},  # empty -> every country missing
            prompt_b={},
            prompt_source={"kind": "llama.cpp", "model": {"file": "x.gguf"}},
        )
