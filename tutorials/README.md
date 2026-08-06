# cvprofiles tutorial

**`cvprofiles_tutorial.ipynb`** — the independent, two-part walk-through:

1. **Part 1 (synthetic):** builds a scores matrix inline, writes the SCORE/RESTRICT
   inputs to disk, runs a full profile, and shows the empty-set contrast. Needs no
   repository files — only the installed package.
2. **Part 2 (H5 replication):** reproduces the frozen country-level generalized-trust
   evaluation (n=35) from the committed frozen inputs
   (`evals/h5_trust/data/`), including the pinned network and the pre-data θ-anchor
   file. The final cell asserts `M* = {m_trust_general, m_trust_in_group}` and
   `[L,U] = [0.370754, 0.623891]` bit-identically.

## Why "independent"

The verification installs the **published wheel** (not the source tree) into a fresh
virtual environment, then executes the notebook. Run it from the repository root so the
H5 data paths resolve:

```bash
# fresh venv, wheel-only install (PYTHONPATH unset so the src tree cannot leak in)
uv venv /tmp/cvp_tutorial_venv --python 3.11
uv pip install --python /tmp/cvp_tutorial_venv/bin/python \
    dist/cvprofiles-2.0.0a1-py3-none-any.whl jupyter nbconvert ipykernel

# execute a copy of the notebook
cp tutorials/cvprofiles_tutorial.ipynb /tmp/cvp_tutorial_exec.ipynb
env -u PYTHONPATH /tmp/cvp_tutorial_venv/bin/python -m jupyter nbconvert \
    --to notebook --execute /tmp/cvp_tutorial_exec.ipynb \
    --output /tmp/cvp_tutorial_exec_out.ipynb
```

After publishing, the same flow works with `pip install cvprofiles` in place of the
wheel path.

## Notes

- Empty `M*` and wide `[L,U]` are scientific features, not crashes.
- The engine is score-agnostic and model-free; the menu and network are researcher-owned.
- The H5 replication is *preliminary paper-facing evidence* (owner-approved 2026-08-04);
  it is not a final paper lock.
