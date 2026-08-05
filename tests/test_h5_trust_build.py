"""TDD tests for the H5 Trust SCORE builder (evals/h5_trust/build_dataset.py).

Tests cover the pure builder logic with synthetic fixtures: missing-code
masking, 1-4 reversal, country aggregation, auxiliary averaging, canonical
hash stability, and fail-loud NaN enforcement. No network, no raw data.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evals" / "h5_trust"))

import build_dataset as h5  # noqa: E402

WVS_MISSING = {-1, -2, -3, -4, -5}


# --- masking -------------------------------------------------------------

def test_mask_missing_replaces_codes_with_nan() -> None:
    s = pd.Series([1, 2, -1, 4, -5, 3], dtype="Int64")
    out = h5.mask_missing(s, WVS_MISSING)
    assert list(out.isna()) == [False, False, True, False, True, False]
    assert list(out.dropna()) == [1, 2, 4, 3]


def test_mask_missing_accepts_ab_style_codes() -> None:
    s = pd.Series([1, 88, 98, 4, 7], dtype="Int64")
    out = h5.mask_missing(s, {88, 98})
    assert list(out.isna()) == [False, True, True, False, False]


# --- reversal ------------------------------------------------------------

def test_reverse_trust_1_4_maps_high_trust_to_one() -> None:
    x = pd.Series([1.0, 2.0, 3.0, 4.0, np.nan])
    out = h5.reverse_trust_1_4(x)
    assert np.allclose(out.dropna(), [1.0, 0.75, 0.5, 0.25])
    assert out.isna().iloc[-1]


# --- aggregation ---------------------------------------------------------

def _wvs_frame() -> pd.DataFrame:
    # 2 countries x 3 respondents; Q57 binary, Q58/Q60 1-4, with missing codes.
    return pd.DataFrame(
        {
            "country": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "q57": [1, 2, -1, 1, 1, 2],
            "q58": [1, 4, 2, 2, 3, 4],
            "q60": [1, 3, 2, 2, 4, 3],
            "q61": [1, 2, 3, 3, 4, 2],
            "q62": [2, 2, 3, 3, 3, 2],
            "q63": [1, 3, 4, 2, 3, 4],
            "q64": [1, 2, 2, 3, 4, 1],
            "q69": [2, 2, 3, 2, 3, 2],
            "q70": [1, 3, 4, 2, 2, 3],
            "q71": [2, 1, 3, 3, 3, 4],
        }
    )


def test_aggregate_wvs_country_means_and_counts() -> None:
    df = _wvs_frame()
    out = h5.aggregate_wvs_country(df, missing_codes=WVS_MISSING)
    assert set(out.index) == {"AAA", "BBB"}

    # AAA: q57 valid = [1, 2] (third is missing) -> share trust = 0.5
    assert out.loc["AAA", "m_trust_general"] == pytest.approx(0.5)
    # AAA: q57 valid count = 2
    assert out.loc["AAA", "n_trust_general"] == 2
    # BBB: q57 = [1, 1, 2] -> share = 2/3
    assert out.loc["BBB", "m_trust_general"] == pytest.approx(2 / 3)

    # AAA in_group = mean(reverse(q58), reverse(q60)) per respondent, then mean.
    # respondent1: rev(1)=1, rev(1)=1 -> 1.0 ; respondent2: rev(4)=0.25, rev(3)=0.5 -> 0.375
    # respondent3: rev(2)=0.75, rev(2)=0.75 -> 0.75 ; mean = (1 + .375 + .75)/3
    assert out.loc["AAA", "m_trust_in_group"] == pytest.approx((1 + 0.375 + 0.75) / 3)
    assert out.loc["AAA", "n_trust_in_group"] == 3

    # institution uses q64/q69/q70/q71 (all valid for AAA) -> 4 items x 3 respondents
    assert out.loc["AAA", "n_trust_institution"] == 3


def test_aggregate_wvs_country_requires_all_measures() -> None:
    df = _wvs_frame().drop(columns=["q69"])
    with pytest.raises(h5.BuildError, match="missing item column"):
        h5.aggregate_wvs_country(df, missing_codes=WVS_MISSING)


# --- aux averaging -------------------------------------------------------

def _aux_long() -> pd.DataFrame:
    rows = []
    for iso in ["AAA", "BBB"]:
        for year in [2015, 2016, 2017]:
            rows.append(
                {
                    "iso3": iso,
                    "year": year,
                    "gdp_pc_ppp": 100.0 if iso == "AAA" else 50.0,
                    "gini": 0.30 if iso == "AAA" else 0.45,
                    "agri_empl": 5.0 if iso == "AAA" else 40.0,
                }
            )
    return pd.DataFrame(rows)


def test_average_year_range_computes_log_gdp() -> None:
    aux = _aux_long()
    out = h5.average_year_range(aux, lo=2015, hi=2017)
    assert out.loc["AAA", "log_gdp_pc"] == pytest.approx(np.log(100.0))
    assert out.loc["BBB", "log_gdp_pc"] == pytest.approx(np.log(50.0))
    assert out.loc["AAA", "gini"] == pytest.approx(0.30)
    assert out.loc["BBB", "m_share_agriculture"] == pytest.approx(40.0)


def test_load_aux_local_reads_wdi_and_wgi(tmp_path: Path) -> None:
    wdi = _aux_long()
    wgi = pd.DataFrame(
        {
            "iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "year": [2015, 2016, 2017] * 2,
            "rule_of_law": [1.5] * 3 + [-0.8] * 3,
        }
    )
    wdi.to_csv(tmp_path / "wdi.csv", index=False)
    wgi.to_csv(tmp_path / "wgi.csv", index=False)
    out = h5.load_aux_local(tmp_path)
    assert out.loc["AAA", "rule_of_law"] == pytest.approx(1.5)
    assert out.loc["BBB", "rule_of_law"] == pytest.approx(-0.8)


def test_load_aux_local_missing_file_fails_loud(tmp_path: Path) -> None:
    with pytest.raises(h5.BuildError, match="aux cache"):
        h5.load_aux_local(tmp_path)


# --- canonical hash ------------------------------------------------------

def test_canonical_csv_hash_is_stable_and_sensitive() -> None:
    df = pd.DataFrame({"iso3": ["BBB", "AAA"], "v": [1.0, 2.0]})
    h1 = h5.canonical_csv_hash(df)
    h2 = h5.canonical_csv_hash(df.copy())
    assert h1 == h2 == hashlib.sha256(b"").hexdigest() or h1 == h2
    df2 = df.copy()
    df2.loc[0, "v"] = 1.5
    assert h5.canonical_csv_hash(df2) != h1


def test_parse_wgi_sheet_maps_legacy_codes() -> None:
    """Header=None WGI-style frame: year row + sub row + data rows."""
    filler = pd.DataFrame([[np.nan] * 8] * 12, dtype=float)
    header = pd.DataFrame(
        [
            [np.nan, np.nan, 2015, 2015, 2015, 2016, 2016, 2016],
            [
                "Country/Territory",
                "Code",
                "Estimate",
                "StdErr",
                "NumSrc",
                "Estimate",
                "StdErr",
                "NumSrc",
            ],
        ]
    )
    data = pd.DataFrame(
        [
            ["Andorra", "ADO", 1.5, 0.2, 3, 1.6, 0.2, 3],
            ["Romania", "ROM", 0.5, 0.1, 4, 0.6, 0.1, 4],
            ["Brazil", "BRA", -0.2, 0.1, 5, -0.1, 0.1, 5],
        ]
    )
    df = pd.concat([filler, header, data], ignore_index=True)
    out = h5.parse_wgi_sheet(df)
    iso_by_year = {iso: sorted(g["year"].tolist()) for iso, g in out.groupby("iso3")}
    assert "AND" in iso_by_year  # ADO -> AND
    assert "ROU" in iso_by_year  # ROM -> ROU
    assert "BRA" in iso_by_year
    assert out.loc[out["iso3"] == "AND", "rule_of_law"].iloc[0] == pytest.approx(1.5)


def test_parse_wgi_sheet_raises_without_header() -> None:
    with pytest.raises(h5.BuildError, match="Country/Territory"):
        h5.parse_wgi_sheet(pd.DataFrame({"a": [1, 2, 3]}))


# --- build orchestration (end-to-end on synthetic raw files) ------------

def _gps_frame() -> pd.DataFrame:
    return pd.DataFrame({"iso3": ["AAA", "BBB"], "trust": [0.4, -0.6]})


def test_build_end_to_end_writes_scores_and_manifest(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    aux_dir = tmp_path / "aux"
    out = tmp_path / "out"
    raw.mkdir()
    aux_dir.mkdir()

    _wvs_frame().to_csv(raw / "wvs.csv", index=False)
    _gps_frame().to_csv(raw / "gps.csv", index=False)
    _aux_long().to_csv(aux_dir / "wdi.csv", index=False)
    pd.DataFrame(
        {
            "iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "year": [2015, 2016, 2017] * 2,
            "rule_of_law": [1.5] * 3 + [-0.8] * 3,
        }
    ).to_csv(aux_dir / "wgi.csv", index=False)

    h5.build(raw_root=raw, aux_dir=aux_dir, out_dir=out, seed=20260804, floor=1)

    scores = pd.read_csv(out / "scores.csv")
    assert list(scores["iso3"]) == ["AAA", "BBB"]  # canonical sort
    for col in [
        "m_trust_general",
        "m_trust_in_group",
        "m_trust_out_group",
        "m_trust_institution",
        "m_noise",
        "m_share_agriculture",
        "gps_trust",
        "rule_of_law",
        "gini",
        "log_gdp_pc",
    ]:
        assert col in scores.columns
    assert not scores[["m_trust_general", "gps_trust", "log_gdp_pc"]].isna().any().any()

    manifest = json.loads((out / "score_manifest.json").read_text())
    assert manifest["n_countries"] == 2
    assert manifest["settings"]["seed"] == 20260804
    assert manifest["scores_hash"] == h5.canonical_csv_hash(scores)


def test_build_drops_countries_below_floor(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    aux_dir = tmp_path / "aux"
    out = tmp_path / "out"
    raw.mkdir()
    aux_dir.mkdir()

    _wvs_frame().to_csv(raw / "wvs.csv", index=False)
    _gps_frame().to_csv(raw / "gps.csv", index=False)
    _aux_long().to_csv(aux_dir / "wdi.csv", index=False)
    pd.DataFrame(
        {
            "iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "year": [2015, 2016, 2017] * 2,
            "rule_of_law": [1.5] * 3 + [-0.8] * 3,
        }
    ).to_csv(aux_dir / "wgi.csv", index=False)

    with pytest.raises(h5.BuildError, match="no countries"):
        h5.build(raw_root=raw, aux_dir=aux_dir, out_dir=out, seed=20260804, floor=4)


def test_build_drops_country_without_aux_coverage(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    aux_dir = tmp_path / "aux"
    out = tmp_path / "out"
    raw.mkdir()
    aux_dir.mkdir()

    _wvs_frame().to_csv(raw / "wvs.csv", index=False)
    _gps_frame().to_csv(raw / "gps.csv", index=False)
    # wdi covers only AAA -> BBB has no aux coverage -> excluded by universe rule
    wdi = _aux_long()
    wdi = wdi[wdi["iso3"] == "AAA"]
    wdi.to_csv(aux_dir / "wdi.csv", index=False)
    pd.DataFrame(
        {
            "iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "year": [2015, 2016, 2017] * 2,
            "rule_of_law": [1.5] * 3 + [-0.8] * 3,
        }
    ).to_csv(aux_dir / "wgi.csv", index=False)

    h5.build(raw_root=raw, aux_dir=aux_dir, out_dir=out, seed=20260804, floor=1)
    scores = pd.read_csv(out / "scores.csv")
    assert list(scores["iso3"]) == ["AAA"]
    manifest = json.loads((out / "score_manifest.json").read_text())
    assert manifest["universe"]["with_aux"] == 1


def test_build_drops_country_with_nan_aux(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    aux_dir = tmp_path / "aux"
    out = tmp_path / "out"
    raw.mkdir()
    aux_dir.mkdir()

    _wvs_frame().to_csv(raw / "wvs.csv", index=False)
    _gps_frame().to_csv(raw / "gps.csv", index=False)
    # BBB is present in aux but its GDP series is NaN within the window
    # -> no coverage, excluded per universe rule (never imputed), recorded.
    wdi = pd.DataFrame(
        {
            "iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "year": [2015, 2016, 2017] * 2,
            "gdp_pc_ppp": [100.0, 100.0, 100.0, np.nan, np.nan, np.nan],
            "gini": [0.30] * 3 + [0.45] * 3,
            "agri_empl": [5.0] * 3 + [40.0] * 3,
        }
    )
    wdi.to_csv(aux_dir / "wdi.csv", index=False)
    pd.DataFrame(
        {
            "iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "year": [2015, 2016, 2017] * 2,
            "rule_of_law": [1.5] * 3 + [-0.8] * 3,
        }
    ).to_csv(aux_dir / "wgi.csv", index=False)

    h5.build(raw_root=raw, aux_dir=aux_dir, out_dir=out, seed=20260804, floor=1)
    scores = pd.read_csv(out / "scores.csv")
    assert list(scores["iso3"]) == ["AAA"]
    manifest = json.loads((out / "score_manifest.json").read_text())
    assert manifest["universe"]["dropped_missing_coverage"] == ["BBB"]


def test_build_fails_loud_on_nan_measure(tmp_path: Path) -> None:
    raw = tmp_path / "raw"
    aux_dir = tmp_path / "aux"
    out = tmp_path / "out"
    raw.mkdir()
    aux_dir.mkdir()

    wvs = _wvs_frame()
    # All respondents missing q58/q60 -> in-group measure is NaN; with floor=0
    # the country survives the floor and the measure guard must fail loud.
    wvs["q58"] = -1
    wvs["q60"] = -1
    wvs.to_csv(raw / "wvs.csv", index=False)
    _gps_frame().to_csv(raw / "gps.csv", index=False)
    _aux_long().to_csv(aux_dir / "wdi.csv", index=False)
    pd.DataFrame(
        {
            "iso3": ["AAA", "AAA", "AAA", "BBB", "BBB", "BBB"],
            "year": [2015, 2016, 2017] * 2,
            "rule_of_law": [1.5] * 3 + [-0.8] * 3,
        }
    ).to_csv(aux_dir / "wgi.csv", index=False)

    with pytest.raises(h5.BuildError, match="NaN in measure columns"):
        h5.build(raw_root=raw, aux_dir=aux_dir, out_dir=out, seed=20260804, floor=0)
