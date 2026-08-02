# mini_v1 — M1 contract fixture

Hand-numeric vertical slice for schema + freeze-hash contract tests.
**Not** a DGP museum import. No RNG.

## Files

| File | Role |
|---|---|
| `scores.csv` | 10 units × 3 measures + aux + outcome + diagnostic |
| `roles.json` | `ScoreColumnRoles` mapping |
| `network.yaml` | 2 restrictions (`corr_min`, `corr_sign` on `v_aux`) |
| `beta.yaml` | `corr_y` on `y` |
| `expected_freeze.json` | Golden piece hashes + `run_id` (pinned version) |

## Columns

- **Freeze hash columns (engine):** `unit_id`, `m_good`, `m_weak`, `m_slop`, `v_aux`, `y`
- **Diagnostic only (out of default scores_hash):** `V_star`

## Design intent (for later M4/M5 — not enforced at M1)

Under oracle \(R\) with \(\delta=0\):

- `m_good` — strong positive with `v_aux` → should survive
- `m_weak` — weaker positive → borderline / may survive depending on sample corr
- `m_slop` — confounded / opposite-ish pattern → should fail `corr_min` or `corr_sign`

M1 only validates schemas + freeze bit-stability. Membership is M4.
