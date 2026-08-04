"""G6: bootstrap over units (v1.1 M6). Deterministic pinned-seed contracts."""

from __future__ import annotations

import pytest
import yaml

from cvprofiles import __version__
from cvprofiles.freeze import (
    compute_run_id,
    hash_beta,
    hash_network,
    hash_scores_frame,
    normalize_n_boot,
)
from cvprofiles.identify.pipeline import run_identify
from cvprofiles.inference.bootstrap import (
    BootstrapError,
    bootstrap_payload,
    run_bootstrap,
)
from cvprofiles.restrict.pipeline import RestrictBundle, run_restrict
from cvprofiles.schemas.network import NetworkConfig, RestrictionSpec


@pytest.fixture(scope="module")
def oracle_bundle(mini_roles, mini_network, mini_beta) -> RestrictBundle:
    return run_restrict(mini_roles, mini_network, mini_beta)


@pytest.fixture(scope="module")
def harsh_bundle(mini_dir, mini_roles, mini_beta) -> RestrictBundle:
    harsh = NetworkConfig.model_validate(
        yaml.safe_load((mini_dir / "network_harsh.yaml").read_text())
    )
    return run_restrict(mini_roles, harsh, mini_beta)


# --- normalize_n_boot + preimage stability (docs/12 v1.1 lock) ---


def test_normalize_n_boot() -> None:
    assert normalize_n_boot(None) is None
    assert normalize_n_boot(0) is None
    assert normalize_n_boot(-3) is None
    assert normalize_n_boot(1) == 1
    assert normalize_n_boot(50) == 50


def test_default_n_boot_null_preserves_bumped_run_id(
    mini_scores_df,
    mini_roles,
    mini_network,
    mini_beta,
    mini_freeze_columns,
    mini_expected_freeze,
) -> None:
    """Lock-meets-code: n_boot < 1 serializes as null ⇒ default run_id intact.

    (The golden carries the current package version; what this locks is the
    n_boot normalization, not the version.)
    """
    scores_hash = hash_scores_frame(
        mini_scores_df, mini_freeze_columns, unit_id_col=mini_roles.unit_id
    )
    run_id = compute_run_id(
        scores_hash=scores_hash,
        network_hash=hash_network(mini_network),
        beta_hash=hash_beta(mini_beta),
        package_version=__version__,
        seed=0,
        delta=float(mini_network.delta),
        n_boot=normalize_n_boot(0),
        config={},
    )
    assert run_id == mini_expected_freeze["run_id"]


# --- oracle band: containment, counts, determinism ---


def test_oracle_band_contains_headline_range(
    mini_scores_df, mini_roles, oracle_bundle
) -> None:
    headline = run_identify(mini_scores_df, mini_roles, oracle_bundle)
    assert not headline.empty
    assert headline.range_L is not None and headline.range_U is not None
    res = run_bootstrap(
        mini_scores_df, mini_roles, oracle_bundle, n_boot=100, seed=7
    )
    assert res.band_L is not None and res.band_U is not None
    assert res.band_L <= res.band_U
    # Empirical pinned-seed containment, NOT a theorem: resample correlations
    # can exceed full-sample values (see harsh test). Kept because it is
    # deterministic at this seed and documents the observed band behavior.
    assert res.band_L <= headline.range_L
    assert headline.range_U <= res.band_U


def test_counts_invariant(mini_scores_df, mini_roles, oracle_bundle) -> None:
    res = run_bootstrap(
        mini_scores_df, mini_roles, oracle_bundle, n_boot=40, seed=11
    )
    assert (
        res.replicates_nonempty
        + res.replicates_empty
        + res.replicates_degenerate
        == res.n_boot
    )
    assert res.empty_replicate_rate == res.replicates_empty / res.n_boot
    assert res.degenerate_replicate_rate == res.replicates_degenerate / res.n_boot
    assert len(res.L_samples) == res.replicates_nonempty
    assert len(res.U_samples) == res.replicates_nonempty


def test_cold_double_run_identical(mini_scores_df, mini_roles, oracle_bundle) -> None:
    a = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=50, seed=7)
    b = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=50, seed=7)
    assert bootstrap_payload(a) == bootstrap_payload(b)


def test_different_seed_changes_draws(mini_scores_df, mini_roles, oracle_bundle) -> None:
    a = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=50, seed=7)
    b = run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=50, seed=8)
    assert (a.L_samples, a.U_samples) != (b.L_samples, b.U_samples)


# --- empty / impossible networks ---


def test_impossible_theta_all_empty_band_null(
    mini_scores_df, mini_roles, mini_beta
) -> None:
    """θ above the correlation ceiling ⇒ every replicate empty ⇒ band null.

    Note: this exercises the EMPTY channel; the degenerate channel
    (resample-induced evaluation failure) is not triggered here because
    run_identify returns an empty result rather than raising.
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
    headline = run_identify(mini_scores_df, mini_roles, bundle)
    assert headline.empty

    res = run_bootstrap(mini_scores_df, mini_roles, bundle, n_boot=30, seed=3)
    assert res.replicates_nonempty == 0
    assert res.band_L is None and res.band_U is None
    assert res.note is not None and "empty" in res.note
    assert res.empty_replicate_rate + res.degenerate_replicate_rate == 1.0


def test_harsh_fixture_invariants(mini_scores_df, mini_roles, harsh_bundle) -> None:
    """Harsh mini (θ=0.999): headline empty; band either null or well-ordered."""
    headline = run_identify(mini_scores_df, mini_roles, harsh_bundle)
    assert headline.empty
    res = run_bootstrap(mini_scores_df, mini_roles, harsh_bundle, n_boot=40, seed=3)
    assert res.replicates_total == 40
    assert (
        res.replicates_nonempty
        + res.replicates_empty
        + res.replicates_degenerate
        == res.n_boot
    )
    if res.replicates_nonempty == 0:
        assert res.band_L is None and res.band_U is None
        assert res.note is not None
    else:
        # Resample correlations can exceed the full-sample value; that is
        # honest behavior, and the band must still be well-ordered.
        assert res.band_L is not None and res.band_U is not None
        assert res.band_L <= res.band_U


# --- loud failures ---


def test_bad_inputs_fail_loud(mini_scores_df, mini_roles, oracle_bundle) -> None:
    with pytest.raises(BootstrapError, match="n_boot"):
        run_bootstrap(mini_scores_df, mini_roles, oracle_bundle, n_boot=0, seed=0)
    with pytest.raises(BootstrapError, match="quantiles"):
        run_bootstrap(
            mini_scores_df,
            mini_roles,
            oracle_bundle,
            n_boot=10,
            seed=0,
            quantiles=(0.9, 0.1),
        )
    with pytest.raises(BootstrapError, match="RestrictBundle"):
        run_bootstrap(
            mini_scores_df, mini_roles, "not-a-bundle", n_boot=10, seed=0  # type: ignore[arg-type]
        )
