from __future__ import annotations

import streamlit as st

from project.core import VoteCoreService
from project.pages.admin_shared import (
    DEFAULT_QUICK_OPTIONS,
    STATE_NEW_OPTION,
    STATE_OPTIONS,
    STATE_PENDING_RESET,
    STATE_VOTE_NAME,
    add_option_from_input,
    append_options,
    clear_options,
    count_manual_options,
)
from project.utils.streamlit_table import extract_editor_column_values
from project.utils.streamlit_ui import render_callout, render_empty_state
from project.utils.text_normalize import normalize_option_list


def render_create_tab(service: VoteCoreService) -> None:
    topic = str(st.session_state.get(STATE_VOTE_NAME, "")).strip()
    current_options = list(st.session_state.get(STATE_OPTIONS, []))
    manual_option_count = count_manual_options(current_options)
    can_submit = bool(topic) and len(current_options) >= 2 and manual_option_count >= 2

    control_col, preview_col = st.columns([2, 1])
    with control_col:
        st.subheader("建立投票")
        st.text_input("投票主題", placeholder="例如：最喜歡的飲料", key=STATE_VOTE_NAME)

        input_col, button_col = st.columns([3, 1], vertical_alignment="bottom")
        with input_col:
            st.text_input("新增選項", placeholder="輸入後按右邊加入", key=STATE_NEW_OPTION)
        with button_col:
            st.button("加入", width="stretch", on_click=add_option_from_input)

        quick_col, clear_col = st.columns([1, 1])
        with quick_col:
            if st.button("快速填入選項", width="stretch", disabled=not topic):
                appended = append_options(DEFAULT_QUICK_OPTIONS)
                if appended:
                    st.success(f"已加入 {appended} 個建議選項")
                else:
                    st.info("建議選項都已存在")
                st.rerun()
        with clear_col:
            st.button("清空選項", width="stretch", on_click=clear_options, disabled=not current_options)

    with preview_col:
        render_callout(
            "建立前檢查",
            [
                f"目前主題：{topic or '尚未填寫'}",
                f"選項數量：{len(current_options)}",
                f"手動填寫：{manual_option_count}",
                "至少需要 2 個手動填寫的選項",
            ],
        )

    st.caption("目前選項")
    if not current_options:
        render_empty_state("尚未加入任何選項", hint="先輸入選項，或用快速填入建立初稿")
    else:
        edited_rows = st.data_editor(
            [{"選項": option} for option in current_options],
            key="admin_option_editor",
            hide_index=True,
            width="stretch",
            num_rows="dynamic",
            column_config={
                "選項": st.column_config.TextColumn(
                    "選項",
                    help="雙擊後可直接修改，也可新增或刪除列",
                    required=True,
                )
            },
        )
        current_options = normalize_option_list(extract_editor_column_values(edited_rows, "選項"))
        manual_option_count = count_manual_options(current_options)
        can_submit = bool(topic) and len(current_options) >= 2 and manual_option_count >= 2

    st.caption(
        f"已加入 {len(current_options)} 個選項，其中手動填寫 {manual_option_count} 個；至少需要 2 個手動填寫的選項"
    )
    if st.button("建立投票", type="primary", disabled=not can_submit):
        vote_uuid = service.storage.create_vote(topic, set(current_options))
        st.session_state[STATE_OPTIONS] = current_options
        st.success(f"已建立投票：{topic}（ID: {vote_uuid[:8]}）")
        st.code(f"/vote?uuid={vote_uuid}", language="text")
        st.session_state[STATE_PENDING_RESET] = True
        st.rerun()
