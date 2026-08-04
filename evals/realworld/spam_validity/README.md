# Real-world intermediate audit: spamminess (20newsgroups features)

**Status:** intermediate evaluation · **NOT** main path · **NOT** paper H5  
**Branch:** `feat/realworld-spam` (merged to `main` @ `3be6367`; deleted)  
**Engine:** installed `cvprofiles` package (`SCORE → RESTRICT → IDENTIFY → REPORT`)

## What this is

A domain-agnostic stress of the thin spine on a **public, free, offline-cached** text corpus (`sklearn.datasets.fetch_20newsgroups`).  
Construct (incidental): **spamminess / promotional pressure** as a latent, operationalized by several hand-built feature-family scores.

This is **not** a claim that 20newsgroups *is* spam, nor a contribution to spam detection.  
It answers: *does the package produce a transparent \(M^*\) and \([L,U]\) on a non-toy matrix with designed valid/invalid columns?*

## Menu (design roles — outside the engine)

| Measure | Design role | Construction sketch |
|---|---|---|
| `m_lexicon` | valid | bangs + promo lexicon density |
| `m_money_url` | valid | `$` + URL density |
| `m_caps_buy` | valid | CAPS share + promo words |
| `m_llm_full` | valid | weighted mix of signal flags |
| `m_short_cap` | valid | CAPS + log length mix |
| `m_noise` | **invalid_noise** | Gaussian noise |
| `m_topic_leak` | **invalid_confounded** | newsgroup topic identity leak |

- **Aux** `v_aux`: log-ish length + signal-flag density (clean structural correlate; not the outcome).  
- **Outcome** `y`: noisy latent built from bang/`$`/URL components.  
- **β:** `corr_y`.  
- **Oracle \(R\):** `corr_min(v_aux, 0.15)` + `corr_sign(v_aux, +, 0.05)`.  
- **Harsh \(R\):** `corr_min(v_aux, 0.99)` → expected empty \(M^*\).

## Reproduce

```bash
# from repo root, package installed (uv sync)
uv run python evals/realworld/spam_validity/build_dataset.py
uv run python evals/realworld/spam_validity/verify_audit.py   # exit 0 required

# or manual CLI
uv run cvprofiles run \
  --scores evals/realworld/spam_validity/data/scores.csv \
  --roles  evals/realworld/spam_validity/data/roles.json \
  --network evals/realworld/spam_validity/data/network_oracle.yaml \
  --beta   evals/realworld/spam_validity/data/beta.yaml \
  --out    evals/realworld/spam_validity/runs_oracle \
  --seed 0
```

## Expected gates (verify_audit.py)

| Gate | Expectation |
|---|---|
| FA | `m_noise`, `m_topic_leak` ∉ \(M^*\) |
| Oracle nonempty | designed valids ∈ \(M^*\) |
| Range | \([L,U]=\min/\max B^*\) on survivors only |
| Harsh empty | \(M^*=\emptyset\), exit 0, HTML empty callout |
| H4 cold | freeze core identical across two independent runs |

## Authority note

Network here is **agent-authored for intermediate eval only** (user granted this for non-main-path stress).  
It does **not** set H5 / paper empirical \(R\). Do not copy into main-path claims without Augusto’s authorship.
