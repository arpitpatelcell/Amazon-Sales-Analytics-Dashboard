"""
data_loader.py
Handles loading, cleaning, and validating the Amazon sales dataset.

Separated from the UI code so that:
  1. It can be unit-tested independently (see tests/test_data_loader.py)
  2. The same cleaning logic could be reused in a notebook or a batch script
"""

from typing import Optional
import pandas as pd
import streamlit as st

from config import COLUMN_CANDIDATES, CACHE_TTL_SECONDS
from utils.logger import get_logger

logger = get_logger()


class DataLoadError(Exception):
    """Raised when the dataset cannot be loaded or is missing required columns."""
    pass


def _find_col(df_columns, candidates: list) -> Optional[str]:
    """Return the first matching column name from a list of candidates."""
    for c in candidates:
        if c in df_columns:
            return c
    return None


def _clean_numeric_column(series: pd.Series) -> pd.Series:
    """Strip currency symbols, percentage signs, and commas; coerce to numeric."""
    cleaned = (
        series.astype(str)
        .str.replace("₹", "", regex=False)
        .str.replace(",", "", regex=False)
        .str.replace("%", "", regex=False)
        .str.strip()
    )
    return pd.to_numeric(cleaned, errors="coerce")


def clean_data(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans a raw Amazon sales DataFrame:
      - standardizes column names
      - maps flexible column name variants to a fixed internal schema
      - strips currency/percentage symbols and converts to numeric
      - fills missing numeric values with the column median
      - drops rows missing essential identifying fields
    """
    df = raw_df.copy()
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    col_map = {key: _find_col(df.columns, candidates) for key, candidates in COLUMN_CANDIDATES.items()}

    for key in ["discounted_price", "actual_price", "discount_percentage", "rating_count"]:
        c = col_map[key]
        if c is not None:
            df[c] = _clean_numeric_column(df[c])

    rating_col = col_map["rating"]
    if rating_col is not None:
        df[rating_col] = pd.to_numeric(df[rating_col].astype(str).str.strip(), errors="coerce")

    essential = [c for c in [col_map["product_name"], col_map["category"]] if c is not None]
    if essential:
        before = len(df)
        df = df.dropna(subset=essential)
        dropped = before - len(df)
        if dropped:
            logger.info("Dropped %d rows missing essential fields (%s)", dropped, essential)

    for key in ["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]:
        c = col_map[key]
        if c is not None and df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())

    rename_dict = {v: k for k, v in col_map.items() if v is not None}
    df = df.rename(columns=rename_dict)

    if "category" in df.columns:
        df["category"] = df["category"].astype(str).str.split("|").str[0]

    return df


def validate_data(df: pd.DataFrame) -> None:
    """
    Raises DataLoadError if the cleaned dataset is unusable
    (e.g. empty, or missing every expected column).
    """
    if df.empty:
        raise DataLoadError("Dataset is empty after cleaning. Check the source CSV.")

    known_cols = set(COLUMN_CANDIDATES.keys())
    present_cols = known_cols.intersection(df.columns)
    if not present_cols:
        raise DataLoadError(
            "None of the expected columns were found. "
            f"Expected one of: {COLUMN_CANDIDATES}"
        )


@st.cache_data(ttl=CACHE_TTL_SECONDS, show_spinner="Loading and cleaning dataset...")
def load_data(path: str) -> pd.DataFrame:
    """
    Loads the CSV at `path`, cleans it, validates it, and returns the
    ready-to-use DataFrame. Cached so repeated Streamlit reruns (e.g. from
    filter changes) don't re-read the file from disk every time.
    """
    try:
        raw_df = pd.read_csv(path)
    except FileNotFoundError as exc:
        logger.error("Dataset not found at %s", path)
        raise DataLoadError(f"Dataset not found at `{path}`.") from exc
    except pd.errors.ParserError as exc:
        logger.error("Failed to parse CSV at %s: %s", path, exc)
        raise DataLoadError(f"The file at `{path}` is not a valid CSV.") from exc

    logger.info("Loaded raw dataset with %d rows, %d columns", *raw_df.shape)

    cleaned_df = clean_data(raw_df)
    validate_data(cleaned_df)

    logger.info("Cleaned dataset ready: %d rows, %d columns", *cleaned_df.shape)
    return cleaned_df
