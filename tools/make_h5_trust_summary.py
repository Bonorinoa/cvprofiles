#!/usr/bin/env python3
"""Generate the tracked H5 Trust evidence summary (reports/summaries/).

Reads the audited proof (evals/h5_trust/proof_summary.json), the frozen-score
manifest, and the diagnostic run (theta-grid + bootstrap) and writes a compact,
allow-listed evidence summary with the owner's approval metadata. Read-only
w.r.t. run artifacts; does not rerun the pipeline.

The proof itself is audited separately by tools/verify_h5_trust.py; this
summary is the paper-facing index, not a duplicate proof.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def _load(path: Path) -> dict:
    return json.loads(path.read_text())


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--diag-root", type=Path, default=Path("reports/runs/h5_trust_diag"))
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--approved-by", default="Augusto")
    parser.add_argument("--status", default="preliminary_paper_facing_evidence")
    args = parser.parse_args()

    proof = _load(args.proof)
    manifest = _load(args.manifest)

    theta_grid = None
    grid_path = args.diag_root / "theta_grid.json"
    if grid_path.exists():
        grid = _load(grid_path)
        theta_grid = {
            "headline_lambda": grid.get("headline_lambda"),
            "rows": [
                {
                    "lambda": r["lambda"],
                    "n_admissible": r["n_admissible"],
                    "admissible": r["admissible"],
                    "empty": r["empty"],
                    "L": r["L"],
                    "U": r["U"],
                }
                for r in grid.get("rows", [])
            ],
        }

    bootstrap = None
    boot_path = args.diag_root / "bootstrap.json"
    if boot_path.exists():
        boot = _load(boot_path)
        bootstrap = {
            "method": boot.get("method"),
            "n_boot": boot.get("n_boot"),
            "band_L": boot.get("band_L"),
            "band_U": boot.get("band_U"),
            "empty_replicate_rate": boot.get("empty_replicate_rate"),
            "degenerate_replicate_rate": boot.get("degenerate_replicate_rate"),
        }

    summary = {
        "artifact": "h5_trust_evidence_summary",
        "schema_version": "1",
        "status": args.status,
        "approved_by": args.approved_by,
        "approved_at": "2026-08-04",
        "boundary": (
            "Preliminary paper-facing evidence per docs/16 amendment 2026-08-04 "
            "and docs/12 entry. Final paper lock and submission claims remain "
            "Augusto's; this is a checkpoint, not a release."
        ),
        "design": "docs/17_H5_Trust_Design.md",
        "package_version": proof.get("settings", {}).get("package_version"),
        "parent_sha": manifest.get("parent_sha"),
        "scores_hash": proof.get("settings", {}).get("scores_hash"),
        "network_hash": proof.get("settings", {}).get("network_hash"),
        "beta_hash": proof.get("settings", {}).get("beta_hash"),
        "universe": manifest.get("universe"),
        "settings": manifest.get("settings"),
        "n_countries": proof.get("settings", {}).get("n_countries"),
        "gates": proof.get("gates"),
        "designed_valid": proof.get("designed_valid"),
        "designed_invalid": proof.get("designed_invalid"),
        "M_star": proof.get("M_star"),
        "L": proof.get("L"),
        "U": proof.get("U"),
        "empty": proof.get("empty"),
        "rejected": proof.get("rejected"),
        "cold_match": proof.get("cold_match"),
        "failures": proof.get("failures"),
        "theta_grid": theta_grid,
        "bootstrap": bootstrap,
        "proof_artifact": "evals/h5_trust/proof_summary.json",
        "run_artifacts": "evals/h5_trust/runs_verify/default",
        "diagnostic_run": str(args.diag_root),
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(summary, indent=2) + "\n")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
