"""Screen diagnostics wiring (logs/DECISIONS.md 2026-10-19 D1/D2/D3/D9).

Pins: report.json / report.html / summary_dict surface the three blocks;
criteria declarations and the diagnostics never move run_id, M*, [L,U], or
any identify / coverage artifact; CLI stdout stays JSON. The motivating
two-resolution cases are reproduced on committed data.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.report.screen_diagnostics import (
    aux_ceiling,
    criterion_self_consistency,
)
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.score.pipeline import load_roles, load_table, run_score

IDENTITY_ARTIFACTS = (
    "slacks.csv",
    "admissible.json",
    "beta_values.json",
    "range.json",
    "score_manifest.json",
    "network_resolved.json",
    "beta_resolved.json",
    "restrict_bundle.json",
)


def _mini_inputs(mini_dir: Path) -> dict[str, Path]:
    return {
        "scores": mini_dir / "scores.csv",
        "roles": mini_dir / "roles.json",
        "network": mini_dir / "network.yaml",
        "beta": mini_dir / "beta.yaml",
    }


def _roles_with_criteria(mini_dir: Path, dest: Path, criteria: list[str]) -> Path:
    raw = json.loads((mini_dir / "roles.json").read_text())
    raw["criteria"] = criteria
    dest.write_text(json.dumps(raw))
    return dest


def test_report_json_html_and_summary_carry_screen_diagnostics(
    mini_dir: Path, tmp_path: Path
) -> None:
    res = run_profile(**_mini_inputs(mini_dir), out_dir=tmp_path / "run", n_boot=20)
    payload = json.loads((tmp_path / "run" / "report.json").read_text())
    sd = payload["screen_diagnostics"]
    assert sd["purpose"] == "report_only_screen_diagnostics"
    assert set(sd) >= {
        "criterion_self_consistency",
        "aux_ceiling",
        "near_threshold",
        "headline_note",
    }
    # corr_y on y ⇒ y is the default criterion
    crit = sd["criterion_self_consistency"]["criteria"]
    assert [c["criterion"] for c in crit] == ["y"]
    assert sd["near_threshold"]["available"] is True
    html = (tmp_path / "run" / "report.html").read_text()
    assert "Screen diagnostics" in html
    assert "report-only" in html

    summ = summary_dict(res)["screen_diagnostics"]
    assert summ == {
        "n_criteria_self_rejected": sd["criterion_self_consistency"][
            "n_self_rejected"
        ],
        "n_aux_ceiling_flagged": sd["aux_ceiling"]["n_flagged_measures"],
        "n_near_threshold_survivors": sd["near_threshold"][
            "n_near_threshold_survivors"
        ],
        "see": "report.json#screen_diagnostics",
    }


@pytest.mark.parametrize("n_boot", [None, 16])
def test_criteria_and_diagnostics_never_move_the_freeze_or_headline(
    mini_dir: Path, mini_expected_freeze: dict, tmp_path: Path, n_boot: int | None
) -> None:
    inputs = _mini_inputs(mini_dir)
    plain = run_profile(**inputs, out_dir=tmp_path / "plain", n_boot=n_boot)
    roles_c = _roles_with_criteria(
        mini_dir, tmp_path / "roles_c.json", ["m_good", "v_aux"]
    )
    declared = run_profile(
        **{**inputs, "roles": roles_c}, out_dir=tmp_path / "declared", n_boot=n_boot
    )
    assert plain.run_id == declared.run_id
    if n_boot is None:
        assert plain.run_id == mini_expected_freeze["run_id"]
    assert plain.identify.admissible == declared.identify.admissible
    assert (plain.identify.range_L, plain.identify.range_U) == (
        declared.identify.range_L,
        declared.identify.range_U,
    )
    names = list(IDENTITY_ARTIFACTS)
    if n_boot is not None:
        names += ["bootstrap.json", "coverage.json"]
    for name in names:
        a = (tmp_path / "plain" / name).read_bytes()
        b = (tmp_path / "declared" / name).read_bytes()
        if name == "score_manifest.json":
            # the only difference allowed: the echoed criteria pointer list
            ja, jb = json.loads(a), json.loads(b)
            assert jb["roles"].pop("criteria") == ["m_good", "v_aux"]
            assert ja == jb
        else:
            assert a == b, name
    # declared criteria do show up in the report
    sd = declared.report.payload["screen_diagnostics"]
    got = [c["criterion"] for c in sd["criterion_self_consistency"]["criteria"]]
    assert got == ["y", "m_good", "v_aux"]


def test_cli_stdout_is_json_with_screen_summary(
    mini_dir: Path, tmp_path: Path
) -> None:
    proc = subprocess.run(
        [
            sys.executable,
            "-m",
            "cvprofiles",
            "run",
            "--scores",
            str(mini_dir / "scores.csv"),
            "--roles",
            str(mini_dir / "roles.json"),
            "--network",
            str(mini_dir / "network.yaml"),
            "--beta",
            str(mini_dir / "beta.yaml"),
            "--out",
            str(tmp_path / "cli"),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["screen_diagnostics"]["n_near_threshold_survivors"] is None
    assert summary["screen_diagnostics"]["n_criteria_self_rejected"] == 0


# ----------------------------------------- motivating cases (committed data)

TWO_RES = Path(__file__).resolve().parents[1] / "evals" / "wvs_gps_two_resolution"


def _two_res(case: str, scores: str) -> tuple[Any, Any, Any]:
    path = TWO_RES / "data" / "cells_demeaned" / scores
    if not path.is_file():
        pytest.skip(f"missing committed data {path}")
    roles = load_roles(TWO_RES / "roles" / f"{case}.json")
    score = run_score(load_table(path), roles)
    beta_case = case.removesuffix("_llm")
    bundle = run_restrict(
        score.roles,
        TWO_RES / "networks" / f"{case}.yaml",
        TWO_RES / "betas" / f"{beta_case}.yaml",
    )
    return score.frame, score.roles, bundle


def test_trust_cells_criterion_fails_its_own_screen() -> None:
    frame, roles, bundle = _two_res("trust_cells", "trust.csv")
    out = criterion_self_consistency(frame, roles, bundle, delta=bundle.delta)
    (row,) = out["criteria"]
    assert row["criterion"] == "gps_trust_cell"
    assert row["self_rejected"] is True
    assert row["slacks"]["conv_edu_cell"] == pytest.approx(-0.235 - 0.20, abs=5e-4)


def test_patience_cells_phi_exceeds_gps_criterion_on_education() -> None:
    frame, roles, bundle = _two_res("patience_cells_llm", "patience_llm_extension.csv")
    out = aux_ceiling(frame, roles, bundle)
    (row,) = [
        r
        for r in out["rows"]
        if r["restriction"] == "conv_edu_cell"
        and r["measure"] == "m_llm_patience_phi"
        and r["criterion"] == "gps_patience_cell"
    ]
    assert row["assoc_measure"] == pytest.approx(0.640, abs=5e-4)
    assert row["assoc_criterion"] == pytest.approx(0.475, abs=5e-4)
    assert row["exceeds_criterion"] is True
    assert "m_llm_patience_phi" in out["flagged_measures"]
