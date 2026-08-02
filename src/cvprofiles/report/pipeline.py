"""Thin REPORT: JSON dump + one-page HTML audit trail (no bootstrap panels)."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape

from cvprofiles.identify.pipeline import IdentifyResult
from cvprofiles.restrict.pipeline import RestrictBundle
from cvprofiles.schemas.run import RunManifest


class ReportError(ValueError):
    """Loud REPORT failure (templating / IO)."""


@dataclass(frozen=True)
class ReportResult:
    """Paths written by REPORT."""

    html_path: Path
    json_path: Path
    payload: dict[str, Any]


def _templates_dir() -> Path:
    return Path(__file__).resolve().parent / "templates"


def build_report_payload(
    *,
    run_manifest: RunManifest,
    restrict: RestrictBundle,
    identify: IdentifyResult,
    title: str = "Construct-validity profile",
) -> dict[str, Any]:
    """Machine-complete report dict (also drives HTML)."""
    slacks_dict: dict[str, dict[str, float]] = {}
    for m in identify.measures:
        slacks_dict[m] = {
            rid: float(identify.slacks.at[m, rid]) for rid in identify.restriction_ids
        }

    return {
        "schema_version": "1",
        "title": title,
        "run_id": run_manifest.run_id,
        "package_version": run_manifest.freeze.package_version,
        "created_at": run_manifest.created_at,
        "freeze": run_manifest.freeze.model_dump(mode="json"),
        "scores_hash": run_manifest.freeze.scores_hash,
        "network_hash": run_manifest.freeze.network_hash,
        "beta_hash": run_manifest.freeze.beta_hash,
        "delta": identify.delta,
        "seed": run_manifest.freeze.seed,
        "network_name": restrict.network.name,
        "beta_type": restrict.beta.type,
        "outcome": restrict.beta.outcome,
        "measures": identify.measures,
        "restriction_ids": identify.restriction_ids,
        "restrictions": [
            r.model_dump(mode="json") for r in restrict.network.restrictions
        ],
        "admissible": identify.admissible,
        "rejected": identify.rejected,
        "beta_values": identify.beta_values,
        "slacks": slacks_dict,
        "L": identify.range_L,
        "U": identify.range_U,
        "empty": identify.empty,
        "point_id": identify.point_id,
        "range": {
            "L": identify.range_L,
            "U": identify.range_U,
            "empty": identify.empty,
            "point_id": identify.point_id,
            "method": "min_max_B_star",
            "bootstrap": None,
            "note": "v1.0 range is min/max of beta on M*; bootstrap deferred to v1.1",
        },
        "artifact_paths": run_manifest.artifact_paths,
    }


def render_html(payload: dict[str, Any]) -> str:
    """Render one-page HTML from report payload."""
    env = Environment(
        loader=FileSystemLoader(str(_templates_dir())),
        autoescape=select_autoescape(["html", "xml"]),
    )
    template = env.get_template("report.html.j2")
    return template.render(**payload)


def write_report(
    *,
    run_manifest: RunManifest,
    restrict: RestrictBundle,
    identify: IdentifyResult,
    out_dir: Path | str,
    title: str = "Construct-validity profile",
) -> ReportResult:
    """Write report.html + report.json under out_dir."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(
        run_manifest=run_manifest,
        restrict=restrict,
        identify=identify,
        title=title,
    )
    json_path = out / "report.json"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    try:
        html = render_html(payload)
    except Exception as exc:
        raise ReportError(f"HTML render failed: {exc}") from exc
    html_path = out / "report.html"
    html_path.write_text(html)
    return ReportResult(html_path=html_path, json_path=json_path, payload=payload)
