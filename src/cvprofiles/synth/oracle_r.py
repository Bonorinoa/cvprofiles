"""Oracle-compatible networks for synthetic evals only (not paper empirical R)."""

from __future__ import annotations

from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig, RestrictionSpec


def beta_corr_y(outcome: str = "y") -> BetaSpec:
    return BetaSpec(type="corr_y", outcome=outcome, params={})


def network_for(scenario: str) -> NetworkConfig:
    """Return eval-only NetworkConfig for a scenario.

    Uses only restriction types with v1.0 evaluators: corr_min, corr_sign.
    """
    if scenario == "harsh_theta":
        # θ above feasible corr(m_valid, v_aux) under the DGP (~0.7–0.9).
        restrictions = [
            RestrictionSpec(
                id="r_corr_min_aux",
                type="corr_min",
                theta=0.95,
                params={"variable": "v_aux"},
            ),
            RestrictionSpec(
                id="r_corr_sign_aux",
                type="corr_sign",
                theta=0.50,
                params={"variable": "v_aux", "sign": 1},
            ),
        ]
        return NetworkConfig(
            schema_version="1",
            name=f"oracle_{scenario}",
            delta=0.0,
            restrictions=restrictions,
        )

    # oracle_easy, oracle_with_slop, all_invalid — standard oracle R
    restrictions = [
        RestrictionSpec(
            id="r_corr_min_aux",
            type="corr_min",
            theta=0.35,
            params={"variable": "v_aux"},
        ),
        RestrictionSpec(
            id="r_corr_sign_aux",
            type="corr_sign",
            theta=0.10,
            params={"variable": "v_aux", "sign": 1},
        ),
    ]
    return NetworkConfig(
        schema_version="1",
        name=f"oracle_{scenario}",
        delta=0.0,
        restrictions=restrictions,
    )
