"""
Amazon Sales Analytics Dashboard
A complete, professional Streamlit dashboard for exploring Amazon sales data.

Run with:
    streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os

# ----------------------------------------------------------------------------
# PAGE CONFIG (must be the first Streamlit command)
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Amazon Sales Analytics Dashboard",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------------------------------------------------------
# CUSTOM CSS — Modern gradient theme, colored KPI cards, footer
# ----------------------------------------------------------------------------
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .hero-title {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #FF9900, #FF5F6D, #FFC371);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        padding: 10px 0 0 0;
    }
    .hero-subtitle {
        text-align: center;
        color: #9aa0a6;
        font-size: 16px;
        padding-bottom: 20px;
    }
    .kpi-card {
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        color: white;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        margin-bottom: 10px;
    }
    .kpi-value {
        font-size: 28px;
        font-weight: 800;
        margin: 0;
    }
    .kpi-label {
        font-size: 13px;
        opacity: 0.9;
        margin: 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .section-header {
        font-size: 24px;
        font-weight: 700;
        border-left: 5px solid #FF9900;
        padding-left: 12px;
        margin: 25px 0 15px 0;
    }
    .footer {
        text-align: center;
        color: #9aa0a6;
        font-size: 13px;
        padding: 30px 0 10px 0;
        border-top: 1px solid #262730;
        margin-top: 40px;
    }
    div[data-testid="stMetric"] {
        background-color: #1c1f26;
        border-radius: 12px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# DATA LOADING & CLEANING
# ----------------------------------------------------------------------------
DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "dataset", "amazon.csv")


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)

    # Standardize column names (lowercase, strip spaces)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    # Helper: find the first matching column from a list of candidates
    def find_col(candidates):
        for c in candidates:
            if c in df.columns:
                return c
        return None

    col_map = {
        "product_name": find_col(["product_name", "product", "name"]),
        "category": find_col(["category", "product_category"]),
        "discounted_price": find_col(["discounted_price", "sale_price", "selling_price"]),
        "actual_price": find_col(["actual_price", "original_price", "mrp"]),
        "discount_percentage": find_col(["discount_percentage", "discount_percent", "discount"]),
        "rating": find_col(["rating", "star_rating"]),
        "rating_count": find_col(["rating_count", "num_ratings", "reviews_count"]),
    }

    # Clean price/percentage columns: remove currency symbols, %, commas
    for key in ["discounted_price", "actual_price", "discount_percentage", "rating_count"]:
        c = col_map[key]
        if c is not None:
            df[c] = (
                df[c]
                .astype(str)
                .str.replace("₹", "", regex=False)
                .str.replace(",", "", regex=False)
                .str.replace("%", "", regex=False)
                .str.strip()
            )
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Clean rating column (sometimes contains non-numeric junk)
    rc = col_map["rating"]
    if rc is not None:
        df[rc] = pd.to_numeric(df[rc].astype(str).str.strip(), errors="coerce")

    # Drop rows with completely missing essential fields
    essential = [c for c in [col_map["product_name"], col_map["category"]] if c is not None]
    if essential:
        df = df.dropna(subset=essential)

    # Fill numeric NaNs with median so charts don't break
    for key in ["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]:
        c = col_map[key]
        if c is not None and df[c].isna().any():
            df[c] = df[c].fillna(df[c].median())

    # Rename to standard internal names for the rest of the app
    rename_dict = {v: k for k, v in col_map.items() if v is not None}
    df = df.rename(columns=rename_dict)

    # If category has pipe-separated hierarchy (common in this dataset), take the top level
    if "category" in df.columns:
        df["category"] = df["category"].astype(str).str.split("|").str[0]

    return df


if not os.path.exists(DATA_PATH):
    st.error(f"⚠️ Dataset not found at `{DATA_PATH}`. Please make sure `amazon.csv` is inside the `dataset/` folder.")
    st.stop()

df = load_data(DATA_PATH)

# ----------------------------------------------------------------------------
# SIDEBAR — NAVIGATION + FILTERS
# ----------------------------------------------------------------------------
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

    if "rating" in df.columns:
        min_r, max_r = float(df["rating"].min()), float(df["rating"].max())
        rating_range = st.slider("Rating", min_r, max_r, (min_r, max_r))
    else:
        rating_range = None

    if "discounted_price" in df.columns:
        min_p, max_p = float(df["discounted_price"].min()), float(df["discounted_price"].max())
        price_range = st.slider("Price Range (₹)", min_p, max_p, (min_p, max_p))
    else:
        price_range = None

    st.markdown("---")
    st.caption("Built with ❤️ using Streamlit")

# Apply filters
filtered_df = df.copy()
if selected_categories:
    filtered_df = filtered_df[filtered_df["category"].isin(selected_categories)]
if rating_range is not None:
    filtered_df = filtered_df[
        (filtered_df["rating"] >= rating_range[0]) & (filtered_df["rating"] <= rating_range[1])
    ]
if price_range is not None:
    filtered_df = filtered_df[
        (filtered_df["discounted_price"] >= price_range[0]) & (filtered_df["discounted_price"] <= price_range[1])
    ]

# ----------------------------------------------------------------------------
# HERO HEADER
# ----------------------------------------------------------------------------
st.markdown('<p class="hero-title">📊 Amazon Sales Analytics Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Explore product performance, pricing trends, and customer ratings — all in one place.</p>',
    unsafe_allow_html=True,
)

# ----------------------------------------------------------------------------
# KPI CARDS
# ----------------------------------------------------------------------------
total_products = len(filtered_df)
total_categories = filtered_df["category"].nunique() if "category" in filtered_df.columns else 0
avg_rating = filtered_df["rating"].mean() if "rating" in filtered_df.columns else 0
avg_discount = filtered_df["discount_percentage"].mean() if "discount_percentage" in filtered_df.columns else 0
avg_price = filtered_df["discounted_price"].mean() if "discounted_price" in filtered_df.columns else 0

kpi_data = [
    ("Total Products", f"{total_products:,}", "📦", "linear-gradient(135deg,#FF9900,#FF5F6D)"),
    ("Total Categories", f"{total_categories:,}", "🗂️", "linear-gradient(135deg,#36D1DC,#5B86E5)"),
    ("Average Rating", f"{avg_rating:.2f} ⭐", "⭐", "linear-gradient(135deg,#F7971E,#FFD200)"),
    ("Average Discount", f"{avg_discount:.1f}%", "🏷️", "linear-gradient(135deg,#11998e,#38ef7d)"),
    ("Average Selling Price", f"₹{avg_price:,.0f}", "💰", "linear-gradient(135deg,#8E2DE2,#4A00E0)"),
]

cols = st.columns(5)
for col, (label, value, icon, gradient) in zip(cols, kpi_data):
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

st.markdown("---")

# ============================================================================
# PAGE: HOME
# ============================================================================
if page == "🏠 Home":
    st.markdown('<p class="section-header">📈 Quick Overview</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if "category" in filtered_df.columns:
            cat_counts = filtered_df["category"].value_counts().head(10).reset_index()
            cat_counts.columns = ["category", "count"]
            fig = px.bar(
                cat_counts, x="count", y="category", orientation="h",
                title="Top 10 Categories by Product Count",
                color="count", color_continuous_scale="Oranges",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        if "rating" in filtered_df.columns:
            fig = px.histogram(
                filtered_df, x="rating", nbins=20,
                title="Rating Distribution", color_discrete_sequence=["#FF9900"],
            )
            st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        if "category" in filtered_df.columns:
            pie_data = filtered_df["category"].value_counts().head(8).reset_index()
            pie_data.columns = ["category", "count"]
            fig = px.pie(
                pie_data, names="category", values="count",
                title="Category Share (Top 8)", hole=0.4,
            )
            st.plotly_chart(fig, use_container_width=True)

    with c4:
        if "product_name" in filtered_df.columns and "rating_count" in filtered_df.columns:
            top_products = filtered_df.nlargest(10, "rating_count")[["product_name", "rating_count"]]
            top_products["product_name"] = top_products["product_name"].str.slice(0, 35) + "..."
            fig = px.bar(
                top_products, x="rating_count", y="product_name", orientation="h",
                title="Top 10 Most Reviewed Products", color="rating_count",
                color_continuous_scale="Blues",
            )
            fig.update_layout(yaxis={"categoryorder": "total ascending"})
            st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: ANALYTICS (all chart types)
# ============================================================================
elif page == "📈 Analytics":
    st.markdown('<p class="section-header">📊 Deep Dive Analytics</p>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["💰 Pricing", "⭐ Ratings", "🗂️ Categories"])

    # ---------------- PRICING TAB ----------------
    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            if "discounted_price" in filtered_df.columns and "actual_price" in filtered_df.columns:
                fig = px.scatter(
                    filtered_df, x="actual_price", y="discounted_price",
                    color="rating" if "rating" in filtered_df.columns else None,
                    title="Actual Price vs Discounted Price",
                    color_continuous_scale="Viridis",
                    hover_data=["product_name"] if "product_name" in filtered_df.columns else None,
                )
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if "discount_percentage" in filtered_df.columns:
                fig = px.histogram(
                    filtered_df, x="discount_percentage", nbins=25,
                    title="Discount Percentage Distribution",
                    color_discrete_sequence=["#38ef7d"],
                )
                st.plotly_chart(fig, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            if "category" in filtered_df.columns and "discounted_price" in filtered_df.columns:
                top_cats = filtered_df["category"].value_counts().head(8).index
                box_df = filtered_df[filtered_df["category"].isin(top_cats)]
                fig = px.box(
                    box_df, x="category", y="discounted_price",
                    title="Price Spread by Category (Box Plot)",
                    color="category",
                )
                fig.update_layout(showlegend=False, xaxis_tickangle=-30)
                st.plotly_chart(fig, use_container_width=True)
        with c4:
            if "category" in filtered_df.columns and "discounted_price" in filtered_df.columns:
                avg_price_cat = filtered_df.groupby("category")["discounted_price"].mean().sort_values(ascending=False).head(10).reset_index()
                fig = px.line(
                    avg_price_cat, x="category", y="discounted_price",
                    title="Average Price Trend Across Top Categories", markers=True,
                )
                fig.update_layout(xaxis_tickangle=-30)
                st.plotly_chart(fig, use_container_width=True)

    # ---------------- RATINGS TAB ----------------
    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            if "rating" in filtered_df.columns and "discounted_price" in filtered_df.columns:
                fig = px.scatter(
                    filtered_df, x="rating", y="discounted_price",
                    color="category" if "category" in filtered_df.columns else None,
                    title="Rating vs Price",
                    hover_data=["product_name"] if "product_name" in filtered_df.columns else None,
                )
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if "rating" in filtered_df.columns and "category" in filtered_df.columns:
                top_cats = filtered_df["category"].value_counts().head(8).index
                box_df = filtered_df[filtered_df["category"].isin(top_cats)]
                fig = px.box(
                    box_df, x="category", y="rating",
                    title="Rating Spread by Category (Box Plot)",
                    color="category",
                )
                fig.update_layout(showlegend=False, xaxis_tickangle=-30)
                st.plotly_chart(fig, use_container_width=True)

        if "rating" in filtered_df.columns and "rating_count" in filtered_df.columns:
            fig = px.scatter(
                filtered_df, x="rating", y="rating_count", size="rating_count",
                color="rating", title="Rating vs Number of Reviews",
                color_continuous_scale="Sunset",
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---------------- CATEGORIES TAB ----------------
    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            if "category" in filtered_df.columns:
                cat_counts = filtered_df["category"].value_counts().head(15).reset_index()
                cat_counts.columns = ["category", "count"]
                fig = px.bar(
                    cat_counts, x="category", y="count",
                    title="Top 15 Categories by Product Count",
                    color="count", color_continuous_scale="Purples",
                )
                fig.update_layout(xaxis_tickangle=-40)
                st.plotly_chart(fig, use_container_width=True)
        with c2:
            if "category" in filtered_df.columns and "rating" in filtered_df.columns:
                avg_rating_cat = filtered_df.groupby("category")["rating"].mean().sort_values(ascending=False).head(10).reset_index()
                fig = px.bar(
                    avg_rating_cat, x="rating", y="category", orientation="h",
                    title="Top 10 Categories by Average Rating",
                    color="rating", color_continuous_scale="Teal",
                )
                fig.update_layout(yaxis={"categoryorder": "total ascending"})
                st.plotly_chart(fig, use_container_width=True)

# ============================================================================
# PAGE: PRODUCT EXPLORER
# ============================================================================
elif page == "📋 Product Explorer":
    st.markdown('<p class="section-header">🔍 Product Explorer</p>', unsafe_allow_html=True)

    search_col, sort_col = st.columns([2, 1])
    with search_col:
        search_term = st.text_input("🔎 Search Product", placeholder="Type a product name...")
    with sort_col:
        sort_options = [c for c in ["rating", "discounted_price", "actual_price", "discount_percentage", "rating_count"] if c in filtered_df.columns]
        sort_by = st.selectbox("Sort by", sort_options if sort_options else ["None"])

    explorer_df = filtered_df.copy()
    if search_term and "product_name" in explorer_df.columns:
        explorer_df = explorer_df[explorer_df["product_name"].str.contains(search_term, case=False, na=False)]

    if sort_by in explorer_df.columns:
        explorer_df = explorer_df.sort_values(by=sort_by, ascending=False)

    display_cols = [c for c in ["product_name", "category", "actual_price", "discounted_price",
                                 "discount_percentage", "rating", "rating_count"] if c in explorer_df.columns]

    st.markdown(f"**{len(explorer_df):,} products found**")
    st.dataframe(explorer_df[display_cols], use_container_width=True, height=500)

    # ---------------- EXPORT ----------------
    st.markdown('<p class="section-header">📥 Export Data</p>', unsafe_allow_html=True)
    csv_data = explorer_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=csv_data,
        file_name="amazon_filtered_data.csv",
        mime="text/csv",
    )

# ----------------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------------
st.markdown(
    """
    <div class="footer">
        📦 Amazon Sales Analytics Dashboard &nbsp;|&nbsp; Built with Streamlit & Plotly &nbsp;|&nbsp; © 2026
    </div>
    """,
    unsafe_allow_html=True,
)