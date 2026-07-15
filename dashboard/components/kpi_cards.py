"""
components/kpi_cards.py
Renders the 5 top-level KPI cards.
"""

import pandas as pd
import streamlit as st

from config import KPI_GRADIENTS


def render_kpi_cards(df: pd.DataFrame) -> None:
    total_products = len(df)
    total_categories = df["category"].nunique() if "category" in df.columns else 0
    avg_rating = df["rating"].mean() if "rating" in df.columns else 0
    avg_discount = df["discount_percentage"].mean() if "discount_percentage" in df.columns else 0
    avg_price = df["discounted_price"].mean() if "discounted_price" in df.columns else 0

    kpi_data = [
        ("Total Products", f"{total_products:,}", "📦"),
        ("Total Categories", f"{total_categories:,}", "🗂️"),
        ("Average Rating", f"{avg_rating:.2f} ⭐", "⭐"),
        ("Average Discount", f"{avg_discount:.1f}%", "🏷️"),
        ("Average Selling Price", f"₹{avg_price:,.0f}", "💰"),
    ]

    cols = st.columns(5)
    for col, (label, value, icon), gradient in zip(cols, kpi_data, KPI_GRADIENTS):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card" style="background:{gradient};">
                    <p class="kpi-label">{icon} {label}</p>
                    <p class="kpi-value">{value}</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
