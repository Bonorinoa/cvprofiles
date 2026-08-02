"""Full SCORE → RESTRICT → IDENTIFY → REPORT composition (v1.0 thin spine)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from cvprofiles import __version__
from cvprofiles.freeze import build_freeze_bundle, compute_run_id
from cvprofiles.identify.pipeline import IdentifyResult, run_identify, write_identify_artifacts
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
) -> FullRunResult:
    """Compose four states and write a frozen run directory.

    Empty M* is a clean success path (report explains; no exception).
    Fail loud only on schema / IO / binding / evaluator errors.
    """
    roles_m = load_roles(roles)
    df = load_table(scores)

    score = run_score(df, roles_m, policy=policy)
    restrict = run_restrict(score.roles, network, beta)

    if score.manifest.scores_hash is None:
        raise RuntimeError("SCORE did not set scores_hash")

    freeze = build_freeze_bundle(
        scores_hash=score.manifest.scores_hash,
        network_hash=restrict.network_hash,
        beta_hash=restrict.beta_hash,
        package_version=__version__,
        seed=seed,
        delta=float(restrict.delta),
        n_boot=None,
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

    identify = run_identify(score.frame, score.roles, restrict)

    paths: dict[str, Path] = {}
    paths.update(write_score_artifacts(score, dest, parquet=write_parquet))
    paths.update(write_restrict_artifacts(restrict, dest))
    paths.update(write_identify_artifacts(identify, dest))

    created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    artifact_paths = {k: str(v.name) for k, v in paths.items()}

    run_manifest = RunManifest(
        run_id=run_id,
        freeze=freeze,
        created_at=created_at,
        artifact_paths=artifact_paths,
        notes="v1.0 thin spine; bootstrap deferred to v1.1",
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
    )


def summary_dict(result: FullRunResult) -> dict[str, Any]:
    """Small console/JSON summary for CLI and demos."""
    ident = result.identify
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
        "report_html": str(result.report.html_path),
        "report_json": str(result.report.json_path),
    }
