"""Calibrated synthetic measurement menus (controllability > realism).

Rewritten for the package path. Do not import the museum monolith.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from cvprofiles.schemas.scores import ScoreColumnRoles

# Menu order is freeze order (roles.measures).
MEASURES: list[str] = [
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

# Design-role labels (NOT fed to identify; metrics only).
LABELS: dict[str, str] = {
    "m_dict": "valid",
    "m_llm_good": "valid",
    "m_para": "valid",  # paraphrase default: valid (Q9)
    "m_slop": "invalid_confounded",
    "m_noise": "invalid_noise",
    "m_wrong": "wrong_construct",
    "m_near": "near_miss",
    "m_heavy_tail": "valid",
    "m_floor": "near_miss",
    "m_aux_only": "invalid_confounded",
}

INVALID_LABELS = frozenset({"invalid_confounded", "invalid_noise", "wrong_construct"})
NEAR_MISS_LABELS = frozenset({"near_miss"})
VALID_LABELS = frozenset({"valid"})

SCENARIOS: tuple[str, ...] = (
    "oracle_easy",
    "oracle_with_slop",
    "harsh_theta",
    "all_invalid",
)

ANCHOR = "m_dict"

# Structural loadings for y (latent diagnostic uses Corr(V*, y) on scored frame).
STRUCT_BETA_V = 0.6
STRUCT_BETA_W = 0.35

DEFAULT_N = 1000


def roles_for_menu() -> ScoreColumnRoles:
    """SCORE roles for the standard synthetic menu."""
    return ScoreColumnRoles(
        unit_id="unit_id",
        measures=list(MEASURES),
        aux=["v_aux"],
        outcome="y",
        diagnostic=["V_star", "W", "U", "g"],
    )


def make_dgp(scenario: str, n: int, seed: int) -> pd.DataFrame:
    """Build unit×measure frame with latents for diagnostics.

    identify() must never see labels or use V_star — only SCORE roles + R.
    """
    if scenario not in SCENARIOS:
        raise ValueError(f"unknown scenario: {scenario!r}; expected one of {SCENARIOS}")
    if n < 10:
        raise ValueError("n must be >= 10")

    rng = np.random.default_rng(int(seed))

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
    m_floor = np.tanh(0.22 * V) + rng.normal(0.0, 0.55, size=n)

    # --- invalids ---
    m_slop = 0.12 * V + 0.80 * W + 0.12 * y + rng.normal(0.0, 0.30, size=n)
    m_noise = rng.normal(0.0, 1.0, size=n)
    m_wrong = 0.92 * U + rng.normal(0.0, 0.28, size=n)
    m_aux_only = 0.04 * V + 0.55 * W + rng.normal(0.0, 0.85, size=n)

    if scenario == "oracle_with_slop":
        # Distinct path: stronger confound / y-leak on slop only.
        m_slop = (
            0.02 * V + 0.95 * W + 0.25 * y + rng.normal(0.0, 0.20, size=n)
        )

    if scenario == "all_invalid":
        # Destroy every measure's V* track under standard oracle R → M*=∅.
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

    # harsh_theta uses the same DGP as oracle_easy; network θ changes, not columns.

    unit_id = [f"u{i:04d}" for i in range(n)]
    df = pd.DataFrame(
        {
            "unit_id": unit_id,
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
    return df
