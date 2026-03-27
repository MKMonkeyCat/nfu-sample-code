from __future__ import annotations

from typing import NamedTuple, TypedDict


class VoteRecord(NamedTuple):
    """Vote record with optional round/date support."""

    name: str
    option: str
    round: str = "default"


class SummaryData(NamedTuple):
    """Summary data structure for vote statistics."""

    total: int
    counts: dict[str, int]
    modes: list[str]
    mode_count: int
    least: list[str]
    least_count: int


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


class RoundComparisonRow(TypedDict):
    """Row model for round comparison table."""

    round_name: str
    total_votes: int
    modes_text: str
