# Freeze-preserving computation specs — September 2026

Not executed as paper freezes. No θ change. No new R. No LLM re-scoring.

Status 2026-08-31:

| Computation | Status | Artifact |
|---|---|---|
| Number reconciliation | **ran** | `paper/NUMBER_RECONCILIATION.md`, `evals/wvs_gps_two_resolution/preprint_audit/audit.json` |
| §3.5 diagnostics table | **extracted** from existing `coverage.json` | same |
| Comparative falsification (11) | **ran** on frozen slacks | same |
| Leave-one-measure-out | **ran** | same |
| Frozen-M* vs re-formed (cell-exchangeable) | **ran** (independent stream) | same |
| Country-cluster bootstrap + re-demean | **ran** | `preprint_audit/cluster_bootstrap_cells.json` |
| DGP-B Monte Carlo | **not run** — spec below | — |

---

## A. Country-cluster bootstrap (cells)

**Question.** Do Table 3 bands and empty-rep = 0 survive when the resampling unit is the country, with re-demeaning inside each replicate?

**Inputs (committed, not rewritten):**
- `data/cells/patience_llm_extension.csv`, `trust_llm_extension.csv` (undemeaned)
- `networks/{patience,trust}_cells_llm.yaml`
- `betas/{patience,trust}_cells.yaml`

**Procedure:**
1. Parse `iso3` from `unit_id`.
2. Seed `20260814`, `n_boot=1000`.
3. Draw 42 countries with replacement. Stack all cells of each draw. Uniquify `unit_id` by draw index.
4. Country-demean every column that enters R or β inside the replicate (same column list as `demean_cells.py` plus LLM columns).
5. `run_identify(..., include_holdout_verdict=False)` — same admission path as the engine bootstrap.
6. Band = 5th percentile of L and 95th of U over non-empty replicates. Report empty-rep and p̂_m.

**Headline [L,U] stays the freeze.** This is additive.

**Do not** treat a change in the band as a license to move θ.

**Interpretation gate (Augusto):** which of `[0.245, 0.556]`, empty-rep = 0, and the Phi singleton still have a band that does not cross zero / does not empty.

---

## B. DGP-B Monte Carlo (operating characteristics of the band)

**Question.** Under the paper’s own coupling regime, how often does the uncertainty band cover population `[L,U]`, and how does it compare to a Bonferroni union on a fixed menu and to sample-splitting?

**This is the largest remaining methods-journal gap.** It does not require the companion coverage theorem.

**DGP (Appendix B, DGP B):**
- Standardized latent C; convergent criterion V_c with Corr(V_c, C) = 0.80.
- Menu: m_true loading 0.90, m_weak 0.50, plus the other Appendix B columns as distractors if we want the full menu; minimum viable is {m_true, m_weak} plus noise.
- Convergent floor τ such that m_true is near-boundary and m_weak is the β-extreme that couples admission to the lower endpoint (paper: floor 0.40 at the weak measure’s population correlation, or 0.70 which keeps only m_true with +0.02 slack).
- Use **both** of those τ values as two rows.
- n ∈ {50, 480} (country-ish vs cell-ish).
- β(m) = Corr(m, Y) with Corr(Y, C) = 0.60.
- 1000 Monte Carlo samples; per sample, n_boot = 399 or 999 (399 is enough for operating characteristics; 999 if wall-clock allows).
- Seed a single `default_rng` stream, record it.

**Estimands to report (table, not a theorem):**

| Row | n | τ | population [L,U] | band coverage of pop. [L,U] | empty-rep mean | Bonferroni-on-true-M* coverage | 50/50 sample-split coverage | mean band width |
|---|---|---|---|---|---|---|---|---|

Coverage of a *set* = both endpoints of the population interval lie inside the reported band (conservative reading). Also report one-sided endpoint coverage separately.

**Bonferroni comparator:** treat M* as known (oracle population survivors), ordinary percentile CIs on min/max β, Bonferroni over |M*| endpoints.

**Sample-split comparator:** half-sample admits, other half evaluates β on the admitted set; no bootstrap.

**Do not claim:** simultaneous coverage theory, that the band is a confidence set, or that DGP B is the application.

**Engine:** call `run_identify` + `run_bootstrap` / coverage helper. Do not reimplement slacks.

**Output:** `evals/synthetic/dgp_b_band_mc.json` + a short appendix-ready table. Not a freeze. Not a package version bump.

**Owner:** agent. **Augusto signs** whether the table goes in Appendix A.5 or a new App K.

---

## C. What not to spec this month

- Prompt paraphrase / third model family (new freeze).
- New cell holdout implications (new R, circularity on this sample).
- Precision layer in the engine.
- Item-level CFA.
- Causal composition (12) as a real application.

---

## D. Already answered without new scoring

Comparative falsification on frozen cell slacks:

- Patience: p̂_S = 1, best-β = 1, best-anchor = 1; random-k mean 0.49; only 5.3% of random k=3 subsets match p̂_S. The *level* of p̂ is vacuous (Pearson/Spearman twins); the comparison to random is not empty.
- Trust: p̂_S = 1 on Phi; best-β (composite) p̂ = 0; random-k=1 mean 0.13. Validity-guided selection and criterion-fit pull apart.

Frozen vs re-formed cell-exchangeable bands are nearly the same width. Coupling shows up as p̂(Q13) = 0.83, not as a large frozen/reformed gap.

**Cluster bootstrap (ran 2026-08-31):** see `preprint_audit/cluster_bootstrap_cells.json`.

| Profile | Paper cell-exchangeable band | Country-cluster + re-demean | Empty-rep | p̂ |
|---|---|---|---:|---|
| Patience cells | [0.179, 0.614] | [0.174, 0.622] | 0.000 | Q13 0.74 (was 0.83); Llama/Phi 1.0 |
| Trust cells | [−0.382, −0.240] | **[−0.400, 0.195] crosses 0** | 0.001 | Phi 0.997; Llama 0.079 |

Patience headline is stable to clustering. The trust “entirely negative coverage” sentence is not. That is Augusto’s interpretation gate, not a silent paper edit.
