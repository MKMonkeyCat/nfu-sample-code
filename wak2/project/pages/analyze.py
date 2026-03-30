from __future__ import annotations

import html
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib import font_manager

from project.core import VoteCoreService
from project.core.storage import VoteConfig
from project.types.models import VoteRecord
from project.utils.datetime import parse_iso_datetime
from project.utils.streamlit_ui import render_empty_state, render_page_intro

ALL_ROUNDS_VALUE = "__all_rounds__"


def _configure_matplotlib_font() -> None:
    font_path = Path(__file__).resolve().parents[2] / "assets" / "NotoSansJP-VariableFont_wght.ttf"
    if not font_path.exists():
        return

    font_manager.fontManager.addfont(str(font_path))
    font_name = font_manager.FontProperties(fname=str(font_path)).get_name()
    plt.rcParams["font.sans-serif"] = [font_name, "DejaVu Sans"]
    plt.rcParams["axes.unicode_minus"] = False


_configure_matplotlib_font()


def _round_sort_key(config: VoteConfig | None, round_id: str) -> tuple[int, datetime, str]:
    if config is None:
        return (1, datetime.max.replace(tzinfo=UTC), round_id)

    round_config = config.rounds.get(round_id)
    if round_config is None:
        return (1, datetime.max.replace(tzinfo=UTC), round_id)

    try:
        return (0, parse_iso_datetime(round_config.start_time), round_id)
    except ValueError:
        return (0, datetime.max.replace(tzinfo=UTC), round_id)


def _inject_page_style() -> None:
    st.markdown(
        """
        <style>
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
            font-size: 1.05rem;
            font-weight: 700;
            color: #111827;
            line-height: 1.35;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _summary_card(title: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="analyze-summary">
            <div class="analyze-summary-title">{html.escape(title)}</div>
            <div class="analyze-summary-value">{html.escape(value)}</div>
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
    ax.set_title("選項票數分布")
    ax.set_xlabel("選項")
    ax.set_ylabel("票數")
    st.pyplot(fig)
    plt.close(fig)


def _render_pie_chart(counts: dict[str, int]) -> None:
    labels = list(counts.keys())
    values = list(counts.values())

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(values, labels=labels, autopct="%1.1f%%", startangle=90)
    ax.set_title("票數比例")
    st.pyplot(fig)
    plt.close(fig)


def _render_line_chart_by_round(records: list[VoteRecord], config: VoteConfig) -> None:
    round_ids = sorted(
        {str(record.round) for record in records},
        key=lambda value: _round_sort_key(config, value),
    )
    if len(round_ids) < 2:
        st.info("輪次少於 2，暫不顯示折線圖")
        return

    round_labels = [_round_display_name(config, round_id) for round_id in round_ids]
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

    ax.set_title("多輪票數變化")
    ax.set_xlabel("輪次")
    ax.set_ylabel("票數")
    ax.grid(axis="y", linestyle="--", alpha=0.35)
    ax.legend(title="選項", bbox_to_anchor=(1.02, 1), loc="upper left")
    plt.tight_layout()
    st.pyplot(fig)
    plt.close(fig)


def _round_display_name(config: VoteConfig | None, round_uuid: str) -> str:
    if config is None:
        return round_uuid
    voting_round = config.rounds.get(round_uuid)
    return voting_round.name if voting_round else round_uuid


def _format_modes_text(modes: list[str], mode_count: int) -> str:
    if not modes or mode_count <= 0:
        return "目前尚未形成眾數"
    if len(modes) == 1:
        return f"目前眾數是「{modes[0]}」，共有 {mode_count} 票"
    return f"目前為並列眾數：{'、'.join(modes)}，各有 {mode_count} 票"


def _build_round_change_text(all_records: list[VoteRecord], config: VoteConfig) -> str | None:
    round_ids = sorted(
        {str(record.round) for record in all_records}, key=lambda value: _round_sort_key(config, value)
    )
    if len(round_ids) < 2:
        return None

    previous_round_id = round_ids[-2]
    current_round_id = round_ids[-1]
    previous_summary = _summarize_round(all_records, previous_round_id)
    current_summary = _summarize_round(all_records, current_round_id)

    previous_name = _round_display_name(config, previous_round_id)
    current_name = _round_display_name(config, current_round_id)
    previous_modes = set(previous_summary["modes"])
    current_modes = set(current_summary["modes"])

    if previous_modes == current_modes:
        return f"{previous_name} 到 {current_name} 的眾數沒有改變"
    return f"{previous_name} 的眾數是「{'、'.join(previous_summary['modes'])}」，到了 {current_name} 變成「{'、'.join(current_summary['modes'])}」"


def _summarize_round(records: list[VoteRecord], round_id: str) -> dict[str, Any]:
    one_round = [record for record in records if str(record.round) == round_id]
    counts = Counter(record.option for record in one_round)
    if not counts:
        return {"modes": [], "mode_count": 0}

    mode_count = max(counts.values())
    modes = sorted([option for option, count in counts.items() if count == mode_count])
    return {"modes": modes, "mode_count": mode_count}


@st.fragment(run_every=3.0)
def _render_analysis_fragment(
    service: VoteCoreService, vote_uuid: str, selected_round: str, config: VoteConfig
):
    all_records = service.storage.read_vote_records(vote_uuid)

    if not all_records:
        render_empty_state("目前沒有投票資料", hint="先到投票頁累積資料，這裡才會顯示統計", level="warning")
        return

    records = (
        all_records
        if selected_round == ALL_ROUNDS_VALUE
        else [record for record in all_records if str(record.round) == str(selected_round)]
    )

    if not records:
        render_empty_state("目前篩選條件下沒有投票資料", level="warning")
        return

    statistics = service.analysis.statistics(records)
    summary = service.analysis.summarize(records)
    mode_sentence = _format_modes_text(summary.modes, summary.mode_count)
    round_change_text = (
        _build_round_change_text(all_records, config) if selected_round == ALL_ROUNDS_VALUE else None
    )

    st.markdown(
        f"""
        <div class="analyze-summary">
            <div class="analyze-summary-title">結論 (自動更新中: {datetime.now().strftime('%H:%M:%S')})</div>
            <div class="analyze-summary-value">{html.escape(mode_sentence)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if round_change_text:
        st.info(f"多輪變化：{round_change_text}")

    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    metric_col1.metric("總票數", statistics.total)
    metric_col2.metric("投票人數", statistics.unique_voters)
    metric_col3.metric("眾數票數", statistics.mode_count)
    metric_col4.metric("選項數量", statistics.unique_options)

    card_col1, card_col2 = st.columns(2)
    with card_col1:
        _summary_card("眾數", "、".join(summary.modes) if summary.modes else "無")
    with card_col2:
        _summary_card("最少票選項", "、".join(summary.least) if summary.least else "無")

    tab_stats, tab_records, tab_charts = st.tabs(["統計表", "投票明細", "圖表"])

    with tab_stats:
        st.subheader("選項統計")
        st.dataframe(service.analysis.count_rows(summary), width="stretch", hide_index=True)

        st.subheader("輪次比較")
        round_rows = service.analysis.round_rows(all_records)
        mapped_round_rows: list[dict[str, Any]] = []
        for row in round_rows:
            round_uuid = str(row.get("round_name", ""))
            mapped_round_rows.append(
                {
                    **row,
                    "_round_uuid": round_uuid,
                    "round_name": _round_display_name(config, round_uuid),
                }
            )
        mapped_round_rows = sorted(
            mapped_round_rows,
            key=lambda row: _round_sort_key(config, str(row.get("_round_uuid", ""))),
        )
        for row in mapped_round_rows:
            row.pop("_round_uuid", None)
        if selected_round != ALL_ROUNDS_VALUE:
            st.caption("輪次比較固定顯示全部輪次，方便觀察整體變化。")
        st.dataframe(mapped_round_rows, width="stretch", hide_index=True)

    with tab_records:
        st.subheader("投票明細")
        vote_rows = service.analysis.vote_rows(records)
        mapped_vote_rows: list[dict[str, Any]] = []
        for row in vote_rows:
            round_uuid_row = str(row.get("round_name", ""))
            mapped_vote_rows.append(
                {
                    **row,
                    "round_name": _round_display_name(config, round_uuid_row),
                }
            )
        st.dataframe(mapped_vote_rows, width="stretch", hide_index=True)

    with tab_charts:
        chart_col1, chart_col2 = st.columns(2)
        with chart_col1:
            _render_bar_chart(summary.counts, summary.modes)
        with chart_col2:
            _render_pie_chart(summary.counts)

        if selected_round == ALL_ROUNDS_VALUE:
            _render_line_chart_by_round(all_records, config)


def render(service: VoteCoreService) -> None:
    _inject_page_style()
    render_page_intro("分析頁", "圖表與數據將每 3 秒自動更新")

    configs = service.storage.list_vote_configs()
    if not configs:
        render_empty_state("目前沒有投票活動，請先到管理頁建立")
        return

    # 篩選控制項 (放在 Fragment 之外，避免使用者操作選單時被自動重新整理中斷)
    filter_col1, filter_col2 = st.columns([2, 1])
    with filter_col1:
        vote_uuid = st.selectbox(
            "選擇投票主題",
            options=[uuid for uuid, _ in configs],
            format_func=lambda item: f"{service.storage.vote_configs[item].name} ({item[:8]})",
        )

    config = service.storage.get_vote_config(vote_uuid)
    if not config:
        render_empty_state(f"找不到投票設定：{vote_uuid}", level="error")
        return

    # 先獲取一次數據以確定輪次選單內容
    all_records_init = service.storage.read_vote_records(vote_uuid)
    round_ids = sorted(
        {str(record.round) for record in all_records_init}, key=lambda value: _round_sort_key(config, value)
    )

    with filter_col2:
        selected_round = st.selectbox(
            "輪次篩選",
            options=[ALL_ROUNDS_VALUE, *round_ids],
            format_func=lambda value: (
                "全部輪次" if value == ALL_ROUNDS_VALUE else _round_display_name(config, str(value))
            ),
        )

    st.divider()

    # 呼叫自動更新片段
    _render_analysis_fragment(service, vote_uuid, selected_round, config)
