"""F1 (2026-08-16 audit): CSV scores must parse exactly (round-trip floats).

The default pandas fast parser is not correctly rounded on all platforms: the
audit reproduced a committed cell (-2.0682856501203517) parsing to
-2.0682856501203521 under the default parser on Linux, forking scores_hash and
therefore run_id. On macOS the same value round-trips by luck of the libc —
which is the point: only an explicit float_precision="round_trip" makes SCORE
parsing platform-independent so run_id re-verifies from committed inputs.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from cvprofiles.score.pipeline import load_table


def test_load_table_csv_round_trips_exact_floats(tmp_path: Path) -> None:
    value = -2.0682856501203517
    p = tmp_path / "scores.csv"
    p.write_text(f"unit_id,x\nunit,{value!r}\n", encoding="utf-8")
    df = load_table(p)
    parsed = float(df.loc[0, "x"])
    # Exact float equality is the whole point: the committed CSV value must
    # re-parse to itself so scores_hash (and run_id) re-verify from inputs.
    assert parsed == value


def test_load_table_pins_round_trip_float_parsing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """SCORE must explicitly pin float_precision='round_trip'.

    The default fast parser is not guaranteed correctly rounded across
    platforms; the audit reproduced a 1-ulp parse fork on Linux. This contract
    test pins the kwarg so the behavior cannot silently regress on any platform.
    """
    p = tmp_path / "scores.csv"
    p.write_text("unit_id,x\nunit,1.5\n", encoding="utf-8")
    seen: dict = {}
    orig = pd.read_csv

    def spy(*args, **kwargs):
        seen.update(kwargs)
        return orig(*args, **kwargs)

    monkeypatch.setattr(pd, "read_csv", spy)
    load_table(p)
    assert seen.get("float_precision") == "round_trip"
