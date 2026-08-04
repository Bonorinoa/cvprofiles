"""θ-grid sensitivity surface tests (v1.1 M6; semantics in docs/12, 2026-08-01)."""

from __future__ import annotations

import json

import pytest
import yaml

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.inference.theta_grid import (
    ThetaGridError,
    run_theta_grid,
    theta_grid_payload,
)
from cvprofiles.restrict.pipeline import RestrictBundle, run_restrict
from cvprofiles.schemas.network import NetworkConfig


@pytest.fixture(scope="module")
def oracle_bundle(mini_roles, mini_network, mini_beta) -> RestrictBundle:
    return run_restrict(mini_roles, mini_network, mini_beta)


@pytest.fixture(scope="module")
def harsh_bundle(mini_dir, mini_roles, mini_beta) -> RestrictBundle:
    harsh = NetworkConfig.model_validate(
        yaml.safe_load((mini_dir / "network_harsh.yaml").read_text())
    )
    return run_restrict(mini_roles, harsh, mini_beta)


# --- validation: loud failures on bad λ declarations ---


@pytest.mark.parametrize(
    "bad",
    [
        [],  # empty grid
        [0.0],  # λ must be > 0
        [-0.5, 1.0],  # negative λ
        [float("inf")],  # non-finite
        [float("nan")],  # non-finite
        [0.5, 0.5],  # duplicates
        "1.0",  # not a sequence of numbers
        [1.0, "two"],  # non-numeric entry
        None,  # not a sequence
    ],
)
def test_bad_lambdas_fail_loud(
    mini_scores_df, mini_roles, oracle_bundle, bad
) -> None:
    with pytest.raises(ThetaGridError):
        run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, bad)


def test_requires_restrict_bundle(mini_scores_df, mini_roles) -> None:
    with pytest.raises(ThetaGridError, match="RestrictBundle"):
        run_theta_grid(
            mini_scores_df, mini_roles, "not-a-bundle", [1.0]  # type: ignore[arg-type]
        )


# --- scaling semantics: λθ on thresholds; sign/δ untouched ---


def test_thetas_scale_exactly_by_lambda(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    lams = [0.5, 1.0, 2.0]
    res = run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, lams)
    declared = {r.id: float(r.theta) for r in oracle_bundle.network.restrictions}
    for row in res.rows:
        for rid, theta_declared in declared.items():
            assert row.thetas[rid] == pytest.approx(theta_declared * row.lambda_value)


def test_lambdas_sorted_and_used_as_declared(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    # Unsorted input is accepted and sorted ascending; no implicit 1.0 injection.
    res = run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, [2.0, 0.25])
    assert res.lambdas == (0.25, 2.0)
    assert [row.lambda_value for row in res.rows] == [0.25, 2.0]


def test_sign_and_delta_never_scaled(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, [3.0])
    sign_row = next(
        r for r in oracle_bundle.network.restrictions if r.type == "corr_sign"
    )
    # Reconstruct the scaled network to inspect params directly.
    from cvprofiles.inference.theta_grid import _scale_network

    scaled_net = _scale_network(oracle_bundle.network, 3.0)
    scaled_sign = next(r for r in scaled_net.restrictions if r.id == sign_row.id)
    assert scaled_sign.params == sign_row.params  # sign direction untouched
    assert scaled_net.delta == oracle_bundle.network.delta  # δ untouched


# --- behavior: λ=1.0 reproduces headline; monotone shrinkage; empty rows ---


def test_lambda_1_row_equals_headline(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    headline = run_identify(mini_scores_df, mini_roles, oracle_bundle)
    res = run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, [1.0])
    row = res.row_for(1.0)
    assert row is not None
    assert row.admissible == tuple(headline.admissible)
    assert row.empty == headline.empty
    assert row.range_L == headline.range_L
    assert row.range_U == headline.range_U
    assert row.network_hash == oracle_bundle.network_hash


def test_antitone_monotonicity_positive_thetas(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    """All declared θ > 0 here ⇒ larger λ tightens ⇒ M* can only shrink.

    (General case: monotonicity direction follows θ's sign; this fixture's
    θs are positive so antitone is the expected shape.)
    """
    assert all(r.theta > 0 for r in oracle_bundle.network.restrictions)
    lams = [0.5, 1.0, 1.5, 2.0, 3.0]
    res = run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, lams)
    counts = [row.n_admissible for row in res.rows]
    assert counts == sorted(counts, reverse=True)
    # Sets shrink, not just counts: M*(λ') ⊆ M*(λ) for λ' > λ.
    for lo, hi in zip(res.rows, res.rows[1:], strict=False):
        assert set(hi.admissible) <= set(lo.admissible)


def test_large_lambda_yields_empty_first_class(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    """θ=0.35·λ with λ=4 ⇒ 1.4 > correlation ceiling ⇒ empty M*, no crash."""
    res = run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, [4.0])
    row = res.rows[0]
    assert row.empty is True
    assert row.range_L is None and row.range_U is None
    assert row.n_admissible == 0


def test_harsh_grid_all_rows_empty(mini_scores_df, mini_roles, harsh_bundle) -> None:
    res = run_theta_grid(mini_scores_df, mini_roles, harsh_bundle, [1.0, 2.0])
    assert all(row.empty for row in res.rows)
    assert all(row.range_L is None for row in res.rows)


# --- purity: bundle untouched; deterministic; payload JSON-safe ---


def test_bundle_not_mutated_by_grid(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    hash_before = oracle_bundle.network_hash
    before = run_identify(mini_scores_df, mini_roles, oracle_bundle)
    run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, [0.5, 2.0])
    assert oracle_bundle.network_hash == hash_before
    after = run_identify(mini_scores_df, mini_roles, oracle_bundle)
    assert after.admissible == before.admissible
    assert after.range_L == before.range_L


def test_payload_json_serializable_and_deterministic(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    a = run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, [0.5, 1.0, 2.0])
    b = run_theta_grid(mini_scores_df, mini_roles, oracle_bundle, [0.5, 1.0, 2.0])
    assert theta_grid_payload(a) == theta_grid_payload(b)
    text = json.dumps(theta_grid_payload(a), sort_keys=True)
    assert '"headline_lambda": 1.0' in text
    assert '"purpose": "diagnostic_theta_sensitivity"' in text
