#!/usr/bin/env python3
"""
cvprofiles — synthetic PoC monolith (v0.1 hygiene)

HISTORICAL / MUSEUM PIECE.
  - Not the package layout. Do NOT import from src/.
  - Keep as evidence of how we started; re-implement cleanly for M1+.

Spine:
  0 SCORE    — calibrated DGP → unit×measure matrix; z-score measures + aux
  1 RESTRICT — oracle-compatible (or harsh) network R, θ
  2 IDENTIFY — slacks → M* → β(m) → [L,U]  (min/max over survivors; no bootstrap)
  3 REPORT   — console + JSON under reports/runs/

Oracle labels live OUTSIDE identify(). Engine only sees numbers + R.

Metrics (docs/03, docs/05 — LOCKED 2026-08-01):
  H1a        FA of invalid_* / wrong_construct; anchor m_dict in M*
  H1b        β(anchor) ∈ [L,U] when anchor in M*  (construction invariant)
  H1_latent  Corr(V*, y) ∈ [L,U]  — diagnostic only (attenuation); NOT a gate
  H3         empty-set honesty on harsh_theta / all_invalid
  H4         cold double-run equality of slacks, M*, L, U

Usage (from project root):
  .venv/bin/python evals/synthetic/v0_poc.py
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# ---------------------------------------------------------------------------
# Paths / constants
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parents[2]
REPORTS = ROOT / "reports" / "runs"
SUMMARIES = ROOT / "reports" / "summaries"
REPORTS.mkdir(parents=True, exist_ok=True)
SUMMARIES.mkdir(parents=True, exist_ok=True)

POC_VERSION = "v0_1_poc"
DEFAULT_N = 1000
DEFAULT_SEEDS = (0, 1, 2, 3, 4)
DELTA = 0.0
# Structural loading of y on V* (latent diagnostic uses Corr(V*, y) after SCORE)
STRUCT_BETA_V = 0.6
STRUCT_BETA_W = 0.35
ANCHOR = "m_dict"

MEASURES = [
    "m_dict",
    "m_llm_good",
    "m_para",
    "m_slop",
    "m_noise",
    "m_wrong",
    "m_near",
    "m_heavy_tail",
    "m_floor",
    "m_aux_only",
]

# Oracle labels — NOT fed to identify(); only to metrics.
LABELS: dict[str, str] = {
    "m_dict": "valid",
    "m_llm_good": "valid",
    "m_para": "valid",  # paraphrase default: valid
    "m_slop": "invalid_confounded",
    "m_noise": "invalid_noise",
    "m_wrong": "wrong_construct",
    "m_near": "near_miss",
    "m_heavy_tail": "valid",
    "m_floor": "near_miss",
    "m_aux_only": "invalid_confounded",
}

INVALID_LABELS = {"invalid_confounded", "invalid_noise", "wrong_construct"}
VALID_LABELS = {"valid"}
NEAR_MISS_LABELS = {"near_miss"}

SCENARIOS = ("oracle_easy", "oracle_with_slop", "harsh_theta", "all_invalid")


# ---------------------------------------------------------------------------
# 0. SCORE / DGP
# ---------------------------------------------------------------------------

def make_dgp(scenario: str, n: int, seed: int) -> pd.DataFrame:
    """
    Calibrated synthetic menu. Controllability > realism.

    Latents (kept for diagnostics; not used inside identify):
      V_star — true construct
      W      — confounder for bad measures
      U      — wrong construct
      v_aux  — clean auxiliary correlated with V*
      g      — binary group (higher V* → more likely g=1)
      y      — outcome
    """
    rng = np.random.default_rng(seed)

    V = rng.normal(0.0, 1.0, size=n)
    W = rng.normal(0.0, 1.0, size=n)
    U = rng.normal(0.0, 1.0, size=n)
    v_aux = 0.80 * V + rng.normal(0.0, 0.45, size=n)
    g = (V + rng.normal(0.0, 0.75, size=n) > 0.0).astype(float)

    eps_y = rng.normal(0.0, 1.0, size=n)
    y = STRUCT_BETA_V * V + STRUCT_BETA_W * W + eps_y

    # --- valid archetypes (strong V* track) ---
    m_dict = 0.92 * V + rng.normal(0.0, 0.30, size=n)
    m_llm_good = 0.88 * V + rng.normal(0.0, 0.35, size=n)
    m_para = 0.96 * m_llm_good + rng.normal(0.0, 0.12, size=n)
    m_heavy_tail = 0.88 * V + rng.standard_t(df=3, size=n) * 0.30

    # --- near_miss: must FAIL ≥1 standard oracle restriction by design ---
    # weak V* link → fails corr_min(v_aux, 0.35)
    m_near = 0.22 * V + rng.normal(0.0, 1.00, size=n)
    # heavy squash + noise → fails corr_min
    m_floor = np.tanh(0.22 * V) + rng.normal(0.0, 0.55, size=n)

    # --- invalids ---
    # baseline slop (also used / strengthened under oracle_with_slop)
    m_slop = 0.12 * V + 0.80 * W + 0.12 * y + rng.normal(0.0, 0.30, size=n)
    m_noise = rng.normal(0.0, 1.0, size=n)
    m_wrong = 0.92 * U + rng.normal(0.0, 0.28, size=n)
    m_aux_only = 0.04 * V + 0.55 * W + rng.normal(0.0, 0.85, size=n)

    if scenario == "oracle_with_slop":
        # Distinct path: stronger confounder / y-leak, weaker V* on slop only.
        # Valid columns unchanged so FA stress is real (slop looks "outcome-good").
        m_slop = (
            0.02 * V
            + 0.95 * W
            + 0.25 * y
            + rng.normal(0.0, 0.20, size=n)
        )

    if scenario == "all_invalid":
        # Destroy EVERY measure's V* track under standard oracle R.
        # Must yield M*=∅ without switching to harsh θ.
        m_dict = 0.90 * W + rng.normal(0.0, 0.35, size=n)
        m_llm_good = rng.normal(0.0, 1.0, size=n)
        m_para = 0.85 * W + 0.10 * y + rng.normal(0.0, 0.30, size=n)
        m_heavy_tail = 0.90 * U + rng.normal(0.0, 0.30, size=n)
        m_near = rng.normal(0.0, 1.0, size=n)
        m_floor = 0.70 * W + rng.normal(0.0, 0.50, size=n)
        m_slop = 0.05 * V + 0.90 * W + 0.20 * y + rng.normal(0.0, 0.25, size=n)
        m_noise = rng.normal(0.0, 1.0, size=n)
        m_wrong = 0.90 * U + rng.normal(0.0, 0.30, size=n)
        m_aux_only = 0.02 * V + 0.60 * W + rng.normal(0.0, 0.80, size=n)

    return pd.DataFrame(
        {
            "V_star": V,
            "W": W,
            "U": U,
            "v_aux": v_aux,
            "g": g,
            "y": y,
            "m_dict": m_dict,
            "m_llm_good": m_llm_good,
            "m_para": m_para,
            "m_slop": m_slop,
            "m_noise": m_noise,
            "m_wrong": m_wrong,
            "m_near": m_near,
            "m_heavy_tail": m_heavy_tail,
            "m_floor": m_floor,
            "m_aux_only": m_aux_only,
        }
    )


def score_normalize(df: pd.DataFrame) -> pd.DataFrame:
    """
    SCORE: z-score measure columns and columns used in slacks / β.

    Convention (documented): identify() and all β / latent diagnostics use
    this normalized frame so Corr(V*, y) and Corr(m, y) share one scale.
    """
    out = df.copy()
    cols = list(MEASURES) + ["v_aux", "y", "V_star"]
    for col in cols:
        x = out[col].to_numpy(dtype=float)
        sd = float(x.std(ddof=1))
        if sd < 1e-12:
            out[col] = 0.0
        else:
            out[col] = (x - x.mean()) / sd
    # g stays {0,1}
    return out


# ---------------------------------------------------------------------------
# 1. RESTRICT
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Restriction:
    id: str
    type: str  # corr_min | corr_sign | mean_order
    theta: float
    aux: str | None = None
    sign: float | None = None
    group: str | None = None


def network_for(scenario: str) -> list[Restriction]:
    """Oracle-compatible R for synthetic path only (not paper empirical network)."""
    if scenario == "harsh_theta":
        return [
            Restriction("r_corr_aux", "corr_min", theta=0.85, aux="v_aux"),
            Restriction("r_sign_aux", "corr_sign", theta=0.50, aux="v_aux", sign=1.0),
            Restriction("r_group", "mean_order", theta=0.80, group="g"),
        ]
    # oracle_easy, oracle_with_slop, all_invalid — same standard R
    return [
        Restriction("r_corr_aux", "corr_min", theta=0.35, aux="v_aux"),
        Restriction("r_sign_aux", "corr_sign", theta=0.10, aux="v_aux", sign=1.0),
        Restriction("r_group", "mean_order", theta=0.10, group="g"),
    ]


# ---------------------------------------------------------------------------
# 2. IDENTIFY
# ---------------------------------------------------------------------------

def _corr(a: np.ndarray, b: np.ndarray) -> float:
    if a.std(ddof=1) < 1e-12 or b.std(ddof=1) < 1e-12:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


def slack(m: np.ndarray, df: pd.DataFrame, r: Restriction) -> float:
    """Sample slack; >= 0 (up to -DELTA) means satisfied."""
    if r.type == "corr_min":
        assert r.aux is not None
        c = _corr(m, df[r.aux].to_numpy(dtype=float))
        return abs(c) - r.theta
    if r.type == "corr_sign":
        assert r.aux is not None and r.sign is not None
        c = _corr(m, df[r.aux].to_numpy(dtype=float))
        return r.sign * c - r.theta
    if r.type == "mean_order":
        assert r.group is not None
        g = df[r.group].to_numpy(dtype=float)
        m1 = m[g >= 0.5]
        m0 = m[g < 0.5]
        if len(m1) < 2 or len(m0) < 2:
            return -np.inf
        return float(m1.mean() - m0.mean() - r.theta)
    raise ValueError(f"unknown restriction type: {r.type}")


def beta_corr_y(m: np.ndarray, y: np.ndarray) -> float:
    return _corr(m, y)


def beta_ols_coef(m: np.ndarray, y: np.ndarray) -> float:
    x = np.column_stack([np.ones(len(m)), m])
    coef, _, _, _ = np.linalg.lstsq(x, y, rcond=None)
    return float(coef[1])


def identify(
    df: pd.DataFrame,
    restrictions: list[Restriction],
    delta: float = DELTA,
    beta_id: str = "corr_y",
) -> dict[str, Any]:
    y = df["y"].to_numpy(dtype=float)
    slacks: dict[str, dict[str, float]] = {}
    beta_values: dict[str, float] = {}
    failures: dict[str, list[str]] = {}

    for mid in MEASURES:
        m = df[mid].to_numpy(dtype=float)
        row_s = {r.id: slack(m, df, r) for r in restrictions}
        slacks[mid] = row_s
        failures[mid] = [rid for rid, s in row_s.items() if s < -delta]
        if beta_id == "corr_y":
            beta_values[mid] = beta_corr_y(m, y)
        elif beta_id == "ols_coef":
            beta_values[mid] = beta_ols_coef(m, y)
        else:
            raise ValueError(beta_id)

    M_star = [mid for mid in MEASURES if len(failures[mid]) == 0]
    empty = len(M_star) == 0
    if empty:
        L, U = None, None
        point_id = False
    else:
        b_vals = [beta_values[mid] for mid in M_star]
        L, U = float(min(b_vals)), float(max(b_vals))
        point_id = math.isclose(L, U, abs_tol=1e-12)

    return {
        "slacks": slacks,
        "failures": failures,
        "M_star": M_star,
        "beta_values": beta_values,
        "beta_id": beta_id,
        "L": L,
        "U": U,
        "empty_set": empty,
        "point_id": point_id,
        "delta": delta,
        "restrictions": [asdict(r) for r in restrictions],
    }


def _result_core(result: dict[str, Any]) -> dict[str, Any]:
    """Comparable core for cold determinism (no wall-clock fields)."""
    return {
        "M_star": list(result["M_star"]),
        "L": result["L"],
        "U": result["U"],
        "empty_set": result["empty_set"],
        "slacks": {
            m: {k: float(v) for k, v in result["slacks"][m].items()}
            for m in MEASURES
        },
        "beta_values": {m: float(result["beta_values"][m]) for m in MEASURES},
        "failures": {m: list(result["failures"][m]) for m in MEASURES},
    }


def cores_equal(a: dict[str, Any], b: dict[str, Any], tol: float = 1e-12) -> bool:
    if a["M_star"] != b["M_star"]:
        return False
    if a["empty_set"] != b["empty_set"]:
        return False
    for key in ("L", "U"):
        av, bv = a[key], b[key]
        if av is None and bv is None:
            continue
        if av is None or bv is None:
            return False
        if abs(av - bv) > tol:
            return False
    for m in MEASURES:
        for rid in a["slacks"][m]:
            if abs(a["slacks"][m][rid] - b["slacks"][m][rid]) > tol:
                return False
        if abs(a["beta_values"][m] - b["beta_values"][m]) > tol:
            return False
        if a["failures"][m] != b["failures"][m]:
            return False
    return True


# ---------------------------------------------------------------------------
# Metrics (oracle labels outside engine)
# ---------------------------------------------------------------------------

def metrics_for(result: dict[str, Any], df: pd.DataFrame) -> dict[str, Any]:
    M_star = set(result["M_star"])
    admitted_invalid = sorted(m for m in M_star if LABELS[m] in INVALID_LABELS)
    admitted_valid = sorted(m for m in M_star if LABELS[m] in VALID_LABELS)
    admitted_near = sorted(m for m in M_star if LABELS[m] in NEAR_MISS_LABELS)
    excluded_valid = sorted(
        m for m in MEASURES if LABELS[m] in VALID_LABELS and m not in M_star
    )
    n_invalid = sum(1 for m in MEASURES if LABELS[m] in INVALID_LABELS)
    fa_rate = len(admitted_invalid) / n_invalid if n_invalid else 0.0

    anchor_in = ANCHOR in M_star
    beta_anchor = float(result["beta_values"][ANCHOR])
    beta_latent = _corr(
        df["V_star"].to_numpy(dtype=float),
        df["y"].to_numpy(dtype=float),
    )

    # H1b: construction invariant when anchor survives
    if result["empty_set"]:
        h1b_hit = None
    elif not anchor_in:
        h1b_hit = False
    else:
        assert result["L"] is not None and result["U"] is not None
        h1b_hit = result["L"] - 1e-12 <= beta_anchor <= result["U"] + 1e-12

    # H1_latent: diagnostic only
    if result["empty_set"]:
        h1_latent_hit = None
    else:
        assert result["L"] is not None and result["U"] is not None
        h1_latent_hit = result["L"] - 1e-12 <= beta_latent <= result["U"] + 1e-12

    return {
        "n_M_star": len(M_star),
        "M_star": sorted(M_star),
        "admitted_invalid": admitted_invalid,
        "admitted_valid": admitted_valid,
        "admitted_near_miss": admitted_near,
        "excluded_valid": excluded_valid,
        "false_admission_rate": fa_rate,
        "empty_set": result["empty_set"],
        "point_id": result["point_id"],
        "anchor": ANCHOR,
        "anchor_in_M_star": anchor_in,
        "beta_anchor": beta_anchor,
        "beta_latent": beta_latent,
        "H1b_hit": h1b_hit,
        "H1_latent_hit": h1_latent_hit,
        "L": result["L"],
        "U": result["U"],
        "width": None if result["empty_set"] else float(result["U"] - result["L"]),  # type: ignore[operator]
    }


# ---------------------------------------------------------------------------
# 3. REPORT
# ---------------------------------------------------------------------------

def print_report(
    scenario: str,
    seed: int,
    result: dict[str, Any],
    metrics: dict[str, Any],
) -> None:
    print()
    print("=" * 72)
    print(
        f" scenario={scenario}  seed={seed}  beta={result['beta_id']}  "
        f"δ={result['delta']}  {POC_VERSION}"
    )
    print("=" * 72)
    print("Restrictions:")
    for r in result["restrictions"]:
        print(
            f"  - {r['id']}: type={r['type']} θ={r['theta']} "
            f"aux={r.get('aux')} sign={r.get('sign')} group={r.get('group')}"
        )
    print()
    print(f"{'measure':<14} {'label':<20} {'β':>8}  slacks / fails")
    print("-" * 72)
    for mid in MEASURES:
        s = result["slacks"][mid]
        fails = result["failures"][mid]
        mark = "✓" if mid in result["M_star"] else "·"
        slack_str = " ".join(f"{k}={v:+.3f}" for k, v in s.items())
        fail_str = f"  FAIL[{','.join(fails)}]" if fails else ""
        print(
            f"{mark} {mid:<12} {LABELS[mid]:<20} "
            f"{result['beta_values'][mid]:+8.3f}  {slack_str}{fail_str}"
        )
    print("-" * 72)
    if result["empty_set"]:
        print("Result: M* empty — all candidates rejected under declared R.")
        print("First-class scientific outcome (not a crash).")
    else:
        print(f"M* = {result['M_star']}")
        print(
            f"[L, U] = [{result['L']:+.4f}, {result['U']:+.4f}]  "
            f"(survivor min/max; not a CI)"
        )
    print(
        f"anchor={ANCHOR} in_M*={metrics['anchor_in_M_star']}  "
        f"β_anchor={metrics['beta_anchor']:+.4f}  H1b={metrics['H1b_hit']}"
    )
    print(
        f"β_latent=Corr(V*,y)={metrics['beta_latent']:+.4f}  "
        f"H1_latent={metrics['H1_latent_hit']}  (diagnostic only)"
    )
    print(
        f"FA={metrics['false_admission_rate']:.3f}  "
        f"invalid_in={metrics['admitted_invalid']}  "
        f"near_in={metrics['admitted_near_miss']}  "
        f"valid_out={metrics['excluded_valid']}"
    )


def write_run_json(scenario: str, seed: int, payload: dict[str, Any]) -> Path:
    path = REPORTS / f"{POC_VERSION}_{scenario}_seed{seed}.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_identify_once(
    scenario: str, seed: int, n: int = DEFAULT_N, beta_id: str = "corr_y"
) -> tuple[dict[str, Any], dict[str, Any], pd.DataFrame]:
    """Fresh DGP + SCORE + IDENTIFY. Independent call = cold path for H4."""
    df_raw = make_dgp(scenario, n=n, seed=seed)
    df = score_normalize(df_raw)
    R = network_for(scenario)
    result = identify(df, R, delta=DELTA, beta_id=beta_id)
    metrics = metrics_for(result, df)
    return result, metrics, df


def run_one(scenario: str, seed: int, n: int = DEFAULT_N) -> dict[str, Any]:
    result, metrics, _df = run_identify_once(scenario, seed, n=n, beta_id="corr_y")
    # secondary β (side payload only)
    result_ols, _, _ = run_identify_once(scenario, seed, n=n, beta_id="ols_coef")

    # H4 cold: second independent full pipeline, same (scenario, n, seed)
    result2, _, _ = run_identify_once(scenario, seed, n=n, beta_id="corr_y")
    cold_ok = cores_equal(_result_core(result), _result_core(result2))

    payload = {
        "poc_version": POC_VERSION,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario,
        "seed": seed,
        "n": n,
        "delta": DELTA,
        "measures": MEASURES,
        "labels": LABELS,
        "anchor": ANCHOR,
        "score_convention": (
            "z-score measures, v_aux, y, V_star; g binary; "
            "all β and H1_latent use this frame"
        ),
        "result_corr_y": result,
        "result_ols_coef": {
            "M_star": result_ols["M_star"],
            "L": result_ols["L"],
            "U": result_ols["U"],
            "beta_values": result_ols["beta_values"],
            "empty_set": result_ols["empty_set"],
        },
        "metrics_corr_y": metrics,
        "cold_determinism_ok": cold_ok,
        "note": (
            "No bootstrap in PoC. [L,U]=min/max over M*. "
            "H1_latent is diagnostic (attenuation); not a gate."
        ),
    }
    path = write_run_json(scenario, seed, payload)
    print_report(scenario, seed, result, metrics)
    print(f"cold_determinism_ok={cold_ok}")
    print(f"wrote {path}")
    return payload


def summarize(payloads: list[dict[str, Any]]) -> dict[str, Any]:
    print("\n" + "#" * 72)
    print("# SUMMARY — H1a / H1b / H1_latent / H3 / H4")
    print("#" * 72)
    by_sc: dict[str, list[dict[str, Any]]] = {}
    cold_flags: dict[str, list[bool]] = {}
    for p in payloads:
        by_sc.setdefault(p["scenario"], []).append(p["metrics_corr_y"])
        cold_flags.setdefault(p["scenario"], []).append(bool(p["cold_determinism_ok"]))

    rows = []
    for sc in SCENARIOS:
        ms = by_sc.get(sc, [])
        if not ms:
            continue
        n = len(ms)
        empty_rate = sum(1 for m in ms if m["empty_set"]) / n
        point_rate = sum(1 for m in ms if m["point_id"]) / n
        fa = float(np.mean([m["false_admission_rate"] for m in ms]))
        anchor_rate = sum(1 for m in ms if m["anchor_in_M_star"]) / n
        h1b_def = [m["H1b_hit"] for m in ms if m["H1b_hit"] is not None]
        h1b = float(np.mean(h1b_def)) if h1b_def else float("nan")
        lat_def = [m["H1_latent_hit"] for m in ms if m["H1_latent_hit"] is not None]
        h1_lat = float(np.mean(lat_def)) if lat_def else float("nan")
        widths = [m["width"] for m in ms if m["width"] is not None]
        mean_width = float(np.mean(widths)) if widths else float("nan")
        inv_any = sorted({x for m in ms for x in m["admitted_invalid"]})
        near_any = sorted({x for m in ms for x in m["admitted_near_miss"]})
        cold_ok = all(cold_flags.get(sc, []))
        # slop β diagnostic: mean β(m_slop) to show oracle_with_slop ≠ easy
        slop_betas = []
        for p in payloads:
            if p["scenario"] == sc:
                slop_betas.append(p["result_corr_y"]["beta_values"]["m_slop"])
        mean_slop_beta = float(np.mean(slop_betas)) if slop_betas else float("nan")

        row = {
            "scenario": sc,
            "seeds": n,
            "empty_set_rate": empty_rate,
            "point_id_rate": point_rate,
            "mean_false_admission": fa,
            "anchor_in_M_star_rate": anchor_rate,
            "H1b_rate": h1b,
            "H1_latent_rate": h1_lat,
            "mean_width": mean_width,
            "mean_beta_m_slop": mean_slop_beta,
            "invalid_ever_admitted": inv_any,
            "near_miss_ever_admitted": near_any,
            "cold_determinism_all_ok": cold_ok,
        }
        rows.append(row)
        print(
            f"{sc:<18} empty={empty_rate:.2f}  FA={fa:.3f}  "
            f"anchor_in={anchor_rate:.2f}  H1b={h1b if h1b == h1b else float('nan'):.2f}  "
            f"H1_lat={h1_lat if h1_lat == h1_lat else float('nan'):.2f}  "
            f"width={mean_width if mean_width == mean_width else float('nan'):.3f}  "
            f"slop_β={mean_slop_beta:+.3f}  cold={cold_ok}  "
            f"inv={inv_any}  near={near_any}"
        )

    summary = {
        "poc_version": POC_VERSION,
        "ts_utc": datetime.now(timezone.utc).isoformat(),
        "seeds": list(DEFAULT_SEEDS),
        "n": DEFAULT_N,
        "delta": DELTA,
        "anchor": ANCHOR,
        "rows": rows,
    }
    # Prefer non-ignored path for repo-proof summary
    summary_path = SUMMARIES / f"{POC_VERSION}_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8")
    # Also under runs for local browsing
    (REPORTS / f"{POC_VERSION}_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(f"\nwrote {summary_path}")
    return summary


def evaluate_gates(summary: dict[str, Any], payloads: list[dict[str, Any]]) -> list[str]:
    """Return list of gate failure strings. Empty => pass."""
    fails: list[str] = []
    by = {r["scenario"]: r for r in summary["rows"]}

    for sc in ("oracle_easy", "oracle_with_slop"):
        r = by[sc]
        if r["mean_false_admission"] > 1e-12:
            fails.append(f"{sc}: FA={r['mean_false_admission']} > 0")
        if r["anchor_in_M_star_rate"] < 1.0 - 1e-12:
            fails.append(f"{sc}: anchor_in_M* rate={r['anchor_in_M_star_rate']} < 1")
        if r["empty_set_rate"] > 1e-12:
            fails.append(f"{sc}: unexpected empty_set_rate={r['empty_set_rate']}")
        h1b = r["H1b_rate"]
        if not (isinstance(h1b, float) and h1b == h1b and h1b >= 1.0 - 1e-12):
            fails.append(f"{sc}: H1b_rate={h1b} (want 1.0 when anchor in M*)")
        if not r["cold_determinism_all_ok"]:
            fails.append(f"{sc}: cold determinism failed")
        # near_miss should not all flood M* — at least one near_miss type excluded somewhere
        # Stronger: no near_miss ever admitted under standard oracle R
        if r["near_miss_ever_admitted"]:
            fails.append(
                f"{sc}: near_miss admitted {r['near_miss_ever_admitted']} "
                f"(Q23: should fail ≥1 restriction)"
            )
        if r["invalid_ever_admitted"]:
            fails.append(f"{sc}: invalid admitted {r['invalid_ever_admitted']}")

    for sc in ("harsh_theta", "all_invalid"):
        r = by[sc]
        if r["empty_set_rate"] < 1.0 - 1e-12:
            fails.append(f"{sc}: empty_set_rate={r['empty_set_rate']} < 1")
        if r["mean_false_admission"] > 1e-12:
            fails.append(f"{sc}: FA={r['mean_false_admission']} > 0")
        if not r["cold_determinism_all_ok"]:
            fails.append(f"{sc}: cold determinism failed")

    # Distinct slop path: mean β(m_slop) must differ easy vs with_slop
    be = by["oracle_easy"]["mean_beta_m_slop"]
    bs = by["oracle_with_slop"]["mean_beta_m_slop"]
    if abs(be - bs) < 1e-6:
        fails.append(
            f"oracle_with_slop not distinct from easy: mean β(m_slop) "
            f"easy={be} slop={bs}"
        )

    # All cold flags on payloads
    if not all(p["cold_determinism_ok"] for p in payloads):
        fails.append("global: some payload cold_determinism_ok=False")

    return fails


def main() -> int:
    print(f"cvprofiles {POC_VERSION}  root={ROOT}")
    print(
        f"n={DEFAULT_N}  seeds={list(DEFAULT_SEEDS)}  δ={DELTA}  "
        f"measures={len(MEASURES)}  anchor={ANCHOR}"
    )
    payloads: list[dict[str, Any]] = []
    for scenario in SCENARIOS:
        for seed in DEFAULT_SEEDS:
            payloads.append(run_one(scenario, seed))

    summary = summarize(payloads)
    fails = evaluate_gates(summary, payloads)

    print("\n" + "#" * 72)
    print("# GATE CHECK")
    print("#" * 72)
    if not fails:
        print("ALL GATES PASSED (H1_latent not gated).")
        print(
            "Note: H1b=1 with min/max range + anchor∈M* is a construction "
            "invariant; primary bite is H1a / H3 / H4."
        )
        return 0

    print("GATE FAILURES:")
    for f in fails:
        print(f"  - {f}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
