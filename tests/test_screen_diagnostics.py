"""Report-only screen diagnostics (docs: logs/DECISIONS.md 2026-10-19, D1–D9).

(a) criterion self-consistency, (b) auxiliary ceiling / proxy flag,
(c) near-threshold multiplicity. None of them may touch M*, [L,U], or run_id.
"""

from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd
import pytest
from pydantic import ValidationError

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.identify.slacks import pearson_corr, spearman_corr
from cvprofiles.inference.bootstrap import run_bootstrap
from cvprofiles.inference.coverage import BoundaryRow, CoverageResult, compute_coverage
from cvprofiles.report.screen_diagnostics import (
    aux_ceiling,
    criterion_self_consistency,
    near_threshold,
    resolve_criteria,
)
from cvprofiles.restrict.pipeline import RestrictBundle, run_restrict
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.scores import ScoreColumnRoles

MEASURES = ["m_track", "m_proxy", "m_noise"]


def _frame(n: int = 200, seed: int = 0, slope: float = -0.3) -> pd.DataFrame:
    """Criterion y = slope·v_aux + noise (default NEGATIVE); m_proxy ≈ v_aux."""
    rng = np.random.default_rng(seed)
    v = rng.normal(size=n)
    y = slope * v + rng.normal(size=n)
    return pd.DataFrame(
        {
            "unit_id": [f"u{i:03d}" for i in range(n)],
            "m_track": y + 0.1 * rng.normal(size=n),
            "m_proxy": v + 0.3 * rng.normal(size=n),
            "m_noise": rng.normal(size=n),
            "v_aux": v,
            "w_const": np.ones(n),
            "y": y,
        }
    )


def _roles(criteria: list[str] | None = None) -> ScoreColumnRoles:
    payload: dict[str, Any] = {
        "unit_id": "unit_id",
        "measures": MEASURES,
        "aux": ["v_aux", "w_const"],
        "outcome": "y",
    }
    if criteria is not None:
        payload["criteria"] = criteria
    return ScoreColumnRoles.model_validate(payload)


def _network(delta: float = 0.0) -> dict[str, Any]:
    return {
        "schema_version": "1",
        "delta": delta,
        "restrictions": [
            {
                "id": "conv",
                "type": "corr_min",
                "theta": 0.20,
                "stage": "select",
                "params": {"variable": "v_aux"},
            },
            {
                "id": "mono",
                "type": "monotone_rank",
                "theta": 0.15,
                "stage": "holdout",
                "params": {"variable": "v_aux", "sign": 1},
            },
        ],
    }


def _bundle(
    roles: ScoreColumnRoles, *, delta: float = 0.0, beta_type: str = "corr_y"
) -> RestrictBundle:
    beta: dict[str, Any] = {"type": beta_type, "outcome": "y", "params": {}}
    if beta_type == "ols_coef":
        beta["params"] = {"controls": ["v_aux"]}
    return run_restrict(roles, _network(delta), beta)


def _row(payload: dict[str, Any], criterion: str) -> dict[str, Any]:
    rows = [r for r in payload["criteria"] if r["criterion"] == criterion]
    assert len(rows) == 1, payload
    return rows[0]


# ---------------------------------------------------------------- roles.criteria


def test_roles_criteria_accepts_engine_columns_and_overlap() -> None:
    roles = _roles(["m_track", "y", "v_aux"])
    assert roles.criteria == ["m_track", "y", "v_aux"]


@pytest.mark.parametrize("bad", ["V_star", "not_a_column", ""])
def test_roles_criteria_rejects_non_engine_columns(bad: str) -> None:
    with pytest.raises(ValidationError):
        ScoreColumnRoles.model_validate(
            {
                "measures": MEASURES,
                "aux": ["v_aux"],
                "outcome": "y",
                "diagnostic": ["V_star"],
                "criteria": [bad],
            }
        )


def test_roles_criteria_rejects_duplicates() -> None:
    with pytest.raises(ValidationError):
        _roles(["y", "y"])


def test_roles_criteria_omitted_from_dumps_when_empty() -> None:
    roles = _roles()
    assert roles.criteria == []
    assert "criteria" not in roles.model_dump()
    assert '"criteria"' not in roles.model_dump_json()
    declared = _roles(["m_track"])
    assert declared.model_dump()["criteria"] == ["m_track"]


# ------------------------------------------------------------- resolve_criteria


def test_resolve_criteria_includes_corr_y_outcome_first_and_dedupes() -> None:
    roles = _roles(["m_track", "y"])
    beta = BetaSpec(type="corr_y", outcome="y")
    assert resolve_criteria(roles, beta) == [
        ("y", "beta_outcome"),
        ("m_track", "declared"),
    ]


def test_resolve_criteria_skips_outcome_for_non_corr_y_beta() -> None:
    roles = _roles(["m_track"])
    beta = BetaSpec(type="ols_coef", outcome="y", params={"controls": ["v_aux"]})
    assert resolve_criteria(roles, beta) == [("m_track", "declared")]
    assert resolve_criteria(_roles(), beta) == []


# ------------------------------------------- (a) criterion self-consistency


def test_criterion_self_rejected_when_network_selects_against_it() -> None:
    frame = _frame()
    roles = _roles()
    bundle = _bundle(roles)
    out = criterion_self_consistency(frame, roles, bundle, delta=0.0)
    row = _row(out, "y")
    expected = float(np.corrcoef(frame["y"], frame["v_aux"])[0, 1]) - 0.20
    assert expected < 0.0
    assert row["source"] == "beta_outcome"
    assert row["slacks"]["conv"] == pytest.approx(expected, abs=1e-12)
    assert row["failing_select"] == ["conv"]
    assert row["self_rejected"] is True
    assert out["n_self_rejected"] == 1


def test_holdout_stage_failure_is_reported_separately() -> None:
    frame = _frame()
    roles = _roles()
    out = criterion_self_consistency(frame, roles, _bundle(roles), delta=0.0)
    row = _row(out, "y")
    assert row["failing_holdout"] == ["mono"]
    assert row["holdout_noncompliant"] is True
    # holdout-stage failures never feed self_rejected
    assert row["failing_select"] == ["conv"]


@pytest.mark.parametrize("delta", [0.0, 0.25])
@pytest.mark.parametrize("units_split", [False, True])
def test_menu_measure_criterion_matches_admission(
    delta: float, units_split: bool
) -> None:
    frame = _frame()
    roles = _roles(list(MEASURES))
    bundle = _bundle(roles, delta=delta)
    units = list(frame["unit_id"].iloc[::5]) if units_split else None
    ident = run_identify(frame, roles, bundle, holdout_units=units)
    out = criterion_self_consistency(
        frame,
        roles,
        bundle,
        delta=ident.delta,
        holdout_units=ident.holdout_units_used,
    )
    assert ident.M_star_select is not None
    for m in MEASURES:
        row = _row(out, m)
        assert row["self_rejected"] is (m not in ident.M_star_select), m
        # same evaluator, same frame as the engine's slack matrix
        for rid in ident.restriction_ids:
            assert row["slacks"][rid] == pytest.approx(
                float(ident.slacks.at[m, rid]), abs=1e-12
            )


def test_criterion_numeric_failure_is_null_not_crash() -> None:
    frame = _frame()
    roles = _roles(["w_const"])  # zero variance: correlation undefined
    out = criterion_self_consistency(frame, roles, _bundle(roles), delta=0.0)
    row = _row(out, "w_const")
    assert row["slacks"]["conv"] is None
    assert "conv" in row["errors"]
    assert row["self_rejected"] is None


def test_empty_r_criteria_have_no_slacks() -> None:
    frame = _frame()
    roles = _roles()
    bundle = run_restrict(
        roles,
        {"schema_version": "1", "empty_R": True, "restrictions": []},
        {"type": "corr_y", "outcome": "y"},
    )
    out = criterion_self_consistency(frame, roles, bundle, delta=0.0)
    row = _row(out, "y")
    assert row["slacks"] == {}
    assert row["self_rejected"] is False
    assert out["n_self_rejected"] == 0


# ------------------------------------------- (b) auxiliary ceiling / proxy


def _ceiling_network(extra: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    net = _network()
    net["restrictions"] += [
        {
            "id": "sign_neg",
            "type": "corr_sign",
            "theta": 0.0,
            "stage": "select",
            "params": {"variable": "v_aux", "sign": -1},
        },
        # not floors on an aux column: excluded from (b)
        {
            "id": "disc",
            "type": "corr_zero",
            "theta": 0.99,
            "stage": "select",
            "params": {"variable": "v_aux"},
        },
        {
            "id": "conv_y",
            "type": "corr_min",
            "theta": -1.0,
            "stage": "select",
            "params": {"variable": "y"},
        },
    ]
    net["restrictions"] += extra or []
    return net


def _ceiling_rows(
    payload: dict[str, Any], restriction: str, measure: str, criterion: str | None
) -> dict[str, Any]:
    rows = [
        r
        for r in payload["rows"]
        if r["restriction"] == restriction
        and r["measure"] == measure
        and r["criterion"] == criterion
    ]
    assert len(rows) == 1, (restriction, measure, criterion)
    return rows[0]


def _partial(x: np.ndarray, y: np.ndarray, v: np.ndarray) -> float:
    rxy, rxv, ryv = pearson_corr(x, y), pearson_corr(x, v), pearson_corr(y, v)
    return (rxy - rxv * ryv) / float(np.sqrt((1 - rxv**2) * (1 - ryv**2)))


def test_aux_proxy_exceeds_criterion_with_near_zero_partial() -> None:
    frame = _frame(n=400, slope=0.5)
    roles = _roles()
    bundle = run_restrict(roles, _ceiling_network(), {"type": "corr_y", "outcome": "y"})
    out = aux_ceiling(frame, roles, bundle)
    m, y, v = (frame[c].to_numpy(dtype=float) for c in ("m_proxy", "y", "v_aux"))

    row = _ceiling_rows(out, "conv", "m_proxy", "y")
    assert row["statistic"] == "pearson"
    assert row["assoc_measure"] == pytest.approx(pearson_corr(m, v), abs=1e-12)
    assert row["assoc_criterion"] == pytest.approx(pearson_corr(y, v), abs=1e-12)
    assert row["exceeds_criterion"] is True
    assert row["partial_corr"] == pytest.approx(_partial(m, y, v), abs=1e-12)
    assert abs(row["partial_corr"]) < 0.15

    track = _ceiling_rows(out, "conv", "m_track", "y")
    assert track["partial_corr"] > 0.9
    assert "m_proxy" in out["flagged_measures"]
    assert out["n_flagged_measures"] == len(out["flagged_measures"])


def test_aux_ceiling_uses_the_restrictions_own_statistic_and_sign() -> None:
    frame = _frame(n=400, slope=0.5)
    roles = _roles()
    bundle = run_restrict(roles, _ceiling_network(), {"type": "corr_y", "outcome": "y"})
    out = aux_ceiling(frame, roles, bundle)
    m, y, v = (frame[c].to_numpy(dtype=float) for c in ("m_proxy", "y", "v_aux"))

    mono = _ceiling_rows(out, "mono", "m_proxy", "y")
    assert mono["statistic"] == "spearman"
    assert mono["stage"] == "holdout"
    assert mono["assoc_measure"] == pytest.approx(spearman_corr(m, v), abs=1e-12)
    assert mono["assoc_criterion"] == pytest.approx(spearman_corr(y, v), abs=1e-12)

    neg = _ceiling_rows(out, "sign_neg", "m_proxy", "y")
    assert neg["sign"] == -1
    assert neg["assoc_measure"] == pytest.approx(-pearson_corr(m, v), abs=1e-12)
    assert neg["exceeds_criterion"] is False

    covered = {r["restriction"] for r in out["rows"]}
    assert covered == {"conv", "mono", "sign_neg"}  # corr_zero / non-aux excluded


def test_aux_ceiling_self_pair_and_undefined_partial_are_null() -> None:
    frame = _frame(n=400, slope=0.5)
    roles = _roles(["m_track", "v_aux"])
    bundle = run_restrict(roles, _network(), {"type": "corr_y", "outcome": "y"})
    out = aux_ceiling(frame, roles, bundle)

    self_pair = _ceiling_rows(out, "conv", "m_track", "m_track")
    assert self_pair["exceeds_criterion"] is None
    assert self_pair["partial_corr"] is None
    assert self_pair["reason"]

    on_v = _ceiling_rows(out, "conv", "m_proxy", "v_aux")
    assert on_v["assoc_criterion"] == pytest.approx(1.0)
    assert on_v["partial_corr"] is None
    assert on_v["reason"]


def test_aux_ceiling_without_criteria_reports_assoc_only() -> None:
    frame = _frame(n=400, slope=0.5)
    roles = _roles()
    bundle = _bundle(roles, beta_type="ols_coef")
    out = aux_ceiling(frame, roles, bundle)
    row = _ceiling_rows(out, "conv", "m_proxy", None)
    assert row["assoc_measure"] is not None
    assert row["assoc_criterion"] is None
    assert row["exceeds_criterion"] is None
    assert row["partial_corr"] is None
    assert out["flagged_measures"] == []


# ------------------------------------------- (c) near-threshold multiplicity


def _coverage(
    boundary: tuple[BoundaryRow, ...], p_hat: dict[str, float | None]
) -> CoverageResult:
    return CoverageResult(
        alpha=0.10,
        kappa=2.0,
        quantiles=(0.05, 0.95),
        band_L=0.1,
        band_U=0.2,
        replicates_total=200,
        replicates_nonempty=200,
        replicates_empty=0,
        replicates_degenerate=0,
        empty_replicate_rate=0.0,
        degenerate_replicate_rate=0.0,
        boundary=boundary,
        p_hat_m=p_hat,
        note=None,
    )


def test_near_threshold_unavailable_without_bootstrap() -> None:
    frame = _frame()
    roles = _roles()
    ident = run_identify(frame, roles, _bundle(roles))
    out = near_threshold(ident, None)
    assert out["available"] is False
    assert out["rows"] is None
    assert out["n_near_threshold_survivors"] is None
    assert "--n-boot" in out["note"]


def test_near_threshold_counts_only_boundary_survivors() -> None:
    frame = _frame()
    roles = _roles()
    ident = run_identify(frame, roles, _bundle(roles))
    assert ident.admissible == ["m_proxy"]
    cov = _coverage(
        (
            BoundaryRow("m_track", -0.6, 0.05, 2.0, False),
            BoundaryRow("m_proxy", 0.031, 0.040, 2.0, True),
            BoundaryRow("m_noise", -0.05, 0.04, 2.0, True),  # rejected, near
        ),
        {"m_track": 0.0, "m_proxy": 0.66, "m_noise": 0.3},
    )
    out = near_threshold(ident, cov)
    assert out["available"] is True
    assert out["n_survivors"] == 1
    assert out["n_near_threshold_survivors"] == 1
    assert out["near_threshold_survivors"] == ["m_proxy"]
    rows = {r["measure"]: r for r in out["rows"]}
    assert [r["measure"] for r in out["rows"]] == MEASURES
    assert rows["m_proxy"]["status"] == "admitted"
    assert rows["m_noise"]["status"] == "rejected"
    assert rows["m_proxy"]["p_hat"] == 0.66
    assert rows["m_proxy"]["margin"] == 0.031
    assert rows["m_proxy"]["se"] == 0.040
    assert rows["m_proxy"]["boundary"] is True
    v = rows["m_proxy"]["verdict"]
    assert v.startswith("admitted; admitted in 66% of 200 non-empty resamples")
    assert "near threshold" in v
    assert "near threshold" not in rows["m_track"]["verdict"]
    assert out["caveat"]


def test_near_threshold_handles_null_p_hat_and_missing_boundary() -> None:
    frame = _frame()
    roles = _roles()
    ident = run_identify(frame, roles, _bundle(roles))
    out = near_threshold(ident, _coverage((), {m: None for m in MEASURES}))
    rows = {r["measure"]: r for r in out["rows"]}
    assert rows["m_proxy"]["margin"] is None
    assert rows["m_proxy"]["boundary"] is None
    assert "unavailable" in rows["m_proxy"]["verdict"]
    assert out["n_near_threshold_survivors"] == 0


def test_near_threshold_reads_real_coverage_without_new_resampling() -> None:
    frame = _frame(n=60, slope=0.5)
    roles = _roles()
    bundle = _bundle(roles)
    ident = run_identify(frame, roles, bundle)
    boot = run_bootstrap(frame, roles, bundle, n_boot=40, seed=3)
    cov = compute_coverage(boot, frame, roles, bundle)
    out = near_threshold(ident, cov)
    by_m = {r.measure: r for r in cov.boundary}
    for row in out["rows"]:
        assert row["p_hat"] == cov.p_hat_m[row["measure"]]
        assert row["boundary"] == by_m[row["measure"]].boundary
    expected = [m for m in ident.admissible if by_m[m].boundary]
    assert out["near_threshold_survivors"] == expected
