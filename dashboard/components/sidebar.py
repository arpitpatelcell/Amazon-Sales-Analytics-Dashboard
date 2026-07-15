"""
components/sidebar.py
Renders the sidebar (navigation + filters) and returns the user's
selections so app.py can apply them to the dataset.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple
import pandas as pd
import streamlit as st


@dataclass
class FilterState:
    page: str
    categories: List[str]
    rating_range: Optional[Tuple[float, float]]
    price_range: Optional[Tuple[float, float]]


def render_sidebar(df: pd.DataFrame) -> FilterState:
    with st.sidebar:
        st.markdown("## 📦 Amazon Analytics")
        st.markdown("---")
        page = st.radio(
            "Navigate",
            ["🏠 Home", "📈 Analytics", "📋 Product Explorer"],
            label_visibility="collapsed",
        )
        st.markdown("---")
        st.markdown("### 🎯 Filters")

        categories = sorted(df["category"].dropna().unique().tolist()) if "category" in df.columns else []
        selected_categories = st.multiselect("Category", categories, default=[])

        rating_range = None
        if "rating" in df.columns:
            min_r, max_r = float(df["rating"].min()), float(df["rating"].max())
            rating_range = st.slider("Rating", min_r, max_r, (min_r, max_r))

        price_range = None
        if "discounted_price" in df.columns:
            min_p, max_p = float(df["discounted_price"].min()), float(df["discounted_price"].max())
            price_range = st.slider("Price Range (₹)", min_p, max_p, (min_p, max_p))

        st.markdown("---")
        st.caption("Built with ❤️ using Streamlit")

    return FilterState(
        page=page,
        categories=selected_categories,
        rating_range=rating_range,
        price_range=price_range,
    )


def apply_filters(df: pd.DataFrame, filters: FilterState) -> pd.DataFrame:
    filtered = df.copy()
    if filters.categories:
        filtered = filtered[filtered["category"].isin(filters.categories)]
    if filters.rating_range is not None:
        filtered = filtered[
            (filtered["rating"] >= filters.rating_range[0]) & (filtered["rating"] <= filters.rating_range[1])
        ]
    if filters.price_range is not None:
        filtered = filtered[
            (filtered["discounted_price"] >= filters.price_range[0])
            & (filtered["discounted_price"] <= filters.price_range[1])
        ]
    return filtered
