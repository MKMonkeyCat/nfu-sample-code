from __future__ import annotations

import streamlit as st

from project import core
from project.types import (
    CountRow,
    RoundComparisonRow,
    StatisticsData,
    SummaryData,
    VoteRecord,
    VoteTableRow,
)

from .charts import render_bar_chart, render_round_grouped_bar_chart
from .config import CSV_FILE
from .shared import format_list, load_app_data, render_empty_report, render_hover_metric
from .texts import (
    COLUMN_DRINK,
    COLUMN_MODES,
    COLUMN_NAME,
    COLUMN_RATIO,
    COLUMN_ROUND,
    COLUMN_VOTES,
)


def build_count_rows(summary: SummaryData) -> list[CountRow]:
    """依照票數排序，建立選項列"""
    counts = summary.counts
    total = summary.total or 1
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [
        {
            "option": option,
            "votes": vote,
            "ratio": f"{vote / total:.0%}",
        }
        for option, vote in sorted_items
    ]


def render_summary_metrics(summary: SummaryData, stats: StatisticsData) -> None:
    """顯示報表指標"""
    modes = format_list(summary.modes)
    least = format_list(summary.least)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總票數", summary.total)
    col2.metric("投票者", stats.unique_voters)
    with col3:
        render_hover_metric(
            "眾數",
            modes,
            "{count} 票".format(count=summary.mode_count),
            "完整眾數品項：{modes}".format(modes=modes),
        )
    with col4:
        render_hover_metric(
            "最少票",
            least,
            "{count} 票".format(count=summary.least_count),
            "完整最少票品項：{least}".format(least=least),
        )


def render_round_report(stats: StatisticsData) -> None:
    """顯示多輪比較結果"""
    if len(stats.rounds) <= 1:
        st.info("目前只有單一輪次，新增多輪資料後會在這裡顯示比較結果")
        return

    comparison = core.compare_rounds(CSV_FILE)
    rows: list[RoundComparisonRow] = []
    for round_name, round_summary in comparison.items():
        rows.append(
            {
                "round_name": round_name,
                "total_votes": round_summary.total,
                "modes_text": format_list(round_summary.modes),
            }
        )

    display_rows = [
        {
            COLUMN_ROUND: row["round_name"],
            COLUMN_VOTES: row["total_votes"],
            COLUMN_MODES: row["modes_text"],
        }
        for row in rows
    ]
    st.dataframe(display_rows, width=True, hide_index=True)

    changes = core.get_mode_changes(CSV_FILE)
    if changes:
        st.caption("變化摘要：" + "；".join(changes))


def render_data_table(records: list[VoteRecord]) -> None:
    """顯示完整資料表"""
    sorted_records = core.sort_records_for_detail(records)
    rows: list[VoteTableRow] = [
        {"round_name": r.round, "voter_name": r.name, "option": r.option} for r in sorted_records
    ]
    display_rows = [
        {
            COLUMN_ROUND: row["round_name"],
            COLUMN_NAME: row["voter_name"],
            COLUMN_DRINK: row["option"],
        }
        for row in rows
    ]
    st.dataframe(display_rows, width=True, hide_index=True)


def render_report_page(records: list[VoteRecord], summary: SummaryData, stats: StatisticsData) -> None:
    """顯示報表頁面"""
    st.title("資料報告")
    st.caption("統計結果、圖表與輪次比較，提供快速分析與展示")

    if not records:
        render_empty_report()
        return

    render_summary_metrics(summary, stats)
    st.divider()

    chart_col, table_col = st.columns([1.4, 1], gap="large")
    with chart_col:
        st.subheader("投票分布圖")
        st.caption("依票數高低排序，眾數會以較深色標示")
        render_bar_chart(summary)

    with table_col:
        st.subheader("票數摘要")
        st.caption("各飲料票數與占比")
        count_rows = build_count_rows(summary)
        display_count_rows = [
            {
                COLUMN_DRINK: row["option"],
                COLUMN_VOTES: row["votes"],
                COLUMN_RATIO: row["ratio"],
            }
            for row in count_rows
        ]
        st.dataframe(display_count_rows, width=True, hide_index=True)

    st.divider()
    st.subheader("多輪比較圖")
    st.caption("以長條圖顯示各飲料在不同輪次的票數比較")
    render_round_grouped_bar_chart(stats)

    st.divider()
    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        st.subheader("輪次比較")
        st.caption("多輪模式下快速比對每輪眾數")
        render_round_report(stats)

    with right_col:
        st.subheader("資料明細")
        st.caption("完整投票紀錄")
        render_data_table(records)


def render_report_app() -> None:
    """顯示報表頁面"""
    records, summary, stats = load_app_data()
    render_report_page(records, summary, stats)
