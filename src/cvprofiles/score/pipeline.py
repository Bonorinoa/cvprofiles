"""SCORE pipeline: load → validate → optional normalize → freeze hash + manifest."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

import numpy as np
import pandas as pd

from cvprofiles.freeze import hash_scores_frame
from cvprofiles.schemas.scores import ScoreColumnRoles, ScoreManifest

NormPolicy = Literal["none", "zscore_measures"]


class ScoreError(ValueError):
    """Loud SCORE failure (schema / data contract)."""


@dataclass(frozen=True)
class ScoreResult:
    """In-memory SCORE outputs."""

    frame: pd.DataFrame
    roles: ScoreColumnRoles
    manifest: ScoreManifest
    freeze_columns: list[str]


def freeze_columns_for(roles: ScoreColumnRoles) -> list[str]:
    """Default engine freeze column order (diagnostics excluded)."""
    cols = [roles.unit_id, *roles.measures, *roles.aux]
    if roles.outcome is not None:
        cols.append(roles.outcome)
    return cols


def load_table(path: Path | str) -> pd.DataFrame:
    """Load scores CSV or parquet."""
    p = Path(path)
    if not p.is_file():
        raise ScoreError(f"scores file not found: {p}")
    suffix = p.suffix.lower()
    if suffix == ".csv":
        return pd.read_csv(p)
    if suffix in {".parquet", ".pq"}:
        return pd.read_parquet(p)
    raise ScoreError(f"unsupported scores format: {suffix} (use .csv or .parquet)")


def load_roles(path: Path | str | ScoreColumnRoles | dict[str, Any]) -> ScoreColumnRoles:
    """Load roles from JSON path, mapping, or model."""
    if isinstance(path, ScoreColumnRoles):
        return path
    if isinstance(path, dict):
        return ScoreColumnRoles.model_validate(path)
    p = Path(path)
    if not p.is_file():
        raise ScoreError(f"roles file not found: {p}")
    return ScoreColumnRoles.model_validate_json(p.read_text())


def _require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ScoreError(f"scores frame missing required columns: {missing}")


def _check_unit_ids(series: pd.Series, unit_id_col: str) -> None:
    if series.isna().any():
        raise ScoreError(f"{unit_id_col} contains missing values")
    as_str = series.astype(str)
    if as_str.duplicated().any():
        dups = sorted(as_str[as_str.duplicated()].unique().tolist())
        raise ScoreError(f"duplicate unit_id values: {dups}")


def _check_finite(df: pd.DataFrame, cols: list[str]) -> None:
    for c in cols:
        if c not in df.columns:
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        if s.isna().any() and not df[c].isna().equals(s.isna()):
            # non-numeric non-null values
            bad = df.loc[s.isna() & df[c].notna(), c]
            if len(bad):
                raise ScoreError(f"column {c!r} has non-numeric values")
        arr = s.to_numpy(dtype=float)
        if not np.isfinite(arr).all():
            raise ScoreError(f"column {c!r} has non-finite values (NaN/Inf)")


def apply_normalization(
    df: pd.DataFrame,
    roles: ScoreColumnRoles,
    *,
    policy: NormPolicy = "none",
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Apply normalization policy. Returns (frame, normalization manifest dict)."""
    out = df.copy()
    meta: dict[str, Any] = {
        "policy": policy,
        "zscore_measures": policy == "zscore_measures",
        "ddof": 0 if policy == "zscore_measures" else None,
        "columns_transformed": [],
    }
    if policy == "none":
        return out, meta
    if policy != "zscore_measures":
        raise ScoreError(f"unknown normalization policy: {policy!r}")

    transformed: list[str] = []
    for col in roles.measures:
        x = pd.to_numeric(out[col], errors="raise").to_numpy(dtype=float)
        mu = float(np.mean(x))
        sd = float(np.std(x, ddof=0))
        if sd == 0.0 or not np.isfinite(sd):
            raise ScoreError(f"cannot z-score measure {col!r}: zero or non-finite std")
        out[col] = (x - mu) / sd
        transformed.append(col)
    meta["columns_transformed"] = transformed
    return out, meta


def run_score(
    df: pd.DataFrame,
    roles: ScoreColumnRoles | dict[str, Any] | Path | str,
    *,
    policy: NormPolicy = "none",
) -> ScoreResult:
    """Validate, optionally normalize, and freeze a score table."""
    roles_m = load_roles(roles)
    if len(df) < 1:
        raise ScoreError("scores frame is empty")

    needed = freeze_columns_for(roles_m)
    # Diagnostics optional on disk; if declared, must exist
    optional_diag = list(roles_m.diagnostic)
    _require_columns(df, needed + [c for c in optional_diag if c not in needed])

    work = df.copy()
    _check_unit_ids(work[roles_m.unit_id], roles_m.unit_id)

    # Finite checks on freeze columns only (diagnostics may be messy)
    numeric_freeze = [c for c in needed if c != roles_m.unit_id]
    _check_finite(work, numeric_freeze)

    work, norm_meta = apply_normalization(work, roles_m, policy=policy)
    # Re-check finiteness after transform
    _check_finite(work, numeric_freeze)

    # Keep stable column order: freeze cols first, then any extras (diagnostics)
    extras = [c for c in work.columns if c not in needed]
    ordered = work.loc[:, needed + extras].copy()

    scores_hash = hash_scores_frame(ordered, needed, unit_id_col=roles_m.unit_id)
    dtypes = {c: str(ordered[c].dtype) for c in needed}
    manifest = ScoreManifest(
        roles=roles_m,
        n_rows=int(len(ordered)),
        n_measures=len(roles_m.measures),
        measure_columns=list(roles_m.measures),
        normalization=norm_meta,
        scores_hash=scores_hash,
        dtypes=dtypes,
    )
    return ScoreResult(
        frame=ordered,
        roles=roles_m,
        manifest=manifest,
        freeze_columns=needed,
    )


def write_score_artifacts(
    result: ScoreResult,
    out_dir: Path | str,
    *,
    parquet: bool = True,
) -> dict[str, Path]:
    """Write S_frozen + score_manifest.json under out_dir."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    paths: dict[str, Path] = {}
    if parquet:
        pq = out / "S_frozen.parquet"
        result.frame.to_parquet(pq, index=False)
        paths["S_frozen.parquet"] = pq
    csv_path = out / "S_frozen.csv"
    result.frame.to_csv(csv_path, index=False)
    paths["S_frozen.csv"] = csv_path
    man_path = out / "score_manifest.json"
    man_path.write_text(result.manifest.model_dump_json(indent=2) + "\n")
    paths["score_manifest.json"] = man_path
    return paths
