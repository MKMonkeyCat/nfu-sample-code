from __future__ import annotations

from typing import NamedTuple


class VoteSelection(NamedTuple):
    uuid: str
    name: str


def vote_display_text(item: VoteSelection) -> str:
    return f"{item.name} ({item.uuid[:8]})"


__all__ = ["VoteSelection", "vote_display_text"]
