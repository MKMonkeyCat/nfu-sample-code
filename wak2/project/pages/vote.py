from __future__ import annotations

from collections.abc import Sequence

import streamlit as st

from project.core import VoteCoreService
from project.core.storage import VoteConfig


def _get_uuid_from_query() -> str:
    raw = st.query_params.get("uuid", "")
    if isinstance(raw, list):
        return str(raw[0]).strip() if raw else ""
    return str(raw).strip()


def _render_uuid_help(configs: Sequence[tuple[str, VoteConfig]]) -> None:
    st.info("請使用投票連結進入此頁，例如：/vote?uuid=<投票UUID>")
    st.caption("可用 UUID 清單")
    for uuid, config in configs:
        st.markdown(f"- [{config.name} ({uuid[:8]})](/vote?uuid={uuid})")


def render(service: VoteCoreService) -> None:
    st.header("投票頁")
    configs = service.storage.list_vote_configs()

    if not configs:
        st.info("目前沒有投票活動，請先到管理頁建立。")
        return

    vote_uuid = _get_uuid_from_query()
    if not vote_uuid:
        _render_uuid_help(configs)
        return

    config = service.storage.get_vote_config(vote_uuid)
    if config is None:
        st.error(f"找不到對應投票：{vote_uuid}")
        _render_uuid_help(configs)
        return

    st.subheader(config.name)
    # st.caption(f"UUID: {vote_uuid}")

    active_round = service.storage.get_active_round(vote_uuid)
    if active_round is None:
        st.warning("目前沒有可用輪次（可能未設定輪次時間，或不在投票時間區間）")
        return

    round_uuid, round_config = active_round
    st.caption(f"目前輪次：{round_config.name} ({round_uuid[:8]})")

    # st.caption("可投選項：" + "、".join(sorted(config.options)))

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
