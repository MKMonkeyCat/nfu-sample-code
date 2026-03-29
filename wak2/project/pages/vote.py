from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from project.core import VoteCoreService
from project.core.storage import VoteConfig
from project.utils.streamlit_ui import (
    render_callout,
    render_empty_state,
    render_page_intro,
)


def _get_uuid_from_query() -> str:
    raw = st.query_params.get("uuid", "")
    if isinstance(raw, list):
        return str(raw[0]).strip() if raw else ""
    return str(raw).strip()


def _render_uuid_help(configs: Sequence[tuple[str, VoteConfig]]) -> None:
    render_empty_state("請使用下方投票連結進入此頁")
    st.caption("投票連結清單")
    for uuid, config in configs:
        st.markdown(f"- [{config.name} ({uuid[:8]})](/vote?uuid={uuid})")


def render(service: VoteCoreService) -> None:
    render_page_intro("投票頁", "使用專屬連結進入投票，系統會自動套用目前生效的輪次")
    configs = service.storage.list_vote_configs()

    if not configs:
        render_empty_state("目前沒有投票活動，請先到管理頁建立。")
        return

    vote_uuid = _get_uuid_from_query()
    if not vote_uuid:
        _render_uuid_help(configs)
        return

    config = service.storage.get_vote_config(vote_uuid)
    if config is None:
        render_empty_state(f"找不到對應投票：{vote_uuid}", level="error")
        _render_uuid_help(configs)
        return

    st.subheader(config.name)

    active_round = service.storage.get_active_round(vote_uuid)
    if active_round is None:
        render_empty_state(
            "目前沒有可用輪次。", hint="可能尚未設定輪次時間，或現在不在投票開放區間內。", level="warning"
        )
        return

    round_uuid, round_config = active_round
    summary_col, meta_col = st.columns([2, 1])
    with summary_col:
        render_callout(
            "本輪資訊",
            [
                f"目前輪次：{round_config.name}",
                f"可投選項：{len(config.options)} 個",
                f"輪次識別碼：{round_uuid[:8]}",
            ],
        )
    with meta_col:
        st.metric("可投選項", len(config.options))
        st.metric("累積票數", len(service.storage.read_vote_records(vote_uuid, round_name=round_uuid)))

    with st.form("vote_form", clear_on_submit=True):
        voter_name = st.text_input("姓名", placeholder="輸入投票者姓名")
        option = st.selectbox("選項", options=sorted(config.options))
        submit = st.form_submit_button("送出投票")

        if submit:
            if not voter_name.strip():
                st.error("請輸入姓名")
            else:
                service.storage.add_vote_record(
                    uuid=vote_uuid,
                    voter_name=voter_name.strip(),
                    option=option,
                    round_name=round_uuid,
                )

                current_round_records = service.storage.read_vote_records(vote_uuid, round_name=round_uuid)
                summary = service.analysis.summarize(current_round_records)
                mode_text = "、".join(summary.modes) if summary.modes else "無"
                st.success(f"投票成功：{voter_name.strip()} -> {option}")
                st.info(f"目前眾數（{round_config.name}）：{mode_text}（{summary.mode_count}票）")

    # all_records = service.storage.read_vote_records(vote_uuid)
    # st.subheader("目前資料")
    # st.write(f"總筆數：{len(all_records)}")

    # if all_records:
    #     st.dataframe(
    #         service.analysis.vote_rows(all_records),
    #         width="stretch",
    #         hide_index=True,
    #     )
