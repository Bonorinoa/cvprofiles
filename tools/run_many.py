"""Batch orchestrator: many profiles, one shared score matrix.

Runs N (network, beta) profiles from a YAML manifest against a single SCORE
input, writing each profile's frozen run directory under
<out_root>/<profile_id>/ plus a machine-readable batch summary. This is
orchestration only — it composes the existing engine, never re-implements it.

Manifest shape (YAML):

    profiles:
      - id: trust
        network: networks/trust.yaml
        beta: betas/trust.yaml
      - id: patience
        network: networks/patience.yaml
        beta: betas/patience.yaml

Relative network/beta paths resolve against the manifest file's directory.
All profiles share the same scores/roles/policy/seed and the same additive
diagnostic flags (bootstrap, θ-grid, δ-grid, anchors) when given.

CLI contract mirrors the engine CLI: stdout is a single machine-clean JSON
batch summary; human status messages go to stderr. Empty M* in any profile is
a clean success (exit 0), exactly as in the single-run path.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Annotated, Any

import typer
import yaml

from cvprofiles.pipeline import FullRunResult, run_profile, summary_dict

app = typer.Typer(no_args_is_help=True, add_completion=False)


class BatchError(ValueError):
    """Loud batch-manifest failure (parse / missing file / unknown profile)."""


@dataclass(frozen=True)
class ProfileResult:
    """One profile's frozen run inside a batch."""

    id: str
    run: FullRunResult
    summary: dict[str, Any]


@dataclass(frozen=True)
class BatchResult:
    """All profiles in one batch, keyed by profile id."""

    out_root: Path
    profiles: list[ProfileResult] = field(default_factory=list)

    @property
    def profile_ids(self) -> list[str]:
        return [p.id for p in self.profiles]

    @property
    def by_id(self) -> dict[str, ProfileResult]:
        return {p.id: p for p in self.profiles}


def _resolve_manifest(manifest: Path | str) -> tuple[Path, dict[str, Any]]:
    """Load and validate the batch manifest; returns (manifest_dir, data)."""
    p = Path(manifest)
    if not p.is_file():
        raise BatchError(f"batch manifest not found: {p}")
    try:
        raw = yaml.safe_load(p.read_text())
    except yaml.YAMLError as exc:
        raise BatchError(f"invalid batch manifest YAML: {exc}") from exc
    if not isinstance(raw, dict) or "profiles" not in raw:
        raise BatchError("batch manifest must be a mapping with a 'profiles' list")
    profiles = raw["profiles"]
    if not isinstance(profiles, list) or not profiles:
        raise BatchError("batch manifest 'profiles' must be a non-empty list")
    for entry in profiles:
        if not isinstance(entry, dict):
            raise BatchError("each profile must be a mapping")
        missing = [k for k in ("id", "network", "beta") if k not in entry]
        if missing:
            raise BatchError(f"profile {entry.get('id', '?')!r} missing keys: {missing}")
        if not entry["id"] or not str(entry["id"]).strip():
            raise BatchError("profile id must be a non-empty string")
    return p.parent, raw


def _resolve_profile_paths(
    manifest_dir: Path, entry: dict[str, Any]
) -> tuple[Path, Path]:
    net = Path(entry["network"])
    beta = Path(entry["beta"])
    net = net if net.is_absolute() else manifest_dir / net
    beta = beta if beta.is_absolute() else manifest_dir / beta
    if not net.is_file():
        raise BatchError(f"profile {entry['id']!r} network file not found: {net}")
    if not beta.is_file():
        raise BatchError(f"profile {entry['id']!r} beta file not found: {beta}")
    return net, beta


def run_many(
    *,
    scores: Path | str,
    roles: Path | str,
    manifest: Path | str,
    out_root: Path | str,
    policy: str = "none",
    seed: int = 0,
    title: str = "Construct-validity profile",
    n_boot: int | None = None,
    theta_grid_lambdas: list[float] | None = None,
    delta_grid_deltas: list[float] | None = None,
    anchors: Path | str | None = None,
) -> BatchResult:
    """Run every profile in the manifest against the shared SCORE input.

    Each profile gets its own frozen run directory under ``out_root/<id>/``.
    Returns a BatchResult; raises BatchError on manifest or profile-file
    problems. Empty M* per profile is a clean success.
    """
    manifest_dir, raw = _resolve_manifest(manifest)
    root = Path(out_root)
    root.mkdir(parents=True, exist_ok=True)

    profiles: list[ProfileResult] = []
    seen: set[str] = set()
    for entry in raw["profiles"]:
        pid = str(entry["id"])
        if pid in seen:
            raise BatchError(f"duplicate profile id: {pid!r}")
        seen.add(pid)
        net, beta = _resolve_profile_paths(manifest_dir, entry)
        dest = root / pid
        run = run_profile(
            scores=scores,
            roles=roles,
            network=net,
            beta=beta,
            out_dir=dest,
            policy=policy,  # type: ignore[arg-type]
            seed=seed,
            title=title,
            n_boot=n_boot,
            theta_grid_lambdas=theta_grid_lambdas,
            delta_grid_deltas=delta_grid_deltas,
            anchors=anchors,
        )
        profiles.append(ProfileResult(id=pid, run=run, summary=summary_dict(run)))

    batch_payload = {
        "schema_version": "1",
        "out_root": str(root),
        "profiles": [
            {
                "id": p.id,
                "run_id": p.summary["run_id"],
                "empty": p.summary["empty"],
                "M_star": p.summary["M_star"],
                "rejected": p.summary["rejected"],
                "L": p.summary["L"],
                "U": p.summary["U"],
                "report_html": p.summary["report_html"],
            }
            for p in profiles
        ],
    }
    (root / "batch_summary.json").write_text(
        json.dumps(batch_payload, indent=2, sort_keys=True) + "\n"
    )
    return BatchResult(out_root=root, profiles=profiles)


@app.command("run")
def run_cmd(
    scores: Annotated[
        Path,
        typer.Option("--scores", exists=True, dir_okay=False, help="Shared scores CSV/parquet"),
    ],
    roles: Annotated[
        Path,
        typer.Option("--roles", exists=True, dir_okay=False, help="Shared roles.json"),
    ],
    manifest: Annotated[
        Path,
        typer.Option("--manifest", exists=True, dir_okay=False, help="Batch manifest YAML"),
    ],
    out: Annotated[Path, typer.Option("--out", help="Batch output root")],
    policy: Annotated[
        str, typer.Option("--policy", help="SCORE normalization: none | zscore_measures")
    ] = "none",
    seed: Annotated[int, typer.Option("--seed", min=0)] = 0,
    title: Annotated[str, typer.Option("--title")] = "Construct-validity profile",
    n_boot: Annotated[
        int | None,
        typer.Option("--n-boot", min=0, help="Bootstrap replicates per profile; 0 disables"),
    ] = None,
    theta_grid: Annotated[
        str | None, typer.Option("--theta-grid", help="Comma-separated λ multipliers")
    ] = None,
    delta_grid: Annotated[
        str | None, typer.Option("--delta-grid", help="Comma-separated absolute δ")
    ] = None,
    anchors: Annotated[
        Path | None,
        typer.Option("--anchors", exists=True, dir_okay=False, help="Pre-data θ-anchor YAML"),
    ] = None,
) -> None:
    """SCORE once, profile many. Empty M* in any profile is exit-0 success."""
    grids: list[float] | None = None
    if theta_grid is not None:
        try:
            grids = [float(t) for t in theta_grid.split(",")]
        except ValueError as exc:
            raise typer.BadParameter("theta-grid must be comma-separated floats") from exc
    deltas: list[float] | None = None
    if delta_grid is not None:
        try:
            deltas = [float(d) for d in delta_grid.split(",")]
        except ValueError as exc:
            raise typer.BadParameter("delta-grid must be comma-separated floats") from exc

    try:
        result = run_many(
            scores=scores,
            roles=roles,
            manifest=manifest,
            out_root=out,
            policy=policy,
            seed=seed,
            title=title,
            n_boot=n_boot,
            theta_grid_lambdas=grids,
            delta_grid_deltas=deltas,
            anchors=anchors,
        )
    except BatchError as exc:
        typer.secho(f"error: {exc}", fg=typer.colors.RED, err=True)
        raise typer.Exit(code=1) from exc

    payload = {
        "out_root": str(result.out_root),
        "profiles": [
            {
                "id": p.id,
                "run_id": p.summary["run_id"],
                "empty": p.summary["empty"],
                "M_star": p.summary["M_star"],
                "L": p.summary["L"],
                "U": p.summary["U"],
                "report_html": p.summary["report_html"],
            }
            for p in result.profiles
        ],
    }
    typer.echo(json.dumps(payload, indent=2))
    for p in result.profiles:
        if p.summary["empty"]:
            typer.secho(
                f"profile {p.id!r}: empty M* — clean success",
                fg=typer.colors.YELLOW,
                err=True,
            )
        else:
            typer.secho(
                f"profile {p.id!r}: M*={p.summary['M_star']}  "
                f"[L,U]=[{p.summary['L']}, {p.summary['U']}]",
                fg=typer.colors.GREEN,
                err=True,
            )


if __name__ == "__main__":
    app()
