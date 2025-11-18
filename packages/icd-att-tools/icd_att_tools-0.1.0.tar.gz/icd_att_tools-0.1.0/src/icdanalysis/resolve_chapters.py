from typing import Optional, Tuple, List, Dict
import pandas as pd
import numpy as np
import sys

try:  # pragma: no cover - validated at runtime.
    import simple_icd_10 as icd10
except Exception as exc:  # pragma: no cover - import must succeed for this script.
    raise ImportError(
        "The 'simple-icd-10' package is required. Install it via 'uv pip install simple-icd-10'."
    ) from exc

# Cache for validated codes to avoid redundant ICD library calls
_validation_cache: Dict[str, bool] = {}
_chapter_cache: Dict[str, str] = {}

# Pre-compiled letter-to-chapter mapping
LETTER_TO_CHAPTER = {
    "A": "I", "B": "I", "C": "II", "D": "II", "E": "IV", "F": "V",
    "G": "VI", "H": "VII", "I": "IX", "J": "X", "K": "XI", "L": "XII",
    "M": "XIII", "N": "XIV", "O": "XV", "P": "XVI", "Q": "XVII",
    "R": "XVIII", "S": "XIX", "T": "XIX", "U": "XXII",
    "V": "XX", "W": "XX", "X": "XX", "Y": "XX", "Z": "XXI",
}


def _is_valid_cached(candidate: str) -> bool:
    """Cache ICD validation results to minimize library calls."""
    if candidate not in _validation_cache:
        _validation_cache[candidate] = icd10.is_valid_item(candidate)
    return _validation_cache[candidate]


def _generate_candidates(text: str) -> List[str]:
    """Generate candidate ICD codes from input text."""
    candidates = []
    seen = set()

    def add_candidate(code: str) -> None:
        if code and code not in seen:
            candidates.append(code)
            seen.add(code)

    # Primary candidate variations
    working = text
    while working:
        add_candidate(working)

        # Try adding decimal if missing and length >= 4
        if "." not in working and len(working) >= 4:
            add_candidate(f"{working[:3]}.{working[3:]}")

        # Try removing decimal
        no_dot = working.replace(".", "")
        if no_dot != working:
            add_candidate(no_dot)

        # Strip trailing characters
        if working.endswith("-"):
            working = working[:-1]
        elif len(working) > 3 and working[-1].isalpha():
            working = working[:-1]
        else:
            break

    return candidates


def _sanitize_fallback(text: str) -> List[str]:
    """Create sanitized fallback candidates."""
    trimmed = text.rstrip('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    if not trimmed:
        return []

    # Extract letter + digits only
    sanitized = trimmed[0] + ''.join(ch for ch in trimmed[1:] if ch.isdigit())

    if len(sanitized) < 3:
        return []

    candidates = [sanitized]
    if len(sanitized) > 3:
        candidates.append(f"{sanitized[:3]}.{sanitized[3:]}")

    return candidates


def normalize_icd_code(value: object) -> Tuple[Optional[str], Optional[str]]:
    """
    Normalize an ICD-10 code and return (best_valid_code, match_code).

    Args:
        value: Raw ICD code value (string, number, or None)

    Returns:
        Tuple of (validated ICD code, matching key for grouping)
    """
    # Handle null values
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None, None

    # Normalize input
    text = str(value).strip().upper()
    if not text:
        return None, None

    # Remove leading 'D' prefix if present (e.g., "DC50" -> "C50")
    if text.startswith("D") and len(text) > 1 and text[1].isalnum():
        text = text[1:]

    text = text.replace(" ", "")

    # Generate and validate candidates
    candidates = _generate_candidates(text)
    validated = [c for c in candidates if _is_valid_cached(c)]

    # Fallback: try sanitized version if no valid candidates
    if not validated:
        fallback_candidates = _sanitize_fallback(text)
        validated.extend(c for c in fallback_candidates if _is_valid_cached(c))
        candidates.extend(fallback_candidates)

    # Select best valid code (prioritize categories/subcategories, then chapters)
    best_valid = None
    if validated:
        for candidate in validated:
            if icd10.is_category_or_subcategory(candidate) or icd10.is_block(candidate):
                best_valid = candidate
                break

        if best_valid is None:
            for candidate in validated:
                if icd10.is_chapter(candidate):
                    best_valid = candidate
                    break

        if best_valid is None:
            best_valid = validated[0]

    # Determine match code for grouping
    if candidates:
        match_code = candidates[0]
    elif best_valid:
        match_code = best_valid
    else:
        match_code = ''.join(ch for ch in text if ch.isalnum()) or None

    return best_valid, match_code


def _infer_chapter_from_letter(match_code: str) -> str:
    """Infer ICD chapter from the first letter of the code."""
    if not match_code:
        raise ValueError("Empty match code cannot be mapped to an ICD chapter.")

    first = match_code[0]

    # Special handling for 'H' codes (chapters VII and VIII)
    if first == "H" and len(match_code) >= 3:
        digits = ''.join(ch for ch in match_code[1:3] if ch.isdigit())
        numeric_val = int(digits) if digits else 0
        return "VIII" if numeric_val >= 60 else "VII"

    chapter = LETTER_TO_CHAPTER.get(first)
    if chapter is None:
        raise ValueError(f"Unable to infer ICD chapter from code '{match_code}'.")

    return chapter


def _get_chapter_label(best_valid: Optional[str], match_code: str) -> str:
    """Get chapter label with caching."""
    cache_key = best_valid or match_code

    if cache_key in _chapter_cache:
        return _chapter_cache[cache_key]

    # Try to get chapter from validated code
    chapter_code = None
    if best_valid:
        ancestors = icd10.get_ancestors(best_valid)
        chapter_code = next((anc for anc in ancestors if icd10.is_chapter(anc)), None)

        if chapter_code is None and icd10.is_chapter(best_valid):
            chapter_code = best_valid

    # Fallback to letter-based inference
    if chapter_code is None:
        chapter_code = _infer_chapter_from_letter(match_code)

    description = icd10.get_description(chapter_code)
    label = f"{chapter_code} {description}"
    _chapter_cache[cache_key] = label

    return label


def resolve_icd_chapters(
    df: pd.DataFrame,
    icd_code_col: str,
    *,
    verbose: bool = False,
) -> Tuple[pd.Series, pd.Series]:
    """
    Resolve ICD codes to chapter labels.

    Args:
        df: DataFrame containing ICD codes
        icd_code_col: Name of column with ICD codes
        verbose: Whether to print resolution statistics

    Returns:
        Tuple of (chapter labels series, normalized codes series)

    Raises:
        ValueError: If any ICD codes cannot be normalized
    """
    # Vectorized normalization
    results = [normalize_icd_code(val) for val in df[icd_code_col]]
    best_valid_codes, match_codes = zip(*results) if results else ([], [])

    # Create normalized series
    normalized_series = pd.Series(match_codes, index=df.index, dtype=object)

    # Check for missing matches
    missing_mask = normalized_series.isna()
    if missing_mask.any():
        missing_values = df.loc[missing_mask, icd_code_col].dropna().unique()
        raise ValueError(
            f"Unable to derive matching keys for {len(missing_values)} ICD code(s): "
            f"{', '.join(map(str, missing_values[:5]))}"
            f"{'...' if len(missing_values) > 5 else ''}"
        )

    # Resolve chapters
    chapter_labels = [
        _get_chapter_label(best, match)
        for best, match in zip(best_valid_codes, match_codes)
    ]

    if verbose:
        unique_labels = len(set(chapter_labels))
        print(
            f"Resolved {unique_labels} unique ICD chapters from {icd_code_col}.",
            file=sys.stderr,
        )

    return pd.Series(chapter_labels, index=df.index, dtype=object), normalized_series


def clear_caches() -> None:
    """Clear validation and chapter caches (useful for testing or memory management)."""
    _validation_cache.clear()
    _chapter_cache.clear()
