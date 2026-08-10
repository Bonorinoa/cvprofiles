"""Thin Typer CLI — state helpers + full SCORE→REPORT run."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Annotated

import typer

from cvprofiles import __version__

app = typer.Typer(
    name="cvprofiles",
    help="Construct-validity profiles: admissible sets and construct-identified ranges.",
    no_args_is_help=True,
    add_completion=False,
)


def _parse_theta_grid(raw: str | None) -> list[float] | None:
    """Parse a comma-separated positive finite λ grid, fail-loudly."""
    if raw is None:
        return None
    tokens = raw.split(",")
    if not raw.strip() or any(not token.strip() for token in tokens):
        raise ValueError("must be a non-empty comma-separated list of positive numbers")
    values: list[float] = []
    for token in tokens:
        try:
            value = float(token.strip())
        except ValueError as exc:
            raise ValueError(f"invalid lambda {token.strip()!r}") from exc
        if not math.isfinite(value) or value <= 0.0:
            raise ValueError(f"lambda {token.strip()!r} must be finite and > 0")
        if value in values:
            raise ValueError(f"duplicate lambda {token.strip()!r}")
        values.append(value)
    return values


def _parse_delta_grid(raw: str | None) -> list[float] | None:
    """Parse a comma-separated non-negative finite δ grid, fail-loudly."""
    if raw is None:
        return None
    tokens = raw.split(",")
    if not raw.strip() or any(not token.strip() for token in tokens):
        raise ValueError("must be a non-empty comma-separated list of non-negative numbers")
    values: list[float] = []
    for token in tokens:
        try:
            value = float(token.strip())
        except ValueError as exc:
            raise ValueError(f"invalid delta {token.strip()!r}") from exc
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"delta {token.strip()!r} must be finite and >= 0")
        if value in values:
            raise ValueError(f"duplicate delta {token.strip()!r}")
        values.append(value)
    return values


def _parse_holdout_units(raw: str | None) -> list[str] | None:
    """Parse a comma-separated unit-id holdout list, fail-loudly.

    Thin splitter: whitespace is stripped, and an empty string or any empty
    token fails loud (mirrors ``_parse_theta_grid``). Duplicates and list
    order are passed through unchanged — the pipeline's
    ``normalize_holdout_units`` dedupes sorted-unique (identify/pipeline.py),
    so dupes/order can never fork ``run_id``.
    """
    if raw is None:
        return None
    tokens = raw.split(",")
    if not raw.strip() or any(not token.strip() for token in tokens):
        raise ValueError("must be a non-empty comma-separated list of unit ids")
    return [token.strip() for token in tokens]


def _check_alpha(alpha: float) -> float:
    """Validate the coverage band tail probability per coverage.py (0 < alpha
    < 1, finite); fail-loudly. Rule mirrored from inference/coverage.py:103-105."""
    a = float(alpha)
    if not math.isfinite(a) or not (0.0 < a < 1.0):
        raise ValueError("alpha must satisfy 0 < alpha < 1")
    return a


def _check_kappa(kappa: float) -> float:
    """Validate the boundary multiplier per coverage.py (finite, > 0);
    fail-loudly. Rule mirrored from inference/coverage.py:106-108."""
    k = float(kappa)
    if not math.isfinite(k) or k <= 0.0:
        raise ValueError("kappa must be finite and > 0")
    return k


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"cvprofiles {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show package version and exit.",
        callback=_version_callback,
        is_eager=True,
    ),
) -> None:
    """cvprofiles CLI (thin spine, v2.5.0)."""


@app.command("run")
def run_cmd(
    scores: Annotated[
        Path,
        typer.Option("--scores", exists=True, dir_okay=False, help="Scores CSV/parquet"),
    ],
    roles: Annotated[
        Path,
        typer.Option("--roles", exists=True, dir_okay=False, help="roles.json"),
    ],
    network: Annotated[
        Path,
        typer.Option("--network", exists=True, dir_okay=False, help="network.yaml"),
    ],
    beta: Annotated[
        Path,
        typer.Option("--beta", exists=True, dir_okay=False, help="beta.yaml"),
    ],
    out: Annotated[
        Path | None,
        typer.Option("--out", help="Output dir (default: reports/runs/<run_id>/)"),
    ] = None,
    policy: Annotated[
        str,
        typer.Option("--policy", help="SCORE normalization: none | zscore_measures"),
    ] = "none",
    seed: Annotated[int, typer.Option("--seed", min=0)] = 0,
    n_boot: Annotated[
        int,
        typer.Option(
            "--n-boot",
            min=0,
            help="Bootstrap replicates over units; 0 disables bootstrap.",
        ),
    ] = 0,
    theta_grid: Annotated[
        str | None,
        typer.Option(
            "--theta-grid",
            help="Comma-separated positive threshold scale multipliers.",
        ),
    ] = None,
    delta_grid: Annotated[
        str | None,
        typer.Option(
            "--delta-grid",
            help="Comma-separated non-negative tolerance values (absolute δ).",
        ),
    ] = None,
    holdout_units: Annotated[
        str | None,
        typer.Option(
            "--holdout-units",
            help="Comma-separated unit ids held out for the P4b units-split "
            "compliance check (select on train, verdict on hold).",
        ),
    ] = None,
    alpha: Annotated[
        float,
        typer.Option(
            "--alpha",
            help="Coverage band tail probability; must satisfy 0 < alpha < 1 "
            "(default 0.10 ⇒ band (0.05, 0.95)).",
        ),
    ] = 0.10,
    kappa: Annotated[
        float,
        typer.Option(
            "--kappa",
            help="Boundary attribution multiplier |margin| <= kappa*SE; must "
            "be finite and > 0 (default 2.0).",
        ),
    ] = 2.0,
    anchors: Annotated[
        Path | None,
        typer.Option(
            "--anchors",
            exists=True,
            dir_okay=False,
            help="Pre-data θ-anchor YAML (documentation; excluded from run_id).",
        ),
    ] = None,
    title: Annotated[
        str,
        typer.Option("--title"),
    ] = "Construct-validity profile",
) -> None:
    """SCORE → RESTRICT → IDENTIFY → REPORT. Empty M* exits 0.

    stdout is always a single JSON summary (machine-clean).
    Human status crumbs go to stderr only.
    """
    from cvprofiles.identify.pipeline import IdentifyError
    from cvprofiles.pipeline import run_profile, summary_dict
    from cvprofiles.report.pipeline import ReportError
    from cvprofiles.restrict.pipeline import RestrictError
    from cvprofiles.score.pipeline import ScoreError

    if policy not in ("none", "zscore_measures"):
        typer.secho(f"error: unknown policy: {policy}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2)

    try:
        theta_grid_lambdas = _parse_theta_grid(theta_grid)
    except ValueError as exc:
        typer.secho(f"error: theta-grid: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    try:
        delta_grid_deltas = _parse_delta_grid(delta_grid)
    except ValueError as exc:
        typer.secho(f"error: delta-grid: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    try:
        holdout = _parse_holdout_units(holdout_units)
    except ValueError as exc:
        typer.secho(f"error: holdout-units: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    try:
        alpha_ok = _check_alpha(alpha)
    except ValueError as exc:
        typer.secho(f"error: alpha: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    try:
        kappa_ok = _check_kappa(kappa)
    except ValueError as exc:
        typer.secho(f"error: kappa: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=2) from exc

    try:
        result = run_profile(
            scores=scores,
            roles=roles,
            network=network,
            beta=beta,
            out_dir=out,
            policy=policy,  # type: ignore[arg-type]
            seed=seed,
            title=title,
            n_boot=n_boot,
            theta_grid_lambdas=theta_grid_lambdas,
            delta_grid_deltas=delta_grid_deltas,
            anchors=anchors,
            holdout_units=holdout,
            alpha=alpha_ok,
            kappa=kappa_ok,
        )
    except (ScoreError, RestrictError, IdentifyError, ReportError, ValueError) as exc:
        typer.secho(f"error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    summary = summary_dict(result)
    # stdout = JSON only (tests + scripts parse this)
    typer.echo(json.dumps(summary, indent=2))
    # human crumbs → stderr only
    if result.identify.empty:
        typer.secho(
            "empty M* — clean success; see report.html for binding restrictions",
            fg=typer.colors.YELLOW,
            err=True,
        )
    else:
        typer.secho(
            f"M*={result.identify.admissible}  "
            f"[L,U]=[{result.identify.range_L}, {result.identify.range_U}]",
            fg=typer.colors.GREEN,
            err=True,
        )


if __name__ == "__main__":
    app()
