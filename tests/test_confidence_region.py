"""Conservative Bonferroni confidence region for [L0, U0] — contract tests.

Locked semantics (logs/DECISIONS.md 2026-10-20; spec reports/specs/conservative_cr_spec.md):
- Per-pair one-sided slack bounds (Fisher-z for Pearson types with robust or
  classical SE; Bonett–Wright Fisher-z for Spearman types; Welch for mean_order).
- Outer set M+ (UCB >= -delta at a_out) and inner set M- (LCB >= -delta at a_in);
  statuses certainly_admissible / possibly_admissible / certainly_rejected.
- Levels: endpoint K_out = min(2, J) * Q, beta per side alpha2 / 2 (default);
  simultaneous K_out = J * Q, beta per side alpha2 / (2J); K_in = J always.
- CR = [min_{M+} lo, max_{M+} hi]; M+ empty ⇒ null CR + empty_outer (exit 0).
- Deterministic nesting: M- ⊆ M* ⊆ M+ and [L, U] ⊆ CR (Proposition 4).
- Select-stage restrictions only; ols_coef / map_distance fail loud (D8).
"""

from __future__ import annotations

import json
import math
from dataclasses import replace
from statistics import NormalDist

import numpy as np
import pandas as pd
import pytest
from scipy.special import stdtrit

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.identify.slacks import evaluate_slack, spearman_corr
from cvprofiles.inference.confidence_region import (
    ConfidenceRegionError,
    compute_confidence_region,
    confidence_region_payload,
    cr_levels,
    fisher_bounds,
    pearson_se_z,
    slack_bound,
    spearman_se_z,
    welch_stats,
)
from cvprofiles.restrict.pipeline import RestrictBundle, run_restrict
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import RestrictionSpec
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.synth.dgp import make_dgp, roles_for_menu
from cvprofiles.synth.oracle_r import beta_corr_y, network_for

ND = NormalDist()
STATUSES = {"certainly_admissible", "possibly_admissible", "certainly_rejected"}


def q(p: float) -> float:
    return ND.inv_cdf(p)


@pytest.fixture(scope="module")
def mini_bundle(mini_roles, mini_network, mini_beta) -> RestrictBundle:
    return run_restrict(mini_roles, mini_network, mini_beta)


@pytest.fixture(scope="module")
def synth_frame() -> pd.DataFrame:
    return make_dgp("oracle_with_slop", n=300, seed=11)


# --- primitives --------------------------------------------------------------------


def test_fisher_bounds_hand_computed() -> None:
    lo, hi = fisher_bounds(0.5, 0.2, 0.025)
    z = math.atanh(0.5)
    assert lo == pytest.approx(math.tanh(z - q(0.975) * 0.2), abs=1e-15)
    assert hi == pytest.approx(math.tanh(z + q(0.975) * 0.2), abs=1e-15)
    assert fisher_bounds(1.0, 0.0, 0.01) == (1.0, 1.0)  # degenerate |r| = 1


def test_pearson_se_classical_and_robust() -> None:
    rng = np.random.default_rng(3)
    x = rng.normal(size=40)
    y = 0.5 * x + rng.normal(size=40)
    r = float(np.corrcoef(x, y)[0, 1])
    assert pearson_se_z(x, y, r, "classical") == pytest.approx(1 / math.sqrt(37))
    zx = (x - x.mean()) / x.std()
    zy = (y - y.mean()) / y.std()
    psi = zx * zy - 0.5 * r * (zx**2 + zy**2)
    expected = math.sqrt(float(np.mean(psi**2))) / (1 - r * r) / math.sqrt(37)
    assert pearson_se_z(x, y, r, "robust") == pytest.approx(expected, rel=1e-12)


def test_spearman_se_bonett_wright() -> None:
    assert spearman_se_z(0.4, 50) == pytest.approx(math.sqrt((1 + 0.08) / 47))


def test_welch_stats_hand_computed() -> None:
    m = np.asarray([1.0, 2.0, 3.0, 4.0, 5.0, 6.0])
    g = np.asarray([0.0, 0.0, 0.0, 1.0, 1.0, 1.0])
    diff, se, nu = welch_stats(m, g)
    assert diff == 3.0
    assert se == pytest.approx(math.sqrt(2 / 3))
    assert nu == pytest.approx(4.0)


def test_cr_levels_bookkeeping() -> None:
    e = cr_levels(3, 2, 0.05, 0.05, "endpoint")
    assert (e.k_out, e.k_in) == (4, 3)
    assert e.a_out == pytest.approx(0.0125)
    assert e.a_in == pytest.approx(0.05 / 3)
    assert e.beta_per_side == pytest.approx(0.025)
    s = cr_levels(3, 2, 0.05, 0.05, "simultaneous")
    assert s.k_out == 6 and s.a_out == pytest.approx(0.05 / 6)
    assert s.beta_per_side == pytest.approx(0.05 / 6)
    one = cr_levels(1, 2, 0.05, 0.05, "endpoint")
    assert one.k_out == 2 and one.a_out == pytest.approx(0.025)
    none = cr_levels(4, 0, 0.05, 0.05, "endpoint")
    assert none.k_out == 0 and none.a_out is None


# --- per-evaluator slack bounds ------------------------------------------------------


def _check_bound(frame: pd.DataFrame, measure: str, r: RestrictionSpec, **kw):
    b = slack_bound(frame, measure, r, **kw)
    assert b.slack_hat == evaluate_slack(frame[measure].to_numpy(dtype=float), frame, r)
    assert b.lcb <= b.slack_hat <= b.ucb
    return b


def test_corr_min_bound_formula(synth_frame) -> None:
    r = RestrictionSpec(id="r", type="corr_min", theta=0.35, params={"variable": "v_aux"})
    b = _check_bound(synth_frame, "m_near", r, a_out=0.01, a_in=0.02, se_method="classical")
    se = 1 / math.sqrt(len(synth_frame) - 3)
    assert b.se == pytest.approx(se)
    assert b.ucb == pytest.approx(fisher_bounds(b.statistic, se, 0.01)[1] - 0.35)
    assert b.lcb == pytest.approx(fisher_bounds(b.statistic, se, 0.02)[0] - 0.35)


def test_corr_sign_negative_mirrors_positive(synth_frame) -> None:
    neg = RestrictionSpec(
        id="r", type="corr_sign", theta=0.1, params={"variable": "v_aux", "sign": -1}
    )
    pos = RestrictionSpec(
        id="r", type="corr_sign", theta=0.1, params={"variable": "v_aux", "sign": 1}
    )
    flipped = synth_frame.assign(m_dict=-synth_frame["m_dict"])
    for method in ("classical", "robust"):
        a = _check_bound(synth_frame, "m_dict", neg, a_out=0.01, a_in=0.02, se_method=method)
        b = _check_bound(flipped, "m_dict", pos, a_out=0.01, a_in=0.02, se_method=method)
        assert a.ucb == pytest.approx(b.ucb, abs=1e-12)
        assert a.lcb == pytest.approx(b.lcb, abs=1e-12)


def test_corr_zero_straddle_and_non_straddle(synth_frame) -> None:
    straddle = RestrictionSpec(id="r", type="corr_zero", theta=0.3, params={"variable": "U"})
    b = _check_bound(synth_frame, "m_dict", straddle, a_out=0.01, a_in=0.02, se_method="classical")
    lo, hi = fisher_bounds(b.statistic, b.se, 0.005)  # two-sided at a_out / 2 per side
    assert lo <= 0.0 <= hi
    assert b.ucb == pytest.approx(0.3)
    lo_i, hi_i = fisher_bounds(b.statistic, b.se, 0.02)
    assert b.lcb == pytest.approx(0.3 - max(abs(lo_i), abs(hi_i)))

    far = RestrictionSpec(id="r", type="corr_zero", theta=0.3, params={"variable": "v_aux"})
    c = _check_bound(synth_frame, "m_dict", far, a_out=0.01, a_in=0.02, se_method="classical")
    lo, hi = fisher_bounds(c.statistic, c.se, 0.005)
    assert lo > 0.0
    assert c.ucb == pytest.approx(0.3 - min(abs(lo), abs(hi)))


@pytest.mark.parametrize("sign", [1, -1])
def test_mean_order_welch_bound(synth_frame, sign: int) -> None:
    r = RestrictionSpec(id="r", type="mean_order", theta=0.2, params={"group": "g", "sign": sign})
    b = _check_bound(synth_frame, "m_dict", r, a_out=0.01, a_in=0.02, se_method="robust")
    m = synth_frame["m_dict"].to_numpy(dtype=float)
    diff, se, nu = welch_stats(m, synth_frame["g"].to_numpy(dtype=float))
    assert b.se == pytest.approx(se)
    assert b.ucb == pytest.approx(sign * diff + float(stdtrit(nu, 0.99)) * se - 0.2)
    assert b.lcb == pytest.approx(sign * diff - float(stdtrit(nu, 0.98)) * se - 0.2)


def test_rank_types_use_bonett_wright(synth_frame) -> None:
    mono = RestrictionSpec(
        id="r", type="monotone_rank", theta=0.2, params={"variable": "v_aux", "sign": 1}
    )
    b = _check_bound(synth_frame, "m_dict", mono, a_out=0.01, a_in=0.02, se_method="robust")
    rho = spearman_corr(
        synth_frame["m_dict"].to_numpy(dtype=float), synth_frame["v_aux"].to_numpy(dtype=float)
    )
    assert b.se == pytest.approx(spearman_se_z(rho, len(synth_frame)))
    assert b.ucb == pytest.approx(fisher_bounds(rho, b.se, 0.01)[1] - 0.2)


def test_rank_agree_with_itself_is_degenerate(synth_frame) -> None:
    r = RestrictionSpec(id="r", type="rank_agree", theta=0.5, params={"ref_measure": "m_dict"})
    b = _check_bound(synth_frame, "m_dict", r, a_out=0.01, a_in=0.02, se_method="robust")
    assert b.se == 0.0
    assert b.ucb == b.lcb == b.slack_hat == pytest.approx(0.5)


# --- region: nesting, variants, empties -----------------------------------------------


def _assert_nesting(frame, roles, bundle, cr) -> None:
    ident = run_identify(frame, roles, bundle)
    assert set(cr.M_minus) <= set(ident.admissible) <= set(cr.M_plus)
    if not ident.empty:
        assert cr.cr_L is not None and cr.cr_U is not None
        assert cr.cr_L <= ident.range_L and ident.range_U <= cr.cr_U
    for m in roles.measures:
        expected = (
            "certainly_admissible"
            if m in cr.M_minus
            else "possibly_admissible"
            if m in cr.M_plus
            else "certainly_rejected"
        )
        assert cr.status[m] == expected


def test_nesting_on_mini_fixture(mini_scores_df, mini_roles, mini_bundle) -> None:
    for variant in ("endpoint", "simultaneous"):
        for method in ("robust", "classical"):
            cr = compute_confidence_region(
                mini_scores_df, mini_roles, mini_bundle, variant=variant, se_method=method
            )
            _assert_nesting(mini_scores_df, mini_roles, mini_bundle, cr)
            assert len(cr.slack_bounds) == len(mini_roles.measures) * 2


@pytest.mark.parametrize("scenario", ["oracle_easy", "oracle_with_slop", "all_invalid"])
def test_nesting_on_synthetic_scenarios(scenario: str) -> None:
    frame = make_dgp(scenario, n=300, seed=4)
    roles = roles_for_menu()
    bundle = run_restrict(roles, network_for(scenario), beta_corr_y())
    cr = compute_confidence_region(frame, roles, bundle)
    _assert_nesting(frame, roles, bundle, cr)


def test_endpoint_region_inside_simultaneous(synth_frame) -> None:
    roles = roles_for_menu()
    bundle = run_restrict(roles, network_for("oracle_with_slop"), beta_corr_y())
    e = compute_confidence_region(synth_frame, roles, bundle, variant="endpoint")
    s = compute_confidence_region(synth_frame, roles, bundle, variant="simultaneous")
    assert set(e.M_plus) <= set(s.M_plus)
    assert s.cr_L <= e.cr_L <= e.cr_U <= s.cr_U
    assert e.levels.k_out == 2 * 2 and s.levels.k_out == len(roles.measures) * 2


def test_empty_outer_set_is_null_region() -> None:
    frame = make_dgp("harsh_theta", n=1000, seed=0)
    roles = roles_for_menu()
    bundle = run_restrict(roles, network_for("harsh_theta"), beta_corr_y())
    cr = compute_confidence_region(frame, roles, bundle)
    assert cr.M_plus == [] and cr.M_minus == []
    assert cr.empty_outer is True
    assert cr.cr_L is None and cr.cr_U is None
    assert set(cr.status.values()) == {"certainly_rejected"}


def test_empty_r_region_is_union_of_beta_intervals(mini_scores_df, mini_roles, mini_beta) -> None:
    bundle = run_restrict(
        mini_roles, {"schema_version": "1", "empty_R": True, "restrictions": []}, mini_beta
    )
    cr = compute_confidence_region(mini_scores_df, mini_roles, bundle)
    assert cr.M_plus == cr.M_minus == list(mini_roles.measures)
    assert cr.levels.a_out is None and cr.slack_bounds == ()
    assert cr.cr_L == min(b.lo for b in cr.beta_intervals)
    assert cr.cr_U == max(b.hi for b in cr.beta_intervals)


def test_holdout_stage_restrictions_never_enter_region(
    mini_scores_df, mini_roles, mini_beta
) -> None:
    network = {
        "schema_version": "1",
        "restrictions": [
            {"id": "sel", "type": "corr_min", "theta": 0.35, "params": {"variable": "v_aux"}},
            {
                "id": "hold",
                "type": "corr_sign",
                "theta": 0.9,
                "params": {"variable": "v_aux", "sign": 1},
                "stage": "holdout",
            },
        ],
    }
    bundle = run_restrict(mini_roles, network, mini_beta)
    cr = compute_confidence_region(mini_scores_df, mini_roles, bundle)
    assert cr.n_select_restrictions == 1
    assert {b.restriction for b in cr.slack_bounds} == {"sel"}


# --- beta intervals ------------------------------------------------------------------


def test_corr_y_interval_uses_fisher_z(mini_scores_df, mini_roles, mini_bundle) -> None:
    cr = compute_confidence_region(mini_scores_df, mini_roles, mini_bundle, se_method="classical")
    se = 1 / math.sqrt(len(mini_scores_df) - 3)
    for bi in cr.beta_intervals:
        lo, hi = fisher_bounds(bi.beta_hat, se, 0.025)
        assert (bi.lo, bi.hi) == (pytest.approx(lo), pytest.approx(hi))
        assert bi.source == "engine"


def test_diff_means_interval_uses_welch(synth_frame) -> None:
    roles = roles_for_menu()
    beta = BetaSpec(type="diff_means", outcome="y", params={"group": "g", "sign": -1})
    bundle = run_restrict(roles, network_for("oracle_easy"), beta)
    cr = compute_confidence_region(synth_frame, roles, bundle)
    m = synth_frame["m_dict"].to_numpy(dtype=float)
    diff, se, nu = welch_stats(m, synth_frame["g"].to_numpy(dtype=float))
    bi = next(b for b in cr.beta_intervals if b.measure == "m_dict")
    t = float(stdtrit(nu, 0.975))
    assert bi.beta_hat == pytest.approx(-diff)
    assert (bi.lo, bi.hi) == (pytest.approx(-diff - t * se), pytest.approx(-diff + t * se))


def test_external_interval_normal_t_and_cluster_df(
    mini_scores_df, mini_roles, mini_network, tmp_path
) -> None:
    path = tmp_path / "est.csv"
    path.write_text(
        "measure,beta_hat,se,df,n_clusters\n"
        "m_good,0.41,0.10,,\n"
        "m_weak,0.22,0.12,12.5,\n"
        "m_slop,0.90,0.05,,41\n"
    )
    ext = {"schema_version": "1", "type": "external", "outcome": "y_fe", "params": {}}
    bundle = run_restrict(mini_roles, mini_network, ext, beta_estimates=path)
    cr = compute_confidence_region(mini_scores_df, mini_roles, bundle)
    by = {b.measure: b for b in cr.beta_intervals}
    assert by["m_good"].lo == pytest.approx(0.41 - q(0.975) * 0.10)
    assert by["m_weak"].hi == pytest.approx(0.22 + float(stdtrit(12.5, 0.975)) * 0.12)
    assert by["m_slop"].df == 40.0
    assert by["m_slop"].lo == pytest.approx(0.90 - float(stdtrit(40.0, 0.975)) * 0.05)
    assert {b.source for b in cr.beta_intervals} == {"external"}
    assert cr.beta_estimates_hash == bundle.beta_estimates.estimates_hash


# --- fail loud --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "beta",
    [
        BetaSpec(type="ols_coef", outcome="y", params={"controls": ["v_aux"]}),
        BetaSpec(
            type="map_distance",
            outcome="y",
            params={"items": ["a"], "loadings": [[1.0, 0.0]], "target": [0.0, 0.0]},
        ),
    ],
)
def test_unsupported_beta_types_fail_loud(mini_scores_df, mini_roles, mini_bundle, beta) -> None:
    bundle = replace(mini_bundle, beta=beta)
    with pytest.raises(ConfidenceRegionError, match="external"):
        compute_confidence_region(mini_scores_df, mini_roles, bundle)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"alpha1": 0.0},
        {"alpha1": 1.0},
        {"alpha2": -0.1},
        {"alpha1": float("nan")},
        {"alpha1": 0.6, "alpha2": 0.5},
        {"variant": "bonferroni"},
        {"se_method": "hc3"},
    ],
)
def test_bad_options_fail_loud(mini_scores_df, mini_roles, mini_bundle, kwargs) -> None:
    with pytest.raises(ConfidenceRegionError):
        compute_confidence_region(mini_scores_df, mini_roles, mini_bundle, **kwargs)


def test_too_few_units_fail_loud(mini_scores_df, mini_roles, mini_bundle) -> None:
    with pytest.raises(ConfidenceRegionError, match="n >= 4"):
        compute_confidence_region(mini_scores_df.head(3), mini_roles, mini_bundle)


# --- payload -----------------------------------------------------------------------------


def test_payload_contract(mini_scores_df, mini_roles, mini_bundle) -> None:
    cr = compute_confidence_region(mini_scores_df, mini_roles, mini_bundle)
    payload = confidence_region_payload(cr)
    json.dumps(payload, allow_nan=False)  # finite + serializable
    for key in (
        "schema_version", "purpose", "label", "variant", "alpha1", "alpha2",
        "nominal_coverage", "se_method", "n_units", "n_menu", "n_select_restrictions",
        "delta", "levels", "CR_L", "CR_U", "empty_outer", "M_plus", "M_minus", "status",
        "slack_bounds", "beta_intervals", "beta_estimates_hash", "target", "note",
        "headline_note",
    ):  # fmt: skip
        assert key in payload, key
    assert payload["purpose"] == "conservative_confidence_region"
    assert payload["variant"] == "endpoint" and payload["se_method"] == "robust"
    assert payload["nominal_coverage"] == pytest.approx(0.90)
    assert payload["target"] == "select_stage_population_range"
    assert "Conservative confidence region" in payload["label"]
    assert set(payload["status"].values()) <= STATUSES
    assert "never replaces" in payload["headline_note"]


# --- operating characteristic smoke (package implementation) ---------------------------


def test_knife_edge_coverage_smoke() -> None:
    """Spec §12 DGP, J = 3, d = 0: both range-defining measures sit on the boundary."""
    a = np.asarray([0.80, 0.50, 0.80])
    b = np.asarray([0.00, 0.00, 0.30])
    names = ["core", "edge_lo", "edge_hi"]
    beta0 = 0.5 * a + 0.6 * b
    L0, U0 = float(beta0.min()), float(beta0.max())
    roles = ScoreColumnRoles(unit_id="unit_id", measures=names, aux=["V", "W"], outcome="Y")
    network = {
        "schema_version": "1",
        "restrictions": [
            {"id": "r1", "type": "corr_min", "theta": 0.40, "params": {"variable": "V"}},
            {"id": "r2", "type": "corr_zero", "theta": 0.30, "params": {"variable": "W"}},
        ],
    }
    bundle = run_restrict(roles, network, {"schema_version": "1", "type": "corr_y", "outcome": "Y"})
    rng = np.random.default_rng(20261020)
    reps, n, covered = 200, 200, 0
    for _ in range(reps):
        sh = rng.standard_normal(size=(n, 7))
        C, W = sh[:, 0], sh[:, 1]
        M = C[:, None] * a + W[:, None] * b + sh[:, 4:] * np.sqrt(1 - a**2 - b**2)
        frame = pd.DataFrame(M, columns=names)
        frame["V"] = 0.8 * C + 0.6 * sh[:, 2]
        frame["W"] = W
        frame["Y"] = 0.5 * C + 0.6 * W + math.sqrt(0.39) * sh[:, 3]
        frame["unit_id"] = [f"u{i}" for i in range(n)]
        cr = compute_confidence_region(frame, roles, bundle)
        covered += cr.cr_L is not None and cr.cr_L <= L0 and cr.cr_U >= U0
    # nominal >= 0.90; MC SE at 200 reps ≈ 0.021 ⇒ 3-SE floor
    assert covered / reps >= 0.84


# --- pipeline / report / CLI wiring ------------------------------------------------------


def _profile(mini_dir, out, **kw):
    from cvprofiles.pipeline import run_profile

    args = {
        "scores": mini_dir / "scores.csv",
        "roles": mini_dir / "roles.json",
        "network": mini_dir / "network.yaml",
        "beta": mini_dir / "beta.yaml",
        "out_dir": out,
    }
    args.update(kw)
    return run_profile(**args)


def test_pipeline_writes_region_and_keeps_golden_run_id(
    mini_dir, tmp_path, mini_expected_freeze, mini_scores_df, mini_roles, mini_bundle
) -> None:
    on = _profile(mini_dir, tmp_path / "on", confidence_region=True)
    assert on.run_id == mini_expected_freeze["run_id"]
    payload = json.loads((on.out_dir / "confidence_region.json").read_text())
    expected = confidence_region_payload(
        compute_confidence_region(mini_scores_df, mini_roles, mini_bundle)
    )
    assert payload == json.loads(json.dumps(expected))
    assert on.confidence_region is not None
    assert on.artifact_paths["confidence_region.json"] == "confidence_region.json"


def test_region_knobs_never_enter_freeze_preimage(mini_dir, tmp_path, mini_expected_freeze) -> None:
    golden = mini_expected_freeze["run_id"]
    off = _profile(mini_dir, tmp_path / "off")
    tuned = _profile(
        mini_dir,
        tmp_path / "tuned",
        confidence_region=True,
        cr_alpha1=0.01,
        cr_alpha2=0.04,
        cr_variant="simultaneous",
        cr_se="classical",
    )
    assert off.run_id == tuned.run_id == golden
    assert tuned.run_manifest.freeze.config == {}
    a = json.loads((tuned.out_dir / "confidence_region.json").read_text())
    assert (a["alpha1"], a["variant"], a["se_method"]) == (0.01, "simultaneous", "classical")


def test_headline_unchanged_by_region_layer(mini_dir, tmp_path) -> None:
    off = _profile(mini_dir, tmp_path / "off", n_boot=20)
    on = _profile(mini_dir, tmp_path / "on", n_boot=20, confidence_region=True)
    for attr in ("range_L", "range_U", "admissible", "M_star_select", "M_star_robust"):
        assert getattr(on.identify, attr) == getattr(off.identify, attr)
    assert on.identify.slacks.equals(off.identify.slacks)
    for name in ("range.json", "admissible.json", "bootstrap.json", "coverage.json"):
        assert (on.out_dir / name).read_bytes() == (off.out_dir / name).read_bytes()


def test_stale_region_artifact_removed_when_layer_off(mini_dir, tmp_path) -> None:
    out = tmp_path / "reuse"
    _profile(mini_dir, out, confidence_region=True)
    assert (out / "confidence_region.json").exists()
    _profile(mini_dir, out)
    assert not (out / "confidence_region.json").exists()


def test_report_and_summary_carry_region(mini_dir, tmp_path) -> None:
    from cvprofiles.pipeline import summary_dict

    on = _profile(mini_dir, tmp_path / "on", confidence_region=True)
    off = _profile(mini_dir, tmp_path / "off")
    rep_on = json.loads((on.out_dir / "report.json").read_text())
    rep_off = json.loads((off.out_dir / "report.json").read_text())
    assert rep_on["confidence_region"]["purpose"] == "conservative_confidence_region"
    assert rep_off["confidence_region"] is None
    assert "Conservative confidence region" in (on.out_dir / "report.html").read_text()
    assert "Conservative confidence region" not in (off.out_dir / "report.html").read_text()
    s_on, s_off = summary_dict(on), summary_dict(off)
    assert s_off["confidence_region"] is None
    block = s_on["confidence_region"]
    assert block["artifact"] == "confidence_region.json"
    assert block["CR_L"] <= on.identify.range_L <= on.identify.range_U <= block["CR_U"]


def test_region_with_holdout_units_fails_before_writing(mini_dir, tmp_path) -> None:
    out = tmp_path / "split"
    with pytest.raises(ConfidenceRegionError, match="holdout_units"):
        _profile(mini_dir, out, confidence_region=True, holdout_units=["u01", "u02", "u03"])
    assert not out.exists()


def test_region_with_unsupported_beta_fails_before_writing(mini_dir, tmp_path) -> None:
    beta = tmp_path / "ols.yaml"
    beta.write_text(
        "schema_version: '1'\ntype: ols_coef\noutcome: y\nparams:\n  controls: [v_aux]\n"
    )
    out = tmp_path / "ols"
    with pytest.raises(ConfidenceRegionError, match="external"):
        _profile(mini_dir, out, beta=beta, confidence_region=True)
    assert not out.exists()


def test_region_with_external_beta(mini_dir, tmp_path) -> None:
    est = tmp_path / "est.csv"
    est.write_text("measure,beta_hat,se\nm_good,0.41,0.10\nm_weak,0.22,0.12\nm_slop,0.90,0.05\n")
    beta = tmp_path / "ext.yaml"
    beta.write_text("schema_version: '1'\ntype: external\noutcome: y_fe\nparams: {}\n")
    res = _profile(
        mini_dir, tmp_path / "ext", beta=beta, beta_estimates=est, confidence_region=True
    )
    payload = json.loads((res.out_dir / "confidence_region.json").read_text())
    assert payload["beta_source"] == "external"
    assert payload["beta_estimates_hash"] == res.restrict.beta_estimates.estimates_hash
    assert payload["CR_L"] <= 0.22 and payload["CR_U"] >= 0.41


def _cli(mini_dir, out, *extra: str):
    import subprocess
    import sys

    cmd = [
        sys.executable, "-m", "cvprofiles", "run",
        "--scores", str(mini_dir / "scores.csv"),
        "--roles", str(mini_dir / "roles.json"),
        "--network", str(mini_dir / "network.yaml"),
        "--beta", str(mini_dir / "beta.yaml"),
        "--out", str(out), *extra,
    ]  # fmt: skip
    return subprocess.run(cmd, check=False, capture_output=True, text=True)


def test_cli_confidence_region_flags(mini_dir, tmp_path, mini_expected_freeze) -> None:
    proc = _cli(
        mini_dir, tmp_path / "cli", "--confidence-region", "--cr-variant", "simultaneous",
        "--cr-alpha1", "0.04", "--cr-alpha2", "0.06", "--cr-se", "classical",
    )  # fmt: skip
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["run_id"] == mini_expected_freeze["run_id"]
    block = summary["confidence_region"]
    assert (block["variant"], block["alpha1"], block["se_method"]) == (
        "simultaneous", 0.04, "classical"
    )
    default = json.loads(_cli(mini_dir, tmp_path / "plain").stdout)
    assert default["confidence_region"] is None


@pytest.mark.parametrize(
    "extra",
    [("--cr-alpha1", "0"), ("--cr-alpha2", "1.5"), ("--cr-variant", "bonf"), ("--cr-se", "hc3")],
)
def test_cli_bad_region_options_exit_2(mini_dir, tmp_path, extra) -> None:
    proc = _cli(mini_dir, tmp_path / "bad", "--confidence-region", *extra)
    assert proc.returncode == 2
    assert proc.stdout.strip() == ""
