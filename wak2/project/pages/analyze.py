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


def render(service: VoteCoreService) -> None:
    st.header("分析頁")
    configs = service.storage.list_vote_configs()

    if not configs:
        st.info("目前沒有投票活動，請先到管理頁建立。")
        return

    vote_uuid = st.selectbox(
        "選擇投票主題",
        options=[uuid for uuid, _ in configs],
        format_func=lambda item: f"{service.storage.vote_configs[item].name} ({item[:8]})",
    )

    records = service.storage.read_vote_records(vote_uuid)
    config = service.storage.get_vote_config(vote_uuid)
    if not records:
        st.warning("目前沒有投票資料。")
        return

    statistics = service.analysis.statistics(records)
    summary = service.analysis.summarize(records)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總人數", statistics.total)
    c2.metric("不同投票者", statistics.unique_voters)
    c3.metric("眾數票數", statistics.mode_count)
    c4.metric("最少票數", statistics.least_count)

    st.write(f"眾數：{'、'.join(summary.modes) if summary.modes else '無'}")
    st.write(f"最少選項：{'、'.join(summary.least) if summary.least else '無'}")

    st.subheader("選項統計")
    st.dataframe(service.analysis.count_rows(summary), width="stretch", hide_index=True)

    st.subheader("投票紀錄")
    vote_rows = service.analysis.vote_rows(records)
    if config is not None:
        mapped_vote_rows: list[dict[str, Any]] = []
        for row in vote_rows:
            round_uuid = str(row.get("round_name", ""))
            mapped_vote_rows.append(
                {
                    **row,
                    "round_name": (
                        voting_round.name
                        if (voting_round := config.rounds.get(round_uuid, None))
                        else round_uuid
                    ),
                }
            )
        st.dataframe(mapped_vote_rows, width="stretch", hide_index=True)
    else:
        st.dataframe(vote_rows, width="stretch", hide_index=True)

    st.subheader("多輪比較")
    round_rows = service.analysis.round_rows(records)
    if config is not None:
        mapped_round_rows: list[dict[str, Any]] = []
        for row in round_rows:
            round_uuid = str(row.get("round_name", ""))
            mapped_round_rows.append(
                {
                    **row,
                    "round_name": (
                        voting_round.name
                        if (voting_round := config.rounds.get(round_uuid, None))
                        else round_uuid
                    ),
                }
            )
        st.dataframe(mapped_round_rows, width="stretch", hide_index=True)
    else:
        st.dataframe(round_rows, width="stretch", hide_index=True)

    st.subheader("圖表")
    _render_bar_chart(summary.counts, summary.modes)
    _render_pie_chart(summary.counts)
    if config is not None:
        _render_line_chart_by_round(records, config)
