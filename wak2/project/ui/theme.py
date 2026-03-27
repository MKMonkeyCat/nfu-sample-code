from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """設定主題"""
    st.markdown(
        """
        <style>
        :root {
            --bg: #F5F7FB;
            --surface: rgba(255, 255, 255, 0.88);
            --surface-strong: #FFFFFF;
            --text: #162033;
            --muted: #5B6578;
            --accent: #1F6FEB;
            --accent-soft: #EAF2FF;
            --border: rgba(22, 32, 51, 0.10);
            --danger: #D14343;
        }
        * {
            font-family: "Microsoft JhengHei", sans-serif;
        }
        .stApp {
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(31, 111, 235, 0.10), transparent 26%),
                linear-gradient(180deg, #F9FBFF 0%, #F3F6FB 100%);
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #F8FAFD 0%, #EEF3F9 100%);
            border-right: 1px solid var(--border);
        }
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px 16px;
        }
        [data-testid="stMetricLabel"] {
            color: var(--muted);
        }
        [data-testid="stMetricValue"] {
            color: var(--text);
        }
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #1F6FEB 0%, #3286F5 100%);
            color: white;
            font-weight: 600;
            min-height: 42px;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            filter: brightness(1.03);
        }
        [data-testid="stSidebar"] .stButton > button {
            background: white;
            color: var(--danger);
            border: 1px solid rgba(209, 67, 67, 0.20);
        }
        [data-baseweb="input"] input,
        [data-baseweb="select"] > div,
        .stTextInput input {
            background: rgba(255, 255, 255, 0.96) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
        }
        .summary-line {
            color: var(--muted);
            font-size: 0.95rem;
            margin-bottom: 0.4rem;
        }
        .metric-hover-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px 16px;
            min-height: 96px;
        }
        .metric-hover-label {
            color: var(--muted);
            font-size: 0.95rem;
            margin-bottom: 0.35rem;
        }
        .metric-hover-value {
            color: var(--text);
            font-size: 1.55rem;
            font-weight: 700;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .metric-hover-delta {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def configure_page(page_title: str) -> None:
    """設定共用的 Streamlit 頁面設定"""
    st.set_page_config(
        page_title=page_title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )
