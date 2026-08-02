"""Package-path synthetic battery tests (M8). Museum must stay unimported."""

from __future__ import annotations

import ast
from pathlib import Path

import pytest

from cvprofiles.identify.pipeline import run_identify
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.score.pipeline import run_score
from cvprofiles.synth.battery import run_battery, run_seed, write_battery_summary
from cvprofiles.synth.dgp import LABELS, SCENARIOS, make_dgp, roles_for_menu
from cvprofiles.synth.metrics import cold_cores_equal
from cvprofiles.synth.oracle_r import beta_corr_y, network_for

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_src_has_no_museum_import() -> None:
    """AST import graph only — docstrings may name the museum to forbid it."""
    src = REPO_ROOT / "src" / "cvprofiles"
    offenders: list[str] = []
    for path in src.rglob("*.py"):
        tree = ast.parse(path.read_text(), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module:
                mod = node.module
                if "v0_poc" in mod or "evals.synthetic" in mod:
                    offenders.append(f"{path.relative_to(REPO_ROOT)}:from {mod}")
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if "v0_poc" in alias.name or "evals.synthetic" in alias.name:
                        offenders.append(
                            f"{path.relative_to(REPO_ROOT)}:import {alias.name}"
                        )
    assert not offenders, offenders
    assert (REPO_ROOT / "evals" / "synthetic" / "v0_poc.py").is_file()


def test_seed0_membership_oracle_and_empty() -> None:
    """Directional membership smoke (seed 0)."""
    _, m_easy = run_seed("oracle_easy", 0, n=1000, check_cold=False)
    assert m_easy.empty is False
    assert m_easy.anchor_in_M is True
    assert m_easy.false_admissions == []
    assert m_easy.near_miss_admitted == []
    assert "m_dict" in m_easy.M_star
    assert "m_slop" not in m_easy.M_star
    assert m_easy.h1b is True

    _, m_slop = run_seed("oracle_with_slop", 0, n=1000, check_cold=False)
    assert m_slop.false_admissions == []
    assert m_slop.anchor_in_M is True
    assert "m_slop" not in m_slop.M_star

    _, m_harsh = run_seed("harsh_theta", 0, n=1000, check_cold=False)
    assert m_harsh.empty is True
    assert m_harsh.M_star == []
    assert m_harsh.L is None and m_harsh.U is None

    _, m_all = run_seed("all_invalid", 0, n=1000, check_cold=False)
    assert m_all.empty is True
    assert m_all.false_admissions == []


def test_slop_path_distinct_easy_vs_with_slop() -> None:
    """oracle_with_slop must stress confounded β differently from oracle_easy."""
    id_easy, _ = run_seed("oracle_easy", 0, n=1000, check_cold=False)
    id_slop, _ = run_seed("oracle_with_slop", 0, n=1000, check_cold=False)
    b_easy = id_easy.beta_values["m_slop"]
    b_slop = id_slop.beta_values["m_slop"]
    assert abs(b_slop - b_easy) > 0.02
    # Valids unchanged enough that anchor still in both
    assert "m_dict" in id_easy.admissible and "m_dict" in id_slop.admissible


def test_cold_cores_equal_unit() -> None:
    roles = roles_for_menu()
    net = network_for("oracle_easy")
    beta = beta_corr_y()
    df = make_dgp("oracle_easy", 500, 1)
    s1 = run_score(df, roles, policy="none")
    r1 = run_restrict(roles, net, beta)
    i1 = run_identify(s1.frame, roles, r1)
    df2 = make_dgp("oracle_easy", 500, 1)
    s2 = run_score(df2, roles, policy="none")
    r2 = run_restrict(roles, net, beta)
    i2 = run_identify(s2.frame, roles, r2)
    assert cold_cores_equal(i1, i2)


def test_labels_not_in_identify_inputs() -> None:
    """Sanity: LABELS keys are measures; identify only sees frame columns + R."""
    assert set(LABELS) >= {"m_dict", "m_slop", "m_near", "m_floor"}
    # No label column in DGP frame
    df = make_dgp("oracle_easy", 100, 0)
    assert "label" not in df.columns
    assert "oracle_label" not in df.columns


@pytest.mark.slow
def test_full_battery_gates_green() -> None:
    """Full M8 mini battery — H1a/H1b/H3/H4. H1_latent not gated."""
    result = run_battery(
        scenarios=SCENARIOS,
        seeds=(0, 1, 2, 3, 4),
        n=1000,
        check_cold=True,
    )
    # Explicit gate checks (clearer failure messages than only passed)
    for sc in ("oracle_easy", "oracle_with_slop"):
        assert result.gates[f"H1a_fa_{sc}"] is True, result.gate_notes[f"H1a_fa_{sc}"]
        assert result.gates[f"H1a_anchor_{sc}"] is True, result.gate_notes[f"H1a_anchor_{sc}"]
        assert result.gates[f"H1b_{sc}"] is True, result.gate_notes[f"H1b_{sc}"]
        agg = result.scenarios[sc]
        assert agg.fa_rate == 0.0
        assert agg.anchor_rate == 1.0
        assert agg.h1b_rate == 1.0
        assert agg.invalid_ever_admitted == []
    for sc in ("harsh_theta", "all_invalid"):
        assert result.gates[f"H3_{sc}"] is True, result.gate_notes[f"H3_{sc}"]
        assert result.scenarios[sc].empty_rate == 1.0
        assert result.scenarios[sc].fa_rate == 0.0
    assert result.gates["H4_cold"] is True, result.gate_notes["H4_cold"]
    assert result.passed is True

    # H1_latent is diagnostic — may be 0; must be present on oracle rows
    for sc in ("oracle_easy", "oracle_with_slop"):
        lat = result.scenarios[sc].h1_latent_rate
        assert lat is not None  # computed on nonempty seeds
        # Do NOT require lat == 1.0


def test_write_summary_roundtrip(tmp_path: Path) -> None:
    # Tiny battery for IO smoke (still real gates on 1 seed if DGP healthy)
    result = run_battery(
        scenarios=("oracle_easy", "harsh_theta"),
        seeds=(0,),
        n=800,
        check_cold=True,
    )
    path = write_battery_summary(result, tmp_path / "summary.json")
    assert path.is_file()
    text = path.read_text()
    assert "battery_version" in text
    assert "gates" in text
