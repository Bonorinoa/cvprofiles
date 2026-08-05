"""Build the frozen SCORE input for the H5 Trust evaluation (docs/17).

Reads raw public survey files (WVS Wave 7, GPS country level) plus local
auxiliary caches (WDI/WGI), applies the design-locked missingness/aggregation
rules from docs/17, and writes ``data/scores.csv`` + ``score_manifest.json``
with a canonical freeze hash.

This is a design-locked eval artifact, NOT part of the cvprofiles engine.
It makes no network calls unless ``--fetch-wdi`` is passed explicitly; tests
never fetch. Raw files may be CSV (tests / small extracts) or Stata ``.dta``
(the actual survey files); the loader dispatches on suffix.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd

WVS_MISSING_CODES = {-1, -2, -3, -4, -5}
AB_MISSING_CODES = {88, 98}
AUX_YEARS = (2015, 2019)
SCHEMA_VERSION = "1"
MEASURE_COLUMNS = [
    "m_trust_general",
    "m_trust_in_group",
    "m_trust_out_group",
    "m_trust_institution",
]
N_COLUMNS = [
    "n_trust_general",
    "n_trust_in_group",
    "n_trust_out_group",
    "n_trust_institution",
]
# Default logical item groups (lowercase). The real WVS .dta uses uppercase
# Q57-style names; map them in build() before aggregating.
DEFAULT_ITEM_GROUPS = {
    "m_trust_general": ["q57"],
    "m_trust_in_group": ["q58", "q60"],
    "m_trust_out_group": ["q61", "q62", "q63"],
    "m_trust_institution": ["q64", "q69", "q70", "q71"],
}
WVS_COUNTRY_TO_LOGICAL = {
    "B_COUNTRY_ALPHA": "country",
    "country": "country",
}
# Real WVS file column names (uppercase master-questionnaire codes).
WVS_REAL_ITEM_COLUMNS = {k: k.upper() for k in sum(DEFAULT_ITEM_GROUPS.values(), [])}


class BuildError(Exception):
    """Fail-loud error for the H5 Trust builder."""


# --- pure helpers --------------------------------------------------------

def mask_missing(series: pd.Series, missing_codes: set[int]) -> pd.Series:
    """Replace official missing codes with NaN (WVS negatives, AB 88/98)."""
    return series.mask(series.isin(missing_codes))


def reverse_trust_1_4(x: pd.Series) -> pd.Series:
    """Reverse 1..4 trust items so 1.0 = trust completely, 0.25 = not at all."""
    return (5.0 - x) / 4.0


def aggregate_wvs_country(
    df: pd.DataFrame,
    missing_codes: set[int],
    item_groups: dict[str, list[str]] | None = None,
) -> pd.DataFrame:
    """Aggregate raw WVS items to country-level measures + valid-response counts.

    The frame must contain a ``country`` column (iso3-style codes) and every
    item column named in ``item_groups``. The generalized-trust item is a
    binary share; the facet measures are means of reversed 1..4 items, averaged
    over available items per respondent, then over respondents per country.
    """
    groups = item_groups if item_groups is not None else DEFAULT_ITEM_GROUPS
    if "country" not in df.columns:
        raise BuildError("missing country column; map B_COUNTRY_ALPHA first")
    for measure, cols in groups.items():
        missing = [c for c in cols if c not in df.columns]
        if missing:
            raise BuildError(f"missing item column(s) {missing} for {measure}")

    rows: dict[str, pd.Series] = {}
    general_col = groups["m_trust_general"][0]
    for country, g in df.groupby("country", sort=True):
        general = mask_missing(g[general_col], missing_codes).dropna().astype(float)
        share = float((general == 1.0).mean()) if len(general) else np.nan
        n_general = int(len(general))

        facet_means: dict[str, float] = {}
        n_counts: dict[str, int] = {}
        for measure in ["m_trust_in_group", "m_trust_out_group", "m_trust_institution"]:
            items = pd.concat(
                [reverse_trust_1_4(mask_missing(g[c], missing_codes)) for c in groups[measure]],
                axis=1,
            )
            per_respondent = items.mean(axis=1)
            facet_means[measure] = (
                float(per_respondent.mean()) if per_respondent.notna().any() else np.nan
            )
            n_counts[measure] = int(per_respondent.notna().sum())

        rows[str(country)] = pd.Series(
            {
                "m_trust_general": share,
                "m_trust_in_group": facet_means["m_trust_in_group"],
                "m_trust_out_group": facet_means["m_trust_out_group"],
                "m_trust_institution": facet_means["m_trust_institution"],
                "n_trust_general": n_general,
                "n_trust_in_group": n_counts["m_trust_in_group"],
                "n_trust_out_group": n_counts["m_trust_out_group"],
                "n_trust_institution": n_counts["m_trust_institution"],
            }
        )
    out = pd.DataFrame.from_dict(rows, orient="index")
    out.index.name = "iso3"
    return out


def average_year_range(
    aux_long: pd.DataFrame, lo: int = AUX_YEARS[0], hi: int = AUX_YEARS[1]
) -> pd.DataFrame:
    """Per-country means over [lo, hi]; log GDP per capita; agri share renamed."""
    sub = aux_long[(aux_long["year"] >= lo) & (aux_long["year"] <= hi)]
    means = sub.groupby("iso3")[["gdp_pc_ppp", "gini", "agri_empl"]].mean()
    out = pd.DataFrame(
        {
            "log_gdp_pc": np.log(means["gdp_pc_ppp"]),
            "gini": means["gini"],
            "m_share_agriculture": means["agri_empl"],
        }
    )
    return out


def load_aux_local(aux_dir: Path) -> pd.DataFrame:
    """Merge local WDI/WGI caches into the auxiliary frame (deterministic)."""
    wdi_path = aux_dir / "wdi.csv"
    wgi_path = aux_dir / "wgi.csv"
    if not wdi_path.exists() or not wgi_path.exists():
        raise BuildError(
            f"aux cache incomplete: need {wdi_path.name} and {wgi_path.name} under {aux_dir}"
        )
    wdi = pd.read_csv(wdi_path)
    wgi = pd.read_csv(wgi_path)
    out = average_year_range(wdi)
    rule = wgi[(wgi["year"] >= AUX_YEARS[0]) & (wgi["year"] <= AUX_YEARS[1])]
    out = out.join(rule.groupby("iso3")["rule_of_law"].mean(), how="left")
    return out


def canonical_csv_hash(df: pd.DataFrame) -> str:
    """Stable SHA-256 of the canonical CSV (sorted columns, LF, no index)."""
    canon = df.copy().sort_index(axis=1)
    canon = canon.sort_values(by=canon.columns[0]).reset_index(drop=True)
    text = canon.to_csv(index=False, lineterminator="\n")
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_gps(gps_df: pd.DataFrame) -> pd.Series:
    """Extract gps_trust indexed by iso3, tolerating name variants."""
    trust_col = next((c for c in ["trust", "TRUST", "trust_mean"] if c in gps_df.columns), None)
    country_col = next((c for c in ["isocode", "iso3", "ISO3", "ccode"] if c in gps_df.columns), None)
    if trust_col is None or country_col is None:
        raise BuildError(f"GPS frame lacks trust/country columns; got {list(gps_df.columns)}")
    s = gps_df.set_index(country_col)[trust_col].rename("gps_trust")
    s.index.name = "iso3"
    return s


# --- optional WDI/WGI fetch (opt-in; tests never call network) -------------

# WGI uses a few legacy codes that differ from ISO-3; map to standard codes.
WGI_CODE_MAP = {"ADO": "AND", "ROM": "ROU", "ZAR": "COD", "KSV": "XKX", "TMP": "TLS"}


def fetch_wdi_aux(aux_dir: Path) -> None:
    """Fetch the three WDI indicators (2015-2019) and write aux_dir/wdi.csv.

    Public World Bank API, no key. Maps World Bank country codes to ISO-3 via
    the /v2/country metadata so the merge with WVS/GPS (ISO-3) works.
    Requires network; deterministic once cached.
    """
    import json as _json
    import urllib.request

    # Country metadata: the /v2/country endpoint id IS the ISO-3 code for real
    # countries (aggregates have non-alpha ids like "1A"/"ZH"). Indicator rows
    # expose countryiso3code; keep rows whose code is a real country.
    with urllib.request.urlopen(
        "https://api.worldbank.org/v2/country?per_page=400&format=json", timeout=60
    ) as resp:  # noqa: S310
        country_body = _json.loads(resp.read().decode("utf-8"))
    iso3_set = {
        rec["id"]
        for rec in country_body[1]
        if len(rec["id"]) == 3 and rec["id"].isalpha()
    }

    indicators = {
        "gdp_pc_ppp": "NY.GDP.PCAP.PP.KD",
        "gini": "SI.POV.GINI",
        "agri_empl": "SL.AGR.EMPL.ZS",
    }
    frames = []
    for key, code in indicators.items():
        url = (
            f"https://api.worldbank.org/v2/country/all/indicator/{code}"
            f"?date={AUX_YEARS[0]}:{AUX_YEARS[1]}&format=json&per_page=20000"
        )
        with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310
            body = _json.loads(resp.read().decode("utf-8"))
        rows = []
        for rec in body[1]:
            if rec.get("value") is None:
                continue
            iso3 = rec.get("countryiso3code", "")
            if iso3 not in iso3_set:
                continue
            rows.append(
                {"iso3": iso3, "year": int(rec["date"]), key: float(rec["value"])}
            )
        frames.append(pd.DataFrame(rows))
    merged = frames[0]
    for f in frames[1:]:
        merged = merged.merge(f, on=["iso3", "year"], how="outer")
    merged.to_csv(aux_dir / "wdi.csv", index=False)


def parse_wgi_sheet(df: pd.DataFrame) -> pd.DataFrame:
    """Parse a WGI indicator sheet (header=None read) into iso3/year/value.

    WGI workbook layout: one sheet per indicator; a header block where one row
    carries year groups and the row below carries sub-indicators (Estimate,
    StdErr, NumSrc, Rank, Lower, Upper); data rows have country name at col 0
    and country code at col 1. Returns a long frame with ISO-3 codes mapped
    from legacy WGI codes.
    """
    sub_row = None
    for i in range(df.shape[0]):
        if any(str(df.iloc[i, c]).strip() == "Country/Territory" for c in range(min(3, df.shape[1]))):
            sub_row = i
            break
    if sub_row is None:
        raise BuildError("WGI sheet lacks a Country/Territory header row")
    year_row = sub_row - 1

    est_cols: dict[int, int] = {}
    for col in range(2, df.shape[1]):
        year = df.iloc[year_row, col]
        sub = str(df.iloc[sub_row, col]).strip()
        if pd.notna(year) and sub == "Estimate":
            est_cols[col] = int(pd.to_numeric(year))

    rows = []
    for _, r in df.iloc[sub_row + 1 :].iterrows():
        code = r.iloc[1]
        if pd.isna(code):
            continue
        iso3 = WGI_CODE_MAP.get(str(code), str(code))
        for col, year in est_cols.items():
            if AUX_YEARS[0] <= year <= AUX_YEARS[1] and pd.notna(r.iloc[col]):
                rows.append({"iso3": iso3, "year": year, "rule_of_law": float(r.iloc[col])})
    out = pd.DataFrame(rows)
    if out.empty:
        raise BuildError("WGI sheet parsed to zero rows")
    return out


def fetch_wgi_aux(aux_dir: Path) -> None:
    """Download the WGI workbook and write aux_dir/wgi.csv (rule of law, rl).

    Requires network and openpyxl; deterministic once cached. The World Bank
    endpoint blocks plain urllib, so a browser User-Agent is sent.
    """
    import urllib.request

    url = "https://www.worldbank.org/content/dam/sites/govindicators/doc/wgidataset.xlsx"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
            )
        },
    )
    with urllib.request.urlopen(req, timeout=90) as resp:  # noqa: S310
        raw = resp.read()
    source = aux_dir / "wgi_source.xlsx"
    source.write_bytes(raw)
    df = pd.read_excel(source, sheet_name="RuleofLaw", header=None)
    parse_wgi_sheet(df).to_csv(aux_dir / "wgi.csv", index=False)


# --- orchestration -------------------------------------------------------

def build(
    raw_root: Path,
    aux_dir: Path,
    out_dir: Path,
    seed: int = 20260804,
    floor: int = 200,
    wvs_file: str = "wvs.csv",
    gps_file: str = "gps.csv",
    item_groups: dict[str, list[str]] | None = None,
    country_col: str = "country",
    fetch_wdi: bool = False,
) -> None:
    """Assemble and write the frozen scores + manifest (docs/17 SCORE spec)."""
    print("[1/5] Loading WVS Wave 7 items...")
    wvs_path = raw_root / wvs_file
    # convert_categoricals=False: the WVS .dta has non-unique value labels
    # (town names repeat across countries) that pandas cannot turn into
    # categoricals; we keep raw integer codes and mask missing ourselves.
    wvs = (
        pd.read_stata(wvs_path, convert_categoricals=False)
        if wvs_path.suffix == ".dta"
        else pd.read_csv(wvs_path)
    )
    if country_col != "country":
        wvs = wvs.rename(columns={country_col: "country"})
    groups = item_groups if item_groups is not None else DEFAULT_ITEM_GROUPS
    wvs_measures = aggregate_wvs_country(wvs, missing_codes=WVS_MISSING_CODES, item_groups=groups)
    print(f"      {len(wvs_measures)} countries from WVS")

    print("[2/5] Loading GPS country-level trust...")
    gps_path = raw_root / gps_file
    gps_df = (
        pd.read_stata(gps_path, convert_categoricals=False)
        if gps_path.suffix == ".dta"
        else pd.read_csv(gps_path)
    )
    gps = load_gps(gps_df)
    print(f"      {gps.notna().sum()} countries with GPS trust")

    print("[3/5] Loading auxiliaries (WDI/WGI local cache)...")
    if fetch_wdi:
        fetch_wdi_aux(aux_dir)
    aux = load_aux_local(aux_dir)
    print(f"      {len(aux)} countries with auxiliaries")

    print("[4/5] Joining, applying respondent floor, adding designed-invalid m_noise...")
    n_wvs = len(wvs_measures)
    with_gps = wvs_measures.join(gps, how="inner")
    n_gps = len(with_gps)
    merged = with_gps.join(aux, how="inner")
    n_aux = len(merged)
    merged = merged.sort_index()
    n_before = len(merged)
    merged = merged[(merged[N_COLUMNS] >= floor).all(axis=1)]
    print(
        f"      universe: wvs={n_wvs} -> with_gps={n_gps} -> with_aux={n_aux} -> "
        f"floor={floor}: {n_before} countries"
    )
    merged["m_noise"] = np.random.default_rng(seed).standard_normal(len(merged))

    # Measures must be complete: NaN here means an aggregation bug -> fail loud.
    measure_nan = [c for c in MEASURE_COLUMNS + ["m_noise"] if merged[c].isna().any()]
    if measure_nan:
        raise BuildError(f"NaN in measure columns after merge: {measure_nan}")

    # Aux/outcome/designed-invalid-with-aux NaN = no coverage -> exclude per the
    # universe rule (never impute), recorded in the manifest for observability.
    coverage_cols = ["gps_trust", "rule_of_law", "gini", "log_gdp_pc", "m_share_agriculture"]
    drop_mask = merged[coverage_cols].notna().all(axis=1)
    dropped_coverage = sorted(merged.index[~drop_mask])
    merged = merged[drop_mask]
    if merged.empty:
        raise BuildError("no countries with complete aux/outcome coverage")
    if dropped_coverage:
        print(f"      dropped {len(dropped_coverage)} countries (missing aux/outcome): {dropped_coverage}")

    print("[5/5] Writing frozen scores + manifest...")
    out_dir.mkdir(parents=True, exist_ok=True)
    scores = merged.reset_index()
    scores.to_csv(out_dir / "scores.csv", index=False)

    try:
        parent_sha = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=Path(__file__).resolve().parents[2], text=True
        ).strip()
    except Exception:  # noqa: BLE001 - best-effort provenance
        parent_sha = None

    manifest = {
        "schema_version": SCHEMA_VERSION,
        "unit_id": "iso3",
        "n_countries": len(scores),
        "universe": {
            "wvs_countries": n_wvs,
            "with_gps": n_gps,
            "with_aux": n_aux,
            "after_floor": len(merged) + len(dropped_coverage),
            "dropped_missing_coverage": dropped_coverage,
        },
        "settings": {
            "seed": seed,
            "floor": floor,
            "policy": "none",
            "delta": 0.0,
            "weights": "unweighted",
            "aux_years": list(AUX_YEARS),
        },
        "sources": {
            "wvs": str(wvs_path),
            "gps": str(gps_path),
            "wdi": "World Bank WDI (NY.GDP.PCAP.PP.KD, SI.POV.GINI, SL.AGR.EMPL.ZS)",
            "wgi": "World Bank WGI rule_of_law (rl)",
        },
        "scores_hash": canonical_csv_hash(scores),
        "parent_sha": parent_sha,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
    }
    (out_dir / "score_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")

    print(f"      n={len(scores)}; scores_hash={manifest['scores_hash'][:16]}...")
    for m in MEASURE_COLUMNS + ["m_noise", "m_share_agriculture"]:
        print(f"      {m:24s} mean={scores[m].mean():.4f} std={scores[m].std():.4f}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--raw-root", type=Path, default=Path("data/h5_trust_raw"))
    parser.add_argument("--aux-dir", type=Path, default=Path("data/h5_trust_aux"))
    parser.add_argument("--out-dir", type=Path, default=Path("evals/h5_trust/data"))
    parser.add_argument("--seed", type=int, default=20260804)
    parser.add_argument("--floor", type=int, default=200)
    parser.add_argument("--wvs-file", default="WVS_wave7.dta")
    parser.add_argument("--gps-file", default="country_gps.dta")
    parser.add_argument("--country-col", default="B_COUNTRY_ALPHA")
    parser.add_argument("--fetch-wdi", action="store_true", help="fetch WDI indicators into the aux cache and exit")
    parser.add_argument("--fetch-wgi", action="store_true", help="fetch WGI rule-of-law workbook into the aux cache and exit")
    args = parser.parse_args()

    if args.fetch_wdi:
        fetch_wdi_aux(args.aux_dir)
        return
    if args.fetch_wgi:
        fetch_wgi_aux(args.aux_dir)
        return

    real_items = {
        k: [WVS_REAL_ITEM_COLUMNS[c] for c in v] for k, v in DEFAULT_ITEM_GROUPS.items()
    }
    build(
        raw_root=args.raw_root,
        aux_dir=args.aux_dir,
        out_dir=args.out_dir,
        seed=args.seed,
        floor=args.floor,
        wvs_file=args.wvs_file,
        gps_file=args.gps_file,
        item_groups=real_items,
        country_col=args.country_col,
    )


if __name__ == "__main__":
    main()
