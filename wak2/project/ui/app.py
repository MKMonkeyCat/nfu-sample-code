"""Compatibility facade for UI entry points."""

from __future__ import annotations

from .report_page import render_report_app
from .theme import configure_page
from .vote_page import render_vote_app

__all__ = [
    "configure_page",
    "render_vote_app",
    "render_report_app",
]
