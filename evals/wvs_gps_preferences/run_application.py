"""WVS/GPS patience application — flagship public-facing empirical example.

Monolith (readability first; refactor later only if it becomes dirty):

    stage 0  parse args / seeds                (stdout = JSON summary; stderr = human notes)
    stage 1  build data (GPS/WVS/WDI) + provenance + frozen inputs   <-- implemented
    stage 2  prompting measures (llama.cpp)    (stub — NotImplementedError)
    stage 3  engine run_profile + units-split + coverage
    stage 4  random-selection baselines + tier-3 holdout moments
    stage 5  summary JSON + report

Frozen specifications (docs/16 §11, D1–D10, 2026-08-10):
  construct = patience (Falk et al. 2018 time preference)
  menu_7    = [m_gps_patience, m_wvs_q13, m_wvs_q14, m_composite,
               m_prompt_a, m_prompt_b, m_noise]
  network   = conv_edu corr_min(q275_mean) 0.20 (select)
              mono_edu monotone_rank(q275_mean, sign=+1) 0.15 (holdout)
              disc_risk corr_zero(risktaking) 0.30 (select)
  beta      = ols_coef, outcome log_gdp_pc, controls [q275_mean]
  outcome   = beta-only; NEVER in R (no selection-on-outcome)
  units     = countries (iso3); 80/20 fixed-seed random units-split
  baseline  = random selection, 500 draws, k-grid 1..4
  data      = respondent floor >= 30; WVS missing -1..-5 masked, never imputed;
              WDI snapshot + sha256 (wbgapi/urllib public API, no key)

Engine is score-agnostic; this harness lives in evals/ and never imports an
LLM client into src/ (AST import-graph lock stays green).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections.abc import Sequence
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import yaml

# ---------------------------------------------------------------------------
# Frozen constants (docs/16 §11)
# ---------------------------------------------------------------------------

MENU_MEASURES: list[str] = [
    "m_gps_patience",
    "m_wvs_q13",
    "m_wvs_q14",
    "m_composite",
    "m_prompt_a",
    "m_prompt_b",
    "m_noise",
]
AUX_COLUMNS: list[str] = ["risktaking", "q275_mean"]
OUTCOME_COLUMN = "log_gdp_pc"
RESPONDENT_FLOOR = 30
WVS_MISSING = {-1, -2, -3, -4, -5}
WVS_ITEMS = ["Q13", "Q14", "Q275"]
AUX_YEARS = (2015, 2019)

NETWORK: dict[str, Any] = {
    "schema_version": "1",
    "name": "wvs_gps_patience_application",
    "delta": 0.0,
    "restrictions": [
        {
            "id": "conv_edu",
            "type": "corr_min",
            "theta": 0.20,
            "params": {"variable": "q275_mean"},
            "stage": "select",
        },
        {
            "id": "mono_edu",
            "type": "monotone_rank",
            "theta": 0.15,
            "params": {"variable": "q275_mean", "sign": 1},
            "stage": "holdout",
        },
        {
            "id": "disc_risk",
            "type": "corr_zero",
            # θ re-anchored 2026-08-10 (docs/12; literature memo in lane):
            # Falk et al. 2018 Table IV ρ=0.230 (n=76); Hanushek et al. 2022
            # ρ=0.358 (n=49); Netspar preprint 0.30 excl. Africa. θ=0.30 sat
            # inside the published range and rejected the positive control on
            # a 0.21-SE train-frame knife-edge (slack -0.035). 0.35 remains a
            # binding discriminant (rejects r >= 0.6).
            "theta": 0.35,
            "params": {"variable": "risktaking"},
            "stage": "select",
        },
    ],
}

BETA: dict[str, Any] = {
    "schema_version": "1",
    "type": "ols_coef",
    "outcome": OUTCOME_COLUMN,
    "params": {"controls": [AUX_COLUMNS[1]]},  # q275_mean
}

# ---------------------------------------------------------------------------
# Small helpers
# ---------------------------------------------------------------------------


def mask_missing(s: pd.Series) -> pd.Series:
    """Mask WVS official missing codes (-1..-5) to NaN; never impute."""
    return s.where(~s.isin(WVS_MISSING))


def canonical_csv_hash(df: pd.DataFrame) -> str:
    """Stable SHA-256 of the canonical CSV (sorted columns, LF, no index)."""
    canon = df.copy().sort_index(axis=1)
    canon = canon.sort_values(by=canon.columns[0]).reset_index(drop=True)
    text = canon.to_csv(index=False, lineterminator="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_yaml(path: Path | str) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def zscore(v: pd.Series) -> pd.Series:
    sd = float(v.std(ddof=0))
    if not np.isfinite(sd) or sd == 0.0:
        raise ValueError("zscore requires non-zero variance")
    return (v - float(v.mean())) / sd


# ---------------------------------------------------------------------------
# Stage 1 — data build (pure functions; tests feed synthetic frames)
# ---------------------------------------------------------------------------


def wvs_country_means(
    wvs: pd.DataFrame, items: list[str], floor: int = RESPONDENT_FLOOR
) -> pd.DataFrame:
    """Country means of WVS items, masking missing codes.

    A country enters only if EVERY requested item has >= floor valid
    (non-missing) responses; below-floor countries are excluded (the
    respondent-floor rule at country level). Never imputes.
    """
    country_col = next(
        (c for c in ["B_COUNTRY_ALPHA", "country", "COUNTRY_ALPHA"] if c in wvs.columns),
        None,
    )
    if country_col is None:
        raise ValueError(f"WVS frame lacks country column; got {list(wvs.columns)}")
    present = [c for c in items if c in wvs.columns]
    missing = [c for c in items if c not in wvs.columns]
    if missing:
        raise ValueError(f"WVS frame lacks items {missing}; got {list(wvs.columns)}")
    clean = wvs.copy()
    for c in present:
        clean[c] = pd.to_numeric(clean[c], errors="coerce")
        clean[c] = mask_missing(clean[c])
    counts = clean.groupby(country_col)[present].count()
    keep = counts[counts.min(axis=1) >= floor].index
    means = clean[clean[country_col].isin(keep)].groupby(country_col)[present].mean()
    out = means.rename_axis("unit_id").reset_index()
    return out


def merge_universe(
    gps: pd.DataFrame,
    wvs: pd.DataFrame,
    wdi: pd.DataFrame,
    floor: int = RESPONDENT_FLOOR,
) -> tuple[pd.DataFrame, dict[str, list[str]]]:
    """Inner-join GPS ∩ WVS ∩ WDI-aux; record every drop with a reason.

    Drops recorded: below_floor (WVS country excluded by respondent floor),
    missing_gps / missing_wvs_means / missing_wdi (absent from that source),
    missing_coverage (present but NaN in a needed measure/aux/outcome).
    Never impute.
    """
    drops: dict[str, list[str]] = {
        "below_floor": [],
        "missing_gps": [],
        "missing_wvs": [],
        "missing_wdi": [],
        "missing_coverage": [],
    }

    gps_col = next((c for c in ["isocode", "iso3", "ISO3"] if c in gps.columns), None)
    if gps_col is None:
        raise ValueError(f"GPS frame lacks country column; got {list(gps.columns)}")
    gps_s = gps[[gps_col, "patience", "risktaking"]].rename(columns={gps_col: "unit_id"})

    means = wvs_country_means(wvs, items=WVS_ITEMS, floor=floor)
    means = means.rename(columns={"Q275": "q275_mean"})
    wdi_col = next((c for c in ["iso3", "isocode"] if c in wdi.columns), None)
    if wdi_col is None:
        raise ValueError(f"WDI frame lacks country column; got {list(wdi.columns)}")
    wdi_s = wdi[[wdi_col, OUTCOME_COLUMN]].rename(columns={wdi_col: "unit_id"})

    gps_ids = set(gps_s["unit_id"])
    wvs_raw_ids = set(wvs_country_means(wvs, items=WVS_ITEMS, floor=0)["unit_id"])
    wvs_floor_ids = set(means["unit_id"])
    wdi_ids = set(wdi_s["unit_id"])

    merged = (
        gps_s.merge(means, on="unit_id", how="inner")
        .merge(wdi_s, on="unit_id", how="inner")
    )
    drops["below_floor"] = sorted((gps_ids & wvs_raw_ids) - wvs_floor_ids)
    drops["missing_gps"] = sorted(wvs_raw_ids - gps_ids)
    drops["missing_wvs"] = sorted(gps_ids - wvs_raw_ids)
    drops["missing_wdi"] = sorted((gps_ids & wvs_floor_ids) - wdi_ids)

    before = set(merged["unit_id"])
    needed = ["patience", "risktaking", "q275_mean", OUTCOME_COLUMN]
    merged = merged.dropna(subset=needed)
    drops["missing_coverage"] = sorted(before - set(merged["unit_id"]))
    return merged.reset_index(drop=True), drops


def compose_scores(merged: pd.DataFrame, seed: int) -> pd.DataFrame:
    """Add composite C = F(phi), seeded noise, and prompt stubs.

    m_composite = z(Q13) + z(Q14)   (explicit F, no PCA; ddof=0 z-scores)
    m_noise     = seeded Gaussian   (negative control; deterministic per seed)
    m_prompt_a/b = seeded stubs for stage-1 plumbing; the frozen run requires
                   prompt_source="llama.cpp" (stage 2) — stubs are NOT
                   frozen-run material (writer refuses without an explicit
                   prompt_source declaration).
    """
    frame = merged.copy()
    frame["m_gps_patience"] = frame["patience"]
    frame["m_wvs_q13"] = frame["Q13"]
    frame["m_wvs_q14"] = frame["Q14"]
    frame["m_composite"] = zscore(frame["m_wvs_q13"]) + zscore(frame["m_wvs_q14"])
    rng = np.random.default_rng(seed)
    frame["m_noise"] = rng.normal(size=len(frame))
    frame["m_prompt_a"] = np.random.default_rng(seed + 101).normal(size=len(frame))
    frame["m_prompt_b"] = np.random.default_rng(seed + 202).normal(size=len(frame))
    keep = ["unit_id", *MENU_MEASURES, *AUX_COLUMNS, OUTCOME_COLUMN]
    return frame[keep].copy()


def write_frozen_inputs(
    out_dir: Path | str,
    frame: pd.DataFrame,
    drops: dict[str, list[str]],
    seed: int,
    prompt_source: str | dict[str, Any] | None,
    sources: dict[str, Any] | None = None,
) -> dict[str, Path]:
    """Write scores.csv + roles.json + network.yaml + beta.yaml + manifest.

    prompt_source MUST be declared (e.g. "stub" for plumbing smoke, or a
    llama.cpp record for the frozen run). None raises — a frozen scores.csv
    must never silently carry undeclared prompt columns.
    """
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if prompt_source is None:
        raise ValueError(
            "prompt_source must be declared ('stub' for smoke, or a llama.cpp "
            "record for the frozen run); refusing to write undeclared prompts"
        )

    scores_path = out / "scores.csv"
    frame.to_csv(scores_path, index=False)
    roles = {
        "unit_id": "unit_id",
        "measures": MENU_MEASURES,
        "aux": AUX_COLUMNS,
        "outcome": OUTCOME_COLUMN,
    }
    (out / "roles.json").write_text(json.dumps(roles, indent=2) + "\n")
    (out / "network.yaml").write_text(yaml.safe_dump(NETWORK, sort_keys=False))
    (out / "beta.yaml").write_text(yaml.safe_dump(BETA, sort_keys=False))

    manifest: dict[str, Any] = {
        "schema_version": "1",
        "construct": "patience",
        "menu": MENU_MEASURES,
        "n_rows": len(frame),
        "scores_hash": canonical_csv_hash(frame),
        "universe": drops,
        "seed": seed,
        "prompt_source": prompt_source,
        "respondent_floor": RESPONDENT_FLOOR,
        "wvs_items": WVS_ITEMS,
        "aux_years": list(AUX_YEARS),
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": sources or {},
    }
    (out / "score_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return {
        "scores.csv": scores_path,
        "roles.json": out / "roles.json",
        "network.yaml": out / "network.yaml",
        "beta.yaml": out / "beta.yaml",
        "score_manifest.json": out / "score_manifest.json",
    }


# ---------------------------------------------------------------------------
# Stage 1 — real-data loaders (opt-in; tests never call these)
# ---------------------------------------------------------------------------


def load_gps_country(path: Path) -> pd.DataFrame:
    gps = pd.read_stata(path, convert_categoricals=False)
    return gps


def load_wvs_raw(path: Path) -> pd.DataFrame:
    return pd.read_stata(path, convert_categoricals=False)


def fetch_wdi_aux(aux_dir: Path) -> Path:
    """Fetch WDI log GDP pc (PPP, constant) 2015-2019 via public API, snapshot CSV.

    Uses the same public World Bank JSON endpoint as the H5 builder (no key).
    Deterministic once cached; tests never call this.
    """
    import urllib.request

    aux_dir.mkdir(parents=True, exist_ok=True)
    wdi_path = aux_dir / "wdi.csv"
    url = (
        "https://api.worldbank.org/v2/country/all/indicator/NY.GDP.PCAP.PP.KD"
        f"?date={AUX_YEARS[0]}:{AUX_YEARS[1]}&format=json&per_page=20000"
    )
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310
        body = json.loads(resp.read().decode("utf-8"))
    rows = []
    for rec in body[1]:
        iso3 = rec.get("countryiso3code", "")
        value = rec.get("value")
        if value is None or len(iso3) != 3 or not iso3.isalpha():
            continue
        rows.append({"iso3": iso3, "year": int(rec["date"]), OUTCOME_COLUMN: float(value)})
    df = pd.DataFrame(rows)
    # average over the aux window -> one log GDP pc per country
    df[OUTCOME_COLUMN] = np.log(df[OUTCOME_COLUMN])
    out = df.groupby("iso3")[OUTCOME_COLUMN].mean().rename_axis("iso3").reset_index()
    out.to_csv(wdi_path, index=False)
    return wdi_path


def build_real_stage1(
    gps_path: Path,
    wvs_path: Path,
    wdi_path: Path | None,
    out_dir: Path,
    seed: int,
    prompt_source: str | dict[str, Any],
) -> dict[str, Path]:
    """Full stage-1 real-data build. wdi_path=None fetches from the API."""
    gps = load_gps_country(gps_path)
    wvs = load_wvs_raw(wvs_path)
    if wdi_path is None:
        wdi_path = fetch_wdi_aux(out_dir / "aux")
    wdi = pd.read_csv(wdi_path)
    merged, drops = merge_universe(gps, wvs, wdi, floor=RESPONDENT_FLOOR)
    frame = compose_scores(merged, seed=seed)
    sources = {
        "gps": str(gps_path),
        "wvs": str(wvs_path),
        "wdi": str(wdi_path),
    }
    return write_frozen_inputs(
        out_dir=out_dir / "inputs",
        frame=frame,
        drops=drops,
        seed=seed,
        prompt_source=prompt_source,
        sources=sources,
    )


# ---------------------------------------------------------------------------
# Stage 2 — prompting measures (llama.cpp log-prob scoring)
#
# PROMPT ITEMS ARE DRAFT-FOR-AUGUSTO-FREEZE (measure-generation content;
# same status as the θ anchors before D4). The frozen run pins these exact
# templates; do not change them after the freeze without a dated decision.
# ---------------------------------------------------------------------------

PROMPT_ITEMS: list[dict[str, Any]] = [
    {
        "id": "p01",
        "template": (
            "Consider a typical adult living in {country}. They can receive "
            "100 units of money today or 150 units in 12 months. Which would "
            "most people in {country} choose?\n"
            "A. Receive 100 today\nB. Receive 150 in 12 months\nAnswer:"
        ),
        "options": {"A": None, "B": None},
    },
    {
        "id": "p02",
        "template": (
            "Consider a typical adult living in {country}. They can receive "
            "100 units of money today or 120 units in 12 months. Which would "
            "most people in {country} choose?\n"
            "A. Receive 100 today\nB. Receive 120 in 12 months\nAnswer:"
        ),
        "options": {"A": None, "B": None},
    },
    {
        "id": "p03",
        "template": (
            "Consider a typical adult living in {country}. They can receive "
            "100 units of money today or 200 units in 24 months. Which would "
            "most people in {country} choose?\n"
            "A. Receive 100 today\nB. Receive 200 in 24 months\nAnswer:"
        ),
        "options": {"A": None, "B": None},
    },
    {
        "id": "p04",
        "template": (
            "Consider a typical adult living in {country}. How much do they "
            "prioritize long-term planning over immediate enjoyment?\n"
            "A. They prefer immediate enjoyment\nB. They are willing to wait "
            "for larger rewards\nAnswer:"
        ),
        "options": {"A": None, "B": None},
    },
    {
        "id": "p05",
        "template": (
            "Which statement better describes most people in {country}?\n"
            "A. They find it hard to save because they prefer spending now\n"
            "B. They save regularly because they value future security\n"
            "Answer:"
        ),
        "options": {"A": None, "B": None},
    },
]
PATIENT_OPTION = "B"


def option_probabilities(
    logits: np.ndarray, option_tokens: dict[str, list[int]]
) -> dict[str, float]:
    """Softmax over the given option token ids -> P(option).

    ``logits`` is the next-token logits vector (vocab size). Each option maps
    to one or more token ids (e.g. "B" and " B"); probabilities sum over
    variants. Token ids outside the vocab are skipped. Non-empty options only.
    """
    out: dict[str, float] = {}
    for label, ids in option_tokens.items():
        if not ids:
            raise ValueError(f"option {label!r} has no candidate token ids")
        valid = [i for i in ids if 0 <= i < len(logits)]
        if not valid:
            out[label] = 0.0
            continue
        z = np.logaddexp.reduce(logits[valid]) if len(valid) > 1 else logits[valid[0]]
        out[label] = float(np.exp(z))
    total = sum(out.values())
    if total <= 0.0:
        raise ValueError("option probabilities did not normalize (all zero?)")
    return {k: v / total for k, v in out.items()}


def score_country(
    item_probs: list[dict[str, float]], patient_option: str = PATIENT_OPTION
) -> float:
    """Country patience score = mean over items of P(patient option)."""
    vals: list[float] = []
    for p in item_probs:
        if patient_option not in p:
            raise ValueError(f"patient option {patient_option!r} missing from item probs")
        vals.append(p[patient_option])
    if not vals:
        raise ValueError("no item probabilities to aggregate")
    return float(np.mean(vals))


def render_prompt(template: str, country: str) -> str:
    return template.format(country=country)


def build_option_token_map(
    llm: Any, options: dict[str, None]
) -> dict[str, list[int]]:
    """Map each option label to candidate token ids (label and space+label).

    ``tokenize`` prepends a BOS token; take the LAST token of each encoding
    so "A" -> [32] and " A" -> [362] (distinct ids) instead of both mapping
    to the BOS id (which would make every option degenerate-equal).
    """
    out: dict[str, list[int]] = {}
    for label in options:
        ids: list[int] = []
        for text in (label, " " + label):
            toks = llm.tokenize(text.encode("utf-8"))
            if toks:
                ids.append(int(toks[-1]))
        out[label] = sorted(set(ids))
    return out


def _sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_llm(model_path: Path, seed: int, n_gpu_layers: int = 35) -> Any:
    """Load a pinned GGUF via llama-cpp-python (lazy import; Metal offload)."""
    try:
        from llama_cpp import Llama
    except ImportError as exc:  # pragma: no cover - environment check
        raise RuntimeError(
            "llama-cpp-python is not installed; run "
            "'uv pip install llama-cpp-python' to score prompt measures"
        ) from exc
    return Llama(
        model_path=str(model_path),
        n_ctx=4096,
        n_gpu_layers=n_gpu_layers,
        seed=seed,
        verbose=False,
        logits_all=True,  # populate eval_logits so we can read next-token logits
    )


def score_country_with_llm(
    llm: Any,
    country: str,
    items: list[dict[str, Any]],
    patient_option: str = PATIENT_OPTION,
) -> tuple[float, list[dict[str, float]]]:
    """Score one country: for each item, render -> eval -> option probs."""
    item_probs: list[dict[str, float]] = []
    for item in items:
        prompt = render_prompt(item["template"], country)
        tokens = llm.tokenize(prompt.encode("utf-8"))
        llm.reset()
        llm.eval(tokens)
        # eval_logits holds per-token logits; the LAST row is the
        # next-token prediction we score the option labels against.
        logits = np.asarray(llm.eval_logits, dtype=float)[-1]
        opt_map = build_option_token_map(llm, item["options"])
        probs = option_probabilities(logits, opt_map)
        item_probs.append(probs)
    return score_country(item_probs, patient_option), item_probs


def update_prompt_columns(
    out_dir: Path | str,
    prompt_a: dict[str, float],
    prompt_b: dict[str, float],
    prompt_source: str | dict[str, Any],
) -> dict[str, Any]:
    """Replace stub prompt columns in scores.csv with real model scores.

    Re-reads the frozen inputs, replaces m_prompt_a / m_prompt_b, re-hashes,
    and updates the manifest prompt_source. Only an explicit llama.cpp record
    may overwrite stubs; "stub" is rejected (a frozen scores.csv must never
    silently keep placeholders).
    """
    out = Path(out_dir)
    if not isinstance(prompt_source, dict) or prompt_source.get("kind") != "llama.cpp":
        raise ValueError(
            "update_prompt_columns requires a llama.cpp prompt_source record; "
            "refusing to overwrite stubs with a non-model source"
        )
    scores_path = out / "scores.csv"
    scores = pd.read_csv(scores_path)
    missing_a = [u for u in scores["unit_id"] if u not in prompt_a]
    missing_b = [u for u in scores["unit_id"] if u not in prompt_b]
    if missing_a or missing_b:
        raise ValueError(
            "missing prompt scores for countries: "
            f"{sorted(set(missing_a + missing_b))}"
        )
    scores["m_prompt_a"] = scores["unit_id"].map(prompt_a)
    scores["m_prompt_b"] = scores["unit_id"].map(prompt_b)
    scores.to_csv(scores_path, index=False)

    manifest_path = out / "score_manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["scores_hash"] = canonical_csv_hash(scores)
    manifest["prompt_source"] = prompt_source
    manifest["prompt_items"] = [i["id"] for i in PROMPT_ITEMS]
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def score_model_arm(
    llm: Any,
    units: list[str],
    items: list[dict[str, Any]],
) -> dict[str, float]:
    """Score every unit with one loaded model -> {unit_id: patience score}."""
    out: dict[str, float] = {}
    for i, country in enumerate(units):
        score, _probs = score_country_with_llm(llm, country, items)
        out[country] = score
        print(f"  [{i+1}/{len(units)}] {country}: {score:.3f}", file=sys.stderr)
    return out


def run_prompting(
    out_dir: Path | str,
    model_a: Path,
    model_a_meta: dict[str, Any],
    model_b: Path,
    model_b_meta: dict[str, Any],
    seed: int,
    subset: int | None = None,
) -> dict[str, Any]:
    """Score all countries with both frozen prompt arms; write real columns.

    ``model_*_meta`` carry the pinned provenance (repo, file, sha256, quant,
    runtime version). ``subset`` limits countries for smoke runs; the frozen
    run passes subset=None. Human progress -> stderr; returns the manifest.
    """
    out = Path(out_dir)
    scores_path = out / "scores.csv"
    if not scores_path.exists():
        scores_path = out / "inputs" / "scores.csv"
    if not scores_path.exists():
        raise FileNotFoundError(f"stage-1 inputs not found under {out_dir}")
    scores = pd.read_csv(scores_path)
    units = list(scores["unit_id"])
    if subset is not None:
        units = units[:subset]

    print(f"arm A: {model_a.name}", file=sys.stderr)
    llm_a = load_llm(model_a, seed=seed)
    prompt_a = score_model_arm(llm_a, units, PROMPT_ITEMS)

    print(f"arm B: {model_b.name}", file=sys.stderr)
    llm_b = load_llm(model_b, seed=seed)
    prompt_b = score_model_arm(llm_b, units, PROMPT_ITEMS)

    prompt_source: dict[str, Any] = {
        "kind": "llama.cpp",
        "model_a": model_a_meta,
        "model_b": model_b_meta,
        "items": [i["id"] for i in PROMPT_ITEMS],
        "patient_option": PATIENT_OPTION,
        "temperature": 0.0,
        "seed": seed,
    }
    manifest = update_prompt_columns(
        scores_path.parent,
        prompt_a=prompt_a,
        prompt_b=prompt_b,
        prompt_source=prompt_source,
    )
    return manifest


# ---------------------------------------------------------------------------
# Stage 3 — engine run (units-split + bootstrap + coverage)
# ---------------------------------------------------------------------------

HOLDOUT_FRACTION = 0.20


def make_holdout_split(
    units: list[str], split_seed: int, fraction: float = HOLDOUT_FRACTION
) -> list[str]:
    """Fixed-seed random ~fraction of units -> sorted holdout list.

    Deterministic given (units order, seed, fraction); >=2 holdout and >=2
    train so the engine's units-split contract holds (evaluators need n>=2
    per frame). Returns sorted-unique ids so list order cannot fork run_id.
    """
    if not 0.05 <= fraction <= 0.4:
        raise ValueError(f"fraction must be in [0.05, 0.4]; got {fraction}")
    units_sorted = sorted(set(units))
    rng = np.random.default_rng(split_seed)
    n_hold = max(2, int(round(fraction * len(units_sorted))))
    n_train = len(units_sorted) - n_hold
    if n_train < 2:
        n_hold = len(units_sorted) - 2
    perm = rng.permutation(units_sorted)
    return sorted(perm[:n_hold])


def stage3_engine(
    data_dir: Path | str,
    out_dir: Path | str,
    seed: int,
    split_seed: int,
    n_boot: int | None = None,
    alpha: float = 0.10,
    kappa: float = 2.0,
    holdout_units: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Run the engine on stage-1/2 inputs with the frozen units-split.

    Reads inputs/{scores,roles,network,beta}, computes the fixed-seed 80/20
    country holdout split (unless ``holdout_units`` is given, e.g. one fold
    of a pooled K-fold design), calls run_profile (holdout + bootstrap +
    coverage), returns the summary dict. The frozen run is a stage-2-completed
    inputs dir; smoke runs may use the smoke_stage2 dir.
    """
    from cvprofiles.pipeline import run_profile, summary_dict

    data = Path(data_dir)
    inputs = data / "inputs" if (data / "inputs").exists() else data
    scores = inputs / "scores.csv"
    if not scores.exists():
        raise FileNotFoundError(f"stage-1 inputs not found: {scores}")

    frame = pd.read_csv(scores)
    units = sorted(set(frame["unit_id"].astype(str)))
    if holdout_units is None:
        holdout = make_holdout_split(units, split_seed=split_seed)
    else:
        holdout = sorted(set(str(u) for u in holdout_units))

    result = run_profile(
        scores=scores,
        roles=inputs / "roles.json",
        network=inputs / "network.yaml",
        beta=inputs / "beta.yaml",
        out_dir=out_dir,
        seed=seed,
        title="WVS/GPS patience application",
        n_boot=n_boot,
        holdout_units=holdout,
        alpha=alpha,
        kappa=kappa,
    )
    s = summary_dict(result)
    s["n_units"] = len(units)
    s["holdout_units"] = holdout
    s["split_seed"] = split_seed
    return s


# ---------------------------------------------------------------------------
# Later stages (explicit stubs — not yet implemented)
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Stage 4 — random-selection baselines (falsifiable core)
# ---------------------------------------------------------------------------

RESTRICTIONS_OF = {
    "all": lambda r: True,
    "select": lambda r: r.stage is None or r.stage == "select",
    "holdout": lambda r: r.stage == "holdout",
}


def _restriction_list(
    network_yaml: dict[str, Any], stage_filter: str | None
) -> list[Any]:
    from cvprofiles.schemas.network import NetworkConfig

    net = NetworkConfig.model_validate(network_yaml)
    if stage_filter is None or stage_filter == "all":
        return net.restrictions
    if stage_filter not in RESTRICTIONS_OF:
        raise ValueError(f"unknown stage_filter {stage_filter!r}")
    return [r for r in net.restrictions if RESTRICTIONS_OF[stage_filter](r)]


def holdout_pass_rate(
    hold_frame: pd.DataFrame,
    measures: list[str],
    network_yaml: dict[str, Any],
    stage_filter: str | None = None,
    delta: float = 0.0,
) -> float:
    """Fraction of ``measures`` complying on the HOLD frame.

    Compliance = slack >= -delta for every restriction in the chosen stage
    filter (None = all restrictions; "holdout" = tier-3 moments only). This
    is the held-out-moment test: measures selected on train are judged on
    countries they never saw.
    """
    from cvprofiles.identify.slacks import slack_matrix

    if not measures:
        return 0.0
    restrs = _restriction_list(network_yaml, stage_filter)
    if not restrs:
        return 1.0  # vacuous: no restrictions in this stage filter
    sl = slack_matrix(hold_frame, measures, restrs)
    n_pass = 0
    for m in measures:
        if all(float(sl.at[m, r.id]) >= -delta for r in restrs):
            n_pass += 1
    return n_pass / len(measures)


def random_subset_baseline(
    hold_frame: pd.DataFrame,
    k: int,
    n_draws: int,
    seed: int,
    network_yaml: dict[str, Any],
    stage_filter: str | None = None,
    menu: list[str] | None = None,
) -> list[float]:
    """Holdout pass-rate distribution over random subsets of size k.

    Seeded; draws are subsets of ``menu`` (default the frozen menu). Each
    value = holdout_pass_rate for one random subset. This is the null: how
    well does blind selection do on held-out moments?
    """
    if k < 1:
        raise ValueError("k must be >= 1")
    menu = menu or list(MENU_MEASURES)
    rng = np.random.default_rng(seed)
    out: list[float] = []
    for _ in range(n_draws):
        subset = list(rng.choice(menu, size=k, replace=False))
        out.append(
            holdout_pass_rate(hold_frame, subset, network_yaml, stage_filter=stage_filter)
        )
    return out


def percentile_in_baseline(value: float, baseline: list[float]) -> float:
    """Fraction of baseline draws <= value (empirical percentile in [0,1])."""
    if not baseline:
        raise ValueError("empty baseline")
    return float(np.mean([v <= value for v in baseline]))


def tool_range_width(
    frame: pd.DataFrame,
    measures: list[str],
    beta_yaml: dict[str, Any],
) -> float | None:
    """Width of [min,max] beta over ``measures`` on ``frame``.

    None when the set is empty (no survivors -> no range, matching the
    engine's empty-M* semantics).
    """
    from cvprofiles.identify.beta_fn import evaluate_beta
    from cvprofiles.schemas.beta import BetaSpec

    if not measures:
        return None
    beta = BetaSpec.model_validate(beta_yaml)
    vals = [float(evaluate_beta(frame, m, beta)) for m in measures]
    return float(max(vals) - min(vals))


def random_subset_range_widths(
    frame: pd.DataFrame,
    k: int,
    n_draws: int,
    seed: int,
    network_yaml: dict[str, Any],
    beta_yaml: dict[str, Any],
    menu: list[str] | None = None,
) -> list[float]:
    """Width distribution of beta over random subsets of size k."""
    if k < 1:
        raise ValueError("k must be >= 1")
    menu = menu or list(MENU_MEASURES)
    rng = np.random.default_rng(seed)
    out: list[float] = []
    for _ in range(n_draws):
        subset = list(rng.choice(menu, size=k, replace=False))
        w = tool_range_width(frame, subset, beta_yaml)
        if w is not None:
            out.append(w)
    return out


def stage4_baselines(
    data_dir: Path | str,
    seed: int,
    split_seed: int,
    n_draws: int = 500,
    k_grid: tuple[int, ...] = (1, 2, 3, 4),
    n_boot: int | None = 100,
    alpha: float = 0.10,
    kappa: float = 2.0,
) -> dict[str, Any]:
    """Run the falsifiable baselines on the current inputs.

    Returns a JSON-ready payload: tool holdout pass-rate (robust set vs
    random distribution per k), tool range width vs random width
    distribution, and percentiles. Requires stage-3 run artifacts for the
    robust set (or recomputes it via the engine if absent).
    """
    data = Path(data_dir)
    inputs = data / "inputs" if (data / "inputs").exists() else data
    frame = pd.read_csv(inputs / "scores.csv")
    network_yaml = load_yaml(inputs / "network.yaml")
    beta_yaml = load_yaml(inputs / "beta.yaml")

    units = sorted(set(frame["unit_id"].astype(str)))
    hold_units = make_holdout_split(units, split_seed=split_seed)
    hold = frame[frame["unit_id"].astype(str).isin(hold_units)].reset_index(drop=True)

    # Recompute the robust set via the engine (deterministic; same inputs).
    s3 = stage3_engine(
        data_dir=data,
        out_dir=data / "runs_stage4",
        seed=seed,
        split_seed=split_seed,
        n_boot=n_boot,
        alpha=alpha,
        kappa=kappa,
    )
    robust = list(s3.get("M_star_robust") or [])
    select = list(s3.get("M_star_select") or [])

    tool_rate = holdout_pass_rate(hold, robust, network_yaml)
    tool_width = tool_range_width(frame, robust, beta_yaml)

    baseline_payload: dict[str, Any] = {}
    for k in k_grid:
        draws = random_subset_baseline(
            hold, k=k, n_draws=n_draws, seed=seed + k, network_yaml=network_yaml
        )
        widths = random_subset_range_widths(
            frame, k=k, n_draws=n_draws, seed=seed + k,
            network_yaml=network_yaml, beta_yaml=beta_yaml,
        )
        baseline_payload[str(k)] = {
            "draws": n_draws,
            "pass_rate_mean": float(np.mean(draws)),
            "pass_rate_p05": float(np.quantile(draws, 0.05)),
            "pass_rate_p50": float(np.quantile(draws, 0.50)),
            "pass_rate_p95": float(np.quantile(draws, 0.95)),
            "tool_percentile": percentile_in_baseline(tool_rate, draws),
            "width_mean": float(np.mean(widths)) if widths else None,
            "width_p50": float(np.quantile(widths, 0.50)) if widths else None,
        }

    return {
        "n_units": len(units),
        "n_holdout": len(hold_units),
        "M_star_select": select,
        "M_star_robust": robust,
        "tool_holdout_pass_rate": tool_rate,
        "tool_range_width": tool_width,
        "random_baseline": baseline_payload,
        "n_draws": n_draws,
        "k_grid": list(k_grid),
        "seed": seed,
        "split_seed": split_seed,
    }


# ---------------------------------------------------------------------------
# Stage 3b — pooled K-fold holdout (docs/16 §11 amendment 2026-08-10)
# ---------------------------------------------------------------------------


def make_kfold_splits(
    units: list[str], k: int, split_seed: int
) -> list[list[str]]:
    """K-fold country split; each unit held out exactly once.

    Deterministic given (units, k, seed). Each fold's holdout list has >= 2
    units (engine contract: evaluators need n >= 2 per frame) and train has
    >= 2 by construction when k <= n//2.
    """
    if k < 2:
        raise ValueError("k must be >= 2")
    units_sorted = sorted(set(units))
    n = len(units_sorted)
    if k > n // 2:
        raise ValueError(f"k={k} too large for n={n} (need k <= n//2)")
    rng = np.random.default_rng(split_seed)
    perm = rng.permutation(units_sorted)
    folds: list[list[str]] = []
    base, rem = divmod(n, k)
    start = 0
    for f in range(k):
        size = base + (1 if f < rem else 0)
        folds.append(sorted(perm[start : start + size]))
        start += size
    return folds


def pool_holdout_verdicts(
    per_fold_select: list[list[str]],
    per_fold_compliant: list[list[str]],
) -> tuple[list[str], list[str], list[str]]:
    """Pool per-fold verdicts -> (selected_all, compliant_all, robust).

    selected_all = measures in M*_select^(f) for EVERY fold f.
    compliant_all = measures whose holdout verdict is empty in EVERY fold.
    robust = selected_all ∩ compliant_all (sorted).
    """
    if not per_fold_select or len(per_fold_select) != len(per_fold_compliant):
        raise ValueError("per-fold select/compliant must be non-empty and same length")
    k = len(per_fold_select)
    candidates = set(per_fold_select[0])
    for f in range(1, k):
        candidates &= set(per_fold_select[f])
    selected_all = sorted(candidates)

    compliant_all = sorted(
        m
        for m in candidates
        if all(m in per_fold_compliant[f] for f in range(k))
    )
    robust = sorted(set(selected_all) & set(compliant_all))
    return selected_all, compliant_all, robust


def pooled_stage3(
    data_dir: Path | str,
    out_dir: Path | str,
    seed: int,
    split_seed: int,
    k: int = 5,
    n_boot: int | None = None,
    alpha: float = 0.10,
    kappa: float = 2.0,
) -> dict[str, Any]:
    """Run the engine once per fold; pool the verdicts.

    For each fold f (holdout = fold f): stage3_engine gives M*_select^(f) and
    the holdout verdict on fold f's countries. Pooling per
    pool_holdout_verdicts; headline [L,U] = min/max beta over pooled_robust
    (beta evaluated on the full frame, matching engine semantics).
    """
    from cvprofiles.identify.beta_fn import evaluate_beta
    from cvprofiles.schemas.beta import BetaSpec

    data = Path(data_dir)
    inputs = data / "inputs" if (data / "inputs").exists() else data
    scores = inputs / "scores.csv"
    if not scores.exists():
        raise FileNotFoundError(f"stage-1 inputs not found: {scores}")
    frame = pd.read_csv(scores)
    units = sorted(set(frame["unit_id"].astype(str)))
    folds = make_kfold_splits(units, k=k, split_seed=split_seed)

    per_fold_select: list[list[str]] = []
    per_fold_compliant: list[list[str]] = []
    fold_summaries: list[dict[str, Any]] = []
    for f_idx, hold in enumerate(folds):
        fold_dir = Path(out_dir) / f"fold{f_idx}"
        s = stage3_engine(
            data_dir=data,
            out_dir=fold_dir,
            seed=seed,
            split_seed=split_seed,
            n_boot=n_boot,
            alpha=alpha,
            kappa=kappa,
            holdout_units=hold,  # THIS fold is the holdout
        )
        fold_summaries.append(s)
        per_fold_select.append(list(s.get("M_star_select") or []))
        # holdout verdict: measures with empty failing list comply on the fold
        # (parsed from admissible.json written by stage3_engine).
        adm_path = fold_dir / "admissible.json"
        adm = json.loads(adm_path.read_text()) if adm_path.exists() else {}
        verdict = (adm.get("holdout") or {}).get("verdict") or {}
        per_fold_compliant.append(
            [m for m in app_menu() if m not in verdict]
        )

    selected_all, compliant_all, robust = pool_holdout_verdicts(
        per_fold_select, per_fold_compliant
    )

    beta = BetaSpec.model_validate(load_yaml(inputs / "beta.yaml"))
    b_vals = {m: float(evaluate_beta(frame, m, beta)) for m in robust}
    L = min(b_vals.values()) if b_vals else None
    U = max(b_vals.values()) if b_vals else None

    summary: dict[str, Any] = {
        "k": k,
        "n_folds": len(folds),
        "n_units": len(units),
        "folds": folds,
        "per_fold_select": per_fold_select,
        "per_fold_compliant": per_fold_compliant,
        "selected_all_folds": selected_all,
        "compliant_all_folds": compliant_all,
        "pooled_robust": robust,
        "L": L,
        "U": U,
        "empty": len(robust) == 0,
        "seed": seed,
        "split_seed": split_seed,
    }
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "pooled_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n"
    )
    return summary


def app_menu() -> list[str]:
    return list(MENU_MEASURES)


# ---------------------------------------------------------------------------
# Stage 5 — summary writer (allow-listed proof artifact)
# ---------------------------------------------------------------------------


def stage5_report(
    data_dir: Path | str,
    seed: int,
    split_seed: int,
    k: int = 5,
    n_boot: int | None = None,
    n_draws: int = 500,
    k_grid: tuple[int, ...] = (1, 2, 3, 4),
    alpha: float = 0.10,
    kappa: float = 2.0,
    out_path: Path | str | None = None,
) -> dict[str, Any]:
    """Compose the full application summary for the proof artifact.

    Reporting posture (a) (docs/16 §11 2026-08-10): headline = M*_select
    with [L,U] = min/max beta on select survivors; pooled holdout verdicts
    and baselines are diagnostics; verifier gate summary included.
    """
    from cvprofiles.identify.beta_fn import evaluate_beta
    from cvprofiles.schemas.beta import BetaSpec

    data = Path(data_dir)
    inputs = data / "inputs" if (data / "inputs").exists() else data
    frame = pd.read_csv(inputs / "scores.csv")
    beta_yaml = load_yaml(inputs / "beta.yaml")

    pooled = pooled_stage3(
        data_dir=data,
        out_dir=data / "pool_runs",
        seed=seed,
        split_seed=split_seed,
        k=k,
        n_boot=n_boot,
        alpha=alpha,
        kappa=kappa,
    )

    # Headline: selection across ALL folds (reporting posture a).
    select_all = list(pooled.get("selected_all_folds") or [])
    beta = BetaSpec.model_validate(beta_yaml)
    b_vals = {m: float(evaluate_beta(frame, m, beta)) for m in select_all}
    L = min(b_vals.values()) if b_vals else None
    U = max(b_vals.values()) if b_vals else None

    baselines = stage4_baselines(
        data_dir=data,
        seed=seed,
        split_seed=split_seed,
        n_draws=n_draws,
        k_grid=k_grid,
        n_boot=n_boot,
        alpha=alpha,
        kappa=kappa,
    )

    summary: dict[str, Any] = {
        "schema_version": "1",
        "construct": "patience",
        "package_version": __import__("cvprofiles").__version__,
        "seed": seed,
        "split_seed": split_seed,
        "k": k,
        "n_units": pooled.get("n_units"),
        "headline": {
            "M_star_select": select_all,
            "L": L,
            "U": U,
            "empty": len(select_all) == 0,
            "method": "min_max_beta_on_M_star_select",
            "note": (
                "Reporting posture (a): selection across all pooled folds is "
                "primary; holdout verdicts are power-limited diagnostics."
            ),
        },
        "holdout": {
            "pooled_robust": pooled.get("pooled_robust"),
            "compliant_all_folds": pooled.get("compliant_all_folds"),
            "per_fold_select": pooled.get("per_fold_select"),
            "per_fold_compliant": pooled.get("per_fold_compliant"),
            "folds": pooled.get("folds"),
            "note": (
                "Per-fold holdout n small (power-limited); empty pooled robust "
                "is a test-power limitation, not a construct verdict."
            ),
        },
        "baselines": {
            k_: v for k_, v in (baselines.get("random_baseline") or {}).items()
        },
        "tool_holdout_pass_rate": baselines.get("tool_holdout_pass_rate"),
        "tool_range_width": baselines.get("tool_range_width"),
        "verifier": {
            "tool": "tools/verify_wvs_gps.py",
            "status": "run separately on frozen inputs + run dir",
        },
    }
    if out_path is not None:
        p = Path(out_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="WVS/GPS patience application (cvprofiles)")
    p.add_argument("--gps", type=Path, help="GPS country .dta path")
    p.add_argument("--wvs", type=Path, help="WVS Wave 7 .dta path")
    p.add_argument("--wdi", type=Path, default=None, help="cached WDI csv (else fetch)")
    p.add_argument("--out", type=Path, default=Path("evals/wvs_gps_preferences/data"))
    p.add_argument("--seed", type=int, default=20260810)
    p.add_argument("--prompt-source", default=None, help="'stub' or llama.cpp record")
    p.add_argument("--stage", default="1", choices=["1", "2", "3", "4", "5"])
    p.add_argument("--model-a", type=Path, default=None, help="arm A GGUF (Llama-3.1-8B)")
    p.add_argument("--model-b", type=Path, default=None, help="arm B GGUF (Phi-4-mini 3.8B)")
    p.add_argument("--model-a-repo", default="bartowski/Meta-Llama-3.1-8B-Instruct-GGUF",
                   help="arm A HF repo")
    p.add_argument("--model-b-repo", default="MaziyarPanahi/Phi-4-mini-instruct-GGUF",
                   help="arm B HF repo")
    p.add_argument("--model-a-quant", default="Q8_0", help="arm A quant label")
    p.add_argument("--model-b-quant", default="Q8_0", help="arm B quant label")
    p.add_argument("--subset", type=int, default=None, help="limit countries (smoke only)")
    p.add_argument("--split-seed", type=int, default=17, help="holdout split seed")
    p.add_argument("--k-fold", type=int, default=0, help="pooled K-fold (K>=2; 0 = single split)")
    p.add_argument("--n-boot", type=int, default=100, help="bootstrap replicates (0=off)")
    p.add_argument("--n-draws", type=int, default=500, help="random baseline draws")
    p.add_argument("--k-grid", type=int, nargs="+", default=[1, 2, 3, 4], help="baseline k values")
    p.add_argument("--alpha", type=float, default=0.10, help="coverage tail probability")
    p.add_argument("--kappa", type=float, default=2.0, help="boundary attribution rule")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.stage == "1":
        if args.gps is None or args.wvs is None:
            print("stage 1 requires --gps and --wvs paths", file=sys.stderr)
            return 2
        paths = build_real_stage1(
            gps_path=args.gps,
            wvs_path=args.wvs,
            wdi_path=args.wdi,
            out_dir=args.out,
            seed=args.seed,
            prompt_source=args.prompt_source,
        )
        summary = {"stage": "1", "artifacts": {k: str(v) for k, v in paths.items()}}
    elif args.stage == "2":
        if args.model_a is None or args.model_b is None:
            print("stage 2 requires --model-a and --model-b GGUF paths", file=sys.stderr)
            return 2
        meta_a = {
            "repo": args.model_a_repo,
            "file": args.model_a.name,
            "sha256": _sha256_file(args.model_a),
            "quant": args.model_a_quant,
        }
        meta_b = {
            "repo": args.model_b_repo,
            "file": args.model_b.name,
            "sha256": _sha256_file(args.model_b),
            "quant": args.model_b_quant,
        }
        if args.subset is not None:
            # Smoke path: copy stage-1 inputs into a smoke dir, trim countries
            # there, and write prompt columns on the trimmed copy. The real
            # frozen inputs are never touched by a smoke run.
            smoke_dir = args.out / "smoke_stage2"
            import shutil

            smoke_dir.mkdir(parents=True, exist_ok=True)
            for name in (
                "scores.csv",
                "roles.json",
                "network.yaml",
                "beta.yaml",
                "score_manifest.json",
            ):
                shutil.copy2(args.out / "inputs" / name, smoke_dir / name)
            smoke_scores = pd.read_csv(smoke_dir / "scores.csv")
            keep = smoke_scores["unit_id"].iloc[: args.subset]
            smoke_scores = smoke_scores[smoke_scores["unit_id"].isin(keep)].reset_index(drop=True)
            smoke_scores.to_csv(smoke_dir / "scores.csv", index=False)
            manifest = json.loads((smoke_dir / "score_manifest.json").read_text())
            manifest["n_rows"] = len(smoke_scores)
            (smoke_dir / "score_manifest.json").write_text(
                json.dumps(manifest, indent=2) + "\n"
            )
            prompt_source = run_prompting(
                out_dir=smoke_dir,
                model_a=args.model_a,
                model_a_meta=meta_a,
                model_b=args.model_b,
                model_b_meta=meta_b,
                seed=args.seed,
                subset=None,  # already trimmed; score all rows in the smoke dir
            )
            summary = {
                "stage": "2",
                "mode": "smoke",
                "smoke_dir": str(smoke_dir),
                "scores_hash": prompt_source["scores_hash"],
                "n_rows": prompt_source["n_rows"],
            }
        else:
            manifest = run_prompting(
                out_dir=args.out,
                model_a=args.model_a,
                model_a_meta=meta_a,
                model_b=args.model_b,
                model_b_meta=meta_b,
                seed=args.seed,
                subset=None,
            )
            summary = {
                "stage": "2",
                "scores_hash": manifest["scores_hash"],
                "n_rows": manifest["n_rows"],
            }
    elif args.stage == "3":
        if args.k_fold:
            summary = pooled_stage3(
                data_dir=args.out,
                out_dir=args.out / "pool_runs",
                seed=args.seed,
                split_seed=args.split_seed,
                k=args.k_fold,
                n_boot=args.n_boot if args.n_boot > 0 else None,
                alpha=args.alpha,
                kappa=args.kappa,
            )
            summary["stage"] = "3"
            summary["mode"] = "pooled_kfold"
        else:
            summary = stage3_engine(
                data_dir=args.out,
                out_dir=args.out / "runs",
                seed=args.seed,
                split_seed=args.split_seed,
                n_boot=args.n_boot if args.n_boot > 0 else None,
                alpha=args.alpha,
                kappa=args.kappa,
            )
            summary["stage"] = "3"
    elif args.stage == "4":
        summary = stage4_baselines(
            data_dir=args.out,
            seed=args.seed,
            split_seed=args.split_seed,
            n_draws=args.n_draws,
            k_grid=args.k_grid,
            n_boot=args.n_boot if args.n_boot > 0 else None,
            alpha=args.alpha,
            kappa=args.kappa,
        )
        summary["stage"] = "4"
    elif args.stage == "5":
        summary = stage5_report(
            data_dir=args.out,
            seed=args.seed,
            split_seed=args.split_seed,
            k=args.k_fold if args.k_fold else 5,
            n_boot=args.n_boot if args.n_boot > 0 else None,
            n_draws=args.n_draws,
            k_grid=tuple(args.k_grid),
            alpha=args.alpha,
            kappa=args.kappa,
            out_path=args.out / "wvs_gps_application_summary.json",
        )
        summary["stage"] = "5"
    else:
        raise NotImplementedError(f"stage {args.stage} not implemented yet")
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
