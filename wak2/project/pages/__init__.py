from __future__ import annotations

from .admin import render as render_admin
from .analyze import render as render_analyze
from .vote import render as render_vote

__all__ = ["PAGES"]


PAGES = [
    ("admin", "管理頁", render_admin),
    ("vote", "投票頁", render_vote),
    ("analyze", "分析頁", render_analyze),
]
