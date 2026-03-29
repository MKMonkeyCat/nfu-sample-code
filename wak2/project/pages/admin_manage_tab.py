from __future__ import annotations

import streamlit as st

from project.core import VoteCoreService
from project.core.storage import VoteConfig
from project.pages.admin_shared import build_vote_rows, delete_selected_votes, save_vote_table_changes
from project.utils.streamlit_table import extract_editor_rows
from project.utils.streamlit_ui import render_callout, render_empty_state


def render_manage_tab(service: VoteCoreService, configs: list[tuple[str, VoteConfig]]) -> None:
    if not configs:
        render_empty_state("目前尚未建立任何投票", hint="先到上方的「建立投票」分頁新增一筆")
        return

    render_callout(
        "管理方式",
        [
            "主題與選項可直接在表格中編輯",
            "投票時間由『輪次設定』決定（請到輪次頁調整）",
            "選項欄支援使用 、 或 , 分隔",
            "勾選左側核取方塊後，可一次刪除多筆投票",
        ],
    )

    raw_rows = build_vote_rows(configs)

    edited_rows = st.data_editor(
        raw_rows,
        key="admin_vote_table_editor",
        width="stretch",
        hide_index=True,
        column_config={
            "uuid": st.column_config.TextColumn("投票編號 (ID)", disabled=True),
            "file": None,
            "selected": st.column_config.CheckboxColumn(""),
            "topic": st.column_config.TextColumn("主題", required=True),
            "options": st.column_config.TextColumn("選項"),
            "start_time": st.column_config.DatetimeColumn("開始時間"),
            "end_time": st.column_config.DatetimeColumn("結束時間"),
            "vote_url": st.column_config.TextColumn("投票連結"),
        }
    )


    rows = extract_editor_rows(edited_rows)
    
    raw_map = {r["uuid"]: r for r in raw_rows}

    final_rows = []
    for r in rows:
        uid = r.get("uuid")
        if uid in raw_map:
            final_rows.append({**raw_map[uid], **r})


    action_col, danger_col = st.columns([1, 1])
    with action_col:
        if st.button("儲存投票變更", type="primary", width="stretch"):
            save_vote_table_changes(service, final_rows)
    with danger_col:
        selected_count = sum(1 for row in rows if bool(row.get("selected", False)))
        if st.button("刪除勾選投票", type="secondary", width="stretch", disabled=selected_count == 0):
            delete_selected_votes(service, final_rows)
