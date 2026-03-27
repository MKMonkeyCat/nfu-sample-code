from __future__ import annotations

import html

import streamlit as st

from project import core
from project.types import StatisticsData, SummaryData, VoteRecord

from .config import CSV_FILE, init_app
from .texts import (
    BUTTON_DELETE_SELECTED,
    COLUMN_DRINK,
    COLUMN_NAME,
    COLUMN_ROUND,
    EMPTY_LIST_PLACEHOLDER,
    FORM_DELETE_ID,
    INFO_EMPTY_REPORT,
    LABEL_DELETE_SELECTION,
    PLACEHOLDER_DELETE_SELECTION,
    RECENT_VOTES_LIMIT,
    SIDEBAR_CAPTION_CLEANUP,
    SIDEBAR_CAPTION_DATA_PATH,
    SIDEBAR_SUMMARY_ROUNDS_TEMPLATE,
    SIDEBAR_SUMMARY_TOTAL_TEMPLATE,
    SIDEBAR_SUMMARY_VOTERS_TEMPLATE,
    SIDEBAR_TITLE_CLEANUP,
    SIDEBAR_TITLE_MANAGEMENT,
    SUCCESS_DELETE_TEMPLATE,
    WARNING_DELETE_NONE,
)
from .theme import apply_theme


def format_list(items: list[str], empty: str = EMPTY_LIST_PLACEHOLDER) -> str:
    """將字串列表格式化以便顯示"""
    return "、".join(items) if items else empty


def build_delete_options(records: list[VoteRecord]) -> list[tuple[str, int]]:
    """在側邊欄建立可選擇的刪除選項"""
    options: list[tuple[str, int]] = []
    sorted_indices = sorted(
        range(len(records)),
        key=lambda index: (
            core.get_round_sort_key(records[index].round),
            records[index].name,
            records[index].option,
        ),
    )
    for display_index, index in enumerate(sorted_indices, start=1):
        record = records[index]
        label = f"{display_index}. {record.round}｜{record.name}｜{record.option}"
        options.append((label, index))
    return options


def render_hover_metric(label: str, value: str, delta: str, tooltip: str) -> None:
    """以指標卡片形式呈現，並在瀏覽器中顯示懸浮提示"""
    escaped_tooltip = html.escape(tooltip, quote=True)
    escaped_label = html.escape(label)
    escaped_value = html.escape(value)
    escaped_delta = html.escape(delta)
    st.markdown(
        f"""
        <div class="metric-hover-card" title="{escaped_tooltip}">
            <div class="metric-hover-label">{escaped_label}</div>
            <div class="metric-hover-value">{escaped_value}</div>
            <div class="metric-hover-delta">{escaped_delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_app_data() -> tuple[list[VoteRecord], SummaryData, StatisticsData]:
    """載入並初始化各頁共用資料"""
    apply_theme()
    init_app()
    records = core.read_votes(CSV_FILE)
    summary = core.build_summary(records)
    stats = core.get_statistics(CSV_FILE)
    render_sidebar(stats, records)
    return records, summary, stats


def render_sidebar(stats: StatisticsData, records: list[VoteRecord]) -> None:
    """顯示共用的側邊欄控制元件"""
    with st.sidebar:
        st.markdown(SIDEBAR_TITLE_MANAGEMENT)
        st.caption(SIDEBAR_CAPTION_DATA_PATH)
        st.markdown(
            f"""
            <div class="summary-line">{SIDEBAR_SUMMARY_TOTAL_TEMPLATE.format(total=stats.total)}</div>
            <div class="summary-line">{SIDEBAR_SUMMARY_VOTERS_TEMPLATE.format(unique_voters=stats.unique_voters)}</div>
            <div class="summary-line">{SIDEBAR_SUMMARY_ROUNDS_TEMPLATE.format(rounds_count=len(stats.rounds) or 1)}</div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown(SIDEBAR_TITLE_CLEANUP)
        st.caption(SIDEBAR_CAPTION_CLEANUP)

        delete_options = build_delete_options(records)
        labels = [label for label, _ in delete_options]
        index_map = {label: index for label, index in delete_options}

        with st.form(FORM_DELETE_ID, clear_on_submit=True):
            selected_labels = st.multiselect(
                LABEL_DELETE_SELECTION,
                options=labels,
                placeholder=PLACEHOLDER_DELETE_SELECTION,
                disabled=not labels,
            )
            delete_submitted = st.form_submit_button(BUTTON_DELETE_SELECTED, use_container_width=True)

            if delete_submitted:
                selected_indices = [index_map[label] for label in selected_labels]
                deleted_count = core.delete_votes_by_indices(CSV_FILE, selected_indices)
                if deleted_count == 0:
                    st.warning(WARNING_DELETE_NONE)
                else:
                    st.success(SUCCESS_DELETE_TEMPLATE.format(count=deleted_count))
                    st.rerun()


def render_empty_report() -> None:
    """為兩個分頁提供無資料時的顯示狀態"""
    st.info(INFO_EMPTY_REPORT)


def render_recent_votes(records: list[VoteRecord]) -> None:
    """顯示最新的投票紀錄"""
    recent = list(reversed(records[-RECENT_VOTES_LIMIT:]))
    rows = [{COLUMN_ROUND: r.round, COLUMN_NAME: r.name, COLUMN_DRINK: r.option} for r in recent]
    st.dataframe(rows, use_container_width=True, hide_index=True)
