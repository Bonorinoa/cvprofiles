# PROJECT_MANIFEST

```yaml
project: cvprofiles
display_name: "Construct-Validity Profiles"
type: academic_methods_tool
status: v0.1_poc
version: "0.1.0"
created: 2026-08-01
path: ~/Hermes/Projects/cvprofiles
hermes_profile: cvprofiles
github: https://github.com/Bonorinoa/cvprofiles  # set when remote exists / after push
tag: v0.1
poc:
  script: evals/synthetic/v0_poc.py
  version_string: v0_1_poc
  proof_summary: reports/summaries/v0_1_poc_summary.json
  museum: true  # do not import into src/


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
```
