"""Score exact-instrument LLM batteries for the two-resolution extension.

Country and cell units. Llama and Phi see identical prompt bytes.
Not imported from src/. Resume-safe JSONL per (model, resolution).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
MODELS = ROOT.parents[1] / "models"
SEED = 20260815

ISO_NAME = {
    "ARG": "Argentina",
    "AUS": "Australia",
    "BGD": "Bangladesh",
    "BOL": "Bolivia",
    "BRA": "Brazil",
    "CAN": "Canada",
    "CHL": "Chile",
    "CHN": "China",
    "COL": "Colombia",
    "CZE": "Czechia",
    "DEU": "Germany",
    "EGY": "Egypt",
    "GBR": "the United Kingdom",
    "GRC": "Greece",
    "GTM": "Guatemala",
    "IDN": "Indonesia",
    "IND": "India",
    "IRN": "Iran",
    "IRQ": "Iraq",
    "JOR": "Jordan",
    "JPN": "Japan",
    "KAZ": "Kazakhstan",
    "KEN": "Kenya",
    "KOR": "South Korea",
    "MAR": "Morocco",
    "MEX": "Mexico",
    "NGA": "Nigeria",
    "NIC": "Nicaragua",
    "NLD": "the Netherlands",
    "PAK": "Pakistan",
    "PER": "Peru",
    "PHL": "the Philippines",
    "ROU": "Romania",
    "RUS": "Russia",
    "SRB": "Serbia",
    "THA": "Thailand",
    "TUR": "Turkey",
    "UKR": "Ukraine",
    "USA": "the United States",
    "VEN": "Venezuela",
    "VNM": "Vietnam",
    "ZWE": "Zimbabwe",
}

ARMS = {
    "llama": {
        "path": MODELS / "llama-3.1-8b-instruct-q8" / "Meta-Llama-3.1-8B-Instruct-Q8_0.gguf",
        "sha256": "9da71c45c90a821809821244d4971e5e5dfad7eb091f0b8ff0546392393b6283",
        "col_patience": "m_llm_patience_llama",
        "col_trust": "m_llm_trust_llama",
    },
    "phi": {
        "path": MODELS / "phi-4-mini-instruct-q8" / "Phi-4-mini-instruct.Q8_0.gguf",
        "sha256": "56cccfeba1168a4fdd07197d8b5cdfb765eea720bdb4bad59211449687b82000",
        "col_patience": "m_llm_patience_phi",
        "col_trust": "m_llm_trust_phi",
    },
}

ITEMS = {
    "p_qual": {
        "kind": "scale10",
        "construct": "patience",
        "text": (
            "How willing are you to give up something that is beneficial for you today\n"
            "in order to benefit more from that in the future?\n"
            "Please answer with a single integer from 0 to 10.\n"
            "0 means “completely unwilling to do so.”\n"
            "10 means “very willing to do so.”\n"
            "Answer:"
        ),
    },
    "p_bin": {
        "kind": "binary",
        "construct": "patience",
        "text": (
            "Suppose you can receive a payment today or a payment in 12 months.\n"
            "Assume there is no inflation.\n"
            "Would you rather receive 100 units today or 154 units in 12 months?\n"
            "A. 100 units today\n"
            "B. 154 units in 12 months\n"
            "Answer:"
        ),
    },
    "t_qual": {
        "kind": "scale10",
        "construct": "trust",
        "text": (
            "How well does the following statement describe you as a person?\n"
            "“I assume that people have only the best intentions.”\n"
            "Please answer with a single integer from 0 to 10.\n"
            "0 means “does not describe me at all.”\n"
            "10 means “describes me perfectly.”\n"
            "Answer:"
        ),
    },
    "t_q57": {
        "kind": "binary",
        "construct": "trust",
        "text": (
            "Generally speaking, would you say that most people can be trusted or that\n"
            "you need to be very careful in dealing with people?\n"
            "A. Need to be very careful\n"
            "B. Most people can be trusted\n"
            "Answer:"
        ),
    },
}

COUNTRY_WRAP = (
    "You are a typical adult living in {country}.\n"
    "Answer the following survey question as this person would.\n"
    "Do not mention being an AI.\n\n"
    "{item}"
)
CELL_WRAP = (
    "You are a {sex} aged {age_band} living in {country}.\n"
    "Answer the following survey question as this person would.\n"
    "Do not mention being an AI.\n\n"
    "{item}"
)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def verify_gguf(arm: str) -> Path:
    spec = ARMS[arm]
    path = spec["path"]
    if not path.exists():
        raise FileNotFoundError(f"missing GGUF for {arm}: {path}")
    digest = sha256_file(path)
    if digest != spec["sha256"]:
        raise RuntimeError(f"{arm} sha256 mismatch: {digest}")
    return path


def token_ids(llm: Any, text: str) -> list[int]:
    toks = llm.tokenize(text.encode("utf-8"))
    return [int(toks[-1])] if toks else []


def option_map(llm: Any, labels: list[str]) -> dict[str, list[int]]:
    out: dict[str, list[int]] = {}
    for lab in labels:
        ids: list[int] = []
        for variant in (lab, " " + lab):
            ids.extend(token_ids(llm, variant))
        out[lab] = sorted(set(ids))
    return out


def softmax_named(logits: np.ndarray, named_ids: dict[str, list[int]]) -> dict[str, float]:
    raw: dict[str, float] = {}
    for lab, ids in named_ids.items():
        valid = [i for i in ids if 0 <= i < len(logits)]
        if not valid:
            raw[lab] = 0.0
            continue
        z = np.logaddexp.reduce(logits[valid]) if len(valid) > 1 else logits[valid[0]]
        raw[lab] = float(np.exp(z))
    total = sum(raw.values())
    if total <= 0:
        raise ValueError("option probabilities did not normalize")
    return {k: v / total for k, v in raw.items()}


def next_logits(llm: Any, prompt: str) -> np.ndarray:
    tokens = llm.tokenize(prompt.encode("utf-8"))
    llm.reset()
    llm.eval(tokens)
    return np.asarray(llm.eval_logits, dtype=float)[-1]


def score_item(llm: Any, prompt: str, kind: str, cache: dict[str, Any]) -> float:
    logits = next_logits(llm, prompt)
    if kind == "binary":
        key = "bin"
        if key not in cache:
            cache[key] = option_map(llm, ["A", "B"])
        probs = softmax_named(logits, cache[key])
        return float(probs["B"])
    if kind == "scale10":
        key = "scale"
        if key not in cache:
            labels = [str(k) for k in range(11)]
            cache[key] = option_map(llm, labels)
        probs = softmax_named(logits, cache[key])
        return float(sum(int(k) * p for k, p in probs.items()))
    raise ValueError(kind)


def load_llm(path: Path) -> Any:
    from llama_cpp import Llama

    return Llama(
        model_path=str(path),
        n_ctx=4096,
        n_gpu_layers=35,
        seed=SEED,
        verbose=False,
        logits_all=True,
    )


def _require_names(isos: list[str], label: str) -> None:
    missing = sorted({iso for iso in isos if iso not in ISO_NAME})
    if missing:
        raise KeyError(f"no English name for {label}: {missing}")


def country_jobs(construct: str) -> list[dict[str, str]]:
    frame = pd.read_csv(ROOT / "data/country" / f"{construct}.csv")
    isos = list(frame["unit_id"])
    _require_names(isos, "country")
    return [
        {
            "unit_id": iso,
            "resolution": "country",
            "country": ISO_NAME[iso],
            "construct": construct,
        }
        for iso in isos
    ]


def cell_jobs(construct: str) -> list[dict[str, str]]:
    frame = pd.read_csv(ROOT / "data/cells" / f"{construct}.csv")
    parsed = [uid.split("|") for uid in frame["unit_id"]]
    _require_names([p[0] for p in parsed], "cells")
    jobs = []
    for uid, (iso, sex_code, band) in zip(frame["unit_id"], parsed):
        jobs.append(
            {
                "unit_id": uid,
                "resolution": "cell",
                "country": ISO_NAME[iso],
                "sex": "woman" if sex_code == "F" else "man",
                "age_band": band,
                "construct": construct,
            }
        )
    return jobs


def render(job: dict[str, str], item_text: str) -> str:
    if job["resolution"] == "country":
        return COUNTRY_WRAP.format(country=job["country"], item=item_text)
    return CELL_WRAP.format(
        sex=job["sex"],
        age_band=job["age_band"],
        country=job["country"],
        item=item_text,
    )


def load_done(path: Path) -> set[tuple[str, str]]:
    done: set[tuple[str, str]] = set()
    if not path.exists():
        return done
    with path.open() as f:
        for line in f:
            rec = json.loads(line)
            done.add((rec["unit_id"], rec["item_id"]))
    return done


def score_arm(arm: str, construct: str, resolution: str) -> Path:
    path = verify_gguf(arm)
    out_dir = ROOT / "data" / "llm_raw"
    out_dir.mkdir(parents=True, exist_ok=True)
    raw_path = out_dir / f"{construct}_{resolution}_{arm}.jsonl"
    done = load_done(raw_path)
    jobs = country_jobs(construct) if resolution == "country" else cell_jobs(construct)
    item_ids = [k for k, v in ITEMS.items() if v["construct"] == construct]
    remaining = [
        (job, iid)
        for job in jobs
        for iid in item_ids
        if (job["unit_id"], iid) not in done
    ]
    print(f"{arm} {construct} {resolution}: {len(done)} done, {len(remaining)} left", file=sys.stderr)
    if not remaining:
        return raw_path
    llm = load_llm(path)
    cache: dict[str, Any] = {}
    with raw_path.open("a") as f:
        for i, (job, iid) in enumerate(remaining, 1):
            spec = ITEMS[iid]
            prompt = render(job, spec["text"])
            score = score_item(llm, prompt, spec["kind"], cache)
            rec = {
                "unit_id": job["unit_id"],
                "item_id": iid,
                "arm": arm,
                "construct": construct,
                "resolution": resolution,
                "score": score,
                "seed": SEED,
            }
            f.write(json.dumps(rec) + "\n")
            f.flush()
            if i % 25 == 0 or i == len(remaining):
                print(f"  {i}/{len(remaining)} {job['unit_id']} {iid} {score:.4f}", file=sys.stderr)
    return raw_path


def aggregate(construct: str, resolution: str) -> pd.DataFrame:
    rows = []
    for arm in ARMS:
        raw = ROOT / "data" / "llm_raw" / f"{construct}_{resolution}_{arm}.jsonl"
        if not raw.exists():
            raise FileNotFoundError(raw)
        recs = [json.loads(line) for line in raw.read_text().splitlines() if line.strip()]
        df = pd.DataFrame(recs)
        item_ids = [k for k, v in ITEMS.items() if v["construct"] == construct]
        wide = df.pivot_table(index="unit_id", columns="item_id", values="score", aggfunc="mean")
        missing = [c for c in item_ids if c not in wide.columns]
        if missing:
            raise RuntimeError(f"{arm} missing items {missing}")
        col = ARMS[arm][f"col_{construct}"]
        # scale10 is 0-10, binary is 0-1: put both on the unit interval before averaging
        parts = []
        for iid in item_ids:
            series = wide[iid]
            if ITEMS[iid]["kind"] == "scale10":
                series = series / 10.0
            parts.append(series)
        wide[col] = sum(parts) / len(parts)
        rows.append(wide[[col]])
    out = rows[0].join(rows[1], how="outer")
    if out.isna().any().any():
        raise RuntimeError(f"unbalanced aggregate for {construct} {resolution}")
    return out.reset_index()


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--arm", choices=["llama", "phi", "both"], default="both")
    p.add_argument("--construct", choices=["patience", "trust", "both"], default="both")
    p.add_argument("--resolution", choices=["country", "cell", "both"], default="both")
    p.add_argument("--aggregate-only", action="store_true")
    args = p.parse_args()
    arms = list(ARMS) if args.arm == "both" else [args.arm]
    constructs = ["patience", "trust"] if args.construct == "both" else [args.construct]
    resolutions = ["country", "cell"] if args.resolution == "both" else [args.resolution]
    if not args.aggregate_only:
        for arm in arms:
            verify_gguf(arm)
            for construct in constructs:
                for resolution in resolutions:
                    score_arm(arm, construct, resolution)
    print(json.dumps({"ok": True, "arms": arms, "constructs": constructs, "resolutions": resolutions}))


if __name__ == "__main__":
    main()
