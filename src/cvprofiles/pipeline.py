"""Full SCORE → RESTRICT → IDENTIFY → REPORT composition (v2.0 spine).

Inference layers on top of the four-state spine (all additive diagnostics;
headline [L,U] = min/max B* is never replaced):
- bootstrap over units (percentile band over non-empty replicates)
- θ-grid sensitivity surface (λ scales thresholds; NOT in the freeze preimage)
- δ-grid tolerance surface (absolute δ; NOT in the freeze preimage)
- θ-anchor audit (schema'd anchors.yaml; documentation, NOT in the preimage)

Freeze rule (docs/12): ``n_boot`` is normalized with
``freeze.normalize_n_boot`` (< 1 ⇒ JSON null) before the preimage is built,
so bootstrap-off runs keep their run_ids bit-stable. Grids and anchors are
diagnostic viewports: same bundle + different grid/± anchors ⇒ same run_id,
different artifacts. Run directories must reflect exactly the layers this run
produced, so stale ``bootstrap.json`` / ``theta_grid.json`` /
``delta_grid.json`` / ``anchors.json`` from a previous run into the same
directory are removed when the layer is off.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cvprofiles import __version__
from cvprofiles.anchors.pipeline import anchors_payload, parse_anchors, validate_completeness
from cvprofiles.freeze import build_freeze_bundle, compute_run_id, normalize_n_boot
from cvprofiles.identify.pipeline import IdentifyResult, run_identify, write_identify_artifacts
from cvprofiles.inference.bootstrap import BootstrapResult, bootstrap_payload, run_bootstrap
from cvprofiles.inference.delta_grid import DeltaGridResult, delta_grid_payload, run_delta_grid
from cvprofiles.inference.theta_grid import ThetaGridResult, run_theta_grid, theta_grid_payload
from cvprofiles.report.pipeline import ReportResult, write_report
from cvprofiles.restrict.pipeline import RestrictBundle, run_restrict, write_restrict_artifacts
from cvprofiles.schemas.run import RunManifest
from cvprofiles.score.pipeline import (
    NormPolicy,
    ScoreResult,
    load_roles,
    load_table,
    run_score,
    write_score_artifacts,
)


@dataclass(frozen=True)
class FullRunResult:
    """End-to-end engine run outputs."""

    run_id: str
    out_dir: Path
    score: ScoreResult
    restrict: RestrictBundle
    identify: IdentifyResult
    report: ReportResult
    run_manifest: RunManifest
    artifact_paths: dict[str, str]
    bootstrap: BootstrapResult | None = None
    theta_grid: ThetaGridResult | None = None
    delta_grid: DeltaGridResult | None = None
    anchors_hash: str | None = None


def run_profile(
    *,
    scores: Path | str,
    roles: Path | str,
    network: Path | str,
    beta: Path | str,
    out_dir: Path | str | None = None,
    policy: NormPolicy = "none",
    seed: int = 0,
    title: str = "Construct-validity profile",
    write_parquet: bool = True,
    n_boot: int | None = None,
    theta_grid_lambdas: Sequence[float] | None = None,
    delta_grid_deltas: Sequence[float] | None = None,
    anchors: Path | str | None = None,
) -> FullRunResult:
    """Compose four states (+ v1.1/v2.0 inference layers) and write a frozen run dir.

    Empty M* is a clean success path (report explains; no exception).
    Fail loud only on schema / IO / binding / evaluator errors.

    Inference layers (off unless requested):
      n_boot >= 1           → bootstrap over units (seed = the run's seed).
      theta_grid_lambdas    → θ-sensitivity surface (diagnostic; excluded
                              from the freeze preimage by design).
      delta_grid_deltas     → δ-tolerance surface (diagnostic; absolute δ
                              values; excluded from the freeze preimage).
      anchors               → pre-data θ-anchor file (documentation; parsed,
                              completeness-checked, hashed; EXCLUDED from the
                              freeze preimage — same bundle ± anchors ⇒ same
                              run_id, different anchors.json).
    """
    n_boot_norm = normalize_n_boot(n_boot)
    grid = list(theta_grid_lambdas) if theta_grid_lambdas else None
    grid_deltas = list(delta_grid_deltas) if delta_grid_deltas else None

    anchors_config = None
    anchors_payload_dict: dict[str, Any] | None = None
    if anchors is not None:
        anchors_config = parse_anchors(anchors)  # completeness checked after RESTRICT

    roles_m = load_roles(roles)
    df = load_table(scores)
    score = run_score(df, roles_m, policy=policy)
    restrict = run_restrict(score.roles, network, beta)

    anchors_hash_value: str | None = None
    if anchors_config is not None:
        validate_completeness(anchors_config, restrict.network)
        anchors_payload_dict = anchors_payload(anchors_config)
        anchors_hash_value = anchors_payload_dict["anchors_hash"]

    if score.manifest.scores_hash is None:
        raise RuntimeError("SCORE did not set scores_hash")

    freeze = build_freeze_bundle(
        scores_hash=score.manifest.scores_hash,
        network_hash=restrict.network_hash,
        beta_hash=restrict.beta_hash,
        package_version=__version__,
        seed=seed,
        delta=float(restrict.delta),
        n_boot=n_boot_norm,
        config={},
    )
    run_id = compute_run_id(
        scores_hash=freeze.scores_hash,
        network_hash=freeze.network_hash,
        beta_hash=freeze.beta_hash,
        package_version=freeze.package_version,
        seed=freeze.seed,
        delta=freeze.delta,
        schema_version=freeze.schema_version,
        n_boot=freeze.n_boot,
        config=freeze.config,
    )

    if out_dir is None:
        dest = Path("reports") / "runs" / run_id
    else:
        dest = Path(out_dir)
    dest.mkdir(parents=True, exist_ok=True)

    # Run directories mirror exactly the layers this run produces: drop stale
    # inference artifacts from any previous run into the same directory.
    if n_boot_norm is None and (dest / "bootstrap.json").exists():
        (dest / "bootstrap.json").unlink()
    if grid is None and (dest / "theta_grid.json").exists():
        (dest / "theta_grid.json").unlink()
    if grid_deltas is None and (dest / "delta_grid.json").exists():
        (dest / "delta_grid.json").unlink()
    if anchors is None and (dest / "anchors.json").exists():
        (dest / "anchors.json").unlink()

    identify = run_identify(score.frame, score.roles, restrict)

    # --- v1.1/v2.0 inference layers (additive; headline [L,U] untouched) ---
    boot: BootstrapResult | None = None
    if n_boot_norm is not None:
        boot = run_bootstrap(
            score.frame, score.roles, restrict, n_boot=n_boot_norm, seed=seed
        )

    grid_result: ThetaGridResult | None = None
    if grid is not None:
        grid_result = run_theta_grid(score.frame, score.roles, restrict, grid)

    delta_grid_result: DeltaGridResult | None = None
    if grid_deltas is not None:
        delta_grid_result = run_delta_grid(
            score.frame, score.roles, restrict, grid_deltas
        )

    paths: dict[str, Path] = {}
    paths.update(write_score_artifacts(score, dest, parquet=write_parquet))
    paths.update(write_restrict_artifacts(restrict, dest))
    paths.update(write_identify_artifacts(identify, dest))
    if boot is not None:
        boot_path = dest / "bootstrap.json"
        boot_path.write_text(json.dumps(bootstrap_payload(boot), indent=2, sort_keys=True) + "\n")
        paths["bootstrap.json"] = boot_path
    if grid_result is not None:
        grid_path = dest / "theta_grid.json"
        grid_path.write_text(
            json.dumps(theta_grid_payload(grid_result), indent=2, sort_keys=True) + "\n"
        )
        paths["theta_grid.json"] = grid_path
    if delta_grid_result is not None:
        dgrid_path = dest / "delta_grid.json"
        dgrid_path.write_text(
            json.dumps(delta_grid_payload(delta_grid_result), indent=2, sort_keys=True)
            + "\n"
        )
        paths["delta_grid.json"] = dgrid_path
    if anchors_payload_dict is not None and anchors_hash_value is not None:
        anchors_path = dest / "anchors.json"
        anchors_path.write_text(
            json.dumps(anchors_payload_dict, indent=2, sort_keys=True) + "\n"
        )
        paths["anchors.json"] = anchors_path

    created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    artifact_paths = {k: str(v.name) for k, v in paths.items()}

    run_manifest = RunManifest(
        run_id=run_id,
        freeze=freeze,
        created_at=created_at,
        artifact_paths=artifact_paths,
        notes=(
            "v2.0 spine; inference: bootstrap + theta-grid + delta-grid "
            "+ anchors (diagnostic)"
        ),
        anchors_hash=anchors_hash_value,
    )
    man_path = dest / "run_manifest.json"
    man_path.write_text(run_manifest.model_dump_json(indent=2) + "\n")
    artifact_paths["run_manifest.json"] = "run_manifest.json"

    report = write_report(
        run_manifest=run_manifest,
        restrict=restrict,
        identify=identify,
        out_dir=dest,
        title=title,
        bootstrap=bootstrap_payload(boot) if boot is not None else None,
        theta_grid=theta_grid_payload(grid_result) if grid_result is not None else None,
        delta_grid=(
            delta_grid_payload(delta_grid_result)
            if delta_grid_result is not None
            else None
        ),
        anchors=anchors_payload_dict,
    )
    artifact_paths["report.html"] = report.html_path.name
    artifact_paths["report.json"] = report.json_path.name

    # Refresh manifest with report paths
    run_manifest = RunManifest(
        run_id=run_id,
        freeze=freeze,
        created_at=created_at,
        artifact_paths=artifact_paths,
        notes=run_manifest.notes,
        anchors_hash=anchors_hash_value,
    )
    man_path.write_text(run_manifest.model_dump_json(indent=2) + "\n")

    return FullRunResult(
        run_id=run_id,
        out_dir=dest,
        score=score,
        restrict=restrict,
        identify=identify,
        report=report,
        run_manifest=run_manifest,
        artifact_paths=artifact_paths,
        bootstrap=boot,
        theta_grid=grid_result,
        delta_grid=delta_grid_result,
        anchors_hash=anchors_hash_value,
    )


def summary_dict(result: FullRunResult) -> dict[str, Any]:
    """Small console/JSON summary for CLI and demos (additive keys only)."""
    ident = result.identify
    boot_summary: dict[str, Any] | None = None
    if result.bootstrap is not None:
        b = result.bootstrap
        boot_summary = {
            "n_boot": b.n_boot,
            "seed": b.seed_used,
            "band_L": b.band_L,
            "band_U": b.band_U,
            "replicates_nonempty": b.replicates_nonempty,
            "replicates_empty": b.replicates_empty,
            "replicates_degenerate": b.replicates_degenerate,
            "empty_replicate_rate": b.empty_replicate_rate,
            "degenerate_replicate_rate": b.degenerate_replicate_rate,
            "note": b.note,
            "artifact": "bootstrap.json",
        }
    grid_summary: dict[str, Any] | None = None
    if result.theta_grid is not None:
        g = result.theta_grid
        grid_summary = {
            "lambdas": list(g.lambdas),
            "rows": len(g.rows),
            "headline_lambda": 1.0,
            "artifact": "theta_grid.json",
        }
    grid2_summary: dict[str, Any] | None = None
    if result.delta_grid is not None:
        g2 = result.delta_grid
        grid2_summary = {
            "deltas": list(g2.deltas),
            "rows": len(g2.rows),
            "headline_delta": g2.headline_delta,
            "artifact": "delta_grid.json",
        }
    return {
        "run_id": result.run_id,
        "out_dir": str(result.out_dir),
        "empty": ident.empty,
        "M_star": ident.admissible,
        "rejected": ident.rejected,
        "L": ident.range_L,
        "U": ident.range_U,
        "point_id": ident.point_id,
        "scores_hash": result.score.manifest.scores_hash,
        "network_hash": result.restrict.network_hash,
        "beta_hash": result.restrict.beta_hash,
        "n_boot": result.run_manifest.freeze.n_boot,
        "bootstrap": boot_summary,
        "theta_grid": grid_summary,
        "delta_grid": grid2_summary,
        "anchors_hash": result.anchors_hash,
        "report_html": str(result.report.html_path),
        "report_json": str(result.report.json_path),
    }
