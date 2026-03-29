from __future__ import annotations

from typing import Any

import streamlit as st

from project.core import VoteCoreService
from project.core.storage import VoteConfig
from project.utils.datetime import parse_optional_iso_datetime, to_iso_datetime_text
from project.utils.text_normalize import normalize_option_list, normalize_option_text, parse_options_text

STATE_OPTIONS = "admin_draft_options"
STATE_NEW_OPTION = "admin_new_option"
STATE_VOTE_NAME = "admin_vote_name"
STATE_PENDING_RESET = "admin_pending_reset"
STATE_ROUND_DRAFT_VOTE_UUID = "admin_round_draft_vote_uuid"
STATE_ROUND_DRAFT_ROWS = "admin_round_draft_rows"
STATE_ROUND_DRAFT_IDS = "admin_round_draft_ids"
STATE_ROUND_NOTICE = "admin_round_notice"
STATE_ROUND_EDITOR_VERSION = "admin_round_editor_version"
STATE_ROUND_DELETE_SELECTION = "admin_round_delete_selection"
STATE_ROUND_DELETE_RESET_PENDING = "admin_round_delete_reset_pending"
PLACEHOLDER_OPTIONS = {"選項 A", "選項 B", "選項 C"}
DEFAULT_QUICK_OPTIONS = ["選項 A", "選項 B", "選項 C"]


def init_state() -> None:
    defaults: dict[str, Any] = {
        STATE_OPTIONS: [],
        STATE_NEW_OPTION: "",
        STATE_VOTE_NAME: "",
        STATE_PENDING_RESET: False,
        STATE_ROUND_DRAFT_VOTE_UUID: "",
        STATE_ROUND_DRAFT_ROWS: [],
        STATE_ROUND_DRAFT_IDS: [],
        STATE_ROUND_NOTICE: "",
        STATE_ROUND_EDITOR_VERSION: 0,
        STATE_ROUND_DELETE_SELECTION: [],
        STATE_ROUND_DELETE_RESET_PENDING: False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def apply_pending_reset() -> None:
    if not bool(st.session_state.get(STATE_PENDING_RESET, False)):
        return

    st.session_state[STATE_OPTIONS] = []
    st.session_state[STATE_NEW_OPTION] = ""
    st.session_state[STATE_VOTE_NAME] = ""
    st.session_state[STATE_PENDING_RESET] = False


def append_options(options: list[str]) -> int:
    current: list[str] = st.session_state[STATE_OPTIONS]
    appended = 0
    for option in normalize_option_list(options):
        if option not in current:
            current.append(option)
            appended += 1
    return appended


def add_option_from_input() -> None:
    option = normalize_option_text(st.session_state.get(STATE_NEW_OPTION, ""))
    if not option:
        return

    if append_options([option]) == 0:
        st.warning(f"選項「{option}」已存在")
        return

    st.session_state[STATE_NEW_OPTION] = ""


def clear_options() -> None:
    st.session_state[STATE_OPTIONS] = []


def count_manual_options(options: list[str]) -> int:
    return sum(1 for option in options if option not in PLACEHOLDER_OPTIONS)


def build_vote_rows(configs: list[tuple[str, VoteConfig]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for vote_uuid, config in configs:
        rows.append(
            {
                "selected": False,
                "uuid": vote_uuid,
                "topic": config.name,
                "options": "、".join(sorted(config.options)),
                "start_time": parse_optional_iso_datetime(config.start_time),
                "end_time": parse_optional_iso_datetime(config.end_time),
                "vote_url": f"/vote?uuid={vote_uuid}",
                "file": str(config.path),
            }
        )
    return rows


def save_vote_table_changes(service: VoteCoreService, rows: list[dict[str, Any]]) -> None:
    errors: list[str] = []
    success_count = 0

    for row in rows:
        vote_uuid = str(row.get("uuid", "")).strip()
        topic = str(row.get("topic", "")).strip()
        options = parse_options_text(str(row.get("options", "")))
        start_time = to_iso_datetime_text(row.get("start_time"))
        end_time = to_iso_datetime_text(row.get("end_time"))

        try:
            if not start_time or not end_time:
                raise ValueError("開始時間與結束時間為必填")

            service.storage.update_vote(vote_uuid, name=topic, options=options)
            config = service.storage.get_vote_config(vote_uuid)
            if config is None:
                raise ValueError("找不到投票設定")

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
    if success_count or errors:
        st.rerun()


def delete_selected_votes(service: VoteCoreService, rows: list[dict[str, Any]]) -> None:
    selected_uuids = [
        str(row.get("uuid", "")).strip()
        for row in rows
        if isinstance(row, dict) and bool(row.get("selected", False))
    ]
    if not selected_uuids:
        return

    deleted_names: list[str] = []
    for vote_uuid in selected_uuids:
        deleted = service.storage.delete_vote(vote_uuid)
        if deleted is not None:
            deleted_names.append(deleted.name)

    if deleted_names:
        st.warning("已刪除：" + "、".join(deleted_names))
        st.rerun()
