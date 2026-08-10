"""Execute the WVS/GPS input-builder tutorial and print the outputs.

Scientific-integrity gate: a committed tutorial must have been executed and
its headline claims verified against actual output. This runner executes a
COPY of the notebook (the committed file stays clean), then prints each code
cell's stream/execute results so a human can verify the numbers.

Usage: env -u PYTHONPATH uv run python tools/execute_wvs_gps_inputs_tutorial.py
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SRC = REPO / "tutorials" / "cvprofiles_wvs_gps_inputs.ipynb"
PY = sys.executable


def main() -> None:
    if not SRC.exists():
        raise SystemExit(f"missing notebook: {SRC}")

    work = Path(tempfile.mkdtemp(prefix="cvp_wvsgps_exec_"))
    exec_path = work / "exec.ipynb"
    out_path = work / "out.ipynb"
    shutil.copyfile(SRC, exec_path)

    cmd = [
        PY,
        "-m",
        "jupyter",
        "nbconvert",
        "--to",
        "notebook",
        "--execute",
        str(exec_path),
        "--output",
        str(out_path),
    ]
    print("running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print("STDERR:", proc.stderr[-4000:])
        raise SystemExit(f"nbconvert failed rc={proc.returncode}")

    nb = json.loads(out_path.read_text())
    print(f"\nexecuted {len(nb['cells'])} cells OK")

    for i, c in enumerate(nb["cells"]):
        if c["cell_type"] != "code":
            continue
        texts = []
        for o in c.get("outputs", []):
            if o.get("output_type") == "stream":
                texts.append("".join(o.get("text", [])))
            elif o.get("output_type") == "execute_result":
                texts.append("".join(o.get("data", {}).get("text/plain", [])))
            elif o.get("output_type") == "error":
                raise SystemExit(
                    f"cell {i} raised {o.get('ename')}: {o.get('evalue')}\n"
                    + "".join(o.get("traceback", []))[-2000:]
                )
        joined = "".join(texts).strip()
        if joined:
            print(f"\n--- cell {i} ---\n{joined}")

    # Headline claims from the synthetic walk-through must appear verbatim.
    payload = out_path.read_text()
    for claim in [
        "Part 1 assertions PASSED",
        "Empty-set honesty PASSED",
        "cold re-run bit-identical on freeze core: PASSED",
        "-> merge refused. WVS items enter only as country means (Part 2).",
    ]:
        if claim not in payload:
            raise SystemExit(f"MISSING claim in executed notebook: {claim!r}")
        print(f"\nclaim verified: {claim}")
    print("\nSCIENTIFIC-INTEGRITY GATE: PASSED")


if __name__ == "__main__":
    main()
