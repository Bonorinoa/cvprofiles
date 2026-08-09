"""P5 coverage uncertainty band — RED/GREEN contract tests (docs/12, 2026-08-08).

Locked semantics under test:
- Coverage block derives from the SAME per-replicate samples as bootstrap.json —
  one resampling loop, no second RNG stream (structural: compute_coverage takes
  the BootstrapResult as input).
- Default alpha = 0.10 ⇒ quantiles (0.05, 0.95); validated 0 < alpha < 1.
- bootstrap.json keeps its v1.1 locked percentile pair (0.025, 0.975) — payload
  shape unchanged (no new keys).
- Boundary attribution: margin_m = min_r s_r(m) over ALL restrictions on the
  pooled full-frame slacks; SE_m = ddof=1 SD of per-replicate min-slacks across
  non-empty replicates; boundary iff |margin_m| <= kappa * SE_m (amendment
  cb566c8 — distance from the threshold; far-rejected measures are NOT
  boundary). kappa default 2.0.
- "Non-empty replicate" = replicate whose overall M*_b is non-empty (clarified
  docs/12 2026-08-08). Pinned via len(min_slack_samples[m]) == replicates_nonempty.
- p_hat_m = #admitted-in-nonempty-replicate / #non-empty-replicates; null when
  denominator 0 (all-empty ⇒ band null + note, structured nulls, exit 0).
- alpha/kappa EXCLUDED from the freeze preimage: same bundle + different alpha
  ⇒ same run_id, different coverage.json. No new FreezeBundle.config keys.
- Stale coverage.json removed when bootstrap off.
"""

from __future__ import annotations

import json

import numpy as np
import pytest

from cvprofiles.identify.slacks import slack_matrix
from cvprofiles.inference.bootstrap import (
    bootstrap_payload,
    run_bootstrap,
)
from cvprofiles.inference.coverage import (
    CoverageError,
    compute_coverage,
    coverage_payload,
)
from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.restrict.pipeline import RestrictBundle, run_restrict
from cvprofiles.schemas.network import NetworkConfig, RestrictionSpec


@pytest.fixture(scope="module")
def oracle_bundle(mini_roles, mini_network, mini_beta) -> RestrictBundle:
    return run_restrict(mini_roles, mini_network, mini_beta)


# --- bootstrap.json v1.1 shape unchanged; coverage is a separate artifact ---


def test_bootstrap_payload_v11_shape_unchanged(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    res = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=50, seed=7)
    payload = bootstrap_payload(res)
    # v1.1 locked pair stays put
    assert payload["quantiles"] == [0.025, 0.975]
    # coverage-layer fields live on BootstrapResult / coverage.json, never here
    assert "alpha" not in payload
    assert "min_slack_samples" not in payload
    assert "admission_counts" not in payload


def test_min_slack_samples_collected_over_nonempty_replicates(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    """Denominator pin (docs/12 clarification): non-empty replicate = non-empty M*."""
    res = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=60, seed=7)
    assert res.min_slack_samples is not None
    assert res.admission_counts is not None
    assert len(res.min_slack_samples) == len(mini_roles.measures)
    assert set(res.admission_counts) == set(mini_roles.measures)
    for m in mini_roles.measures:
        assert len(res.min_slack_samples[m]) == res.replicates_nonempty
        assert 0 <= res.admission_counts[m] <= res.replicates_nonempty


# --- coverage band: same-loop identity + alpha quantiles + validation ---


def test_coverage_band_derives_from_same_bootstrap_samples(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    """Structural guard against a second resampling loop / RNG divergence."""
    res = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=200, seed=7)
    cov = compute_coverage(res, mini_scores_df, mini_roles, oracle_bundle, alpha=0.10)
    assert cov.quantiles == (0.05, 0.95)
    assert cov.band_L == float(np.quantile(np.asarray(res.L_samples), 0.05))
    assert cov.band_U == float(np.quantile(np.asarray(res.U_samples), 0.95))


def test_coverage_alpha_validation_fails_loud(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    res = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=20, seed=3)
    for bad in (0.0, 1.0, -0.1, 1.5):
        with pytest.raises(CoverageError, match="alpha"):
            compute_coverage(res, mini_scores_df, mini_roles, oracle_bundle, alpha=bad)
    with pytest.raises(CoverageError, match="kappa"):
        compute_coverage(res, mini_scores_df, mini_roles, oracle_bundle, kappa=0.0)
    with pytest.raises(CoverageError, match="BootstrapResult"):
        # string passed in the RESULT slot (the guard is on result, not bundle)
        compute_coverage("not-a-result", mini_scores_df, mini_roles, oracle_bundle, alpha=0.10)  # type: ignore[arg-type]


# --- boundary attribution: margin/SE rule, semi-golden, rejected-can-be-boundary ---


def test_boundary_attribution_matches_locked_rule(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    res = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=200, seed=7)
    cov = compute_coverage(res, mini_scores_df, mini_roles, oracle_bundle, kappa=2.0)

    # Independent margins: pooled full-frame slacks, min over ALL restrictions.
    sl = slack_matrix(mini_scores_df, mini_roles.measures, oracle_bundle.network.restrictions)
    margins = sl.min(axis=1)

    rows = {row.measure: row for row in cov.boundary}
    assert set(rows) == set(mini_roles.measures)
    for m in mini_roles.measures:
        row = rows[m]
        assert row.margin == float(margins[m])
        # SE from the SAME per-replicate samples, ddof=1
        assert row.se == float(np.std(np.asarray(res.min_slack_samples[m]), ddof=1))
        assert row.kappa == 2.0
        if row.se is not None:
            assert row.boundary == (abs(row.margin) <= row.kappa * row.se)
        else:
            assert row.boundary is False


def test_boundary_rule_applies_to_all_measures_including_rejected(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    """Boundary attribution runs for EVERY menu measure, admissible or not.

    Locked semantics: boundary iff |margin_m| <= kappa*SE_m (amendment
    cb566c8 — the signed rule is vacuous for rejected measures). Which
    measures land on the boundary depends on bootstrap draws — the contract
    is the rule, asserted by test_boundary_attribution_matches_locked_rule.
    This test pins the stable part: m_good sits far above the threshold on
    the mini fixture, so it is NOT boundary under the locked rule
    (margin ~0.6+, SE well below 0.3).
    """
    res = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=200, seed=7)
    cov = compute_coverage(res, mini_scores_df, mini_roles, oracle_bundle, kappa=2.0)
    boundary_measures = [row.measure for row in cov.boundary if row.boundary]
    assert "m_good" not in boundary_measures
    # every boundary flag must satisfy the locked rule
    for row in cov.boundary:
        if row.boundary:
            assert row.se is not None and abs(row.margin) <= row.kappa * row.se


def test_far_rejected_measure_is_not_boundary_deterministic(
    mini_scores_df, mini_roles, mini_beta
) -> None:
    """Construction pinned by docs/12 (cb566c8): single corr_min with θ =
    midpoint of the top-two measured correlations with v_aux ⇒ the most
    anti-correlated measure (m_slop) misses by ≈ the full distance to θ, far
    beyond κ·SE ⇒ NOT boundary under the |margin| rule. The OLD signed rule
    would mark it boundary (negative margin <= κ·SE) — this test is the RED
    guard that keeps the amendment honest.
    """
    v = mini_scores_df["v_aux"].to_numpy(dtype=float)
    corrs = {
        m: float(np.corrcoef(mini_scores_df[m].to_numpy(dtype=float), v)[0, 1])
        for m in mini_roles.measures
    }
    top2 = sorted(corrs.values(), reverse=True)[:2]
    theta = float((top2[0] + top2[1]) / 2.0)
    net = NetworkConfig(
        name="far_rejected",
        delta=0.0,
        restrictions=[
            RestrictionSpec.model_validate(
                {
                    "id": "r_corr_min",
                    "type": "corr_min",
                    "theta": theta,
                    "params": {"variable": "v_aux"},
                }
            )
        ],
    )
    bundle = run_restrict(mini_roles, net, mini_beta)
    res = run_bootstrap(mini_scores_df, mini_roles, bundle, n_boot=100, seed=7)
    assert res.replicates_nonempty > 0  # m_good survives the midpoint threshold
    cov = compute_coverage(res, mini_scores_df, mini_roles, bundle, kappa=2.0)
    anti = min(corrs, key=lambda m: corrs[m])  # most anti-correlated measure
    row = next(r for r in cov.boundary if r.measure == anti)
    assert row.margin < 0.0
    assert row.boundary is False  # |margin| >> kappa*SE


# --- p_hat_m admission frequency ---


def test_p_hat_m_denominator_and_endpoints(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    res = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=200, seed=7)
    cov = compute_coverage(res, mini_scores_df, mini_roles, oracle_bundle)
    assert set(cov.p_hat_m) == set(mini_roles.measures)
    for m in mini_roles.measures:
        assert cov.p_hat_m[m] is not None
        assert 0.0 <= cov.p_hat_m[m] <= 1.0
    # m_good always passes both oracle restrictions; m_slop never passes corr_sign
    assert cov.p_hat_m["m_good"] == 1.0
    assert cov.p_hat_m["m_slop"] == 0.0
    # Consistency with the collected admission counts
    for m in mini_roles.measures:
        assert cov.p_hat_m[m] == res.admission_counts[m] / res.replicates_nonempty


# --- all-empty harsh fixture: structured nulls, exit-0 semantics ---


def test_all_empty_structured_nulls_deterministic(
    mini_scores_df, mini_roles, mini_beta
) -> None:
    """All-empty MUST be deterministic: a corr_min threshold above the corr
    ceiling (θ=1.5) empties every replicate regardless of resampling draws —
    no dependence on the θ=0.999 harsh fixture's near-ceiling behavior.
    """
    net = NetworkConfig(
        name="impossible",
        delta=0.0,
        restrictions=[
            RestrictionSpec.model_validate(
                {
                    "id": "r_impossible",
                    "type": "corr_min",
                    "theta": 1.5,
                    "params": {"variable": "v_aux"},
                }
            )
        ],
    )
    bundle = run_restrict(mini_roles, net, mini_beta)
    res = run_bootstrap(mini_scores_df, mini_roles, bundle, n_boot=40, seed=3)
    assert res.replicates_nonempty == 0
    cov = compute_coverage(res, mini_scores_df, mini_roles, bundle)
    assert cov.band_L is None and cov.band_U is None
    assert cov.note is not None and "empty" in cov.note
    assert cov.boundary == ()  # dataclass field is a frozen tuple
    for m in mini_roles.measures:
        assert cov.p_hat_m[m] is None
    payload = coverage_payload(cov)
    assert payload["band_L"] is None and payload["band_U"] is None
    assert payload["boundary"] == []  # JSON contract is a list


# --- freeze preimage: alpha/kappa excluded (the governance witness) ---


def test_alpha_kappa_never_enter_freeze_preimage(
    mini_dir, mini_expected_freeze, tmp_path
) -> None:
    def _run_kwargs() -> dict:
        return {
            "scores": mini_dir / "scores.csv",
            "roles": mini_dir / "roles.json",
            "network": mini_dir / "network.yaml",
            "beta": mini_dir / "beta.yaml",
        }

    # n_boot off: alpha must not move the golden run_id
    default = run_profile(**_run_kwargs(), out_dir=tmp_path / "default", alpha=0.10)
    assert default.run_id == mini_expected_freeze["run_id"]
    assert default.run_manifest.freeze.config.get("alpha") is None
    assert default.run_manifest.freeze.config.get("kappa") is None

    # n_boot on: same bundle + different alpha ⇒ same run_id, different coverage.json
    a = run_profile(
        **_run_kwargs(), out_dir=tmp_path / "a", n_boot=20, seed=7, alpha=0.10
    )
    b = run_profile(
        **_run_kwargs(), out_dir=tmp_path / "b", n_boot=20, seed=7, alpha=0.05
    )
    assert a.run_id == b.run_id
    assert (a.out_dir / "coverage.json").is_file()
    assert (b.out_dir / "coverage.json").is_file()
    assert json.loads((a.out_dir / "coverage.json").read_text())["alpha"] == 0.10
    assert json.loads((b.out_dir / "coverage.json").read_text())["alpha"] == 0.05
    assert "alpha" not in a.run_manifest.freeze.config
    assert "kappa" not in a.run_manifest.freeze.config


# --- wiring: coverage.json artifact, summary, report, stale cleanup ---


def test_stale_coverage_artifact_removed_when_bootstrap_off(
    mini_dir, tmp_path
) -> None:
    out = tmp_path / "reuse"
    run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=out,
        n_boot=10,
        seed=7,
    )
    assert (out / "coverage.json").is_file()

    result = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=out,
    )
    assert result.bootstrap is None
    assert not (out / "coverage.json").exists()
    assert result.run_manifest.artifact_paths.get("coverage.json") is None


def test_wiring_summary_report_and_html(mini_dir, tmp_path) -> None:
    result = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=tmp_path / "wired",
        n_boot=12,
        seed=7,
        alpha=0.10,
    )
    assert result.bootstrap is not None
    assert result.report.payload["coverage"] is not None
    assert result.report.payload["coverage"]["alpha"] == 0.10
    assert result.report.payload["coverage"]["band_L"] is not None
    assert result.report.payload["coverage"]["band_U"] is not None

    summary = summary_dict(result)
    assert summary["coverage"]["artifact"] == "coverage.json"
    assert summary["coverage"]["alpha"] == 0.10

    html = (result.out_dir / "report.html").read_text()
    assert "Uncertainty band" in html
    assert "not a confidence interval" in html
    # existing literal assertions must survive
    assert "Bootstrap inference" in html
    assert "v1.1/v2.0 inference" in html


def test_coverage_off_is_none_and_template_safe(mini_dir, tmp_path) -> None:
    off = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=tmp_path / "off",
    )
    assert off.bootstrap is None
    assert summary_dict(off)["coverage"] is None
    assert off.report.payload["coverage"] is None
    assert not (off.out_dir / "coverage.json").exists()
    html = (off.out_dir / "report.html").read_text()
    assert "Uncertainty band" not in html  # panel absent when layer off
