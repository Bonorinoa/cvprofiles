# PROJECT_MANIFEST

```yaml
project: cvprofiles
display_name: "Construct-Validity Profiles"
type: academic_methods_tool
status: v1_1_verified_dev_protocol_provisional_synthetic_locked_empirical_open
version: "0.1.0"          # last tagged symbolization
dev_version: "1.1.0a1"    # current dev package version (no tag)
target_version: "1.1.0"   # v1.1 inference layer (not yet tagged)
created: 2026-08-01
path: ~/Hermes/Projects/cvprofiles
hermes_profile: cvprofiles
github: https://github.com/Bonorinoa/cvprofiles
tag_v0_1: v0.1            # frozen forever at fb62b48 — do not move/retag
tag_v0_1_sha: fb62b48

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

spine:
  states: [SCORE, RESTRICT, IDENTIFY, REPORT]
  thesis_core: [RESTRICT, IDENTIFY, REPORT]
  engine: score_agnostic_model_free

docs:
  required_reading_order:
    - docs/01_Project_Overview.md
    - docs/02_System_Architecture.md
    - docs/03_Methodology.md
    - docs/04_Synthetic_DGPs.md
    - docs/05_Pre_Registration.md
    - docs/06_Tech_Stack.md
    - docs/07_Software_Development_Strategy.md
    - docs/08_Observability_and_Evaluations.md
    - docs/09_MVP_Plan.md
    - docs/10_Open_Questions.md
    - docs/11_Glossary.md
    - docs/12_Decision_Engineering_Log.md
    - docs/13_Evaluations_Log.md
    - docs/14_Researcher_Input_Guide.md
    - docs/16_Paper_Protocol_Freeze.md
  live:
    - docs/12_Decision_Engineering_Log.md
    - docs/13_Evaluations_Log.md

directories:
  - src/
  - tests/
  - evals/synthetic/
  - data/synthetic/
  - data/fixtures/
  - reports/
  - docs/

agents:
  AGENTS.md: deferred  # create before handing repo to coding agents
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
```
