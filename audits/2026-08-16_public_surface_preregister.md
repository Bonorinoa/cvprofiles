# Preregister — public-surface sprint (2026-08-16)

Captured **before** any demo/README/tutorial edit, from:

```bash
env -u PYTHONPATH uv run python -m cvprofiles run \
  --scores data/fixtures/mini_v1/scores.csv \
  --roles data/fixtures/mini_v1/roles.json \
  --network data/fixtures/mini_v1/network.yaml \
  --beta data/fixtures/mini_v1/beta.yaml \
  --out /tmp/cvp_prereg_mini --seed 0
```

on `main` @ `be19d41`, package `3.0.1`.

## Engine / freeze (must be unchanged after all three commits)

| Field | Expected |
|---|---|
| `package_version` | `3.0.1` |
| `run_id` | `dafc6e038485b4969d03a4ee91377e438ce45341e4c390858b655348dabea4a8` |
| `scores_hash` | `c20f0e674cf89ea0c0cd4e6d050e872e5e2ec16801bd30e72b5f0f8aaf85e237` |
| `network_hash` | `3540790e5f4394b08f2d995ea74d064ed5489228fd5c0d34c1d525b07131f921` |
| `beta_hash` | `d94474e81d48e07d8fc686abf56204315c27f3f4628e736653224ed490f3c648` |
| `empty` | `false` |
| `M_star` | `["m_good", "m_weak"]` |
| `rejected` | `{"m_slop": ["r_corr_min_aux", "r_corr_sign_aux"]}` |
| `L` | `0.9908134006120914` |
| `U` | `0.9929645567186532` |
| `n_boot` / bootstrap / coverage / grids / anchors_hash | all null |
| `data/fixtures/mini_v1/expected_freeze.json` | bit-identical to pre-sprint |

`cvprofiles demo` must replay this exact profile.

## Docs / surface (must be true after commit 3)

- README Quickstart does not depend on a repo checkout path.
- README Version row still matches `tools/check_version_consistency.py` (`3.0.1`).
- `tutorials/README.md`, core notebook opening markdown, `docs/README.md`, and root README tutorial table do not sell H5 as the v3 / live flagship.
- Core notebook **code cells and outputs** unchanged (markdown-only diff).
- No `__version__` / `pyproject.toml` version bump.

## Quality gates (must be green after commit 3)

```bash
uv run ruff check src tests tools
uv run mypy src
uv run pytest -q --tb=short
uv run python tools/check_version_consistency.py
uv run cvprofiles --version   # 3.0.1
git diff --check
```
