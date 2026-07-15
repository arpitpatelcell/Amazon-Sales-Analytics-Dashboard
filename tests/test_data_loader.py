"""
tests/test_data_loader.py
Automated tests for the data cleaning logic.

Why this matters: any teacher or recruiter looking at a project with a
tests/ folder + passing CI badge immediately reads it as "production-grade
practice," not just a script. Run locally with:

    pytest tests/
"""

import os
import sys
import pandas as pd
import pytest

# Make the dashboard/ package importable when running pytest from the repo root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "dashboard"))

from data_loader import clean_data, validate_data, DataLoadError  # noqa: E402


@pytest.fixture
def raw_sample_df():
    return pd.DataFrame({
        "product_name": ["Wireless Mouse", "USB Cable", None, "Bluetooth Speaker"],
        "category": ["Electronics|Accessories", "Electronics|Cables", "Home", "Electronics|Audio"],
        "discounted_price": ["₹499", "₹149", "₹999", "₹1,299"],
        "actual_price": ["₹999", "₹299", "₹1,499", "₹2,499"],
        "discount_percentage": ["50%", "50%", "33%", "48%"],
        "rating": ["4.2", "3.8", "4.5", "4.0"],
        "rating_count": ["1,204", "532", "89", "3,410"],
    })


def test_clean_data_strips_currency_and_percent_symbols(raw_sample_df):
    cleaned = clean_data(raw_sample_df)
    assert cleaned["discounted_price"].dtype.kind in "fi"
    assert cleaned.loc[cleaned.index[0], "discounted_price"] == 499


def test_clean_data_drops_rows_missing_essential_fields(raw_sample_df):
    cleaned = clean_data(raw_sample_df)
    # The row with product_name=None should be dropped
    assert cleaned["product_name"].isna().sum() == 0
    assert len(cleaned) == 3


def test_clean_data_splits_pipe_separated_category(raw_sample_df):
    cleaned = clean_data(raw_sample_df)
    assert all("|" not in str(c) for c in cleaned["category"])


def test_validate_data_raises_on_empty_dataframe():
    with pytest.raises(DataLoadError):
        validate_data(pd.DataFrame())


def test_validate_data_passes_on_valid_dataframe(raw_sample_df):
    cleaned = clean_data(raw_sample_df)
    # Should not raise
    validate_data(cleaned)
