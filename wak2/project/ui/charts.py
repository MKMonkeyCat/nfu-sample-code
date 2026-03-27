from __future__ import annotations

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import MaxNLocator

from project import core
from project.types import StatisticsData, SummaryData

from .config import COLOR_PALETTE, CSV_FILE

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False


def render_bar_chart(summary: SummaryData) -> None:
    """建立精簡投票比例圖"""
    counts = summary.counts
    if not counts:
        st.info("目前沒有可顯示的圖表資料")
        return

    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    options = [item[0] for item in sorted_items]
    votes = [item[1] for item in sorted_items]
    modes = set(summary.modes)

    colors = []
    for option in options:
        palette = COLOR_PALETTE.get(option, {"primary": "#5F6B7A", "soft": "#D9E0E8"})
        colors.append(palette["primary"] if option in modes else palette["soft"])

    fig, ax = plt.subplots(figsize=(10, 4.8))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    bars = ax.bar(options, votes, color=colors, edgecolor="#D7DDE8", linewidth=1.0, width=0.58)
    ax.set_title("投票分布", fontsize=13, fontweight="bold", color="#162033", pad=14)
    ax.set_xlabel("飲料品項", fontsize=10, color="#5B6578", labelpad=10)
    ax.set_ylabel("票\n數", fontsize=10, color="#5B6578", labelpad=0, rotation=0)
    ax.yaxis.label.set_horizontalalignment("center")
    ax.yaxis.label.set_verticalalignment("center")
    ax.yaxis.set_label_coords(-0.05, 0.5)
    ax.tick_params(colors="#364152", labelsize=10)
    ax.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.35, color="#CFD7E4")
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color("#D7DDE8")

    for bar, vote in zip(bars, votes):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            vote + 0.05,
            str(vote),
            ha="center",
            va="bottom",
            fontsize=10,
            color="#162033",
        )

    ax.margins(y=0.14)
    st.pyplot(fig, width="stretch")
    plt.close(fig)


def render_round_grouped_bar_chart(stats: StatisticsData) -> None:
    """顯示多輪投票趨勢的分組長條圖"""
    rounds = [round_name for round_name in stats.rounds if round_name != core.ROUND_SINGLE]

    if len(rounds) <= 1:
        st.info("目前輪次不足，至少需要兩個多輪資料才能顯示多輪比較圖")
        return

    comparison = core.compare_rounds(CSV_FILE)
    option_names = sorted(
        {option for round_summary in comparison.values() for option in round_summary.counts.keys()}
    )
    if not option_names:
        st.info("目前沒有可顯示的多輪資料")
        return

    fig, ax = plt.subplots(figsize=(10, 5.2))
    fig.patch.set_facecolor("#FFFFFF")
    ax.set_facecolor("#FFFFFF")

    group_positions = list(range(len(rounds)))
    group_width = 0.78
    max_vote = 0
    shown_labels: set[str] = set()

    for group_position, round_name in zip(group_positions, rounds):
        active_options = [
            option for option in option_names if comparison[round_name].counts.get(option, 0) > 0
        ]
        if not active_options:
            continue

        bar_width = group_width / len(active_options)
        for option_index, option in enumerate(active_options):
            vote_count = comparison[round_name].counts.get(option, 0)
            max_vote = max(max_vote, vote_count)
            palette = COLOR_PALETTE.get(option, {"primary": "#5F6B7A"})
            x_position = group_position - (group_width / 2) + (bar_width / 2) + option_index * bar_width
            label = option if option not in shown_labels else None
            ax.bar(
                x_position,
                vote_count,
                width=bar_width,
                color=palette["primary"],
                label=label,
            )
            shown_labels.add(option)
            ax.text(
                x_position,
                vote_count + 0.03,
                str(vote_count),
                ha="center",
                va="bottom",
                fontsize=9,
                color="#162033",
            )

    ax.set_title("多輪票數比較", fontsize=13, fontweight="bold", color="#162033", pad=14)
    ax.set_xlabel("輪次", fontsize=10, color="#5B6578", labelpad=10)
    ax.set_ylabel("")
    ax.text(
        -0.05,
        0.5,
        "票\n數",
        transform=ax.transAxes,
        ha="center",
        va="center",
        fontsize=10,
        color="#5B6578",
    )
    ax.set_xticks(group_positions)
    ax.set_xticklabels(rounds)
    ax.set_xlim(-0.5, len(rounds) - 0.5)
    ax.set_ylim(0, max_vote + 0.6)
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.tick_params(colors="#364152", labelsize=10)
    ax.grid(axis="y", linestyle="--", linewidth=0.8, alpha=0.35, color="#CFD7E4")
    ax.set_axisbelow(True)

    for spine in ax.spines.values():
        spine.set_color("#D7DDE8")

    handles, labels = ax.get_legend_handles_labels()
    if handles:
        fig.legend(
            handles,
            labels,
            frameon=False,
            loc="lower right",
            bbox_to_anchor=(0.98, 0.03),
            bbox_transform=fig.transFigure,
        )
    fig.subplots_adjust(right=0.84, bottom=0.16)
    st.pyplot(fig, width="stretch")
    plt.close(fig)
