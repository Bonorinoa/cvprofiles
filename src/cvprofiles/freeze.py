"""Freeze hashing and run_id construction (M1 lock).

Algorithm (LOCKED 2026-08-01 — see docs/12):

1. Piece hashes are bare lowercase SHA-256 hex (64 chars), no ``sha256:`` prefix.
2. Canonical JSON: UTF-8, ``sort_keys=True``, separators ``(",", ":")``,
   ``allow_nan=False``. Non-JSON types raise.
3. ``network_hash`` / ``beta_hash``: hash canonical JSON of
   ``model_dump(mode="json")`` for validated NetworkConfig / BetaSpec.
4. ``scores_hash``: hash canonical CSV text of the score table:
   - columns in declared order (caller supplies column list);
   - rows sorted by ``unit_id`` ascending (string sort);
   - header line = comma-joined column names;
   - floats formatted with 17 significant digits (``format(x, ".17g")``);
   - integers without decimal; bool as ``0``/``1``; null as empty field;
   - UTF-8 bytes of the full CSV (including trailing newline after last row).
5. ``run_id``: SHA-256 of canonical JSON of the freeze preimage dict with keys
   (JSON is sort_keys; documentation order is not the hash order):
   ``beta_hash``, ``config``, ``delta``, ``n_boot``, ``network_hash``,
   ``package_version``, ``schema_version``, ``scores_hash``, ``seed``.
   ``n_boot`` is JSON ``null`` in v1.0.
6. **Excluded from run_id preimage:** ``created_at``, wall clock, absolute paths,
   hostnames, artifact path maps, report HTML.

Bit-stability: same validated scores + network + beta + package_version +
seed + delta + config ⇒ identical scores/network/beta hashes and run_id.

Engine freeze column list should be unit_id + measures + aux + outcome only;
diagnostic columns (e.g. ``V_star``) stay out of ``scores_hash`` unless the
caller intentionally versions them.
"""

from __future__ import annotations

import hashlib
import json
import math
import re
from collections.abc import Mapping, Sequence
from typing import Any

import numpy as np
import pandas as pd

from cvprofiles.schemas.beta import BetaSpec
from cvprofiles.schemas.network import NetworkConfig
from cvprofiles.schemas.run import FreezeBundle

CANONICAL_JSON_SEPARATORS = (",", ":")
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


def canonical_json_bytes(obj: Any) -> bytes:
    """Serialize ``obj`` to canonical UTF-8 JSON bytes (sorted keys, compact)."""
    try:
        text = json.dumps(
            obj,
            sort_keys=True,
            separators=CANONICAL_JSON_SEPARATORS,
            ensure_ascii=False,
            allow_nan=False,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(f"object is not JSON-canonicalizable: {exc}") from exc
    return text.encode("utf-8")


def sha256_hex(data: bytes) -> str:
    """Bare lowercase SHA-256 hex digest (64 chars)."""
    return hashlib.sha256(data).hexdigest()


def hash_canonical_json(obj: Any) -> str:
    """SHA-256 hex of canonical JSON bytes."""
    return sha256_hex(canonical_json_bytes(obj))


def _format_cell(value: Any) -> str:
    if value is None:
        return ""

    # Numpy scalars → Python before NA / bool / int branching
    if isinstance(value, np.generic):
        value = value.item()

    # Non-finite floats must fail loud (never coerce NaN/Inf to empty).
    if isinstance(value, float):
        if math.isnan(value) or math.isinf(value):
            raise ValueError("scores table must not contain NaN or Inf for freeze hash")
        return format(value, ".17g")

    # Remaining missing values (e.g. pd.NA on non-float columns) → empty field
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass

    if isinstance(value, bool):
        return "1" if value else "0"
    if isinstance(value, int) and not isinstance(value, bool):
        return str(value)
    if isinstance(value, str):
        if any(c in value for c in (",", '"', "\n", "\r")):
            escaped = value.replace('"', '""')
            return f'"{escaped}"'
        return value
    raise ValueError(f"unsupported cell type for scores hash: {type(value)!r}")


def scores_canonical_csv_bytes(
    df: pd.DataFrame,
    columns: Sequence[str],
    *,
    unit_id_col: str = "unit_id",
) -> bytes:
    """Build canonical CSV bytes for score-table hashing.

    Rows are sorted by ``unit_id_col`` (as string). Column order is exactly
    ``columns`` (typically unit_id + measures + aux + outcome; diagnostics out).
    """
    missing = [c for c in columns if c not in df.columns]
    if missing:
        raise ValueError(f"scores frame missing columns for hash: {missing}")
    if unit_id_col not in columns:
        raise ValueError(f"unit_id column {unit_id_col!r} must be included in columns")

    work = df.loc[:, list(columns)].copy()
    work["_sort_key"] = work[unit_id_col].astype(str)
    work = work.sort_values("_sort_key", kind="mergesort").drop(columns=["_sort_key"])

    lines: list[str] = [",".join(columns)]
    for row in work.itertuples(index=False, name=None):
        lines.append(",".join(_format_cell(v) for v in row))
    text = "\n".join(lines) + "\n"
    return text.encode("utf-8")


def hash_scores_frame(
    df: pd.DataFrame,
    columns: Sequence[str],
    *,
    unit_id_col: str = "unit_id",
) -> str:
    """SHA-256 hex of canonical score CSV bytes."""
    return sha256_hex(scores_canonical_csv_bytes(df, columns, unit_id_col=unit_id_col))


def hash_network(network: NetworkConfig | Mapping[str, Any]) -> str:
    """SHA-256 of canonical JSON for a validated network (or raw mapping)."""
    if isinstance(network, NetworkConfig):
        payload = network.model_dump(mode="json")
    else:
        payload = NetworkConfig.model_validate(dict(network)).model_dump(mode="json")
    return hash_canonical_json(payload)


def hash_beta(beta: BetaSpec | Mapping[str, Any]) -> str:
    """SHA-256 of canonical JSON for a validated beta spec (or raw mapping)."""
    if isinstance(beta, BetaSpec):
        payload = beta.model_dump(mode="json")
    else:
        payload = BetaSpec.model_validate(dict(beta)).model_dump(mode="json")
    return hash_canonical_json(payload)


def _validate_hex64(name: str, value: str) -> None:
    if not isinstance(value, str) or not _HEX64.match(value):
        raise ValueError(f"{name} must be 64-char lowercase hex string")


def normalize_n_boot(n_boot: int | None) -> int | None:
    """Normalize ``n_boot`` for the freeze preimage (docs/12 v1.1 lock).

    ``< 1`` (or None) ⇒ JSON ``null`` so v1.0-era run_ids stay bit-stable
    when bootstrap is off; ``>= 1`` ⇒ int. Every preimage producer must call
    this before ``compute_run_id`` / ``build_freeze_bundle``.
    """
    if n_boot is None or n_boot < 1:
        return None
    return int(n_boot)


def freeze_preimage(
    *,
    scores_hash: str,
    network_hash: str,
    beta_hash: str,
    package_version: str,
    seed: int = 0,
    delta: float = 0.0,
    schema_version: str = "1",
    n_boot: int | None = None,
    config: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the run_id preimage dict (hashed by ``compute_run_id``)."""
    return {
        "beta_hash": beta_hash,
        "config": dict(config or {}),
        "delta": float(delta),
        "n_boot": n_boot,
        "network_hash": network_hash,
        "package_version": package_version,
        "schema_version": schema_version,
        "scores_hash": scores_hash,
        "seed": int(seed),
    }


def compute_run_id(
    *,
    scores_hash: str,
    network_hash: str,
    beta_hash: str,
    package_version: str,
    seed: int = 0,
    delta: float = 0.0,
    schema_version: str = "1",
    n_boot: int | None = None,
    config: Mapping[str, Any] | None = None,
) -> str:
    """Compute ``run_id`` = SHA-256 hex of canonical freeze preimage JSON."""
    _validate_hex64("scores_hash", scores_hash)
    _validate_hex64("network_hash", network_hash)
    _validate_hex64("beta_hash", beta_hash)

    preimage = freeze_preimage(
        scores_hash=scores_hash,
        network_hash=network_hash,
        beta_hash=beta_hash,
        package_version=package_version,
        seed=seed,
        delta=delta,
        schema_version=schema_version,
        n_boot=n_boot,
        config=config,
    )
    return hash_canonical_json(preimage)


def build_freeze_bundle(
    *,
    scores_hash: str,
    network_hash: str,
    beta_hash: str,
    package_version: str,
    seed: int = 0,
    delta: float = 0.0,
    schema_version: str = "1",
    n_boot: int | None = None,
    config: Mapping[str, Any] | None = None,
) -> FreezeBundle:
    """Construct a validated FreezeBundle (does not compute run_id)."""
    return FreezeBundle(
        scores_hash=scores_hash,
        network_hash=network_hash,
        beta_hash=beta_hash,
        package_version=package_version,
        schema_version=schema_version,
        seed=seed,
        delta=delta,
        n_boot=n_boot,
        config=dict(config or {}),
    )


def run_id_from_bundle(bundle: FreezeBundle) -> str:
    """Compute run_id from a FreezeBundle (created_at is not on the bundle)."""
    return compute_run_id(
        scores_hash=bundle.scores_hash,
        network_hash=bundle.network_hash,
        beta_hash=bundle.beta_hash,
        package_version=bundle.package_version,
        seed=bundle.seed,
        delta=bundle.delta,
        schema_version=bundle.schema_version,
        n_boot=bundle.n_boot,
        config=bundle.config,
    )
