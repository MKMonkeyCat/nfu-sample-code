from __future__ import annotations

from functools import partial

import streamlit as st

from project.core import VoteCoreService
from project.pages.admin import render as render_admin
from project.pages.analyze import render as render_analyze
from project.pages.vote import render as render_vote


def _render_home() -> None:
    st.title("眾數應用互動遊戲系統")
    st.markdown(
        """
        這個系統支援：
        - 互動投票與 CSV 存取
        - 眾數與最少選項統計
        - 多輪投票比較
        - 長條圖與圓餅圖視覺化
        """
    )


def run_web() -> None:
    st.set_page_config(page_title="Mode Vote System", page_icon="🗳️", layout="wide")
    service = VoteCoreService()

    if hasattr(st, "Page") and hasattr(st, "navigation"):
        pages = [
            st.Page(_render_home, title="首頁", icon="🏠", url_path="home"),
            st.Page(partial(render_admin, service), title="管理", icon="🛠️", url_path="admin"),
            st.Page(partial(render_vote, service), title="投票", icon="🗳️", url_path="vote"),
            st.Page(partial(render_analyze, service), title="分析", icon="📊", url_path="analyze"),
        ]
        navigation = st.navigation({"Vote System": pages}, position="sidebar")
        navigation.run()
        return

    # Fallback for older Streamlit versions without path navigation.
    page = st.sidebar.radio("功能頁", ["首頁", "管理", "投票", "分析"], index=0)
    if page == "首頁":
        _render_home()
    elif page == "管理":
        render_admin(service)
    elif page == "投票":
        render_vote(service)
    else:
        render_analyze(service)


if __name__ == "__main__":
    run_web()
