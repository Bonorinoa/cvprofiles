"""IDENTIFY state contract tests (M4 slacks/M* + M5 β/range)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.identify.pipeline import IdentifyError, run_identify, write_identify_artifacts
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.schemas.scores import ScoreColumnRoles
from cvprofiles.score.pipeline import run_score

# Hand-computed goldens for mini_v1 (atol loose enough for float, tight on sign/membership)
_ATOL = 1e-9


@pytest.fixture
def scored_mini(mini_scores_df: pd.DataFrame, mini_roles: ScoreColumnRoles):
    return run_score(mini_scores_df, mini_roles, policy="none")


@pytest.fixture
def restrict_mini(mini_dir: Path, mini_roles: ScoreColumnRoles):
    return run_restrict(mini_roles, mini_dir / "network.yaml", mini_dir / "beta.yaml")


@pytest.fixture
def restrict_harsh(mini_dir: Path, mini_roles: ScoreColumnRoles):
    return run_restrict(
        mini_roles, mini_dir / "network_harsh.yaml", mini_dir / "beta.yaml"
    )


def test_identify_mini_membership_and_slacks(scored_mini, restrict_mini) -> None:
    result = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)

    assert set(result.admissible) == {"m_good", "m_weak"}
    assert "m_slop" not in result.admissible
    assert "m_slop" in result.rejected
    assert "r_corr_min_aux" in result.rejected["m_slop"]
    assert "r_corr_sign_aux" in result.rejected["m_slop"]
    assert result.empty is False
    assert result.point_id is False

    # Hand goldens
    assert result.slacks.at["m_good", "r_corr_min_aux"] == pytest.approx(0.647689, abs=1e-5)
    assert result.slacks.at["m_slop", "r_corr_min_aux"] == pytest.approx(-1.325692, abs=1e-5)
    assert float(result.slacks.at["m_good", "r_corr_min_aux"]) >= 0.0
    assert float(result.slacks.at["m_slop", "r_corr_min_aux"]) < 0.0


def test_identify_range_is_image_on_M_star_only(scored_mini, restrict_mini) -> None:
    result = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)

    # β reported for full menu
    assert set(result.beta_values) == {"m_good", "m_weak", "m_slop"}
    # range uses survivors only
    b_star = [result.beta_values[m] for m in result.admissible]
    assert result.range_L == pytest.approx(min(b_star), abs=_ATOL)
    assert result.range_U == pytest.approx(max(b_star), abs=_ATOL)
    # slop β is negative and must NOT pull L down
    assert result.beta_values["m_slop"] < 0
    assert result.range_L is not None and result.range_L > 0.9
    assert result.range_U is not None and result.range_U > result.range_L - 1e-12


def test_identify_false_admission_zero(scored_mini, restrict_mini) -> None:
    """FA proxy: designed invalid m_slop never in M*."""
    result = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)
    assert "m_slop" not in result.admissible


def test_identify_harsh_empty_is_success(scored_mini, restrict_harsh) -> None:
    result = run_identify(scored_mini.frame, scored_mini.roles, restrict_harsh)
    assert result.empty is True
    assert result.admissible == []
    assert result.range_L is None
    assert result.range_U is None
    assert result.point_id is False
    # all measures rejected
    assert set(result.rejected) == {"m_good", "m_weak", "m_slop"}


def test_identify_cold_double_run(scored_mini, restrict_mini) -> None:
    a = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)
    b = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)
    assert a.admissible == b.admissible
    assert a.range_L == b.range_L and a.range_U == b.range_U
    pd.testing.assert_frame_equal(a.slacks, b.slacks)
    assert a.beta_values == b.beta_values


def test_identify_unimplemented_restriction_fails_loud(
    scored_mini, mini_roles: ScoreColumnRoles, mini_dir: Path
) -> None:
    # mean_order is schema-valid but has no v1.0 evaluator
    raw_net = {
        "schema_version": "1",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_mean",
                "type": "mean_order",
                "theta": 0.1,
                "params": {"group": "v_aux"},  # bindable column; evaluator missing
            }
        ],
    }
    # beta still needed
    bundle = run_restrict(mini_roles, raw_net, mini_dir / "beta.yaml")
    with pytest.raises(IdentifyError, match="no evaluator|thin spine"):
        run_identify(scored_mini.frame, scored_mini.roles, bundle)


def test_write_identify_artifacts(scored_mini, restrict_mini, tmp_path: Path) -> None:
    result = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)
    paths = write_identify_artifacts(result, tmp_path)
    assert paths["slacks.csv"].is_file()
    assert paths["admissible.json"].is_file()
    assert paths["beta_values.json"].is_file()
    assert paths["range.json"].is_file()
    import json

    adm = json.loads(paths["admissible.json"].read_text())
    assert set(adm["M_star"]) == {"m_good", "m_weak"}
    rng = json.loads(paths["range.json"].read_text())
    assert rng["empty"] is False
    assert rng["method"] == "min_max_B_star"
    assert rng["bootstrap"] is None


def test_write_empty_artifacts(scored_mini, restrict_harsh, tmp_path: Path) -> None:
    result = run_identify(scored_mini.frame, scored_mini.roles, restrict_harsh)
    paths = write_identify_artifacts(result, tmp_path)
    import json

    rng = json.loads(paths["range.json"].read_text())
    assert rng["empty"] is True
    assert rng["L"] is None and rng["U"] is None


# --- v2.0 δ-grid API: delta_override on run_identify (docs/12, 2026-08-05) ---


def test_delta_override_none_matches_default(scored_mini, restrict_mini) -> None:
    """Default path stays bit-identical when no override is passed."""
    default = run_identify(scored_mini.frame, scored_mini.roles, restrict_mini)
    explicit = run_identify(
        scored_mini.frame, scored_mini.roles, restrict_mini, delta_override=None
    )
    assert explicit.admissible == default.admissible
    assert explicit.range_L == default.range_L and explicit.range_U == default.range_U
    assert explicit.delta == default.delta == 0.0


def test_delta_override_changes_harsh_admission(scored_mini, restrict_harsh) -> None:
    """Tolerance override is an IDENTIFY-side admission rule, not a network change.

    Measured slacks on mini_v1 harsh (hand-verified): m_good corr_min slack
    -0.001311, m_weak -0.005854; m_slop fails both bars (corr_min -1.974692,
    corr_sign -1.075692). δ=0.01 admits both designed valids, never m_slop.
    """
    empty = run_identify(scored_mini.frame, scored_mini.roles, restrict_harsh)
    assert empty.empty is True

    result = run_identify(
        scored_mini.frame, scored_mini.roles, restrict_harsh, delta_override=0.01
    )
    assert result.empty is False
    assert set(result.admissible) == {"m_good", "m_weak"}
    assert "m_slop" not in result.admissible
    assert result.delta == pytest.approx(0.01, abs=1e-12)
    assert result.range_L is not None and result.range_U is not None


def test_delta_override_negative_fails_loud(scored_mini, restrict_mini) -> None:
    with pytest.raises(IdentifyError, match="delta_override"):
        run_identify(
            scored_mini.frame, scored_mini.roles, restrict_mini, delta_override=-0.1
        )


def test_delta_override_nonfinite_fails_loud(scored_mini, restrict_mini) -> None:
    with pytest.raises(IdentifyError, match="delta_override"):
        run_identify(
            scored_mini.frame,
            scored_mini.roles,
            restrict_mini,
            delta_override=float("nan"),
        )
