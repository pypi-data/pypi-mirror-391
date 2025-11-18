#!/usr/bin/env python3

"""Main estimation pipeline for ICD-based double-robust ATT effects.

This script expects a prepared panel dataset containing matched cases and
controls with the following columns:

- MATCH_INDEX: identifier shared by a treated individual and its matched controls
- ROLE: indicates whether the row belongs to the treated case ("case") or a control
- INDEX_DATE: index timestamp (used for informational outputs only)
- BARN_FOEDSELSDATO: child date of birth (optional, not used directly)
- PARITET_CAT, SCD_STATUS: optional stratifying metadata (not used directly)
- ICD_CODE: ICD-10 code associated with the treated case/cohort
- parent_type, cpr_parent, parent_birthday, child_pnr, parent_pnr: metadata
- RELATIVE_YEAR: event time relative to the baseline (e.g., -3 .. +k)
- PERINDKIALT_13, LOENMV_13: numeric outcome columns
- YEAR: calendar year (optional for reporting)
- SOCIO13, FAMILIE_TYPE, CIVST, CIV_VFRA, PARENT_OPR_LAND,
  CHILD_OPR_LAND, CHILD_IE_TYPE, ISCED, HFAUDD: auxiliary columns

The script estimates ATT effects for each ICD chapter (derived from ICD_CODE)
and user-specified outcome columns using the panel double-robust estimator
(`drdid_panel`). Results are written to CSV files in the supplied output
directory.
"""

from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from statistics import NormalDist
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd
from csdid.utils.bmisc import multiplier_bootstrap
from patsy import dmatrix
from tqdm import tqdm

try:  # pragma: no cover - validated at runtime
    from drdid.drdid import drdid_panel  # type: ignore[attr-defined]
except Exception as exc:  # pragma: no cover
    raise ImportError(
        "The 'drdid' package is required. Install it via 'uv pip install drdid'."
    ) from exc

from .resolve_chapters import resolve_icd_chapters  # type: ignore


###############################################################################
# Argument parsing and logging helpers
###############################################################################


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", required=True, help="Path to the input parquet file."
    )
    parser.add_argument(
        "--output-dir", required=True, help="Directory for result CSV files."
    )
    parser.add_argument(
        "--outcome-columns",
        nargs="*",
        default=["PERINDKIALT_13_winsorized", "LOENMV_13_winsorized"],
        help=(
            "Outcome columns for ATT estimation "
            "(default: PERINDKIALT_13_winsorized LOENMV_13_winsorized)."
        ),
    )
    parser.add_argument(
        "--baseline",
        type=int,
        default=-1,
        help="Baseline relative year (default: -1).",
    )
    parser.add_argument(
        "--min-treated",
        type=int,
        default=25,
        help="Minimum treated individuals at baseline required to estimate a chapter (default: 25).",
    )
    parser.add_argument(
        "--adjustments",
        nargs="*",
        default=[
            "employment_category",
            "education_category",
            "ethnicity_category",
            "cohabitation_category",
        ],
        help="Adjustment covariates for the DR estimator (default: employment/education/ethnicity/cohabitation categories).",
    )
    parser.add_argument(
        "--covariate-formula",
        default=None,
        help="Patsy formula (RHS) for covariates used in propensity/outcome models (e.g., '~ 1 + age + C(gender)'). Overrides --adjustments.",
    )
    parser.add_argument(
        "--weight-column",
        default=None,
        help="Optional column containing sampling weights.",
    )
    parser.add_argument(
        "--bootstrap-iterations",
        type=int,
        default=1000,
        help="Number of multiplier bootstrap draws for inference (default: 1000). Set to 0 to disable.",
    )
    parser.add_argument(
        "--uniform-band",
        action="store_true",
        help="Use multiplier bootstrap to compute uniform confidence bands for aggregated ATT outputs.",
    )
    parser.add_argument(
        "--horizon-breaks",
        nargs="*",
        type=int,
        default=[0, 3, 7, 11],
        help=(
            "Sorted event-time cut points (in years) used to form short/medium/long"
            " horizon aggregates. Bounds refer to post-baseline event times; default"
            " [0,3,7,11] yields buckets [0,2], [3,6], [7,10], [11,+]."
        ),
    )
    parser.add_argument(
        "--alpha",
        type=float,
        default=0.05,
        help="Significance level for confidence intervals (default: 0.05).",
    )
    parser.add_argument(
        "--samples",
        nargs="*",
        choices=["all", "mother", "father"],
        default=["all", "mother", "father"],
        help=(
            "Samples to estimate (default: all, mother, father). Requires 'parent_type' column for mother/father splits."
        ),
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable detailed debug output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable progress bars and verbose logging.",
    )
    parser.add_argument(
        "--estimation-strategy",
        choices=["sequential", "fixed_baseline"],
        default="fixed_baseline",
        help="Strategy for creating time pairs: 'sequential' uses consecutive periods, 'fixed_baseline' uses baseline as reference for all post periods (default: fixed_baseline).",
    )
    parser.add_argument(
        "--max-post-periods",
        type=int,
        default=None,
        help="Maximum number of post-treatment periods to estimate (default: all available).",
    )
    return parser.parse_args(argv)


###############################################################################
# Core estimation helpers
###############################################################################


REQUIRED_COLUMNS: Sequence[str] = (
    "MATCH_INDEX",
    "ROLE",
    "INDEX_DATE",
    "ICD_CODE",
    "RELATIVE_YEAR",
    "child_pnr",
)


def validate_columns(df: pd.DataFrame, columns: Iterable[str]) -> None:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))


def derive_treatment_indicator(role_series: pd.Series) -> pd.Series:
    role = role_series.astype("string").str.lower().str.strip()
    treated = role.isin({"case", "treated", "treatment", "1", "true"})
    return treated.astype(int)


def prepare_dataframe(
    df: pd.DataFrame, weight_column: Optional[str], debug: bool = False
) -> pd.DataFrame:
    validate_columns(df, REQUIRED_COLUMNS)

    if df["ROLE"].isna().all():
        raise ValueError(
            "Column 'ROLE' contains only missing values; cannot determine treatment status."
        )

    enriched = df.copy()

    enriched["treatment_indicator"] = derive_treatment_indicator(enriched["ROLE"])
    enriched["treatment"] = enriched["treatment_indicator"]

    # Resolve ICD chapters for grouping
    chapter_labels, normalized_codes = resolve_icd_chapters(enriched, "ICD_CODE")
    enriched["icd_chapter"] = chapter_labels
    enriched["icd_code_normalized"] = normalized_codes

    if weight_column:
        if weight_column not in enriched.columns:
            raise ValueError(f"Weight column '{weight_column}' not found in data.")
        enriched[weight_column] = pd.to_numeric(
            enriched[weight_column], errors="coerce"
        )

    if debug:
        print(
            f"[DEBUG] Data prepared: {enriched.shape[0]} rows, {enriched.shape[1]} columns"
        )
        print(
            f"[DEBUG] Relative year range: {enriched['RELATIVE_YEAR'].min()} to {enriched['RELATIVE_YEAR'].max()}"
        )
        print(
            f"[DEBUG] Unique relative years: {sorted(enriched['RELATIVE_YEAR'].dropna().unique())}"
        )

    return enriched


def resolve_covariate_formula(
    adjustments: Sequence[str], explicit_formula: Optional[str]
) -> str:
    if explicit_formula:
        return explicit_formula

    if adjustments:
        quoted_terms = [f"Q('{col}')" for col in adjustments]
        rhs = "1 + " + " + ".join(quoted_terms)
    else:
        rhs = "1"
    return f"~ {rhs}"


def ensure_patsy_compatible(df: pd.DataFrame) -> pd.DataFrame:
    """Convert pandas extension types that Patsy cannot interpret."""
    compatible = df.copy()
    string_cols = compatible.select_dtypes(include="string").columns
    if len(string_cols) > 0:
        compatible[string_cols] = compatible[string_cols].astype("object")
    return compatible


def build_sample_sets(
    df: pd.DataFrame, requested: Sequence[str]
) -> Dict[str, pd.DataFrame]:
    samples: Dict[str, pd.DataFrame] = {"all": df}
    if "parent_type" in df.columns:
        parent = df["parent_type"].astype("string").str.lower().str.strip()
        mother_mask = parent.isin({"mother", "mor", "m", "moder"})
        father_mask = parent.isin({"father", "far", "f", "fader"})
        samples["mother"] = df[mother_mask]
        samples["father"] = df[father_mask]

    if requested:
        subset: Dict[str, pd.DataFrame] = {}
        for name in requested:
            key = name.lower()
            if key not in samples:
                raise ValueError(f"Requested sample '{name}' not available in data.")
            subset[key] = samples[key]
        return subset

    return samples


def build_chapter_dataset(
    df: pd.DataFrame,
    chapter_label: str,
    baseline: int,
) -> pd.DataFrame:
    treated_mask = (
        (df["icd_chapter"] == chapter_label)
        & (df["treatment_indicator"] == 1)
        & (df["RELATIVE_YEAR"] == baseline)
    )

    treated_matches = df.loc[treated_mask, "MATCH_INDEX"].dropna().unique()
    if treated_matches.size == 0:
        raise ValueError(
            f"No treated units with MATCH_INDEX for chapter '{chapter_label}'."
        )

    eligible_mask = (
        (df["icd_chapter"] == chapter_label) & (df["treatment_indicator"] == 1)
    ) | ((df["treatment_indicator"] == 0) & df["MATCH_INDEX"].isin(treated_matches))

    subset = df.loc[eligible_mask].copy()
    subset.sort_values(
        ["MATCH_INDEX", "RELATIVE_YEAR", "child_pnr"], inplace=True, na_position="last"
    )
    return subset


def compose_unit_keys(df: pd.DataFrame, columns: Sequence[str]) -> pd.Series:
    """Create deterministic unit identifiers from the provided columns."""
    if not columns:
        return pd.Series(
            (f"unit_{idx}" for idx in range(df.shape[0])), index=df.index, dtype="string"
        )
    keys = df[columns[0]].astype("string").fillna("NA")
    for col in columns[1:]:
        col_values = df[col].astype("string").fillna("NA")
        keys = keys + "|" + col_values
    return keys


@dataclass
class DidResult:
    chapter: str
    outcome: str
    sample: str
    reference_year: int
    relative_year: int
    estimate: float
    std_error: float
    conf_low: float
    conf_high: float
    n_pairs: int
    n_treated: int
    n_control: int
    convergence: str = "success"
    unit_ids: Optional[Tuple[str, ...]] = None
    influence: Optional[Tuple[float, ...]] = None


###############################################################################
# Aggregation helpers inspired by csdid::aggte
###############################################################################


def _ensure_confidence_bounds(
    df: pd.DataFrame, alpha: float, se_column: str = "std_error"
) -> pd.DataFrame:
    """Ensure confidence intervals exist by falling back to normal approximation."""
    if df.empty:
        return df
    if "conf_low" not in df.columns or "conf_high" not in df.columns:
        df = df.copy()
        df["conf_low"] = np.nan
        df["conf_high"] = np.nan
    crit = NormalDist().inv_cdf(1 - alpha / 2)
    needs_bounds = df["conf_low"].isna() | df["conf_high"].isna()
    if needs_bounds.any() and se_column in df.columns:
        se_available = df[se_column].notna()
        mask = needs_bounds & se_available
        if mask.any():
            df = df.copy()
            df.loc[mask, "conf_low"] = (
                df.loc[mask, "estimate"] - crit * df.loc[mask, se_column]
            )
            df.loc[mask, "conf_high"] = (
                df.loc[mask, "estimate"] + crit * df.loc[mask, se_column]
            )
    return df


def _normalize_weights(weights: pd.Series) -> np.ndarray:
    """Normalize weights; default to uniform if they do not sum to a positive value."""
    arr = weights.fillna(0.0).astype(float).to_numpy()
    total = arr.sum()
    if not np.isfinite(total) or total <= 0:
        if arr.size == 0:
            return arr
        return np.repeat(1.0 / arr.size, arr.size)
    return arr / total


def _filter_successful_estimates(df: pd.DataFrame) -> pd.DataFrame:
    """Keep rows with finite estimates and successful convergence status."""
    if df.empty:
        return df
    numeric_estimates = pd.to_numeric(df["estimate"], errors="coerce")
    valid = np.isfinite(numeric_estimates)
    filtered = df.loc[valid].copy()
    if filtered.empty:
        return filtered
    filtered["estimate"] = numeric_estimates.loc[filtered.index]
    if "convergence" in filtered.columns:
        status = filtered["convergence"].fillna("").str.lower()
        filtered = filtered[status.str.startswith("success")]
    return filtered


def _coerce_sequence(value: object) -> List:
    if value is None:
        return []
    if isinstance(value, float) and np.isnan(value):
        return []
    if isinstance(value, (list, tuple, np.ndarray)):
        return list(value)
    return [value]


def _build_phi_map(
    unit_ids_obj: object, influence_obj: object, sample_size: Optional[int]
) -> Dict[str, float]:
    ids = _coerce_sequence(unit_ids_obj)
    infl = _coerce_sequence(influence_obj)
    length = min(len(ids), len(infl))
    if length == 0:
        return {}
    n_obs = sample_size if sample_size and sample_size > 0 else length
    if n_obs <= 0:
        return {}
    scale = 1.0 / n_obs
    return {str(ids[i]): float(infl[i]) * scale for i in range(length)}


def _sum_numeric(rows: List[Dict[str, object]], indices: List[int], key: str) -> float:
    total = 0.0
    has_value = False
    for idx in indices:
        value = rows[idx].get(key)
        if value is None:
            continue
        try:
            fval = float(value)
        except (TypeError, ValueError):
            continue
        if np.isnan(fval):
            continue
        total += fval
        has_value = True
    return total if has_value else np.nan


def _aggregate_dynamic_series(
    df: pd.DataFrame,
    baseline: int,
    alpha: float,
    chapter: str,
    outcome: str,
    sample: str,
    cband: bool = False,
    biters: int = 0,
    horizon_breaks: Optional[Sequence[int]] = None,
) -> List[Dict[str, object]]:
    """Aggregate ATT series to a dynamic summary with covariance-aware SEs."""
    cleaned = _filter_successful_estimates(df)
    if cleaned.empty:
        return []

    cleaned = cleaned.sort_values("relative_year").copy()
    rows = cleaned.to_dict("records")
    for row in rows:
        row["event_time"] = int(row["relative_year"]) - baseline
        row.setdefault("conf_low", np.nan)
        row.setdefault("conf_high", np.nan)
        row.setdefault("std_error", np.nan)
        row.setdefault("weight", np.nan)

    num_events = len(rows)
    unit_vectors: Dict[str, np.ndarray] = {}
    for idx, row in enumerate(rows):
        n_obs = int(row.get("n_pairs") or 0)
        phi_map = _build_phi_map(row.get("unit_ids"), row.get("influence"), n_obs)
        if not phi_map:
            continue
        for uid, value in phi_map.items():
            vec = unit_vectors.setdefault(uid, np.zeros(num_events, dtype=float))
            vec[idx] = value

    if unit_vectors:
        inf_matrix = np.vstack(list(unit_vectors.values()))
    else:
        inf_matrix = np.zeros((0, num_events), dtype=float)

    if inf_matrix.size > 0:
        cov_matrix = inf_matrix.T @ inf_matrix
    else:
        cov_matrix = np.zeros((num_events, num_events), dtype=float)

    diag_var = np.diag(cov_matrix)
    tol = np.sqrt(np.finfo(float).eps) * 10
    se_vector = np.sqrt(np.maximum(diag_var, 0.0))
    se_vector = np.where(se_vector <= tol, np.nan, se_vector)

    crit_pointwise = NormalDist().inv_cdf(1 - alpha / 2)
    for idx, row in enumerate(rows):
        se_val = se_vector[idx] if idx < se_vector.size else np.nan
        if np.isfinite(se_val):
            row["std_error"] = float(se_val)
            row["conf_low"] = float(row["estimate"]) - crit_pointwise * float(se_val)
            row["conf_high"] = float(row["estimate"]) + crit_pointwise * float(se_val)
        else:
            row["std_error"] = np.nan
            row["conf_low"] = np.nan
            row["conf_high"] = np.nan
        row["band_type"] = "pointwise"
        row["critical_value"] = crit_pointwise
        row["horizon_start"] = None
        row["horizon_end"] = None
        row["horizon_label"] = None
        row["bucket_periods"] = None

    post_rows = [(idx, row) for idx, row in enumerate(rows) if row["relative_year"] > baseline]
    post_periods_count = len(post_rows)
    weight_candidates = pd.Series(
        [
            row.get("n_treated")
            if pd.notna(row.get("n_treated"))
            else row.get("n_pairs", 0.0)
            for _, row in post_rows
        ],
        dtype=float,
    )
    if post_periods_count > 0:
        weights = _normalize_weights(weight_candidates)
        for (idx, row), weight in zip(post_rows, weights):
            row["weight"] = float(weight)
        post_indices = [idx for idx, _ in post_rows]
        post_cov = cov_matrix[np.ix_(post_indices, post_indices)]
        overall_att = float(
            np.dot(weights, [rows[idx]["estimate"] for idx in post_indices])
        )
        overall_var = float(weights @ post_cov @ weights)
        overall_se = float(np.sqrt(max(overall_var, 0.0)))
        overall_low = (
            overall_att - crit_pointwise * overall_se if np.isfinite(overall_se) else np.nan
        )
        overall_high = (
            overall_att + crit_pointwise * overall_se if np.isfinite(overall_se) else np.nan
        )
        overall_row = {
            "chapter": chapter,
            "outcome": outcome,
            "sample": sample,
            "aggregation": "dynamic",
            "component": "overall",
            "relative_year": None,
            "event_time": None,
            "estimate": overall_att,
            "std_error": overall_se,
            "conf_low": overall_low,
            "conf_high": overall_high,
            "weight": 1.0,
            "post_periods": post_periods_count,
            "bucket_periods": post_periods_count,
            "n_pairs": _sum_numeric(rows, post_indices, "n_pairs"),
            "n_treated": _sum_numeric(rows, post_indices, "n_treated"),
            "n_control": _sum_numeric(rows, post_indices, "n_control"),
            "band_type": "pointwise",
            "critical_value": crit_pointwise,
            "horizon_start": None,
            "horizon_end": None,
            "horizon_label": None,
        }
    else:
        weights = np.array([])
        overall_row = None

    for row in rows:
        row["post_periods"] = post_periods_count

    crit_uniform = None
    if cband:
        crit_uniform = _multiplier_critical_value(inf_matrix, se_vector, biters, alpha)
        if crit_uniform is not None:
            for row in rows:
                se_val = row.get("std_error")
                if se_val is None or not np.isfinite(se_val):
                    continue
                row["conf_low"] = float(row["estimate"]) - crit_uniform * float(se_val)
                row["conf_high"] = float(row["estimate"]) + crit_uniform * float(se_val)
                row["band_type"] = "simultaneous"
                row["critical_value"] = crit_uniform
            if overall_row is not None and np.isfinite(overall_row.get("std_error", np.nan)):
                se_val = float(overall_row["std_error"])
                overall_row["conf_low"] = overall_row["estimate"] - crit_uniform * se_val
                overall_row["conf_high"] = overall_row["estimate"] + crit_uniform * se_val
                overall_row["band_type"] = "simultaneous"
                overall_row["critical_value"] = crit_uniform

    horizon_rows: List[Dict[str, object]] = []
    buckets = _build_horizon_buckets(horizon_breaks)
    if buckets and post_rows:
        for start, end, label in buckets:
            bucket_indices = [
                idx
                for idx, _ in post_rows
                if rows[idx]["event_time"] >= start
                and (end is None or rows[idx]["event_time"] < end)
            ]
            if not bucket_indices:
                continue
            weight_values = []
            for idx in bucket_indices:
                raw = rows[idx].get("n_treated")
                if raw is None or (isinstance(raw, float) and np.isnan(raw)):
                    raw = rows[idx].get("n_pairs", 0.0)
                weight_values.append(raw)
            weight_series = (
                pd.Series(weight_values, dtype=float)
                if weight_values
                else pd.Series([], dtype=float)
            )
            weights = _normalize_weights(weight_series) if len(weight_series) > 0 else np.array([])
            if weights.size == 0:
                continue
            bucket_cov = cov_matrix[np.ix_(bucket_indices, bucket_indices)]
            estimates = np.array([rows[idx]["estimate"] for idx in bucket_indices], dtype=float)
            bucket_est = float(np.dot(weights, estimates))
            bucket_var = float(weights @ bucket_cov @ weights)
            bucket_se = float(np.sqrt(max(bucket_var, 0.0)))
            crit = crit_uniform if (crit_uniform is not None) else crit_pointwise
            band_type = "simultaneous" if crit_uniform is not None else "pointwise"
            if np.isfinite(bucket_se):
                bucket_low = bucket_est - crit * bucket_se
                bucket_high = bucket_est + crit * bucket_se
            else:
                bucket_low = np.nan
                bucket_high = np.nan
            horizon_rows.append(
                {
                    "chapter": chapter,
                    "outcome": outcome,
                    "sample": sample,
                    "aggregation": "dynamic",
                    "component": f"horizon_{label}",
                    "relative_year": None,
                    "event_time": None,
                    "estimate": bucket_est,
                    "std_error": bucket_se,
                    "conf_low": bucket_low,
                    "conf_high": bucket_high,
                    "weight": 1.0,
                    "post_periods": post_periods_count,
                    "bucket_periods": len(bucket_indices),
                    "reference_year": None,
                    "n_pairs": _sum_numeric(rows, bucket_indices, "n_pairs"),
                    "n_treated": _sum_numeric(rows, bucket_indices, "n_treated"),
                    "n_control": _sum_numeric(rows, bucket_indices, "n_control"),
                    "band_type": band_type,
                    "critical_value": crit,
                    "horizon_start": start,
                    "horizon_end": (end - 1) if end is not None else None,
                    "horizon_label": label,
                }
            )

    records: List[Dict[str, object]] = []
    for row in rows:
        records.append(
            {
                "chapter": chapter,
                "outcome": outcome,
                "sample": sample,
                "aggregation": "dynamic",
                "component": "event_time",
                "relative_year": int(row["relative_year"]),
                "event_time": int(row["event_time"]),
                "estimate": float(row["estimate"]),
                "std_error": float(row.get("std_error"))
                if pd.notna(row.get("std_error"))
                else np.nan,
                "conf_low": float(row.get("conf_low"))
                if pd.notna(row.get("conf_low"))
                else np.nan,
                "conf_high": float(row.get("conf_high"))
                if pd.notna(row.get("conf_high"))
                else np.nan,
                "weight": float(row.get("weight"))
                if pd.notna(row.get("weight"))
                else np.nan,
                "post_periods": post_periods_count,
                "reference_year": int(row["reference_year"])
                if pd.notna(row.get("reference_year"))
                else None,
                "n_pairs": float(row.get("n_pairs"))
                if pd.notna(row.get("n_pairs"))
                else np.nan,
                "n_treated": float(row.get("n_treated"))
                if pd.notna(row.get("n_treated"))
                else np.nan,
                "n_control": float(row.get("n_control"))
                if pd.notna(row.get("n_control"))
                else np.nan,
                "band_type": row.get("band_type"),
                "critical_value": float(row.get("critical_value"))
                if row.get("critical_value") is not None
                else np.nan,
                "horizon_start": row.get("horizon_start"),
                "horizon_end": row.get("horizon_end"),
                "horizon_label": row.get("horizon_label"),
                "bucket_periods": row.get("bucket_periods"),
            }
        )

    if overall_row is not None:
        records.append(overall_row)
    records.extend(horizon_rows)

    return records


def aggregate_att_effects(
    att_df: pd.DataFrame,
    baseline: int,
    alpha: float,
    cband: bool = False,
    biters: int = 0,
    horizon_breaks: Optional[Sequence[int]] = None,
) -> pd.DataFrame:
    """Aggregate ATT estimates per (chapter, outcome, sample) combination."""
    if att_df.empty:
        return pd.DataFrame()

    required = {"chapter", "outcome", "sample", "relative_year", "estimate"}
    missing = required.difference(att_df.columns)
    if missing:
        raise ValueError(
            "ATT dataframe missing required columns for aggregation: "
            + ", ".join(sorted(missing))
        )

    grouped = att_df.groupby(["chapter", "outcome", "sample"], dropna=False)
    rows: List[Dict[str, object]] = []
    for (chapter, outcome, sample), group in grouped:
        rows.extend(
            _aggregate_dynamic_series(
                group,
                baseline,
                alpha,
                chapter,
                outcome,
                sample,
                cband=cband,
                biters=biters,
                horizon_breaks=horizon_breaks,
            )
        )
    return pd.DataFrame(rows)


def build_time_pairs(
    relative_years: Iterable[int],
    baseline: int,
    strategy: str = "fixed_baseline",
    max_post: Optional[int] = None,
    debug: bool = False,
) -> List[Tuple[int, int]]:
    """Build time pairs for estimation with improved logic.

    Args:
        relative_years: Available relative years in the data
        baseline: The baseline year (e.g., -1)
        strategy: Either 'sequential' or 'fixed_baseline'
        max_post: Maximum number of post-treatment periods to estimate
        debug: Enable debug output
    """
    years = sorted({int(year) for year in relative_years if pd.notna(year)})
    if len(years) < 2:
        return []

    if debug:
        print(f"[DEBUG] build_time_pairs: baseline={baseline}, strategy={strategy}")
        print(f"[DEBUG] Available years: {years}")

    pairs: List[Tuple[int, int]] = []

    if strategy == "fixed_baseline":
        # Use baseline as reference for all post-treatment periods
        # This is more standard for event study designs
        if baseline not in years:
            # Find closest pre-treatment year to use as baseline
            pre_years = [y for y in years if y <= baseline]
            if pre_years:
                actual_baseline = max(pre_years)
                if debug:
                    print(
                        f"[DEBUG] Baseline {baseline} not in data, using {actual_baseline}"
                    )
            else:
                actual_baseline = min(years)
                if debug:
                    print(
                        f"[DEBUG] No pre-treatment years, using {actual_baseline} as baseline"
                    )
        else:
            actual_baseline = baseline

        # Add all post-treatment periods paired with baseline
        post_years = [y for y in years if y > actual_baseline]
        if max_post:
            post_years = post_years[:max_post]

        for post_year in post_years:
            pairs.append((actual_baseline, post_year))
            if debug:
                print(f"[DEBUG] Adding pair: ({actual_baseline}, {post_year})")

        # Also add pre-treatment comparisons if requested
        pre_years = [y for y in years if y < actual_baseline]
        for pre_year in pre_years:
            pairs.append((pre_year, actual_baseline))
            if debug:
                print(f"[DEBUG] Adding pre-trend pair: ({pre_year}, {actual_baseline})")

    else:  # sequential strategy
        # Original sequential pairing logic
        pre_candidates = [year for year in years if year <= baseline]
        if pre_candidates:
            reference_year = pre_candidates[-1]
        else:
            reference_year = years[0]

        post_candidates = [year for year in years if year > reference_year]
        first_post = post_candidates[0] if post_candidates else None

        for idx in range(1, len(years)):
            target = years[idx]
            if first_post is not None and target >= first_post:
                pre_year = reference_year
            else:
                pre_year = years[idx - 1]
            if pre_year == target:
                continue
            pairs.append((pre_year, target))
            if debug:
                print(f"[DEBUG] Adding sequential pair: ({pre_year}, {target})")

    return pairs


def run_drdid_estimator(
    y_pre: np.ndarray,
    y_post: np.ndarray,
    treat: np.ndarray,
    covariates: Optional[np.ndarray],
    weights: Optional[np.ndarray],
) -> tuple[float, np.ndarray]:
    if weights is None:
        weights = np.ones_like(treat, dtype=float)
    else:
        weights = np.asarray(weights, dtype=float).flatten()

    result = drdid_panel(
        y1=y_post,
        y0=y_pre,
        D=treat,
        covariates=covariates,
        i_weights=weights,
    )

    att, influence = result
    influence_array = np.asarray(influence, dtype=float).flatten()
    if influence_array.size == 0:
        raise ValueError("drdid returned an empty influence function.")

    return float(att), influence_array


def compute_inference_metrics(
    att: float,
    influence: np.ndarray,
    alpha: float,
    bootstrap_iterations: int,
) -> Tuple[float, float, float]:
    n = influence.size
    if n == 0:
        raise ValueError("Influence function must contain at least one observation.")

    plugin_variance = np.var(influence, ddof=1) / n
    plugin_se = float(np.sqrt(plugin_variance)) if plugin_variance > 0 else 0.0
    crit = NormalDist().inv_cdf(1 - alpha / 2)
    se = plugin_se
    conf_low = float(att - crit * se)
    conf_high = float(att + crit * se)

    if (
        bootstrap_iterations
        and bootstrap_iterations > 0
        and np.any(np.isfinite(influence))
    ):
        try:
            inf_matrix = influence.reshape(-1, 1)
            boot_draws = multiplier_bootstrap(inf_matrix, int(bootstrap_iterations))
            boot_scaled = np.sqrt(n) * np.asarray(boot_draws).reshape(-1)
            if boot_scaled.size > 0:
                q75 = np.quantile(boot_scaled, 0.75, method="inverted_cdf")
                q25 = np.quantile(boot_scaled, 0.25, method="inverted_cdf")
                denom = NormalDist().inv_cdf(0.75) - NormalDist().inv_cdf(0.25)
                if denom != 0:
                    b_sigma = (q75 - q25) / denom
                    if np.isfinite(b_sigma) and b_sigma > 0:
                        se = float(b_sigma / np.sqrt(n))
                        crit = float(
                            np.quantile(
                                np.abs(boot_scaled / b_sigma),
                                1 - alpha,
                                method="inverted_cdf",
                            )
                        )
                        conf_low = float(att - crit * se)
                        conf_high = float(att + crit * se)
        except Exception:
            # Fall back to plug-in estimates if bootstrap fails
            pass

    return se, conf_low, conf_high


def sanitise_for_csv(df: pd.DataFrame, float_precision: int = 4) -> pd.DataFrame:
    if df.empty:
        return df
    sanitized = df.copy()
    float_cols = sanitized.select_dtypes(include=["float32", "float64"]).columns
    if len(float_cols) > 0:
        sanitized[float_cols] = sanitized[float_cols].round(float_precision)
    return sanitized


def enforce_nullable_ints(
    df: pd.DataFrame, columns: Sequence[str]
) -> pd.DataFrame:
    if df.empty:
        return df
    converted = df.copy()
    for col in columns:
        if col not in converted.columns:
            continue
        series = pd.to_numeric(converted[col], errors="coerce")
        series = series.where(series.notna(), pd.NA)
        converted[col] = series.round().astype("Int64")
    return converted


NON_EXPORT_COLUMNS = ("unit_ids", "influence")
AGG_INT_COLUMNS = (
    "relative_year",
    "event_time",
    "reference_year",
    "post_periods",
    "bucket_periods",
    "n_pairs",
    "n_treated",
    "n_control",
    "horizon_start",
    "horizon_end",
)


def _multiplier_critical_value(
    inf_matrix: np.ndarray, se_vector: np.ndarray, biters: int, alpha: float
) -> Optional[float]:
    if biters is None or biters <= 0:
        return None
    if inf_matrix.size == 0:
        return None
    n_units, n_cols = inf_matrix.shape
    if n_units == 0 or n_cols == 0:
        return None

    se_vector = np.asarray(se_vector, dtype=float)
    valid_cols = np.isfinite(se_vector) & (se_vector > np.sqrt(np.finfo(float).eps) * 10)
    if not np.any(valid_cols):
        return None

    try:
        boot = multiplier_bootstrap(inf_matrix[:, valid_cols], biters)
    except Exception:
        return None

    if boot.size == 0:
        return None

    boot = np.sqrt(n_units) * np.asarray(boot, dtype=float)
    q75 = np.quantile(boot, 0.75, axis=0, method="inverted_cdf")
    q25 = np.quantile(boot, 0.25, axis=0, method="inverted_cdf")
    denom = NormalDist().inv_cdf(0.75) - NormalDist().inv_cdf(0.25)
    if denom == 0:
        return None
    b_sigma = (q75 - q25) / denom
    sigma_valid = np.isfinite(b_sigma) & (b_sigma > np.sqrt(np.finfo(float).eps) * 10)
    if not np.any(sigma_valid):
        return None

    boot = boot[:, sigma_valid]
    b_sigma = b_sigma[sigma_valid]
    with np.errstate(divide="ignore", invalid="ignore"):
        t_stats = np.max(np.abs(boot / b_sigma), axis=1)
    t_stats = t_stats[np.isfinite(t_stats)]
    if t_stats.size == 0:
        return None

    return float(np.quantile(t_stats, 1 - alpha, method="inverted_cdf"))


def _build_horizon_buckets(
    breaks: Optional[Sequence[int]],
) -> List[Tuple[int, Optional[int], str]]:
    if not breaks:
        return []
    cleaned = sorted({int(b) for b in breaks})
    if not cleaned:
        return []
    default_breaks = [0, 3, 7, 11]
    use_default_labels = cleaned == default_breaks
    labels = ["short_term", "medium_term", "long_term", "very_long_term"]
    buckets: List[Tuple[int, Optional[int], str]] = []
    for idx, start in enumerate(cleaned):
        end = cleaned[idx + 1] if idx + 1 < len(cleaned) else None
        if use_default_labels and idx < len(labels):
            label = labels[idx]
        else:
            end_label = f"{end - 1}" if end is not None else "plus"
            label = f"horizon_{start}_{end_label}"
        buckets.append((start, end, label))
    return buckets


def summarize_chapter(df: pd.DataFrame, baseline: int) -> tuple[int, int, int]:
    baseline_rows = df[df["RELATIVE_YEAR"] == baseline]
    treated = baseline_rows[baseline_rows["treatment_indicator"] == 1]
    control = baseline_rows[baseline_rows["treatment_indicator"] == 0]
    return treated.shape[0], control.shape[0], df.shape[0]


def compute_att_for_outcome(
    df: pd.DataFrame,
    label: str,
    outcome: str,
    baseline: int,
    covariate_formula: str,
    weight_column: Optional[str],
    alpha: float,
    bootstrap_iterations: int,
    strategy: str = "fixed_baseline",
    max_post: Optional[int] = None,
    debug: bool = False,
) -> List[DidResult]:
    results: List[DidResult] = []
    relative_years = df["RELATIVE_YEAR"].dropna().unique()
    time_pairs = build_time_pairs(relative_years, baseline, strategy, max_post, debug)

    if not time_pairs:
        if debug:
            print(f"[DEBUG] No time pairs generated for {label} {outcome}")
        return results

    # Determine merge keys dynamically
    id_cols: List[str] = []
    if "parent_pnr" in df.columns:
        id_cols.append("parent_pnr")
    elif "PNR" in df.columns:
        id_cols.append("PNR")
    else:
        id_cols.append("child_pnr")

    if "MATCH_INDEX" in df.columns:
        id_cols.append("MATCH_INDEX")
    if "parent_type" in df.columns:
        id_cols.append("parent_type")

    if debug:
        print(f"[DEBUG] Using identifier columns: {id_cols}")
        print(f"[DEBUG] Processing {len(time_pairs)} time pairs for {label} {outcome}")

    successful_pairs = 0
    failed_pairs = 0

    for pair_idx, (reference_year, target_year) in enumerate(time_pairs):
        if debug:
            print(
                f"\n[DEBUG] Pair {pair_idx + 1}/{len(time_pairs)}: {label} {outcome}: reference={reference_year}, target={target_year}"
            )

        pair_mask = df["RELATIVE_YEAR"].isin({reference_year, target_year})
        pair_df = df.loc[pair_mask].copy()

        if pair_df.empty:
            if debug:
                print("[DEBUG]  -> No observations for this pair")
            failed_pairs += 1
            continue

        pair_df = pair_df.drop_duplicates(subset=id_cols + ["RELATIVE_YEAR"])

        pivot = pair_df.pivot_table(
            index=id_cols + ["treatment", "treatment_indicator"],
            columns="RELATIVE_YEAR",
            values=outcome,
        )

        if reference_year not in pivot.columns or target_year not in pivot.columns:
            if debug:
                print("[DEBUG]  -> Missing outcome column after pivot")
            failed_pairs += 1
            continue

        pivot = pivot.dropna(subset=[reference_year, target_year])

        if pivot.empty:
            if debug:
                print("[DEBUG]  -> No units with both periods available")
            failed_pairs += 1
            continue

        panel_units = pivot.reset_index()
        panel_units["_unit_key"] = compose_unit_keys(panel_units, id_cols)

        treated = panel_units[panel_units["treatment"] == 1]
        control = panel_units[panel_units["treatment"] == 0]

        if treated.empty or control.empty:
            if debug:
                print("[DEBUG]  -> One of the groups is empty after pivot")
            failed_pairs += 1
            continue

        if debug:
            print(
                f"[DEBUG]  -> Merged {panel_units.shape[0]} units; "
                f"treated={treated.shape[0]}, control={control.shape[0]}"
            )

        unit_keys = panel_units["_unit_key"].astype(str).tolist()
        panel_units = panel_units.drop(columns="_unit_key")

        if reference_year <= target_year:
            y_pre = panel_units[reference_year].to_numpy(dtype=float)
            y_post = panel_units[target_year].to_numpy(dtype=float)
        else:
            y_pre = panel_units[target_year].to_numpy(dtype=float)
            y_post = panel_units[reference_year].to_numpy(dtype=float)

        treat_array = panel_units["treatment"].to_numpy(dtype=float)

        weights = None
        if weight_column and weight_column in df.columns:
            weight_source = df.loc[
                df["RELATIVE_YEAR"] == reference_year, id_cols + [weight_column]
            ]
            weight_source = weight_source.drop_duplicates(subset=id_cols)
            panel_units = panel_units.merge(weight_source, on=id_cols, how="left")
            if panel_units[weight_column].notna().any():
                weights = panel_units[weight_column].fillna(1.0).to_numpy(dtype=float)

        covariate_matrix = None
        if covariate_formula and covariate_formula != "~ 1":
            cov_source = df.loc[df["RELATIVE_YEAR"] == reference_year].drop_duplicates(
                subset=id_cols
            )
            cov_panel = panel_units.merge(
                cov_source, on=id_cols, how="left", suffixes=("", "_ref")
            )
            try:
                covariate_df = dmatrix(
                    covariate_formula,
                    ensure_patsy_compatible(cov_panel),
                    return_type="dataframe",
                )
                treat_mask = treat_array.astype(bool)
                control_mask = ~treat_mask
                valid_cols = []
                for col in covariate_df.columns:
                    vals = covariate_df[col].to_numpy()
                    if col == "Intercept":
                        valid_cols.append(col)
                        continue
                    if control_mask.any() and np.ptp(vals[control_mask]) == 0:
                        continue
                    if treat_mask.any() and np.ptp(vals[treat_mask]) == 0:
                        continue
                    valid_cols.append(col)
                if valid_cols:
                    covariate_matrix = covariate_df[valid_cols].to_numpy()
                    if debug:
                        print(
                            f"[DEBUG]  -> Using {covariate_matrix.shape[1]} covariates"
                        )
            except Exception as exc:
                if debug:
                    print(f"[DEBUG]  -> Covariate construction failed: {exc}")
                covariate_matrix = None

        try:
            att, influence = run_drdid_estimator(
                y_pre, y_post, treat_array, covariate_matrix, weights
            )
            se, lci, uci = compute_inference_metrics(
                att, influence, alpha, bootstrap_iterations
            )
            influence_list = tuple(float(val) for val in influence.tolist())
            results.append(
                DidResult(
                    chapter=label,
                    outcome=outcome,
                    sample="",
                    reference_year=int(reference_year),
                    relative_year=int(target_year),
                    estimate=float(att),
                    std_error=float(se),
                    conf_low=float(lci),
                    conf_high=float(uci),
                    n_pairs=int(panel_units.shape[0]),
                    n_treated=int((treat_array == 1).sum()),
                    n_control=int((treat_array == 0).sum()),
                    convergence="success",
                    unit_ids=tuple(unit_keys),
                    influence=influence_list,
                )
            )
            successful_pairs += 1
            if debug:
                print(f"[DEBUG]  -> SUCCESS: ATT={att:.4f}, SE={se:.4f}")
        except Exception as exc:
            failed_pairs += 1
            if debug:
                print(f"[DEBUG]  -> Estimation failed: {exc}")
            results.append(
                DidResult(
                    chapter=label,
                    outcome=outcome,
                    sample="",
                    reference_year=int(reference_year),
                    relative_year=int(target_year),
                    estimate=np.nan,
                    std_error=np.nan,
                    conf_low=np.nan,
                    conf_high=np.nan,
                    n_pairs=int(panel_units.shape[0]),
                    n_treated=int((treat_array == 1).sum()),
                    n_control=int((treat_array == 0).sum()),
                    convergence=f"failed: {str(exc)[:50]}",
                    unit_ids=tuple(unit_keys),
                )
            )

    if debug:
        print(f"\n[DEBUG] Summary for {label} {outcome}:")
        print(
            f"[DEBUG]  - Successful estimations: {successful_pairs}/{len(time_pairs)}"
        )
        print(f"[DEBUG]  - Failed estimations: {failed_pairs}/{len(time_pairs)}")

    return results


def run_overall_estimations(
    df: pd.DataFrame,
    outcomes: Sequence[str],
    baseline: int,
    min_treated: int,
    covariate_formula: str,
    weight_column: Optional[str],
    alpha: float,
    bootstrap_iterations: int,
    samples: Sequence[str],
    verbose: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    att_rows: List[DidResult] = []
    summary_rows: List[Dict[str, object]] = []

    sample_sets = build_sample_sets(df, samples)
    sample_items = list(sample_sets.items())
    sample_iter = tqdm(
        sample_items,
        desc="Samples (overall)",
        total=len(sample_items),
        leave=False,
        disable=not verbose,
    )
    for sample_name, sample_df in sample_iter:
        if sample_df.empty:
            continue

        treated_baseline, control_baseline, total_rows = summarize_chapter(
            sample_df, baseline
        )

        summary_entry = {
            "icd_chapter": "OVERALL",
            "sample": sample_name,
            "treated_baseline": treated_baseline,
            "control_baseline": control_baseline,
            "rows": total_rows,
            "estimated": treated_baseline >= min_treated,
        }
        summary_rows.append(summary_entry)

        if treated_baseline < min_treated:
            if verbose:
                print(
                    f"Skipping sample '{sample_name}': treated baseline {treated_baseline} < {min_treated}"
                )
            continue

        for outcome in outcomes:
            if outcome not in sample_df.columns:
                if verbose:
                    print(
                        f"Column '{outcome}' missing for sample '{sample_name}'; skipping outcome."
                    )
                continue

            att_results = compute_att_for_outcome(
                sample_df,
                "OVERALL",
                outcome,
                baseline,
                covariate_formula,
                weight_column,
                alpha,
                bootstrap_iterations,
            )
            for result in att_results:
                result.sample = sample_name
                att_rows.append(result)

    att_df = (
        pd.DataFrame([r.__dict__ for r in att_rows]) if att_rows else pd.DataFrame()
    )
    summary_df = pd.DataFrame(summary_rows) if summary_rows else pd.DataFrame()
    return att_df, summary_df


def run_chapter_estimations(
    df: pd.DataFrame,
    chapters: Sequence[str],
    outcomes: Sequence[str],
    baseline: int,
    min_treated: int,
    covariate_formula: str,
    weight_column: Optional[str],
    alpha: float,
    bootstrap_iterations: int,
    samples: Sequence[str],
    verbose: bool,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    att_rows: List[DidResult] = []
    summary_rows: List[Dict[str, object]] = []

    sample_sets = build_sample_sets(df, samples)
    sample_items = list(sample_sets.items())
    sample_iter = tqdm(
        sample_items,
        desc="Samples (chapters)",
        total=len(sample_items),
        leave=False,
        disable=not verbose,
    )
    for sample_name, sample_df in sample_iter:
        if sample_df.empty:
            continue

        chapter_iter = tqdm(
            chapters,
            desc=f"Chapters ({sample_name})",
            disable=not verbose,
        )

        for chapter in chapter_iter:
            try:
                chapter_df = build_chapter_dataset(sample_df, chapter, baseline)
            except ValueError as exc:
                if verbose:
                    print(f"Skipping chapter {chapter} ({sample_name}): {exc}")
                continue

            treated_baseline, control_baseline, total_rows = summarize_chapter(
                chapter_df, baseline
            )
            if treated_baseline < min_treated:
                if verbose:
                    print(
                        f"Skipping chapter {chapter} ({sample_name}): treated baseline {treated_baseline} < {min_treated}"
                    )
                continue

            for outcome in outcomes:
                if outcome not in chapter_df.columns:
                    if verbose:
                        print(
                            f"Column '{outcome}' missing for chapter {chapter}; skipping outcome."
                        )
                    continue

                att_results = compute_att_for_outcome(
                    chapter_df,
                    chapter,
                    outcome,
                    baseline,
                    covariate_formula,
                    weight_column,
                    alpha,
                    bootstrap_iterations,
                )
                for result in att_results:
                    result.sample = sample_name
                    att_rows.append(result)

            summary_rows.append(
                {
                    "icd_chapter": chapter,
                    "sample": sample_name,
                    "treated_baseline": treated_baseline,
                    "control_baseline": control_baseline,
                    "rows": total_rows,
                    "estimated": True,
                }
            )

    att_df = (
        pd.DataFrame([r.__dict__ for r in att_rows]) if att_rows else pd.DataFrame()
    )
    summary_df = pd.DataFrame(summary_rows) if summary_rows else pd.DataFrame()
    return att_df, summary_df


def main(argv: Optional[Sequence[str]] = None) -> None:
    args = parse_args(argv)

    os.makedirs(args.output_dir, exist_ok=True)

    df = pd.read_parquet(args.input)

    enriched = prepare_dataframe(df, args.weight_column)
    covariate_formula = resolve_covariate_formula(
        args.adjustments, args.covariate_formula
    )

    att_overall_df, summary_overall_df = run_overall_estimations(
        enriched,
        args.outcome_columns,
        args.baseline,
        args.min_treated,
        covariate_formula,
        args.weight_column,
        args.alpha,
        args.bootstrap_iterations,
        args.samples,
        args.verbose,
    )

    chapters_array = enriched["icd_chapter"].dropna().astype(str).unique()
    chapters: Sequence[str] = sorted(chapters_array, key=str)

    att_chapter_df, summary_chapter_df = run_chapter_estimations(
        enriched,
        chapters,
        args.outcome_columns,
        args.baseline,
        args.min_treated,
        covariate_formula,
        args.weight_column,
        args.alpha,
        args.bootstrap_iterations,
        args.samples,
        args.verbose,
    )

    att_frames = [df for df in (att_overall_df, att_chapter_df) if not df.empty]
    att_df = pd.concat(att_frames, ignore_index=True) if att_frames else pd.DataFrame()

    summary_frames = [
        df for df in (summary_overall_df, summary_chapter_df) if not df.empty
    ]
    summary_df = (
        pd.concat(summary_frames, ignore_index=True)
        if summary_frames
        else pd.DataFrame()
    )

    aggregated_df = (
        aggregate_att_effects(
            att_df,
            args.baseline,
            args.alpha,
            cband=args.uniform_band,
            biters=args.bootstrap_iterations,
            horizon_breaks=args.horizon_breaks,
        )
        if not att_df.empty
        else pd.DataFrame()
    )
    if not aggregated_df.empty:
        aggregated_df = enforce_nullable_ints(aggregated_df, AGG_INT_COLUMNS)

    non_export = list(NON_EXPORT_COLUMNS)
    if not att_df.empty:
        att_export = att_df.drop(columns=non_export, errors="ignore")
        att_export = sanitise_for_csv(att_export)
        att_path = os.path.join(args.output_dir, "att_effects.csv")
        att_export.to_csv(att_path, index=False)
        if args.verbose:
            print(f"ATT estimates written to {att_path}")
    else:
        if args.verbose:
            print("No ATT estimates produced.")

    if not aggregated_df.empty:
        agg_export = aggregated_df.drop(columns=non_export, errors="ignore")
        agg_export = sanitise_for_csv(agg_export)
        agg_path = os.path.join(args.output_dir, "aggregated_effects.csv")
        agg_export.to_csv(agg_path, index=False)
        if args.verbose:
            print(f"Aggregated ATT summaries written to {agg_path}")

    if not summary_df.empty:
        summary_df = sanitise_for_csv(summary_df, float_precision=3)
        summary_path = os.path.join(args.output_dir, "sample_summary.csv")
        summary_df.to_csv(summary_path, index=False)
        if args.verbose:
            print(f"Sample summary written to {summary_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
