# PROJECT_MANIFEST

```yaml
project: cvprofiles
display_name: "Construct-Validity Profiles"
type: academic_methods_tool
status: v2_5_1_pypi_released
version: "0.1.0"          # first tagged symbolization (methods KB + PoC)
dev_version: "2.5.1"        # current package version (PyPI release 2026-08-09; first PyPI since 2.0.0)
target_version: "3.0.0"   # v3.0.0 remains Gate C target; 2.5.1 is the current PyPI release
created: 2026-08-01
path: ~/Hermes/Projects/cvprofiles
hermes_profile: cvprofiles
github: https://github.com/Bonorinoa/cvprofiles
tag_v0_1: v0.1            # frozen forever at fb62b48 — do not move/retag
tag_v0_1_sha: fb62b48
tag_v1_1: v1.1.0           # MVP tag 2026-08-04 — do not move/retag
tag_v1_1_sha: fce31c8
tag_v2_0: v2.0.0           # measure discipline release 2026-08-06 — do not move/retag
tag_v2_0_sha: 6abb6e4
tag_v2_0_1a1: v2.0.1a1     # dev checkpoint 2026-08-07 — docs/tooling/tutorials sprint
tag_v2_5: v2.5.0           # P1–P5 engine infrastructure checkpoint 2026-08-08 — not PyPI
tag_v2_5_sha: 62b99c7      # peel of annotated tag v2.5.0 (post-tag follow-up; tag itself stays at 62b99c7)
tag_v2_5_1: v2.5.1           # PyPI release 2026-08-09 — first PyPI since 2.0.0
tag_v2_5_1_sha: TBD          # owner fills after tagging v2.5.1

poc:
  script: evals/synthetic/v0_poc.py
  version_string: v0_1_poc
  proof_summary: reports/summaries/v0_1_poc_summary.json
  museum: true  # do not import into src/

v1_0:
  scope: thin_first_principles_spine
  states: [SCORE, RESTRICT, IDENTIFY, REPORT_thin]
  bootstrap: deferred_to_v1.1
  build_order: [M1, M2, M3, M4, M5, M7, M8, M9]  # no M6, no M10 this sprint
  range: min_max_B_star   # no bootstrap / θ-grid in v1.0

v1_1:
  scope: M6_inference_layer_shipped_handoff_ready
  bootstrap: units_only_percentile_nonempty_replicates
  theta_grid: diagnostic_scale_multipliers
  headline_range: min_max_B_star_unchanged
  build_order: [version_bump_atomic, bootstrap, theta_grid, wiring, evidence, handoff]
  implementation_sha: 784c1be
  evidence_summary: reports/summaries/v1_1_package_synth_summary.json
  evidence_parent_sha: 098e2fa
  handoff: no_tag_no_pypi_release_review_owns_release
  protocol: docs/16_Paper_Protocol_Freeze.md
  protocol_status: provisional_synthetic_locked
  protocol_evidence_summary: reports/summaries/v1_1_protocol_synth_mc50_summary.json
  protocol_evidence_parent_sha: 5bfea25

h5_trust:
  design: docs/17_H5_Trust_Design.md
  status: preliminary_paper_facing_evidence
  evidence_summary: reports/summaries/h5_trust_evidence_summary.json
  evidence_generator: tools/make_h5_trust_summary.py
  approved: 2026-08-04
  owner: Augusto
  construct: country_level_generalized_trust
  data: wvs_wave7_gps_country_ab_2country_probe
  network: corr_min(gps_trust,0.3)+corr_min(rule_of_law,0.3)+corr_sign(gini,-1,0.1)
  beta: corr_y_on_log_gdp_pc
  delta: 0.0
  n_countries: 35
  M_star: [m_trust_general, m_trust_in_group]
  range: [0.37075446228800285, 0.62389053803067]

v2_0:
  status: measure_discipline_published
  plan: docs/archive/18_Measure_Discipline_Plan.md
  threads: [delta_grid, evaluator_registry, theta_anchor_discipline]
  version: 2.0.0  # published on PyPI 2026-08-06 (tag v2.0.0 @ 6abb6e4)
  checkpoint: per_thread
  h5_delta_grid_run: done

v2_5:
  status: tagged_engine_infra_checkpoint
  version: 2.5.0  # tag v2.5.0 2026-08-08; NOT on PyPI (latest PyPI remains 2.0.0)
  scope: rev3_p1_to_p5  # corr_zero/monotone_rank; diff_means/map_distance; stage+units-split holdout; coverage uncertainty band
  pypi: false
  next: p6_benchmark_kit_ivs_harness_deferred

v3_0:
  status: p1_p5_engine_closed_at_v2_5_0_p6_deferred
  plan: reports/DEVELOPMENT_PLAN_v3_REV3.md  # Rev 3 authority; Rev 2 historical
  inventory: reports/VERIFIED_TASK_INVENTORY.md
  amendment: docs/16_Paper_Protocol_Freeze.md  # §9 dated amendment 2026-08-07
  design_doc: docs/18_IVS_Cultural_Map.md
  target_version: "3.0.0"
  headline: ivs_cultural_values_lane
  h5_status: historical_regression_witness
  open_weight_policy: true  # no adapters, no proprietary APIs (D5/D6)
  run_gate: gate_b_augusto_run_decision
  note: "v2.5.0 closed Rev 3 P1–P5 engine go; P6/P7/Gate B/C remain"

wvs_gps_preferences:
  status: intermediate_demo_opened
  constructs: [patience, risk_taking]
  data: local GPS Falk 2018 + WVS Wave 7  # country + individual level; WVS missing codes -1..-5 masked, never imputed
  p6_scope: e2e_proof_teaching
  tag_candidate: v2.6.0
  owner: Augusto
  paper_status: complement_not_headline  # intermediate demo; IVS cultural-values remains Gate B headline

spine:
  states: [SCORE, RESTRICT, IDENTIFY, REPORT]
  thesis_core: [RESTRICT, IDENTIFY, REPORT]
  engine: score_agnostic_model_free

docs:
  required_reading_order:
    - docs/METHODOLOGY.md
    - docs/USER_GUIDE.md
    - docs/ARCHITECTURE.md
    - docs/ROADMAP.md
    - docs/12_Decision_Engineering_Log.md
    - docs/13_Evaluations_Log.md
    - docs/16_Paper_Protocol_Freeze.md
    - docs/17_H5_Trust_Design.md
    - tutorials/cvprofiles_irt_scoring_tutorial.ipynb
    - tutorials/cvprofiles_sensemakr_tutorial.ipynb
    - docs/archive/README.md
  live:
    - docs/12_Decision_Engineering_Log.md
    - docs/13_Evaluations_Log.md
    - docs/ROADMAP.md

directories:
  - src/
  - tests/
  - evals/synthetic/
  - data/synthetic/
  - data/fixtures/
  - reports/
  - audits/
  - docs/

agents:
  AGENTS.md: present  # created 2026-08-04; read before handing repo to coding agents
  soul_authority: ~/.hermes/profiles/cvprofiles/SOUL.md

locks:
  - four_state_machine
  - no_llm_in_engine
  - user_owns_nomological_network
  - synthetic_dgp_before_real_baselines
  - dual_live_logs
  - v0_1_tag_immovable
  - museum_poc_unimported
  - v1_0_no_bootstrap
  - v1_1_diagnostics_additive
  - v1_1_grid_excluded_from_freeze_preimage
  - h5_trust_design_locked_run_gated
  - v2_0_measure_discipline_scope_box
  - v2_0_0_published_pypi
  - gate_a_signed_2026_08_07
  - ivs_design_reserved_run_gated  # design RESERVED/AWAITING AUGUSTO; locked only at Gate B
  - h5_re_grade_historical_2026_08_07
  - open_weight_v3
  - v2_5_0_tagged_engine_infra_checkpoint  # P1–P5 closed; not PyPI; 3.0.0 still Gate C
  - wvs_gps_intermediate_demo_2026_08_09  # intermediate demo box; NOT paper evidence; IVS cultural-values remains Gate B headline
```
