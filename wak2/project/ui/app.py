from __future__ import annotations

import html
from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st
from matplotlib.ticker import MaxNLocator

from .. import core

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False

DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "votes.csv"
DRINK_OPTIONS = ["奶茶", "紅茶", "綠茶", "拿鐵", "烏龍茶", "其他"]

COLOR_PALETTE = {
    "奶茶": {"primary": "#C97A2B", "soft": "#F1D1AB"},
    "紅茶": {"primary": "#B64A4A", "soft": "#E9B0B0"},
    "綠茶": {"primary": "#2F8F6B", "soft": "#B7DEC9"},
    "拿鐵": {"primary": "#7B5C99", "soft": "#D5C3E7"},
    "烏龍茶": {"primary": "#2D7F91", "soft": "#B6DCE5"},
}


def init_app() -> None:
    """初始化應用"""
    DATA_DIR.mkdir(exist_ok=True)
    core.ensure_csv(CSV_FILE)


def apply_theme() -> None:
    """設定主題"""
    st.markdown(
        """
        <style>
        :root {
            --bg: #F5F7FB;
            --surface: rgba(255, 255, 255, 0.88);
            --surface-strong: #FFFFFF;
            --text: #162033;
            --muted: #5B6578;
            --accent: #1F6FEB;
            --accent-soft: #EAF2FF;
            --border: rgba(22, 32, 51, 0.10);
            --danger: #D14343;
        }
        * {
            font-family: "Microsoft JhengHei", sans-serif;
        }
        .stApp {
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(31, 111, 235, 0.10), transparent 26%),
                linear-gradient(180deg, #F9FBFF 0%, #F3F6FB 100%);
        }
        [data-testid="stHeader"] {
            background: transparent;
        }
        [data-testid="stSidebar"] > div:first-child {
            background: linear-gradient(180deg, #F8FAFD 0%, #EEF3F9 100%);
            border-right: 1px solid var(--border);
        }
        [data-testid="stMetric"] {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px 16px;
        }
        [data-testid="stMetricLabel"] {
            color: var(--muted);
        }
        [data-testid="stMetricValue"] {
            color: var(--text);
        }
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 12px;
            border: none;
            background: linear-gradient(135deg, #1F6FEB 0%, #3286F5 100%);
            color: white;
            font-weight: 600;
            min-height: 42px;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            filter: brightness(1.03);
        }
        [data-testid="stSidebar"] .stButton > button {
            background: white;
            color: var(--danger);
            border: 1px solid rgba(209, 67, 67, 0.20);
        }
        [data-baseweb="input"] input,
        [data-baseweb="select"] > div,
        .stTextInput input {
            background: rgba(255, 255, 255, 0.96) !important;
            color: var(--text) !important;
            border: 1px solid var(--border) !important;
            border-radius: 12px !important;
        }
        .summary-line {
            color: var(--muted);
            font-size: 0.95rem;
            margin-bottom: 0.4rem;
        }
        .metric-hover-card {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 14px 16px;
            min-height: 96px;
        }
        .metric-hover-label {
            color: var(--muted);
            font-size: 0.95rem;
            margin-bottom: 0.35rem;
        }
        .metric-hover-value {
            color: var(--text);
            font-size: 1.55rem;
            font-weight: 700;
            line-height: 1.2;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .metric-hover-delta {
            color: var(--muted);
            font-size: 0.9rem;
            margin-top: 0.35rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_list(items: list[str], empty: str = "無") -> str:
    """將字串列表格式化以便顯示"""
    return "、".join(items) if items else empty


def build_count_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    """依照票數排序，建立選項列"""
    counts = summary["counts"]
    total = summary["total"] or 1
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return [
        {
            "飲料": option,
            "票數": vote,
            "占比": f"{vote / total:.0%}",
        }
        for option, vote in sorted_items
    ]


def build_delete_options(records: list[core.VoteRecord]) -> list[tuple[str, int]]:
    """在側邊欄建立可選擇的刪除選項"""
    options: list[tuple[str, int]] = []
    sorted_indices = sorted(range(len(records)), key=lambda index: (core.get_round_sort_key(records[index].round), records[index].name, records[index].option))
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


def configure_page(page_title: str) -> None:
    """設定共用的 Streamlit 頁面設定"""
    st.set_page_config(
        page_title=page_title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_app_data() -> tuple[list[core.VoteRecord], dict[str, object], dict[str, object]]:
    """載入並初始化各頁共用資料"""
    apply_theme()
    init_app()
    records = core.read_votes(CSV_FILE)
    summary = core.build_summary(records)
    stats = core.get_statistics(CSV_FILE)
    render_sidebar(stats, records)
    return records, summary, stats


def render_sidebar(stats: dict[str, object], records: list[core.VoteRecord]) -> None:
    """顯示共用的側邊欄控制元件"""
    with st.sidebar:
        st.markdown("### 投票管理")
        st.caption("資料會寫入 `data/votes.csv`，送出後立即更新報表內容")
        st.markdown(
            f"""
            <div class="summary-line">總票數：{stats["total"]}</div>
            <div class="summary-line">投票者：{stats["unique_voters"]}</div>
            <div class="summary-line">輪次：{len(stats["rounds"]) or 1}</div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        st.markdown("### 資料清理")
        st.caption("刪除後的資料不可復原")

        delete_options = build_delete_options(records)
        labels = [label for label, _ in delete_options]
        index_map = {label: index for label, index in delete_options}

        with st.form("delete_votes_form", clear_on_submit=True):
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


def render_vote_form() -> None:
    """顯示投票提交表單"""
    if st.session_state.get("reset_vote_form", False):
        st.session_state["vote_mode"] = "單輪"
        st.session_state["vote_option"] = DRINK_OPTIONS[0]
        st.session_state["vote_round_choice"] = core.ROUND_OPTIONS[0]
        st.session_state["vote_name"] = ""
        st.session_state["vote_custom_option"] = ""
        st.session_state["vote_custom_round_name"] = ""
        st.session_state["reset_vote_form"] = False

    st.subheader("新增投票")
    st.caption("輸入姓名、飲料與輪次，系統會自動寫入 CSV")
    mode = st.radio("模式", ["單輪", "多輪"], horizontal=True, key="vote_mode")
    selected_option = st.selectbox("飲料", DRINK_OPTIONS, key="vote_option")
    if mode == "多輪":
        round_choice = st.selectbox("輪次", core.ROUND_OPTIONS + [core.CUSTOM_ROUND_OPTION], key="vote_round_choice")
    else:
        round_choice = "單輪"

    with st.form("vote_form", clear_on_submit=False):
        name = st.text_input("姓名", placeholder="例如：小明", key="vote_name")

        if selected_option == "其他":
            custom_option = st.text_input("自訂飲料", placeholder="請輸入飲料名稱", key="vote_custom_option")
        else:
            custom_option = ""

        if mode == "多輪" and round_choice == core.CUSTOM_ROUND_OPTION:
            round_name = st.text_input("自訂輪次名稱", placeholder="例如：midterm", key="vote_custom_round_name")
            st.caption("自訂輪次只允許中文、英文、數字、-、_，且不能超過20字")
        elif mode == "多輪":
            round_name = round_choice
        else:
            round_name = "單輪"

        submitted = st.form_submit_button("送出投票", use_container_width=True)

        if submitted:
            final_option = custom_option.strip() if selected_option == "其他" else selected_option
            valid, msg = core.validate_vote_data(name, final_option)
            normalized_round = round_name.strip()

            if selected_option == "其他" and not final_option:
                st.error("請輸入自訂飲料名稱")
            elif not valid:
                st.error(msg)
            elif mode == "多輪":
                round_valid, round_msg = core.validate_round_name(normalized_round)
                if not round_valid:
                    st.error(round_msg)
                else:
                    try:
                        core.add_vote(CSV_FILE, name, final_option, normalized_round)
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state["reset_vote_form"] = True
                        st.success(f"已新增 {name} 的投票資料")
                        st.rerun()
            else:
                try:
                    core.add_vote(CSV_FILE, name, final_option, "單輪")
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.session_state["reset_vote_form"] = True
                    st.success(f"已新增 {name} 的投票資料")
                    st.rerun()


def render_recent_votes(records: list[core.VoteRecord]) -> None:
    """顯示最新的投票紀錄"""
    recent = list(reversed(records[-8:]))
    rows = [{"輪次": r.round, "姓名": r.name, "飲料": r.option} for r in recent]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_vote_overview(records: list[core.VoteRecord], summary: dict[str, object], stats: dict[str, object]) -> None:
    """顯示即時投票概況"""
    st.subheader("即時概況")
    st.caption("即時呈現投票統計與最新資料變化")

    leader = format_list(summary["modes"], "尚未產生")
    st.metric("目前眾數", leader, f"{summary['mode_count']} 票")
    metric_cols = st.columns(3)
    metric_cols[0].metric("總票數", summary["total"])
    metric_cols[1].metric("投票者", stats["unique_voters"])
    metric_cols[2].metric("輪次", len(stats["rounds"]) or 1)

    st.markdown("#### 最近資料")
    if records:
        render_recent_votes(records)
    else:
        st.info("尚未建立任何投票資料。")


def render_vote_page(records: list[core.VoteRecord], summary: dict[str, object], stats: dict[str, object]) -> None:
    """顯示投票頁面"""
    st.title("投票系統")
    st.caption("快輸入投票資料並即時呈現統計結果")

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        render_vote_form()
    with col2:
        render_vote_overview(records, summary, stats)


def render_summary_metrics(summary: dict[str, object], stats: dict[str, object]) -> None:
    """顯示報表指標"""
    modes = format_list(summary["modes"])
    least = format_list(summary["least"])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總票數", summary["total"])
    col2.metric("投票者", stats["unique_voters"])
    with col3:
        render_hover_metric("眾數", modes, f"{summary['mode_count']} 票", f"完整眾數品項：{modes}")
    with col4:
        render_hover_metric("最少票", least, f"{summary['least_count']} 票", f"完整最少票品項：{least}")


def render_bar_chart(summary: dict[str, object]) -> None:
    """建立精簡投票比例圖"""
    counts = summary["counts"]
    if not counts:
        st.info("目前沒有可顯示的圖表資料")
        return

    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    options = [item[0] for item in sorted_items]
    votes = [item[1] for item in sorted_items]
    modes = set(summary["modes"])

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
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_round_report(stats: dict[str, object]) -> None:
    """顯示多輪比較結果"""
    if len(stats["rounds"]) <= 1:
        st.info("目前只有單一輪次，新增多輪資料後會在這裡顯示比較結果")
        return

    comparison = core.compare_rounds(CSV_FILE)
    rows = []
    for round_name, round_summary in comparison.items():
        rows.append(
            {
                "輪次": round_name,
                "票數": round_summary["total"],
                "眾數": format_list(round_summary["modes"]),
            }
        )

    st.dataframe(rows, use_container_width=True, hide_index=True)

    changes = core.get_mode_changes(CSV_FILE)
    if changes:
        st.caption("變化摘要：" + "；".join(changes))


def render_round_grouped_bar_chart(stats: dict[str, object]) -> None:
    """顯示多輪投票趨勢的分組長條圖"""
    rounds = [round_name for round_name in stats["rounds"] if round_name != "單輪"]
    if len(rounds) <= 1:
        st.info("目前輪次不足，至少需要兩個多輪資料才能顯示多輪比較圖")
        return

    comparison = core.compare_rounds(CSV_FILE)
    option_names = sorted(
        {
            option
            for round_summary in comparison.values()
            for option in round_summary["counts"].keys()
        }
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
            option
            for option in option_names
            if comparison[round_name]["counts"].get(option, 0) > 0
        ]
        if not active_options:
            continue

        bar_width = group_width / len(active_options)
        for option_index, option in enumerate(active_options):
            vote_count = comparison[round_name]["counts"].get(option, 0)
            max_vote = max(max_vote, vote_count)
            palette = COLOR_PALETTE.get(option, {"primary": "#5F6B7A"})
            x_position = (
                group_position
                - (group_width / 2)
                + (bar_width / 2)
                + option_index * bar_width
            )
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
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def render_data_table(records: list[core.VoteRecord]) -> None:
    """顯示完整資料表"""
    sorted_records = core.sort_records(records)
    rows = [{"輪次": r.round, "姓名": r.name, "飲料": r.option} for r in sorted_records]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_report_page(records: list[core.VoteRecord], summary: dict[str, object], stats: dict[str, object]) -> None:
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
        st.dataframe(build_count_rows(summary), use_container_width=True, hide_index=True)

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


def render_vote_app() -> None:
    """顯示投票系統頁面"""
    records, summary, stats = load_app_data()
    render_vote_page(records, summary, stats)


def render_report_app() -> None:
    """顯示報表頁面"""
    records, summary, stats = load_app_data()
    render_report_page(records, summary, stats)
