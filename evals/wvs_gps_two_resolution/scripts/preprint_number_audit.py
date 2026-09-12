"""Read-only preprint number audit + freeze-preserving diagnostics.

Does not modify freezes, theta, or position_paper.tex.
Writes:
  evals/wvs_gps_two_resolution/preprint_audit/audit.json
  paper/NUMBER_RECONCILIATION.md
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
EVAL = ROOT / "evals" / "wvs_gps_two_resolution"
RUNS = EVAL / "runs"
OUT = EVAL / "preprint_audit"
PAPER = ROOT / "paper" / "NUMBER_RECONCILIATION.md"
SEED = 20260814
N_PERM = 1000


def load_json(path: Path) -> dict:
    return json.loads(path.read_text())


def r3(x: float | None) -> float | None:
    if x is None or (isinstance(x, float) and not np.isfinite(x)):
        return None
    return round(float(x), 3)


def pearson(a: np.ndarray, b: np.ndarray) -> float:
    if a.std() == 0 or b.std() == 0:
        return float("nan")
    return float(np.corrcoef(a, b)[0, 1])


def spearman(a: np.ndarray, b: np.ndarray) -> float:
    return float(pd.Series(a).corr(pd.Series(b), method="spearman"))


def check(name: str, claimed, observed, tol: float, rows: list[dict]) -> None:
    if claimed is None or observed is None:
        status = "UNVERIFIED"
        delta = None
    else:
        delta = abs(float(claimed) - float(observed))
        status = "PASS" if delta <= tol else "FAIL"
    rows.append(
        {
            "claim": name,
            "claimed": claimed,
            "observed": observed if not isinstance(observed, float) else r3(observed),
            "delta": None if delta is None else round(delta, 6),
            "tol": tol,
            "status": status,
        }
    )


def profile_bundle(tag: str) -> dict:
    d = RUNS / tag
    slacks = pd.read_csv(d / "slacks.csv").set_index("measure")
    bv = load_json(d / "beta_values.json")
    adm = load_json(d / "admissible.json")
    rng = load_json(d / "range.json")
    cov = load_json(d / "coverage.json")
    man = load_json(d / "score_manifest.json")
    net = load_json(d / "network_resolved.json")
    scores = pd.read_csv(d / "S_frozen.csv")
    return {
        "tag": tag,
        "slacks": slacks,
        "betas": bv["beta_values"],
        "flags": bv["admissible_flag"],
        "adm": adm,
        "range": rng,
        "cov": cov,
        "roles": man["roles"],
        "net": net,
        "scores": scores,
        "n": int(man["n_rows"]),
        "n_menu": int(adm["n_menu"]),
        "measures": list(man["roles"]["measures"]),
    }


def select_hold_ids(net: dict) -> tuple[list[str], list[str]]:
    sel, hold = [], []
    for r in net["restrictions"]:
        stage = r.get("stage")
        if stage in (None, "select"):
            sel.append(r["id"])
        elif stage == "holdout":
            hold.append(r["id"])
    return sel, hold


def passes(slacks: pd.DataFrame, m: str, ids: list[str]) -> bool:
    return all(float(slacks.loc[m, r]) >= 0 for r in ids)


def comparative_falsification(b: dict, rng: np.random.Generator) -> dict:
    sel, hold = select_hold_ids(b["net"])
    measures = list(b["measures"])
    selected = [m for m in measures if passes(b["slacks"], m, sel)]
    h = {m: int(passes(b["slacks"], m, hold)) for m in measures}

    def rate(ms: list[str]) -> float | None:
        if not ms:
            return None
        return float(np.mean([h[m] for m in ms]))

    p_s = rate(selected)
    k = len(selected)
    best_beta = max(measures, key=lambda m: b["betas"][m])
    best_anchor = max(measures, key=lambda m: float(b["slacks"].loc[m, sel[0]]))
    # size-matched random subsets
    if k == 0 or k > len(measures):
        rand_mean = None
        rand_share_ge = None
        rand_draws = []
    else:
        rand_draws = []
        idx = np.arange(len(measures))
        for _ in range(N_PERM):
            take = rng.choice(idx, size=k, replace=False)
            subset = [measures[i] for i in take]
            rand_draws.append(rate(subset))
        rand_mean = float(np.mean(rand_draws))
        rand_share_ge = float(np.mean(np.array(rand_draws) >= p_s)) if p_s is not None else None

    no_noise = [m for m in measures if m != "m_noise"]
    selected_nn = [m for m in selected if m != "m_noise"]
    return {
        "n_menu": len(measures),
        "k": k,
        "M_star_S": selected,
        "p_hat_S": p_s,
        "best_beta_measure": best_beta,
        "p_hat_best_beta": rate([best_beta]),
        "best_anchor_measure": best_anchor,
        "p_hat_best_anchor": rate([best_anchor]),
        "random_k_mean": rand_mean,
        "random_k_share_S_ge": rand_share_ge,
        "n_perm": N_PERM,
        "seed": SEED,
        "without_noise": {
            "M_star_S": selected_nn,
            "p_hat_S": rate(selected_nn),
            "best_beta": max(no_noise, key=lambda m: b["betas"][m]),
            "p_hat_best_beta": rate([max(no_noise, key=lambda m: b["betas"][m])]),
        },
        "note": "Holdout H(m)=1 iff every holdout slack >= 0. Random is uniform size-k subsets of the declared menu.",
    }


def leave_one_out(b: dict) -> dict:
    sel, _ = select_hold_ids(b["net"])
    measures = list(b["measures"])
    rows = []
    for drop in measures:
        rest = [m for m in measures if m != drop]
        survivors = [m for m in rest if passes(b["slacks"], m, sel)]
        betas = [b["betas"][m] for m in survivors]
        unrestr = [b["betas"][m] for m in rest]
        rows.append(
            {
                "dropped": drop,
                "M_star": survivors,
                "L": r3(min(betas) if betas else None),
                "U": r3(max(betas) if betas else None),
                "unrestricted_L": r3(min(unrestr)),
                "unrestricted_U": r3(max(unrestr)),
                "empty": not bool(survivors),
            }
        )
    return {"rows": rows}


def frozen_vs_reformed_cell(b: dict, rng: np.random.Generator) -> dict:
    """Frozen-M* vs re-formed M* bands under the paper's cell-exchangeable bootstrap.

    Admission uses the select-stage Pearson floor only (matches engine stage split).
    Beta is Pearson vs the outcome column. Not a cluster bootstrap.
    """
    sel, _ = select_hold_ids(b["net"])
    assert len(sel) == 1
    sel_id = sel[0]
    theta = 0.0
    aux = ""
    for r in b["net"]["restrictions"]:
        if r["id"] == sel_id:
            theta = float(r["theta"])
            aux = str(r["params"]["variable"])
            break
    if not aux:
        raise ValueError(f"select restriction {sel_id} missing aux")
    outcome = b["roles"]["outcome"]
    frame = b["scores"]
    n = len(frame)
    measures = list(b["measures"])
    m_star = [m for m in measures if passes(b["slacks"], m, sel)]
    y = frame[outcome].to_numpy()
    edu = frame[aux].to_numpy()
    cols = {m: frame[m].to_numpy() for m in measures}

    L_ref, U_ref, L_frz, U_frz = [], [], [], []
    n_empty = 0
    for _ in range(1000):
        idx = rng.integers(0, n, size=n)
        yb, eb = y[idx], edu[idx]
        admitted = []
        betas = {}
        for m in measures:
            xb = cols[m][idx]
            r_edu = pearson(xb, eb)
            r_y = pearson(xb, yb)
            betas[m] = r_y
            if r_edu - theta >= 0:
                admitted.append(m)
        if not admitted:
            n_empty += 1
            continue
        b_ad = [betas[m] for m in admitted]
        L_ref.append(min(b_ad))
        U_ref.append(max(b_ad))
        b_fr = [betas[m] for m in m_star]
        if any(not np.isfinite(v) for v in b_fr):
            continue
        L_frz.append(min(b_fr))
        U_frz.append(max(b_fr))

    def band(Ls, Us) -> tuple[float, float]:
        return float(np.quantile(Ls, 0.05)), float(np.quantile(Us, 0.95))

    return {
        "M_star_frozen": m_star,
        "theta_select": theta,
        "aux": aux,
        "n_boot": 1000,
        "empty_replicate_rate_reformed": n_empty / 1000,
        "reformed_band": [r3(x) for x in band(L_ref, U_ref)] if L_ref else None,
        "frozen_Mstar_band": [r3(x) for x in band(L_frz, U_frz)] if L_frz else None,
        "paper_coverage_band": [r3(b["cov"]["band_L"]), r3(b["cov"]["band_U"])],
        "note": (
            "Reformed admission = Pearson(m, edu) >= theta on the resample; "
            "holdout is not used (engine stage split). Frozen band evaluates "
            "beta only on the original M*. Same seed family, independent RNG "
            "stream from the shipped bootstrap.json (do not expect bit-match)."
        ),
    }


def diagnostics_table(b: dict) -> list[dict]:
    rows = []
    sel, hold = select_hold_ids(b["net"])
    bound = {row["measure"]: row for row in b["cov"]["boundary"]}
    p_hat = b["cov"].get("p_hat_m", {})
    for m in b["measures"]:
        sl = {r: float(b["slacks"].loc[m, r]) for r in list(b["slacks"].columns)}
        br = bound.get(m, {})
        rows.append(
            {
                "measure": m,
                "admitted": bool(b["flags"][m]),
                "beta": r3(b["betas"][m]),
                "select_slacks": {k: r3(v) for k, v in sl.items() if k in sel},
                "holdout_slacks": {k: r3(v) for k, v in sl.items() if k in hold},
                "min_slack_margin": r3(br.get("margin")),
                "boot_SE": r3(br.get("se")),
                "kappa2_boundary": br.get("boundary"),
                "p_hat_admission": r3(p_hat.get(m)),
            }
        )
    return rows


def menu_unrestricted(b: dict, exclude_noise: bool) -> dict:
    ms = [m for m in b["measures"] if not (exclude_noise and m == "m_noise")]
    betas = {m: b["betas"][m] for m in ms}
    lo_m = min(betas, key=lambda m: betas[m])
    hi_m = max(betas, key=lambda m: betas[m])
    return {
        "columns": ms,
        "n": len(ms),
        "L": r3(betas[lo_m]),
        "U": r3(betas[hi_m]),
        "L_measure": lo_m,
        "U_measure": hi_m,
    }


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    pc = profile_bundle("patience_cells_demeaned_llm")
    tc = profile_bundle("trust_cells_demeaned_llm")
    pco = profile_bundle("patience_country_llm")
    tco = profile_bundle("trust_country_llm")
    pch = profile_bundle("patience_cells_demeaned")
    pcn = profile_bundle("patience_country")

    empty_r = load_json(
        ROOT / "evals/composition_special_cases/empty_R_patience_recovery.json"
    )
    mtmm = load_json(
        ROOT / "evals/composition_special_cases/mtmm_patience_trust_recovery.json"
    )
    partial = load_json(
        ROOT / "evals/composition_special_cases/partial_r_patience_trust.json"
    )
    dif = load_json(EVAL / "dif_level_dependence.json")
    grid = load_json(EVAL / "network_sensitivity_summary.json")

    rows: list[dict] = []

    # --- headline cells patience ---
    check("patience_cells L", 0.245, pc["range"]["L"], 0.0005, rows)
    check("patience_cells U", 0.556, pc["range"]["U"], 0.0005, rows)
    check("patience_cells band_L", 0.179, pc["cov"]["band_L"], 0.0005, rows)
    check("patience_cells band_U", 0.614, pc["cov"]["band_U"], 0.0005, rows)
    check("patience_cells empty_rep", 0.0, pc["cov"]["empty_replicate_rate"], 1e-12, rows)
    check("patience_cells n", 480, pc["n"], 0, rows)
    check("Q13 edu slack", 0.051, pc["slacks"].loc["m_wvs_q13", "conv_edu_cell"], 0.0005, rows)
    check("Q13 leftover", 0.060, pc["slacks"].loc["m_wvs_q13", "mono_edu_cell"], 0.0005, rows)
    check("Q13 beta", 0.245, pc["betas"]["m_wvs_q13"], 0.0005, rows)
    check("Q14 slack", -0.564, pc["slacks"].loc["m_wvs_q14", "conv_edu_cell"], 0.0005, rows)
    check("Q14 beta", -0.326, pc["betas"]["m_wvs_q14"], 0.0005, rows)
    check("Llama slack", 0.322, pc["slacks"].loc["m_llm_patience_llama", "conv_edu_cell"], 0.0005, rows)
    check("Llama beta", 0.417, pc["betas"]["m_llm_patience_llama"], 0.0005, rows)
    check("Phi slack", 0.440, pc["slacks"].loc["m_llm_patience_phi", "conv_edu_cell"], 0.0005, rows)
    check("Phi beta", 0.556, pc["betas"]["m_llm_patience_phi"], 0.0005, rows)
    check("human-only empty_rep", 0.17, pch["cov"]["empty_replicate_rate"], 1e-12, rows)
    check("human-only L", 0.245, pch["range"]["L"], 0.0005, rows)

    # --- trust cells ---
    check("trust_cells L", -0.317, tc["range"]["L"], 0.0005, rows)
    check("trust_cells U", -0.317, tc["range"]["U"], 0.0005, rows)
    check("trust_cells band_L", -0.382, tc["cov"]["band_L"], 0.0005, rows)
    check("trust_cells band_U", -0.240, tc["cov"]["band_U"], 0.0005, rows)
    check("trust_cells empty_rep", 0.0, tc["cov"]["empty_replicate_rate"], 1e-12, rows)
    check("Llama trust slack", -0.077, tc["slacks"].loc["m_llm_trust_llama", "conv_edu_cell"], 0.0005, rows)
    check("Phi trust select slack", 0.149, tc["slacks"].loc["m_llm_trust_phi", "conv_edu_cell"], 0.0005, rows)
    check("Phi trust leftover", 0.133, tc["slacks"].loc["m_llm_trust_phi", "mono_edu_cell"], 0.0005, rows)
    check("Q57 cell beta", 0.052, tc["betas"]["m_trust_general"], 0.0005, rows)
    check("in-group cell beta", 0.224, tc["betas"]["m_trust_in_group"], 0.0005, rows)
    check("out-group cell beta", 0.211, tc["betas"]["m_trust_out_group"], 0.0005, rows)
    check("institution cell beta", 0.285, tc["betas"]["m_trust_institution"], 0.0005, rows)
    check("composite cell beta", 0.318, tc["betas"]["m_trust_composite"], 0.0005, rows)

    # --- country ---
    check("patience_country L", 0.402, pco["range"]["L"], 0.0005, rows)
    check("patience_country U", 0.565, pco["range"]["U"], 0.0005, rows)
    check("patience_country band_L", 0.157, pco["cov"]["band_L"], 0.0005, rows)
    check("patience_country band_U", 0.674, pco["cov"]["band_U"], 0.0005, rows)
    check("patience_country empty_rep", 0.089, pco["cov"]["empty_replicate_rate"], 1e-12, rows)
    check("Llama country edu slack", 0.027, pco["slacks"].loc["m_llm_patience_llama", "conv_edu"], 0.0005, rows)
    check("empty_R L", -0.219, empty_r["L"], 0.0005, rows)
    check("empty_R U", 0.565, empty_r["U"], 0.0005, rows)
    check("human-only country empty_rep", 0.297, pcn["cov"]["empty_replicate_rate"], 1e-12, rows)
    check("human-only country L", 0.402, pcn["range"]["L"], 0.0005, rows)
    check("trust_country L", 0.107, tco["range"]["L"], 0.0005, rows)
    check("trust_country U", 0.481, tco["range"]["U"], 0.0005, rows)
    check("trust_country band_L", -0.016, tco["cov"]["band_L"], 0.0005, rows)
    check("trust_country band_U", 0.699, tco["cov"]["band_U"], 0.0005, rows)
    check("Phi gini slack", -0.158, tco["slacks"].loc["m_llm_trust_phi", "disc_gini"], 0.0005, rows)

    gps_rol = pearson(
        tco["scores"]["m_gps_trust"].to_numpy(),
        tco["scores"]["rule_of_law"].to_numpy(),
    )
    check("GPS trust vs rule_of_law r", 0.12, gps_rol, 0.005, rows)

    facet_r = {}
    for m in [
        "m_trust_general",
        "m_trust_in_group",
        "m_trust_out_group",
        "m_trust_institution",
        "m_trust_composite",
    ]:
        facet_r[m] = pearson(tco["scores"][m].to_numpy(), tco["scores"]["rule_of_law"].to_numpy())
    # Paper: "every WVS facet sits between 0.48 and 0.71"
    in_band = {
        m: 0.48 - 1e-6 <= facet_r[m] <= 0.71 + 1e-6 for m in facet_r
    }
    check("MTMM GPS patience vs child-qualities", -0.252, mtmm["correlations"]["gps_patience"]["m_patience_child_qualities"], 0.0005, rows)
    check("MTMM GPS trust vs Q57", 0.284, mtmm["correlations"]["gps_trust"]["m_trust_general"], 0.0005, rows)
    check("MTMM Q57 vs GPS patience", 0.825, mtmm["correlations"]["m_trust_general"]["gps_patience"], 0.0005, rows)
    check("partial r Q57 vs GPS patience", 0.706, partial["partial_r"], 0.0005, rows)

    d13 = dif["education_assoc_by_level"]["m_wvs_q13"]
    d14 = dif["education_assoc_by_level"]["m_wvs_q14"]
    check("AppI Q13 country edu", -0.33, d13["country_level"], 0.005, rows)
    check("AppI Q13 pooled edu", -0.17, d13["pooled_cell"], 0.005, rows)
    check("AppI Q13 within edu", 0.25, d13["within_cell"], 0.005, rows)
    check("AppI Q14 country edu", -0.59, d14["country_level"], 0.005, rows)
    check("AppI Q14 pooled edu", -0.53, d14["pooled_cell"], 0.005, rows)
    check("AppI Q14 within edu", -0.36, d14["within_cell"], 0.005, rows)
    check("AppI Q13 share_positive", 0.79, dif["country_slopes_vs_education"]["m_wvs_q13"]["share_positive"], 0.01, rows)
    check("AppI Q14 share_negative", 0.88, 1 - dif["country_slopes_vs_education"]["m_wvs_q14"]["share_positive"], 0.01, rows)
    # Table 8 row IV claimed Q14 anti-aligned at both levels (-0.33)
    check("Table8 Q14 both-levels -0.33 vs country edu", -0.33, d14["country_level"], 0.01, rows)
    check("Table8 Q14 both-levels -0.33 vs within edu", -0.33, d14["within_cell"], 0.01, rows)

    # Q13-Q14 co-movement
    r_q13q14_country = pearson(
        pco["scores"]["m_wvs_q13"].to_numpy(), pco["scores"]["m_wvs_q14"].to_numpy()
    )
    pooled = pd.read_csv(RUNS / "patience_cells" / "S_frozen.csv")
    r_q13q14_pooled = pearson(pooled["m_wvs_q13"].to_numpy(), pooled["m_wvs_q14"].to_numpy())
    r_q13q14_within = pearson(
        pc["scores"]["m_wvs_q13"].to_numpy(), pc["scores"]["m_wvs_q14"].to_numpy()
    )
    check("AppI Q13-Q14 country r", 0.83, r_q13q14_country, 0.01, rows)
    check("AppI Q13-Q14 pooled r", 0.52, r_q13q14_pooled, 0.01, rows)

    # n countries from cell unit_id
    n_cty = pc["scores"]["unit_id"].str.split("|").str[0].nunique()
    check("n countries in cells", 42, n_cty, 0, rows)
    check("patience country n", 41, pco["n"], 0, rows)
    check("trust country n", 35, tco["n"], 0, rows)

    # grid anchors
    pgrid = grid["patience_cells_demeaned_llm"]["grid"]
    tgrid = grid["trust_cells_demeaned_llm"]["grid"]
    r0p = next(g for g in pgrid if g["network"].startswith("R0"))
    r4p = next(g for g in pgrid if "0.30" in g["network"] or g.get("theta_edu_select") == 0.3)
    r6p = next(g for g in pgrid if "unrestricted" in g["network"] or g.get("theta_edu_select") is None)
    check("grid patience R0 L", 0.245, r0p["L"], 0.0005, rows)
    check("grid patience R0 U", 0.556, r0p["U"], 0.0005, rows)
    check("grid patience theta0.30 L", 0.417, r4p["L"], 0.0005, rows)
    check("grid trust R1 L", -0.317, next(g for g in tgrid if g.get("theta_edu_select") == 0.1)["L"], 0.0005, rows)
    check("grid trust R1 U", 0.179, next(g for g in tgrid if g.get("theta_edu_select") == 0.1)["U"], 0.0005, rows)

    # human-cell corr(slack, beta)
    human_p = ["m_wvs_q13", "m_wvs_q14", "m_composite"]
    sp = spearman(
        np.array([pc["slacks"].loc[m, "conv_edu_cell"] for m in human_p]),
        np.array([pc["betas"][m] for m in human_p]),
    )
    human_t = [
        "m_trust_general",
        "m_trust_in_group",
        "m_trust_out_group",
        "m_trust_institution",
        "m_trust_composite",
    ]
    st = pearson(
        np.array([tc["slacks"].loc[m, "conv_edu_cell"] for m in human_t]),
        np.array([tc["betas"][m] for m in human_t]),
    )
    check("AppH patience rank corr(slack,beta) human", 1.0, sp, 1e-9, rows)
    check("AppH trust corr(slack,beta) human", -0.82, st, 0.01, rows)

    # Phi coverage margin uses leftover not select
    phi_bound = next(x for x in tc["cov"]["boundary"] if x["measure"] == "m_llm_trust_phi")
    check(
        "Phi coverage margin equals leftover (not select)",
        float(tc["slacks"].loc["m_llm_trust_phi", "mono_edu_cell"]),
        phi_bound["margin"],
        1e-12,
        rows,
    )

    fals_p = comparative_falsification(pc, rng)
    fals_t = comparative_falsification(tc, np.random.default_rng(SEED + 1))
    loo_p = leave_one_out(pc)
    loo_t = leave_one_out(tc)
    diag_p = diagnostics_table(pc)
    diag_t = diagnostics_table(tc)
    fv_p = frozen_vs_reformed_cell(pc, np.random.default_rng(SEED + 2))
    fv_t = frozen_vs_reformed_cell(tc, np.random.default_rng(SEED + 3))

    menus = {
        "patience_cells_unrestricted_all_six_incl_noise": menu_unrestricted(pc, False),
        "patience_cells_unrestricted_five_excl_noise": menu_unrestricted(pc, True),
        "trust_cells_unrestricted_all_eight_incl_noise": menu_unrestricted(tc, False),
        "trust_cells_unrestricted_seven_excl_noise": menu_unrestricted(tc, True),
        "patience_country_seven_incl_noise": menu_unrestricted(pco, False),
        "trust_country_nine_incl_noise": menu_unrestricted(tco, False),
    }

    n_pass = sum(1 for r in rows if r["status"] == "PASS")
    n_fail = sum(1 for r in rows if r["status"] == "FAIL")
    n_unv = sum(1 for r in rows if r["status"] == "UNVERIFIED")

    artifact = {
        "seed": SEED,
        "package_note": "read-only over committed freezes; no engine write",
        "n_checks": len(rows),
        "n_pass": n_pass,
        "n_fail": n_fail,
        "n_unverified": n_unv,
        "checks": rows,
        "facet_rule_of_law_r": {k: r3(v) for k, v in facet_r.items()},
        "gps_trust_rule_of_law_r": r3(gps_rol),
        "q13_q14_r": {
            "country": r3(r_q13q14_country),
            "pooled_cells": r3(r_q13q14_pooled),
            "demeaned_cells": r3(r_q13q14_within),
        },
        "menus": menus,
        "diagnostics_patience_cells": diag_p,
        "diagnostics_trust_cells": diag_t,
        "comparative_falsification_patience_cells": fals_p,
        "comparative_falsification_trust_cells": fals_t,
        "leave_one_out_patience_cells": loo_p,
        "leave_one_out_trust_cells": loo_t,
        "frozen_vs_reformed_patience_cells": fv_p,
        "frozen_vs_reformed_trust_cells": fv_t,
        "M_star": {
            "patience_cells": pc["adm"]["M_star"],
            "trust_cells": tc["adm"]["M_star"],
            "patience_country": pco["adm"]["M_star"],
            "trust_country": tco["adm"]["M_star"],
        },
        "dif_trust_variance": "NOT IN dif_level_dependence.json — App I Result 3 (89-94% between) is UNVERIFIED against the committed artifact",
    }
    (OUT / "audit.json").write_text(json.dumps(artifact, indent=2) + "\n")
    write_markdown(artifact, rows, n_pass, n_fail, n_unv)
    print(f"PASS {n_pass}  FAIL {n_fail}  UNVERIFIED {n_unv}")
    print(f"wrote {OUT / 'audit.json'}")
    print(f"wrote {PAPER}")


def write_markdown(artifact: dict, rows: list[dict], n_pass: int, n_fail: int, n_unv: int) -> None:
    fails = [r for r in rows if r["status"] == "FAIL"]
    lines = [
        "# Number reconciliation — 2026-08-31 (read-only)",
        "",
        "Generated by `evals/wvs_gps_two_resolution/scripts/preprint_number_audit.py`.",
        "Does not modify freezes, θ, or `position_paper.tex`.",
        "",
        f"**Checks:** {n_pass} PASS / {n_fail} FAIL / {n_unv} UNVERIFIED of {len(rows)}.",
        "",
        "## 1. Failures (fix in the next prose pass)",
        "",
    ]
    if not fails:
        lines.append("None.")
    else:
        lines += [
            "| Claim | Paper | Artifact | |δ| |",
            "|---|---:|---:|---:|",
        ]
        for r in fails:
            lines.append(
                f"| {r['claim']} | {r['claimed']} | {r['observed']} | {r['delta']} |"
            )
    lines += [
        "",
        "### Institution / composite vs App H Finding 4",
        "",
        "App H: GPS trust vs rule of law r = +0.12, “every WVS facet sits between 0.48 and 0.71”.",
        "Recomputed Pearson vs `rule_of_law` on `trust_country_llm/S_frozen.csv`:",
        "",
        "| Column | r |",
        "|---|---:|",
        f"| GPS trust | {artifact['gps_trust_rule_of_law_r']} |",
    ]
    for k, v in artifact["facet_rule_of_law_r"].items():
        lines.append(f"| {k} | {v} |")
    lines += [
        "",
        "The 0.48–0.71 band holds only for {Q57, in-group, out-group}.",
        "Institution r ≈ −0.12 and the composite r ≈ 0.40 are outside it.",
        "Institution already fails the rule-of-law gate; the sentence still overstates “every WVS facet”.",
        "",
        "### Table 8 row IV",
        "",
        "Claimed: Perseverance anti-aligned at both levels (−0.33).",
        "App I / `dif_level_dependence.json`: Q14 education association is",
        "−0.592 / −0.525 / −0.364 (country / pooled / within).",
        "−0.33 is Q13’s *country* education association (−0.329).",
        "",
        "### App I Result 3 (trust between-share 89–94%)",
        "",
        artifact["dif_trust_variance"] + ".",
        "",
        "## 2. Menu composition behind every unrestricted range",
        "",
        "| Object | Columns | [L, U] | Endpoint measures |",
        "|---|---|---|---|",
    ]
    labels = {
        "patience_cells_unrestricted_all_six_incl_noise": "Patience cells, n_menu=6 (incl. noise)",
        "patience_cells_unrestricted_five_excl_noise": "Patience cells, five human+LLM (paper “all five”)",
        "trust_cells_unrestricted_all_eight_incl_noise": "Trust cells, n_menu=8 (incl. noise)",
        "trust_cells_unrestricted_seven_excl_noise": "Trust cells, seven excl. noise (paper “all seven”)",
        "patience_country_seven_incl_noise": "Patience country, seven (empty-R object)",
        "trust_country_nine_incl_noise": "Trust country, nine incl. noise",
    }
    for key, lab in labels.items():
        m = artifact["menus"][key]
        cols = ", ".join(m["columns"])
        lines.append(
            f"| {lab} | {cols} | [{m['L']}, {m['U']}] | {m['L_measure']} / {m['U_measure']} |"
        )
    lines += [
        "",
        "Endpoints do not move when noise is dropped (noise is interior).",
        "Paper should still *name* the columns. Cell unrestricted patience",
        "[−0.326, 0.556] is Q14 / Phi. Country unrestricted [−0.219, 0.565]",
        "is composite / Phi on the seven-measure menu including noise.",
        "",
        "## 3. Mandatory §3.5 diagnostics (already in coverage.json, never tabled)",
        "",
        "κ = 2. Margin = min slack (engine uses the binding restriction, which",
        "for Phi-trust is leftover 0.133 not select 0.149). Flag = |margin| ≤ 2 SE.",
        "",
        "### Patience cells (demeaned + LLM)",
        "",
        "| Measure | In M* | β | Select slack | Holdout slack | Margin | SE | κ=2 flag | p̂ admit |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for r in artifact["diagnostics_patience_cells"]:
        ss = next(iter(r["select_slacks"].values()))
        hs = next(iter(r["holdout_slacks"].values()))
        flag = "YES" if r["kappa2_boundary"] else "no"
        lines.append(
            f"| {r['measure']} | {r['admitted']} | {r['beta']} | {ss} | {hs} | "
            f"{r['min_slack_margin']} | {r['boot_SE']} | {flag} | {r['p_hat_admission']} |"
        )
    lines += [
        "",
        "Q13 is the only κ=2 admission. p̂(Q13 admitted) = 0.83, so 17% of",
        "replicates drop the lower endpoint — that is the coupling the paper named",
        "and did not table. Llama/Phi p̂ = 1.0.",
        "",
        "### Trust cells (demeaned + LLM)",
        "",
        "| Measure | In M* | β | Select slack | Holdout slack | Margin | SE | κ=2 flag | p̂ admit |",
        "|---|---|---:|---:|---:|---:|---:|---|---:|",
    ]
    for r in artifact["diagnostics_trust_cells"]:
        ss = next(iter(r["select_slacks"].values()))
        hs = next(iter(r["holdout_slacks"].values()))
        flag = "YES" if r["kappa2_boundary"] else "no"
        lines.append(
            f"| {r['measure']} | {r['admitted']} | {r['beta']} | {ss} | {hs} | "
            f"{r['min_slack_margin']} | {r['boot_SE']} | {flag} | {r['p_hat_admission']} |"
        )
    fp = artifact["frozen_vs_reformed_patience_cells"]
    ft = artifact["frozen_vs_reformed_trust_cells"]
    lines += [
        "",
        "Llama-trust is a κ=2 *near-miss rejection* (p̂ = 0.022). Phi is not on the boundary.",
        "",
        "## 4. Frozen-M* vs re-formed band (cell-exchangeable, not clustered)",
        "",
        "Independent 1000-resample under seed family 20260814+k; Pearson select floor;",
        "β = Pearson vs GPS cell. Not bit-identical to shipped `bootstrap.json`.",
        "",
        "| Profile | Paper coverage band | Re-formed (this script) | Frozen M* | Empty-rep (re-formed) |",
        "|---|---|---|---|---:|",
        f"| Patience cells | {fp['paper_coverage_band']} | {fp['reformed_band']} | {fp['frozen_Mstar_band']} | {fp['empty_replicate_rate_reformed']} |",
        f"| Trust cells | {ft['paper_coverage_band']} | {ft['reformed_band']} | {ft['frozen_Mstar_band']} | {ft['empty_replicate_rate_reformed']} |",
        "",
        "If frozen-M* is materially narrower than re-formed, the extra width is",
        "admission–endpoint coupling. Country-cluster + re-demean is still unrun.",
        "",
        "## 5. Comparative falsification (contribution ii, executed on frozen slacks)",
        "",
        "H(m) = 1 iff every leftover holdout slack ≥ 0. Random = 1000 size-k subsets.",
        "",
    ]
    for name, key in [
        ("Patience cells", "comparative_falsification_patience_cells"),
        ("Trust cells", "comparative_falsification_trust_cells"),
    ]:
        f = artifact[key]
        lines += [
            f"### {name}",
            "",
            f"- M*_S (k={f['k']}): {f['M_star_S']}",
            f"- p̂_S = {r3(f['p_hat_S'])}",
            f"- best-β = {f['best_beta_measure']}, p̂ = {r3(f['p_hat_best_beta'])}",
            f"- best-anchor (highest select slack) = {f['best_anchor_measure']}, p̂ = {r3(f['p_hat_best_anchor'])}",
            f"- random-k mean p̂ = {r3(f['random_k_mean'])}; share of random subsets with p̂ ≥ p̂_S = {r3(f['random_k_share_S_ge'])}",
            "",
        ]
    lines += [
        "Patience: select and holdout are Pearson/Spearman of the same education",
        "auxiliary, so p̂_S = 1 and best-β / best-anchor also pass. The comparison",
        "is nearly vacuous — Coarse was right.",
        "",
        "Trust: construct-guided picks Phi (p̂=1); best-β picks the composite",
        "(fails holdout). That *is* a real contrast, and it is the App H",
        "anti-alignment: validity-guided selection and criterion-fit pull apart.",
        "",
        "## 6. Leave-one-measure-out (menu-curation check, frozen slacks/β)",
        "",
        "### Patience cells",
        "",
        "| Drop | M* | [L, U] | Unrestricted |",
        "|---|---|---|---|",
    ]
    for r in artifact["leave_one_out_patience_cells"]["rows"]:
        lines.append(
            f"| {r['dropped']} | {r['M_star']} | [{r['L']}, {r['U']}] | "
            f"[{r['unrestricted_L']}, {r['unrestricted_U']}] |"
        )
    lines += [
        "",
        "### Trust cells",
        "",
        "| Drop | M* | [L, U] | Unrestricted |",
        "|---|---|---|---|",
    ]
    for r in artifact["leave_one_out_trust_cells"]["rows"]:
        lu = "empty" if r["empty"] else f"[{r['L']}, {r['U']}]"
        lines.append(
            f"| {r['dropped']} | {r['M_star']} | {lu} | "
            f"[{r['unrestricted_L']}, {r['unrestricted_U']}] |"
        )
    lines += [
        "",
        "Patience [0.245, 0.556] becomes the Q13 singleton if both cheap columns",
        "are dropped (already reported). Dropping Q13 leaves [0.417, 0.556].",
        "Dropping noise or Q14 does not move B*. Trust singleton is Phi: drop Phi",
        "and M* is empty.",
        "",
        "## 7. Full check log",
        "",
        "| Status | Claim | Paper | Artifact |",
        "|---|---|---:|---:|",
    ]
    for r in rows:
        lines.append(f"| {r['status']} | {r['claim']} | {r['claimed']} | {r['observed']} |")
    lines.append("")
    PAPER.write_text("\n".join(lines))


if __name__ == "__main__":
    main()
