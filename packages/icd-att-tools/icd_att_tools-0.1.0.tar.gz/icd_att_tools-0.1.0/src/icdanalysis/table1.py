#!/usr/bin/env python3
"""Generate Table 1 descriptive statistics at the index date.

The script summarises baseline covariates (counts & percentages) and continuous
variables (means, medians, etc.) for Overall, Case, and Control samples. It also
reports follow-up availability in terms of the number of observed event-time
periods per parent. Designed to feed into a downstream LaTeX table.

Example
-------
uv run python PYTHON/generate_table1_v2.py \
    --input data/panel_dataset.parquet \
    --output-dir results/table1 \
    --baseline -1
"""

from __future__ import annotations

import argparse
import logging
import os
from dataclasses import dataclass
from typing import List, Optional, Sequence, SupportsInt, Tuple, cast

import numpy as np
import pandas as pd

# Optional third-party helper; comment out if you prefer not to depend on it.
try:
    from tabulate import tabulate  # noqa: F401
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

LOGGER = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Configuration
# --------------------------------------------------------------------------- #

CATEGORICAL_VARS: Sequence[str] = (
    "employment_category",
    "education_category",
    "ethnicity_category",
    "cohabitation_category",
    "parent_type",
    "gender",  # derived if missing
    "parity_category",
)

DEFAULT_OUTCOME_COLUMNS: Sequence[str] = (
    "PERINDKIALT_13_winsorized",
    "LOENMV_13_winsorized",
)

CHILD_BIRTH_CANDIDATES: Sequence[str] = (
    "BARN_FOEDSELSDATO",
    "child_birthdate",
    "child_birthday",
)

PARENT_BIRTH_CANDIDATES: Sequence[str] = (
    "parent_birthdate",
    "parent_birthday",
)

INDEX_DATE = "INDEX_DATE"

SAMPLES: Sequence[Tuple[str, Optional[int]]] = (
    ("overall", None),
    ("case", 1),
    ("control", 0),
)


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Input dataset (parquet or CSV).")
    parser.add_argument("--output-dir", required=True, help="Directory for result CSV files.")
    parser.add_argument("--baseline", type=int, default=-1, help="Baseline RELATIVE_YEAR (default: -1).")
    parser.add_argument("--weight-column", default=None, help="Optional sampling weight column.")
    parser.add_argument("--drop-missing", action="store_true", help="Drop rows with missing covariates.")
    parser.add_argument("--verbose", action="store_true", help="Print progress messages.")
    parser.add_argument("--show-summary", action="store_true", help="Pretty-print summaries to stdout.")
    parser.add_argument(
        "--outcome-columns",
        nargs="*",
        default=list(DEFAULT_OUTCOME_COLUMNS),
        help=(
            "Continuous outcome columns to summarize (defaults to "
            "PERINDKIALT_13_winsorized and LOENMV_13_winsorized)."
        ),
    )
    return parser.parse_args(argv)


def load_dataset(path: str) -> pd.DataFrame:
    if path.endswith(".parquet"):
        return pd.read_parquet(path)
    if path.endswith(".csv"):
        return pd.read_csv(path)
    raise ValueError("Unsupported file format. Use .parquet or .csv.")


def ensure_datetime(series: pd.Series) -> pd.Series:
    return pd.to_datetime(series, errors="coerce")


def get_series(df: pd.DataFrame, column: str) -> pd.Series:
    value = df[column]
    if isinstance(value, pd.Series):
        return value
    raise TypeError(f"Column '{column}' is not a Series.")


def try_get_series(df: pd.DataFrame, column: str) -> Optional[pd.Series]:
    if column not in df.columns:
        return None
    value = df[column]
    if isinstance(value, pd.Series):
        return value
    raise TypeError(f"Column '{column}' is not a Series.")


def compute_age(reference: pd.Series, birth: pd.Series) -> pd.Series:
    ref = ensure_datetime(reference)
    birth = ensure_datetime(birth)
    delta = cast(pd.Series, ref - birth)
    seconds = cast(pd.Series, delta.dt.total_seconds())
    return seconds / (365.25 * 24 * 3600)


def derive_gender(df: pd.DataFrame) -> pd.Series:
    if "gender" in df.columns:
        return get_series(df, "gender").astype("string")

    gender = pd.Series("unknown", index=df.index, dtype="string")
    if "parent_type" in df.columns:
        parent = get_series(df, "parent_type").astype("string").str.lower().str.strip()
        gender[parent.isin({"mother", "mor", "m", "moder"})] = "female"
        gender[parent.isin({"father", "far", "f", "fader"})] = "male"

    for candidate in ("gender_code", "gender_flag", "sex"):
        if candidate in df.columns:
            code = get_series(df, candidate).astype("string").str.lower().str.strip()
            gender[code.isin({"female", "f", "kvinde", "2"})] = "female"
            gender[code.isin({"male", "m", "mand", "1"})] = "male"
            break

    return gender


def weighted_counts(series: pd.Series, weights: Optional[pd.Series]) -> Tuple[pd.Series, float]:
    if weights is None:
        counts = series.value_counts(dropna=False, sort=False)
        total = float(counts.sum())
    else:
        working = pd.DataFrame({"cat": series, "w": weights})
        counts = working.groupby("cat")[["w"]].sum()["w"]
        total = float(counts.sum())
    return counts, total

def derive_parity(df: pd.DataFrame) -> pd.Series:
    if "parity_category" in df.columns:
        return get_series(df, "parity_category").astype("string")
    if "PARITET_CAT" in df.columns:
        parity_numeric = pd.to_numeric(get_series(df, "PARITET_CAT"), errors="coerce")
        parity = cast(pd.Series, parity_numeric).fillna(0).astype(int)
        labels = parity.map({0: "unknown", 1: "1", 2: "2"}).astype("string")
        labels[parity >= 3] = "3+"
        return labels
    return pd.Series("unknown", index=df.index, dtype="string")


@dataclass
class ContinuousStats:
    variable: str
    sample: str
    mean: float
    std: float
    median: float
    q1: float
    q3: float
    minimum: float
    maximum: float
    n: int
    weighted: bool


def summarize_continuous(
    series: pd.Series,
    sample: str,
    variable: str,
    weights: Optional[pd.Series],
) -> ContinuousStats:
    numeric = pd.to_numeric(series, errors="coerce")
    clean = cast(pd.Series, numeric).dropna()
    if clean.empty:
        return ContinuousStats(variable, sample, *(float("nan"),) * 7, 0, weights is not None)

    if weights is not None:
        weight_slice = cast(pd.Series, weights.loc[clean.index])
        w = weight_slice.to_numpy(dtype=float)
        x = clean.to_numpy(dtype=float)
        total = w.sum()
        mean = float(np.average(x, weights=w))
        variance = float(np.average((x - mean) ** 2, weights=w))
        std = float(np.sqrt(variance))
        sorter = np.argsort(x)
        x_sorted = x[sorter]
        w_sorted = w[sorter]
        cdf = np.cumsum(w_sorted) / total

        def w_quantile(q: float) -> float:
            return float(np.interp(q, cdf, x_sorted))

        median = w_quantile(0.5)
        q1 = w_quantile(0.25)
        q3 = w_quantile(0.75)
    else:
        x = clean.to_numpy(dtype=float)
        mean = float(x.mean())
        std = float(x.std(ddof=1))
        median = float(np.median(x))
        q1 = float(np.quantile(x, 0.25))
        q3 = float(np.quantile(x, 0.75))

    return ContinuousStats(
        variable=variable,
        sample=sample,
        mean=mean,
        std=std,
        median=median,
        q1=q1,
        q3=q3,
        minimum=float(x.min()),
        maximum=float(x.max()),
        n=int(clean.shape[0]),
        weighted=weights is not None,
    )


def summarize_followup(df: pd.DataFrame, sample: str, id_column: str) -> pd.DataFrame:
    sample_df_obj = df[[id_column, "RELATIVE_YEAR"]].dropna()
    sample_df = cast(pd.DataFrame, sample_df_obj)
    if sample_df.empty:
        return pd.DataFrame()

    id_series = get_series(sample_df, id_column)
    total_ids = int(id_series.nunique())
    # Coverage of each relative period
    coverage_counts_obj = sample_df.groupby("RELATIVE_YEAR", as_index=False)[id_column].nunique()
    coverage_counts = cast(pd.DataFrame, coverage_counts_obj).rename(columns={id_column: "subjects"})
    period_coverage = coverage_counts.assign(
        sample=sample,
        identifier=id_column,
        coverage_percent=lambda s: 100.0 * s["subjects"] / total_ids if total_ids else 0.0,
    )

    # Number of periods per id
    periods_series = cast(
        pd.Series, sample_df.groupby(id_column)["RELATIVE_YEAR"].nunique()
    )
    periods_per_id = periods_series.value_counts().sort_index()
    running = 0
    period_distribution = []
    for num_periods, freq in periods_per_id.items():
        num_periods_int = int(cast(SupportsInt, num_periods))
        freq_int = int(freq)
        running += freq_int
        period_distribution.append(
            {
                "sample": sample,
                "identifier": id_column,
                "periods": num_periods_int,
                "subjects": freq_int,
                "subjects_cumulative": running,
                "subjects_percent": 100.0 * running / total_ids if total_ids else 0.0,
            }
        )

    distribution_df = pd.DataFrame(period_distribution)
    distribution_df["metric"] = "periods_per_id"
    period_coverage["metric"] = "period_coverage"
    period_coverage = period_coverage.rename(columns={"RELATIVE_YEAR": "periods"})

    combined = pd.concat([distribution_df, period_coverage], ignore_index=True, sort=False)
    combined["total_subjects"] = total_ids
    return combined


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)
    df = load_dataset(args.input)

    if "RELATIVE_YEAR" not in df.columns:
        raise ValueError("Dataset must contain 'RELATIVE_YEAR' column.")
    if INDEX_DATE not in df.columns:
        raise ValueError("Dataset must contain 'INDEX_DATE' column.")

    df = df.copy()

    # Derive treatment indicator if not present
    if "treatment_indicator" in df.columns:
        ti_numeric = pd.to_numeric(get_series(df, "treatment_indicator"), errors="coerce")
        df["treatment_indicator"] = cast(pd.Series, ti_numeric)
    else:
        if "ROLE" not in df.columns:
            raise ValueError("Dataset must contain either 'treatment_indicator' or 'ROLE'.")
        role_obj = get_series(df, "ROLE")
        role_norm = role_obj.astype("string").str.lower().str.strip()
        df["treatment_indicator"] = role_norm.isin({"case", "treated", "treatment", "1", "true"}).astype(int)

    df["gender"] = derive_gender(df)
    df["parity_category"] = derive_parity(df)

    baseline_df = df.loc[df["RELATIVE_YEAR"] == args.baseline].copy()
    if baseline_df.empty:
        raise ValueError(f"No observations at RELATIVE_YEAR == {args.baseline}.")

    weights: Optional[pd.Series]
    if args.weight_column:
        if args.weight_column not in baseline_df.columns:
            raise ValueError(f"Weight column '{args.weight_column}' not found in dataset.")
        weight_numeric = pd.to_numeric(get_series(baseline_df, args.weight_column), errors="coerce")
        weights = cast(pd.Series, weight_numeric).fillna(0.0)
    else:
        weights = None

    child_age: Optional[pd.Series] = None
    for col in CHILD_BIRTH_CANDIDATES:
        if col in df.columns:
            child_age = compute_age(get_series(df, INDEX_DATE), get_series(df, col))
            break

    parent_age: Optional[pd.Series] = None
    for col in PARENT_BIRTH_CANDIDATES:
        if col in df.columns:
            parent_age = compute_age(get_series(df, INDEX_DATE), get_series(df, col))
            break

    categorical_rows: List[dict] = []
    continuous_rows: List[ContinuousStats] = []
    followup_frames: List[pd.DataFrame] = []

    id_column = "parent_pnr" if "parent_pnr" in df.columns else None
    if id_column is None:
        for candidate in ("PNR", "child_pnr"):
            if candidate in df.columns:
                id_column = candidate
                break

    sample_weights: Optional[pd.Series]
    for sample_name, treat_flag in SAMPLES:
        if treat_flag is None:
            sample_baseline = baseline_df
            sample_weights = weights
        else:
            treat_mask = get_series(baseline_df, "treatment_indicator") == treat_flag
            sample_baseline = baseline_df.loc[treat_mask]
            sample_weights = (
                cast(pd.Series, weights.loc[sample_baseline.index])
                if weights is not None
                else None
            )
        if sample_baseline.empty:
            continue

        if sample_weights is not None:
            sample_total = float(sample_weights.sum())
        else:
            sample_total = float(sample_baseline.shape[0])

        for cat in CATEGORICAL_VARS:
            if cat not in sample_baseline.columns:
                continue
            categories = get_series(sample_baseline, cat)
            if args.drop_missing:
                categories = categories.dropna()
            counts, total = weighted_counts(categories, sample_weights)
            counts = counts.sort_values(ascending=False)
            for category, count in counts.items():
                categorical_rows.append(
                    {
                        "sample": sample_name,
                        "variable": cat,
                        "category": str(category),
                        "count": float(count),
                        "percent": float(100.0 * count / total) if total else 0.0,
                        "total_sample": sample_total,
                        "weighted": sample_weights is not None,
                    }
                )

        if child_age is not None:
            continuous_rows.append(
                summarize_continuous(child_age.loc[sample_baseline.index], sample_name, "child_age_years", sample_weights)
            )
        if parent_age is not None:
            continuous_rows.append(
                summarize_continuous(parent_age.loc[sample_baseline.index], sample_name, "parent_age_years", sample_weights)
            )

        seen_outcome_cols = set()
        for outcome in args.outcome_columns:
            candidate_columns: List[str] = []
            if outcome in df.columns:
                candidate_columns.append(outcome)
            else:
                LOGGER.warning("Outcome column '%s' missing; skipping.", outcome)
            for col in candidate_columns:
                if col in seen_outcome_cols:
                    continue
                seen_outcome_cols.add(col)
                continuous_rows.append(
                    summarize_continuous(
                        df.loc[sample_baseline.index, col], sample_name, col, sample_weights
                    )
                )

        if id_column:
            relative_years = get_series(df, "RELATIVE_YEAR")
            sample_full = df.loc[relative_years.notna()].copy()
            if treat_flag is not None:
                ti_series = get_series(sample_full, "treatment_indicator")
                sample_full = sample_full.loc[ti_series == treat_flag]
            if not sample_full.empty:
                followup_frames.append(summarize_followup(sample_full, sample_name, id_column))

    os.makedirs(args.output_dir, exist_ok=True)

    cat_df = pd.DataFrame(categorical_rows)
    cont_df = pd.DataFrame([vars(stat) for stat in continuous_rows])
    follow_df = pd.concat(followup_frames, ignore_index=True) if followup_frames else pd.DataFrame()

    cat_path = os.path.join(args.output_dir, "table1_categorical.csv")
    cont_path = os.path.join(args.output_dir, "table1_continuous.csv")
    follow_path = os.path.join(args.output_dir, "table1_followup.csv")

    cat_df.to_csv(cat_path, index=False)
    cont_df.to_csv(cont_path, index=False)
    follow_df.to_csv(follow_path, index=False)

    if args.verbose:
        print(f"Wrote categorical summary to {cat_path}")
        print(f"Wrote continuous summary to {cont_path}")
        print(f"Wrote follow-up availability to {follow_path}")

    if args.show_summary:
        if HAS_TABULATE:
            print("\nCategorical summary")
            print(tabulate(cat_df.head(20).to_dict(orient="records"), headers="keys"))  # type: ignore[arg-type]
            print("\nContinuous summary")
            print(tabulate(cont_df.head(20).to_dict(orient="records"), headers="keys"))  # type: ignore[arg-type]
            if not follow_df.empty:
                print("\nFollow-up availability")
                print(tabulate(follow_df.head(20).to_dict(orient="records"), headers="keys"))  # type: ignore[arg-type]
        else:
            print("tabulate not installed; use --verbose to see file paths")


if __name__ == "__main__":  # pragma: no cover
    main()
