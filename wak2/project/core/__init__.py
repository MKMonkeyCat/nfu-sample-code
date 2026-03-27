"""Compatibility facade for core operations.

Public API remains available from this module while implementations are split
into smaller files to keep each file maintainable.
"""

from project.core.analysis import (
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
    ROUND_NAME_PATTERN,
    ROUND_OPTIONS,
)
from project.core.storage import (
    add_vote,
    delete_votes_by_indices,
    ensure_csv,
    read_votes,
    validate_round_name,
    validate_vote_data,
)

__all__ = [
    "ROUND_OPTIONS",
    "CUSTOM_ROUND_OPTION",
    "ROUND_NAME_PATTERN",
    "get_round_sort_key",
    "sort_round_names",
    "sort_records",
    "sort_records_for_detail",
    "ensure_csv",
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
