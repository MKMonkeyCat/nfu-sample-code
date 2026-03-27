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
    CAPTION_CHANGES_PREFIX,
    CAPTION_CHART_DISTRIBUTION,
    CAPTION_COUNT_SUMMARY,
    CAPTION_DATA_DETAIL,
    CAPTION_MULTI_ROUND_CHART,
    CAPTION_REPORT_PAGE,
    CAPTION_ROUND_COMPARISON,
    CHANGES_JOINER,
    COLUMN_DRINK,
    COLUMN_MODES,
    COLUMN_NAME,
    COLUMN_RATIO,
    COLUMN_ROUND,
    COLUMN_VOTES,
    INFO_SINGLE_ROUND_ONLY,
    METRIC_TOTAL_VOTES,
    METRIC_VOTERS,
    SUBHEADER_CHART_DISTRIBUTION,
    SUBHEADER_COUNT_SUMMARY,
    SUBHEADER_DATA_DETAIL,
    SUBHEADER_MULTI_ROUND_CHART,
    SUBHEADER_ROUND_COMPARISON,
    SUMMARY_COUNT_TEMPLATE,
    SUMMARY_METRIC_LEAST,
    SUMMARY_METRIC_MODES,
    SUMMARY_TOOLTIP_LEAST_TEMPLATE,
    SUMMARY_TOOLTIP_MODES_TEMPLATE,
    TITLE_REPORT_PAGE,
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
    col1.metric(METRIC_TOTAL_VOTES, summary.total)
    col2.metric(METRIC_VOTERS, stats.unique_voters)
    with col3:
        render_hover_metric(
            SUMMARY_METRIC_MODES,
            modes,
            SUMMARY_COUNT_TEMPLATE.format(count=summary.mode_count),
            SUMMARY_TOOLTIP_MODES_TEMPLATE.format(modes=modes),
        )
    with col4:
        render_hover_metric(
            SUMMARY_METRIC_LEAST,
            least,
            SUMMARY_COUNT_TEMPLATE.format(count=summary.least_count),
            SUMMARY_TOOLTIP_LEAST_TEMPLATE.format(least=least),
        )


def render_round_report(stats: StatisticsData) -> None:
    """顯示多輪比較結果"""
    if len(stats.rounds) <= 1:
        st.info(INFO_SINGLE_ROUND_ONLY)
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
    st.dataframe(display_rows, use_container_width=True, hide_index=True)

    changes = core.get_mode_changes(CSV_FILE)
    if changes:
        st.caption(CAPTION_CHANGES_PREFIX + CHANGES_JOINER.join(changes))


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
    st.dataframe(display_rows, use_container_width=True, hide_index=True)


def render_report_page(records: list[VoteRecord], summary: SummaryData, stats: StatisticsData) -> None:
    """顯示報表頁面"""
    st.title(TITLE_REPORT_PAGE)
    st.caption(CAPTION_REPORT_PAGE)

    if not records:
        render_empty_report()
        return

    render_summary_metrics(summary, stats)
    st.divider()

    chart_col, table_col = st.columns([1.4, 1], gap="large")
    with chart_col:
        st.subheader(SUBHEADER_CHART_DISTRIBUTION)
        st.caption(CAPTION_CHART_DISTRIBUTION)
        render_bar_chart(summary)

    with table_col:
        st.subheader(SUBHEADER_COUNT_SUMMARY)
        st.caption(CAPTION_COUNT_SUMMARY)
        count_rows = build_count_rows(summary)
        display_count_rows = [
            {
                COLUMN_DRINK: row["option"],
                COLUMN_VOTES: row["votes"],
                COLUMN_RATIO: row["ratio"],
            }
            for row in count_rows
        ]
        st.dataframe(display_count_rows, use_container_width=True, hide_index=True)

    st.divider()
    st.subheader(SUBHEADER_MULTI_ROUND_CHART)
    st.caption(CAPTION_MULTI_ROUND_CHART)
    render_round_grouped_bar_chart(stats)

    st.divider()
    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        st.subheader(SUBHEADER_ROUND_COMPARISON)
        st.caption(CAPTION_ROUND_COMPARISON)
        render_round_report(stats)

    with right_col:
        st.subheader(SUBHEADER_DATA_DETAIL)
        st.caption(CAPTION_DATA_DETAIL)
        render_data_table(records)


def render_report_app() -> None:
    """顯示報表頁面"""
    records, summary, stats = load_app_data()
    render_report_page(records, summary, stats)
