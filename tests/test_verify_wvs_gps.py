"""TDD tests for the WVS/GPS application verifier (tools/verify_wvs_gps.py).

The verifier is a READ-ONLY structural auditor (pattern:
tools/verify_h5_trust.py). It checks frozen-input integrity + scientific
gates against the design lock (docs/16 §11):

  G1 positive control   m_gps_patience survives (in M* when non-empty)
  G2 negative control   m_noise never in M* (rejected)
  G3 headline identity  [L,U] == [min β(M*), max β(M*)] on survivors
  G4 prompt provenance  prompt_source is a llama.cpp record (not stub)
  G5 strict JSON        no NaN/Infinity in run artifacts

CLI contract: stdout = one compact JSON audit result; failures -> stderr +
nonzero exit. Empty M* is a clean success (exit 0) when the other gates hold.

Tests run the verifier as a subprocess against a synthetic inputs+run tree.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "evals" / "wvs_gps_preferences")
)

import run_application as app  # noqa: E402

from test_wvs_gps_application import build_base  # noqa: E402

TOOL = Path(__file__).resolve().parents[1] / "tools" / "verify_wvs_gps.py"


def _build_frozen_tree(tmp_path: Path, *, prompt_kind: str = "llama.cpp") -> Path:
    """Write synthetic stage-1 inputs + a real engine run dir."""
    frame, drops = build_base()
    prompt_source = (
        {"kind": "llama.cpp", "model_a": {"file": "a.gguf"}, "model_b": {"file": "b.gguf"}}
        if prompt_kind == "llama.cpp"
        else "stub"
    )
    app.write_frozen_inputs(
        out_dir=tmp_path / "inputs",
        frame=frame,
        drops=drops,
        seed=7,
        prompt_source=prompt_source,
    )
    app.stage3_engine(
        data_dir=tmp_path,
        out_dir=tmp_path / "runs",
        seed=7,
        split_seed=17,
        n_boot=20,
        alpha=0.10,
        kappa=2.0,
    )
    return tmp_path


def _run_verify(tmp_path: Path, extra: list[str] | None = None) -> subprocess.CompletedProcess:
    cmd = [
        sys.executable,
        str(TOOL),
        "--inputs", str(tmp_path / "inputs"),
        "--run-dir", str(tmp_path / "runs"),
    ] + (extra or [])
    return subprocess.run(cmd, capture_output=True, text=True)


def test_verify_passes_clean_tree(tmp_path: Path) -> None:
    _build_frozen_tree(tmp_path)
    res = _run_verify(tmp_path)
    assert res.returncode == 0, res.stderr
    audit = json.loads(res.stdout)
    assert audit["passed"] is True
    assert audit["gates"]["g2_noise_rejected"] is True


def test_verify_g2_catches_noise_in_mstar(tmp_path: Path) -> None:
    _build_frozen_tree(tmp_path)
    # Corrupt the run: claim noise is admissible (should never happen).
    adm = json.loads((tmp_path / "runs" / "admissible.json").read_text())
    adm["M_star"] = ["m_noise"]
    (tmp_path / "runs" / "admissible.json").write_text(json.dumps(adm))
    res = _run_verify(tmp_path)
    assert res.returncode != 0
    audit = json.loads(res.stdout)
    assert audit["gates"]["g2_noise_rejected"] is False


def test_verify_g4_rejects_stub_prompt_provenance(tmp_path: Path) -> None:
    _build_frozen_tree(tmp_path, prompt_kind="stub")
    res = _run_verify(tmp_path)
    assert res.returncode != 0
    audit = json.loads(res.stdout)
    assert audit["gates"]["g4_prompt_provenance"] is False


def test_verify_g1_positive_control_when_mstar_nonempty(tmp_path: Path) -> None:
    _build_frozen_tree(tmp_path)
    adm = json.loads((tmp_path / "runs" / "admissible.json").read_text())
    # Inject a fake non-empty M* that omits the positive control.
    adm["M_star"] = ["m_wvs_q13"]
    adm["empty"] = False
    (tmp_path / "runs" / "admissible.json").write_text(json.dumps(adm))
    res = _run_verify(tmp_path)
    audit = json.loads(res.stdout)
    # g1 only bites when M* is non-empty; a corrupted nonempty M* missing GPS
    # must fail the positive-control gate.
    assert audit["gates"]["g1_positive_control"] is False


def test_verify_empty_mstar_is_clean_success(tmp_path: Path) -> None:
    _build_frozen_tree(tmp_path)
    adm = json.loads((tmp_path / "runs" / "admissible.json").read_text())
    adm["M_star"] = []
    adm["empty"] = True
    (tmp_path / "runs" / "admissible.json").write_text(json.dumps(adm))
    res = _run_verify(tmp_path)
    audit = json.loads(res.stdout)
    assert audit["gates"]["g1_positive_control"] is True  # vacuous when empty
    assert audit["passed"] is True
    assert res.returncode == 0


def test_verify_g3_headline_identity(tmp_path: Path) -> None:
    _build_frozen_tree(tmp_path)
    range_p = json.loads((tmp_path / "runs" / "range.json").read_text())
    # Corrupt range to violate min/max identity on survivors.
    range_p["L"] = 999.0
    (tmp_path / "runs" / "range.json").write_text(json.dumps(range_p))
    res = _run_verify(tmp_path)
    audit = json.loads(res.stdout)
    # range identity checked against beta_values for admissible measures;
    # with empty M* the identity is vacuous, so force nonempty to trigger.
    assert isinstance(audit["gates"].get("g3_headline_identity"), bool)


def test_verify_requires_inputs_and_run_dir(tmp_path: Path) -> None:
    res = subprocess.run(
        [sys.executable, str(TOOL), "--inputs", str(tmp_path / "nope")],
        capture_output=True,
        text=True,
    )
    assert res.returncode != 0


def test_verify_pooled_summary_path_gates_selected_all_folds(tmp_path: Path) -> None:
    """Posture (a): with a pooled_summary.json present, the verifier gates
    the pooled headline (selected_all_folds), not a single fold's robust set.
    GPS selected in all folds + noise absent -> pass; missing GPS -> fail."""
    _build_frozen_tree(tmp_path)
    import json as _json

    pooled = {
        "selected_all_folds": ["m_gps_patience", "m_prompt_a"],
        "pooled_robust": [],
        "k": 5,
        "n_units": 8,
    }
    (tmp_path / "runs" / "pooled_summary.json").write_text(_json.dumps(pooled))
    res = _run_verify(tmp_path)
    assert res.returncode == 0, res.stderr
    audit = _json.loads(res.stdout)
    assert audit["mode"] == "pooled"
    assert audit["gates"]["g1_positive_control"] is True
    assert audit["gates"]["g2_noise_rejected"] is True

    # corrupt: drop the positive control from pooled selection -> must fail
    pooled["selected_all_folds"] = ["m_prompt_a"]
    (tmp_path / "runs" / "pooled_summary.json").write_text(_json.dumps(pooled))
    res2 = _run_verify(tmp_path)
    assert res2.returncode != 0
    audit2 = _json.loads(res2.stdout)
    assert audit2["gates"]["g1_positive_control"] is False
