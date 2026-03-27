from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import streamlit as st

from .. import core

plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False

DATA_DIR = Path("data")
CSV_FILE = DATA_DIR / "votes.csv"
DRINK_OPTIONS = ["奶茶", "紅茶", "綠茶", "拿鐵", "烏龍茶"]

COLOR_PALETTE = {
    "奶茶": {"primary": "#C97A2B", "soft": "#F1D1AB"},
    "紅茶": {"primary": "#B64A4A", "soft": "#E9B0B0"},
    "綠茶": {"primary": "#2F8F6B", "soft": "#B7DEC9"},
    "拿鐵": {"primary": "#7B5C99", "soft": "#D5C3E7"},
    "烏龍茶": {"primary": "#2D7F91", "soft": "#B6DCE5"},
}


def init_app() -> None:
    """初始化應用。"""
    DATA_DIR.mkdir(exist_ok=True)
    core.ensure_csv(CSV_FILE)


def clear_all_data() -> None:
    """清空所有資料。"""
    if CSV_FILE.exists():
        CSV_FILE.unlink()
    core.ensure_csv(CSV_FILE)


def apply_theme() -> None:
    """設定簡潔、專業的淺色主題。"""
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
        </style>
        """,
        unsafe_allow_html=True,
    )


def format_list(items: list[str], empty: str = "無") -> str:
    """Format a string list for display."""
    return "、".join(items) if items else empty


def build_count_rows(summary: dict[str, object]) -> list[dict[str, object]]:
    """Build option rows sorted by vote count."""
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


def configure_page(page_title: str) -> None:
    """Configure shared Streamlit page settings."""
    st.set_page_config(
        page_title=page_title,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def load_app_data() -> tuple[list[core.VoteRecord], dict[str, object], dict[str, object]]:
    """Load and prepare shared data for each page."""
    apply_theme()
    init_app()
    records = core.read_votes(CSV_FILE)
    summary = core.build_summary(records)
    stats = core.get_statistics(CSV_FILE)
    render_sidebar(stats)
    return records, summary, stats


def render_sidebar(stats: dict[str, object]) -> None:
    """Render the shared sidebar controls."""
    with st.sidebar:
        st.markdown("### 投票管理")
        st.caption("資料會寫入 `data/votes.csv`，送出後立即更新報表。")
        st.markdown(
            f"""
            <div class="summary-line">總票數：{stats["total"]}</div>
            <div class="summary-line">投票者：{stats["unique_voters"]}</div>
            <div class="summary-line">輪次：{len(stats["rounds"]) or 1}</div>
            """,
            unsafe_allow_html=True,
        )
        st.divider()
        if st.button("清空所有資料", use_container_width=True):
            clear_all_data()
            st.rerun()


def render_empty_report() -> None:
    """Empty state for both tabs."""
    st.info("目前尚無投票資料，請先到「投票系統」頁面新增資料。")


def render_vote_form() -> None:
    """Render the vote submission form."""
    st.subheader("新增投票")
    st.caption("輸入姓名、飲料與輪次，系統會自動寫入 CSV。")
    with st.form("vote_form", clear_on_submit=False):
        mode = st.radio("模式", ["單輪", "多輪"], horizontal=True)
        name = st.text_input("姓名", placeholder="例如：小明")
        option = st.selectbox("飲料", DRINK_OPTIONS)
        round_name = st.text_input("輪次", value="day1") if mode == "多輪" else "day1"
        submitted = st.form_submit_button("送出投票", use_container_width=True)

        if submitted:
            valid, msg = core.validate_vote_data(name, option)
            if not valid:
                st.error(msg)
            else:
                core.add_vote(CSV_FILE, name, option, round_name or "day1")
                st.success(f"已新增 {name} 的投票資料。")
                st.rerun()


def render_recent_votes(records: list[core.VoteRecord]) -> None:
    """Render the latest vote records."""
    recent = list(reversed(records[-8:]))
    rows = [{"輪次": r.round, "姓名": r.name, "飲料": r.option} for r in recent]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_vote_overview(records: list[core.VoteRecord], summary: dict[str, object], stats: dict[str, object]) -> None:
    """Render live vote overview content."""
    st.subheader("即時概況")
    st.caption("保留必要資訊，讓輸入與檢視更聚焦。")
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
    """Render the vote page."""
    st.title("投票系統")
    st.caption("專注輸入與即時確認，將操作流程簡化為一個主要表單。")

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        render_vote_form()
    with col2:
        render_vote_overview(records, summary, stats)


def render_summary_metrics(summary: dict[str, object], stats: dict[str, object]) -> None:
    """Render report metrics."""
    modes = format_list(summary["modes"])
    least = format_list(summary["least"])
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("總票數", summary["total"])
    col2.metric("投票者", stats["unique_voters"])
    col3.metric("眾數", modes, f"{summary['mode_count']} 票")
    col4.metric("最少票", least, f"{summary['least_count']} 票")


def render_bar_chart(summary: dict[str, object]) -> None:
    """Render a concise vote distribution chart."""
    counts = summary["counts"]
    if not counts:
        st.info("目前沒有可顯示的圖表資料。")
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
    ax.set_ylabel("票數", fontsize=10, color="#5B6578", labelpad=10)
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
    """Render multi-round comparison."""
    if len(stats["rounds"]) <= 1:
        st.info("目前只有單一輪次，新增多輪資料後會在這裡顯示比較結果。")
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


def render_data_table(records: list[core.VoteRecord]) -> None:
    """Render the full data table."""
    rows = [{"輪次": r.round, "姓名": r.name, "飲料": r.option} for r in records]
    st.dataframe(rows, use_container_width=True, hide_index=True)


def render_report_page(records: list[core.VoteRecord], summary: dict[str, object], stats: dict[str, object]) -> None:
    """Render the report page."""
    st.title("資料報告")
    st.caption("保留關鍵統計、圖表與輪次比較，方便快速報告與展示。")

    if not records:
        render_empty_report()
        return

    render_summary_metrics(summary, stats)
    st.divider()

    chart_col, table_col = st.columns([1.4, 1], gap="large")
    with chart_col:
        st.subheader("投票分布圖")
        st.caption("依票數高低排序，眾數會以較深色標示。")
        render_bar_chart(summary)

    with table_col:
        st.subheader("票數摘要")
        st.caption("各飲料票數與占比。")
        st.dataframe(build_count_rows(summary), use_container_width=True, hide_index=True)

    st.divider()
    left_col, right_col = st.columns([1, 1], gap="large")
    with left_col:
        st.subheader("輪次比較")
        st.caption("多輪模式下可快速比對每輪眾數。")
        render_round_report(stats)

    with right_col:
        st.subheader("資料明細")
        st.caption("完整投票紀錄，適合課堂展示或核對。")
        render_data_table(records)


def render_vote_app() -> None:
    """Render the vote system page."""
    records, summary, stats = load_app_data()
    render_vote_page(records, summary, stats)


def render_report_app() -> None:
    """Render the report page."""
    records, summary, stats = load_app_data()
    render_report_page(records, summary, stats)
