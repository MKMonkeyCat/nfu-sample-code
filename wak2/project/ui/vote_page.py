from __future__ import annotations

import streamlit as st

from project import core
from project.types import StatisticsData, SummaryData, VoteRecord

from . import texts
from .config import CSV_FILE, DRINK_OPTIONS
from .shared import format_list, load_app_data, render_recent_votes

SUCCESS_VOTE_ADDED_TEMPLATE = "已新增 {name} 的投票資料"


def render_vote_form() -> None:
    """顯示投票提交表單"""
    if st.session_state.get(texts.STATE_RESET, False):
        st.session_state[texts.STATE_VOTE_MODE] = core.ROUND_SINGLE
        st.session_state[texts.STATE_VOTE_OPTION] = DRINK_OPTIONS[0]
        st.session_state[texts.STATE_VOTE_ROUND_CHOICE] = core.ROUND_OPTIONS[0]
        st.session_state[texts.STATE_VOTE_NAME] = ""
        st.session_state[texts.STATE_VOTE_CUSTOM_OPTION] = ""
        st.session_state[texts.STATE_VOTE_CUSTOM_ROUND_NAME] = ""
        st.session_state[texts.STATE_RESET] = False

    st.subheader("新增投票")
    st.caption("輸入姓名、飲料與輪次，系統會自動寫入 CSV")
    mode = st.radio("模式", texts.MODE_OPTIONS, horizontal=True, key=texts.STATE_VOTE_MODE)
    selected_option = st.selectbox("飲料", DRINK_OPTIONS, key=texts.STATE_VOTE_OPTION)
    if mode == core.MODE_MULTI:
        round_choice = st.selectbox(
            "輪次",
            core.ROUND_OPTIONS + [core.CUSTOM_ROUND_OPTION],
            key=texts.STATE_VOTE_ROUND_CHOICE,
        )
    else:
        round_choice = core.ROUND_SINGLE

    with st.form(texts.FORM_VOTE_ID, clear_on_submit=False):
        name = st.text_input("姓名", placeholder="例如：小明", key=texts.STATE_VOTE_NAME)

        if selected_option == DRINK_OPTIONS[-1]:
            custom_option = st.text_input(
                "自訂飲料",
                placeholder="請輸入飲料名稱",
                key=texts.STATE_VOTE_CUSTOM_OPTION,
            )
        else:
            custom_option = ""

        if mode == core.MODE_MULTI and round_choice == core.CUSTOM_ROUND_OPTION:
            round_name = st.text_input(
                "自訂輪次名稱",
                placeholder="例如：midterm",
                key=texts.STATE_VOTE_CUSTOM_ROUND_NAME,
            )
            st.caption("自訂輪次只允許中文、英文、數字、-、_，且不能超過20字")
        elif mode == core.MODE_MULTI:
            round_name = round_choice
        else:
            round_name = core.ROUND_SINGLE

        submitted = st.form_submit_button("送出投票", width="stretch")

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
                        st.session_state[texts.STATE_RESET] = True
                        st.success(SUCCESS_VOTE_ADDED_TEMPLATE.format(name=name))
                        st.rerun()
            else:
                try:
                    core.add_vote(CSV_FILE, name, final_option, core.ROUND_SINGLE)
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.session_state[texts.STATE_RESET] = True
                    st.success(SUCCESS_VOTE_ADDED_TEMPLATE.format(name=name))
                    st.rerun()


def render_vote_overview(records: list[VoteRecord], summary: SummaryData, stats: StatisticsData) -> None:
    """顯示即時投票概況"""
    st.subheader(texts.SUBHEADER_VOTE_OVERVIEW)
    st.caption(texts.CAPTION_VOTE_OVERVIEW)

    leader = format_list(summary.modes, texts.LEADER_EMPTY_PLACEHOLDER)
    st.metric(texts.METRIC_MODE_NOW, leader, f"{summary.mode_count} 票")
    metric_cols = st.columns(3)
    metric_cols[0].metric(texts.METRIC_TOTAL_VOTES, summary.total)
    metric_cols[1].metric(texts.METRIC_VOTERS, stats.unique_voters)
    metric_cols[2].metric(texts.METRIC_ROUNDS, len(stats.rounds) or 1)

    st.markdown(texts.SECTION_RECENT_DATA)
    if records:
        render_recent_votes(records)
    else:
        st.info(texts.INFO_NO_VOTE_DATA)


def render_vote_page() -> None:
    """顯示投票頁面"""
    st.title(texts.PAGE_TITLE_VOTE)
    st.caption(texts.CAPTION_VOTE_PAGE)
    render_vote_form()


def render_vote_app() -> None:
    """顯示投票系統頁面"""
    load_app_data()
    render_vote_page()
