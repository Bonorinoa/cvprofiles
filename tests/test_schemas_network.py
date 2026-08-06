"""NetworkConfig / RestrictionSpec contract tests (M1)."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from cvprofiles.schemas.network import NetworkConfig, RestrictionSpec, parse_network


def test_mini_network_validates(mini_network: NetworkConfig) -> None:
    assert mini_network.delta == 0.0
    assert len(mini_network.restrictions) == 2
    types = {r.type for r in mini_network.restrictions}
    assert types == {"corr_min", "corr_sign"}
    sign_r = next(r for r in mini_network.restrictions if r.type == "corr_sign")
    assert sign_r.params["sign"] == 1
    assert sign_r.params["variable"] == "v_aux"


def test_parse_network_helper(mini_network: NetworkConfig) -> None:
    again = parse_network(mini_network.model_dump(mode="json"))
    assert again == mini_network


def test_unknown_restriction_type_fails() -> None:
    with pytest.raises(ValidationError):
        RestrictionSpec(
            id="r_bad",
            type="not_a_real_type",  # type: ignore[arg-type]
            theta=0.1,
            params={"variable": "v_aux"},
        )


def test_corr_min_requires_variable() -> None:
    with pytest.raises(ValidationError, match="variable"):
        RestrictionSpec(id="r1", type="corr_min", theta=0.35, params={})


def test_corr_sign_requires_sign() -> None:
    with pytest.raises(ValidationError, match="sign"):
        RestrictionSpec(
            id="r1",
            type="corr_sign",
            theta=0.1,
            params={"variable": "v_aux"},
        )


def test_corr_sign_bad_sign_fails() -> None:
    with pytest.raises(ValidationError, match="sign"):
        RestrictionSpec(
            id="r1",
            type="corr_sign",
            theta=0.1,
            params={"variable": "v_aux", "sign": 0},
        )


def test_mean_order_requires_group() -> None:
    with pytest.raises(ValidationError, match="group"):
        RestrictionSpec(id="r1", type="mean_order", theta=0.1, params={})


def test_mean_order_bad_sign_fails() -> None:
    with pytest.raises(ValidationError, match="sign"):
        RestrictionSpec(
            id="r1", type="mean_order", theta=0.1, params={"group": "g", "sign": 0}
        )


def test_rank_agree_requires_ref_measure() -> None:
    with pytest.raises(ValidationError, match="ref_measure"):
        RestrictionSpec(id="r1", type="rank_agree", theta=0.5, params={})


def test_duplicate_restriction_ids_fail() -> None:
    with pytest.raises(ValidationError, match="unique"):
        NetworkConfig(
            restrictions=[
                RestrictionSpec(
                    id="same",
                    type="corr_min",
                    theta=0.3,
                    params={"variable": "v_aux"},
                ),
                RestrictionSpec(
                    id="same",
                    type="corr_sign",
                    theta=0.1,
                    params={"variable": "v_aux", "sign": 1},
                ),
            ]
        )


def test_empty_restrictions_fail() -> None:
    with pytest.raises(ValidationError):
        NetworkConfig(restrictions=[])


def test_extra_field_forbidden() -> None:
    with pytest.raises(ValidationError):
        NetworkConfig.model_validate(
            {
                "restrictions": [
                    {
                        "id": "r1",
                        "type": "corr_min",
                        "theta": 0.3,
                        "params": {"variable": "v_aux"},
                    }
                ],
                "author_ghost": "nope",
            }
        )


def test_negative_delta_fails() -> None:
    with pytest.raises(ValidationError):
        NetworkConfig(
            delta=-0.01,
            restrictions=[
                RestrictionSpec(
                    id="r1",
                    type="corr_min",
                    theta=0.3,
                    params={"variable": "v_aux"},
                )
            ],
        )
