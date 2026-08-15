# LLM-extension design — cells in the main text, country in the appendix

**Status:** FROZEN 2026-08-15. Exact-instrument battery below. Fresh scores only.
**Parent design:** `DESIGN.md` (2026-08-14). Human `R`, θ, and β do not change.
**Engine:** cvprofiles 3.0.1.

## Architecture lock (Augusto, 2026-08-15)

Delete the old pilot. Country-level human + fresh LLM is a complete underpowered appendix. Cell-level (n=480) is the powered main application. No new construct this week.

**Same-day amendment:** cell-level AI is in scope. Individual-level scoring is a later estimand, not a substitute for cells.

1. The 2026-08-10 units-split freeze is **deleted**. Those columns are not reused.
2. All LLM numbers are generated from scratch.
3. Main-text Table 1 is the demeaned cell table **with** the new LLM columns. Country profiles, including the same LLM battery, live in the appendix.
4. Appendix F (synthesis) stays methods, not a second application.

## Why cells now, individuals later

A cell score is the mean of a sex×age group. Adding LLM columns at that resolution asks whether a cheap measure recovers *who, inside a country, is more patient or trusting* after country demeaning. That is the same estimand as the human cell application, so the cheap measure can speak in the main text. Cost is 480 existing cells × 4 items × 2 models — one forward pass per persona-item, not a new survey.

Individual-level scoring is a different function. It keeps residual variance, education, and respondent-level tails — the place where language models systematically collapse. That test needs its own design (persona grid with education, or one prompt per WVS/GPS respondent) and is how we would later do gradient alignment. It is not how we put cheap measures on the powered surface we already have. Cells first; individuals afterwards.

Education never enters the persona. It is the admission bar. Conditioning on it would build the measure from the restriction.

## What does not change (human side)

Cell and country `R`, θ, β, seed `20260814`, `n_boot=1000`, λ-grid. Human score columns reused. Only LLM columns are new.

## Menus

Two AI columns per construct (one model each). Not item × model.

**Patience country appendix (7).**
`m_gps_patience`, `m_wvs_q13`, `m_wvs_q14`, `m_composite`, `m_llm_patience_llama`, `m_llm_patience_phi`, `m_noise`.

**Trust country appendix (9).**
`m_gps_trust`, `m_trust_general`, `m_trust_in_group`, `m_trust_out_group`, `m_trust_institution`, `m_trust_composite`, `m_llm_trust_llama`, `m_llm_trust_phi`, `m_noise`.

**Patience cells, main (6).** GPS patience cell mean is β, not a menu member.
`m_wvs_q13`, `m_wvs_q14`, `m_composite`, `m_llm_patience_llama`, `m_llm_patience_phi`, `m_noise`.

**Trust cells, main (8).**
`m_trust_general`, `m_trust_in_group`, `m_trust_out_group`, `m_trust_institution`, `m_trust_composite`, `m_llm_trust_llama`, `m_llm_trust_phi`, `m_noise`.

After joining, every numeric column that enters cell `R` or `β` — including the LLM columns — is country-demeaned before SCORE.

Llama and Phi see identical prompt bytes. Human GPS/WVS remain the different-method auxiliaries. Llama–Phi agreement is correlated error, not validation.

## Elicitation (same items, both models)

Silicon sampling on published instruments. Temperature 0. Seed 20260815.

**Country wrapper**

```
You are a typical adult living in {country}.
Answer the following survey question as this person would.
Do not mention being an AI.

{item}
```

**Cell wrapper**

```
You are a {sex} aged {age_band} living in {country}.
Answer the following survey question as this person would.
Do not mention being an AI.

{item}
```

`{country}` = English short name. `{sex}` = `woman`/`man` from cell `F`/`M`. `{age_band}` = the cell label (`18-24` … `65+`), not a midpoint. Only the 480 existing cells are scored. Country stays in the prompt at both resolutions so `m` is the same function on a finer partition.

### Patience items → `m_llm_patience_*`

Mean of expected 0–10 on p_qual and P(delayed) on p_bin.

**p_qual** (GPS qualitative)

```
How willing are you to give up something that is beneficial for you today
in order to benefit more from that in the future?
Please answer with a single integer from 0 to 10.
0 means “completely unwilling to do so.”
10 means “very willing to do so.”
Answer:
```

**p_bin** (GPS-style first staircase node, common units)

```
Suppose you can receive a payment today or a payment in 12 months.
Assume there is no inflation.
Would you rather receive 100 units today or 154 units in 12 months?
A. 100 units today
B. 154 units in 12 months
Answer:
```

### Trust items → `m_llm_trust_*`

Mean of expected 0–10 on t_qual and P(trusted) on t_q57.

**t_qual** (GPS trust)

```
How well does the following statement describe you as a person?
“I assume that people have only the best intentions.”
Please answer with a single integer from 0 to 10.
0 means “does not describe me at all.”
10 means “describes me perfectly.”
Answer:
```

**t_q57** (WVS Wave 7 Q57 stem)

```
Generally speaking, would you say that most people can be trusted or that
you need to be very careful in dealing with people?
A. Need to be very careful
B. Most people can be trusted
Answer:
```

Q57 option order is swapped so the trusting answer is B. Declared; not a stem paraphrase. No wallet/institution/in-group items. No Q13/Q14 in the LLM battery.

## Runtime

| Field | Lock |
|---|---|
| Arm A | `bartowski/Meta-Llama-3.1-8B-Instruct-GGUF` / `Meta-Llama-3.1-8B-Instruct-Q8_0.gguf` / sha256 `9da71c45c90a821809821244d4971e5e5dfad7eb091f0b8ff0546392393b6283` |
| Arm B | `MaziyarPanahi/Phi-4-mini-instruct-GGUF` / `Phi-4-mini-instruct.Q8_0.gguf` / sha256 `56cccfeba1168a4fdd07197d8b5cdfb765eea720bdb4bad59211449687b82000` |
| Engine | llama.cpp via `llama-cpp-python`, temperature 0, seed 20260815, n_ctx 4096 |
| Units | country 41/35; cells 480 existing `iso3\|sex\|age_band` |
| Output | `data/country/*_llm_extension.csv`; `data/cells{,_demeaned}/*_llm_extension.csv`; `runs/{patience,trust}_{country,cells_demeaned}_llm/` |

## Claim boundaries

Allowed: cell (main) and country (appendix) `M*_S`, `[L,U]`, coverage, empty-replicate rate; cheap column survived/failed the same human network.

Forbidden: promoting country ranges into the abstract; recycling 2026-08-10 numbers; moving θ; anti-leakage language; education in the persona; treating cell means as individual distributions; new constructs; calling Phi a valid trust measure; treating Llama and Phi as two methods.

**2026-08-15 lock (parent DESIGN.md):** the trust-cell education bar stays. Phi’s \(\beta=-0.317\) is the result, not a reason to edit \(R\).
