# Position Paper v8 — Final Delivery Notes (2026-08-10)

**Manuscript:** `~/Desktop/Github_Repositories/SCA2_PofW/misc/position_paper/position_paper_v8.tex|.pdf` (committed to `EconLLM-Lab/SCA2_PofW`).
**Status:** v8 drafted, built (19 pp), verified against the finalized outline and the frozen cvprofiles 3.0.0 application. Awaiting Augusto's read before Nature/PNAS roadmap discussion.

---

## 1. Approved framing (locked)

- **Title:** *Measuring What We Mean: Construct Validity When Measures Are Cheap* — subtitle: "A position paper on **construct-identified inference** in the age of AI."
- **Center of gravity (per Codex's critique, adopted):** cheap measurement = the motivating technological shock; the contribution = **construct-identified inference**: validate first (R(C) → M\*), propagate second (B\* = image of β over M\*).
- **Conservative priority:** construct validity, multiverses, partial identification all have prior literatures; novelty = their **ordering and composition** + falsifiable selection rule + released implementation. No "we invented X" claims.
- **Application posture:** WVS/GPS patience = **initial demonstration / proof of work**, not decisive validation. §6.5 "The decisive experiments" locks the empirical agenda (consequentiality; powered holdout falsification vs baselines; independence of validity evidence; replication across constructs; threshold/menu provenance).
- **Status box:** cvprofiles **3.0.0 released on PyPI (2026-08-10)**, used as instrument; package development parallel; LLM adapters = upstream generators, never engine features.

## 2. Decisions (Augusto, 2026-08-10)

1. Report the **7-measure menu as frozen** (no SCA2 arm; SCA appears once as a generator family).
2. **Codex's Appendix F (v7→v8 change map) not adopted** in-paper; technical gaps filled instead (Appendices A–E).
3. **"Construct-identified inference"** adopted as the methodological name.
4. No further cvprofiles tests/changes pending.

## 3. Deterministic citation verification (all 49 entries)

- **CRT 2026 CONFIRMED 3-author:** Chen, Rambachan & Tamer, "Partial Identification from LLM Prompts," arXiv:2606.15031v2 (v2 24 Jun 2026) — verified via arXiv abs API. (Codex's draft bib dropped Rambachan; the three-author cite stands.)
- All 17 arXiv IDs verified live (title match); journal works verified via Crossref with **5 DOI corrections** (Imbens–Manski `…00555.x`; Stoye `10.3982/ecta7347`; Butler `10.1111/jeea.12178`; Cronbach–Meehl `10.1037/h0040957`; Campbell–Fiske `10.1037/h0046016`).
- Wallach et al. 2025 = ICML 2025 position paper, arXiv:2411.10939. Hanel–Zarzeczna 2023 journal version = RBB 13(3), DOI `10.1080/2153599X.2022.2070259`.
- URL liveness: NBER lecture series + dell4.pdf, NBER WPs 31122/32381/35110, HAI 2026, Truong PDF, **PyPI cvprofiles = 3.0.0** — all 200.
- Final integrity: 49 cited keys = 49 bib entries, zero gaps. Full report: `/tmp/citation_verify_report2.json` (script `/tmp/verify_citations2.py`).

## 4. Frozen-number contract (verified against frozen run)

- Headline `M*_select = {m_gps_patience, m_prompt_a}`, `[L,U] = [0.328, 0.402]` (= pooled standardized βs with q275_mean control, recomputed and matching the allow-listed summary to the decimal), random-null **100th percentile** (500 draws, k 1–4); pooled robust set ∅ (power-limited posture a).
- Pooled β table: gps +0.4025, prompt_a +0.3275, prompt_b +0.3739, q13 −0.1660, q14 −0.1948, composite −0.2187, noise +0.0199.
- Network: conv_edu θ=0.20 (select) / mono_edu θ=0.15 (holdout) / disc_risk θ=0.35 (select, re-anchored 0.30→0.35 pre-freeze; Dohmen 2011 + Falk 2018 Table IV + Hanushek 2022 cited in the footnote). β = ols_coef log_gdp_pc ctrl q275_mean. n=41, K=5, seed 20260810, split_seed 17, pkg 3.0.0.

## 5. Build & verification record

- Single-file `.tex` (v8 pattern, like v3–v7), 2-pass pdflatex: **exit 0, 0 errors, 0 undefined refs, 0 warnings**; one 2.2pt overfull (invisible).
- Page budget: main text pp. 1–12 (≤12 ✓), appendices 13–16, references 17–19.
- Outline checklist 19/19; banned-content audit clean (no H5/IVS; "Trust" only in the §6.5 replication clause and §4 phrase; SCA once as generator family).
- Figures: Figure 1 (systems view, from sketch) + Figure 2 (core objects; M\* own node, downstream lane, dotted diagnostics, freeze pin) — TikZ, built clean.

## 6. Open items (empirical, per §6.5)

Consequentiality (M\* changes B\* vs multiverse) · powered holdout falsification vs random/anchor/predictive baselines · independent anchors + preregistered prompt search · replication across GPS dimensions/trust/risk · θ-grid and menu-perturbation provenance. These are the "decisive experiments" the paper commits to — next session topic (Nature/PNAS roadmap).

— Hermes, 2026-08-10
