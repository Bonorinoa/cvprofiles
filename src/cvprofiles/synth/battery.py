"""Package-path synthetic battery: DGP → SCORE → RESTRICT → IDENTIFY → gates.

Never imports the museum monolith. Labels stay outside identify().
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from cvprofiles import __version__
from cvprofiles.identify.pipeline import IdentifyResult, run_identify
from cvprofiles.restrict.pipeline import run_restrict
from cvprofiles.score.pipeline import run_score
from cvprofiles.synth.dgp import (
    ANCHOR,
    DEFAULT_N,
    LABELS,
    SCENARIOS,
    make_dgp,
    roles_for_menu,
)
from cvprofiles.synth.metrics import (
    SeedMetrics,
    cold_cores_equal,
    metrics_from_identify,
)
from cvprofiles.synth.oracle_r import beta_corr_y, network_for

BATTERY_VERSION = "v1_0_package_synth"
DEFAULT_SEEDS: tuple[int, ...] = (0, 1, 2, 3, 4)


@dataclass
class ScenarioAggregate:
    scenario: str
    n_seeds: int
    fa_rate: float
    anchor_rate: float
    h1b_rate: float | None
    h1_latent_rate: float | None
    empty_rate: float
    cold_match_rate: float
    mean_abs_M: float
    mean_width: float | None
    mean_beta_slop: float | None
    invalid_ever_admitted: list[str]
    near_miss_ever_admitted: list[str]
    per_seed: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class GateResult:
    battery_version: str
    package_version: str
    n: int
    seeds: list[int]
    delta: float
    beta: str
    score_policy: str
    scenarios: dict[str, ScenarioAggregate]
    gates: dict[str, bool]
    gate_notes: dict[str, str]
    passed: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "battery_version": self.battery_version,
            "package_version": self.package_version,
            "n": self.n,
            "seeds": self.seeds,
            "delta": self.delta,
            "beta": self.beta,
            "score_policy": self.score_policy,
            "anchor": ANCHOR,
            "scenarios": {k: v.to_dict() for k, v in self.scenarios.items()},
            "gates": self.gates,
            "gate_notes": self.gate_notes,
            "passed": self.passed,
        }


def run_seed(
    scenario: str,
    seed: int,
    *,
    n: int = DEFAULT_N,
    check_cold: bool = True,
) -> tuple[IdentifyResult, SeedMetrics]:
    """One seed through the real package spine (SCORE → RESTRICT → IDENTIFY)."""
    roles = roles_for_menu()
    network = network_for(scenario)
    beta = beta_corr_y()

    df = make_dgp(scenario, n=n, seed=seed)
    score = run_score(df, roles, policy="none")
    restrict = run_restrict(roles, network, beta)
    identify = run_identify(score.frame, roles, restrict)

    metrics = metrics_from_identify(
        scenario=scenario,
        seed=seed,
        n=n,
        identify=identify,
        frame=score.frame,
        labels=LABELS,
        anchor=ANCHOR,
    )

    cold_match: bool | None = None
    if check_cold:
        # Independent second path (fresh DGP draw with same seed must match).
        df2 = make_dgp(scenario, n=n, seed=seed)
        score2 = run_score(df2, roles, policy="none")
        restrict2 = run_restrict(roles, network, beta)
        identify2 = run_identify(score2.frame, roles, restrict2)
        cold_match = cold_cores_equal(identify, identify2)

    # Rebuild frozen metrics with cold_match (dataclass is frozen).
    metrics = SeedMetrics(
        scenario=metrics.scenario,
        seed=metrics.seed,
        n=metrics.n,
        empty=metrics.empty,
        M_star=metrics.M_star,
        L=metrics.L,
        U=metrics.U,
        point_id=metrics.point_id,
        false_admissions=metrics.false_admissions,
        fa_rate=metrics.fa_rate,
        n_invalid_admitted=metrics.n_invalid_admitted,
        anchor_in_M=metrics.anchor_in_M,
        h1b=metrics.h1b,
        beta_anchor=metrics.beta_anchor,
        h1_latent=metrics.h1_latent,
        beta_latent=metrics.beta_latent,
        near_miss_admitted=metrics.near_miss_admitted,
        cold_match=cold_match,
    )
    return identify, metrics


def _mean(xs: list[float]) -> float:
    return float(sum(xs) / len(xs)) if xs else float("nan")


def _aggregate(scenario: str, rows: list[SeedMetrics]) -> ScenarioAggregate:
    n = len(rows)
    fa_rate = _mean([r.fa_rate for r in rows])
    anchor_rate = _mean([1.0 if r.anchor_in_M else 0.0 for r in rows])
    empty_rate = _mean([1.0 if r.empty else 0.0 for r in rows])
    cold_vals = [1.0 if r.cold_match else 0.0 for r in rows if r.cold_match is not None]
    cold_match_rate = _mean(cold_vals) if cold_vals else float("nan")

    h1b_vals = [1.0 if r.h1b else 0.0 for r in rows if r.h1b is not None]
    h1b_rate = _mean(h1b_vals) if h1b_vals else None

    lat_vals = [1.0 if r.h1_latent else 0.0 for r in rows if r.h1_latent is not None]
    h1_latent_rate = _mean(lat_vals) if lat_vals else None

    mean_abs_M = _mean([float(len(r.M_star)) for r in rows])
    widths = [
        float(r.U - r.L)
        for r in rows
        if r.L is not None and r.U is not None and not r.empty
    ]
    mean_width = _mean(widths) if widths else None

    # Optional diagnostic: mean β(m_slop) when available on seed rows via recompute not stored.
    # Leave None here; battery caller can attach later if needed.
    mean_beta_slop = None

    invalid_ever: set[str] = set()
    near_ever: set[str] = set()
    for r in rows:
        invalid_ever.update(r.false_admissions)
        near_ever.update(r.near_miss_admitted)

    return ScenarioAggregate(
        scenario=scenario,
        n_seeds=n,
        fa_rate=fa_rate,
        anchor_rate=anchor_rate,
        h1b_rate=h1b_rate,
        h1_latent_rate=h1_latent_rate,
        empty_rate=empty_rate,
        cold_match_rate=cold_match_rate,
        mean_abs_M=mean_abs_M,
        mean_width=mean_width,
        mean_beta_slop=mean_beta_slop,
        invalid_ever_admitted=sorted(invalid_ever),
        near_miss_ever_admitted=sorted(near_ever),
        per_seed=[r.to_dict() for r in rows],
    )


def evaluate_gates(
    aggregates: dict[str, ScenarioAggregate],
) -> tuple[dict[str, bool], dict[str, str]]:
    """Prereg-style package gates (H1_latent is never a gate)."""
    gates: dict[str, bool] = {}
    notes: dict[str, str] = {}

    def need(name: str) -> ScenarioAggregate | None:
        return aggregates.get(name)

    # H1a FA = 0 on oracle scenarios
    for sc in ("oracle_easy", "oracle_with_slop"):
        agg = need(sc)
        if agg is None:
            gates[f"H1a_fa_{sc}"] = False
            notes[f"H1a_fa_{sc}"] = "scenario missing"
            continue
        ok = agg.fa_rate == 0.0 and not agg.invalid_ever_admitted
        gates[f"H1a_fa_{sc}"] = ok
        notes[f"H1a_fa_{sc}"] = f"fa_rate={agg.fa_rate}; invalid_ever={agg.invalid_ever_admitted}"

    # H1a anchor retention
    for sc in ("oracle_easy", "oracle_with_slop"):
        agg = need(sc)
        if agg is None:
            gates[f"H1a_anchor_{sc}"] = False
            notes[f"H1a_anchor_{sc}"] = "scenario missing"
            continue
        ok = agg.anchor_rate >= 0.999
        gates[f"H1a_anchor_{sc}"] = ok
        notes[f"H1a_anchor_{sc}"] = f"anchor_rate={agg.anchor_rate}"

    # H1b construction when nonempty
    for sc in ("oracle_easy", "oracle_with_slop"):
        agg = need(sc)
        if agg is None:
            gates[f"H1b_{sc}"] = False
            notes[f"H1b_{sc}"] = "scenario missing"
            continue
        ok = agg.h1b_rate is not None and agg.h1b_rate >= 0.999
        gates[f"H1b_{sc}"] = ok
        notes[f"H1b_{sc}"] = f"h1b_rate={agg.h1b_rate}"

    # H3 empty honesty
    for sc in ("harsh_theta", "all_invalid"):
        agg = need(sc)
        if agg is None:
            gates[f"H3_{sc}"] = False
            notes[f"H3_{sc}"] = "scenario missing"
            continue
        ok = agg.empty_rate >= 0.999
        gates[f"H3_{sc}"] = ok
        notes[f"H3_{sc}"] = f"empty_rate={agg.empty_rate}"

    # H4 cold
    cold_ok = True
    cold_notes: list[str] = []
    for name, agg in aggregates.items():
        if agg.cold_match_rate < 0.999:
            cold_ok = False
            cold_notes.append(f"{name}:{agg.cold_match_rate}")
    gates["H4_cold"] = cold_ok
    notes["H4_cold"] = "ok" if cold_ok else f"fail {cold_notes}"

    # FA also 0 on empty scenarios (should be vacuously true)
    for sc in ("harsh_theta", "all_invalid"):
        agg = need(sc)
        if agg is None:
            continue
        ok = agg.fa_rate == 0.0 and not agg.invalid_ever_admitted
        gates[f"H1a_fa_{sc}"] = ok
        notes[f"H1a_fa_{sc}"] = f"fa_rate={agg.fa_rate}"

    return gates, notes


def run_battery(
    *,
    scenarios: tuple[str, ...] | list[str] = SCENARIOS,
    seeds: tuple[int, ...] | list[int] = DEFAULT_SEEDS,
    n: int = DEFAULT_N,
    check_cold: bool = True,
) -> GateResult:
    """Run full mini battery and evaluate gates."""
    aggregates: dict[str, ScenarioAggregate] = {}
    for scenario in scenarios:
        rows: list[SeedMetrics] = []
        for seed in seeds:
            _ident, metrics = run_seed(
                scenario, int(seed), n=n, check_cold=check_cold
            )
            rows.append(metrics)
        aggregates[scenario] = _aggregate(scenario, rows)

    gates, gate_notes = evaluate_gates(aggregates)
    passed = all(gates.values()) if gates else False

    return GateResult(
        battery_version=BATTERY_VERSION,
        package_version=__version__,
        n=int(n),
        seeds=[int(s) for s in seeds],
        delta=0.0,
        beta="corr_y",
        score_policy="none",
        scenarios=aggregates,
        gates=gates,
        gate_notes=gate_notes,
        passed=passed,
    )


def write_battery_summary(
    result: GateResult,
    path: Path | str,
) -> Path:
    """Write machine-readable proof summary JSON."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = result.to_dict()
    p.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return p
