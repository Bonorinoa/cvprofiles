# cvprofiles Engineering Report — Paper-Driven Plan to v3.0.0

**For:** cvprofiles lead engineer agent · **From:** Hermes aggregation (2026-08-07)
**Inputs:** grounded package scan (`/tmp/pp_v4/cvprofiles_scan.md`), mathematical implementation spec (`/tmp/pp_v4/math_spec.md`)
**Driver:** Nature/PNAS-level position paper on valid estimation of latent constructs with cultural applications (SCA2 project). **The paper is the package's next real-world target and the v3.0.0 checkpoint.** All file:line references are grounded in the repo at `~/Hermes/Projects/cvprofiles`.

---

## 0. Executive summary

1. The package is in strong shape: v2.0.0 on PyPI (2026-08-06), B4 methodology locked, 222-test battery green, H5 Trust n=35 checkpoint approved as *preliminary paper-facing evidence* ([L,U]=[0.371,0.624], M*={general, in-group}).
2. The paper's headline needs three things that **do not exist yet** (verified: 0 hits): (a) a **coupled inference layer** giving valid coverage for [L,U] under admissibility-classification uncertainty; (b) a **holdout-restriction workflow** (R_select/R_holdout) — the paper's falsifiable core; (c) two small **evaluators** (`monotone_rank`, `corr_zero`) for the deep trust study.
3. All three are **engine changes to the headline path** → each requires a dated `docs/16` amendment and is **Augusto's decision** (AGENTS.md:31-35), not the engineer's. Sequence: amendments FIRST (semantics lock), then TDD implementation.
4. The current bootstrap (inference/bootstrap.py) already recomputes M* and [L,U] per replicate — the coverage layer is closer to promotion+relabeling+honest reporting than to new theory (though the min/max non-smoothness caveat must be documented).
5. Two doc tensions to fix before paper runs: `docs/17:40` still says WGI `rq` (manifest says `rl`, docs/12 records the fix); `docs/16:5` package baseline `1.1.0a1` is stale (now `2.0.1a1`; package_version is in the run-id preimage).

---

## 1. Package state (condensed, grounded)

| Aspect | State | Source |
|---|---|---|
| Version | `2.0.1a1` dev; **2.0.0 on PyPI** (2026-08-06, tag `v2.0.0`@`6abb6e4`); `v1.1.0`@`fce31c8`; `v0.1` immovable @`fb62b48` | pyproject.toml:3; AGENTS.md:26,43-44 |
| Engine | SCORE → RESTRICT → IDENTIFY → REPORT; deterministic, model-free (no LLM, CI-enforced) | AGENTS.md:10-16,20; ci.yml:52-78 |
| Restrictions registry | `corr_min`, `corr_sign`, `mean_order`, `rank_agree` implemented (slacks.py:59-108); `stability` schema-only fail-loud; **`monotone_*` named gap** (METHODOLOGY.md:51) | slacks.py; schemas/network.py:11-17 |
| Beta functionals | `corr_y`, `ols_coef` implemented; `diff_means` schema-only | beta_fn.py:53-73 |
| Inference diagnostics | bootstrap / θ-grid / δ-grid / θ-anchor audit — all **additive, excluded from freeze preimage** | inference/*; freeze.py:22-23 |
| Freeze contract | run-id preimage = beta_hash, config, delta, n_boot, network_hash, package_version, schema_version, scores_hash, seed | freeze.py:17-20 |
| Tests/CI | 27 test files, 169 test fns, last logged 222 passed (docs/12:936); ruff + mypy strict + pytest + import-graph + wheel-smoke | ci.yml:13-143 |
| H5 Trust (n=35) | M*={m_trust_general, m_trust_in_group}, [L,U]=[0.371,0.624], FA=0, cold H4; θ-grid empties λ≥1.5; bootstrap band [0.174,0.752], 17.5% empty replicates | reports/summaries/h5_trust_evidence_summary.json; docs/16:133 |
| Evals not usable as paper evidence | `evals/realworld/{spam_validity, calhousing_validity}` = intermediate, NOT H5 (AGENTS.md:49) | spam/calhousing READMEs |
| Docs governance | METHODOLOGY B4 locked; docs/16 `protocol-v1-synth-provisional`; §8 amendment (2026-08-04) authorizes H5 Trust eval only; docs/17 H5 design locked, run-gated | METHODOLOGY.md:3; docs/16:3,127-135 |

**Authority:** Augusto owns construct, unit/universe, scores, menu, R/anchors/θ/δ/β, paper claims, release posture, tag, PyPI (AGENTS.md:31-35). Agents author oracle networks only for synthetic DGPs; no inventing empirical networks (AGENTS.md:37). Convention 6: no push/tag/publish without explicit user decision (AGENTS.md:80).

---

## 2. Work packages (scope → files → governance)

### WP1 — Coupled inference layer  *(paper: abstract's "inference that remains valid despite the data-dependent screening step"; §2 construct-identified range)*
- **Primary (minimal auditable default):** promote the units-bootstrap (already recomputes slacks+M*+[L,U] per replicate) to a **coverage band** with: per-side quantiles at α/2 (α default 0.10), Bonferroni-joint labeling, **empty-replicate rate as a headline finding**, **boundary attribution** (measures with slack margin ≤ κ·SE, κ=2, flagged), and honest "uncertainty band, not formal CI" language (min/max non-smoothness caveat).
- **Cross-check:** conservative projection — per-admissible-measure CIs (normal/BCa, Bonferroni over |M*|) unioned around [L̂,Û].
- **Files:** new `src/cvprofiles/inference/coverage.py` (or extend bootstrap.py); `CoverageResult` dataclass (frozen, follows IdentifyResult conventions); CLI `--inference coverage --alpha`; REPORT gains Coverage section; freeze preimage grows if headline.
- **Governance: ✅ D1 DECIDED (2026-08-07, Augusto): additive-but-mandatory.** The coverage band is a REQUIRED reporting layer for v3.0.0, not the headline [L,U] (headline remains min/max over B*). This preserves the freeze-preimage contract and the docs/16 method spine; a dated docs/16 amendment + METHODOLOGY §5 inference-stance update are still required to mandate the layer, but no freeze-preimage change. Headline status is deferred to the methods paper (paper A). The paper cites it as "a bootstrap uncertainty band with explicit boundary attribution."
- **Pseudocode + TDD plan:** math_spec §2d.

### WP2 — Holdout-restriction workflow  *(paper: the falsifiable core — "selection guided by construct validity predicts held-out validity evidence")*
- **Schema:** restriction-level `stage: select|holdout` (default select; backward compatible). **Pipeline:** admit on R_select only; report three blocks (selection result; holdout slacks per survivor; **holdout verdict** — survivors failing holdout are named findings, not errors).
- **Files:** schemas/network.py, identify/pipeline.py, report/pipeline.py, METHODOLOGY registry/notation.
- **Governance:** docs/16 amendment (changes what "the stated network" means); the stage split + anchors frozen pre-data is the paper's pre-registration story (the `pre_data: true` anchor discipline already exists).

### WP3 — Evaluators for the deep trust study
- **`monotone_rank`** (closes METHODOLOGY.md:51 gap): slack = sign·Spearman(m, V_cont) − θ. Reuses rank_agree's Spearman path.
- **`corr_zero`** (discriminant/MTMM): slack = θ − |Corr(m,V)| — the registry currently only supports one-sided ≥; two-sided form is required for "measure must NOT track a distinct construct".
- **Multi-group invariance:** no new evaluator — compose `mean_order` per group pair + `rank_agree`; document the pattern.
- **`stability`** (schema-only): split-half; ship only if the paper's evidence profile demands a reliability surface.
- Registry pattern: fixture → semantics lock (docs/12 dated) → schema → evaluator → fail-loud.

### WP4 — Deep trust study (the paper's flagship application)
- Extend the H5 Trust design (docs/17) to a **frozen multi-restriction network**: GPS-trust convergence, rule-of-law, Gini, income gradients (`monotone_rank`), discriminant (`corr_zero` vs a distinct construct), known-groups by region, plus a **pre-registered holdout set** (WP2).
- **Augusto-authored** network/anchors/θ (AGENTS.md:37). Run gated: frozen scores + pinned seed + version + independent audit + Augusto's run decision (docs/17:118 pattern).
- Paper checkpoint discipline: numbers enter the paper only after frozen run + `verify_h5_trust.py`-style audit + dated paper lock (mirror docs/16:133 n=35 flow).

### WP5 — Docs, version, release
- Fix the two doc tensions (docs/17 `rq`→`rl`; docs/16 baseline re-baseline to 2.0.1a1).
- METHODOLOGY (registry + inference stance), ARCHITECTURE (module map), ROADMAP (v3 box — currently "to be drafted", ROADMAP.md:32), PROJECT_MANIFEST, docs/12 dated entries, docs/13 evidence rows (authorized only).
- **v3.0.0 gate** (see §4) and atomic bump `2.0.1a1 → 3.0.0` with golden refresh; PyPI upload by Augusto only (precedent docs/12:813-815).

---

## 3. Paper ↔ package mapping (what the paper claims, what the package must deliver)

| Paper claim (v4 position paper) | Package prerequisite | Status |
|---|---|---|
| "inference that remains valid despite the data-dependent screening step" | WP1 coverage band + boundary attribution | ❌ not built |
| "measurement selection guided by construct validity predicts validity evidence it was not optimized to satisfy, assessed on pre-registered held-out restrictions" | WP2 R_select/R_holdout + frozen stage split | ❌ not built |
| Trust as flagship construct; admissible set informative | H5 deep study (WP4) + `monotone_rank`/`corr_zero` | 🟡 n=35 checkpoint exists; deep study not run |
| "Implemented in an open-source, model-free software package built for auditability" | Already true (PyPI 2.0.0, hash-frozen, no LLM) | ✅ |
| Empty sets and wide ranges as findings | Already true (exit-0 empty path) | ✅ |

---

## 4. v3.0.0 gate checklist (checkpoint = paper-ready)

- [x] **D1 (Augusto, 2026-08-07): additive-but-mandatory** — dated docs/12 entry + docs/16 amendment text still required (semantics lock precedes code); no freeze-preimage change
- [ ] WP1 implemented, TDD green, determinism under seed, battery green
- [ ] WP2 implemented, TDD green; stage split documented in METHODOLOGY
- [ ] WP3 evaluators with fixtures + semantics locks
- [ ] WP4 deep-trust network frozen (Augusto-authored), anchors pre-data, holdout set declared; run + audit exit 0; paper-lock checkpoint
- [ ] Battery: ruff, mypy strict, pytest ≥222, both proof verifiers exit 0, `git diff --check`, `v0.1` peel, import-graph
- [ ] Docs: METHODOLOGY/ARCHITECTURE/ROADMAP/MANIFEST/docs-12/docs-13/docs-16 amendment all current; doc tensions fixed
- [ ] Atomic version bump 2.0.1a1 → 3.0.0, golden refresh, all literals
- [ ] **Augusto's explicit release decision + Augusto runs the PyPI upload**

## 5. Risks (top 5)

1. **Boundary coupling** — measures near the δ-boundary flip admission across replicates; the band is widest exactly when most informative. Mandatory boundary-attribution reporting (§2 WP1).
2. **Empty M\*** — H5 had 17.5% empty replicates; coverage is conditional on non-empty; the empty rate is part of the validity verdict, not noise.
3. **Small-n bootstrap (n≈35 countries)** — coarse bands; report empty rate + boundary set as primary, band as secondary; consider m-out-of-n bootstrap as documented future work.
4. **Multiple testing across evaluators** — restrictions are descriptive screens, not p-values; the paper must not present per-restriction pass/fail as hypothesis tests.
5. **Governance** — any headline-path change without the dated amendment breaks the docs/16 contract; sequence amendments first, implementation second.

## 6. First 72h for the engineer

1. Read AGENTS.md + METHODOLOGY.md + `docs/16` (§8 amendment as the pattern) + `inference/bootstrap.py`.
2. D1 is decided (additive-but-mandatory): draft the dated docs/12 entry + docs/16 amendment text (semantics lock), then implement WP1 per math_spec §2 — no further sign-off gate.
3. TDD spike: coverage band on the existing H5 n=35 inputs (reuse frozen scores; no new empirical claims) — the band [0.174,0.752] with 17.5% empty replicates becomes the worked example.
4. Draft the WP2 schema change and WP3 evaluator fixtures (synthetic only; no empirical network authorship).
5. Fix the two doc tensions (docs/17:40 `rq`→`rl`; docs/16:5 baseline).
