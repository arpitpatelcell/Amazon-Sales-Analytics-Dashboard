"""
components/charts.py
Every chart is a small, pure function: (DataFrame) -> plotly Figure or None.
This makes each chart independently testable and reusable across pages.
"""

from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


def top_categories_bar(df: pd.DataFrame, n: int = 10) -> Optional[go.Figure]:
    if "category" not in df.columns:
        return None
    cat_counts = df["category"].value_counts().head(n).reset_index()
    cat_counts.columns = ["category", "count"]
    fig = px.bar(
        cat_counts, x="count", y="category", orientation="h",
        title=f"Top {n} Categories by Product Count",
        color="count", color_continuous_scale="Oranges",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def rating_histogram(df: pd.DataFrame) -> Optional[go.Figure]:
    if "rating" not in df.columns:
        return None
    return px.histogram(
        df, x="rating", nbins=20,
        title="Rating Distribution", color_discrete_sequence=["#FF9900"],
    )


def category_pie(df: pd.DataFrame, n: int = 8) -> Optional[go.Figure]:
    if "category" not in df.columns:
        return None
    pie_data = df["category"].value_counts().head(n).reset_index()
    pie_data.columns = ["category", "count"]
    return px.pie(pie_data, names="category", values="count", title=f"Category Share (Top {n})", hole=0.4)


def top_reviewed_products_bar(df: pd.DataFrame, n: int = 10) -> Optional[go.Figure]:
    if "product_name" not in df.columns or "rating_count" not in df.columns:
        return None
    top = df.nlargest(n, "rating_count")[["product_name", "rating_count"]].copy()
    top["product_name"] = top["product_name"].str.slice(0, 35) + "..."
    fig = px.bar(
        top, x="rating_count", y="product_name", orientation="h",
        title=f"Top {n} Most Reviewed Products", color="rating_count",
        color_continuous_scale="Blues",
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def price_scatter(df: pd.DataFrame) -> Optional[go.Figure]:
    if "actual_price" not in df.columns or "discounted_price" not in df.columns:
        return None
    return px.scatter(
        df, x="actual_price", y="discounted_price",
        color="rating" if "rating" in df.columns else None,
        title="Actual Price vs Discounted Price", color_continuous_scale="Viridis",
        hover_data=["product_name"] if "product_name" in df.columns else None,
    )


def discount_histogram(df: pd.DataFrame) -> Optional[go.Figure]:
    if "discount_percentage" not in df.columns:
        return None
    return px.histogram(
        df, x="discount_percentage", nbins=25,
        title="Discount Percentage Distribution", color_discrete_sequence=["#38ef7d"],
    )


def price_box_by_category(df: pd.DataFrame, n: int = 8) -> Optional[go.Figure]:
    if "category" not in df.columns or "discounted_price" not in df.columns:
        return None
    top_cats = df["category"].value_counts().head(n).index
    box_df = df[df["category"].isin(top_cats)]
    fig = px.box(box_df, x="category", y="discounted_price", title="Price Spread by Category", color="category")
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    return fig


def rating_box_by_category(df: pd.DataFrame, n: int = 8) -> Optional[go.Figure]:
    if "category" not in df.columns or "rating" not in df.columns:
        return None
    top_cats = df["category"].value_counts().head(n).index
    box_df = df[df["category"].isin(top_cats)]
    fig = px.box(box_df, x="category", y="rating", title="Rating Spread by Category", color="category")
    fig.update_layout(showlegend=False, xaxis_tickangle=-30)
    return fig


def avg_price_trend_line(df: pd.DataFrame, n: int = 10) -> Optional[go.Figure]:
    if "category" not in df.columns or "discounted_price" not in df.columns:
        return None
    avg_price = df.groupby("category")["discounted_price"].mean().sort_values(ascending=False).head(n).reset_index()
    fig = px.line(avg_price, x="category", y="discounted_price", title="Average Price Across Top Categories", markers=True)
    fig.update_layout(xaxis_tickangle=-30)
    return fig


def rating_vs_price_scatter(df: pd.DataFrame) -> Optional[go.Figure]:
    if "rating" not in df.columns or "discounted_price" not in df.columns:
        return None
    return px.scatter(
        df, x="rating", y="discounted_price",
        color="category" if "category" in df.columns else None,
        title="Rating vs Price", hover_data=["product_name"] if "product_name" in df.columns else None,
    )


def rating_vs_reviews_scatter(df: pd.DataFrame) -> Optional[go.Figure]:
    if "rating" not in df.columns or "rating_count" not in df.columns:
        return None
    return px.scatter(
        df, x="rating", y="rating_count", size="rating_count", color="rating",
        title="Rating vs Number of Reviews", color_continuous_scale="Sunset",
    )


def category_count_bar(df: pd.DataFrame, n: int = 15) -> Optional[go.Figure]:
    if "category" not in df.columns:
        return None
    cat_counts = df["category"].value_counts().head(n).reset_index()
    cat_counts.columns = ["category", "count"]
    fig = px.bar(cat_counts, x="category", y="count", title=f"Top {n} Categories by Product Count",
                 color="count", color_continuous_scale="Purples")
    fig.update_layout(xaxis_tickangle=-40)
    return fig


def top_rated_categories_bar(df: pd.DataFrame, n: int = 10) -> Optional[go.Figure]:
    if "category" not in df.columns or "rating" not in df.columns:
        return None
    avg_rating = df.groupby("category")["rating"].mean().sort_values(ascending=False).head(n).reset_index()
    fig = px.bar(avg_rating, x="rating", y="category", orientation="h", title=f"Top {n} Categories by Average Rating",
                 color="rating", color_continuous_scale="Teal")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    return fig


def price_correlation_heatmap(df: pd.DataFrame) -> Optional[go.Figure]:
    """Correlation heatmap across all numeric columns — a common 'industry-level' addition."""
    numeric_cols = [c for c in ["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"] if c in df.columns]
    if len(numeric_cols) < 2:
        return None
    corr = df[numeric_cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
        title="Correlation Heatmap (Numeric Fields)",
    )
    return fig


def render_chart(fig: Optional[go.Figure], st_module) -> None:
    """Safely render a chart, or show an info message if data was insufficient."""
    if fig is None:
        st_module.info("Not enough data to render this chart for the current filters.")
    else:
        st_module.plotly_chart(fig, use_container_width=True)
