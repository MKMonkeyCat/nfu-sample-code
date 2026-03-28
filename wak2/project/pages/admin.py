from __future__ import annotations

from typing import Any
from uuid import uuid4

import streamlit as st

from project.core import VoteCoreService
from project.core.storage import VoteRoundConfig
from project.utils.datetime import parse_optional_iso_datetime, to_iso_datetime_text
from project.utils.streamlit_table import (
    extract_editor_column_values,
    extract_editor_rows,
)
from project.utils.text_normalize import (
    normalize_option_list,
    normalize_option_text,
    parse_options_text,
)

STATE_OPTIONS = "admin_draft_options"
STATE_NEW_OPTION = "admin_new_option"
STATE_VOTE_NAME = "admin_vote_name"
STATE_PENDING_RESET = "admin_pending_reset"


def _init_state() -> None:
    if STATE_OPTIONS not in st.session_state:
        st.session_state[STATE_OPTIONS] = []
    if STATE_NEW_OPTION not in st.session_state:
        st.session_state[STATE_NEW_OPTION] = ""
    if STATE_VOTE_NAME not in st.session_state:
        st.session_state[STATE_VOTE_NAME] = ""
    if STATE_PENDING_RESET not in st.session_state:
        st.session_state[STATE_PENDING_RESET] = False


def _apply_pending_reset() -> None:
    if not bool(st.session_state.get(STATE_PENDING_RESET, False)):
        return

    # Reset before widgets are instantiated in this run.
    st.session_state[STATE_OPTIONS] = []
    st.session_state[STATE_NEW_OPTION] = ""
    st.session_state[STATE_VOTE_NAME] = ""
    st.session_state[STATE_PENDING_RESET] = False


def _add_option_from_input() -> None:
    option = normalize_option_text(st.session_state.get(STATE_NEW_OPTION, ""))
    if not option:
        return

    current: list[str] = st.session_state[STATE_OPTIONS]
    if option in current:
        st.warning(f"選項「{option}」已存在")
        return

    current.append(option)
    st.session_state[STATE_NEW_OPTION] = ""


def _clear_options() -> None:
    st.session_state[STATE_OPTIONS] = []


def _normalize_round_uuid(value: Any) -> str:
    if value is None:
        return ""

    text = str(value).strip()
    if not text:
        return ""

    # Streamlit data_editor may return None-like strings for new rows.
    if text.lower() in {"none", "null", "nan"}:
        return ""

    return text


def render(service: VoteCoreService) -> None:
    _init_state()
    _apply_pending_reset()

    st.header("管理頁：建立或刪除投票")
    st.caption("建立投票主題與選項，投票紀錄會寫入 CSV。")

    st.subheader("建立新投票")
    st.text_input("投票主題", placeholder="例如：最喜歡飲料票選", key=STATE_VOTE_NAME)

    add_col, button_col = st.columns([3, 1], vertical_alignment="bottom")
    with add_col:
        st.text_input("新增選項", placeholder="輸入一個選項後點右側按鈕", key=STATE_NEW_OPTION)
    with button_col:
        st.button("加入", width="stretch", on_click=_add_option_from_input)

    quick_add_col1, quick_add_col2 = st.columns([1, 1])
    with quick_add_col1:
        if st.button("從主題常見值快速填入", width="stretch"):
            raw_name = st.session_state.get(STATE_VOTE_NAME, "")
            defaults: list[str]
            if "飲料" in raw_name:
                defaults = ["奶茶", "紅茶", "綠茶"]
            elif "午餐" in raw_name:
                defaults = ["便當", "麵", "水餃"]
            elif "顏色" in raw_name:
                defaults = ["紅色", "藍色", "綠色"]
            else:
                defaults = ["選項 A", "選項 B", "選項 C"]

            current: list[str] = st.session_state[STATE_OPTIONS]
            for item in defaults:
                if item not in current:
                    current.append(item)

    with quick_add_col2:
        st.button("清空選項", width="stretch", on_click=_clear_options)

    st.caption("目前選項")
    current_options: list[str] = st.session_state[STATE_OPTIONS]
    if not current_options:
        st.info("尚未加入任何選項")
    else:
        st.caption("可直接雙擊儲存格修改文字，也可新增/刪除列")
        editor_rows = [{"選項": option} for option in current_options]
        edited_rows = st.data_editor(
            editor_rows,
            key="admin_option_editor",
            hide_index=True,
            width="stretch",
            num_rows="dynamic",
            column_config={
                "選項": st.column_config.TextColumn(
                    "選項",
                    help="雙擊後可直接修改",
                    required=True,
                )
            },
        )

        updated_options = normalize_option_list(extract_editor_column_values(edited_rows, "選項"))
        if updated_options != current_options:
            st.session_state[STATE_OPTIONS] = updated_options
            current_options = updated_options

    vote_name = str(st.session_state.get(STATE_VOTE_NAME, "")).strip()
    can_submit = bool(vote_name) and len(current_options) >= 2
    st.caption(f"已加入 {len(current_options)} 個選項，至少需要 2 個")

    if st.button("建立投票", type="primary", disabled=not can_submit):
        vote_uuid = service.storage.create_vote(vote_name, set(current_options))
        st.success(f"已建立投票：{vote_name}（ID: {vote_uuid[:8]}）")
        st.code(f"/vote?uuid={vote_uuid}", language="text")
        st.session_state[STATE_PENDING_RESET] = True
        st.rerun()

    st.subheader("現有投票")
    configs = service.storage.list_vote_configs()
    if not configs:
        st.info("目前尚未建立任何投票。")
        return

    rows: list[dict[str, Any]] = []
    for uuid, config in configs:
        rows.append(
            {
                "selected": False,
                "uuid": uuid,
                "topic": config.name,
                "options": "、".join(sorted(config.options)),
                "start_time": parse_optional_iso_datetime(config.start_time),
                "end_time": parse_optional_iso_datetime(config.end_time),
                "vote_url": f"/vote?uuid={uuid}",
                "file": str(config.path),
            }
        )

    edited_rows = st.data_editor(
        rows,
        key="admin_vote_table_editor",
        width="stretch",
        hide_index=True,
        num_rows="fixed",
        disabled=["uuid", "vote_url", "file"],
        column_config={
            "selected": st.column_config.CheckboxColumn(""),
            "uuid": st.column_config.TextColumn("uuid", width="small"),
            "topic": st.column_config.TextColumn("主題", width="medium", required=True),
            "options": st.column_config.TextColumn("選項", width="large", help="可用 、 或 , 分隔"),
            "start_time": st.column_config.DatetimeColumn(
                "開始時間",
                width="medium",
                help="點選日曆與時間選擇器",
                format="YYYY-MM-DD HH:mm:ss",
                required=True,
            ),
            "end_time": st.column_config.DatetimeColumn(
                "結束時間",
                width="medium",
                help="點選日曆與時間選擇器",
                format="YYYY-MM-DD HH:mm:ss",
                required=True,
            ),
            "vote_url": st.column_config.TextColumn("投票連結", width="large"),
            "file": st.column_config.TextColumn("檔案", width="large"),
        },
    )

    edited_table_rows = extract_editor_rows(edited_rows)
    if st.button("儲存主題/選項變更", type="primary"):
        errors: list[str] = []
        success_count = 0
        for row in edited_table_rows:
            vote_uuid = str(row.get("uuid", "")).strip()
            topic = str(row.get("topic", "")).strip()
            options_text = str(row.get("options", ""))
            options = parse_options_text(options_text)
            start_time = to_iso_datetime_text(row.get("start_time"))
            end_time = to_iso_datetime_text(row.get("end_time"))

            try:
                if not start_time or not end_time:
                    raise ValueError("開始時間與結束時間為必填")
                service.storage.update_vote(vote_uuid, name=topic, options=options)
                config = service.storage.get_vote_config(vote_uuid)
                if config is None:
                    raise ValueError("Vote config not found")
                service.storage.update_vote_rounds(
                    vote_uuid,
                    start_time=start_time,
                    end_time=end_time,
                    rounds=config.rounds,
                )
                success_count += 1
            except ValueError as exc:
                errors.append(f"{vote_uuid[:8]}: {exc}")

        if success_count:
            st.success(f"已更新 {success_count} 筆投票設定")
        if errors:
            st.error("更新失敗：" + "；".join(errors))
        st.rerun()

    selected_delete_uuids = [
        str(row.get("uuid", ""))
        for row in edited_table_rows
        if isinstance(row, dict) and bool(row.get("selected", False))
    ]

    if st.button("刪除勾選項目", type="secondary", disabled=not selected_delete_uuids):
        deleted_names: list[str] = []
        for vote_uuid in selected_delete_uuids:
            deleted = service.storage.delete_vote(vote_uuid)
            if deleted:
                deleted_names.append(deleted.name)

        if deleted_names:
            st.warning("已刪除：" + "、".join(deleted_names))
            st.rerun()

    st.subheader("輪次設定")
    round_vote_uuid = st.selectbox(
        "選擇要設定輪次的投票",
        options=[uuid for uuid, _ in configs],
        format_func=lambda item: f"{service.storage.vote_configs[item].name} ({item[:8]})",
        key="admin_round_vote_uuid",
    )

    round_config = service.storage.get_vote_config(round_vote_uuid)
    if round_config is None:
        st.error("找不到投票設定")
        return

    st.caption("輪次名稱可自訂；投票頁會自動使用目前時間落在區間內的輪次，使用者無法自行選擇")

    round_rows: list[dict[str, Any]] = []
    for round_uuid, item in round_config.rounds.items():
        round_rows.append(
            {
                "round_uuid": round_uuid,
                "name": item.name,
                "start_time": parse_optional_iso_datetime(item.start_time),
                "end_time": parse_optional_iso_datetime(item.end_time),
            }
        )

    edited_round_rows = st.data_editor(
        round_rows,
        key="admin_rounds_editor",
        width="stretch",
        hide_index=True,
        num_rows="dynamic",
        disabled=["round_uuid"],
        column_config={
            "round_uuid": st.column_config.TextColumn("輪次 UUID", help="系統自動產生，無需手動輸入"),
            "name": st.column_config.TextColumn("顯示名稱", required=True),
            "start_time": st.column_config.DatetimeColumn(
                "開始時間", help="點選日曆與時間選擇器", format="YYYY-MM-DD HH:mm:ss", required=True
            ),
            "end_time": st.column_config.DatetimeColumn(
                "結束時間", help="點選日曆與時間選擇器", format="YYYY-MM-DD HH:mm:ss", required=True
            ),
        },
    )

    edited_round_data = extract_editor_rows(edited_round_rows)
    if st.button("儲存輪次設定", type="primary"):
        rounds_payload: dict[str, VoteRoundConfig] = {}
        try:
            for row in edited_round_data:
                raw_uuid = _normalize_round_uuid(row.get("round_uuid"))
                round_uuid = raw_uuid if raw_uuid else str(uuid4())
                round_start = to_iso_datetime_text(row.get("start_time"))
                round_end = to_iso_datetime_text(row.get("end_time"))
                if not round_start or not round_end:
                    raise ValueError("輪次開始/結束時間為必填")
                rounds_payload[round_uuid] = VoteRoundConfig(
                    name=str(row.get("name", "")).strip(),
                    start_time=round_start,
                    end_time=round_end,
                )

            service.storage.update_vote_rounds(
                round_vote_uuid,
                start_time=round_config.start_time,
                end_time=round_config.end_time,
                rounds=rounds_payload,
            )
            st.success("輪次設定已更新")
            st.rerun()
        except ValueError as exc:
            st.error(f"輪次設定失敗：{exc}")
