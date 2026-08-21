# reports/

This directory holds the project's **mathematical specification**, the **final
engineering report**, and **allow-listed proof summaries** for shipped
evaluations. Everything here is either a specification of shipped behavior or
a frozen, verifiable evidence artifact.

| Path | Contents |
|---|---|
| `math_spec.md` | The formal specification the engine implements: menu, slacks, M\*, B\*, range identity |
| `FINAL_ENGINEERING_REPORT.md` | Closeout report for the shipped package |
| `summaries/` | Proof summaries (JSON) — one per evaluation lane, each reproducible via the corresponding verifier |

## Proof summaries

Each JSON under `summaries/` records the headline outputs of a frozen run
(admissible set, range, hashes, seeds). They are the compact, committable
fingerprints of runs whose bulk artifacts are regenerated locally. Reproduce a
summary with the matching verifier (see `tools/verify_wvs_gps.py` for the
flagship WVS/GPS patience application) or the documented synthetic battery.

Internal development plans, task inventories, and sprint notes are kept
locally and are not part of the public repository.
