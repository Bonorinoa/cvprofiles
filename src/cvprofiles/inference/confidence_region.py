"""Conservative confidence region for [L, U] (semantics LOCKED in logs/DECISIONS.md,
2026-10-20; construction and proofs in reports/specs/conservative_cr_spec.md).

Contract:
- Target: the POPULATION range [L0, U0] = [min, max] of beta0 over M*_0, with
  M*_0 defined by SELECT-stage restrictions at the declared delta on the full
  frame. Holdout-stage restrictions never vote; units-split runs are refused
  by the pipeline (D7).
- Per (m, r): one-sided bounds on the population slack. Pearson types
  (corr_min / corr_sign / corr_zero) use Fisher-z with the robust
  influence-function SE (default, D4) or the classical 1/sqrt(n - 3);
  Spearman types (rank_agree / monotone_rank) use Fisher-z with the
  Bonett–Wright SE; mean_order uses Welch with Welch–Satterthwaite df.
- M+ = {m : UCB_r(m; a_out) >= -delta for all r};
  M- = {m : LCB_r(m; a_in) >= -delta for all r}.
- Levels: endpoint (default, D2) K_out = min(2, J) * Q, beta per side alpha2/2;
  simultaneous K_out = J * Q, beta per side alpha2/(2J); K_in = J always.
- CR = [min_{M+} lo, max_{M+} hi]; P([L0, U0] ⊆ CR) >= 1 - alpha1 - alpha2.
  Empty M+ ⇒ null CR (evidence that M*_0 is empty) — a success path, exit 0.
- Every bound contains its point estimate, so M- ⊆ M* ⊆ M+ and [L, U] ⊆ CR on
  every sample. The CR never replaces the headline [L, U] = min/max B*.
- Analytic and deterministic (no RNG). alpha1 / alpha2 / variant / se_method
  are EXCLUDED from the freeze preimage (diagnostic knobs, like alpha/kappa).
- Label: "conservative confidence region". The P5 uncertainty band keeps its
  "not a confidence interval" label.
- Not valid for clustered or otherwise dependent units (i.i.d. rows assumed).
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from statistics import NormalDist
from typing import Any

import numpy as np
import pandas as pd
from scipy.special import stdtrit  # type: ignore[import-untyped]

from cvprofiles.identify.beta_fn import evaluate_beta
from cvprofiles.identify.slacks import (
    SlackError,
    evaluate_slack,
    pearson_corr,
    spearman_corr,
)
from cvprofiles.restrict.pipeline import RestrictBundle
from cvprofiles.schemas.network import RestrictionSpec
from cvprofiles.schemas.scores import ScoreColumnRoles

VARIANTS: tuple[str, ...] = ("endpoint", "simultaneous")
SE_METHODS: tuple[str, ...] = ("robust", "classical")
NATIVE_BETA_TYPES: tuple[str, ...] = ("corr_y", "diff_means", "external")
_PEARSON_TYPES = ("corr_min", "corr_sign", "corr_zero")
_SPEARMAN_TYPES = ("rank_agree", "monotone_rank")
# |r| this close to 1 is a deterministic statistic (e.g. rank_agree against
# itself): se = 0 and the bound equals the estimate.
_DEGENERATE_R = 1.0 - 1e-12
_ND = NormalDist()

LABEL = (
    "Conservative confidence region for the population construct-identified "
    "range (Bonferroni)"
)


class ConfidenceRegionError(ValueError):
    """Loud CR failure (bad options / unsupported configuration).

    An empty outer set M+ is NOT an error: it is a finding (null CR, exit 0).
    """


@dataclass(frozen=True)
class CRLevels:
    """Bonferroni bookkeeping (a_out is None when there are no select restrictions)."""

    k_out: int
    a_out: float | None
    k_in: int
    a_in: float
    beta_per_side: float


@dataclass(frozen=True)
class SlackBound:
    """One (measure, restriction) pair: UCB at a_out, LCB at a_in."""

    measure: str
    restriction: str
    type: str
    statistic: float
    se: float
    slack_hat: float
    ucb: float
    lcb: float


@dataclass(frozen=True)
class BetaInterval:
    """Two-sided interval for beta(m) at per-side level beta_per_side."""

    measure: str
    beta_hat: float
    se: float
    lo: float
    hi: float
    source: str  # "engine" | "external"
    df: float | None


@dataclass(frozen=True)
class ConfidenceRegionResult:
    """Conservative CR output (additive to the headline range)."""

    variant: str
    se_method: str
    alpha1: float
    alpha2: float
    levels: CRLevels
    n_units: int
    n_menu: int
    n_select_restrictions: int
    delta: float
    cr_L: float | None
    cr_U: float | None
    empty_outer: bool
    M_plus: list[str]
    M_minus: list[str]
    status: dict[str, str]
    slack_bounds: tuple[SlackBound, ...]
    beta_intervals: tuple[BetaInterval, ...]
    beta_source: str
    beta_estimates_hash: str | None
    note: str


def _z(p: float) -> float:
    return _ND.inv_cdf(p)


def _t(p: float, df: float) -> float:
    return float(stdtrit(float(df), float(p)))


def fisher_bounds(r: float, se_z: float, a: float) -> tuple[float, float]:
    """One-sided (1 - a) lower and upper confidence bounds for a correlation."""
    if abs(r) >= _DEGENERATE_R or se_z == 0.0:
        return (float(r), float(r))
    z = math.atanh(r)
    c = _z(1.0 - a) * se_z
    return (math.tanh(z - c), math.tanh(z + c))


def pearson_se_z(x: np.ndarray, y: np.ndarray, r: float, method: str) -> float:
    """SE of atanh(r): classical 1/sqrt(n - 3), or robust (kurtosis-adjusted).

    Robust: sd(psi) / ((1 - r^2) sqrt(n - 3)) with the influence function
    psi = zx*zy - (r/2)(zx^2 + zy^2) on ddof=0 standardized data; it equals the
    classical SE under bivariate normality.
    """
    n = len(x)
    if n < 4:
        raise ConfidenceRegionError(f"Fisher-z requires n >= 4 units (got {n})")
    if abs(r) >= _DEGENERATE_R:
        return 0.0
    if method == "classical":
        return 1.0 / math.sqrt(n - 3)
    zx = (x - x.mean()) / x.std()
    zy = (y - y.mean()) / y.std()
    psi = zx * zy - 0.5 * r * (zx**2 + zy**2)
    return math.sqrt(float(np.mean(psi**2))) / (1.0 - r * r) / math.sqrt(n - 3)


def spearman_se_z(r: float, n: int) -> float:
    """Bonett–Wright (2000) SE of atanh(r_S): sqrt((1 + r_S^2 / 2) / (n - 3))."""
    if n < 4:
        raise ConfidenceRegionError(f"Fisher-z requires n >= 4 units (got {n})")
    if abs(r) >= _DEGENERATE_R:
        return 0.0
    return math.sqrt((1.0 + r * r / 2.0) / (n - 3))


def welch_stats(measure: np.ndarray, group: np.ndarray) -> tuple[float, float, float]:
    """(mean(m|g=1) - mean(m|g=0), Welch SE, Welch–Satterthwaite df).

    Same mean arithmetic as the ``mean_order`` / ``diff_means`` evaluators.
    """
    in_group = group == 1.0
    x1, x0 = measure[in_group], measure[~in_group]
    n1, n0 = len(x1), len(x0)
    if n1 < 2 or n0 < 2:
        raise ConfidenceRegionError(
            f"Welch interval requires >= 2 units per group (got {n1} and {n0})"
        )
    diff = float(np.mean(x1)) - float(np.mean(x0))
    v1 = float(np.var(x1, ddof=1)) / n1
    v0 = float(np.var(x0, ddof=1)) / n0
    se = math.sqrt(v1 + v0)
    if se == 0.0:
        return diff, 0.0, math.inf
    nu = (v1 + v0) ** 2 / (v1**2 / (n1 - 1) + v0**2 / (n0 - 1))
    return diff, se, nu


def cr_levels(J: int, Q: int, alpha1: float, alpha2: float, variant: str) -> CRLevels:
    """Per-pair / per-side levels for the endpoint or simultaneous variant."""
    if J < 1:
        raise ConfidenceRegionError("confidence region requires a non-empty menu")
    if variant == "endpoint":
        k_out = min(2, J) * Q
        beta_per_side = alpha2 / 2.0
    elif variant == "simultaneous":
        k_out = J * Q
        beta_per_side = alpha2 / (2.0 * J)
    else:
        raise ConfidenceRegionError(f"variant must be one of {VARIANTS} (got {variant!r})")
    return CRLevels(
        k_out=k_out,
        a_out=(alpha1 / k_out) if k_out else None,
        k_in=J,
        a_in=alpha1 / J,
        beta_per_side=beta_per_side,
    )


def _signed_bounds(
    r: float, se: float, sign: float, theta: float, a_out: float, a_in: float
) -> tuple[float, float]:
    """(UCB at a_out, LCB at a_in) of sign * rho - theta."""
    lo_out, hi_out = fisher_bounds(r, se, a_out)
    lo_in, hi_in = fisher_bounds(r, se, a_in)
    if sign > 0:
        return hi_out - theta, lo_in - theta
    return -lo_out - theta, -hi_in - theta


def slack_bound(
    frame: pd.DataFrame,
    measure: str,
    restriction: RestrictionSpec,
    *,
    a_out: float,
    a_in: float,
    se_method: str,
) -> SlackBound:
    """One-sided bounds on the population slack of one (measure, restriction)."""
    x = frame[measure].to_numpy(dtype=float)
    slack_hat = evaluate_slack(x, frame, restriction)
    t = restriction.type
    theta = float(restriction.theta)
    p = restriction.params
    if t in _PEARSON_TYPES:
        v = frame[str(p["variable"])].to_numpy(dtype=float)
        stat = pearson_corr(x, v)
        se = pearson_se_z(x, v, stat, se_method)
        if t == "corr_zero":
            # UCB needs a lower bound on |rho|: two-sided at a_out/2 per side
            # (both tails can bite at rho = 0).
            lo, hi = fisher_bounds(stat, se, a_out / 2.0)
            lcb_abs = 0.0 if lo <= 0.0 <= hi else min(abs(lo), abs(hi))
            ucb = theta - lcb_abs
            lo_in, hi_in = fisher_bounds(stat, se, a_in)
            lcb = theta - max(abs(lo_in), abs(hi_in))
        else:
            sign = float(p.get("sign", 1)) if t == "corr_sign" else 1.0
            ucb, lcb = _signed_bounds(stat, se, sign, theta, a_out, a_in)
    elif t in _SPEARMAN_TYPES:
        other = p["ref_measure"] if t == "rank_agree" else p["variable"]
        v = frame[str(other)].to_numpy(dtype=float)
        stat = spearman_corr(x, v)
        se = spearman_se_z(stat, len(x))
        sign = float(p.get("sign", 1)) if t == "monotone_rank" else 1.0
        ucb, lcb = _signed_bounds(stat, se, sign, theta, a_out, a_in)
    elif t == "mean_order":
        g = frame[str(p["group"])].to_numpy(dtype=float)
        sign = float(p.get("sign", 1))
        stat, se, nu = welch_stats(x, g)
        if se == 0.0:
            ucb = lcb = sign * stat - theta
        else:
            ucb = sign * stat + _t(1.0 - a_out, nu) * se - theta
            lcb = sign * stat - _t(1.0 - a_in, nu) * se - theta
    else:
        raise ConfidenceRegionError(f"restriction type {t!r} has no confidence bound")
    # Prop. 4 containment: bracket the engine's point slack exactly, even
    # where tanh(atanh(r)) rounds by an ulp.
    return SlackBound(
        measure=measure,
        restriction=restriction.id,
        type=t,
        statistic=float(stat),
        se=float(se),
        slack_hat=float(slack_hat),
        ucb=max(float(ucb), float(slack_hat)),
        lcb=min(float(lcb), float(slack_hat)),
    )


def beta_interval(
    frame: pd.DataFrame,
    measure: str,
    bundle: RestrictBundle,
    beta_hat: float,
    *,
    b: float,
    se_method: str,
) -> BetaInterval:
    """Two-sided interval for beta(m) at per-side level b."""
    beta = bundle.beta
    df: float | None = None
    source = "engine"
    if beta.type == "external":
        assert bundle.beta_estimates is not None  # RESTRICT guarantees it
        row = bundle.beta_estimates.rows[measure]
        df = row.critical_df()
        c = _z(1.0 - b) if df is None else _t(1.0 - b, df)
        se = row.se
        lo, hi = beta_hat - c * se, beta_hat + c * se
        source = "external"
    elif beta.type == "corr_y":
        x = frame[measure].to_numpy(dtype=float)
        y = frame[beta.outcome].to_numpy(dtype=float)
        se = pearson_se_z(x, y, beta_hat, se_method)
        lo, hi = fisher_bounds(beta_hat, se, b)
    elif beta.type == "diff_means":
        x = frame[measure].to_numpy(dtype=float)
        g = frame[str(beta.params["group"])].to_numpy(dtype=float)
        _, se, nu = welch_stats(x, g)
        c = 0.0 if se == 0.0 else _t(1.0 - b, nu)
        lo, hi = beta_hat - c * se, beta_hat + c * se
        df = nu if math.isfinite(nu) else None
    else:
        raise ConfidenceRegionError(_unsupported_beta_message(beta.type))
    return BetaInterval(
        measure=measure,
        beta_hat=float(beta_hat),
        se=float(se),
        lo=min(float(lo), float(beta_hat)),
        hi=max(float(hi), float(beta_hat)),
        source=source,
        df=df,
    )


def _unsupported_beta_message(beta_type: str) -> str:
    return (
        f"beta type {beta_type!r} has no native confidence interval; use beta type "
        "'external' (compute beta and its SE in your own pipeline)"
    )


def validate_cr_options(alpha1: float, alpha2: float, variant: str, se_method: str) -> None:
    """Fail loud on CR knobs (shared by the pipeline pre-flight and the CLI)."""
    for name, value in (("alpha1", alpha1), ("alpha2", alpha2)):
        v = float(value)
        if not math.isfinite(v) or not (0.0 < v < 1.0):
            raise ConfidenceRegionError(f"{name} must satisfy 0 < {name} < 1 (got {value!r})")
    if float(alpha1) + float(alpha2) >= 1.0:
        raise ConfidenceRegionError("alpha1 + alpha2 must be < 1")
    if variant not in VARIANTS:
        raise ConfidenceRegionError(f"variant must be one of {VARIANTS} (got {variant!r})")
    if se_method not in SE_METHODS:
        raise ConfidenceRegionError(
            f"se_method must be one of {SE_METHODS} (got {se_method!r})"
        )


def check_confidence_region_supported(bundle: RestrictBundle, n_units: int) -> None:
    """Fail loud before any artifact is written (pipeline pre-flight)."""
    if bundle.beta.type not in NATIVE_BETA_TYPES:
        raise ConfidenceRegionError(_unsupported_beta_message(bundle.beta.type))
    if n_units < 4:
        raise ConfidenceRegionError(
            f"confidence region requires n >= 4 units (got {n_units})"
        )


def compute_confidence_region(
    frame: pd.DataFrame,
    roles: ScoreColumnRoles,
    bundle: RestrictBundle,
    *,
    alpha1: float = 0.05,
    alpha2: float = 0.05,
    variant: str = "endpoint",
    se_method: str = "robust",
) -> ConfidenceRegionResult:
    """Conservative Bonferroni CR for the select-stage population range."""
    validate_cr_options(alpha1, alpha2, variant, se_method)
    if not isinstance(bundle, RestrictBundle):
        raise ConfidenceRegionError("compute_confidence_region requires a RestrictBundle")
    check_confidence_region_supported(bundle, len(frame))

    measures = list(roles.measures)
    select = [r for r in bundle.network.restrictions if r.stage is None or r.stage == "select"]
    levels = cr_levels(len(measures), len(select), float(alpha1), float(alpha2), variant)
    delta = float(bundle.delta)

    bounds: list[SlackBound] = []
    if levels.a_out is not None:
        try:
            for m in measures:
                for r in select:
                    bounds.append(
                        slack_bound(
                            frame, m, r, a_out=levels.a_out, a_in=levels.a_in,
                            se_method=se_method,
                        )
                    )  # fmt: skip
        except SlackError as exc:
            raise ConfidenceRegionError(str(exc)) from exc

    by_measure: dict[str, list[SlackBound]] = {m: [] for m in measures}
    for bnd in bounds:
        by_measure[bnd.measure].append(bnd)
    M_plus = [m for m in measures if all(b.ucb >= -delta for b in by_measure[m])]
    M_minus = [m for m in measures if all(b.lcb >= -delta for b in by_measure[m])]

    estimates = bundle.beta_estimates.beta_hat if bundle.beta_estimates is not None else None
    try:
        intervals = [
            beta_interval(
                frame, m, bundle, evaluate_beta(frame, m, bundle.beta, estimates),
                b=levels.beta_per_side, se_method=se_method,
            )
            for m in measures
        ]  # fmt: skip
    except SlackError as exc:
        raise ConfidenceRegionError(str(exc)) from exc

    if M_plus:
        kept = [iv for iv in intervals if iv.measure in M_plus]
        cr_L: float | None = min(iv.lo for iv in kept)
        cr_U: float | None = max(iv.hi for iv in kept)
    else:
        cr_L = cr_U = None

    status = {
        m: (
            "certainly_admissible"
            if m in M_minus
            else "possibly_admissible"
            if m in M_plus
            else "certainly_rejected"
        )
        for m in measures
    }
    est_hash = bundle.beta_estimates.estimates_hash if bundle.beta_estimates else None
    nominal = 1.0 - float(alpha1) - float(alpha2)
    note = (
        f"{LABEL}, {variant} variant: P([L0, U0] in CR) >= {nominal:.2f} "
        "asymptotically, for the select-stage population range, under i.i.d. "
        "units and a network/theta/delta/beta fixed before the data. Statuses: "
        "certainly admissible = M-, possibly admissible = M+ minus M-, certainly "
        "rejected = menu minus M+. Not valid for clustered units."
    )
    if not M_plus:
        note += (
            " Outer set M+ is empty: evidence that no menu measure is admissible "
            "in the population (level alpha1/2 for the endpoint variant)."
        )
    if est_hash is not None:
        note += (
            " beta supplied externally: beta intervals use the user's se, whose "
            "validity is the user's claim."
        )

    return ConfidenceRegionResult(
        variant=variant,
        se_method=se_method,
        alpha1=float(alpha1),
        alpha2=float(alpha2),
        levels=levels,
        n_units=len(frame),
        n_menu=len(measures),
        n_select_restrictions=len(select),
        delta=delta,
        cr_L=cr_L,
        cr_U=cr_U,
        empty_outer=not M_plus,
        M_plus=M_plus,
        M_minus=M_minus,
        status=status,
        slack_bounds=tuple(bounds),
        beta_intervals=tuple(intervals),
        beta_source="external" if est_hash is not None else "engine",
        beta_estimates_hash=est_hash,
        note=note,
    )


def confidence_region_payload(result: ConfidenceRegionResult) -> dict[str, Any]:
    """JSON-serializable audit payload (written as confidence_region.json)."""
    lv = result.levels
    return {
        "schema_version": "1",
        "purpose": "conservative_confidence_region",
        "label": LABEL,
        "variant": result.variant,
        "alpha1": result.alpha1,
        "alpha2": result.alpha2,
        "nominal_coverage": 1.0 - result.alpha1 - result.alpha2,
        "se_method": result.se_method,
        "n_units": result.n_units,
        "n_menu": result.n_menu,
        "n_select_restrictions": result.n_select_restrictions,
        "delta": result.delta,
        "levels": {
            "K_out": lv.k_out,
            "a_out": lv.a_out,
            "K_in": lv.k_in,
            "a_in": lv.a_in,
            "beta_per_side": lv.beta_per_side,
        },
        "CR_L": result.cr_L,
        "CR_U": result.cr_U,
        "empty_outer": result.empty_outer,
        "M_plus": result.M_plus,
        "M_minus": result.M_minus,
        "status": result.status,
        "slack_bounds": [
            {
                "measure": b.measure,
                "restriction": b.restriction,
                "type": b.type,
                "statistic": b.statistic,
                "se": b.se,
                "slack_hat": b.slack_hat,
                "ucb": b.ucb,
                "lcb": b.lcb,
            }
            for b in result.slack_bounds
        ],
        "beta_intervals": [
            {
                "measure": iv.measure,
                "beta_hat": iv.beta_hat,
                "se": iv.se,
                "lo": iv.lo,
                "hi": iv.hi,
                "source": iv.source,
                "df": iv.df,
            }
            for iv in result.beta_intervals
        ],
        "beta_source": result.beta_source,
        "beta_estimates_hash": result.beta_estimates_hash,
        "target": "select_stage_population_range",
        "note": result.note,
        "headline_note": (
            "Headline [L,U] remains min/max B* on the full sample; the confidence "
            "region is additive and never replaces it."
        ),
    }
