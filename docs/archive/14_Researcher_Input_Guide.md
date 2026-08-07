# 14 — Researcher Input Guide

**Status:** scaffold v0.1 companion (2026-08-01) — DRAFT guidelines for humans/agents preparing SCORE/RESTRICT inputs
**Audience:** empirical researchers (and coding agents helping them)
**Authority:** USER owns construct definition, network $R,\theta$, and every scoring choice. This doc is **process guidance**, not a substitute nomological network.

---

## 1. Why scoring is outside the engine

The engine is **score-agnostic**. It never invents measures, never calls an LLM, and never decides whether Q57 and “institutional confidence” are the same construct.

That is intentional. Turning instruments into scalar columns is where:

- theory meets item wording,
- reverse codes and missingness live,
- composites either clarify or smuggle non-equivalence,
- criterion anchors (e.g. GPS) can accidentally become circular.

If the package “helpfully” collapsed batteries for you, it would silently author part of $C$. **Bad for identification, worse for the paper trail.**

```
 upstream (researcher)              engine
──────────────────────            ─────────────────────────
raw instruments / models
        │
        ▼
 scoring decisions  ──► unit×measure matrix ──► SCORE
 composites / splits
 missingness / polarity
        │
 network R, θ, β     ─────────────────────────► RESTRICT → IDENTIFY → REPORT
```

---

## 2. Required input files (conceptual contract)

Exact schemas land at M1; shapes below match `02_System_Architecture.md`.

| Artifact | State | Role | Who authors |
|---|---|---|---|
| `scores` (parquet/csv) | SCORE | Units × candidate measures $m_j$ | Researcher (upstream scorers OK) |
| `aux` (optional) | SCORE | Auxiliaries $V$ used in restrictions | Researcher |
| `outcome` (optional) | SCORE | $y$ and controls for $\beta$ | Researcher |
| `units` meta | SCORE | Unit id column, optional weights | Researcher |
| `network.yaml` | RESTRICT | Restrictions $R$ + $\theta$ | **USER (main path)** |
| `beta.yaml` | RESTRICT | Target functional $\beta(\cdot)$ | USER chooses; engine evaluates |

**Rule:** anything not in the score matrix does not exist for IDENTIFY. Document how each column was built in a short `scoring_notes.md` next to the freeze (recipe, not engine module).

### Minimal column hygiene

1. **One row = one unit** (person, firm-year, country, …). Same unit index across scores/aux/outcome.
2. **One column = one scalar measure** already coded so “higher = more of $C$” **or** polarity declared and handled before freeze.
3. **Missingness handled upstream** (drop, impute with audit, or exclude that measure for incomplete units). Engine MVP does not impute.
4. **Finite small $J$** for first profiles ($\sim 3$–$12$). Add columns only when each answers a distinct measurement hypothesis.
5. **Freeze after scoring.** Changing a composite definition ⇒ new score hash ⇒ new run. Do not edit frozen columns in place.

---

## 3. Composites vs split measures

### 3.1 Default posture

| Situation | Default |
|---|---|
| Items are **near-synonyms** of one facet (same stem, same object, same polarity) | Composite OK (mean / PCA-1 / sum), **plus** optionally keep a single flagship item |
| Items differ by **object** (strangers vs family vs police vs parliament) | **Split** — separate columns or separate facet composites |
| Items differ by **response technology** (binary trust vs 1–10 justifiability vs membership) | **Split** |
| Map tags say `clean` vs `bridge` vs `stretch` | Do not pool across tags into one $m_j$ |
| You trained / prompted a model on instrument family A and evaluate on family B | Separate LLM columns per family (e.g. `m_llm_gps_scen` vs `m_llm_wvs_stem`) |
| Only one item available | Single column; do not invent fillers |

**Test question:**
> If two items can move in opposite directions for theoretically respectable reasons, they are not one measure.

Example (trust): generalized trust (most people…) and confidence in government can diverge after a corruption scandal. Pooling them into `m_wvs_trust` hides the failure mode you care about.

### 3.2 When a composite is justified

A composite is reasonable when **all** of the following hold:

1. **Same construct claim** under your prose definition of $C$ (not merely the same GPS dimension *label*).
2. **Same polarity** after reverse-coding.
3. **Comparable scale** or explicit standardization before averaging.
4. **Missingness pattern** does not systematically drop different subpopulations per item (or you document and restrict the sample).
5. You can state one sentence: “This composite is the mean of {…} as an operationalization of *facet F* of $C$.”

Still prefer **reporting the composite and its constituents** in exploratory menus when $J$ allows; use the composite alone only when constituents are pure redundancy.

### 3.3 Recommended split hierarchy (survey batteries)

Work top-down; stop when further splits no longer map to distinct hypotheses:

```
dimension label (e.g. "trust")
  └─ instrument family (GPS tasks | WVS attitudes | AB political culture | LLM)
       └─ facet (generalized interpersonal | in-group | out-group | institutional)
            └─ optional: single flagship item (Q57, IT1, …)
```

**Menu members** are usually at the **facet × family** level, not raw item spam and not one mega-score per dimension label.

### 3.4 Anti-patterns

| Anti-pattern | Why it hurts |
|---|---|
| One column “WVS trust” = all Q57–Q73 | Mixes interpersonal and institutional; slacks become uninterpretable |
| One column “LLM culture” = all six GPS dims | Multi-construct smuggled into single $C$ run |
| Averaging GPS z and WVS mean on different samples without a common unit | Invalid SCORE matrix |
| Reverse-coding “by vibe” after seeing $\beta$ | Garden of forking paths; freeze polarity first |
| Dropping items that disagree with the favorite measure | Silent construction of $M^*$ |
| Building $R$ from the same items that define $m_j$ without declaring criterion posture | Circular admissibility |

---

## 4. Anchors: what they are and when to use them

“Anchor” is overloaded. Separate three roles.

### 4.1 Role A — **Criterion measure** (P1 posture)

One measure is treated as the **standard** you want others to recover.

| Use when | Example |
|---|---|
| Training / design intentionally targeted that standard | LLM / adapter built to match **GPS** moments and Falk-style scenarios |
| First empirical audit is “did we hit the target instrument?” | `corr_min(m_llm, m_gps) ≥ θ` |
| You are explicit that others are judged *relative to* the criterion | WVS is on trial; GPS is not |

**Rules:**

- Label the run **criterion-validity**, not “symmetric construct profile.”
- GPS (or dictionary, or human rater) may sit in $M$ or only in $V$ / restriction RHS. Prefer: criterion in menu **and** in restrictions, with prose stating privilege.
- Do **not** pretend GPS “passed a neutral network” if the only hard gates are correlations with itself.
- $\theta$ on criterion correlation is a **tolerance for recovery**, not a deep theory parameter — grid it.

**First test recommendation (SCA-style and general):**
Start with **P1 / criterion recovery** (LLM vs GPS). It is more empirical, easier to evaluate, and matches the training objective. Graduate to peer networks (Role B) only after recovery is characterized.

### 4.2 Role B — **Peer candidate** in a symmetric menu (P2 posture)

No measure is sacred. All $m_j$ face the same external $R$ (theory-implied correlates, group orderings, stability).

| Use when | Example |
|---|---|
| You want to know which instruments implement a **verbal** definition of $C$ | Falk prose definition + external correlates; GPS is one column among equals |
| Criterion recovery already failed or succeeded and you need external discipline | After P1, ask whether GPS itself is only a narrow task factor |

**Rules:**

- Build $R$ from **auxiliaries and implications not identical to menu columns**.
- Avoid sole reliance on `rank_agree` with a privileged ref measure (dictionary/GPS privilege — see Q5). If used, report as sensitivity.
- GPS can fail. Empty $M^*$ is allowed.

### 4.3 Role C — **Synthetic / eval anchor** (engine gates only)

In synthetic DGPs, `m_dict` (or designated valid) is the **H1a/H1b anchor**: under oracle-compatible $R$, it should stay in $M^*$ and $\beta(m_{\mathrm{anchor}})$ lies in $[L,U]$ by construction of the range.

| Use when | Notes |
|---|---|
| Calibrating the engine | Not a claim about real GPS/WVS |
| Prereg H1a / H1b | Pin anchor id before seeds; no post-hoc swap |

**Do not** import synthetic anchor logic into empirical papers as “the true measure.”

### 4.4 Role D — **Reference for rank agreement** (optional restriction)

`rank_agree(m, m_ref) ≥ θ` says candidates should order units like $m_{\mathrm{ref}}$.

- Useful as a **soft** check under P1.
- Dangerous as the **only** gate under P2.
- Document $m_{\mathrm{ref}}$ and treat θ-grid as mandatory.

---

## 5. Choosing units (before any composite)

| Design | Unit | When |
|---|---|---|
| Cross-walk surveys / GPS country z / country-conditioned LLM | **Country** (or region) | Default for multi-instrument culture work |
| Single microdata survey, internal operationalizations | **Person** | WVS-only or AB-only menus |
| Text scored at document level | **Document** (article, filing, post) | NLP measures + document-level aux |
| Panel | **Entity-time** | Only if every $m_j$ is defined on that index |

**Hard rule (from multi-survey practice):** do not row-bind different surveys’ respondents into one SCORE matrix and treat rows as exchangeable. Join at the **moment level** (country means, etc.) when instruments sample different people.

If a measure is missing for many units (e.g. regional survey), either:

- restrict the universe to overlap, or
- leave that measure out of the global menu and run a subsample profile,

and say which you did in the freeze notes.

---

## 6. Building `network.yaml` without smuggling $\beta$

### 6.1 Order of operations

1. Write **one paragraph** defining $C$ (prose).
2. List **testable implications** as inequalities in plain language.
3. Only then pick restriction types (`corr_sign`, `corr_min`, `mean_order`, …) and $\theta$.
4. Choose $\beta$ **last** (what economic number you track). Do not reverse-engineer $R$ so that your favorite regression survives.

### 6.2 Good restriction sources

- Signed association with aux not in the menu (or used carefully if it is).
- Group orderings pre-registered (country A vs B, treated vs control) when theory speaks.
- Stability across split halves of units (measurement noise discipline).
- Under P1: minimum association with criterion measure.

### 6.3 $\theta$ discipline

- Set $\theta$ **before** looking at the slack heatmap when possible; if exploratory, label run `exploratory` and freeze a second prereg network for claims.
- Always plan a **θ-grid** for any restriction that decides membership on a knife-edge.
- Prefer fewer sharp restrictions over a kitchen-sink net that empties $M^*$ for opaque reasons.

### 6.4 Single construct per run

MVP = one $C$ per profile. Six GPS dimensions ⇒ **six** networks / six runs (shared score file OK if columns are a superset). Multi-construct joint networks are out of MVP.

---

## 7. Worked pattern: criterion recovery first (LLM vs GPS)

*Illustrative workflow — not an authored empirical network for SCA2 main results.*

**Goal:** Did the LLM / adapter operationalization recover GPS dimension $d$ as intended?

| Step | Action |
|---|---|
| 1. Unit | Country (GPS coverage) |
| 2. Menu | `m_gps_d`, `m_llm_d` (and optionally distractors: noise, wrong-dim LLM score) |
| 3. How to score LLM | **Same instrument family as training** first (GPS-style scenarios / Falk-like choices). WVS stems are a **second** column / second run |
| 4. Posture | **P1 criterion** — GPS is standard |
| 5. Core restrictions | `corr_min(m_llm_d, m_gps_d) ≥ θ`; optional sign checks on external aux shared by both |
| 6. $\beta$ | Optional for pure recovery audit; use `corr_y` only if a downstream claim exists |
| 7. Success language | “Under θ-grid, $m_{\text{llm}}$ admissible as GPS-recovery at θ≤…” — **not** “LLM measures true culture” |
| 8. Failure language | “Fails GPS recovery at prereg θ” — then diagnose scenario stem, country slice, dim contamination — **not** silent θ drop in the default path |

**Only after that:** add WVS facet columns and/or a P2 network that does not privilege GPS.

---

## 8. Checklists

### 8.1 Before freeze (SCORE)

- [ ] Unit definition written in one sentence
- [ ] Every column has: source, formula/composite recipe, polarity, missingness rule
- [ ] Split vs composite decisions recorded with the “opposite movement” test
- [ ] Instrument families not silently pooled
- [ ] Overlap sample rule stated if measures differ in coverage
- [ ] No outcome $y$ leakage into measure columns (especially LLM judges that see $y$)
- [ ] Scoring notes path stored next to data

### 8.2 Before claims (RESTRICT / IDENTIFY)

- [ ] Posture labeled: **P1 criterion** vs **P2 peer** vs **synthetic oracle**
- [ ] $C$ paragraph ≠ dimension marketing label alone
- [ ] $R$ not copied from the regression spec that defines $\beta$
- [ ] $\theta$ prereg or explicitly exploratory
- [ ] Anchor roles named (criterion / peer / synth / rank-ref)
- [ ] One construct per run
- [ ] Empty $M^*$ acceptable; no auto-loosen plan in default path

### 8.3 Paper / thesis citation

- [ ] Run id / hashes for scores, network, beta, seed, package version
- [ ] Menu $J$ and identities of survivors / failures
- [ ] Binding restrictions named
- [ ] θ-sensitivity shown for membership-critical gates

---

## 9. What “good documentation” next to a run looks like

Ship a short companion (human markdown is enough):

```text
profiles/trust_gps_criterion_v1/
  scoring_notes.md    # column recipes
  network.yaml
  beta.yaml
  units_universe.md   # who is in the sample
  posture.md          # P1 vs P2, one paragraph C
```

`scoring_notes.md` template:

```markdown
## Construct (prose)
...

## Unit
country_iso3; universe = GPS countries with non-missing trust z

## Measures
| id | recipe | polarity | source |
| m_gps_trust | country z from Falk et al. | higher = more trust | country_gps.dta |
| m_llm_trust | mean adapter pref margin on held-out GPS-style trust scenarios | higher = more trust | ... |

## Explicit non-composites
WVS not in this freeze (deferred to trust_wvs_bridge_v1)

## Posture
P1 criterion recovery of GPS trust
```

---

## 10. Relation to other docs

| Doc | Relation |
|---|---|
| `02_System_Architecture` | File-level IO contracts |
| `03_Methodology` | Formal $M, R, M^*, B^*$ |
| `04_Synthetic_DGPs` | Role C anchors and oracle labels |
| `05_Pre_Registration` | H1a/H1b anchor gates (engine) |
| `10_Open_Questions` | Q5 reference-measure privilege; Q13 user owns $R$ |
| `11_Glossary` | Measure, menu, anchor terms |

---

## 11. One-page defaults (printable)

1. **Engine does not score** — you do; freeze recipes.
2. **Split by default** across objects, stems, and instrument families; composite only inside a facet.
3. **Criterion recovery first** when a system was built to match a standard (e.g. LLM → GPS).
4. **Peer network second** if you need non-circular validity language.
5. **Common unit or don’t run** — no fake row merges.
6. **Small $J$**, written $C$, written posture, θ-grid on knife-edges.
7. **Empty and wide are results.**

---

## 12. Open taste items (not locked)

- Default composite aggregator (mean vs PCA-1 vs IRT) — domain-specific; document choice.
- Whether institutional and interpersonal trust ever share a profile as *facets of one C* vs always separate Cs — USER theory call.
- Minimum country n for country-level profiles — statistical taste; bootstrap honesty matters more than a magic n.
- Exact YAML schema — deferred to M1.

---

## 13. θ-anchor discipline (v2.0, process guidance)

Thresholds $\theta$ are where "literature-grounded, not data-mined" is won or lost. The package now has a schema'd **pre-data anchor artifact** (`anchors.yaml`, v2.0 thread c) so that discipline is machine-checkable, not prose:

**What to write, per restriction:**
- `restriction_id` — must match the network exactly (the engine checks).
- `citation_key` — stable reference key (e.g. `oecd2017`); full citation lives in the design doc.
- `source_phrase` — the published/derived number or bound the θ sits at or below (e.g. "country-level survey↔behavioral r≈0.29" for θ=0.3).
- `anchor_kind` — `literature` (published estimate/bound), `derived` (computed from a stated rule), or `author` (explicit judgment).
- `pre_data: true` — your record that the anchor was declared before the frozen run. The engine **cannot verify timing**; this flag is the researcher's commitment, and the verifier requires it for the H5 lane.

**Practice rules:**
1. **One anchor per restriction**, written before the frozen run, committed with the design inputs. The engine refuses incomplete anchor sets.
2. **Anchor at or below published bounds** (conservative direction), and say so in the source phrase — this is what makes "not data-mined" auditable.
3. Anchors are **documentation, not engine inputs**: they are hashed for provenance (`anchors_hash` in the manifest, `anchors.json` in the run dir, report panel) but **excluded from `run_id`** — adding anchors never changes the freeze.
4. When a restriction has no clean published number, say so explicitly (`anchor_kind: author`, source phrase = the judgment and its reasoning). Silence is a red flag, not a default.

---

## 14. Relation to other docs (v2.0 pointer)
