from __future__ import annotations

import streamlit as st

from project import core
from project.types import StatisticsData, SummaryData, VoteRecord

from .config import CSV_FILE, DRINK_OPTIONS
from .shared import format_list, load_app_data, render_recent_votes
from .texts import (
    FORM_VOTE_ID,
    MODE_OPTIONS,
    PAGE_TITLE_VOTE,
    STATE_RESET,
    STATE_VOTE_CUSTOM_OPTION,
    STATE_VOTE_CUSTOM_ROUND_NAME,
    STATE_VOTE_MODE,
    STATE_VOTE_NAME,
    STATE_VOTE_OPTION,
    STATE_VOTE_ROUND_CHOICE,
)

SUCCESS_VOTE_ADDED_TEMPLATE = "已新增 {name} 的投票資料"


def render_vote_form() -> None:
    """顯示投票提交表單"""
    if st.session_state.get(STATE_RESET, False):
        st.session_state[STATE_VOTE_MODE] = core.ROUND_SINGLE
        st.session_state[STATE_VOTE_OPTION] = DRINK_OPTIONS[0]
        st.session_state[STATE_VOTE_ROUND_CHOICE] = core.ROUND_OPTIONS[0]
        st.session_state[STATE_VOTE_NAME] = ""
        st.session_state[STATE_VOTE_CUSTOM_OPTION] = ""
        st.session_state[STATE_VOTE_CUSTOM_ROUND_NAME] = ""
        st.session_state[STATE_RESET] = False

    st.subheader("新增投票")
    st.caption("輸入姓名、飲料與輪次，系統會自動寫入 CSV")
    mode = st.radio("模式", MODE_OPTIONS, horizontal=True, key=STATE_VOTE_MODE)
    selected_option = st.selectbox("飲料", DRINK_OPTIONS, key=STATE_VOTE_OPTION)
    if mode == core.MODE_MULTI:
        round_choice = st.selectbox(
            "輪次",
            core.ROUND_OPTIONS + [core.CUSTOM_ROUND_OPTION],
            key=STATE_VOTE_ROUND_CHOICE,
        )
    else:
        round_choice = core.ROUND_SINGLE

    with st.form(FORM_VOTE_ID, clear_on_submit=False):
        name = st.text_input("姓名", placeholder="例如：小明", key=STATE_VOTE_NAME)

        if selected_option == DRINK_OPTIONS[-1]:
            custom_option = st.text_input(
                "自訂飲料",
                placeholder="請輸入飲料名稱",
                key=STATE_VOTE_CUSTOM_OPTION,
            )
        else:
            custom_option = ""

        if mode == core.MODE_MULTI and round_choice == core.CUSTOM_ROUND_OPTION:
            round_name = st.text_input(
                "自訂輪次名稱",
                placeholder="例如：midterm",
                key=STATE_VOTE_CUSTOM_ROUND_NAME,
            )
            st.caption("自訂輪次只允許中文、英文、數字、-、_，且不能超過20字")
        elif mode == core.MODE_MULTI:
            round_name = round_choice
        else:
            round_name = core.ROUND_SINGLE

        submitted = st.form_submit_button("送出投票", width=True)

        if submitted:
            final_option = custom_option.strip() if selected_option == DRINK_OPTIONS[-1] else selected_option
            valid, msg = core.validate_vote_data(name, final_option)
            normalized_round = round_name.strip()

            if selected_option == DRINK_OPTIONS[-1] and not final_option:
                st.error("請輸入自訂飲料名稱")
            elif not valid:
                st.error(msg)
            elif mode == core.MODE_MULTI:
                round_valid, round_msg = core.validate_round_name(normalized_round)
                if not round_valid:
                    st.error(round_msg)
                else:
                    try:
                        core.add_vote(CSV_FILE, name, final_option, normalized_round)
                    except ValueError as exc:
                        st.error(str(exc))
                    else:
                        st.session_state[STATE_RESET] = True
                        st.success(SUCCESS_VOTE_ADDED_TEMPLATE.format(name=name))
                        st.rerun()
            else:
                try:
                    core.add_vote(CSV_FILE, name, final_option, core.ROUND_SINGLE)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.session_state[STATE_RESET] = True
                    st.success(SUCCESS_VOTE_ADDED_TEMPLATE.format(name=name))
                    st.rerun()


def render_vote_overview(records: list[VoteRecord], summary: SummaryData, stats: StatisticsData) -> None:
    """顯示即時投票概況"""
    st.subheader("即時概況")
    st.caption("即時呈現投票統計與最新資料變化")

    leader = format_list(summary.modes, "尚未產生")
    st.metric("目前眾數", leader, f"{summary.mode_count} 票")
    metric_cols = st.columns(3)
    metric_cols[0].metric("總票數", summary.total)
    metric_cols[1].metric("投票者", stats.unique_voters)
    metric_cols[2].metric("輪次", len(stats.rounds) or 1)

    st.markdown("#### 最近資料")
    if records:
        render_recent_votes(records)
    else:
        st.info("尚未建立任何投票資料。")


def render_vote_page(records: list[VoteRecord], summary: SummaryData, stats: StatisticsData) -> None:
    """顯示投票頁面"""
    st.title(PAGE_TITLE_VOTE)
    st.caption("請輸入投票資料並即時呈現統計結果")

    col1, col2 = st.columns([1, 1], gap="large")
    with col1:
        render_vote_form()
    with col2:
        render_vote_overview(records, summary, stats)


def render_vote_app() -> None:
    """顯示投票系統頁面"""
    records, summary, stats = load_app_data()
    render_vote_page(records, summary, stats)
