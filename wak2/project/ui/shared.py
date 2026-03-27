from __future__ import annotations

import html

import streamlit as st

from project import core
from project.types import StatisticsData, SummaryData, VoteRecord

from .config import CSV_FILE, init_app
from .texts import (
    COLUMN_DRINK,
    COLUMN_NAME,
    COLUMN_ROUND,
    FORM_DELETE_ID,
    RECENT_VOTES_LIMIT,
)
from .theme import apply_theme


def format_list(items: list[str], empty: str = "無") -> str:
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
        st.markdown("### 投票管理")
        st.caption("資料會寫入 `data/votes.csv`，送出後立即更新報表內容")
        st.markdown(
            f"""
            <div class="summary-line">總票數：{stats.total}</div>
            <div class="summary-line">投票者：{stats.unique_voters}</div>
            <div class="summary-line">輪次：{len(stats.rounds) or 1}</div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("### 資料清理")
        st.caption("刪除後的資料不可復原")

        delete_options = build_delete_options(records)
        labels = [label for label, _ in delete_options]
        index_map = {label: index for label, index in delete_options}

        with st.form(FORM_DELETE_ID, clear_on_submit=True):
            selected_labels = st.multiselect(
                "選擇要刪除的資料",
                options=labels,
                placeholder="可複選",
                disabled=not labels,
            )
            delete_submitted = st.form_submit_button("刪除選取資料", use_container_width=True)

            if delete_submitted:
                selected_indices = [index_map[label] for label in selected_labels]
                deleted_count = core.delete_votes_by_indices(CSV_FILE, selected_indices)
                if deleted_count == 0:
                    st.warning("請先選擇要刪除的資料")
                else:
                    st.success(f"已刪除 {deleted_count} 筆資料")
                    st.rerun()


def render_empty_report() -> None:
    """為兩個分頁提供無資料時的顯示狀態"""
    st.info("目前尚無投票資料，請先到「投票系統」頁面新增資料")


def render_recent_votes(records: list[VoteRecord]) -> None:
    """顯示最新的投票紀錄"""
    recent = list(reversed(records[-RECENT_VOTES_LIMIT:]))
    rows = [{COLUMN_ROUND: r.round, COLUMN_NAME: r.name, COLUMN_DRINK: r.option} for r in recent]
    st.dataframe(rows, use_container_width=True, hide_index=True)
