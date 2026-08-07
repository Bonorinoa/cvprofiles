# 01 — Project Overview

**Status:** scaffold v0 (2026-08-01)
**Type:** open-source academic methods tool (package + paper)

## Problem

Empirical work increasingly fills regressors and text scores with cheap AI operationalizations of latent constructs (sentiment, uncertainty, ideology, “AI exposure,” soft skills, …). Typical practice: pick a favorite prompt or dictionary, run a point estimate, gesture at “robustness.” That collapses measurement uncertainty into a single column and invites overclaiming.

## Claim (load-bearing)

Construct validity under a **menu** of measurement functions is usefully cast as **partial identification**:

1. Researcher states a **nomological network** $R$ (testable implications, often inequalities) with thresholds $\theta$.
2. Engine admits measures that satisfy sample analogues of those restrictions → admissible set $M^*$.
3. Downstream parameter of interest is the image $B^* = \{\beta(m) : m \in M^*\}$, reported as a range $[L,U]$. **v1.0:** $[L,U]=\min/\max B^*$. Bootstrap and $\theta$-sensitivity are **v1.1**.

Empty $M^*$ and wide $[L,U]$ mean **“we don’t know under this theory”** — first-class scientific outputs.

Closest ancestor: **Leamer-style specification uncertainty**, moved from regression specs to measurement functions, disciplined by a researcher-stated network rather than kitchen-sink search. Formal home: partial identification. Variance-based GSA and OVB-on-a-fixed-$X$ are cousins, not the same question.

## Non-claims

- We do **not** claim all of economics is inequalities.
- We do **not** claim sharp new PI theory is required for the tool to be useful (sharp theory is optional garnish).
- We do **not** put an LLM inside the engine. Models may only appear **upstream**, when the user chooses how to fill score columns.
- We do **not** author the researcher’s nomological network for main results (strict paper path).

## Users

| Primary | Secondary |
|---|---|
| Empirical researchers who already have multi-measure scores and want disciplined sensitivity | Methods reviewers who need an audit trail |
| Applied econometricians building AI operationalizations of latent constructs | Students and researchers learning measurement-discipline tooling |

Persona for the tool UX: **a careful applied econometrician**, not a product manager. Prefer boring clarity over dashboard theater.

## Deliverables

| Deliverable | Role |
|---|---|
| Python package (`cvprofiles` working name) | SCORE→REPORT engine, CLI, library API |
| Synthetic DGP suite + eval harness | Capability map before real data |
| Report artifacts (HTML/JSON/LaTeX) | Human- and agent-readable audit trail |
| Paper | Method + synthetic evidence + one public baseline |
| These docs + dual live logs | Cross-agent context and prereg discipline |

## In scope (MVP)

- Four-state pipeline with frozen-run determinism
- Researcher-authored network schema + $\theta$
- Target functional $\beta(\cdot)$ as a declared plug-in (start: simple association / regression coefficient)
- Finite menu $M = \{m_j\}_{j=1}^J$, $J$ small
- Sample slacks → $M^*$ → $B^* / [L,U]$
- Bootstrap and $\theta$-grid sensitivity
- Synthetic DGPs with known truth and four debug metrics
- REPORT layer a non-coder can skim

## Out of scope (unless decision log reopens)

See README hard non-goals. Additionally deferred for MVP:

- Interactive network-elicitation UX beyond plain config files
- Continuous infinite menus / functional optimization over measure space
- Causal identification strategy design (we discipline **measurement** given a stated $\beta$)
- Multi-construct joint networks (single construct $C$ first)
- GUI app / SaaS

## Success criteria (project-level)

1. On calibrated synthetic DGPs, the four debug metrics behave as preregistered (see `05_Pre_Registration.md`).
2. A frozen triple `(scores, network, seed)` reproduces bit-stable engine outputs.
3. A non-author can read `report.html` and state what was admitted, what failed which restriction, and how $[L,U]$ moves in $\theta$.
4. Scope police holds: no LLM in engine; no silent network authorship in main path.

## Name

**cvprofiles** — short, package-aligned. Display phrase: *construct-validity profiles*. Symbolic rename is optional later; do not block scaffold on aesthetics.
