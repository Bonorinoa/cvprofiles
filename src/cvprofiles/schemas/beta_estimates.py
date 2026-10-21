"""Bring-your-own β estimates (``beta_estimates.csv``; DECISIONS 2026-10-20).

One row per menu measure: ``measure, beta_hat, se`` plus optional ``df`` /
``n_clusters`` (critical values) and documentation columns that are hashed and
echoed but never used in arithmetic. The engine fits nothing: these numbers
come from the researcher's own pipeline (fixest, pyfixest, Stata, ...).
"""

from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field

REQUIRED_COLUMNS: tuple[str, ...] = ("measure", "beta_hat", "se")
OPTIONAL_COLUMNS: tuple[str, ...] = (
    "df",
    "n_clusters",
    "cluster_var",
    "vcov",
    "n_obs",
    "estimator",
)
# Canonical column order for the freeze hash (only present columns are kept).
CANONICAL_COLUMNS: tuple[str, ...] = REQUIRED_COLUMNS + OPTIONAL_COLUMNS


class BetaEstimateRow(BaseModel):
    """One externally estimated β(m) with its standard error."""

    model_config = ConfigDict(extra="forbid")

    measure: str = Field(..., min_length=1)
    beta_hat: float = Field(..., allow_inf_nan=False)
    se: float = Field(..., gt=0.0, allow_inf_nan=False)
    df: float | None = Field(default=None, gt=0.0, allow_inf_nan=False)
    n_clusters: int | None = Field(default=None, ge=2)
    cluster_var: str | None = None
    vcov: str | None = None
    n_obs: int | None = Field(default=None, ge=1)
    estimator: str | None = None

    def critical_df(self) -> float | None:
        """Degrees of freedom for t critical values (None ⇒ normal).

        Explicit ``df`` wins; otherwise ``n_clusters - 1`` (the cluster-robust
        default in fixest and Stata); otherwise None.
        """
        if self.df is not None:
            return float(self.df)
        if self.n_clusters is not None:
            return float(self.n_clusters - 1)
        return None


@dataclass(frozen=True)
class BetaEstimates:
    """Validated estimate table bound to a menu (keyed by measure)."""

    rows: dict[str, BetaEstimateRow]
    columns: tuple[str, ...]  # present columns, canonical order
    estimates_hash: str

    @property
    def beta_hat(self) -> dict[str, float]:
        return {m: row.beta_hat for m, row in self.rows.items()}

    def canonical_rows(self) -> list[dict[str, object]]:
        """Rows sorted by measure, restricted to present columns (hash order)."""
        out: list[dict[str, object]] = []
        for m in sorted(self.rows):
            dump = self.rows[m].model_dump()
            out.append({c: dump[c] for c in self.columns})
        return out
