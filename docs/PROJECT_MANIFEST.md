# PROJECT_MANIFEST

```yaml
project: cvprofiles
display_name: "Construct-Validity Profiles"
type: academic_methods_tool
status: v2_0_0_published_pypi_dev_2_0_1a1
version: "0.1.0"          # first tagged symbolization (methods KB + PoC)
dev_version: "2.0.1a1"      # current package version (docs/tooling/tutorials sprint; dev checkpoint tag 2026-08-07)
target_version: "2.0.0"   # v2.0 measure discipline release (PyPI 2026-08-06)
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
```
