# Review of Position Paper v7 → v8 Plan

**Authors of this review:** Hermes (independent lanes) for Augusto + co-authors planning v8.
**Date:** 2026-08-10.
**Inputs:** `position_paper_v7.pdf`, hand-drawn figure sketch `IMG_4203-2.HEIC`, the embedded `notes` block in the request, `docs/16_Paper_Protocol_Freeze.md`, `docs/METHODOLOGY.md`, `docs/18_IVS_Cultural_Map.md`, AGENTS.md, the verified citation bank at `~/.hermes/skills/research/scientific-paper-strategy/references/measurement-selection-literature-2026.md`.

**Scope.** Review only. Not an editor. v8 edit choices remain Augusto's.

---

## 0. Three things to surface before drafting

These would have slipped in silently if I had just executed. Please read them first because they condition everything below.

### 0.1 The sketch you attached is **not** v7's Figure 2

v7's Figure 2 is the **epistemic systems view**: Generators → Menu `M` → Network `R,τ,δ` → Holdout design `M*,B*` → Uncertainty band. It is a **who-owns-what** diagram (researcher vs engine), with dashed boxes for researcher/generator-owned layers. That figure is load-bearing for the methods-lecture tone and the human-owned-validity-gate framing.

The hand-drawn sketch attached (`IMG_4203-2.HEIC`) is **a different figure**: a 4-row conceptual matrix (Uncertainty / Construct validity / Estimation / Inference+robust tests × Theory / Empirically) with method families (ML/DL, PCA/EFA, Survey calb, capabilities in ML layer, AI agent, Human, econometric analysis, causal mediation, stat models, numerical penalty) and data sources (specific sensors, MTM, MTM-CFA, overview identification). The connecting lines form a zigzag between theory rows and empirical rows.

**Options for v8:**
- **(A)** Replace Figure 2 with the 4-row matrix — but then you lose the "engine vs researcher" ownership story, which is one of the paper's main contributions (see §11 in v7 and §3.2 below).
- **(B)** Keep the epistemic systems view as Figure 2 (it earns its place) and use the 4-row matrix as a *motivation* figure earlier in the introduction or as an Appendix figure showing the cross-disciplinary landscape.
- **(C)** Hybrid: the 4-row matrix becomes Figure 1 (now missing in v7), and the epistemic systems view becomes Figure 2.

My recommendation: **(C)**, with a relabel — the 4-row matrix is a **landscape figure**, not a methodology figure. It is honest about the cross-disciplinary toolkit, but it is *not* the framework.

**Double-check on the epistemic breakdown.** The 4-row matrix is a recognizable taxonomy in measurement theory (it tracks the four tasks of validity argumentation: uncertainty quantification, construct validation, estimation, inferential robustness). There is prior art in the same shape:
- Borsboom's "three families of validity evidence" taxonomy (Borsboom, Mellenbergh, van Heerden 2004, *Psychological Review*).
- Wallach et al. (2025) ICML "four-level framework grounded in measurement theory for GenAI evaluation" (cite: arXiv:2409.08931 → PMLR 267:82232–82251).
- Handfield et al. (2024) and related measurement-instrument-validation taxonomies in marketing/psychometrics.

If you keep the matrix as a figure, **cite Wallach et al. 2025** as the closest established four-level framework so the claim is "we instantiate, with explicit menu-level PI, an established four-layer decomposition" rather than "we invented the four layers." That is the same defensive move as Dell–Rambachan positioning.

### 0.2 v7's "flagship" application (SCA2-vs-persona) has been **superseded** for v3

This is the most important landmine. v7 §8 names SCA2-vs-persona prompting on USA/MEX GPS trust as the flagship. But `docs/16` §9 (dated amendment 2026-08-07) and `docs/18` re-graded the v3 empirical lane:
- **H5 Trust (SCA2-vs-persona)** is re-graded to **historical / regression witness**. The n=35 run is not paper evidence.
- **IVS cultural-values evaluation** (Tao et al. 2024-style, Joint EVS/WVS 2017–2022 v5.0, ~92 unique countries, Inglehart–Welzel axes as target, open-weight local models, frozen Tao loadings including PC2′ = 1.61·PC2 − 0.01 **provisional**) is **the** v3 empirical direction under Gate B conditions.
- Open-weight policy (D5/D6): no DPO adapters, no proprietary APIs for paper-reproducible scoring.
- **Y003 status (T32):** 9/10 IW item codes dictionary-verified; **Y003 is absent from the Joint Common Dictionary** (it's a WVS7-only Autonomy Index). Y003 + PC2′ remain **hard Gate B** items requiring your transcription audit.

**Implication for v8 restructure.** If your "Section 4. Preliminary results: applied example on cultural measurement and LLM alignment using cvprofiles" still uses SCA2-vs-persona, you have two choices:
- Re-cast it as a **secondary worked illustration** (worked-example framing, not headline). The GPS trust design + n=35 historical checkpoint is still usable as a *worked example* of the engine, provided you re-label from "preliminary results" to "engine demonstration on a frozen small-n example."
- Pivot to the **IVS lane** as the headline empirical target. But the IVS lane is *not* preliminary results yet — the empirical network, score matrix, and β-registry extension are all AWAITING AUGUSTO in `docs/18`. Honest v8 framing is "planned flagship application (IVS cultural-values lane), subject to Gate B authorization" and not "preliminary results."

My recommendation: **Section 4 in v8 = "Planned empirical application (Gate B)"**, with SCA2-vs-persona as a small-n worked example in an appendix, and IVS as the planned flagship whose preregistration is specified in `docs/18`. This avoids re-claiming H5 as evidence and pre-commits to the v3 lane without overpromising.

### 0.3 The lit-review narrative you drafted has one factual risk + one near-neighbor you should name

**Risk — Dell–Rambachan claim language.** Your draft says: "Dell and Rambachan … explicitly deferred operational estimation, inference protocols, and data-dependent screening." This is the **same wording the v6 SCA2 paper was corrected on** (verified citation bank entry on 2026-08-09). The actual NBER SI 2026 Methods Lectures are titled "**Estimation and Inference with AI-Generated Data**" — Part 4 formalizes identification from repeated measurements with a δ-indexed identified set `H(θ;δ)` (Chen–Rambachan–Tamer 2026). Defensible reword:

> "Dell and Rambachan formalized the nomological network through the lens of microeconometric partial identification — explicit moment inequalities over a menu of candidate measures yielding a construct-identified set — and called explicitly for principled, widely accepted methods of construct validity. The present paper operationalizes that call with a menu-level admissible set, a holdout-falsifiable selection rule, and an inference layer over the estimated admissible set."

**Near-neighbor — Chen, Rambachan & Tamer 2026.** Your draft does not name them. They are the **closest published paper** to your framing: Chen, Rambachan & Tamer, "**Partial Identification from LLM Prompts**" (arXiv:2606.15031v2, 24 Jun 2026, econ.EM). Verified today against the arXiv page and the v2 PDF. Their restrictions are **benchmark-informed bounds on marginal performance and joint response events** for the downstream parameter `θ = P(X* = 1)`, indexed by `δ`, with identification via two linear programs. The contrast you must draw (which I verified in your skill's citation bank is missing from v7):

> "Chen, Rambachan & Tamer (2026) study partial identification of a downstream parameter `θ` from LLM prompts whose errors are arbitrarily correlated. Their identifying restrictions are **benchmark-informed bounds on error correlation** that discipline the mixture in the spirit of the misclassification literature. Ours are **nomological-network moment inequalities over the menu**, with the object of inference being `M*` (the set of surviving measures), not a single downstream parameter; and our selection rule is held-out-falsifiable, not assumed. Theirs sharpens an econometric identification result; ours operationalizes a measurement-validity program."

If you do not draw that contrast, a reviewer (likely an econometrician — Tamer is on the editorial board of *Econometrica*) will read your "menu-level partial identification" framing and assume you have not seen CRT 2026.

**Verified Li et al. 2026 attribution** (you had this right). The full citation is:
- Li, B., Yu, T., Koa, K. J. L., & Huang, K.-W. (2026). "The Proxy Presumption: From Semantic Embeddings to Valid Social Measures." *Proceedings of ACL 2026 (Volume 1: Long Papers)*, pp. 22892–22910. arXiv:2605.07409. ACL 2026 Oral + SAC Highlight.

Verified today against the arXiv page and ACL Anthology (`https://aclanthology.org/2026.acl-long.1048/`). The Construct Validity Protocol (CVP) and Counterfactual Neutralization are correctly attributed in your draft.

---

## 1. Contribution claims audit

### 1.1 The headline contribution as written in v7

> "A general, auditable method for using construct-validity evidence to select among heterogeneous measures and propagate remaining measurement uncertainty into scientific conclusions, implemented in open software, illustrated on controlled DGPs, and designed for a real-world cultural-preferences application."

This is **defensible**, but **vague** at the contribution level. A Nature/PNAS general-science reviewer will want a sharper claim. Three possible reframings, ordered by my preference:

**(R1) Operational gap-closure (recommended).**
> "The first operational bridge between construct-validity psychometrics and partial-identification econometrics: a menu-level admissible set, a holdout-falsifiable selection rule, and a coupled inference layer — closing the gap Dell and Rambachan (2026) explicitly identified in their NBER SI Methods Lectures."

This is the strongest defensible version because:
- It positions against a **named external gap** (Dell–Rambachan: "principled, widely accepted methods for construct validity").
- It names **three concrete operational primitives** (admissible set, falsifiable selection rule, coupled inference) — these are auditable.
- It avoids overclaiming ("we solved construct validity") and avoids underclaiming ("we built a package").

**(R2) Methodological framework.**
> "A menu-level partial-identification framework for measurement selection when measures are cheap, with a falsifiable selection rule and a coupled inference layer."

Weaker — does not name the cross-disciplinary synthesis the paper is doing, which is the *interesting* part.

**(R3) Tool paper.**
> "An open implementation of construct-validity profiles for measurement selection."

Weakest — Nature/PNAS general-science does not publish tool papers.

### 1.2 The "psychometrics × econometrics × CSS/NLP" cross-disciplinary synthesis

Your draft narrative correctly identifies this as the contribution's spine. Defensible as written. Three small tightening suggestions:

- **Name the synthesis, do not just describe it.** Add a sentence at the end of the lit-review intro: "The synthesis implemented in the cvprofiles framework unifies these parallel traditions into an integrated, auditable workflow capable of evaluating human surveys and AI-generated proxies under a single, theory-grounded nomological argument." (This is what your draft already has; keep it but make it the section's closing sentence.)
- **The "operational workflow" language is defensible** — but make sure you do not slip into "we have a unified theory of measurement." You do not. You have a workflow that disciplines *one specific layer* (menu-level selection) using tools from each tradition.
- **Add Chen–Rambachan–Tamer to the lit-review** (see §0.3). It belongs in the econometrics subsection as the closest near-neighbor.

### 1.3 Are the contribution claims *publishable* in Nature/PNAS general science this year?

**Honest answer: yes, plausible, with conditions.** Three reasons it is publishable:

1. **Cross-disciplinary synthesis + named gap.** The Dell–Rambachan gap quote is verifiable, the cross-tradition synthesis is genuine, and the operational primitive (admissible set + holdout-falsifiable rule + coupled inference) is auditable. That is exactly the shape Nature/PNAS general-science likes: take a real methodological problem, propose an operational solution that is auditable across disciplines.

2. **AI-relevance with a defensible framing.** "Cheap measurement + invalid constructs" is a real and growing problem in social science + AI evaluation. v7 already cites the right evidence (Baumann et al. 31% incorrect conclusions; Hall 2026 PolMeth content analysis; Desai–Card–Jacobs 2026).

3. **Software backing without tool-paper cosplay.** The package is real, versioned (2.5.2), tested, and locked against a paper protocol. That is the right posture — not "we invented a method and built software" (tool paper), not "we invented a theory" (theory paper), but "we operationalized a gap that the literature has named."

**Conditions that determine whether it lands:**

- **The IVS lane needs to at least be a *registered* design by submission time.** PNAS/Nature general-science will not accept a position paper whose flagship application is "planned, awaiting Gate B." You need either (a) IVS frozen scores + a small frozen-n preliminary, or (b) the SCA2-vs-persona historical design elevated to a *worked example* with a clearly-labeled "the planned flagship is IVS, see docs/18" pointer. Option (a) is preferable if you can get it before submission.
- **Page count discipline.** v7 is 17 pages. The restructure you propose (move DGPs to Appendix, compress notation to ≤2 pages, eliminate Figure 1) gets you to ~12–14 pages, which is the right zone for Nature/PNAS general-science (most successful submissions are 12–18 pp main text + appendix).
- **The lit-review narrative must be tightened** to the 3-paragraph shape you drafted and integrated *into* the methodology story. Right now v7 §3 mentions psychometric history in one paragraph; v8 should fold that history into a unified lit-review section that the methodology section references back to.
- **The Goodharting claim (§11.6 of v7, "the feedback loop is falsifiable, not universally verifiable") must be sharpened in v8.** Reviewers will probe this. The defensible form: human-owned validity gates `(R, τ_r)` are essential to prevent autonomous LLM agents from Goodharting their own validation criteria. The framework supplies the audit surface; it does not solve Goodharting.

### 1.4 What v7 currently claims that I would **downgrade** in v8

| v7 claim | v8 framing | Why |
|---|---|---|
| "Empirical cells are empty by design; this awaits Section 8" | "Section 4 specifies a preregistered empirical plan whose execution is gated on Gate B (`docs/16 §9`) and frozen scores in `docs/18`" | The current phrasing reads like procrastination; the new phrasing is honest about the gate. |
| "Empirical license (still missing, by design)" in §10 | "Empirical license is gated on Gate B" + cross-link to `docs/18` | "Missing by design" can read as evasive; "gated" is the project-language term and matches AGENTS.md. |
| "Synthetic Cultural Agents are therefore one family of measurement-generation technologies for culturally patterned preference profiles" (Section 6) | Keep, but explicitly distinguish: SCA = a *family of generators* for the menu, not the framework itself. | Reviewers will read SCA as the contribution otherwise. The contribution is the menu-level validity layer; SCA is one menu family. |
| The flagship in §8.1 | Demote to a worked example; promote IVS to the planned flagship (see §0.2) | The H5 Trust run is re-graded to historical. |

### 1.5 What v7 currently underclaims that I would **promote** in v8

- **The cross-disciplinary synthesis IS the contribution.** v7 buries it in §3 ("what should a valid measure do?") and §6 ("AI as a measurement generator"). v8 should put it in the lit-review section explicitly as the synthesis claim, and the methodology section should *refer back to* it, not re-establish it.
- **The human-owned validity gate framing** (currently in §11.6 and §12) deserves its own subsection in v8 §3.1 — it is one of the most quotable framings in the paper and is currently scattered.
- **The Goodharting-with-restrictions warning** is genuinely valuable and should be promoted from a single sentence in §11.6 to a structured paragraph with the exact failure mode spelled out (an LLM agent that optimizes against `R` to enter `M*`; a researcher's `R` written after observing `M*` — the Baumann et al. 2025 failure mode in disguise).

---

## 2. v8 restructure: section-by-section review

Your proposed structure is materially better than v7. Section-by-section:

### 2.1 Section 1 — Introduction (system view → cheap measurement → menu selection → cvprofiles applied example)

**Agree, with two refinements:**

1. The "applied example with cvprofiles" should reference the IVS lane (`docs/18`), not SCA2-vs-persona as the headline. SCA2-vs-persona can appear as a worked example near the end of the intro or as an Appendix reference.
2. The introduction should NOT introduce every object in the formalism (you already have §2 for that). The intro introduces *the systems view* and the *problem framing*; the objects come in §2 (or compressed into a single notation page in §3 if you are aggressive about page count).

### 2.2 Section 2 — Literature review (the three-discipline narrative)

**Agree, with three refinements:**

1. Add Chen, Rambachan & Tamer (2026, arXiv:2606.15031v2) to the econometrics subsection as the closest near-neighbor, with the contrast paragraph (see §0.3).
2. Add Wallach et al. (2025, ICML) as the closest established "four-layer framework" precedent, in case you keep the 4-row matrix figure.
3. The narrative you drafted (psychometrics → econometrics → CSS/NLP) reads well. One tightening: lead the section with **the problem** (measurement selection when measures are cheap) and let the three subsections answer *what each tradition contributes* to that problem. The current draft has the three paragraphs in order; that is correct, but you can sharpen the framing by stating the contribution at the end ("we unify these into a menu-level, audit-ready workflow").

### 2.3 Section 3 — Methodology (your mental DAG)

**Agree, with two structural notes:**

1. **The "methodology should fit in ≤2 pages" instinct is right, but the load-bearing math (slacks, `M*`, `B*`, `[L,U]`, holdout split, falsifiable claim) cannot be compressed below ~3 pages without losing the methods-lecture tone.** My recommendation:
   - **1 page** for objects + the DAG (your `C → M → M* → B*` workflow + the four-layer systems view).
   - **1 page** for restrictions + admissible set + robustness layers.
   - **1 page** for holdout + falsifiability + inference.
   Total methodology ≈ 3 pp main text + everything else moved to Appendix. This matches the Dell–Rambachan lecture style and is what Nature/PNAS general-science actually reads.
2. **Your mental DAG of the method** ("collecting/generating candidate measures → validating → falsifying → valid inference") should be **the methodology section's spine**. Each subsection corresponds to one node. The reader gets the DAG once and then walks it.

### 2.4 Section 4 — Preliminary results

**Do not call this "preliminary results"** unless you have IVS preliminary results by submission time. Two safe options:

- **(A) Section 4 = "Engine demonstration on frozen inputs (worked example)"** — uses the SCA2-vs-persona n=35 historical run as a worked engine demonstration with a clear "this is illustrative, not paper evidence" disclaimer. Then Section 5 (Discussion) introduces the IVS lane as the planned flagship.
- **(B) Section 4 = "Planned flagship application (Gate B gated)"** — presents the IVS preregistration, the IVS design container, and the empirical network *skeleton* (with `R` AWAITING AUGUSTO clearly marked). The actual numbers live behind Gate B.

My recommendation: **(A)** for v8 submission, with a forward pointer to IVS as the planned flagship. Option (B) is honest but reads thin for Nature/PNAS general-science.

### 2.5 Section 5 — Discussion

**Agree, with two priorities:**

1. **"What the framework does not do" content is correct.** v7 has §11 ("What the framework does and does not claim") and §12 (the human-owned validation gate). v8 should keep both, with the human-owned gate folded into §3.1 (see §2.3 refinement 2) and the "does not claim" content living in §5.1.
2. **"AI benchmarking/evaluation design" should be a *short* subsection, not a parallel thread.** The benchmarking extension lives in Appendix B in v7; v8 should keep it there. The Discussion can have ~one paragraph on benchmark-design as a measurement-menu application, citing Wallach et al. (2025) and Truong et al. (2026, https://aimslab.stanford.edu/papers/Truong2026PublicPrivate) on public-vs-private benchmark tradeoffs.
3. **"Automating social science" and "Manning's causal system" connection** belongs in the Discussion, but framed as **a logical argument, not a product pitch**. v7 §C does this correctly (Appendix C, "Forward-looking: validation gates in automated social science"). Keep that content in Appendix C in v8, with a one-paragraph Discussion pointer.

### 2.6 Section 6 — Conclusion

**Agree.** The "five questions" closing is a strong rhetorical move. Keep it. The `C → M → M* → B*` arrow is the right visual.

### 2.7 References + Appendix

**Agree, with one structural note:** moving the synthetic DGPs to the Appendix is correct, and you should *augment* them with cvprofiles code snippets, as you say. This is the most effective single addition you can make for adoption — researchers see the engine and the commands together. The `tools/paper_synth_p4p5.py` script already exists (`tools/paper_synth_p4p5.py`); the appendix can cite run_ids from it.

---

## 3. Figure audit

### 3.1 v7 Figure 1 — "Core objects of the framework"

**Agree, delete.** It is a vocabulary chart (Menu / Tests / Survivors / Construct / Robust set) that the prose already does. Not load-bearing.

### 3.2 v7 Figure 2 — "Epistemic systems view"

**Keep, but tighten.** Currently it shows: Generators → Menu `M` → Network `R,τ,δ` → Holdout design `M*,B*` → Uncertainty band; dashed boxes are researcher/generator-owned. This is load-bearing. Two tightening suggestions:

1. **Add a "freeze / run-id" pin label** at the boundary between the researcher's commitments and the engine's computation. This is the operational meaning of preregistration in this framework; the figure should show it.
2. **The "empty rate" boundary diagnostic should be visually distinguished** from the headline `[L,U]`. Currently it sits inside the same uncertainty-band box. The defensible layout: a separate "diagnostics" lane below the headline output, with the honest uncertainty-band language labeled "selection uncertainty" (not CI).

### 3.3 v7 Figure 3 — "Holdout workflow"

**Keep, but compress.** It currently takes ~half a page of real estate for what is essentially a 3-row table. The right form: a single-row table with `R_S | R_H` columns, a small inset showing the falsifiable claim Eq. (9), and one sentence of explanation. ~1/4 page.

### 3.4 v7 Figure 4 — "AI procedures and conventional instruments as generators"

**Keep.** This is the figure that prevents the reader from collapsing generators into validators. The four-layer split (hypothesis generation / measurement / construct validation / estimation-inference) is the paper's epistemic backbone.

### 3.5 v7 Figure 5 — "Visual slack profile for DGP A"

**Move to Appendix with the DGP section.** It is useful but does not need main-text real estate.

### 3.6 The new figure (your sketch)

**Recommend Option (C) from §0.1 above**: use the 4-row matrix as the new Figure 1 (replacing the deleted vocabulary chart), relabeled as "Cross-disciplinary landscape of measurement-validation toolkit," and keep v7's Figure 2 as the new Figure 2. Cite Wallach et al. 2025 if you keep the four-layer shape.

---

## 4. The specific questions you asked

### 4.1 "Is it too much of a stretch to claim our methodology can help research scientists write better evals that are 'understandable by humans'?" (dotta thread)

**Your reframe is exactly right.** Defensible only if framed around construct validity — translating black-box LLM evaluation scores into explicit, theory-grounded nomological restrictions `R` that domain experts can inspect and audit. The dotta thread ("there's a missing tool for making evals understandable for humans") is the **motivation**, not the **claim**.

The claim, v8-ready:
> "The framework's contribution to LLM evaluation is to replace implicit, hidden, or proxy-based evaluation with an explicit nomological-network argument over a declared menu of operationalizations: the evaluation is auditable because the menu, restrictions, and thresholds are visible, contestable, and falsifiable on held-out evidence."

Avoid: "we make model interpretability tractable." Avoid: "we help close the loop on agentic science." Both are overclaims the framework cannot back.

### 4.2 "Is it accurate to claim that cvprofiles is the validation layer that unlocks or blocks empirical estimation and inference?"

**Mostly yes, with one important caveat.** The accurate claim:

> "For any empirical application whose regressor is a non-trivial operationalization of a latent construct, the framework is the gate that determines which downstream estimates and inference statements are licensed. For applications whose regressor is directly observable, the framework is trivial (every candidate measure is the construct, `M* = M`, `[L,U]` degenerates to a point)."

The caveat matters. If you claim "cvprofiles gates every analysis," a reviewer will point at prices, administrative counts, and physical measurements where the framework is no-op. Defensible phrasing: **"for any analysis whose regressor is an operationalization of a latent construct, the framework gates downstream estimation and inference."**

This also gives you the right scope language: the framework is **load-bearing for latent constructs** (trust, ideology, polarization, AI exposure, cultural preference profiles, soft skills), and **trivial for directly observed variables**. Most of applied economics and social science sits in the first camp.

### 4.3 "Emphasize that cvprofiles helps close loops in automated social science, but human-owned validity gates are essential to prevent autonomous LLM agents from Goodharting their own validation criteria."

**Yes, with one sharpening.** The defensible claim has three pieces:
1. The framework *can* be embedded in an automated loop (generator → menu expansion → `M*` → `B*` → decision).
2. The framework *does not* — and cannot — prevent an autonomous agent from optimizing against `R` to enter `M*` if the agent has access to the menu and the network. This is a Goodhart failure mode (analogous to a benchmark optimizer gaming a benchmark).
3. The defense against Goodharting is **researcher-owned commitments** (`R, τ_r, M, V, holdout design`) that are *frozen* before the agent sees the data — the freeze/run-id discipline.

The Baumann et al. (2025) "31% incorrect conclusions with prompt paraphrases" finding is the supporting evidence: this is what Goodharting-by-prompt-paraphrase looks like in practice. Cite it explicitly.

### 4.4 "Move the entire Section 7 on synthetic DGP examples to the Appendix and augment with cvprofiles code snippets."

**Strong agree.** This is the single biggest page-count win in your restructure and also the most useful for adoption. Each DGP appendix entry should have: (a) the closed-form population table (unchanged), (b) the cvprofiles Python snippet (runnable against the shipped package), (c) the run_id from `tools/paper_synth_p4p5.py` that reproduces the finite-sample check. This is the right shape for "open implementation."

---

## 5. Things I would NOT change in v8

These are the paper's structural strengths. Keep them.

1. **The "human-owned validation gate" framing.** One of the most quotable lines in the paper. Keep it; do not soften it.
2. **The four-layer epistemic separation** (hypothesis generation / measurement / validation / estimation-inference). It is the right backbone and prevents the reader from collapsing generators into validators.
3. **The plug-in vs population distinction** (`M*` vs `M*_plug-in`, `[L,U]` vs `[L̂,Û]`). Reviewers will probe it; v7 handles it correctly.
4. **The "empty set is a finding" framing.** It is the right epistemic posture and aligns with Dell–Rambachan's call.
5. **The boundary-attribution protocol** (`|margin_m| ≤ κ·SE_m`). This is the right way to handle knife-edge measures and is the package's actual novelty over a naive `[L,U]` reporting.

---

## 6. Open questions for co-author planning

These are not decisions I can make. Surface them explicitly in the v8 planning meeting.

1. **H5 vs IVS for the empirical slot.** v7 §8 names SCA2-vs-persona. `docs/16` §9 names IVS. Which is the v8 flagship?
2. **Chen–Rambachan–Tamer contrast paragraph.** In lit-review or in the methodology section? (My vote: lit-review, because it is part of the positioning story.)
3. **Page-count target.** 12 pp main text? 14 pp? 17 pp? (My vote: 12–14 pp main text + Appendix; this matches Nature/PNAS general-science conventions.)
4. **Submission timing.** Is the IVS Gate B run feasible before the submission deadline? If not, what is the smallest frozen preliminary that can be presented as "engine demonstration, not paper evidence"?
5. **The figure-2 redesign.** Keep v7 Figure 2 + add a landscape Figure 1 (Option C from §0.1)? Or some other arrangement?
6. **Open-weight policy.** v8 §6 must reflect the `docs/16` §9 open-weight constraint: no proprietary APIs, no DPO adapters for paper-reproducible scoring. SCA2 is itself a DPO adapter (D5 NOT reopened for v3); how do you handle this for the historical worked example?

---

## 7. Summary verdict

**The contribution claims are defensible for Nature/PNAS general-science.** The "operational gap-closure" reframe (R1 in §1.1) is the strongest available. The cross-disciplinary synthesis is real and well-positioned.

**The v8 restructure is materially better than v7.** Six sections, with the methodology compressed to ~3 pp main text, DGPs moved to Appendix with code snippets, and the lit-review consolidated into a single deliberate section, is the right shape.

**Three landmines must be defused in v8:**
1. The figure-2/sketch question (§0.1, §3).
2. The H5 → IVS empirical pivot (§0.2).
3. The Dell–Rambachan claim language + Chen–Rambachan–Tamer near-neighbor (§0.3).

**The human-owned validity gate and Goodharting defenses are the paper's rhetorical strengths.** Promote them in v8, do not bury them.

**The framework's defensible scope is "latent constructs," not "all measurement."** Get this language right in v8 §1 and §11/§5.1 and the reviewer probe on scope evaporates.

— Hermes, 2026-08-10
