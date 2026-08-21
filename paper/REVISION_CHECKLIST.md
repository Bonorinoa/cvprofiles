# Paper revision — 2026-08-15 LLM join

**Status:** executing under architecture lock (cells+LLM main; country+LLM appendix; delete 2026-08-10 pilot).
**Numbers:** only from `evals/wvs_gps_two_resolution/runs/*_llm/` and `LLM_RESULTS.md`.

## Tasks

| # | Task | Evidence |
|---|---|---|
| 1 | Status / significance / abstract | LLM_RESULTS headline table |
| 2 | §5: cells first with LLM; country pointed to appendix | same |
| 3 | Main Table 1 = demeaned cells + LLM | patience [0.245, 0.556]; trust −0.317 |
| 4 | Replace Appendix E old pilot with country+LLM | [0.402, 0.565]; [0.107, 0.481] |
| 5 | Discussion: LLM is no longer “what remains” | — |
| 6 | empty-R restated on the *new* seven-measure country menu | min composite −0.2187, max Phi 0.5649 → [−0.219, 0.565] |
| 7 | Compile twice in /tmp; hash; grep old 0.328 out of body |

## Number gate (must remain somewhere: special cases / history)

`0.245`, `0.402`, `-0.219`, `0.825`, `0.284`, `41`, `35`, `480`, `3.0.1`

## Forbidden

Promote country ranges to abstract. Recycle `[0.328, 0.402]`. Call Phi a valid trust measure. Move θ.
