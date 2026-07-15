"""
components/styles.py
All custom CSS lives here — keeping presentation separate from logic.
"""

import streamlit as st


def inject_custom_css() -> None:
    st.markdown("""
    <style>
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
        .kpi-value { font-size: 28px; font-weight: 800; margin: 0; }
        .kpi-label {
            font-size: 13px; opacity: 0.9; margin: 0;
            text-transform: uppercase; letter-spacing: 0.5px;
        }
        .section-header {
            font-size: 24px; font-weight: 700;
            border-left: 5px solid #FF9900;
            padding-left: 12px; margin: 25px 0 15px 0;
        }
        .footer {
            text-align: center; color: #9aa0a6; font-size: 13px;
            padding: 30px 0 10px 0; border-top: 1px solid #262730;
            margin-top: 40px;
        }
        div[data-testid="stMetric"] {
            background-color: #1c1f26; border-radius: 12px; padding: 10px;
        }
    </style>
    """, unsafe_allow_html=True)
