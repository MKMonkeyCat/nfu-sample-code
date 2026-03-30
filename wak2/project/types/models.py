from __future__ import annotations

from typing import NamedTuple, TypedDict


class VoteRecord(NamedTuple):
    """Vote record with optional round/date support."""

    name: str
    option: str
    round: str = "default"
    vote_time: str = ""


class SummaryData(NamedTuple):
    """Summary data structure for vote statistics."""

    total: int  # 總票數
    counts: dict[str, int]  # 選項票數
    modes: list[str]  # 眾數選項
    mode_count: int  # 眾數票數
    least: list[str]  # 最少票選項
    least_count: int  # 最少票數


class StatisticsData(NamedTuple):
    """Aggregated statistics used by shared UI components."""

    total: int
    counts: dict[str, int]
    modes: list[str]
    mode_count: int
    least: list[str]
    least_count: int
    unique_voters: int
    unique_options: int
    rounds: list[str]


class CountRow(TypedDict):
    """Row model for the vote count table."""

    option: str
    votes: int
    ratio: str


class VoteTableRow(TypedDict):
    """Row model for vote detail table."""

    round_name: str
    voter_name: str
    option: str
    vote_time: str


class RoundComparisonRow(TypedDict):
    """Row model for round comparison table."""

    round_name: str
    total_votes: int
    modes_text: str
