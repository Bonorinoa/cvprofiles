"""IDENTIFY pipeline: slacks → M* → β(m) → [L,U]=min/max B* (no bootstrap)."""

from __future__ import annotations

import json
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


def run_identify(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    restrict: RestrictBundle | NetworkConfig,
    *,
    beta_bundle: RestrictBundle | None = None,
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

    measures = list(roles.measures)
    if not measures:
        raise IdentifyError("no measures in roles")

    try:
        slacks = slack_matrix(frame, measures, list(network.restrictions))
    except SlackError as exc:
        raise IdentifyError(str(exc)) from exc

    admissible: list[str] = []
    rejected: dict[str, list[str]] = {}
    for m in measures:
        failing = [
            rid
            for rid in slacks.columns
            if float(slacks.at[m, rid]) < -delta
        ]
        if failing:
            rejected[m] = failing
        else:
            admissible.append(m)

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
    except Exception:
        pass  # CSV is enough if parquet backend quirks

    admissible_payload = {
        "M_star": result.admissible,
        "rejected": result.rejected,
        "empty": result.empty,
        "point_id": result.point_id,
        "delta": result.delta,
        "n_menu": len(result.measures),
        "n_admissible": len(result.admissible),
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
        "note": "v1.0 range is min/max of beta on M*; bootstrap deferred to v1.1",
    }
    range_path = out / "range.json"
    range_path.write_text(json.dumps(range_payload, indent=2, sort_keys=True) + "\n")
    paths["range.json"] = range_path
    return paths
