from __future__ import annotations

import streamlit as st

from project.types import StatisticsData, SummaryData, VoteRecord

from . import texts
from .charts import render_bar_chart
from .shared import load_app_data, render_recent_votes


def render_overview_page(records: list[VoteRecord], summary: SummaryData, stats: StatisticsData) -> None:
    """顯示大屏即時概況頁。"""
    st.title(texts.TITLE_OVERVIEW_PAGE)
    st.caption(texts.CAPTION_OVERVIEW_PAGE)

    leader = "、".join(summary.modes) if summary.modes else "尚未產生"
    metric_cols = st.columns(4)
    metric_cols[0].metric(texts.METRIC_MODE_NOW, leader)
    metric_cols[1].metric(texts.METRIC_TOTAL_VOTES, summary.total)
    metric_cols[2].metric(texts.METRIC_VOTERS, stats.unique_voters)
    metric_cols[3].metric(texts.METRIC_ROUNDS, len(stats.rounds) or 1)

    chart_col, recent_col = st.columns([1.6, 1], gap="large")
    with chart_col:
        st.subheader(texts.SUBHEADER_OVERVIEW_CHART)
        render_bar_chart(summary)

    with recent_col:
        st.subheader(texts.SUBHEADER_OVERVIEW_RECENT)
        if records:
            render_recent_votes(records)
        else:
            st.info(texts.INFO_NO_VOTE_DATA)


def render_overview_app() -> None:
    """顯示即時概況大屏頁面。"""
    records, summary, stats = load_app_data(show_sidebar=False)
    render_overview_page(records, summary, stats)
