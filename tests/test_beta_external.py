"""Bring-your-own β (`type: external` + beta_estimates.csv) — contract tests.

Locked semantics (logs/DECISIONS.md 2026-10-20, spec reports/specs/conservative_cr_spec.md §7):
- β type ``external`` reads ``beta_estimates.csv`` (measure, beta_hat, se + optional
  df / n_clusters / documentation columns). Rows must equal the menu exactly.
- For that type the headline is [min, max] of ``beta_hat`` over M*; the engine fits
  nothing. ``outcome`` is a descriptive label, not bound to a SCORE column.
- Canonical-table SHA-256 is folded into ``beta_hash`` for ``external`` only; every
  other β type's ``beta_hash`` is byte-identical. Row/column order never moves it.
- Bootstrap replicates hold external β fixed (admission variability only), labeled.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pandas as pd
import pytest
import yaml

from cvprofiles.freeze import hash_beta, hash_beta_estimates, hash_canonical_json
from cvprofiles.identify.pipeline import run_identify
from cvprofiles.inference.bootstrap import run_bootstrap
from cvprofiles.inference.coverage import compute_coverage
from cvprofiles.pipeline import run_profile, summary_dict
from cvprofiles.restrict.pipeline import RestrictError, load_beta_estimates, run_restrict
from cvprofiles.schemas.beta import BetaSpec

EXTERNAL = {"schema_version": "1", "type": "external", "outcome": "log_wage_fe", "params": {}}
ROWS = [
    {"measure": "m_good", "beta_hat": 0.41, "se": 0.10},
    {"measure": "m_weak", "beta_hat": 0.22, "se": 0.12},
    {"measure": "m_slop", "beta_hat": 0.90, "se": 0.05},
]
MENU = ["m_good", "m_weak", "m_slop"]


def _write_csv(path: Path, rows: list[dict], columns: list[str] | None = None) -> Path:
    df = pd.DataFrame(rows)
    if columns is not None:
        df = df[columns]
    df.to_csv(path, index=False)
    return path


def _write_beta(path: Path, spec: dict) -> Path:
    path.write_text(yaml.safe_dump(spec))
    return path


@pytest.fixture
def est_csv(tmp_path: Path) -> Path:
    return _write_csv(tmp_path / "beta_estimates.csv", ROWS)


# --- schema + loader -------------------------------------------------------------


def test_beta_spec_accepts_external_type() -> None:
    spec = BetaSpec.model_validate(EXTERNAL)
    assert spec.type == "external"


def test_load_beta_estimates_keys_rows_by_measure(est_csv: Path) -> None:
    est = load_beta_estimates(est_csv, MENU)
    assert set(est.rows) == set(MENU)
    assert est.rows["m_weak"].beta_hat == 0.22
    assert est.rows["m_weak"].se == 0.12
    assert est.columns == ("measure", "beta_hat", "se")
    assert est.beta_hat == {"m_good": 0.41, "m_weak": 0.22, "m_slop": 0.90}
    assert len(est.estimates_hash) == 64


@pytest.mark.parametrize(
    ("rows", "match"),
    [
        (ROWS[:2], "missing"),
        (ROWS + [{"measure": "m_extra", "beta_hat": 0.1, "se": 0.1}], "not in the menu"),
        (ROWS + [ROWS[0]], "duplicate"),
        ([{**ROWS[0], "se": 0.0}, *ROWS[1:]], "se"),
        ([{**ROWS[0], "se": -0.1}, *ROWS[1:]], "se"),
        ([{**ROWS[0], "beta_hat": float("nan")}, *ROWS[1:]], "beta_hat"),
        ([{**ROWS[0], "df": 0.0}, *ROWS[1:]], "df"),
        ([{**ROWS[0], "n_clusters": 1}, *ROWS[1:]], "n_clusters"),
        ([{**r, "weird": 1} for r in ROWS], "unknown column"),
    ],
)
def test_load_beta_estimates_fails_loud(
    tmp_path: Path, rows: list[dict], match: str
) -> None:
    path = _write_csv(tmp_path / "bad.csv", rows)
    with pytest.raises(RestrictError, match=match):
        load_beta_estimates(path, MENU)


def test_load_beta_estimates_requires_core_columns(tmp_path: Path) -> None:
    path = _write_csv(
        tmp_path / "no_se.csv", [{"measure": r["measure"], "beta_hat": r["beta_hat"]} for r in ROWS]
    )
    with pytest.raises(RestrictError, match="se"):
        load_beta_estimates(path, MENU)


def test_cluster_df_rule(tmp_path: Path) -> None:
    rows = [
        {**ROWS[0], "n_clusters": 41},
        {**ROWS[1], "n_clusters": 41, "df": 12.5},
        {**ROWS[2]},
    ]
    est = load_beta_estimates(_write_csv(tmp_path / "cl.csv", rows), MENU)
    assert est.rows["m_good"].critical_df() == 40.0  # df = n_clusters - 1
    assert est.rows["m_weak"].critical_df() == 12.5  # explicit df wins
    assert est.rows["m_slop"].critical_df() is None  # normal critical values


# --- hashing ---------------------------------------------------------------------


def test_estimates_hash_ignores_row_and_column_order(tmp_path: Path, est_csv: Path) -> None:
    a = load_beta_estimates(est_csv, MENU).estimates_hash
    shuffled = _write_csv(tmp_path / "b.csv", list(reversed(ROWS)), ["se", "measure", "beta_hat"])
    assert load_beta_estimates(shuffled, MENU).estimates_hash == a


def test_estimates_hash_moves_with_content(tmp_path: Path, est_csv: Path) -> None:
    a = load_beta_estimates(est_csv, MENU).estimates_hash
    changed = _write_csv(tmp_path / "c.csv", [{**ROWS[0], "beta_hat": 0.4100001}, *ROWS[1:]])
    assert load_beta_estimates(changed, MENU).estimates_hash != a
    documented = _write_csv(tmp_path / "d.csv", [{**r, "vcov": "CR1"} for r in ROWS])
    assert load_beta_estimates(documented, MENU).estimates_hash != a


def test_estimates_hash_int_and_float_df_agree(tmp_path: Path) -> None:
    p_int = tmp_path / "i.csv"
    p_int.write_text("measure,beta_hat,se,df\nm_good,0.41,0.1,40\nm_weak,0.22,0.12,40\nm_slop,0.9,0.05,40\n")
    p_flt = tmp_path / "f.csv"
    p_flt.write_text(
        "measure,beta_hat,se,df\nm_good,0.41,0.1,40.0\nm_weak,0.22,0.12,40.0\nm_slop,0.9,0.05,40.0\n"
    )
    assert (
        load_beta_estimates(p_int, MENU).estimates_hash
        == load_beta_estimates(p_flt, MENU).estimates_hash
    )


def test_hash_beta_estimates_canonical_bytes() -> None:
    est_rows = [
        {"measure": "b", "beta_hat": 0.5, "se": 0.25},
        {"measure": "a", "beta_hat": 1.0, "se": 0.125},
    ]
    from cvprofiles.freeze import beta_estimates_canonical_csv_bytes

    raw = beta_estimates_canonical_csv_bytes(est_rows, ["measure", "beta_hat", "se"])
    assert raw == b"measure,beta_hat,se\na,1,0.125\nb,0.5,0.25\n"
    assert hash_beta_estimates(est_rows, ["measure", "beta_hat", "se"]) == (
        __import__("hashlib").sha256(raw).hexdigest()
    )


def test_hash_beta_unchanged_for_existing_types(mini_beta, mini_expected_freeze) -> None:
    assert hash_beta(mini_beta) == mini_expected_freeze["beta_hash"]


def test_hash_beta_external_folds_estimates_hash() -> None:
    spec = BetaSpec.model_validate(EXTERNAL)
    h = "a" * 64
    assert hash_beta(spec, beta_estimates_hash=h) == hash_canonical_json(
        {"beta": spec.model_dump(mode="json"), "beta_estimates_hash": h}
    )
    with pytest.raises(ValueError, match="beta_estimates_hash"):
        hash_beta(spec)


def test_hash_beta_rejects_estimates_hash_for_engine_types(mini_beta) -> None:
    with pytest.raises(ValueError, match="external"):
        hash_beta(mini_beta, beta_estimates_hash="a" * 64)


# --- RESTRICT binding --------------------------------------------------------------


def test_run_restrict_external_binds_estimates(mini_roles, mini_network, est_csv) -> None:
    bundle = run_restrict(mini_roles, mini_network, EXTERNAL, beta_estimates=est_csv)
    assert bundle.beta_estimates is not None
    assert bundle.beta_hash == hash_beta(
        bundle.beta, beta_estimates_hash=bundle.beta_estimates.estimates_hash
    )


def test_run_restrict_external_requires_estimates(mini_roles, mini_network) -> None:
    with pytest.raises(RestrictError, match="beta_estimates"):
        run_restrict(mini_roles, mini_network, EXTERNAL)


def test_run_restrict_estimates_require_external_type(
    mini_roles, mini_network, mini_beta, est_csv
) -> None:
    with pytest.raises(RestrictError, match="external"):
        run_restrict(mini_roles, mini_network, mini_beta, beta_estimates=est_csv)


def test_run_restrict_external_rejects_params(mini_roles, mini_network, est_csv) -> None:
    with pytest.raises(RestrictError, match="params"):
        run_restrict(
            mini_roles,
            mini_network,
            {**EXTERNAL, "params": {"controls": ["v_aux"]}},
            beta_estimates=est_csv,
        )


# --- IDENTIFY headline + bootstrap --------------------------------------------------


def test_external_headline_is_min_max_beta_hat_on_survivors(
    mini_scores_df, mini_roles, mini_network, est_csv
) -> None:
    bundle = run_restrict(mini_roles, mini_network, EXTERNAL, beta_estimates=est_csv)
    res = run_identify(mini_scores_df, mini_roles, bundle)
    assert res.beta_values == {"m_good": 0.41, "m_weak": 0.22, "m_slop": 0.90}
    assert set(res.admissible) == {"m_good", "m_weak"}
    assert (res.range_L, res.range_U) == (0.22, 0.41)


def test_external_beta_held_fixed_in_bootstrap(
    mini_scores_df, mini_roles, mini_network, est_csv
) -> None:
    bundle = run_restrict(mini_roles, mini_network, EXTERNAL, beta_estimates=est_csv)
    boot = run_bootstrap(mini_scores_df, mini_roles, bundle, n_boot=40, seed=5)
    values = {0.41, 0.22, 0.90}
    assert set(boot.L_samples) <= values
    assert set(boot.U_samples) <= values
    cov = compute_coverage(boot, mini_scores_df, mini_roles, bundle)
    assert cov.note is not None and "external" in cov.note


# --- full pipeline + CLI -----------------------------------------------------------


def _run(mini_dir: Path, tmp: Path, est: Path, name: str):
    beta = _write_beta(tmp / f"{name}_beta.yaml", EXTERNAL)
    return run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=beta,
        beta_estimates=est,
        out_dir=tmp / name,
    )


def test_external_run_id_tracks_table_content_not_order(
    mini_dir: Path, tmp_path: Path, est_csv: Path
) -> None:
    a = _run(mini_dir, tmp_path, est_csv, "a")
    reordered = _write_csv(tmp_path / "r.csv", list(reversed(ROWS)))
    b = _run(mini_dir, tmp_path, reordered, "b")
    changed = _write_csv(tmp_path / "x.csv", [{**ROWS[0], "se": 0.11}, *ROWS[1:]])
    c = _run(mini_dir, tmp_path, changed, "c")
    assert a.run_id == b.run_id
    assert a.run_id != c.run_id
    assert (a.identify.range_L, a.identify.range_U) == (0.22, 0.41)


def test_external_run_writes_estimates_artifact(
    mini_dir: Path, tmp_path: Path, est_csv: Path
) -> None:
    res = _run(mini_dir, tmp_path, est_csv, "art")
    est_json = json.loads((res.out_dir / "beta_estimates.json").read_text())
    assert est_json["beta_estimates_hash"] == res.restrict.beta_estimates.estimates_hash
    assert [r["measure"] for r in est_json["rows"]] == sorted(MENU)
    meta = json.loads((res.out_dir / "restrict_bundle.json").read_text())
    assert meta["beta_estimates_hash"] == est_json["beta_estimates_hash"]
    assert summary_dict(res)["beta_estimates_hash"] == est_json["beta_estimates_hash"]
    report = json.loads((res.out_dir / "report.json").read_text())
    assert report["beta_estimates_hash"] == est_json["beta_estimates_hash"]
    assert "supplied externally" in (res.out_dir / "report.html").read_text()


def test_engine_beta_run_has_no_estimates_artifact(mini_dir: Path, tmp_path: Path) -> None:
    res = run_profile(
        scores=mini_dir / "scores.csv",
        roles=mini_dir / "roles.json",
        network=mini_dir / "network.yaml",
        beta=mini_dir / "beta.yaml",
        out_dir=tmp_path / "plain",
    )
    assert not (res.out_dir / "beta_estimates.json").exists()
    meta = json.loads((res.out_dir / "restrict_bundle.json").read_text())
    assert "beta_estimates_hash" not in meta
    assert summary_dict(res)["beta_estimates_hash"] is None


def test_cli_beta_estimates_flag(mini_dir: Path, tmp_path: Path, est_csv: Path) -> None:
    beta = _write_beta(tmp_path / "beta_ext.yaml", EXTERNAL)
    cmd = [
        sys.executable, "-m", "cvprofiles", "run",
        "--scores", str(mini_dir / "scores.csv"),
        "--roles", str(mini_dir / "roles.json"),
        "--network", str(mini_dir / "network.yaml"),
        "--beta", str(beta),
        "--beta-estimates", str(est_csv),
        "--out", str(tmp_path / "cli"),
    ]  # fmt: skip
    proc = subprocess.run(cmd, check=False, capture_output=True, text=True)
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert (summary["L"], summary["U"]) == (0.22, 0.41)
    assert len(summary["beta_estimates_hash"]) == 64
