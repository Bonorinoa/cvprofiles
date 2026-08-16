# Fresh LLM extension — verified readout

**Date:** 2026-08-15
**Engine:** cvprofiles 3.0.1 · seed 20260814 · n_boot=1000 · α=0.10
**Scores:** seed 20260815 · Llama-3.1-8B Q8_0 + Phi-4-mini Q8_0 · exact-item battery
**GGUF sha256:** `9da71c45…6283` / `56cccfeb…2000` (verified)

Human columns reused from the 2026-08-14 freeze. LLM columns generated from scratch. Restriction-stage split. Cell profiles country-demeaned.

## Headline

| Profile | n | M* | [L,U] | Coverage | Empty-rep. |
|---|---:|---|---|---|---:|
| Patience cells (main) | 480 | {Q13, Llama, Phi} | [0.245, 0.556] | [0.179, 0.614] | 0.000 |
| Trust cells (main) | 480 | {Phi} | −0.317 | [−0.382, −0.240] | 0.000 |
| Patience country (appendix) | 41 | {GPS, Llama, Phi} | [0.402, 0.565] | [0.157, 0.674] | 0.089 |
| Trust country (appendix) | 35 | {Q57, in, out, composite, Llama} | [0.107, 0.481] | [−0.016, 0.699] | 0.001 |

Cell β = Corr(m, GPS cell mean) after country demeaning.
Country β = standardized OLS of m on log GDP pc | education.

## Cell patience (main)

Q13 slack +0.051 (knife-edge); leftover mono +0.060; β=+0.245.
Llama edu +0.322 / mono +0.358; β=+0.417.
Phi edu +0.440 / mono +0.523; β=+0.556.
Q14 still anti-aligned (edu −0.564, β=−0.326).
Human-only was the Q13 singleton 0.245. Cheap measures that pass the same bar widen the GPS-recovery range to [0.245, 0.556]. p_hat: Llama=Phi=1.00, Q13=0.83.

## Cell trust (main)

Human menu still empty under the education bar (Q57 −0.177, in −0.268, out −0.275, inst −0.627, composite −0.474).
Llama fails education (−0.077).
Phi passes (+0.149 / leftover +0.133) and is the singleton.
Phi β vs GPS trust = **−0.317**. Coverage entirely negative.
The only speaker is a cheap measure that is education-aligned and GPS-anti-aligned. Human facets still co-move with GPS trust (0.05–0.32) without clearing the bar.

## Country patience (appendix)

GPS, Llama, Phi survive. WVS still fail education.
β: GPS 0.402, Llama 0.447, Phi 0.565.
Llama edu slack +0.027 is boundary (margin < 2 SE).
Empty-rep falls from 0.297 (human-only singleton) to 0.089.

## Country trust (appendix)

Llama survives rule of law (+0.475) and gini (+0.197); leftover education +0.221; β=0.481.
Phi fails gini (−0.158) even though rule of law +0.361 and leftover education +0.051.
GPS trust still fails rule of law. Human survivors unchanged except the range upper end moves 0.391 → 0.481.
Coverage still crosses zero.

## Allowed readings

Disagreement is the result. Two models are not two methods. Llama and Phi do not jointly validate patience or trust.
Cheap columns that pass the frozen human network move [L,U]. That is the title’s empirical content.
Do not recycle [0.328, 0.402]. Do not call Phi a valid trust measure because it cleared education.
