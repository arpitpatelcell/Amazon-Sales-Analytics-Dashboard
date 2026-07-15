"""
config.py
Central configuration for the Amazon Sales Analytics Dashboard.
Keeping all settings in one place is a standard industry practice —
it means changing a theme color or file path never requires touching
business logic.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file if present (falls back to defaults otherwise)
load_dotenv()

# ----------------------------------------------------------------------------
# APP METADATA
# ----------------------------------------------------------------------------
APP_TITLE = os.getenv("APP_TITLE", "Amazon Sales Analytics Dashboard")
APP_ICON = os.getenv("APP_ICON", "📦")
APP_LAYOUT = "wide"

# ----------------------------------------------------------------------------
# PATHS
# ----------------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.getenv("DATA_PATH", os.path.join(BASE_DIR, "dataset", "amazon.csv"))
LOG_DIR = os.path.join(BASE_DIR, "logs")

# ----------------------------------------------------------------------------
# CACHING
# ----------------------------------------------------------------------------
CACHE_TTL_SECONDS = int(os.getenv("CACHE_TTL_SECONDS", 3600))  # 1 hour default

# ----------------------------------------------------------------------------
# THEME / COLORS
# ----------------------------------------------------------------------------
THEME = {
    "primary": "#FF9900",
    "secondary": "#FF5F6D",
    "accent": "#36D1DC",
    "background": "#0e1117",
    "card_bg": "#1c1f26",
    "text_muted": "#9aa0a6",
}

KPI_GRADIENTS = [
    "linear-gradient(135deg,#FF9900,#FF5F6D)",
    "linear-gradient(135deg,#36D1DC,#5B86E5)",
    "linear-gradient(135deg,#F7971E,#FFD200)",
    "linear-gradient(135deg,#11998e,#38ef7d)",
    "linear-gradient(135deg,#8E2DE2,#4A00E0)",
]

# ----------------------------------------------------------------------------
# COLUMN NAME CANDIDATES (for flexible dataset compatibility)
# ----------------------------------------------------------------------------
COLUMN_CANDIDATES = {
    "product_name": ["product_name", "product", "name"],
    "category": ["category", "product_category"],
    "discounted_price": ["discounted_price", "sale_price", "selling_price"],
    "actual_price": ["actual_price", "original_price", "mrp"],
    "discount_percentage": ["discount_percentage", "discount_percent", "discount"],
    "rating": ["rating", "star_rating"],
    "rating_count": ["rating_count", "num_ratings", "reviews_count"],
}
