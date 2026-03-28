from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

from project.core import VoteCoreService


def _configure_matplotlib_font() -> None:
    font_path = Path(__file__).resolve().parents[2] / "assets" / "NotoSansJP-VariableFont_wght.ttf"
    if not font_path.exists():
        return

    font_manager.fontManager.addfont(str(font_path))
    font_name = font_manager.FontProperties(fname=str(font_path)).get_name()
    plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


_configure_matplotlib_font()
ALL_ROUNDS_VALUE = "__all_rounds__"


def _inject_page_style() -> None:
    st.markdown(
        """
        <style>
        .analyze-note {
            color: #4b5563;
            font-size: 0.95rem;
            margin-top: -0.2rem;
            margin-bottom: 0.8rem;
        }
        .analyze-summary {
            border: 1px solid #e5e7eb;
            border-radius: 12px;
            padding: 12px 14px;
            background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
            margin-bottom: 0.75rem;
        }
        .analyze-summary-title {
            font-size: 0.82rem;
            color: #6b7280;
            margin-bottom: 0.35rem;
        }
        .analyze-summary-value {
            font-size: 1.1rem;
            font-weight: 700;
            color: #111827;
            line-height: 1.25;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _summary_card(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="analyze-summary">
            <div class="analyze-summary-title">{title}</div>
            <div class="analyze-summary-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_bar_chart(counts: dict[str, int], modes: list[str]) -> None:
    labels = list(counts.keys())
    values = list(counts.values())
    colors = ["#e63946" if label in modes else "#457b9d" for label in labels]

    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(labels, values, color=colors)
    ax.set_title("各選項票數")
    ax.set_xlabel("選項")
    ax.set_ylabel("票數")
    st.pyplot(fig)
    plt.close(fig)


def _render_pie_chart(counts: dict[str, int]) -> None:
    labels = list(counts.keys())
    values = list(counts.values())

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("選項比例")
    st.pyplot(fig)
    plt.close(fig)


def _render_line_chart_by_round(records: list[Any], config: Any) -> None:
    round_ids = sorted({str(record.round) for record in records})
    if len(round_ids) < 2:
        st.info("輪次少於 2，暫不顯示折線圖")
        return

    round_labels = [
        config.rounds.get(round_id).name if round_id in config.rounds else round_id for round_id in round_ids
    ]

    options = sorted({str(record.option) for record in records})
    series_map: dict[str, list[int]] = {option: [] for option in options}

    for round_id in round_ids:
        one_round = [record for record in records if str(record.round) == round_id]
        counts = Counter(str(record.option) for record in one_round)
        for option in options:
            series_map[option].append(int(counts.get(option, 0)))

    fig, ax = plt.subplots(figsize=(9, 4.8))
    for option, values in series_map.items():
        ax.plot(round_labels, values, marker="o", linewidth=2, label=option)

    ax.set_title("多輪票數趨勢")
    ax.set_xlabel("輪次")
    ax.set_ylabel("票數")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(title="選項", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _round_display_name(config: Any, round_uuid: str) -> str:
    if config is None:
        return round_uuid
    voting_round = config.rounds.get(round_uuid, None)
    return voting_round.name if voting_round else round_uuid


def render(service: VoteCoreService) -> None:
    _inject_page_style()

    st.header("分析頁")
    st.markdown(
        "<div class='analyze-note'>可切換投票主題與輪次篩選，所有統計、表格與圖表會同步更新。</div>",
        unsafe_allow_html=True,
    )

    configs = service.storage.list_vote_configs()

    if not configs:
        st.info("目前沒有投票活動，請先到管理頁建立。")
        return

    filter_col1, filter_col2 = st.columns([2, 1])
    with filter_col1:
        vote_uuid = st.selectbox(
            "選擇投票主題",
            options=[uuid for uuid, _ in configs],
            format_func=lambda item: f"{service.storage.vote_configs[item].name} ({item[:8]})",
        )

    all_records = service.storage.read_vote_records(vote_uuid)
    config = service.storage.get_vote_config(vote_uuid)
    if not all_records:
        st.warning("目前沒有投票資料。")
        return

    round_ids = sorted({str(record.round) for record in all_records})
    with filter_col2:
        selected_round = st.selectbox(
            "輪次篩選",
            options=[ALL_ROUNDS_VALUE, *round_ids],
            format_func=lambda value: (
                "全部輪次" if value == ALL_ROUNDS_VALUE else _round_display_name(config, str(value))
            ),
        )

    records = (
        all_records
        if selected_round == ALL_ROUNDS_VALUE
        else [record for record in all_records if str(record.round) == str(selected_round)]
    )

    if not records:
        st.warning("目前篩選條件下沒有投票資料。")
        return

    statistics = service.analysis.statistics(records)
    summary = service.analysis.summarize(records)

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("總票數", statistics.total)
    metric_col2.metric("投票者數", statistics.unique_voters)
    metric_col3.metric("眾數票數", statistics.mode_count)
    metric_col4.metric("選項種類", statistics.unique_options)

    card_col1, card_col2 = st.columns(2)
    with card_col1:
        _summary_card("眾數", "、".join(summary.modes) if summary.modes else "無")
    with card_col2:
        _summary_card("最少選項", "、".join(summary.least) if summary.least else "無")

    tab_stats, tab_records, tab_charts = st.tabs(["統計摘要", "投票紀錄", "圖表分析"])

    with tab_stats:
        st.subheader("選項統計")
        st.dataframe(service.analysis.count_rows(summary), width="stretch", hide_index=True)

        st.subheader("多輪比較")
        round_rows = service.analysis.round_rows(records if selected_round == ALL_ROUNDS_VALUE else records)
        if config is not None:
            mapped_round_rows: list[dict[str, Any]] = []
            for row in round_rows:
                round_uuid = str(row.get("round_name", ""))
                mapped_round_rows.append(
                    {
                        **row,
                        "round_name": _round_display_name(config, round_uuid),
                    }
                )
            st.dataframe(mapped_round_rows, width="stretch", hide_index=True)
        else:
            st.dataframe(round_rows, width="stretch", hide_index=True)

    with tab_records:
        st.subheader("投票紀錄")
        vote_rows = service.analysis.vote_rows(records)
        if config is not None:
            mapped_vote_rows: list[dict[str, Any]] = []
            for row in vote_rows:
                round_uuid = str(row.get("round_name", ""))
                mapped_vote_rows.append(
                    {
                        **row,
                        "round_name": _round_display_name(config, round_uuid),
                    }
                )
            st.dataframe(mapped_vote_rows, width="stretch", hide_index=True)
        else:
            st.dataframe(vote_rows, width="stretch", hide_index=True)

    with tab_charts:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            _render_bar_chart(summary.counts, summary.modes)
        with chart_col2:
            _render_pie_chart(summary.counts)

        if config is not None and selected_round == ALL_ROUNDS_VALUE:
            _render_line_chart_by_round(all_records, config)
