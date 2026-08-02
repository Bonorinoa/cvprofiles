"""Build a real-world, multi-measure spamminess dataset.

Offline-deterministic. Uses scikit-learn's bundled 20newsgroups training
subset across 4 categories as the text source. Constructs a multi-measure
"spamminess" menu plus a clean auxiliary (`v_aux`) and a noisy outcome `y`.

This is NOT the main path. It is an intermediate audit to gauge the
package spine on a real-world matrix. NO paper claims here.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from sklearn.datasets import fetch_20newsgroups

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"


def count_pattern(text: str, pat: str, flags: int = 0) -> int:
    return len(re.findall(pat, text, flags))


def cap_word_share(text: str) -> float:
    words = re.findall(r"[A-Za-z]+", text)
    if not words:
        return 0.0
    return sum(1 for w in words if w.isupper() and len(w) > 2) / len(words)


def z(x: np.ndarray) -> np.ndarray:
    s = x.std(ddof=0)
    if s == 0:
        return np.zeros_like(x)
    return (x - x.mean()) / s


def build() -> None:
    print("[1/4] Fetching 20newsgroups training subset...")
    ds = fetch_20newsgroups(
        subset="train",
        categories=["sci.med", "alt.atheism", "comp.graphics", "misc.forsale"],
        shuffle=True,
        random_state=42,
        remove=("headers", "footers", "quotes"),
    )
    texts = ds.data
    y_topic = np.array(ds.target)
    print(f"      n={len(texts)}, topics={dict(zip(range(4), ds.target_names, strict=True))}")

    print("[2/4] Building feature families (multi-measure menu)...")
    RANDOM = np.random.default_rng(20260801)

    n_chars = np.array([len(t) for t in texts], dtype=float)
    n_words = np.array([len(re.findall(r"[A-Za-z]+", t)) for t in texts], dtype=float)
    mask = (n_chars > 0) & (n_words > 0)
    texts = [t for t, m in zip(texts, mask, strict=True) if m]
    y_topic = y_topic[mask]
    n_chars = n_chars[mask]
    n_words = n_words[mask]

    n_bang = np.array([count_pattern(t, r"!") for t in texts], dtype=float)
    n_money = np.array([count_pattern(t, r"\$") for t in texts], dtype=float)
    n_url = np.array([count_pattern(t, r"http[s]?://") for t in texts], dtype=float)
    n_free = np.array(
        [
            count_pattern(
                t,
                r"\b(free|cheap|buy|discount|win|cash|money|offer|sale)\b",
                re.IGNORECASE,
            )
            for t in texts
        ],
        dtype=float,
    )
    cap_share = np.array([cap_word_share(t) for t in texts], dtype=float)

    # Five hand-engineered "valid" candidates + two designed invalid.
    m_lexicon = z(0.55 * n_bang + 0.45 * n_free)
    m_money_url = z(0.50 * n_money + 0.50 * n_url)
    m_caps_buy = z(0.60 * cap_share + 0.40 * n_free)
    m_llm_full = z(0.30 * n_bang + 0.30 * n_url + 0.20 * n_money + 0.20 * n_free)
    m_short_cap = z(0.55 * cap_share + 0.45 * z(np.log1p(n_chars)))
    m_noise = RANDOM.standard_normal(len(texts)) * 0.5
    m_topic_leak = z(
        1.0 * (y_topic == 0).astype(float) - 0.3 * (y_topic == 2).astype(float)
    )

    # Clean auxiliary: length + signal-flag density (NOT the outcome).
    v_aux_raw = n_chars + 30 * n_bang + 40 * n_free
    m_aux = z(v_aux_raw)

    # Outcome: noisy latent that the valid measures should track.
    m_label = 0.55 * z(n_bang) + 0.30 * z(n_money) + 0.15 * z(n_url)
    outcome = m_label + 0.10 * RANDOM.standard_normal(len(texts))

    print("[3/4] Assembling unit×measure matrix...")
    df = pd.DataFrame(
        {
            "unit_id": [f"u{i:05d}" for i in range(len(texts))],
            "m_lexicon": m_lexicon,
            "m_money_url": m_money_url,
            "m_caps_buy": m_caps_buy,
            "m_llm_full": m_llm_full,
            "m_short_cap": m_short_cap,
            "m_noise": m_noise,
            "m_topic_leak": m_topic_leak,
            "v_aux": m_aux,
            "y": outcome,
        }
    )
    DATA.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA / "scores.csv", index=False)

    roles = {
        "unit_id": "unit_id",
        "measures": [
            "m_lexicon",
            "m_money_url",
            "m_caps_buy",
            "m_llm_full",
            "m_short_cap",
            "m_noise",
            "m_topic_leak",
        ],
        "aux": ["v_aux"],
        "outcome": "y",
        # Keep empty: SCORE requires declared diagnostics to exist on the score frame.
        "diagnostic": [],
    }
    with (DATA / "roles.json").open("w") as f:
        json.dump(roles, f, indent=2)

    network_oracle = {
        "schema_version": "1",
        "name": "spam_oracle_incidental",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_corr_min_aux",
                "type": "corr_min",
                "theta": 0.15,
                "params": {"variable": "v_aux"},
            },
            {
                "id": "r_corr_sign_aux",
                "type": "corr_sign",
                "theta": 0.05,
                "params": {"variable": "v_aux", "sign": 1},
            },
        ],
    }
    network_harsh = {
        "schema_version": "1",
        "name": "spam_harsh_empty",
        "delta": 0.0,
        "restrictions": [
            {
                "id": "r_corr_min_aux",
                "type": "corr_min",
                "theta": 0.99,
                "params": {"variable": "v_aux"},
            },
        ],
    }
    beta = {"schema_version": "1", "type": "corr_y", "outcome": "y", "params": {}}
    with (DATA / "network_oracle.yaml").open("w") as f:
        yaml.safe_dump(network_oracle, f, sort_keys=False)
    with (DATA / "network_harsh.yaml").open("w") as f:
        yaml.safe_dump(network_harsh, f, sort_keys=False)
    with (DATA / "beta.yaml").open("w") as f:
        yaml.safe_dump(beta, f, sort_keys=False)

    print("[4/4] Sanity check (oracle R at delta=0):")
    for m in roles["measures"]:
        c_aux = float(np.corrcoef(df[m], df["v_aux"])[0, 1])
        c_y = float(np.corrcoef(df[m], df["y"])[0, 1])
        s_min = c_aux - 0.15
        s_sign = c_aux - 0.05
        adm = (s_min >= 0) and (s_sign >= 0)
        print(f"  {m:14s}: corr_aux={c_aux:+.3f} corr_y={c_y:+.3f}  adm={adm}")
    print(f"  v_aux_std={float(df['v_aux'].std()):.4f}  y_std={float(df['y'].std()):.4f}")


if __name__ == "__main__":
    build()
