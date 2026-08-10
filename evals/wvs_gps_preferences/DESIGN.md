# WVS/GPS preferences — network design decisions (live working doc)

**Lane:** intermediate demo + position-paper complement (docs/12 2026-08-09, docs/16 §10)
**Status:** design decisions pinned by Augusto; θs and full restriction list still open (see bottom)

This document records the empirical network choices as they are pinned, before
they become frozen inputs (`data/network.yaml`, `data/beta.yaml`, `data/anchors.yaml`).
It is **Augusto-authored**; the agent scaffolds, validates, and records only.

---

## Pinned decisions (2026-08-09, Augusto)

### D1 — Construct definition (patience)

> **Patience** is the disposition to value future relative to present outcomes,
> observable in choices involving delayed rewards (intertemporal tradeoffs).
> For this study it is treated as a construct that (a) is measurable via stated
> intertemporal preference, (b) should express in long-horizon behavior
> (education, saving), and (c) is conceptually distinct from risk tolerance and
> the other preference dimensions.

Anchored in Falk et al. (2018) time preference (Becker–Mulligan 1997; β-δ
discounting lineage). The risk-taking profile will get its own sibling paragraph.

### D2 — Stability assumption

Country-level patience is the **primary object** (country means aggregate away
individual measurement noise). Individual-level profile is a **secondary,
attenuated robustness check** — β at the individual level is expected to be
attenuated by measurement error; do not interpret individual-level nulls as
evidence against the construct.

### D3 — Discriminant bar (risk-taking orthogonality)

Patience must be **non-reducible to risk tolerance**: `corr_zero` on
`risktaking` with a moderate θ. **θ re-anchored to 0.35 on 2026-08-10**
(docs/12; literature memo `patience_risk_theta_memo.md`): Falk et al. (2018)
Table IV reports ρ=0.230 country-level (n=76, main text); Hanushek et al.
(2022, *EJ*) replicate ρ=0.358 (n=49); Netspar preprint 0.30 excl. Africa.
θ=0.30 sat **inside** the published population range and rejected GPS
patience on a 0.21-SE train-frame knife-edge (slack −0.035 at n=33); 0.35
admits all three project estimates (0.230 / 0.253 / 0.335) with margin while
remaining a binding discriminant (rejects r ≥ 0.6). The θ=0.30 empty-M*
finding is recorded as the motivating diagnostic in docs/12, not discarded.
No discriminant bars on the other four GPS dimensions (altruism, trust,
pos/neg reciprocity) unless theory demands them.

- Country-level profile: feasible directly (GPS country frame has `risktaking`).
- Individual-level (WVS-only) frame: **no `risktaking` column** — the
  discriminant bar applies to the country-level profile only, unless a WVS risk
  proxy is added to the menu. Open item.

### D4 — Menu posture: Peer (P2)

No measure is sacred. GPS `patience` is **one candidate among peers**, facing the
same external bars as the WVS proxies (education, life satisfaction, discriminant
vs risk). The recovery of GPS patience as admissible is itself a result — not a
criterion to bar against (no `corr_min(m, patience_gps)` circular bar).

---

## Implications for the patience network (draft, not yet authored)

| Implication (plain language) | Restriction | Menu/aux | Level |
|---|---|---|---|
| Valid patience co-moves with education | `mean_order` on education or `monotone_rank` on Q275 | Q275/R | both |
| Valid patience co-moves with life satisfaction | `corr_min` on Q49 | Q49 | both |
| Patience is NOT risk tolerance | `corr_zero` on risktaking, θ≈0.3 | GPS `risktaking` | country only |
| Survives country holdout | `stage: holdout` bars on select restrictions | units-split | country |

---

## Feasibility findings (measured 2026-08-09, GPS country frame + WVS Wave 7 means)

### D3 discriminant-bar feasibility — `corr_zero(risktaking, θ=0.30)` on the actual menu

Country-level merged frame (GPS × WVS country means): **n = 42 countries**.

| Menu measure | \|Corr(m, risktaking)\| | slack @ θ=0.30 | verdict |
|---|---|---|---|
| GPS `patience` | 0.253 | +0.047 | ✅ pass |
| Q13 thrift | 0.295 | +0.005 | ✅ **boundary** |
| Q14 determination | 0.015 | +0.285 | ✅ comfortable |

**Finding:** θ=0.30 is a **live claim** — it does not empty $M^*$ by construction.
But Q13 thrift sits ~0.005 from the bar (boundary case; P5 boundary attribution will
flag it). The patience conclusion leans on GPS + Q14.

**Cross-preference context (GPS country, n=76):** Corr(patience, risktaking) = 0.230;
patience vs altruism = −0.010; vs posrecip = 0.016; vs negrecip = 0.258; vs trust = 0.190.
The six dimensions are distinct at country level (Falk et al. pattern).

### Convergent-criterion design alert (measured)

Corr with `risktaking` for candidate auxiliaries (n=42): Q48 freedom = +0.025,
**Q49 life satisfaction = −0.331**, Q275 education = +0.046.

**Implication:** Q49 (life satisfaction) is a **confounded convergent criterion** — it
co-moves with both patience and risk (−0.33). A `corr_min` on Q49 as a patience
convergent bar would be convergent-to-anything-positive, not convergent-to-patience.
Education (Q275) is the cleaner convergent criterion at country level. **Revisit the
convergent-bar design before freezing.**

### θ decision (OPEN — Augusto)

| Option | Effect | Cost |
|---|---|---|
| Keep θ=0.30, keep Q13 | honest; Q13 flagged boundary | conclusion leans on GPS+Q14 |
| Pre-register θ=0.35 w/ literature anchor | Q13 rejected; menu = {GPS, Q14} | narrower menu |
| Pre-register θ=0.25 | Q13 passes comfortably | weaker discriminant claim (risk r=0.25 inside bar) |

Working default while iterating: **θ=0.30, keep Q13** (fragility-audit honest).

**Open items (Augusto):**
- θ values for every restriction + `anchors.yaml` entries (literature / derived / author)
- Whether education is a `mean_order` (binned) or `monotone_rank` (continuous) claim
- Whether to add a WVS risk proxy to the individual menu to carry the discriminant bar
- Full menu list (which proxies beyond Q13/Q14), and β choice (chosen last)
- Holdout country split (pre-registered before freeze)
