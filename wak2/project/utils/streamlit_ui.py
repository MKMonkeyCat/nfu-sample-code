from __future__ import annotations

from collections.abc import Sequence

import streamlit as st


def render_page_intro(title: str, description: str) -> None:
    st.header(title)
    st.caption(description)


def render_empty_state(message: str, *, hint: str | None = None, level: str = "info") -> None:
    renderer = getattr(st, level, st.info)
    renderer(message)
    if hint:
        st.caption(hint)


def render_callout(title: str, lines: Sequence[str]) -> None:
    content = "".join(f"<li>{line}</li>" for line in lines)
    st.markdown(
        f"""
        <div style="border:1px solid #e5e7eb;border-radius:14px;padding:14px 16px;background:#fafaf9;margin:0.25rem 0 1rem 0;">
            <div style="font-size:0.84rem;color:#6b7280;margin-bottom:0.45rem;">{title}</div>
            <ul style="margin:0;padding-left:1.1rem;color:#111827;">
                {content}
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
