# Trust Benchmark Lane — Execution-Path Plan (SCA2 adapter vs persona prompt)

**Status:** PLAN ONLY — recon + design. Nothing here is implemented, frozen, or run.
**Scope:** `evals/trust_benchmark/` (this directory). No engine change, no data build, no run, no git operations are authorized by this document.
**Scope decision (2026-08-09, Augusto):** the SCA2-adapter-vs-persona comparison is SCA2-project work — **out of scope** for cvprofiles. The feasible empirical lane is the GPS-WVS patience/risk demo (`evals/wvs_gps_preferences/`). This plan is retained as recon reference only; do not treat it as an active lane plan.
**Date:** 2026-08-09
**Owner:** Augusto owns every researcher-authored field (construct, menu, network `R`, θ, δ, β, split, claims). Agents scaffold only.
**Companion lane discipline:** mirrors `evals/wvs_gps_preferences/` (README + input-builder tutorial flow) and `evals/h5_trust/` (builder + dev-gate auditor + independent `tools/verify_*.py` auditor) — frozen inputs, verify_*.py auditor, country units-split.

---

## 1. Lane objective and the paper claim it serves

**Paper text location (NOT in the cvprofiles repo).** The cvprofiles repo contains **no** trust-benchmark paper text. The flagship description lives in the SCA2 position paper:
`~/Desktop/Github_Repositories/SCA2_PofW/misc/position_paper/position_paper_v6.tex`, Section 5 ("Applied illustrations: from observation to falsification"), §5.1 "Flagship illustration: cultural preferences, SCA~2 versus persona prompting" (v6.tex:713–767).

Key quoted claims this lane serves:

- **v6.tex:714** — "The flagship application compares two AI measurement technologies---persona prompting and the SCA~2 adapter---against conventional instruments for cultural preferences, under one common validity argument, from observation to falsification."
- **v6.tex:718** — "Construct $C$: cultural preferences across the six GPS dimensions; generalized interpersonal trust---the disposition to expect cooperative behavior from anonymous others in the absence of contractual enforcement---serves as the primary construct, defined independently of any single survey instrument."
- **v6.tex:721** — "The two AI arms are the scientific focus: a cultural persona prompt, which declares the target population at inference, and the SCA~2 adapter, whose preference representation is trained from GPS-anchored labels while the country is never named---indirect encoding…"
- **v6.tex:739** — menu includes a "Noise / shuffled control … Negative control; a useful framework should reject it."
- **v6.tex:754** — "the units-split assigns the USA and Mexico to separate frames, admitting on the training frame and demanding compliance on the held frame, with the robust set as headline."
- **v6.tex:763–767** — baselines: "(i) best fit to a single anchor (e.g., maximize correlation with GPS trust); (ii) best predictive fit on selection-sample criteria; (iii) random or convenience selection among AI measures … The headline scientific claim of the empirical paper is Eq.~[falsifiable], not that any one generator 'wins.'"
- **v6.tex:802** (evidence matrix) — "SCA~2 versus persona prompting is decided by evidence, not engineering | Preregistered units-split (USA/MEX) + tier~3 holdout moments; baselines: random, anchor-fit, LLM judge | … | Survivors do no better on held-out moments than persona prompting or random selection"
- **v6.tex:707, 813–818** — "Empirical cells in this manuscript are empty by design"; "No empirical results are reported in this version."

**What the lane must make executable:** frozen preregistered inputs (i) + an evaluation harness that implements the baselines (ii) + the engine lane that executes SCORE → RESTRICT → IDENTIFY → REPORT with the stage-tagged network and the USA/MEX units-split (iii). The engine side already exists at `cvprofiles==2.5.0` (stage + units-split shipped under P4/P5; v6.tex:687 confirms "cvprofiles 2.5.0's Python API already exposes stage-tagged restrictions, units-split composition, and holdout verdicts under synthetic gates").

**Missing inputs (flagged, not fabricated):**
- No persona-prompt scores exist anywhere (SCA2 Stream C is explicitly "new inference"; `demographic_gradient_protocol.md:149` — the frozen `model_option_probabilities_*` files are unconditional and cannot answer it).
- No frozen tier-2 / tier-3 item partition exists yet (preregistered in prose only, v6.tex:716, 754).
- No frozen noise-control column exists for this lane.
- No empirical network `R`, θ anchors, or β for this lane (docs/17's historical H5 network is a different, superseded design — see §4).

**Governance context:** no `docs/16` amendment currently opens this lane. §8 opened H5 Trust (re-graded historical 2026-08-07, `docs/16:157`), §9 opened IVS (the v3 headline), §10 opened the WVS/GPS intermediate demo and explicitly forbids "extension to any other construct without a further dated amendment" (`docs/16:173`). This lane therefore needs its own dated amendment before anything runs (see §6).

---

## 2. Data build

### 2.1 SCA2 data inventory (read-only recon; nothing modified)

Source: `~/Desktop/Github_Repositories/SCA2_PofW/` (separate repo, cross-repo dependency — see §2.4).

| Artifact | Location | What exists | Lane relevance |
|---|---|---|---|
| WVS Wave 7 microdata | `data/WVS/WVS_wave7.dta` (+ `Codebook.pdf`, `MasterQuestionnaire.pdf`) | 66 countries, individual level | Human-side facet scores (raw source) |
| GPS country level | `data/GPS/GPS_dataset_country_level/country_gps.dta` | ~80 countries, `trust` + 5 preference z-scores | Criterion/aux (gps_trust) |
| GPS individual level | `data/GPS/GPS_dataset_individual_level/individual_new.dta` | ~80k respondents, 76 countries | Demographic-gradient benchmark (Stream A), individual-level criterion |
| AmericasBarometer | `data/Barometer/{USA,MEX}_Barometer/` + `data/merged/*Barometer*.parquet` | USA/MEX only | 2-country probe / appendix only (per `docs/17` §4; do **not** row-stack WVS with AB — `data/merged/DATASET_GUIDE.md`) |
| Frozen OOS parquets | `data/merged/{USA,MEX}_WVS_wave7.parquet`, `*_Barometer_2012_2019.parquet` | USA/MEX × WVS/AB, item-level with weights | Human-side moments per country |
| Country scores | `data/validity/scores_full.csv` | WVS7 country facets (all 6 dims) + `gps_*`; **many countries have missing `gps_*`** (e.g. AND, ARM — verified in header rows) | Survey/composite menu columns |
| Trust scores | `data/validity/scores_trust.csv` + `roles_trust.json` | 4 trust facets + `gps_trust` + `n_*` counts; unit `iso3` | Survey facet columns |
| Adapter scores | `data/validity/scores_adapter.csv` + `roles_adapter.json` | **n=2 (USA, MEX) pilot**: `m_USA_adapter_<dim>`, `m_MEX_adapter_<dim>`, `m_base_<dim>` (6 dims), `gps_<dim>`, `m_wvs_<dim>_<facet>` refs | Adapter + base-prompt menu columns. **Caveat:** the USA and MEX rows are **identical** in the adapter/base columns (unconditional prompting ⇒ same probabilities; only `gps_*`/`m_wvs_*` differ) — matches SCA2 README design note (README.md:74) |
| Option probabilities | `DPO_eval_WVS/eval_results_wvs_wave7/model_option_probabilities_{base,USA_adapter,MEX_adapter}_on_{USA,MEX}.csv` | 6 files; 35 eval items (30 mapped to 6 GPS dims + 5 demographics; 7 trust items: Q57–Q64, Q69–Q71, Q73 per `question_map_wvs_edited.csv`) | Upstream source for adapter/base columns (frozen eval artifacts) |
| Scoring protocol | `sca2_validity/prep/protocol.yaml` (+ `protocol_hash.txt` = `7a4a42bd…`) | Frozen recipe: unit country_iso3, mask negative values, min 30 respondents/country, unweighted, normalize→direction→facet mean | Recipe to reuse verbatim (or re-derive independently — see §2.4) |
| SCA2 pilot network | `sca2_validity/prep/networks/trust.yaml` + `data/validity/pilot_networks/trust.yaml` | Single `corr_min gps_trust θ=0.30`; header says "starter template… not a paper claim"; n=2 mean_order pilot nets from `build_adapter_scores.py` | **Template only — NOT the lane network** (§4) |
| SCA2 minimal engine run | `data/validity/runs/trust/profile.json` | M\*={in_group, out_group, institution}, rejected `m_trust_general` (slack −0.0219 vs θ=0.30), β=null | Historical/pilot witness; different (minimal) engine, not cvprofiles |
| Gradients | `data/validity/gradients_wvs.csv`, `gradients_wvs_summary.json` | Stream B demographic gradients (facet ~ female+age+age²+educ, USA/MEX/pooled) | Input to known-groups/demographic-gradient restrictions (v6.tex:748) |
| Protocol draft | `sca2_validity/prep/demographic_gradient_protocol.md` | Stream A/B/C + cell-mean design; Stream C (persona) **not yet run**; frozen hypotheses H-Grad-1..4 (2026-08-05) | Persona-arm design reference; gate language for the adapter-vs-persona test |
| Audits | `sca2_validity/prep/evaluation_audit.md`, `direction_audit.md` | Number re-verification; direction evidence for `confidence: low` items | Read before reusing any SCA2-side column in a paper lane |

**What must be built (not present):**
1. **Persona-prompt scores** — new inference (Stream C): persona grid sex×age×education, open-weight local model (policy §6), same 35 items, log-prob scoring, temperature 0, repetition ≥3 (draft in `demographic_gradient_protocol.md:155–163`). Lives in a lane harness under `evals/` (no LLM client in `src/`), never in the engine.
2. **Noise / shuffled control column** — designed-invalid measure (paper v6.tex:739). Construction (Gaussian like H5's `m_noise`, or permutation of real responses) is an Augusto call.
3. **Frozen tier-2 / tier-3 item partition** — which WVS items are evaluation vs held-out-validation moments (v6.tex:716, 754).
4. **Adapter score rebuild at lane scope** — either reuse `scores_adapter.csv` (n=2, frozen) or rebuild from `model_option_probabilities_*` with the lane's own freeze hashing. Reuse of the SCA2 CSV as-is is the lowest-risk default (it is already frozen with `protocol_hash.txt`); a rebuild changes the preimage and needs its own freeze.

### 2.2 Score-column mapping plan (adapter outputs → score matrix columns)

Engine is **score-agnostic**: `scores.csv` is a unit×measure wide table; `roles.json` declares which columns are `unit_id` / `measures` / `aux` / `outcome` / `diagnostic` (`src/cvprofiles/score/pipeline.py`; `docs/16:28–29`). **No engine change is needed** — adapter outputs and persona-prompt outputs enter as ordinary score columns.

Planned column families (naming follows the H5/SCA2 `m_<family>_<dim>` convention; exact ids are Augusto's):

| Column family | Source | Role | Status |
|---|---|---|---|
| `iso3` | — | unit_id | exists |
| `m_wvs_trust_general` / `_in_group` / `_out_group` / `_institution` | WVS7 per `protocol.yaml` facets (Q57; Q58,Q60; Q59,Q61,Q62,Q63; Q64,Q69,Q70,Q71,Q73) | measures (survey arms) | exists (`scores_trust.csv`) |
| `m_composite_trust` (survivor composite / PCA / IRT) | composite recipe | measure (composite arm, v6.tex:735) | **Augusto choice** (recipe) |
| `m_base_trust` | base Llama-3.1-8B-Instruct unconditional | measure (base-prompt arm, v6.tex:736) | exists (n=2 pilot) |
| `m_persona_trust` | persona-prompt inference (new) | measure (persona arm, v6.tex:737) | **must build** |
| `m_sca2_<dim>` | adapter predicted scores (adapter arm, v6.tex:738) | measure | exists as `m_USA_adapter_*`/`m_MEX_adapter_*` (n=2) |
| `m_noise` / shuffled control | seeded RNG or permutation | measure (**designed-invalid** — FA gate) | **must build** |
| `gps_trust` (+ `gps_<dim>`) | GPS country z-scores | aux (criterion) | exists; **missing for many countries** — universe rule applies |
| `rule_of_law`, `gini`, `log_gdp_pc` (or another β target) | WDI/WGI public | aux/outcome | reusable from H5 aux pipeline (`evals/h5_trust/build_dataset.py`) if Augusto keeps the docs/17-style criterion; otherwise new |
| `n_*` | per-item respondent counts | diagnostic | exists |

**Universe rule (mirror `evals/h5_trust/build_dataset.py:354–383`):** inner-join WVS∩GPS (∩ aux if used) → apply respondent floor (H5 used ≥200; SCA2 protocol uses ≥30 — **Augusto decides the lane floor**) → drop countries with missing aux/outcome coverage (never impute), record dropped countries in the manifest.

**Missingness policy (fail-loud convention, `docs/16:57`, h5 builder:369–383):** WVS negative codes `-1..-5` and AB `88/98` masked in the builder; any residual NaN in measure columns → `BuildError` (fail loud, no imputation); NaN in aux/outcome → coverage-drop with manifest record; GPS `gps_*` NaN is expected for many countries and is handled by the universe rule, not by imputation.

**Adapter-arm caveat to record in the manifest:** unconditional adapter eval makes the adapter columns constant across USA/MEX rows. The lane's verdict machinery must not treat "adapter USA vs MEX differ" as testable from these columns alone — the adapter-vs-persona contrast lives in the persona arm (new conditional inference) and in the baselines, not in a fake USA/MEX difference.

### 2.3 Provenance record spec (mirror `evals/h5_trust/build_dataset.py:390–426` + `score_manifest.json`)

The builder writes `data/score_manifest.json` with:
- `schema_version`, `unit_id`, `n_countries`;
- `universe`: wvs_countries → with_gps → with_aux → after_floor → dropped_missing_coverage (observability of the universe rule);
- `settings`: seed, floor, `policy: "none"`, `delta: 0.0`, weights (`unweighted` primary per SCA2 convention), aux year range;
- `sources`: exact paths + indicator ids (WVS Wave 7; GPS Falk et al. 2018; WDI `NY.GDP.PCAP.PP.KD` / `SI.POV.GINI` / `SL.AGR.EMPL.ZS`; WGI `rl`; SCA2 eval artifacts with their hashes);
- `scores_hash`: canonical CSV SHA-256 (sorted columns, LF, no index — `canonical_csv_hash`, h5 builder:163–168);
- `parent_sha`: cvprofiles repo HEAD (best-effort);
- `generated_at` (UTC).

**Cross-repo dependency note (mirror `evals/wvs_gps_preferences/README.md:11` and `docs/12:624–627`):** the SCA2_PofW folder is a **separate repository**; this lane consumes its frozen artifacts (option-probability CSVs, scores, protocol hash `7a4a42bd…`, SCA2 repo git SHA) **as data provenance only** — never imported, never modified. Reuse the SCA2 `protocol.yaml` recipe either (a) verbatim with its hash recorded, or (b) re-derived independently in the lane builder with the lane's own hash (H5 Trust chose independence, `docs/17:11`; the choice for this lane is Augusto's — see §7 Q4).

---

## 3. Country units-split design

**Preregistration anchor (paper):** "the units-split assigns the USA and Mexico to separate frames, admitting on the training frame and demanding compliance on the held frame, with the robust set as headline" (v6.tex:754); evidence row "Preregistered units-split (USA/MEX) + tier~3 holdout moments" (v6.tex:802); WVS/GPS lane parallel: holdout by country with a pre-registered split (`evals/wvs_gps_preferences/README.md:22`; tutorial `tools/build_wvs_gps_inputs_tutorial.py:413–423`).

**Engine mechanics (all shipped in `cvprofiles==2.5.0`, no engine change):**
- `run_profile(..., holdout_units=[...])` — P4b units-split: select on train units, compliance on hold units, headline = `M_star_robust`; the holdout list is order-normalized (sorted-unique) so list order cannot fork `run_id` (`src/cvprofiles/pipeline.py:89,110–113,138–143`; `identify` exposes `M_star_select`/`M_star_robust`, `pipeline.py:366–367`).
- `stage: select|holdout|None` on restrictions — `None`/`select` gates M\*; `holdout` = compliance finding only, never rejects (`src/cvprofiles/schemas/network.py:41–50`). Degenerate holdout-only networks are rejected at schema parse (`network.py:110–127`).
- Coverage band (D1, additive): `alpha` (default 0.10) / `kappa` (default 2.0) quantiles over non-empty bootstrap replicates (`pipeline.py:90–91,197–201`).

**Candidate design (skeleton — the assignment itself is Augusto's):**

| Element | Candidate | Status |
|---|---|---|
| Units | country `iso3` | **LOCKED by paper** (v6.tex:754; docs/17 §2 precedent) |
| Candidate countries | USA, MEX (adapter arm is 2-country by frozen eval); survey/composite arms could support a wider panel | **AWAITING AUGUSTO** — see Q2 |
| Train frame | one country (e.g. USA) | **AWAITING AUGUSTO** (which country trains; paper says "assigns the USA and Mexico to separate frames") |
| Holdout frame | the other country (MEX) | **AWAITING AUGUSTO** |
| Select restrictions (stage: none/select) | estimated on the train frame | network TBD (§4) |
| Holdout restrictions (stage: holdout) | tier-3 WVS moments (never used in training/scoring, v6.tex:754) + compliance on the held frame | **AWAITING AUGUSTO** |
| Headline | `M_star_robust` (admissible on train **and** compliant on hold) | engine semantics (`pipeline.py:110–113`) |
| Supplementary | bootstrap (units), coverage band, θ-grid λ∈{0.5,1.0,1.5,2.0}, δ-grid — additive diagnostics, excluded from freeze preimage (`docs/16:43–46`) | follow H5 precedent (`docs/17:97`) |

**Degeneracy warning (must be resolved before freezing):** with one unit per frame, correlation-based restrictions (`corr_min`/`corr_sign`/`corr_zero`) and `beta=corr_y` are **undefined** (n=1). The SCA2 pilot already hit this and used `mean_order(group=is_usa, direction=sign(GPS USA−MEX))` (`sca2_validity/prep/build_adapter_scores.py:129–152`; its docstring: "with two countries, correlation-based restrictions are degenerate"). Options for Augusto: (a) `mean_order`/`rank_agree` restrictions on the two frames with pre-declared direction; (b) widen the units to more countries for the survey/composite/persona arms and treat the adapter arm as the 2-country probe; (c) item-moment units (tier-2 vs tier-3 items as the split surface) with the stage: machinery. The paper's "tier-3 holdout moments" language supports a moment-level R_H regardless.

---

## 4. Network + beta — SKELETON ONLY (AWAITING AUGUSTO)

**The empirical nomological network for this lane is NOT authored here and NOT authored by agents** (AGENTS.md authority; `docs/16:59`; docs/18:5 "agents never author empirical networks"). Everything below is placeholder structure; every substantive value is **AWAITING AUGUSTO**.

Reference material that exists but is NOT the lane network:
- SCA2 pilot `trust.yaml`: single `corr_min gps_trust θ=0.30` — self-declared "starter template … not a paper claim" (`sca2_validity/prep/networks/trust.yaml:1–3`).
- Historical H5 network (docs/17 §5, re-graded historical 2026-08-07): `gps_trust 0.3 / rule_of_law 0.3 / gini −0.1`, β=`corr_y` on `log_gdp_pc` — different menu and superseded status; reuse requires an explicit Augusto decision.
- Paper's required validity-profile content (v6.tex:745–753): convergent evidence; discriminant evidence (e.g. institutional trust, risk preference); known-groups/demographic gradients; external behavioral/economic criteria; cross-country ranking; negative controls; human–model invariance (DIF) where items are administered to both.

Skeleton (schema-valid shape; values are placeholders):

```yaml
# evals/trust_benchmark/data/network.yaml  —  AWAITING AUGUSTO (do not run)
schema_version: "1"
name: trust_benchmark_sca2_vs_persona   # AWAITING AUGUSTO
delta: 0.0                              # AWAITING AUGUSTO (H5 precedent: 0.0)
restrictions:
  # AWAITING AUGUSTO — e.g. convergent bar vs gps_trust:
  # - {id: r_conv_gps_trust, type: corr_min, theta: TBD, params: {variable: gps_trust}, stage: select}
  # AWAITING AUGUSTO — discriminant bars (institutional trust, risk preference…):
  # - {id: r_disc_<name>, type: corr_zero, theta: TBD, params: {variable: <aux>}, stage: select}
  # AWAITING AUGUSTO — holdout restrictions on tier-3 moments (stage: holdout):
  # - {id: r_hold_tier3, type: <TBD>, theta: TBD, params: {...}, stage: holdout}
  # AWAITING AUGUSTO — noise control must be rejected (FA gate is verifier-side, not a restriction)
```

β (target functional, paper v6.tex:757–760): "association of the trust measure with a preregistered economic or behavioral criterion (and, secondarily, cross-country ranking fidelity)". Candidates: `corr_y` on a preregistered criterion (H5 used `log_gdp_pc`, docs/17 §8), `map_distance` (v3 registry, D3 — for cross-country ranking fidelity), `mean_order`/`rank_agree` for the 2-frame design. **AWAITING AUGUSTO.**

θ anchors: pre-data, literature-grounded, one per restriction id, completeness-checked by the engine (`docs/12:728`; anchors artifact excluded from the freeze preimage). **AWAITING AUGUSTO.**

Open questions a human must answer before any freeze (§7 Q5–Q9 collect them): construct paragraph; menu finalization incl. composite recipe and noise construction; restriction set + directions; θ per restriction + anchor citations; δ policy; β type + outcome; tier-2/tier-3 partition; train/holdout country assignment; floor; weighting (unweighted primary per SCA2 convention); baselines implementation (random, anchor-fit, LLM judge — v6.tex:763–767, :802; these are harness-side comparisons of selection rules, not engine restrictions, and their operationalization is an open design item).

---

## 5. Verifier spec — `verify_trust_benchmark.py`

Pattern: `tools/verify_h5_trust.py` (read-only structural auditor; `tools/verify_h5_trust.py:1–21,82–179`) + `evals/h5_trust/verify_audit.py` (dev gate that writes `proof_summary.json`; `evals/h5_trust/verify_audit.py:81–145`).

Proposed dual-layer verifier (filenames provisional):

1. **Dev gate** `evals/trust_benchmark/verify_audit.py` — runs the installed pipeline twice (default + cold), checks and writes `proof_summary.json`:
   - **FA=0**: designed-invalids (noise/shuffled control) ∉ M\* and ∉ M_star_robust;
   - **cold freeze-core equality**: `(empty, M_star, M_star_robust, rejected, L, U, point_id, scores_hash, network_hash, beta_hash)` identical across the two runs (FREEZE_KEYS pattern, `verify_audit.py:35–45`);
   - **empty honesty**: empty M\* ⇒ L=U=null, exit 0 (never auto-loosen θ);
   - **artifacts present**: report.html/json, admissible.json, range.json, slacks.csv, run_manifest.json, score_manifest.json (+ bootstrap/coverage/θ-grid when layers are on);
   - **units-split presence**: `holdout_units` recorded in the freeze config; `M_star_select`/`M_star_robust` populated; holdout-stage restrictions present iff holdout_units set.
2. **Independent auditor** `tools/verify_trust_benchmark.py` — read-only, never reruns the engine; validates `proof_summary.json` against the lane's roles/network/anchor files:
   - strict JSON (reject NaN/Infinity; `tools/verify_h5_trust.py:47–79`);
   - provenance hash shapes (64-hex scores/network/beta hashes; 40-hex parent SHA; `verify_h5_trust.py:117–123`);
   - FA=0 cross-checked against designed-invalid list; `gates.FA_zero` consistency;
   - cold-match ⇒ `gates.cold_H4`; empty flag consistency with L/U null;
   - θ-anchor completeness: every restriction id has exactly one anchor, all `pre_data: true` (`verify_h5_trust.py:160–177`);
   - **lane-specific**: verify the SCA2 artifact pins (protocol hash `7a4a42bd…` or lane equivalent, option-probability file hashes, SCA2 repo SHA) against the manifest — the "empty honesty, provenance" extension the WVS/GPS README calls for (`evals/wvs_gps_preferences/README.md:23`).
   - Structural audit ≠ paper acceptance; Gate C-style decision remains Augusto's (`docs/17:117`).

---

## 6. Governance

**Authorizations required before this lane can execute anything:**
1. **New dated amendment to `docs/16`** (Gate B-style designated-evaluation box for the trust benchmark lane). No existing amendment covers it: §8 (H5 Trust) is historical; §9 (IVS) is the v3 headline; §10 (WVS/GPS) is intermediate-demo and explicitly bars "extension to any other construct without a further dated amendment" (`docs/16:173`).
2. **Augusto's authorship** of construct paragraph, menu, network R, θ/anchors, δ, β, tier-2/tier-3 partition, train/holdout assignment, floor, and claims boundary (§3/§4 AWAITING AUGUSTO fields).
3. **Augusto's run decision** after: frozen scores + manifest, pinned seed + package version, independent audit exit 0 (`docs/16:131` Gate B conditions; `docs/17:122`).
4. **Open-weight policy resolution (D5/D6 tension, explicit):** v3 policy says "no DPO adapters" (D5, `docs/16:151`) and "open-weight local models only" for paper-reproducible scoring (D6, `docs/16:153`). This lane's two AI arms are (a) the SCA2 DPO adapter (an existing adapter on the open-weight Llama-3.1-8B-Instruct base — D5's literal language binds it) and (b) persona prompting (must run on an open-weight local model per D6). Whether D5 bars the adapter arm of this designated lane, or a carve-out is amended, is **Augusto's call** — the plan flags it, does not decide it.
5. **Baseline-harness authorization:** implementing the falsifiable-core baselines (random, anchor-fit, LLM judge) is measurement/selection-rule machinery in the harness, not engine work — needs the amendment's scope wording to cover it.

**What this plan does NOT authorize (block):**
- ❌ No engine change to `src/cvprofiles/` (the engine is score-agnostic; adapter/persona scores enter as ordinary columns — no change needed, `docs/16:28`).
- ❌ No empirical run of cvprofiles on SCA2 or any real data by implication of this plan.
- ❌ No authorship of the empirical nomological network (Augusto-owned; §4 is a skeleton).
- ❌ No modification of anything under `~/Desktop/Github_Repositories/SCA2_PofW/` (read-only; authorized only for the data build, per `docs/12:640–642` style authorization and this task's constraints).
- ❌ No git operations (no add/commit/push/stash/tag), no PyPI publication, no `docs/13` evidence claim.
- ❌ No adapter training / retraining (AGENTS.md non-goal; `docs/16:151` D5).
- ❌ No fresh empirical PCA fit (D3, `docs/16:147`) without a separate amendment.
- ❌ This PLAN.md file is left UNTRACKED (created only; not staged).

---

## 7. Open questions and risks

**Measurement gaps / must-build items:**
- Q1. **Persona-prompt arm has no scores anywhere.** Who runs Stream C inference (open-weight local model; persona grid; 35 items; temp 0; repetitions), under which harness, and is the harness committed in `evals/trust_benchmark/` or kept in the SCA2 lab? Version pinning of the base model + prompt template is a hard freeze item (v6.tex:737 arm).
- Q2. **Universe vs adapter arm.** Adapter scores exist only for USA/MEX (frozen eval). Does the lane universe stay {USA, MEX} (adapter-constrained), or widen for survey/composite/persona arms with the adapter arm as a 2-country probe (docs/17 §4 precedent)?
- Q3. **n=2 degeneracy.** With one unit per frame, `corr_min`/`corr_y` are undefined. Choose: `mean_order`/`rank_agree` restrictions (SCA2 pilot precedent), widened country panel, or item-moment units for the split surface (tier-2 vs tier-3). This is the single biggest design risk.
- Q4. **SCA2 recipe reuse vs independence.** Reuse `protocol.yaml` verbatim (record hash) vs re-derive in the lane builder (H5 chose independence, `docs/17:11`). Affects freeze preimage and provenance.
- Q5. **Item availability for trust.** 7 trust items among the 35 eval items (Q57–Q64, Q69–Q71, Q73 — `question_map_wvs_edited.csv`); in-group facet uses Q58+Q60, institution uses Q64+Q69+Q70+Q71+Q73 — all present. Confirm the exact item list against the MasterQuestionnaire before freezing; tier-2/tier-3 partition must not split a facet's items in a way that makes facet scores non-comparable.
- Q6. **gps_* missingness.** Many countries lack GPS z-scores (`scores_full.csv`); the universe rule drops them (never impute). Confirm floor (H5 ≥200 vs SCA2 ≥30) and whether the missingness changes the intended country set materially.
- Q7. **Noise-control construction.** Gaussian (H5 `m_noise` precedent) vs shuffled/permuted real responses (paper v6.tex:739). Must fail the network; FA=0 is a hard gate.
- Q8. **Baselines operationalization.** "Random, anchor-fit, LLM judge" (v6.tex:802) and the falsifiable-core comparison (Eq. falsifiable) are harness-side selection-rule comparisons — define them precisely before the preregistration freeze, or the headline claim cannot be evaluated.
- Q9. **β and outcome.** "Preregistered economic or behavioral criterion" (v6.tex:757) — which criterion? `corr_y` on log GDP pc (H5 precedent) vs another; `map_distance` for cross-country ranking fidelity (D3) — engine-side choice, Augusto's.
- Q10. **Adapter/persona version pinning.** Which SCA2 adapter checkpoint (DPO_train_test outputs), which option-probability file set, which base-model revision, which persona prompt template — all must be pinned with hashes in the manifest before any run.
- Q11. **D5/D6 policy conflict** (adapter arm vs "no DPO adapters"; persona arm vs "open-weight local only") — needs an explicit amendment decision (see §6).
- Q12. **Weighting.** SCA2 convention is unweighted primary (protocol.yaml:17; DATASET_GUIDE recommends unweighted first, weights after audit); H5 was unweighted with weighted as diagnostic contrast (`docs/17:49`). Confirm for this lane.
- Q13. **Ecological bias + small-sample fragility.** Country-level means and n=2 frames mean admission statements are sample-dependent (docs/17 §2 sample-size posture); bootstrap resamples units (countries). The verifier and claims boundary must state this.

**Risks summary:** n=2 degeneracy forcing restriction-type downgrade (Q3); adapter-arm country ceiling (Q2); persona arm not yet generated (Q1); GPS coverage gaps (Q6); D5/D6 policy conflict (Q11); baseline definitions drifting (Q8); ecological/aggregation bias on country means (Q13).

---

## Appendix — recon citations (key files)

- `~/Desktop/Github_Repositories/SCA2_PofW/misc/position_paper/position_paper_v6.tex:713–767, 802, 707, 813–818`
- `~/Desktop/Github_Repositories/SCA2_PofW/sca2_validity/prep/demographic_gradient_protocol.md:147–210, 176–185, 214–285`
- `~/Desktop/Github_Repositories/SCA2_PofW/sca2_validity/prep/build_adapter_scores.py:2–23, 129–152`
- `~/Desktop/Github_Repositories/SCA2_PofW/sca2_validity/prep/build_wvs_gradients.py:1–32, 56–66`
- `~/Desktop/Github_Repositories/SCA2_PofW/sca2_validity/prep/protocol.yaml:13–41`; `prep/networks/trust.yaml:1–13`
- `~/Desktop/Github_Repositories/SCA2_PofW/data/validity/{scores_trust,scores_adapter,scores_full}.csv`, `roles_trust.json`, `roles_adapter.json`, `protocol_hash.txt`, `runs/trust/profile.json`, `pilot_networks/trust.yaml`
- `~/Desktop/Github_Repositories/SCA2_PofW/DPO_eval_WVS/README.md:32–66`; `question_map_wvs_edited.csv` (35 items; trust rows Q57–Q73)
- `~/Desktop/Github_Repositories/SCA2_PofW/data/merged/DATASET_GUIDE.md` (four parquets; do not row-stack WVS/AB)
- `~/Desktop/Github_Repositories/SCA2_PofW/README.md:7, 56–74`
- cvprofiles: `docs/16_Paper_Protocol_Freeze.md:125–173`; `docs/17_H5_Trust_Design.md:11, 19–49, 57–68, 84–97, 110–124`; `docs/18_IVS_Cultural_Map.md:9–13, 42–64`
- cvprofiles: `src/cvprofiles/schemas/network.py:41–50, 110–127`; `src/cvprofiles/pipeline.py:74–92, 110–113, 138–143, 186–188`
- cvprofiles: `evals/h5_trust/build_dataset.py:309–426`; `evals/h5_trust/verify_audit.py:28–145`; `tools/verify_h5_trust.py:34–179`
- cvprofiles: `evals/wvs_gps_preferences/README.md:9–28`; `tools/build_wvs_gps_inputs_tutorial.py:55–85, 413–423`
- cvprofiles: `docs/archive/05_Pre_Registration.md` (generic H5 template — no trust-benchmark-specific text)
