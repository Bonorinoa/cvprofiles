"""TDD tests for the WVS/GPS patience application stage-1 builder
(evals/wvs_gps_preferences/run_application.py).

Fixture scope: synthetic GPS / WVS / WDI slices through the pure builder
functions — masking, floor, country means, universe merge with drop records,
composite C = F(phi), noise determinism, frozen-input writers (scores/roles/
network/beta) and the canonical hash. No network, no raw data, no llama.cpp.

Frozen specifications under test (docs/16 §11, D2–D10, 2026-08-10):
  menu_7      = [m_gps_patience, m_wvs_q13, m_wvs_q14, m_composite,
                 m_prompt_a, m_prompt_b, m_noise]
  network     = conv_edu corr_min(q275_mean) 0.20 (select)
                mono_edu monotone_rank(q275_mean,+1) 0.15 (holdout)
                disc_risk corr_zero(risktaking) 0.30 (select)
  beta        = ols_coef, outcome log_gdp_pc, controls [q275_mean]
  floor       = 30 valid responses per item for a country mean
  missing     = -1..-5 masked, never imputed
  outcome     = log_gdp_pc is beta-only, never in R
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

# --- fixtures -------------------------------------------------------------

N_COUNTRIES = 8


def make_gps(n: int = N_COUNTRIES, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    iso = [f"C{i:02d}" for i in range(n)]
    return pd.DataFrame(
        {
            "isocode": iso,
            "patience": rng.normal(size=n),
            "risktaking": rng.normal(size=n),
        }
    )


def make_wvs(n: int = N_COUNTRIES, seed: int = 1) -> pd.DataFrame:
    """One country below the floor; one with a missing code to mask."""
    rng = np.random.default_rng(seed)
    rows: list[dict] = []
    iso = [f"C{i:02d}" for i in range(n)]
    for i, c in enumerate(iso):
        reps = 10 if i == 0 else 40  # C00 below floor
        for _ in range(reps):
            q13 = rng.normal(loc=0.0, scale=1.0)
            q14 = rng.normal(loc=0.0, scale=1.0)
            q275 = rng.integers(1, 9)
            if i == 1 and _ == 0:  # inject one -5 missing code
                q13 = -5
            rows.append(
                {"B_COUNTRY_ALPHA": c, "Q13": q13, "Q14": q14, "Q275": q275}
            )
    return pd.DataFrame(rows)


def make_wdi(n: int = N_COUNTRIES, seed: int = 2) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    iso = [f"C{i:02d}" for i in range(n)]
    return pd.DataFrame({"iso3": iso, "log_gdp_pc": rng.normal(loc=9.0, scale=1.0, size=n)})


def build_base(seed: int = 7) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    gps = make_gps()
    wvs = make_wvs()
    wdi = make_wdi()
    merged, drops = app.merge_universe(gps, wvs, wdi, floor=app.RESPONDENT_FLOOR)
    return app.compose_scores(merged, seed=seed), drops


# --- masking / floor ------------------------------------------------------

def test_mask_missing_maps_codes_to_nan() -> None:
    s = pd.Series([1.0, -1, -2, 4, -5, 3])
    out = app.mask_missing(s)
    assert list(out.isna()) == [False, True, True, False, True, False]


def test_wvs_country_means_drops_below_floor_and_masks() -> None:
    wvs = make_wvs()
    means = app.wvs_country_means(wvs, items=["Q13", "Q14", "Q275"], floor=app.RESPONDENT_FLOOR)
    # C00 (10 reps) below floor -> excluded
    assert "C00" not in means["unit_id"].tolist()
    # C01 injected a -5 in Q13 -> Q13 mean computed over 39 non-missing
    c01 = means.set_index("unit_id").loc["C01"]
    assert not np.isnan(c01["Q13"])
    assert c01["Q13"] > -1  # not the masked code


# --- universe merge / drop records ----------------------------------------

def test_merge_universe_drops_missing_coverage_with_record() -> None:
    gps = make_gps(6)
    wvs = make_wvs(6)
    wdi = make_wdi(5)  # C05 missing -> dropped
    merged, drops = app.merge_universe(gps, wvs, wdi, floor=app.RESPONDENT_FLOOR)
    assert "C05" in drops.get("missing_wdi", [])
    assert set(merged["unit_id"]) == {f"C{i:02d}" for i in range(1, 5)}  # C00 floor, C05 wdi


def test_merge_universe_records_floor_drops() -> None:
    gps = make_gps(6)
    wvs = make_wvs(6)
    wdi = make_wdi(6)
    merged, drops = app.merge_universe(gps, wvs, wdi, floor=app.RESPONDENT_FLOOR)
    assert "C00" in drops.get("below_floor", [])


# --- composite / noise ------------------------------------------------------

def test_composite_is_zscore_sum_of_q13_q14() -> None:
    frame, _ = build_base()
    df = frame.set_index("unit_id")
    expected = (
        (df["m_wvs_q13"] - df["m_wvs_q13"].mean()) / df["m_wvs_q13"].std(ddof=0)
        + (df["m_wvs_q14"] - df["m_wvs_q14"].mean()) / df["m_wvs_q14"].std(ddof=0)
    )
    pd.testing.assert_series_equal(df["m_composite"], expected, check_names=False)


def test_noise_deterministic_given_seed_and_distinct_from_measures() -> None:
    f1, _ = build_base(seed=7)
    f2, _ = build_base(seed=7)
    pd.testing.assert_series_equal(f1["m_noise"], f2["m_noise"], check_names=False)
    # noise is seeded Gaussian, not a constant
    assert f1["m_noise"].std(ddof=0) > 1e-6


def test_build_base_frame_has_all_menu_columns() -> None:
    frame, _ = build_base()
    assert set(app.MENU_MEASURES).issubset(frame.columns)
    assert {"unit_id", "risktaking", "q275_mean", "log_gdp_pc"}.issubset(frame.columns)


# --- frozen inputs ----------------------------------------------------------

def test_frozen_network_matches_s11_spec(tmp_path: Path) -> None:
    out = app.write_frozen_inputs(
        out_dir=tmp_path, frame=build_base()[0], drops={}, seed=7, prompt_source="stub"
    )
    network = app.load_yaml(out["network.yaml"])
    by_id = {r["id"]: r for r in network["restrictions"]}
    assert by_id["conv_edu"] == {
        "id": "conv_edu",
        "type": "corr_min",
        "theta": 0.20,
        "params": {"variable": "q275_mean"},
        "stage": "select",
    }
    assert by_id["mono_edu"]["type"] == "monotone_rank"
    assert by_id["mono_edu"]["params"] == {"variable": "q275_mean", "sign": 1}
    assert by_id["mono_edu"]["stage"] == "holdout"
    assert by_id["disc_risk"] == {
        "id": "disc_risk",
        "type": "corr_zero",
        "theta": 0.35,  # re-anchored 2026-08-10 (literature: Falk et al. 2018 ρ=0.23-0.36 range)
        "params": {"variable": "risktaking"},
        "stage": "select",
    }
    # outcome never in R
    vars_in_r = {r["params"].get("variable") for r in network["restrictions"]}
    assert "log_gdp_pc" not in vars_in_r


def test_frozen_beta_matches_s11_spec(tmp_path: Path) -> None:
    out = app.write_frozen_inputs(
        out_dir=tmp_path, frame=build_base()[0], drops={}, seed=7, prompt_source="stub"
    )
    beta = app.load_yaml(out["beta.yaml"])
    assert beta["type"] == "ols_coef"
    assert beta["outcome"] == "log_gdp_pc"
    assert beta["params"]["controls"] == ["q275_mean"]


def test_roles_json_matches_menu(tmp_path: Path) -> None:
    app.write_frozen_inputs(
        out_dir=tmp_path, frame=build_base()[0], drops={}, seed=7, prompt_source="stub"
    )
    roles = json.loads((tmp_path / "roles.json").read_text())
    assert roles["unit_id"] == "unit_id"
    assert roles["measures"] == app.MENU_MEASURES
    assert roles["aux"] == ["risktaking", "q275_mean"]
    assert roles["outcome"] == "log_gdp_pc"


def test_scores_csv_hash_present_and_stable(tmp_path: Path) -> None:
    app.write_frozen_inputs(
        out_dir=tmp_path / "a", frame=build_base(seed=3)[0], drops={}, seed=3, prompt_source="stub"
    )
    app.write_frozen_inputs(
        out_dir=tmp_path / "b", frame=build_base(seed=3)[0], drops={}, seed=3, prompt_source="stub"
    )
    man1 = json.loads((tmp_path / "a" / "score_manifest.json").read_text())
    man2 = json.loads((tmp_path / "b" / "score_manifest.json").read_text())
    assert man1["scores_hash"] == man2["scores_hash"]
    assert man1["n_rows"] == len(build_base(seed=3)[0])


def test_prompt_columns_absent_without_prompt_source_raise(tmp_path: Path) -> None:
    # A frozen scores.csv must not silently carry stub prompts: writer refuses
    # unless prompt_source is explicit.
    with pytest.raises(ValueError, match="prompt"):
        app.write_frozen_inputs(
            out_dir=tmp_path, frame=build_base()[0], drops={}, seed=7, prompt_source=None
        )


def test_manifest_records_drop_reasons_and_prompt_source(tmp_path: Path) -> None:
    frame, drops = build_base()
    drops["missing_wdi"] = ["X99"]
    app.write_frozen_inputs(
        out_dir=tmp_path, frame=frame, drops=drops, seed=7, prompt_source="stub"
    )
    man = json.loads((tmp_path / "score_manifest.json").read_text())
    assert "X99" in man["universe"]["missing_wdi"]
    assert man["prompt_source"] == "stub"
    assert man["seed"] == 7
