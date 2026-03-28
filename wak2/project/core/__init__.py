"""Compatibility facade for core operations.

Public API remains available from this module while implementations are split
into smaller files to keep each file maintainable.
"""

from project.core.analysis import (
    VoteAnalysisService,
    build_summary,
    compare_rounds,
    count_options,
    get_all_rounds,
    get_least_options,
    get_mode_changes,
    get_modes,
    get_round_sort_key,
    get_statistics,
    sort_records,
    sort_records_for_detail,
    sort_round_names,
)
from project.core.constants import (
    CUSTOM_ROUND_OPTION,
    DEFAULT_ROUND,
    MODE_MULTI,
    ROUND_NAME_PATTERN,
    ROUND_OPTIONS,
    ROUND_SINGLE,
)
from project.core.storage import (
    VoteStorageService,
    add_vote,
    delete_votes_by_indices,
    read_votes,
    validate_round_name,
    validate_vote_data,
)


class VoteCoreService:
    """Facade service that composes storage and analysis services."""

    def __init__(self) -> None:
        self.storage = VoteStorageService()
        self.analysis = VoteAnalysisService(self.storage)


__all__ = [
    "VoteStorageService",
    "VoteAnalysisService",
    "VoteCoreService",
    "ROUND_OPTIONS",
    "ROUND_SINGLE",
    "MODE_MULTI",
    "DEFAULT_ROUND",
    "CUSTOM_ROUND_OPTION",
    "ROUND_NAME_PATTERN",
    "get_round_sort_key",
    "sort_round_names",
    "sort_records",
    "sort_records_for_detail",
    "add_vote",
    "read_votes",
    "get_all_rounds",
    "count_options",
    "get_modes",
    "get_least_options",
    "build_summary",
    "compare_rounds",
    "get_mode_changes",
    "validate_vote_data",
    "validate_round_name",
    "get_statistics",
    "delete_votes_by_indices",
]
