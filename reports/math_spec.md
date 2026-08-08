# cvprofiles — Mathematical Implementation Spec: Coupled Inference, Holdout Workflow, Evaluators, v3.0.0 Gate

**Author:** Hermes aggregation (math-spec agent failed twice on provider timeouts; this half written directly by the parent agent from the grounded sources: METHODOLOGY.md, AGENTS.md, `src/cvprofiles/identify/slacks.py`, `identify/pipeline.py`, `inference/bootstrap.py`, `inference/theta_grid.py`, `inference/delta_grid.py`, `freeze.py`, `schemas/network.py`, docs/16, docs/17, plus the scan report's file:line references).
**Consumer:** cvprofiles lead engineer agent (v3.0.0 scheduling).
**Driver:** Nature/PNAS-level paper on valid estimation of latent constructs with cultural applications (SCA2 project). Paper needs: (1) inference layer whose coverage accounts for the coupling between admissibility classification and β; (2) pre-registered holdout-restriction workflow (the paper's falsifiable core); (3) evaluators for a deep country-level trust study (small n); (4) a v3.0.0 gate whose checkpoint is the paper.

---

## §1. Formal model recap (package notation — METHODOLOGY.md §9)

- Construct $C$ (researcher-defined prose), finite menu $\mathcal{M}=\{m_1,\dots,m_J\}$ (score columns), auxiliaries $V$, outcome $y$.
- Nomological network $\mathcal{R}$: restrictions $r$ with thresholds $\theta_r$, each a population moment inequality
  $$\mathbb{E}[g_r(m(X),V;\theta_r)] \ge 0,\qquad r\in\mathcal{R}.$$
- Sample slack $s_r(m)$ (slacks.py): satisfied when $s_r(m)\ge-\delta$, $\delta\ge0$ default 0.
- Admissible set $\mathcal{M}^*=\{m\in\mathcal{M}: s_r(m)\ge-\delta\ \forall r\}$ (identify/pipeline.py).
- Target functional $\beta(m)$ (beta_fn.py: `corr_y`, `ols_coef`).
- Construct-identified range $[L,U]=\left[\min_{m\in\mathcal{M}^*}\beta(m),\ \max_{m\in\mathcal{M}^*}\beta(m)\right]$ — survivors only (AGENTS.md:22).
- Freeze/run-id preimage (freeze.py:17-20): `beta_hash, config, delta, n_boot, network_hash, package_version, schema_version, scores_hash, seed`. Excluded: `created_at`, paths, hostnames, grids, anchors (freeze.py:22-23). `package_version` is in the preimage (docs/12 M1).

## §2. The coupled inference layer (centerpiece)

### 2a. Problem statement

All objects are sample estimates: $\hat{s}_r(m)$, $\hat{\mathcal{M}}^*=\{m:\hat{s}_r(m)\ge-\delta\ \forall r\}$, $\hat\beta(m)$, and the plug-in range $[\hat L,\hat U]=[\min_{m\in\hat{\mathcal{M}}^*}\hat\beta(m),\ \max_{m\in\hat{\mathcal{M}}^*}\hat\beta(m)]$. Two sources of sampling uncertainty enter:
1. **Admissibility classification**: $\hat{\mathcal{M}}^*$ is an estimated set; measures near the boundary ($\hat{s}_r(m)\approx-\delta$) flip in and out across samples.
2. **Endpoint estimation**: $\hat\beta(m)$ is noisy for every candidate.

These are **coupled**: the measures determining the plug-in endpoints are themselves random, and a measure that is (a) near the admissibility boundary and (b) an extreme $\hat\beta$ contributes both selection error and endpoint error. A confidence region for $[L,U]$ must cover the joint distribution of (i) the slack estimators that determine $\hat{\mathcal{M}}^*$ and (ii) the $\beta$ estimators, conditional on a correct admission decision. This is exactly the coupling Dell–Rambachan (NBER 2026 Methods Lecture, `dell3.pdf`, "Construct Validity: Credibility When Measurement Is Cheap") flag: *"uncertainty in the estimated moment inequalities that determine which measures are classified as admissible… coupled when the measures determining the plug-in endpoints are also near the admissibility boundary. Estimation is beyond today's scope."* The paper's abstract commits to "inference that remains valid despite the data-dependent screening step" — this layer is that promise.

### 2b. Candidate approaches (pros/cons in THIS codebase)

**(i) Units-resampling bootstrap recomputing slacks + $\hat{\mathcal{M}}^*$ + $[L,U]$ per replicate — promoted from diagnostic to coverage claim.**
The existing `inference/bootstrap.py` already does most of this: units-only resampling, menu fixed, seeded `default_rng`, recomputes slacks and $\hat{\mathcal{M}}^*$ per replicate, counts all-empty replicates, percentile band over non-empty replicates; headline unchanged (bootstrap.py:1-18, 59-147; H5: band [0.174,0.752], 17.5% empty replicates). What is missing: a coverage *statement*, boundary-case reporting, and honest limits.
- Pros: minimal new machinery; the distribution of the estimator is already simulated; empty-replicate rate is a natural, honest output; deterministic (seeded).
- Cons: min/max over an estimated set is a non-smooth functional — the percentile method is a defensible *uncertainty summary*, not a formal CI under arbitrary dependence; pointwise per-side quantiles do not give joint coverage of ($L$,$U$) simultaneously; small-n (n=35 countries) makes bootstrap bands coarse. Bootstrap for extrema is known to be fragile when gaps between candidate $\beta$'s vanish.
- Implementation difficulty: **low–medium** (relabeling + joint-coverage math + boundary attribution + reporting).

**(ii) Imbens–Manski/Stoye endpoint CIs per admissible measure, union/max adjustment.**
For each $m\in\hat{\mathcal{M}}^*$ build a $(1-\alpha)$ CI for $\beta(m)$ (normal approx or BCa), then form the envelope by taking the max half-width: $[\min_m\hat\beta(m)-\max_m hw_m,\ \max_m\hat\beta(m)+\max_m hw_m]$, with Bonferroni over $|\hat{\mathcal{M}}^*|$ if strict simultaneous coverage is claimed.
- Pros: transparent, per-measure diagnostics; standard theory for each $\beta(m)$.
- Cons: does not cover the selection step (admission decision itself is treated as fixed); Bonferroni over a random set size is conservative; with many near-boundary measures the interval is wide exactly when informative.
- Implementation difficulty: medium (new per-measure CI code + envelope logic).

**(iii) Sample splitting to decorrelate admission and endpoints.**
Split units; estimate $\hat{\mathcal{M}}^*$ on half 1; estimate $\beta(m)$ on half 2 conditional on the split-1 admission set. Conditional independence gives clean per-measure inference; union over the (fixed, split-1-determined) set.
- Pros: cleanest theory; directly addresses the coupling.
- Cons: halves effective n — brutal for the trust study (n=35 → ~17 per half); wastes scarce country-level data. Use as a robustness check, not the primary.
- Implementation difficulty: medium (split plumbing through SCORE/RESTRICT/IDENTIFY).

**(iv) Conservative projection/union (as (ii), stated as a cross-check).**
Same as (ii) without claiming simultaneity: report the per-measure CI union as an outer bound.

### 2c. Recommendation (minimal auditable default + cross-check)

**Primary — bootstrap coverage band (approach i), promoted from diagnostic to a MANDATORY reporting layer (D1 decided 2026-08-07: additive-but-mandatory; headline [L,U] remains min/max over B*), with:**
1. Per-side quantiles: $L_q = q_{\alpha/2}(\{L^{(b)}\})$, $U_q = q_{1-\alpha/2}(\{U^{(b)}\})$ over non-empty replicates (existing percentile band, $\alpha$ default 0.10).
2. **Joint-coverage statement**: report the band as covering the pair with at least $1-\alpha$ under the Bonferroni reading (each side at $\alpha/2$) — documented as conservative. Optionally report the empirical joint coverage of the *replicate* band (share of replicates where $[L^{(b)},U^{(b)}]\supseteq[\text{point-estimate }L,\hat U]$... define precisely: the share of replicates whose band contains the full-sample band) as a diagnostic.
3. **Empty-replicate rate** reported explicitly (already counted; H5: 17.5%). The headline coverage statement is **conditional on non-empty** $\hat{\mathcal{M}}^*$; the empty rate is a headline finding, not a footnote.
4. **Boundary attribution**: for each measure, report $\min_r \hat{s}_r(m)$ and the slack margin $\hat{s}_r(m)+\delta$ in SE units; flag measures with margin $\le \kappa\cdot \mathrm{SE}$ (default $\kappa=2$) as *boundary measures* — these drive the coupling. The band's width should be read together with the boundary set.
5. **Honest labeling**: output is an "uncertainty band", not a formal CI under arbitrary dependence; the METHODOLOGY inference-stance section documents the non-smoothness caveat.

**Cross-check — conservative projection (approach ii/iv)**: per-admissible-measure CIs (normal or BCa, $\alpha/|\hat{\mathcal{M}}^*|$ Bonferroni) unioned around $[\hat L,\hat U]$. If the projection interval is much wider than the bootstrap band, the coupling is material — report both.

**Module path**: `src/cvprofiles/inference/coverage.py` (new), or extend `bootstrap.py` with a `CoverageResult`. Follow existing dataclass conventions (`IdentifyResult` style). New dataclass:
```python
@dataclass(frozen=True)
class CoverageResult:
    method: str            # "bootstrap_band" | "conservative_projection"
    alpha: float
    band_l: float | None   # None when all replicates empty
    band_u: float | None
    empty_rate: float      # share of replicates with empty M*
    boundary_measures: tuple[BoundaryFlag, ...]   # (measure, restriction, slack, slack_se, margin_se)
    cross_check: ConservativeBand | None
```
**CLI/report surface**: `cvprofiles run --inference coverage --alpha 0.1` (or a dedicated `cvprofiles coverage` verb); REPORT gains a "Coverage" section in JSON and HTML payloads. Exit code stays 0 on empty $\hat{\mathcal{M}}^*$ (empty set is a finding).

**Freeze/governance consequences — FLAG**: if the coverage band becomes the *headline* object (rather than additive like today's bootstrap), then:
- The freeze preimage must grow: coverage params (`alpha`, `kappa`, and `n_boot`/`seed` if not already) must enter `freeze.py` keys (currently `n_boot` IS in the preimage but bootstrap is excluded as a layer; the layer flag semantics change).
- `docs/16` requires a dated amendment (§8-pattern, docs/16:21: "Silence is not consent") — **Augusto's decision** (AGENTS.md:31-35).
- METHODOLOGY.md §5 inference stance and ARCHITECTURE.md module map must be updated.
- Version discipline: `package_version` is in the run-id preimage, so the semantics change is version-visible (good).

### 2d. Pseudocode

```
def coverage_band(scores, network, beta, seed, n_boot, alpha=0.10, kappa=2.0):
    rng = np.random.default_rng(seed)
    Ls, Us, empties = [], [], 0
    units = scores.unit_ids
    for b in range(n_boot):
        u_b = rng.choice(units, size=len(units), replace=True)
        slacks_b = compute_slacks(scores.loc[u_b], network)      # per measure × restriction
        Mstar_b = {m for m in network.menu
                   if all(slacks_b[m, r] >= -delta for r in network.restrictions)}
        if Mstar_b:
            vals = [beta_fn(beta, scores.loc[u_b], m) for m in Mstar_b]
            Ls.append(min(vals)); Us.append(max(vals))
        else:
            empties += 1
    if not Ls:
        return CoverageResult(empty_rate=1.0, band_l=None, band_u=None, ...)
    return CoverageResult(
        band_l=quantile(Ls, alpha/2), band_u=quantile(Us, 1 - alpha/2),
        empty_rate=empties/n_boot,
        boundary_measures=flag_boundary(slacks, slack_se, delta, kappa))
```
TDD first (RED→GREEN, AGENTS.md:76): fixtures = small synthetic DGP with a measure exactly at the boundary; assert band contains truth at nominal rate in Monte Carlo; assert empty-rate counting; assert determinism under fixed seed.

## §3. Holdout-restriction workflow (the paper's falsifiable core)

**Purpose**: the paper's headline claim is that *selection guided by construct validity predicts validity evidence it was not optimized to satisfy*. That requires a declared split: build $\hat{\mathcal{M}}^*$ on **selection restrictions** $R_{\text{select}}$, then evaluate survivors on **holdout restrictions** $R_{\text{holdout}}$ that never entered selection. Survivors failing holdout = scientific finding (the screen's honesty), not an error.

**Schema addition** (`schemas/network.py`): each restriction gains an optional `stage` field, `enum("select","holdout")`, default `"select"`. Backward compatibility: existing networks (all `select`) behave identically. `network_hash` necessarily changes (field added) — acceptable inside the v3.0.0 major bump; document in docs/12.

**Pipeline behavior** (identify/pipeline.py):
1. Bind both stages at RESTRICT.
2. IDENTIFY computes slacks for ALL restrictions but admits on $R_{\text{select}}$ only: $\hat{\mathcal{M}}^*_{\text{select}}=\{m: \hat{s}_r(m)\ge-\delta\ \forall r\in R_{\text{select}}\}$.
3. REPORT emits three blocks: (a) selection result $\hat{\mathcal{M}}^*_{\text{select}}$ and $[L,U]_{\text{select}}$; (b) holdout slacks for each survivor (with anchors); (c) **holdout verdict**: survivors passing all holdout restrictions; survivors failing any (listed with the failing restriction and slack) — a named output, not an error.
4. Empty $\hat{\mathcal{M}}^*_{\text{select}}$ → exit 0 with the finding.

**Freeze/docs**: both stage sets and the stage flags enter `network_hash` (preimage). docs/16 amendment required (it changes what "the stated network" means for the headline run — docs/16:21; Augusto's decision). The paper's pre-registration narrative maps to: network + anchors + stage split frozen BEFORE holdout data are consulted (the `pre_data: true` anchor discipline already exists, anchors/pipeline.py).

## §4. New evaluator specs for the deep trust study

Registry pattern (METHODOLOGY.md:51; docs/12 D3-D5): fixture → semantics lock → schema type → evaluator → fail-loud default. Proposed additions (keep the registry small — project philosophy):

1. **`monotone_rank`** (closes the named `monotone_*` gap, METHODOLOGY.md:51) — monotone-in-continuous-covariate, e.g. "trust is increasing in income":
   - Semantics: $\mathrm{slack} = \mathrm{sign}\cdot \mathrm{Spearman}(m, V_{\text{cont}}) - \theta \ge -\delta$.
   - Schema: `{type: monotone_rank, params: {ref: <continuous covariate column>, sign: 1|-1, theta: float}}`.
   - Implementation: reuse rank-correlation code path (rank_agree already computes Spearman, slacks.py:102-108); new evaluator in slacks.py + schema entry + fixture.
   - Why rank not OLS: thin, monotonicity-invariant, no distributional assumptions; matches "the economics is full of monotone structure" (METHODOLOGY.md:49).
2. **`corr_zero`** (discriminant validity, MTMM-style) — "measure must NOT track a distinct construct", e.g. institutional-trust measure must not track rule-of-law beyond a cap:
   - Semantics: $\mathrm{slack} = \theta - |\mathrm{Corr}(m,V)| \ge -\delta$ (two-sided moment inequality; current registry only supports one-sided ≥).
   - Note: the registry's one-sided `corr_sign` with sign=−1 can express "negatively associated" but NOT "|corr| small". The deep trust study's discriminant restrictions need the two-sided form.
   - Schema: `{type: corr_zero, params: {ref: <column>, theta: float}}`.
3. **Cross-country / multi-group invariance**: no new evaluator needed — declare multiple `mean_order` restrictions (one per group pair) and/or `rank_agree` with a reference; document the pattern in METHODOLOGY. Keep registry minimal.
4. **`stability`** (schema-only today, slacks.py:110-113): split-half reliability — natural fixture is the deep trust study (country halves or question halves). Slack = split-half correlation − θ. **Optional / lower priority**: ship only if the paper's evidence profile demands a reliability surface; otherwise leave fail-loud.

## §5. v3.0.0 gate criteria (mapped to paper needs)

| # | Criterion | Extends / mirrors | Paper need |
|---|---|---|---|
| 1 | **Coverage layer implemented + TDD green** (RED→GREEN), semantics locked in docs/12 dated entry; decision additive-vs-headline recorded | bootstrap.py, docs/12 D1-D5 pattern | Abstract's "inference that remains valid despite the data-dependent screening step"; §2 framework's construct-identified range |
| 2 | **Holdout workflow** ($R_{\text{select}}$/$R_{\text{holdout}}$) implemented + tested; deep-trust network frozen with anchors and stage split — **Augusto-authored** (AGENTS.md:37: agents do not author empirical networks) | schemas/network.py, identify/pipeline.py, docs/16 amendment (§8-pattern) | The falsifiable core: "selection guided by construct validity predicts held-out validity evidence" |
| 3 | New evaluators `monotone_rank` + `corr_zero` with fixtures, semantics locks | slacks.py, schemas/network.py, METHODOLOGY registry table | Deep trust study restrictions (income gradients; discriminant/MTMM) |
| 4 | **Battery green**: ruff, mypy strict, pytest (≥222), `verify_h5_trust.py` + `verify_v11_protocol_synth_mc50.py` exit 0, `git diff --check`, `v0.1` peel intact, import-graph (no LLM) | AGENTS.md:93-99, ci.yml | Release integrity |
| 5 | **Docs**: METHODOLOGY (registry + inference stance), ARCHITECTURE (module map), ROADMAP (v3 box), PROJECT_MANIFEST, docs/12 dated entries, docs/13 evidence rows (authorized only), **docs/16 amendment** (dated, §8-pattern) | docs governance | Auditability; reviewers' reproducibility |
| 6 | **Version discipline**: atomic bump `2.0.1a1 → 3.0.0`, golden refresh, all literals (pyproject, `__init__`, uv.lock, tests, CI, README) | docs/12:422,807-809; tools/refresh_mini_golden.py | run-id stability (package_version in preimage) |
| 7 | **Augusto's explicit release decision**; Augusto executes the PyPI upload (token never in agent session) | AGENTS.md:35,80; docs/16:102; docs/12:813-815 | Governance |
| 8 | **Paper checkpoint**: the deep-trust run's numbers enter the paper only after frozen run + independent audit (verify pattern) + dated paper lock — mirroring the n=35 checkpoint → paper-lock flow (docs/16:133; docs/13:393-421) | docs/17 run-gating | The paper's headline evidence |

## §6. Risks & open questions

1. **Boundary coupling**: measures near the $\hat{s}_r(m)\approx-\delta$ boundary flip admission across replicates; the band is widest exactly when it is most informative. Mitigation: mandatory boundary-attribution block (§2c.4); report band + boundary set together.
2. **Empty $\hat{\mathcal{M}}^*$ coverage**: coverage statements are conditional on non-empty; the empty rate is a finding. In H5, 17.5% of replicates were empty — a reviewer will ask what the band means when 1-in-6 samples admit nothing. Answer honestly: the empty rate is part of the validity verdict.
3. **δ (tolerance) interacts with coverage**: δ>0 admits more measures → wider sets and different coupling. Headline coverage at δ=0 (default); δ-grid remains an additive sensitivity surface; document that coverage is δ-conditional.
4. **Multiple testing across evaluators**: each restriction is a descriptive screening test, not a p-value. No family-wise control; the paper must not present per-restriction pass/fail as hypothesis tests.
5. **Small-n bootstrap (country-level units, n≈35)**: coarse; per-side quantiles from 35-unit resamples are lumpy. Mitigations: report empty rate + boundary set as primary, band as secondary; consider m-out-of-n bootstrap as a future robustness item (document, don't ship).
6. **Determinism**: all new RNG streams seeded; coverage params enter the freeze preimage if headline (freeze.py change); test determinism under fixed seed.
7. **Governance risk**: ANY change to the headline range or freeze preimage requires the dated docs/16 amendment and METHODOLOGY inference-stance update — Augusto's decision, not the engineer's. Sequence the amendment BEFORE implementation so the semantics lock precedes code (docs/12 D-series precedent).
8. **D1 DECIDED (2026-08-07, Augusto): additive-but-mandatory** — the coverage band is a required reporting layer, not the headline; no freeze-preimage change; docs/16 amendment + METHODOLOGY inference-stance update still required to mandate the layer. Headline status deferred to the methods paper (paper A).

## §7. Gate A math decisions — dated note (2026-08-07, T26 exit criterion)

**Authority:** Augusto signed the full Gate A bundle 2026-08-07 ("address all the tasks in Gate A as you proposed, everything should stay open-weight or easily interpretable"); recorded in `docs/16` §9 (dated amendment) and `docs/12` (decision entry, same date).

- **D3 — β-functional.** `map_distance` (2D Euclidean distance on the IW cultural map) approved as a v3 β-registry extension. Loadings provenance: **reuse Tao et al.'s published human PCA loadings verbatim**, including the PC2′ = 1.61·PC2 − 0.01 rescaling (**PROVISIONAL — to be verified against Tao et al.'s actual text at the T21 transcription audit, hard Gate B item**). **Fresh empirical PCA fit NOT authorized** (robustness appendix only if later reopened). **Preimage carve-out (explicit):** the registry extension changes `beta_hash` by design inside the v3 major bump; governed by `docs/16` §9, never silent.
- **D7 — Holdout semantics.** The paper's falsifiable core is the **country-level units-split**: select/admit on train-country scores, verdict on held-out-country scores (same frozen network + same β). The restriction-level `stage: select|holdout` split ships as WP2 machinery (same units; R_select predicts R_holdout compliance). Both implementable; D7 fixes the core; T23 specifies the units-split composition.
- **D4 — Evaluator fit note.** `monotone_rank` (sign·Spearman(m, V_cont) − θ) and `corr_zero` (θ − |Corr(m, V)|, two-sided) approved as registry positions. IW axes are PCA axes, **not** monotone-in-covariate restrictions; `monotone_rank` is used by the IVS lane only if the network restricts on a continuous covariate (e.g. self-expression ↑ with GDP per capita).

Consequences for this spec: §2 (coverage) unchanged and additive (D1); §3 holdout section is WP2 machinery; the units-split composition (D7 core) is specified at T23 under the §9 amendment.
