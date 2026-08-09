"""P4b units-split holdout (docs/12 2026-08-08; gates H_holdout_units).

Contract under test:
- holdout_units: None or [] ⇒ no split (legacy, config={} bit-stable).
- Non-empty list ⇒ train = all other units, hold = listed units.
- M*_select  = select-stage admission on the TRAIN frame.
- M*_robust  = M*_select ∩ {m : all restrictions pass on the HOLD frame}.
- Headline admissible/empty/range = robust semantics; β image on the FULL
  pooled frame over M*_robust (decision §1).
- holdout_verdict in split mode = failing restriction ids (any stage) per
  measure on the hold frame (compliance); legacy mode = failing holdout-stage
  ids on the full frame (P4a behavior).
- Normalized sorted-unique list in freeze config; order cannot fork run_id.
- Split frames must each have >= 2 rows (every evaluator requires n >= 2).

Goldens are computed IN-TEST from the real mini fixture via an independent
numpy path — no hand-transcribed numbers.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cvprofiles.identify.pipeline import IdentifyError, run_identify
from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.score.pipeline import run_score

HOLDOUT = ["u01", "u02", "u03"]


@pytest.fixture
def mini_path() -> Path:
    return Path(__file__).resolve().parents[1] / "data" / "fixtures" / "mini_v1"


@pytest.fixture
def scored(mini_path, mini_roles, mini_scores_df):
    return run_score(mini_scores_df, mini_roles, policy="none")


def _corr(x: np.ndarray, y: np.ndarray) -> float:
    return float(np.corrcoef(x, y)[0, 1])


def _reference_split(
    frame: pd.DataFrame, holdout: list[str], measure: str, var: str
) -> tuple[float, float, float]:
    """Independent numpy reference: (train corr, hold corr, full-frame beta)."""
    ids = frame["unit_id"].astype(str)
    train = frame[~ids.isin(holdout)]
    hold = frame[ids.isin(holdout)]
    c_train = _corr(train[measure].to_numpy(dtype=float), train[var].to_numpy(dtype=float))
    c_hold = _corr(hold[measure].to_numpy(dtype=float), hold[var].to_numpy(dtype=float))
    b_full = _corr(frame[measure].to_numpy(dtype=float), frame["y"].to_numpy(dtype=float))
    return c_train, c_hold, b_full


def _discriminating_theta(frame: pd.DataFrame) -> float:
    """Midpoint of m_good / m_weak hold-frame corr — self-calibrating split bar."""
    _, c_good_hold, _ = _reference_split(frame, HOLDOUT, "m_good", "v_aux")
    _, c_weak_hold, _ = _reference_split(frame, HOLDOUT, "m_weak", "v_aux")
    return (c_good_hold + c_weak_hold) / 2.0


def _network(
    restrictions: list[dict],
    *,
    name: str = "split_v1",
    delta: float = 0.0,
) -> dict:
    return {
        "schema_version": "1",
        "name": name,
        "delta": delta,
        "restrictions": restrictions,
    }


def test_run_identify_split_robust_survivors(scored, mini_path) -> None:
    """Network A (mini oracle, both select): train and hold agree → robust = select."""
    raw = _network(
        [
            {"id": "r_corr_min_aux", "type": "corr_min", "theta": 0.35, "params": {"variable": "v_aux"}},
            {"id": "r_corr_sign_aux", "type": "corr_sign", "theta": 0.10, "params": {"variable": "v_aux", "sign": 1}},
        ]
    )
    bundle = run_restrict(scored.roles, raw, mini_path / "beta.yaml")
    res = run_identify(scored.frame, scored.roles, bundle, holdout_units=HOLDOUT)

    assert res.holdout_units_used == ["u01", "u02", "u03"]
    assert res.M_star_select == ["m_good", "m_weak"]
    assert res.M_star_robust == ["m_good", "m_weak"]
    assert res.admissible == ["m_good", "m_weak"]  # robust semantics headline
    assert not res.empty
    # split mode: verdict covers ALL measures on the hold frame (decision #6).
    # m_slop is non-compliant on hold (corr -0.966 < 0.35) even though it was
    # already select-rejected on train; m_good/m_weak are compliant.
    assert res.holdout_verdict == {"m_slop": ["r_corr_min_aux", "r_corr_sign_aux"]}

    # β image on the FULL pooled frame (decision §1)
    _, _, b_good = _reference_split(scored.frame, HOLDOUT, "m_good", "v_aux")
    _, _, b_weak = _reference_split(scored.frame, HOLDOUT, "m_weak", "v_aux")
    assert res.beta_values["m_good"] == pytest.approx(b_good, abs=1e-9)
    assert res.beta_values["m_weak"] == pytest.approx(b_weak, abs=1e-9)
    assert res.range_L == pytest.approx(min(b_good, b_weak), abs=1e-9)
    assert res.range_U == pytest.approx(max(b_good, b_weak), abs=1e-9)


def test_split_empty_robust_is_success(scored, mini_path) -> None:
    """Network B: holdout restriction impossible on hold frame → empty robust = success."""
    raw = _network(
        [
            {"id": "r_select_weak", "type": "corr_min", "theta": -1.0, "params": {"variable": "v_aux"}, "stage": "select"},
            {"id": "r_holdout_harsh", "type": "corr_min", "theta": 2.0, "params": {"variable": "v_aux"}, "stage": "holdout"},
        ]
    )
    bundle = run_restrict(scored.roles, raw, mini_path / "beta.yaml")
    res = run_identify(scored.frame, scored.roles, bundle, holdout_units=HOLDOUT)

    assert res.M_star_select == ["m_good", "m_weak", "m_slop"]  # theta=-1 admits all on train
    assert res.M_star_robust == []
    assert res.admissible == []
    assert res.empty is True
    assert res.range_L is None and res.range_U is None
    # every measure fails the harsh holdout restriction on the hold frame
    assert all("r_holdout_harsh" in v for v in res.holdout_verdict.values())


def test_split_discriminating_verdict(scored, mini_path) -> None:
    """Network C: m_weak passes train admission but FAILS the unseen-holdout check.

    The discriminating holdout theta is derived in-test (midpoint of hold-frame
    corr between m_good and m_weak) so the test stays self-calibrating if the
    fixture is ever regenerated — the falsifiability the holdout core exists
    to catch.
    """
    theta_hold = _discriminating_theta(scored.frame)
    raw = _network(
        [
            {"id": "r_select", "type": "corr_min", "theta": 0.35, "params": {"variable": "v_aux"}},
            {"id": "r_holdout", "type": "corr_min", "theta": theta_hold, "params": {"variable": "v_aux"}, "stage": "holdout"},
        ]
    )
    bundle = run_restrict(scored.roles, raw, mini_path / "beta.yaml")
    res = run_identify(scored.frame, scored.roles, bundle, holdout_units=HOLDOUT)

    assert res.M_star_select == ["m_good", "m_weak"]
    assert res.holdout_verdict["m_weak"] == ["r_holdout"]
    assert res.holdout_verdict["m_slop"] == ["r_select", "r_holdout"]
    assert "m_good" not in res.holdout_verdict
    assert res.M_star_robust == ["m_good"]
    assert res.admissible == ["m_good"]
    assert res.point_id is True
    _, _, b_good = _reference_split(scored.frame, HOLDOUT, "m_good", "v_aux")
    assert res.range_L == pytest.approx(b_good, abs=1e-9)
    assert res.range_U == pytest.approx(b_good, abs=1e-9)


def test_slacks_use_stage_frames(scored, mini_path) -> None:
    """Select-stage columns come from the train frame; holdout-stage from hold frame."""
    theta_hold = _discriminating_theta(scored.frame)
    raw = _network(
        [
            {"id": "r_select", "type": "corr_min", "theta": 0.35, "params": {"variable": "v_aux"}},
            {"id": "r_holdout", "type": "corr_min", "theta": theta_hold, "params": {"variable": "v_aux"}, "stage": "holdout"},
        ]
    )
    bundle = run_restrict(scored.roles, raw, mini_path / "beta.yaml")
    res = run_identify(scored.frame, scored.roles, bundle, holdout_units=HOLDOUT)

    assert set(res.slacks.columns) == {"r_select", "r_holdout"}
    for m in scored.roles.measures:
        c_train, c_hold, _ = _reference_split(scored.frame, HOLDOUT, m, "v_aux")
        assert res.slacks.at[m, "r_select"] == pytest.approx(c_train - 0.35, abs=1e-9)
        assert res.slacks.at[m, "r_holdout"] == pytest.approx(c_hold - theta_hold, abs=1e-9)


def test_holdout_units_order_run_id_invariant(mini_path, tmp_path) -> None:
    """List order must not fork run_id; split vs no-split must differ."""
    a = run_profile(
        scores=mini_path / "scores.csv",
        roles=mini_path / "roles.json",
        network=mini_path / "network.yaml",
        beta=mini_path / "beta.yaml",
        out_dir=tmp_path / "order_a",
        holdout_units=["u03", "u01", "u02"],
    )
    b = run_profile(
        scores=mini_path / "scores.csv",
        roles=mini_path / "roles.json",
        network=mini_path / "network.yaml",
        beta=mini_path / "beta.yaml",
        out_dir=tmp_path / "order_b",
        holdout_units=["u01", "u02", "u03"],
    )
    c = run_profile(
        scores=mini_path / "scores.csv",
        roles=mini_path / "roles.json",
        network=mini_path / "network.yaml",
        beta=mini_path / "beta.yaml",
        out_dir=tmp_path / "no_split",
    )
    assert a.run_id == b.run_id
    assert a.run_id != c.run_id
    assert a.run_manifest.freeze.config == {"holdout_units": ["u01", "u02", "u03"]}
    assert c.run_manifest.freeze.config == {}
    # legacy additivity (decision #9): M_star_select / M_star_robust always
    # present and equal to admissible in no-split runs
    summ_c = summary_dict(c)
    assert summ_c["M_star_select"] == summ_c["M_star"] == ["m_good", "m_weak"]
    assert summ_c["M_star_robust"] == summ_c["M_star"]


def test_holdout_units_validation(scored, mini_path) -> None:
    raw = _network(
        [
            {"id": "r_select", "type": "corr_min", "theta": 0.35, "params": {"variable": "v_aux"}},
            {"id": "r_holdout", "type": "corr_min", "theta": 0.9974, "params": {"variable": "v_aux"}, "stage": "holdout"},
        ]
    )
    bundle = run_restrict(scored.roles, raw, mini_path / "beta.yaml")

    # unknown unit id
    with pytest.raises(IdentifyError, match="not in|unknown|holdout"):
        run_identify(scored.frame, scored.roles, bundle, holdout_units=["u99"])
    # all units held out → empty train
    all_ids = [f"u{i:02d}" for i in range(1, 11)]
    with pytest.raises(IdentifyError, match="train"):
        run_identify(scored.frame, scored.roles, bundle, holdout_units=all_ids)
    # 1-row hold frame cannot evaluate any restriction (n >= 2 evaluators)
    with pytest.raises(IdentifyError, match="holdout|n >= 2|frame"):
        run_identify(scored.frame, scored.roles, bundle, holdout_units=["u01"])


def test_include_holdout_verdict_false(scored, mini_path) -> None:
    """Bootstrap path (lock §3): no per-replicate holdout verdicts."""
    raw = _network(
        [
            {"id": "r_select_weak", "type": "corr_min", "theta": -1.0, "params": {"variable": "v_aux"}, "stage": "select"},
            {"id": "r_holdout_harsh", "type": "corr_min", "theta": 2.0, "params": {"variable": "v_aux"}, "stage": "holdout"},
        ]
    )
    bundle = run_restrict(scored.roles, raw, mini_path / "beta.yaml")
    # legacy (no split): flag suppresses verdict computation entirely
    res = run_identify(scored.frame, scored.roles, bundle, include_holdout_verdict=False)
    assert res.holdout_verdict is None
    # default still computes it (P4a behavior)
    res2 = run_identify(scored.frame, scored.roles, bundle)
    assert res2.holdout_verdict is not None

    # bootstrap over units with a stage-split network: select-only admission,
    # no verdict per replicate, band over non-empty replicates.
    from cvprofiles.inference.bootstrap import run_bootstrap

    boot = run_bootstrap(scored.frame, scored.roles, bundle, n_boot=25, seed=7)
    assert boot.replicates_total == 25
    assert boot.replicates_degenerate == 0
    assert boot.band_L is not None and boot.band_U is not None


def test_run_profile_split_artifacts(mini_path, tmp_path) -> None:
    """Full composition: admissible.json + report.json carry robust semantics."""
    result = run_profile(
        scores=mini_path / "scores.csv",
        roles=mini_path / "roles.json",
        network=mini_path / "network.yaml",
        beta=mini_path / "beta.yaml",
        out_dir=tmp_path / "split_artifacts",
        holdout_units=HOLDOUT,
    )
    import json

    adm = result.out_dir / "admissible.json"
    payload = json.loads(adm.read_text())
    assert payload["M_star"] == ["m_good", "m_weak"]
    assert payload["M_star_select"] == ["m_good", "m_weak"]
    assert payload["M_star_robust"] == ["m_good", "m_weak"]
    assert payload["holdout"]["units"] == HOLDOUT

    report = json.loads((result.out_dir / "report.json").read_text())
    assert report["admissible"] == ["m_good", "m_weak"]
    assert report["M_star_robust"] == ["m_good", "m_weak"]

    summ = summary_dict(result)
    assert summ["M_star"] == ["m_good", "m_weak"]
    assert summ["M_star_robust"] == ["m_good", "m_weak"]
