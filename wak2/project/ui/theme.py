from __future__ import annotations

import streamlit as st


def apply_theme() -> None:
    """設定主題"""
    st.markdown(
        """
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
