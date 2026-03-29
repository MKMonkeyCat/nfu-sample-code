from __future__ import annotations

import streamlit as st

from project.core import VoteCoreService
from project.utils.streamlit_ui import render_page_intro

from .admin_create_tab import render_create_tab
from .admin_manage_tab import render_manage_tab
from .admin_rounds_tab import render_rounds_tab
from .admin_shared import apply_pending_reset, init_state


def render(service: VoteCoreService) -> None:
    init_state()
    apply_pending_reset()

    render_page_intro("管理頁", "建立投票、管理投票和輪次設定")
    tab_create, tab_manage, tab_rounds = st.tabs(["建立投票", "管理投票", "輪次設定"])

    with tab_create:
        render_create_tab(service)

    configs = service.storage.list_vote_configs()
    with tab_manage:
        render_manage_tab(service, configs)

    with tab_rounds:
        render_rounds_tab(service, configs)
