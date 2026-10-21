"""RESTRICT pipeline: parse network + beta, bind columns, hash pieces."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any

import pandas as pd
import yaml
from pydantic import ValidationError

from cvprofiles.freeze import hash_beta, hash_beta_estimates, hash_network
from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.beta_estimates import (
    CANONICAL_COLUMNS,
    REQUIRED_COLUMNS,
    BetaEstimateRow,
    BetaEstimates,
)
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.scores import ScoreColumnRoles


class RestrictError(ValueError):
    """Loud RESTRICT failure (parse / column binding)."""


@dataclass(frozen=True)
class RestrictBundle:
    """Parsed and column-bound RESTRICT outputs (no slacks)."""

    network: NetworkConfig
    beta: BetaSpec
    network_hash: str
    beta_hash: str
    roles: ScoreColumnRoles
    delta: float
    # DECISIONS 2026-10-20: bring-your-own β table, present iff beta.type is
    # "external". Default None keeps every existing bundle unchanged.
    beta_estimates: BetaEstimates | None = None


def load_network(source: Path | str | NetworkConfig | dict[str, Any]) -> NetworkConfig:
    """Load network from YAML path, mapping, or model.

    All invalid inputs raise ``RestrictError`` (including pydantic ValidationError
    on dict/YAML paths) so callers never see a raw schema exception from IO.
    """
    if isinstance(source, NetworkConfig):
        return source
    if isinstance(source, dict):
        try:
            return NetworkConfig.model_validate(source)
        except Exception as exc:  # pydantic ValidationError
            raise RestrictError(f"invalid network schema: {exc}") from exc
    p = Path(source)
    if not p.is_file():
        raise RestrictError(f"network file not found: {p}")
    try:
        raw = yaml.safe_load(p.read_text())
    except yaml.YAMLError as exc:
        raise RestrictError(f"invalid network YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise RestrictError("network YAML must be a mapping at top level")
    try:
        return NetworkConfig.model_validate(raw)
    except Exception as exc:  # pydantic ValidationError
        raise RestrictError(f"invalid network schema: {exc}") from exc


def load_beta(source: Path | str | BetaSpec | dict[str, Any]) -> BetaSpec:
    """Load beta from YAML path, mapping, or model.

    All invalid inputs raise ``RestrictError`` (including pydantic ValidationError).
    """
    if isinstance(source, BetaSpec):
        return source
    if isinstance(source, dict):
        try:
            return BetaSpec.model_validate(source)
        except Exception as exc:
            raise RestrictError(f"invalid beta schema: {exc}") from exc
    p = Path(source)
    if not p.is_file():
        raise RestrictError(f"beta file not found: {p}")
    try:
        raw = yaml.safe_load(p.read_text())
    except yaml.YAMLError as exc:
        raise RestrictError(f"invalid beta YAML: {exc}") from exc
    if not isinstance(raw, dict):
        raise RestrictError("beta YAML must be a mapping at top level")
    try:
        return BetaSpec.model_validate(raw)
    except Exception as exc:
        raise RestrictError(f"invalid beta schema: {exc}") from exc


def _cell(value: Any) -> Any:
    """CSV cell → Python scalar; missing (NaN / None / pd.NA) → None."""
    if hasattr(value, "item"):
        value = value.item()
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def load_beta_estimates(
    source: Path | str | pd.DataFrame | BetaEstimates,
    measures: list[str],
) -> BetaEstimates:
    """Load and validate a bring-your-own β table against the menu.

    Rows must equal the menu exactly; unknown columns, missing required
    columns, non-finite values, ``se <= 0``, ``df <= 0`` and
    ``n_clusters < 2`` all raise ``RestrictError``. CSV is read with the same
    round-trip float parser as scores so the hash re-verifies from bytes.
    """
    if isinstance(source, BetaEstimates):
        if set(source.rows) != set(measures):
            raise RestrictError("beta_estimates rows do not match the menu")
        return source
    if isinstance(source, pd.DataFrame):
        df = source
    else:
        p = Path(source)
        if not p.is_file():
            raise RestrictError(f"beta_estimates file not found: {p}")
        suffix = p.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(p, float_precision="round_trip")
        elif suffix in {".parquet", ".pq"}:
            df = pd.read_parquet(p)
        else:
            raise RestrictError(
                f"unsupported beta_estimates format: {suffix} (use .csv or .parquet)"
            )

    cols = [str(c) for c in df.columns]
    unknown = [c for c in cols if c not in CANONICAL_COLUMNS]
    if unknown:
        raise RestrictError(f"unknown column(s) in beta_estimates: {unknown}")
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in cols]
    if missing_cols:
        raise RestrictError(f"beta_estimates missing required column(s): {missing_cols}")

    names = [str(_cell(v)) for v in df["measure"]]
    dups = sorted({n for n in names if names.count(n) > 1})
    if dups:
        raise RestrictError(f"duplicate measure rows in beta_estimates: {dups}")
    extra = [n for n in names if n not in measures]
    if extra:
        raise RestrictError(f"beta_estimates measure(s) not in the menu: {extra}")
    absent = [m for m in measures if m not in names]
    if absent:
        raise RestrictError(f"beta_estimates missing menu measure(s): {absent}")

    rows: dict[str, BetaEstimateRow] = {}
    for record in df.to_dict(orient="records"):
        data = {str(k): _cell(v) for k, v in record.items()}
        data["measure"] = str(data["measure"])
        try:
            row = BetaEstimateRow.model_validate(data)
        except ValidationError as exc:
            detail = "; ".join(
                f"{'.'.join(str(x) for x in e['loc'])}: {e['msg']}" for e in exc.errors()
            )
            raise RestrictError(
                f"beta_estimates row {data['measure']!r}: {detail}"
            ) from exc
        rows[row.measure] = row

    present = tuple(c for c in CANONICAL_COLUMNS if c in cols)
    unhashed = BetaEstimates(
        rows={m: rows[m] for m in measures}, columns=present, estimates_hash=""
    )
    return replace(
        unhashed,
        estimates_hash=hash_beta_estimates(unhashed.canonical_rows(), present),
    )


def _available_columns(roles: ScoreColumnRoles) -> set[str]:
    cols = {roles.unit_id, *roles.measures, *roles.aux, *roles.diagnostic}
    if roles.outcome is not None:
        cols.add(roles.outcome)
    return cols


def _bind_network_columns(network: NetworkConfig, roles: ScoreColumnRoles) -> None:
    """Fail loud if restriction params reference missing columns."""
    available = _available_columns(roles)
    engine_cols = {roles.unit_id, *roles.measures, *roles.aux}
    if roles.outcome is not None:
        engine_cols.add(roles.outcome)

    for r in network.restrictions:
        t = r.type
        p = r.params
        if t in ("corr_min", "corr_sign", "corr_zero", "monotone_rank"):
            var = p.get("variable")
            if not isinstance(var, str) or not var:
                raise RestrictError(f"{r.id}: {t} requires params.variable")
            if var not in available:
                raise RestrictError(
                    f"{r.id}: variable {var!r} not found in SCORE columns"
                )
            # Aux/outcome/diagnostic/measure all allowed as correlation partners;
            # must not be a measure being tested against itself silently later — OK.
            if var not in engine_cols and var not in roles.diagnostic:
                raise RestrictError(
                    f"{r.id}: variable {var!r} not in engine or diagnostic columns"
                )
        elif t == "mean_order":
            group = p.get("group")
            if not isinstance(group, str) or not group:
                raise RestrictError(f"{r.id}: mean_order requires params.group")
            if group not in available:
                raise RestrictError(
                    f"{r.id}: group column {group!r} not found in SCORE columns"
                )
        elif t == "rank_agree":
            ref = p.get("ref_measure")
            if not isinstance(ref, str) or not ref:
                raise RestrictError(f"{r.id}: rank_agree requires params.ref_measure")
            if ref not in roles.measures and ref not in available:
                raise RestrictError(
                    f"{r.id}: ref_measure {ref!r} not found in SCORE columns"
                )
        # stability: no required external column at bind time (split policy later)


def _bind_beta_columns(beta: BetaSpec, roles: ScoreColumnRoles) -> None:
    if beta.type == "external":
        # DECISIONS 2026-10-20 D5: outcome is a descriptive label (the user's
        # model outcome), never bound to a SCORE column. No params accepted.
        if beta.params:
            raise RestrictError(
                f"external beta takes no params (got {sorted(beta.params)})"
            )
        return
    available = _available_columns(roles)
    if beta.outcome not in available:
        raise RestrictError(
            f"beta.outcome {beta.outcome!r} not found in SCORE columns"
        )
    if beta.type == "ols_coef":
        controls = beta.params.get("controls", [])
        if controls is None:
            controls = []
        if not isinstance(controls, list):
            raise RestrictError("ols_coef params.controls must be a list")
        for c in controls:
            if c not in available:
                raise RestrictError(
                    f"ols_coef control {c!r} not found in SCORE columns"
                )
    if beta.type == "diff_means":
        group = beta.params.get("group")
        if not isinstance(group, str) or not group:
            raise RestrictError("diff_means requires params.group")
        if group not in available:
            raise RestrictError(
                f"diff_means group column {group!r} not found in SCORE columns"
            )
        sign = beta.params.get("sign", 1)
        if sign not in (-1, 1, -1.0, 1.0):
            raise RestrictError("diff_means requires params.sign in {+1,-1}")
    if beta.type == "map_distance":
        items = beta.params.get("items")
        if not isinstance(items, list) or not items:
            raise RestrictError("map_distance requires params.items (non-empty list)")
        if not all(isinstance(j, str) and j for j in items):
            raise RestrictError("map_distance params.items must be non-empty strings")
        loadings = beta.params.get("loadings")
        if not isinstance(loadings, list):
            raise RestrictError("map_distance requires params.loadings (list)")
        if len(loadings) != len(items):
            raise RestrictError(
                f"map_distance loadings length {len(loadings)} != "
                f"items length {len(items)} (shape mismatch)"
            )
        for i, row in enumerate(loadings):
            if not isinstance(row, list) or len(row) != 2:
                raise RestrictError(
                    f"map_distance loadings[{i}] must be length-2 "
                    f"(got {row!r})"
                )
            for v in row:
                try:
                    fv = float(v)
                except (TypeError, ValueError) as exc:
                    raise RestrictError(
                        f"map_distance loadings[{i}] must be finite floats"
                    ) from exc
                if not math.isfinite(fv):
                    raise RestrictError(
                        f"map_distance loadings[{i}] must be finite floats"
                    )
        target = beta.params.get("target")
        if not isinstance(target, list) or len(target) != 2:
            raise RestrictError("map_distance requires params.target of length 2")
        for v in target:
            try:
                fv = float(v)
            except (TypeError, ValueError) as exc:
                raise RestrictError(
                    "map_distance target must be finite floats"
                ) from exc
            if not math.isfinite(fv):
                raise RestrictError("map_distance target must be finite floats")
        # Measure-dependent item columns: {measure}__{item} for every menu measure.
        for m in roles.measures:
            for j in items:
                col = f"{m}__{j}"
                if col not in available:
                    raise RestrictError(
                        f"map_distance item column {col!r} not found in SCORE columns "
                        f"(measure={m!r}, item={j!r})"
                    )


def run_restrict(
    roles: ScoreColumnRoles | dict[str, Any],
    network: Path | str | NetworkConfig | dict[str, Any],
    beta: Path | str | BetaSpec | dict[str, Any],
    *,
    beta_estimates: Path | str | pd.DataFrame | BetaEstimates | None = None,
) -> RestrictBundle:
    """Parse network + beta and bind columns against SCORE roles. No slacks.

    ``beta_estimates`` is required iff the β type is ``external`` (bring-your-
    own β, DECISIONS 2026-10-20); its canonical hash folds into ``beta_hash``.
    """
    if isinstance(roles, dict):
        roles_m = ScoreColumnRoles.model_validate(roles)
    else:
        roles_m = roles

    network_m = load_network(network)
    beta_m = load_beta(beta)
    _bind_network_columns(network_m, roles_m)
    _bind_beta_columns(beta_m, roles_m)

    estimates: BetaEstimates | None = None
    if beta_m.type == "external":
        if beta_estimates is None:
            raise RestrictError(
                "beta type 'external' requires beta_estimates (beta_estimates.csv)"
            )
        estimates = load_beta_estimates(beta_estimates, list(roles_m.measures))
        beta_hash = hash_beta(beta_m, beta_estimates_hash=estimates.estimates_hash)
    else:
        if beta_estimates is not None:
            raise RestrictError(
                f"beta_estimates supplied but beta type is {beta_m.type!r}; "
                "use type: external"
            )
        beta_hash = hash_beta(beta_m)

    return RestrictBundle(
        network=network_m,
        beta=beta_m,
        network_hash=hash_network(network_m),
        beta_hash=beta_hash,
        roles=roles_m,
        delta=float(network_m.delta),
        beta_estimates=estimates,
    )


def write_restrict_artifacts(
    bundle: RestrictBundle,
    out_dir: Path | str,
) -> dict[str, Path]:
    """Write resolved network/beta JSON under out_dir."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    net_path = out / "network_resolved.json"
    net_path.write_text(bundle.network.model_dump_json(indent=2) + "\n")
    paths["network_resolved.json"] = net_path
    beta_path = out / "beta_resolved.json"
    beta_path.write_text(bundle.beta.model_dump_json(indent=2) + "\n")
    paths["beta_resolved.json"] = beta_path
    meta = {
        "network_hash": bundle.network_hash,
        "beta_hash": bundle.beta_hash,
        "delta": bundle.delta,
        "n_restrictions": len(bundle.network.restrictions),
        "beta_type": bundle.beta.type,
    }
    est = bundle.beta_estimates
    if est is not None:
        # External β only: existing bundles keep a byte-identical meta file.
        meta["beta_estimates_hash"] = est.estimates_hash
        est_payload = {
            "schema_version": "1",
            "beta_estimates_hash": est.estimates_hash,
            "columns": list(est.columns),
            "rows": est.canonical_rows(),
            "note": (
                "beta supplied externally; the engine fits nothing. Validity of "
                "se (and same-units estimation) is the user's claim."
            ),
        }
        est_path = out / "beta_estimates.json"
        est_path.write_text(json.dumps(est_payload, indent=2, sort_keys=True) + "\n")
        paths["beta_estimates.json"] = est_path
    meta_path = out / "restrict_bundle.json"
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n")
    paths["restrict_bundle.json"] = meta_path
    return paths
