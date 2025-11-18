#!/usr/bin/env python3
"""Event-study preprocessing utilities.

This script reads a parquet dataset and adds the high-level categorizations used
throughout the project.  It consolidates the R-based logic from the
`PYTHON/r-categorization` helpers into a lightweight Python CLI:

* Employment category from `SOCIO13`
* Education category from `ISCED`
* Ethnicity category from `PARENT_OPR_LAND`, `CHILD_OPR_LAND`, `CHILD_IE_TYPE`
* Cohabitation category from `FAMILIE_TYPE`, `CIVST`, `CIV_VFRA`
* Winsorised versions of `PERINDKIALT_13` and `LOENMV_13`

Example
-------

```
uv run python PYTHON/preprocessing.py \
  --input data/raw_dataset.parquet \
  --output data/preprocessed_dataset.parquet
```
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

LOGGER = logging.getLogger(__name__)

# Sets replicated from the R categorisation helpers
DANISH_COUNTRY_CODES = {"5100", "5101", "5115", "5901", "5902"}
WESTERN_COUNTRY_CODES = {
    "5104",
    "5105",
    "5106",
    "5107",
    "5108",
    "5109",
    "5110",
    "5111",
    "5116",
    "5120",
    "5124",
    "5126",
    "5128",
    "5129",
    "5130",
    "5134",
    "5140",
    "5142",
    "5150",
    "5153",
    "5154",
    "5156",
    "5158",
    "5159",
    "5160",
    "5164",
    "5170",
    "5174",
    "5176",
    "5180",
    "5182",
    "5184",
    "5314",
    "5390",
    "5397",
    "5399",
    "5422",
    "5502",
    "5514",
    "5607",
    "5609",
    "5611",
    "5750",
    "5752",
    "5776",
    "5778",
}
REGION_PREFIX_MAP = {
    "01": "danish_origin",
    "02": "western",
    "03": "non_western",
}

FAMILIE_TYPE_COHABITING = {1, 2, 3, 4, 7, 8}
FAMILIE_TYPE_ALONE = {5, 9, 10}
CIVST_MARRIED = {"G", "P"}
CIVST_NOT_MARRIED = {"U", "F", "O", "E", "L"}

SOCIO13_WORKING = {110, 111, 112, 113, 114, 120, 131, 132, 133, 134, 135, 139, 310}
SOCIO13_UNEMPLOYED = {210, 410}
SOCIO13_OUTSIDE = {330, 220, 321}
SOCIO13_RETIRED = {323, 322}

DEFAULT_CPI_BASE_YEAR = 2015

ANNUAL_CPI_INDEX = {
    2000: 76.2167,
    2001: 78.0250,
    2002: 79.9167,
    2003: 81.5750,
    2004: 82.5167,
    2005: 84.0167,
    2006: 85.6333,
    2007: 87.0833,
    2008: 90.0583,
    2009: 91.2333,
    2010: 93.3417,
    2011: 95.9167,
    2012: 98.2167,
    2013: 98.9917,
    2014: 99.5500,
    2015: 100.0000,
    2016: 100.2500,
    2017: 101.4000,
    2018: 102.2250,
    2019: 103.0000,
    2020: 103.4333,
    2021: 105.3500,
    2022: 113.4583,
    2023: 117.2083,
    2024: 118.8167,
    2025: 120.9900,
}

DKK_PER_EUR = 7.45  # Fixed conversion rate to report amounts in EUR


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Path to the input parquet dataset.")
    parser.add_argument("--output", required=True, help="Path to the output parquet dataset.")
    parser.add_argument(
        "--winsor-lower",
        type=float,
        default=0.01,
        help="Lower tail probability for winsorisation (default: 0.01).",
    )
    parser.add_argument(
        "--winsor-upper",
        type=float,
        default=0.99,
        help="Upper tail probability for winsorisation (default: 0.99).",
    )
    parser.add_argument(
        "--cpi-base-year",
        type=int,
        default=None,
        help="Reference year for CPI deflation (default: latest year available).",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity (default: INFO).",
    )
    return parser.parse_args(argv)


def configure_logging(level: str) -> None:
    logging.basicConfig(
        level=getattr(logging, level),
        format="[%(levelname)s] %(message)s",
    )


def categorize_employment(series: pd.Series) -> pd.Series:
    codes = pd.to_numeric(series, errors="coerce")
    categories = pd.Series("Missing/other", index=series.index, dtype="string")

    categories[codes.isin(list(SOCIO13_WORKING))] = "Working/Student"
    categories[codes.isin(list(SOCIO13_UNEMPLOYED))] = "Temporarily unemployed"
    categories[codes.isin(list(SOCIO13_OUTSIDE))] = "Outside workforce"
    categories[codes.isin(list(SOCIO13_RETIRED))] = "Retired"

    return categories.astype("string")


def categorize_education(series: pd.Series) -> pd.Series:
    levels = pd.to_numeric(series, errors="coerce")
    categories = pd.Series("Unknown", index=series.index, dtype="string")

    categories[levels <= 2] = "Short education"
    categories[levels.isin([3, 4])] = "Medium education"
    categories[levels >= 5] = "Long education"
    categories[levels == 9] = "Unknown"

    categories[pd.isna(levels)] = "Unknown"
    return categories.astype("string")


def _normalise_country_code(value: object) -> Optional[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value).strip().upper()
    if not text:
        return None
    text = text.replace(" ", "")
    if text.startswith("D") and len(text) > 1 and text[1:].isdigit():
        text = text[1:]
    return text


def _classify_region(code: Optional[str]) -> Optional[str]:
    if not code:
        return None

    if code in DANISH_COUNTRY_CODES:
        return "danish_origin"
    if code in WESTERN_COUNTRY_CODES:
        return "western"

    if code.isdigit():
        prefix = code[:2]
        if prefix in REGION_PREFIX_MAP:
            return REGION_PREFIX_MAP[prefix]

    return "non_western"


def _split_parent_codes(value: object) -> List[str]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return []
    text = str(value).strip()
    if not text:
        return []
    separators = [";", ",", "|"]
    for sep in separators:
        if sep in text:
            parts = [part for part in text.split(sep) if part]
            normalized = [_normalise_country_code(part) for part in parts]
            return [code for code in normalized if code]
    parts = text.split()
    if len(parts) > 1:
        normalized = [_normalise_country_code(part) for part in parts]
        return [code for code in normalized if code]
    code = _normalise_country_code(text)
    return [code] if code else []


def categorize_ethnicity(
    child_country: pd.Series,
    parent_country: pd.Series,
    child_ie_type: pd.Series,
) -> pd.Series:
    child_codes = child_country.map(_normalise_country_code)
    parent_codes = parent_country.map(_split_parent_codes)
    ie_types = pd.to_numeric(child_ie_type, errors="coerce")

    categories: List[str] = []
    for idx in child_country.index:
        child_code = child_codes.at[idx]
        parents = [code for code in parent_codes.at[idx] if code]
        ie_type = ie_types.at[idx]

        child_danish = child_code in DANISH_COUNTRY_CODES
        child_western = child_code in WESTERN_COUNTRY_CODES
        child_non_western = (
            child_code not in DANISH_COUNTRY_CODES
            and child_code not in WESTERN_COUNTRY_CODES
            and child_code is not None
        )

        parents_danish = parents and all(code in DANISH_COUNTRY_CODES for code in parents)
        parents_western = parents and any(code in WESTERN_COUNTRY_CODES for code in parents)
        parents_non_western = parents and any(
            (code not in DANISH_COUNTRY_CODES) and (code not in WESTERN_COUNTRY_CODES)
            for code in parents
        )

        if ie_type == 1:
            categories.append("Danish Origin")
            continue

        if child_danish and (not parents or parents_danish):
            categories.append("Danish Origin")
            continue

        if child_western:
            categories.append("Western")
            continue

        if child_non_western:
            categories.append("Non-Western")
            continue

        if child_danish and parents_western and not parents_non_western:
            categories.append("Western")
            continue

        if child_danish and parents_non_western:
            categories.append("Non-Western")
            continue

        if parents_western and not parents_non_western:
            categories.append("Western")
            continue

        if parents_non_western:
            categories.append("Non-Western")
            continue

        if ie_type in {2, 3}:
            categories.append("Non-Western")
            continue

        categories.append("Unknown")

    return pd.Series(categories, index=child_country.index, dtype="string")


def categorize_cohabitation(
    familie_type: pd.Series,
    civst: pd.Series,
    civ_vfra: pd.Series,
) -> pd.Series:
    familie_codes = pd.to_numeric(familie_type, errors="coerce")
    civst_codes = civst.astype("string").str.upper().str.strip()

    cohab_status = pd.Series("Missing", index=familie_type.index, dtype="string")
    cohab_status[familie_codes.isin(list(FAMILIE_TYPE_COHABITING))] = "Cohabiting"
    cohab_status[familie_codes.isin(list(FAMILIE_TYPE_ALONE))] = "Living alone"

    marital_status = pd.Series("Missing", index=civst.index, dtype="string")
    marital_status[civst_codes.isin(list(CIVST_MARRIED))] = "Married"
    marital_status[civst_codes.isin(list(CIVST_NOT_MARRIED))] = "Not married"

    labels: List[str] = []
    for idx in familie_type.index:
        cohab = cohab_status.at[idx]
        marital = marital_status.at[idx]

        if cohab == "Cohabiting" or marital == "Married":
            labels.append("Cohabiting/Married")
        elif cohab == "Living alone" or marital == "Not married":
            labels.append("LivingAlone/NotMarried")
        else:
            labels.append("LivingAlone/NotMarried")

    return pd.Series(labels, index=familie_type.index, dtype="string")


def winsorise(series: pd.Series, lower: float, upper: float) -> pd.Series:
    if series.dropna().empty:
        return series
    quantiles = series.quantile([lower, upper])
    lower_bound = quantiles.iloc[0]
    upper_bound = quantiles.iloc[1]
    return series.clip(lower=lower_bound, upper=upper_bound)


def winsorise_by_group(
    df: pd.DataFrame,
    column: str,
    group_column: str,
    lower: float,
    upper: float,
) -> pd.Series:
    if group_column not in df.columns:
        raise KeyError(f"Grouping column '{group_column}' not found in dataframe.")

    numeric = pd.to_numeric(df[column], errors="coerce")
    grouped = numeric.groupby(df[group_column], observed=True)
    lower_bounds = grouped.quantile(lower)
    upper_bounds = grouped.quantile(upper)

    lower_map = lower_bounds.reindex(df[group_column]).to_numpy()
    upper_map = upper_bounds.reindex(df[group_column]).to_numpy()

    global_quantiles = numeric.quantile([lower, upper])
    global_lower = global_quantiles.iloc[0]
    global_upper = global_quantiles.iloc[1]

    lower_map = np.where(np.isnan(lower_map), global_lower, lower_map)
    upper_map = np.where(np.isnan(upper_map), global_upper, upper_map)

    clipped = np.clip(numeric.to_numpy(dtype=float), lower_map, upper_map)
    return pd.Series(clipped, index=df.index)


def deflate_outcomes(
    df: pd.DataFrame,
    base_year: Optional[int],
    outcomes: Sequence[str] = ("PERINDKIALT_13", "LOENMV_13"),
) -> pd.DataFrame:
    if "YEAR" not in df.columns:
        LOGGER.warning("Column 'YEAR' missing; skipping CPI deflation.")
        return df

    cpi_df = pd.DataFrame(
        {"YEAR": list(ANNUAL_CPI_INDEX.keys()), "CPI_VALUE": list(ANNUAL_CPI_INDEX.values())}
    )
    df = df.copy()
    max_year = int(df["YEAR"].max())
    last_cpi_year = int(cpi_df["YEAR"].max())
    if max_year > last_cpi_year:
        last_value = float(cpi_df.loc[cpi_df["YEAR"] == last_cpi_year, "CPI_VALUE"].iloc[0])
        extra_years = pd.DataFrame(
            {"YEAR": range(last_cpi_year + 1, max_year + 1), "CPI_VALUE": last_value}
        )
        cpi_df = pd.concat([cpi_df, extra_years], ignore_index=True)

    reference_year = base_year if base_year is not None else DEFAULT_CPI_BASE_YEAR
    if reference_year not in set(cpi_df["YEAR"]):
        raise ValueError(f"Reference year {reference_year} not available in CPI table.")
    reference_value = float(
        cpi_df.loc[cpi_df["YEAR"] == reference_year, "CPI_VALUE"].iloc[0]
    )
    cpi_df["__deflator"] = reference_value / cpi_df["CPI_VALUE"]

    df = df.merge(cpi_df[["YEAR", "__deflator"]], on="YEAR", how="left")
    if df["__deflator"].isna().any():
        missing = df.loc[df["__deflator"].isna(), "YEAR"].unique()
        LOGGER.warning(
            "Missing CPI values for years: %s. Using reference-year deflator instead.",
            ", ".join(map(str, sorted(missing))),
        )
        df["__deflator"] = df["__deflator"].fillna(1.0)

    LOGGER.info(
        "Deflating monetary outcomes using CPI reference year %s (value %.2f)",
        reference_year,
        reference_value,
    )

    for outcome in outcomes:
        if outcome not in df.columns:
            LOGGER.warning("Outcome column '%s' missing; skipping deflation.", outcome)
            continue
        nominal_dkk = df[outcome]
        df[f"{outcome}_nominal_dkk"] = nominal_dkk
        df[f"{outcome}_nominal_eur"] = nominal_dkk / DKK_PER_EUR
        df[f"{outcome}_deflated_dkk"] = nominal_dkk * df["__deflator"]
        df[f"{outcome}_deflated_eur"] = df[f"{outcome}_deflated_dkk"] / DKK_PER_EUR
        df[f"{outcome}_deflated"] = df[f"{outcome}_deflated_eur"]
        df[outcome] = df[f"{outcome}_deflated_eur"]

    df = df.drop(columns="__deflator")
    return df


def add_categorizations(
    df: pd.DataFrame,
    winsor_lower: float,
    winsor_upper: float,
) -> pd.DataFrame:
    enriched = df.copy()

    if "SOCIO13" in enriched.columns:
        LOGGER.info("Creating employment_category from SOCIO13")
        enriched["employment_category"] = categorize_employment(enriched["SOCIO13"])
    else:
        LOGGER.warning("Column 'SOCIO13' not found; skipping employment categorization.")

    if "ISCED" in enriched.columns:
        LOGGER.info("Creating education_category from ISCED")
        enriched["education_category"] = categorize_education(enriched["ISCED"])
    else:
        LOGGER.warning("Column 'ISCED' not found; skipping education categorization.")

    required_ethnicity_cols = {"PARENT_OPR_LAND", "CHILD_OPR_LAND", "CHILD_IE_TYPE"}
    if required_ethnicity_cols.issubset(enriched.columns):
        LOGGER.info("Creating ethnicity_category from origin columns")
        enriched["ethnicity_category"] = categorize_ethnicity(
            enriched["CHILD_OPR_LAND"],
            enriched["PARENT_OPR_LAND"],
            enriched["CHILD_IE_TYPE"],
        )
    else:
        missing = required_ethnicity_cols - set(enriched.columns)
        LOGGER.warning(
            "Skipping ethnicity categorization; missing columns: %s", ", ".join(sorted(missing))
        )

    required_cohab_cols = {"FAMILIE_TYPE", "CIVST", "CIV_VFRA"}
    if required_cohab_cols.issubset(enriched.columns):
        LOGGER.info("Creating cohabitation_category from family and civil status columns")
        enriched["cohabitation_category"] = categorize_cohabitation(
            enriched["FAMILIE_TYPE"],
            enriched["CIVST"],
            enriched["CIV_VFRA"],
        )
    else:
        missing = required_cohab_cols - set(enriched.columns)
        LOGGER.warning(
            "Skipping cohabitation categorization; missing columns: %s",
            ", ".join(sorted(missing)),
        )

    group_column = "YEAR"
    for outcome in ("PERINDKIALT_13", "LOENMV_13"):
        if outcome in enriched.columns:
            if group_column in enriched.columns:
                LOGGER.info(
                    "Winsorising %s by %s (%.2f, %.2f)",
                    outcome,
                    group_column,
                    winsor_lower,
                    winsor_upper,
                )
                enriched[f"{outcome}_winsorized"] = winsorise_by_group(
                    enriched,
                    outcome,
                    group_column,
                    winsor_lower,
                    winsor_upper,
                )
            else:
                LOGGER.warning(
                    "Grouping column '%s' missing; applying global winsorisation to %s.",
                    group_column,
                    outcome,
                )
                enriched[f"{outcome}_winsorized"] = winsorise(
                    pd.to_numeric(enriched[outcome], errors="coerce"),
                    winsor_lower,
                    winsor_upper,
                )
        else:
            LOGGER.warning("Outcome column '%s' not found; skipping winsorisation.", outcome)

    return enriched


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    configure_logging(args.log_level)

    input_path = Path(args.input)
    output_path = Path(args.output)

    LOGGER.info("Reading parquet data from %s", input_path)
    df = pd.read_parquet(input_path)

    df = deflate_outcomes(df, args.cpi_base_year)

    enriched = add_categorizations(df, args.winsor_lower, args.winsor_upper)

    LOGGER.info("Writing enriched data to %s", output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    enriched.to_parquet(output_path, index=False)
    LOGGER.info("Preprocessing completed successfully.")


if __name__ == "__main__":
    main()
