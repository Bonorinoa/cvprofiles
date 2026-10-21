"""Report-only screen diagnostics (logs/DECISIONS.md 2026-10-19, D1–D9).

Three descriptions of the screen itself, embedded in ``report.json`` under
``screen_diagnostics``. None of them rejects, admits, re-thresholds, or
touches M*, [L,U], slacks/admissible/range/coverage artifacts, or the freeze
preimage. Pure functions; no RNG.

(a) Criterion self-consistency — slack of each criterion column under every
    restriction, on the frame the engine uses for that restriction's stage
    (full frame legacy; train for select / hold for holdout under a
    units-split). ``self_rejected`` = the criterion would not survive its
    own select-stage screen.
(b) Auxiliary ceiling / proxy flag — for each corr_min / corr_sign /
    monotone_rank floor on an aux column V: assoc_r(m,V) beside the
    criterion's assoc_r(c,V) (the restriction's own statistic and sign),
    plus the Pearson partial corr(m, c | V). ``exceeds_criterion`` is a
    description, not a verdict.
(c) Near-threshold multiplicity — reads the EXISTING CoverageResult (no
    second resampling loop): per-measure p̂_m and coverage's boundary flag
    as-is, the count of survivors with |margin| <= kappa·SE, and a
    plain-language verdict line. No categorical p̂ cutoffs.

Criteria = the β outcome when ``beta.type == "corr_y"`` (β(m) = corr(m, y)
makes y the criterion), plus ``roles.criteria`` declarations. Numeric
failures inside a cell become null + reason; they never abort a run.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any

import pandas as pd

from cvprofiles.identify.pipeline import IdentifyResult
from cvprofiles.identify.slacks import (
    SlackError,
    evaluate_slack,
    pearson_corr,
    spearman_corr,
)
from cvprofiles.inference.coverage import CoverageResult
from cvprofiles.restrict.pipeline import RestrictBundle
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import RestrictionSpec
from cvprofiles.schemas.scores import ScoreColumnRoles

FRAME_RULE = (
    "full frame when no units-split; under a units-split, select-stage "
    "restrictions on the train frame and holdout-stage restrictions on the "
    "hold frame (the engine's own slack-matrix rule)"
)


def resolve_criteria(
    roles: ScoreColumnRoles, beta: BetaSpec
) -> list[tuple[str, str]]:
    """Return ``[(column, source)]``: corr_y outcome first, then declarations."""
    out: list[tuple[str, str]] = []
    if beta.type == "corr_y":
        out.append((beta.outcome, "beta_outcome"))
    seen = {c for c, _ in out}
    for c in roles.criteria:
        if c not in seen:
            out.append((c, "declared"))
            seen.add(c)
    return out


def _is_holdout(r: RestrictionSpec) -> bool:
    return r.stage == "holdout"


def _stage_frames(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    holdout_units: Sequence[str] | None,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(select_frame, holdout_frame) under the engine's frame rule."""
    if not holdout_units:
        return frame, frame
    ids = frame[roles.unit_id].astype(str)
    hold = ids.isin([str(u) for u in holdout_units])
    return frame[~hold], frame[hold]


def _verdict(failing: list[str], unknown: list[str]) -> bool | None:
    if failing:
        return True
    if unknown:
        return None
    return False


def criterion_self_consistency(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    bundle: RestrictBundle,
    *,
    delta: float,
    holdout_units: Sequence[str] | None = None,
) -> dict[str, Any]:
    """(a) Would each criterion survive the screen used to rank against it?"""
    select_frame, hold_frame = _stage_frames(frame, roles, holdout_units)
    rows: list[dict[str, Any]] = []
    for col, source in resolve_criteria(roles, bundle.beta):
        slacks: dict[str, float | None] = {}
        errors: dict[str, str] = {}
        failing_select: list[str] = []
        failing_holdout: list[str] = []
        unknown_select: list[str] = []
        unknown_holdout: list[str] = []
        for r in bundle.network.restrictions:
            sub = hold_frame if _is_holdout(r) else select_frame
            try:
                s: float | None = evaluate_slack(
                    sub[col].to_numpy(dtype=float), sub, r
                )
            except SlackError as exc:
                s = None
                errors[r.id] = str(exc)
            slacks[r.id] = s
            if s is None:
                (unknown_holdout if _is_holdout(r) else unknown_select).append(r.id)
            elif s < -delta:
                (failing_holdout if _is_holdout(r) else failing_select).append(r.id)
        rows.append(
            {
                "criterion": col,
                "source": source,
                "is_menu_measure": col in roles.measures,
                "slacks": slacks,
                "errors": errors,
                "failing_select": failing_select,
                "failing_holdout": failing_holdout,
                "self_rejected": _verdict(failing_select, unknown_select),
                "holdout_noncompliant": _verdict(failing_holdout, unknown_holdout),
            }
        )
    return {
        "criteria": rows,
        "n_self_rejected": sum(1 for r in rows if r["self_rejected"] is True),
        "delta": float(delta),
        "frame_rule": FRAME_RULE,
        "note": (
            "self_rejected = the criterion fails a select-stage restriction "
            "(slack < -delta): a measure that tracked it perfectly would be "
            "rejected. Report-only; never changes M* or [L,U]."
        ),
    }


CEILING_TYPES = ("corr_min", "corr_sign", "monotone_rank")


def _assoc(
    x: pd.Series, v: pd.Series, statistic: str, sign: float
) -> tuple[float | None, str | None]:
    xa, va = x.to_numpy(dtype=float), v.to_numpy(dtype=float)
    try:
        stat = spearman_corr(xa, va) if statistic == "spearman" else pearson_corr(xa, va)
    except SlackError as exc:
        return None, str(exc)
    return sign * stat, None


def _partial_corr(
    x: pd.Series, c: pd.Series, v: pd.Series
) -> tuple[float | None, str | None]:
    """First-order Pearson partial corr(x, c | v); null when undefined."""
    xa, ca, va = (s.to_numpy(dtype=float) for s in (x, c, v))
    try:
        rxc, rxv, rcv = pearson_corr(xa, ca), pearson_corr(xa, va), pearson_corr(ca, va)
    except SlackError as exc:
        return None, str(exc)
    denom = (1.0 - rxv**2) * (1.0 - rcv**2)
    if denom <= 1e-12:
        return None, "partial correlation undefined (|corr with V| = 1)"
    out = (rxc - rxv * rcv) / math.sqrt(denom)
    if not math.isfinite(out):
        return None, "partial correlation non-finite"
    return float(out), None


def aux_ceiling(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    bundle: RestrictBundle,
    *,
    holdout_units: Sequence[str] | None = None,
) -> dict[str, Any]:
    """(b) Does a measure track the auxiliary more than the criterion does?"""
    select_frame, hold_frame = _stage_frames(frame, roles, holdout_units)
    criteria = [c for c, _ in resolve_criteria(roles, bundle.beta)]
    rows: list[dict[str, Any]] = []
    flagged: set[str] = set()
    for r in bundle.network.restrictions:
        var = r.params.get("variable")
        if r.type not in CEILING_TYPES or var not in roles.aux:
            continue
        sub = hold_frame if _is_holdout(r) else select_frame
        statistic = "spearman" if r.type == "monotone_rank" else "pearson"
        sign = float(r.params.get("sign", 1))
        v = sub[var]
        crit_assoc = {c: _assoc(sub[c], v, statistic, sign) for c in criteria}
        base = {
            "restriction": r.id,
            "type": r.type,
            "variable": var,
            "stage": "holdout" if _is_holdout(r) else "select",
            "statistic": statistic,
            "sign": int(sign),
        }
        for m in roles.measures:
            a_m, err_m = _assoc(sub[m], v, statistic, sign)
            if not criteria:
                rows.append(
                    {
                        **base,
                        "measure": m,
                        "assoc_measure": a_m,
                        "criterion": None,
                        "assoc_criterion": None,
                        "exceeds_criterion": None,
                        "partial_corr": None,
                        "reason": err_m,
                    }
                )
                continue
            for c in criteria:
                a_c, err_c = crit_assoc[c]
                exceeds: bool | None = None
                partial: float | None = None
                reason = err_m or err_c
                if m == c:
                    reason = "self-pair (measure is the criterion)"
                else:
                    if a_m is not None and a_c is not None:
                        exceeds = a_m > a_c
                    partial, err_p = _partial_corr(sub[m], sub[c], v)
                    reason = reason or err_p
                if exceeds:
                    flagged.add(m)
                rows.append(
                    {
                        **base,
                        "measure": m,
                        "assoc_measure": a_m,
                        "criterion": c,
                        "assoc_criterion": a_c,
                        "exceeds_criterion": exceeds,
                        "partial_corr": partial,
                        "reason": reason,
                    }
                )
    flagged_measures = [m for m in roles.measures if m in flagged]
    return {
        "rows": rows,
        "flagged_measures": flagged_measures,
        "n_flagged_measures": len(flagged_measures),
        "frame_rule": FRAME_RULE,
        "reading_rule": (
            "exceeds_criterion is a description, not a verdict: a valid measure "
            "can beat a noisy criterion (attenuation). The auxiliary-proxy "
            "signature is high aux association together with near-zero "
            "partial_corr (Pearson partial corr(m, criterion | V))."
        ),
    }


NEAR_THRESHOLD_CAVEAT = (
    "margin/SE/boundary are coverage.json's locked definitions (amendment "
    "cb566c8): margin = min slack over ALL restrictions on the pooled full "
    "frame, without delta; p_hat is pooled, select-stage only. Admission uses "
    "select-stage restrictions with tolerance delta (train frame under a "
    "units-split), so with delta > 0, holdout-stage restrictions, or a "
    "units-split the margin is not exactly the admission distance."
)


def _verdict_line(
    status: str,
    p_hat: float | None,
    n_nonempty: int,
    margin: float | None,
    se: float | None,
    kappa: float,
    boundary: bool | None,
) -> str:
    if p_hat is None:
        line = f"{status}; admission frequency unavailable (no non-empty resamples)"
    else:
        line = f"{status}; admitted in {p_hat:.0%} of {n_nonempty} non-empty resamples"
    if boundary and margin is not None and se is not None:
        line += (
            f"; near threshold (|margin| {abs(margin):.3f} <= {kappa:g}·SE, "
            f"SE {se:.3f})"
        )
    return line


def near_threshold(
    identify: IdentifyResult, coverage: CoverageResult | None
) -> dict[str, Any]:
    """(c) How many survivors sit within kappa·SE of their threshold?"""
    if coverage is None:
        return {
            "available": False,
            "kappa": None,
            "replicates_nonempty": None,
            "rows": None,
            "n_survivors": len(identify.admissible),
            "n_near_threshold_survivors": None,
            "near_threshold_survivors": None,
            "caveat": NEAR_THRESHOLD_CAVEAT,
            "note": (
                "bootstrap off: enable --n-boot (run_profile n_boot >= 1) for "
                "admission frequencies and near-threshold counts"
            ),
        }
    by_m = {row.measure: row for row in coverage.boundary}
    rows: list[dict[str, Any]] = []
    near: list[str] = []
    for m in identify.measures:
        status = "admitted" if m in identify.admissible else "rejected"
        b = by_m.get(m)
        margin = b.margin if b is not None else None
        se = b.se if b is not None else None
        boundary = b.boundary if b is not None else None
        p_hat = coverage.p_hat_m.get(m)
        if status == "admitted" and boundary:
            near.append(m)
        rows.append(
            {
                "measure": m,
                "status": status,
                "p_hat": p_hat,
                "margin": margin,
                "se": se,
                "boundary": boundary,
                "verdict": _verdict_line(
                    status,
                    p_hat,
                    coverage.replicates_nonempty,
                    margin,
                    se,
                    coverage.kappa,
                    boundary,
                ),
            }
        )
    return {
        "available": True,
        "kappa": coverage.kappa,
        "replicates_nonempty": coverage.replicates_nonempty,
        "rows": rows,
        "n_survivors": len(identify.admissible),
        "n_near_threshold_survivors": len(near),
        "near_threshold_survivors": near,
        "caveat": NEAR_THRESHOLD_CAVEAT,
        "note": (
            "p_hat is descriptive (share of non-empty resamples admitting m), "
            "not a coverage statement. Report-only; never changes M* or [L,U]."
        ),
    }


def screen_diagnostics_payload(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    bundle: RestrictBundle,
    identify: IdentifyResult,
    coverage: CoverageResult | None,
) -> dict[str, Any]:
    """``report.json["screen_diagnostics"]`` — (a), (b), (c) in one block."""
    return {
        "schema_version": "1",
        "purpose": "report_only_screen_diagnostics",
        "criteria": [
            {"column": c, "source": src}
            for c, src in resolve_criteria(roles, bundle.beta)
        ],
        "criterion_self_consistency": criterion_self_consistency(
            frame,
            roles,
            bundle,
            delta=identify.delta,
            holdout_units=identify.holdout_units_used,
        ),
        "aux_ceiling": aux_ceiling(
            frame, roles, bundle, holdout_units=identify.holdout_units_used
        ),
        "near_threshold": near_threshold(identify, coverage),
        "headline_note": (
            "Report-only: these diagnostics describe the screen. They never "
            "reject, admit, or re-threshold; M*, [L,U], and run_id are unchanged."
        ),
    }
