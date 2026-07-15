"""
app.py
Main entry point for the Amazon Sales Analytics Dashboard.

This file is intentionally thin — it wires together config, data loading,
and UI components. All heavy logic lives in dedicated modules
(data_loader.py, components/*), which is standard practice for
maintainable, testable applications.

Run with:
    streamlit run dashboard/app.py
"""

import streamlit as st

import config
from data_loader import load_data, DataLoadError
from utils.logger import get_logger
from components.styles import inject_custom_css
from components.sidebar import render_sidebar, apply_filters
from components.kpi_cards import render_kpi_cards
from components import charts

logger = get_logger(config.LOG_DIR)

# ----------------------------------------------------------------------------
# PAGE CONFIG
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon=config.APP_ICON,
    layout=config.APP_LAYOUT,
    initial_sidebar_state="expanded",
)
inject_custom_css()

# ----------------------------------------------------------------------------
# DATA LOADING (with graceful error handling)
# ----------------------------------------------------------------------------
try:
    df = load_data(config.DATA_PATH)
except DataLoadError as exc:
    logger.error("Data load failed: %s", exc)
    st.error(f"⚠️ {exc}")
    st.stop()
except Exception as exc:  # noqa: BLE001 — top-level safety net for the UI
    logger.exception("Unexpected error while loading data")
    st.error("⚠️ An unexpected error occurred while loading the dataset. Check logs/app.log for details.")
    st.stop()

# ----------------------------------------------------------------------------
# SIDEBAR + FILTERS
# ----------------------------------------------------------------------------
filters = render_sidebar(df)
filtered_df = apply_filters(df, filters)

# ----------------------------------------------------------------------------
# HERO HEADER
# ----------------------------------------------------------------------------
st.markdown(f'<p class="hero-title">📊 {config.APP_TITLE}</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">Explore product performance, pricing trends, and customer ratings — all in one place.</p>',
    unsafe_allow_html=True,
)

render_kpi_cards(filtered_df)
st.markdown("---")

# ============================================================================
# PAGE: HOME
# ============================================================================
if filters.page == "🏠 Home":
    st.markdown('<p class="section-header">📈 Quick Overview</p>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        charts.render_chart(charts.top_categories_bar(filtered_df), st)
    with c2:
        charts.render_chart(charts.rating_histogram(filtered_df), st)

    c3, c4 = st.columns(2)
    with c3:
        charts.render_chart(charts.category_pie(filtered_df), st)
    with c4:
        charts.render_chart(charts.top_reviewed_products_bar(filtered_df), st)

# ============================================================================
# PAGE: ANALYTICS
# ============================================================================
elif filters.page == "📈 Analytics":
    st.markdown('<p class="section-header">📊 Deep Dive Analytics</p>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["💰 Pricing", "⭐ Ratings", "🗂️ Categories", "🔗 Correlations"])

    with tab1:
        c1, c2 = st.columns(2)
        with c1:
            charts.render_chart(charts.price_scatter(filtered_df), st)
        with c2:
            charts.render_chart(charts.discount_histogram(filtered_df), st)
        c3, c4 = st.columns(2)
        with c3:
            charts.render_chart(charts.price_box_by_category(filtered_df), st)
        with c4:
            charts.render_chart(charts.avg_price_trend_line(filtered_df), st)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            charts.render_chart(charts.rating_vs_price_scatter(filtered_df), st)
        with c2:
            charts.render_chart(charts.rating_box_by_category(filtered_df), st)
        charts.render_chart(charts.rating_vs_reviews_scatter(filtered_df), st)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            charts.render_chart(charts.category_count_bar(filtered_df), st)
        with c2:
            charts.render_chart(charts.top_rated_categories_bar(filtered_df), st)

    with tab4:
        st.caption("Shows how numeric fields move together — e.g. does a higher discount correlate with a lower rating?")
        charts.render_chart(charts.price_correlation_heatmap(filtered_df), st)

# ============================================================================
# PAGE: PRODUCT EXPLORER
# ============================================================================
elif filters.page == "📋 Product Explorer":
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

    st.markdown('<p class="section-header">📥 Export Data</p>', unsafe_allow_html=True)
    csv_data = explorer_df[display_cols].to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Filtered Data as CSV", data=csv_data,
                        file_name="amazon_filtered_data.csv", mime="text/csv")

# ----------------------------------------------------------------------------
# FOOTER
# ----------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="footer">
        📦 {config.APP_TITLE} &nbsp;|&nbsp; Built with Streamlit & Plotly &nbsp;|&nbsp; © 2026
    </div>
    """,
    unsafe_allow_html=True,
)
