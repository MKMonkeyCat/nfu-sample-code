from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

import streamlit as st

from project.core import VoteCoreService
from project.core.storage import VoteConfig, VoteRoundConfig
from project.utils.datetime import parse_optional_iso_datetime, to_iso_datetime_text
from project.utils.streamlit_table import extract_editor_rows
from project.utils.streamlit_ui import render_callout, render_empty_state

from .admin_shared import (
    STATE_ROUND_DELETE_RESET_PENDING,
    STATE_ROUND_DELETE_SELECTION,
    STATE_ROUND_DRAFT_IDS,
    STATE_ROUND_DRAFT_ROWS,
    STATE_ROUND_DRAFT_VOTE_UUID,
    STATE_ROUND_EDITOR_VERSION,
    STATE_ROUND_NOTICE,
)


def _build_round_rows(config: VoteConfig) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for _, item in config.rounds.items():
        rows.append(
            {
                "name": item.name,
                "start_time": parse_optional_iso_datetime(item.start_time),
                "end_time": parse_optional_iso_datetime(item.end_time),
            }
        )
    return rows


def _align_round_ids(rows: list[dict[str, Any]], ids: list[str]) -> list[str]:
    aligned_ids = list(ids[: len(rows)])
    while len(aligned_ids) < len(rows):
        aligned_ids.append("")
    return aligned_ids


def _reset_round_draft(vote_uuid: str, config: VoteConfig) -> None:
    st.session_state[STATE_ROUND_DRAFT_VOTE_UUID] = vote_uuid
    st.session_state[STATE_ROUND_DRAFT_ROWS] = _build_round_rows(config)
    st.session_state[STATE_ROUND_DRAFT_IDS] = [round_uuid for round_uuid, _ in config.rounds.items()]
    st.session_state[STATE_ROUND_EDITOR_VERSION] = (
        int(st.session_state.get(STATE_ROUND_EDITOR_VERSION, 0)) + 1
    )
    st.session_state[STATE_ROUND_DELETE_RESET_PENDING] = True


def _reset_round_draft_to_first_round(vote_uuid: str) -> None:
    now = datetime.now(UTC)
    st.session_state[STATE_ROUND_DRAFT_VOTE_UUID] = vote_uuid
    st.session_state[STATE_ROUND_DRAFT_ROWS] = [
        {
            "name": "第1輪",
            "start_time": now,
            "end_time": now + timedelta(minutes=30),
        }
    ]
    st.session_state[STATE_ROUND_DRAFT_IDS] = [""]
    st.session_state[STATE_ROUND_EDITOR_VERSION] = (
        int(st.session_state.get(STATE_ROUND_EDITOR_VERSION, 0)) + 1
    )
    st.session_state[STATE_ROUND_DELETE_RESET_PENDING] = True


def _ensure_round_draft(vote_uuid: str, config: VoteConfig) -> None:
    current_vote_uuid = str(st.session_state.get(STATE_ROUND_DRAFT_VOTE_UUID, ""))
    if current_vote_uuid != vote_uuid:
        _reset_round_draft(vote_uuid, config)


def _to_datetime_value(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)

    to_pydatetime = getattr(value, "to_pydatetime", None)
    if callable(to_pydatetime):
        converted = to_pydatetime()
        if isinstance(converted, datetime):
            return converted if converted.tzinfo else converted.replace(tzinfo=UTC)

    text = to_iso_datetime_text(value)
    if not text:
        return None
    try:
        parsed = parse_optional_iso_datetime(text)
    except ValueError:
        return None
    return parsed if parsed is None or parsed.tzinfo else parsed.replace(tzinfo=UTC)


def _append_next_round(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    next_rows = [dict(row) for row in rows]
    switch_time = datetime.now(UTC)

    if next_rows:
        last_row = next_rows[-1]
        last_start = _to_datetime_value(last_row.get("start_time"))
        last_end = _to_datetime_value(last_row.get("end_time"))
        if last_start is not None and last_end is not None and last_start <= switch_time <= last_end:
            last_row["end_time"] = switch_time

    next_rows.append(
        {
            "name": f"第{len(rows) + 1}輪",
            "start_time": switch_time,
            "end_time": switch_time + timedelta(minutes=30),
        }
    )
    return next_rows


def _remove_selected_rounds(
    rows: list[dict[str, Any]], ids: list[str]
) -> tuple[list[dict[str, Any]], list[str]]:
    kept_rows: list[dict[str, Any]] = []
    kept_ids: list[str] = []
    for index, row in enumerate(rows):
        if bool(row.get("_delete", False)):
            continue
        clean_row = dict(row)
        clean_row.pop("_delete", None)
        kept_rows.append(clean_row)
        kept_ids.append(ids[index] if index < len(ids) else "")
    return kept_rows, kept_ids


def _save_round_changes(
    service: VoteCoreService,
    vote_uuid: str,
    config: VoteConfig,
    rows: list[dict[str, Any]],
) -> None:
    rounds_payload: dict[str, VoteRoundConfig] = {}
    round_starts: list[datetime] = []
    round_ends: list[datetime] = []

    for row in rows:
        raw_uuid = str(row.get("round_uuid", "")).strip()
        round_uuid = (
            raw_uuid if raw_uuid and raw_uuid.lower() not in {"none", "null", "nan"} else str(uuid4())
        )
        round_start = to_iso_datetime_text(row.get("start_time"))
        round_end = to_iso_datetime_text(row.get("end_time"))
        if not round_start or not round_end:
            raise ValueError("輪次開始時間與結束時間為必填")

        rounds_payload[round_uuid] = VoteRoundConfig(
            name=str(row.get("name", "")).strip(),
            start_time=round_start,
            end_time=round_end,
        )

        parsed_start = parse_optional_iso_datetime(round_start)
        parsed_end = parse_optional_iso_datetime(round_end)
        if parsed_start is not None:
            round_starts.append(parsed_start)
        if parsed_end is not None:
            round_ends.append(parsed_end)

    overall_start = config.start_time
    overall_end = config.end_time
    if round_starts:
        overall_start = to_iso_datetime_text(min(round_starts))
    if round_ends:
        overall_end = to_iso_datetime_text(max(round_ends))

    service.storage.update_vote_rounds(
        vote_uuid,
        start_time=overall_start,
        end_time=overall_end,
        rounds=rounds_payload,
    )


def render_rounds_tab(service: VoteCoreService, configs: list[tuple[str, VoteConfig]]) -> None:
    if not configs:
        render_empty_state("目前沒有可設定輪次的投票", hint="請先建立投票主題")
        return

    round_vote_uuid = st.selectbox(
        "選擇要設定輪次的投票",
        options=[vote_uuid for vote_uuid, _ in configs],
        format_func=lambda item: f"{service.storage.vote_configs[item].name} ({item[:8]})",
        key="admin_round_vote_uuid",
    )

    config = service.storage.get_vote_config(round_vote_uuid)
    if config is None:
        render_empty_state("找不到投票設定", level="error")
        return

    _ensure_round_draft(round_vote_uuid, config)

    render_callout(
        "輪次",
        [
            "投票頁只會顯示目前生效的輪次",
            "新增下一輪會從現在開始，預設 30 分鐘結束 (可自行手動更改時間)",
            "修改完成後，按儲存輪次設定即可",
        ],
    )

    round_notice = st.session_state.get(STATE_ROUND_NOTICE, {})
    if isinstance(round_notice, dict) and round_notice:
        message = str(round_notice.get("message", "")).strip()
        config_path = str(round_notice.get("config_path", "")).strip()
        data_path = str(round_notice.get("data_path", "")).strip()
        if message:
            st.success(message)
        if config_path or data_path:
            details: list[str] = []
            if config_path:
                details.append(f"設定檔：{config_path}")
            if data_path:
                details.append(f"資料檔：{data_path}")
            st.caption("  ".join(details))
        st.session_state[STATE_ROUND_NOTICE] = ""

    draft_rows: list[dict[str, object]] = list(st.session_state.get(STATE_ROUND_DRAFT_ROWS, []))
    draft_ids: list[str] = list(st.session_state.get(STATE_ROUND_DRAFT_IDS, []))
    editor_key = f"admin_rounds_editor_{st.session_state.get(STATE_ROUND_EDITOR_VERSION, 0)}"
    edited_rows = st.data_editor(
        draft_rows,
        key=editor_key,
        width="stretch",
        hide_index=True,
        num_rows="fixed",
        column_config={
            "name": st.column_config.TextColumn("顯示名稱", required=True),
            "start_time": st.column_config.DatetimeColumn(
                "開始時間",
                help="使用目前時區",
                format="YYYY-MM-DD HH:mm:ss",
                required=True,
            ),
            "end_time": st.column_config.DatetimeColumn(
                "結束時間",
                help="使用目前時區",
                format="YYYY-MM-DD HH:mm:ss",
                required=True,
            ),
        },
    )

    current_rows = extract_editor_rows(edited_rows)
    current_ids = _align_round_ids(current_rows, draft_ids)
    delete_options = list(range(len(current_rows)))
    if bool(st.session_state.get(STATE_ROUND_DELETE_RESET_PENDING, False)):
        st.session_state[STATE_ROUND_DELETE_SELECTION] = []
        st.session_state[STATE_ROUND_DELETE_RESET_PENDING] = False
    else:
        saved_selection = list(st.session_state.get(STATE_ROUND_DELETE_SELECTION, []))
        cleaned_selection = [
            index for index in saved_selection if isinstance(index, int) and 0 <= index < len(delete_options)
        ]
        if cleaned_selection != saved_selection:
            st.session_state[STATE_ROUND_DELETE_SELECTION] = cleaned_selection

    selected_delete_indexes = set(
        st.multiselect(
            "選擇要刪除的輪次",
            options=delete_options,
            format_func=lambda index: f"{index + 1}. {str(current_rows[index].get('name', '')).strip() or '未命名輪次'}",
            placeholder="不刪除可留空",
            key=STATE_ROUND_DELETE_SELECTION,
        )
    )

    action_col, delete_col, reset_col = st.columns([1, 1, 1])
    with action_col:
        if st.button("新增下一輪", width="stretch"):
            next_rows = _append_next_round(current_rows)
            next_ids = list(current_ids)
            next_ids.append("")
            st.session_state[STATE_ROUND_DRAFT_ROWS] = next_rows
            st.session_state[STATE_ROUND_DRAFT_IDS] = next_ids
            st.session_state[STATE_ROUND_EDITOR_VERSION] = (
                int(st.session_state.get(STATE_ROUND_EDITOR_VERSION, 0)) + 1
            )
            st.rerun()
    with delete_col:
        selected_count = len(selected_delete_indexes)
        if st.button("刪除勾選輪次", width="stretch", disabled=selected_count == 0):
            if selected_count >= len(current_rows):
                st.warning("至少保留 1 個輪次。")
                return
            rows_with_delete_flag: list[dict[str, object]] = []
            for index, row in enumerate(current_rows):
                marked_row = dict(row)
                marked_row["_delete"] = index in selected_delete_indexes
                rows_with_delete_flag.append(marked_row)
            next_rows, next_ids = _remove_selected_rounds(rows_with_delete_flag, current_ids)
            st.session_state[STATE_ROUND_DRAFT_ROWS] = next_rows
            st.session_state[STATE_ROUND_DRAFT_IDS] = next_ids
            st.session_state[STATE_ROUND_EDITOR_VERSION] = (
                int(st.session_state.get(STATE_ROUND_EDITOR_VERSION, 0)) + 1
            )
            st.session_state[STATE_ROUND_DELETE_RESET_PENDING] = True
            st.rerun()
    with reset_col:
        if st.button("重設輪次", width="stretch"):
            _reset_round_draft_to_first_round(round_vote_uuid)
            st.rerun()

    if st.button("儲存輪次設定", type="primary"):
        try:
            payload_rows: list[dict[str, object]] = []
            aligned_ids = _align_round_ids(current_rows, current_ids)
            for index, row in enumerate(current_rows):
                payload_rows.append(
                    {
                        "round_uuid": aligned_ids[index],
                        "name": row.get("name"),
                        "start_time": row.get("start_time"),
                        "end_time": row.get("end_time"),
                    }
                )

            _save_round_changes(service, round_vote_uuid, config, payload_rows)
            updated_config = service.storage.get_vote_config(round_vote_uuid)
            if updated_config is not None:
                _reset_round_draft(round_vote_uuid, updated_config)
            active_round = service.storage.get_active_round(round_vote_uuid)
            if active_round is None:
                message = "輪次設定已更新，目前沒有生效中的輪次"
            else:
                _, active_round_config = active_round
                message = f"輪次設定已更新，目前生效輪次為：{active_round_config.name}"
            st.session_state[STATE_ROUND_NOTICE] = {
                "message": message,
                "config_path": str(service.storage.config_path.resolve()),
                "data_path": str(
                    (updated_config.path if updated_config is not None else config.path).resolve()
                ),
            }
            st.rerun()
        except ValueError as exc:
            st.error(f"輪次設定失敗：{exc}")
