"""IDENTIFY pipeline: slacks → M* → β(m) → headline [L,U]=min/max B*."""

from __future__ import annotations

import json
import math
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from cvprofiles.identify.beta_fn import evaluate_beta
from cvprofiles.identify.slacks import SlackError, slack_matrix
from cvprofiles.restrict.pipeline import RestrictBundle
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.scores import ScoreColumnRoles


class IdentifyError(ValueError):
    """Loud IDENTIFY failure (not empty M* — that is success)."""


@dataclass(frozen=True)
class IdentifyResult:
    """IDENTIFY outputs for one frozen run."""

    slacks: pd.DataFrame  # measures × restrictions
    admissible: list[str]
    rejected: dict[str, list[str]]  # measure → failing restriction ids
    beta_values: dict[str, float]  # all measures
    range_L: float | None
    range_U: float | None
    empty: bool
    point_id: bool
    delta: float
    measures: list[str]
    restriction_ids: list[str]
    # P4 (docs/12 2026-08-08): per-measure failing holdout-stage restriction
    # ids. None when the network has no holdout-stage restrictions (legacy
    # runs unchanged); dict mapping measure -> failing holdout ids otherwise.
    holdout_verdict: dict[str, list[str]] | None = None
    # P4b (docs/12 2026-08-08): units-split composition. Always present —
    # legacy (no split) sets both to ``admissible`` (decision #9).
    holdout_units_used: list[str] | None = None
    M_star_select: list[str] | None = None
    M_star_robust: list[str] | None = None


def normalize_holdout_units(
    units: Sequence[str] | None,
    frame: pd.DataFrame,
    unit_id_col: str,
) -> list[str] | None:
    """Normalize and validate a user-supplied holdout unit list.

    ``None`` / empty ⇒ ``None`` (no units-split; legacy path, ``config={}``
    bit-stable). A non-empty list is validated (every id present, train and
    hold frames each >= 2 rows so registry evaluators can run) and returned
    as a sorted-unique list so list order can never fork ``run_id``.
    """
    if units is None:
        return None
    seq = [str(u) for u in units]
    if not seq:
        return None
    all_ids = set(frame[unit_id_col].astype(str))
    unknown = [u for u in seq if u not in all_ids]
    if unknown:
        raise IdentifyError(f"holdout units not in scores frame: {unknown}")
    norm = sorted(set(seq))
    if len(norm) < 2:
        raise IdentifyError(
            "holdout frame must have at least 2 rows (evaluators require n >= 2)"
        )
    train_ids = all_ids - set(norm)
    if len(train_ids) < 2:
        raise IdentifyError("empty train frame after holdout split (need >= 2 rows)")
    return norm


def run_identify(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    restrict: RestrictBundle | NetworkConfig,
    *,
    beta_bundle: RestrictBundle | None = None,
    delta_override: float | None = None,
    holdout_units: Sequence[str] | None = None,
    include_holdout_verdict: bool = True,
) -> IdentifyResult:
    """Compute slacks, M*, β image, and min/max range.

    Parameters
    ----------
    frame:
        SCORE frame (must include measures, aux, outcome used by R and β).
    roles:
        Column roles (measures list defines menu order).
    restrict:
        Either a RestrictBundle (preferred) or NetworkConfig.
    beta_bundle:
        Required if ``restrict`` is only a NetworkConfig; otherwise taken from bundle.
    delta_override:
        v2.0 δ-grid tolerance override (docs/12, 2026-08-05). When not None,
        replaces the bundle/network δ for this call only — an IDENTIFY-side
        admission rule that never touches network_hash/beta_hash. Must be
        finite and >= 0. Default None keeps the declared δ (bit-identical).
    holdout_units:
        P4b units-split list. None/[] ⇒ legacy (no split). Non-empty ⇒
        select-stage admission on the train frame, compliance on the hold
        frame, headline = M*_robust (docs/12 2026-08-08).
    include_holdout_verdict:
        P4b lock §3: bootstrap passes False (selection-only band; holdout
        verdict is a full-sample point finding outside the band).
    """
    if isinstance(restrict, RestrictBundle):
        network = restrict.network
        beta = restrict.beta
        delta = float(restrict.delta)
    else:
        if beta_bundle is None:
            raise IdentifyError("beta_bundle required when restrict is NetworkConfig only")
        network = restrict
        beta = beta_bundle.beta
        delta = float(network.delta)

    if delta_override is not None:
        override = float(delta_override)
        if not math.isfinite(override) or override < 0.0:
            raise IdentifyError("delta_override must be finite and >= 0")
        delta = override

    measures = list(roles.measures)
    if not measures:
        raise IdentifyError("no measures in roles")

    norm_units = normalize_holdout_units(holdout_units, frame, roles.unit_id)

    # P4 (docs/12 2026-08-08): slacks are computed for ALL restrictions, but
    # M* admission uses select-stage restrictions only (None or "select").
    # Holdout-stage failures are findings, never selection rejections.
    select_restrs = [
        r for r in network.restrictions if r.stage is None or r.stage == "select"
    ]
    holdout_restrs = [r for r in network.restrictions if r.stage == "holdout"]
    select_ids = [r.id for r in select_restrs]
    holdout_ids = [r.id for r in holdout_restrs]

    if norm_units is None:
        # ---- legacy path (P4a): single frame, select-only admission ----
        try:
            slacks = slack_matrix(frame, measures, list(network.restrictions))
        except SlackError as exc:
            raise IdentifyError(str(exc)) from exc

        admissible: list[str] = []
        rejected: dict[str, list[str]] = {}
        for m in measures:
            failing: list[str] = []
            for rid in select_ids:
                slack = pd.to_numeric(slacks.at[m, rid], errors="raise")
                if float(slack) < -delta:
                    failing.append(str(rid))
            if failing:
                rejected[m] = failing
            else:
                admissible.append(m)

        holdout_verdict: dict[str, list[str]] | None = None
        if include_holdout_verdict and holdout_ids:
            holdout_verdict = {}
            for m in measures:
                failing_h: list[str] = []
                for rid in holdout_ids:
                    slack = pd.to_numeric(slacks.at[m, rid], errors="raise")
                    if float(slack) < -delta:
                        failing_h.append(str(rid))
                if failing_h:
                    holdout_verdict[m] = failing_h

        M_star_select = list(admissible)
        M_star_robust = list(admissible)
    else:
        # ---- units-split path (P4b): select on train, compliance on hold ----
        ids = frame[roles.unit_id].astype(str)
        train = frame[~ids.isin(norm_units)].copy()
        hold = frame[ids.isin(norm_units)].copy()
        try:
            slacks_train = slack_matrix(train, measures, select_restrs)
            slacks_hold_all = slack_matrix(hold, measures, list(network.restrictions))
        except SlackError as exc:
            raise IdentifyError(str(exc)) from exc

        # Composite slacks: select-stage columns from the train frame,
        # holdout-stage columns from the hold frame (docs/12 P4b #6).
        slacks = pd.DataFrame(index=list(measures))
        for r in network.restrictions:
            src = slacks_hold_all if r.stage == "holdout" else slacks_train
            slacks[r.id] = src[r.id]

        M_star_select = [
            m
            for m in measures
            if all(
                float(pd.to_numeric(slacks_train.at[m, rid], errors="raise"))
                >= -delta
                for rid in select_ids
            )
        ]
        # Compliance on the hold frame: ALL restrictions (select + holdout).
        holdout_verdict = {}
        compliant: dict[str, bool] = {}
        for m in measures:
            failing_comp: list[str] = []
            for rid in slacks_hold_all.columns:
                slack = pd.to_numeric(slacks_hold_all.at[m, rid], errors="raise")
                if float(slack) < -delta:
                    failing_comp.append(str(rid))
            if failing_comp:
                holdout_verdict[m] = failing_comp
            compliant[m] = not failing_comp
        if not include_holdout_verdict:
            holdout_verdict = None

        M_star_robust = [m for m in M_star_select if compliant[m]]
        admissible = list(M_star_robust)
        rejected = {}
        for m in measures:
            if m not in M_star_select:
                rejected[m] = [
                    str(rid)
                    for rid in select_ids
                    if float(pd.to_numeric(slacks_train.at[m, rid], errors="raise"))
                    < -delta
                ]

    beta_values: dict[str, float] = {}
    try:
        for m in measures:
            beta_values[m] = evaluate_beta(frame, m, beta)
    except SlackError as exc:
        raise IdentifyError(str(exc)) from exc

    empty = len(admissible) == 0
    if empty:
        L: float | None = None
        U: float | None = None
    else:
        b_star = [beta_values[m] for m in admissible]
        L = float(min(b_star))
        U = float(max(b_star))

    return IdentifyResult(
        slacks=slacks,
        admissible=admissible,
        rejected=rejected,
        beta_values=beta_values,
        range_L=L,
        range_U=U,
        empty=empty,
        point_id=(len(admissible) == 1),
        delta=delta,
        measures=measures,
        restriction_ids=[r.id for r in network.restrictions],
        holdout_verdict=holdout_verdict,
        holdout_units_used=norm_units,
        M_star_select=M_star_select,
        M_star_robust=M_star_robust,
    )


def write_identify_artifacts(
    result: IdentifyResult,
    out_dir: Path | str,
) -> dict[str, Path]:
    """Write slacks, admissible, beta_values, range under out_dir."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}

    slacks_csv = out / "slacks.csv"
    result.slacks.to_csv(slacks_csv, index_label="measure")
    paths["slacks.csv"] = slacks_csv
    try:
        slacks_pq = out / "slacks.parquet"
        # reset index for parquet friendliness
        result.slacks.reset_index(names="measure").to_parquet(slacks_pq, index=False)
        paths["slacks.parquet"] = slacks_pq
    except Exception as exc:  # parquet backend quirks: CSV remains authoritative
        print(
            f"warning: slacks.parquet not written ({exc}); slacks.csv is authoritative",
            file=sys.stderr,
        )

    holdout_block: dict[str, Any] | None = None
    if result.holdout_units_used is not None or result.holdout_verdict is not None:
        holdout_block = {
            "units": result.holdout_units_used,
            "select_frame": "train" if result.holdout_units_used is not None else None,
            "holdout_frame": "holdout" if result.holdout_units_used is not None else None,
            "verdict": result.holdout_verdict,
        }
    admissible_payload = {
        "M_star": result.admissible,
        "M_star_select": result.M_star_select,
        "M_star_robust": result.M_star_robust,
        "rejected": result.rejected,
        "empty": result.empty,
        "point_id": result.point_id,
        "delta": result.delta,
        "n_menu": len(result.measures),
        "n_admissible": len(result.admissible),
        "holdout": holdout_block,
    }
    adm_path = out / "admissible.json"
    adm_path.write_text(json.dumps(admissible_payload, indent=2, sort_keys=True) + "\n")
    paths["admissible.json"] = adm_path

    beta_payload = {
        "beta_values": result.beta_values,
        "admissible_flag": {
            m: (m in result.admissible) for m in result.measures
        },
    }
    beta_path = out / "beta_values.json"
    beta_path.write_text(json.dumps(beta_payload, indent=2, sort_keys=True) + "\n")
    paths["beta_values.json"] = beta_path

    range_payload: dict[str, Any] = {
        "L": result.range_L,
        "U": result.range_U,
        "empty": result.empty,
        "point_id": result.point_id,
        "method": "min_max_B_star",
        "bootstrap": None,
        "note": (
            "range is min/max of beta on M*; bootstrap band is additive "
            "metadata (bootstrap.json) when enabled"
        ),
    }
    range_path = out / "range.json"
    range_path.write_text(json.dumps(range_payload, indent=2, sort_keys=True) + "\n")
    paths["range.json"] = range_path
    return paths
