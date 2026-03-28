from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

from project.types import StatisticsData, SummaryData, VoteRecord

from .constants import ROUND_OPTIONS, ROUND_SINGLE
from .storage import VoteStorageService


class VoteAnalysisService:
    """Encapsulates vote analysis and summary calculations."""

    def __init__(self, storage_service: VoteStorageService | None = None) -> None:
        self.storage = storage_service or VoteStorageService()

    def get_round_sort_key(self, round_name: str) -> tuple[int, int | str]:
        """Build a stable sort key for round names."""
        if round_name == ROUND_SINGLE:
            return (0, 0)

        if round_name in ROUND_OPTIONS:
            return (1, ROUND_OPTIONS.index(round_name))

        return (2, round_name.lower())

    def sort_round_names(self, round_names: list[str]) -> list[str]:
        """Sort round names by the app's display order."""
        return sorted(round_names, key=self.get_round_sort_key)

    def sort_records(self, records: list[VoteRecord]) -> list[VoteRecord]:
        """Sort records by round, then by voter name and option."""
        return sorted(
            records,
            key=lambda record: (self.get_round_sort_key(record.round), record.name, record.option),
        )

    def count_options(self, records: list[VoteRecord]) -> dict[str, int]:
        """Count votes per option."""
        return dict(Counter(option for record in records for option in [record.option]))

    def get_modes(self, counts: dict[str, int]) -> tuple[list[str], int]:
        """Return all modes and their vote count."""
        if not counts:
            return [], 0

        max_count = max(counts.values())
        modes = sorted([option for option, count in counts.items() if count == max_count])
        return modes, max_count

    def get_least_options(self, counts: dict[str, int]) -> tuple[list[str], int]:
        """Return all least-voted options and their vote count."""
        if not counts:
            return [], 0

        min_count = min(counts.values())
        least = sorted([option for option, count in counts.items() if count == min_count])
        return least, min_count

    def build_summary(self, records: list[VoteRecord]) -> SummaryData:
        """Build statistics summary for output and chart rendering."""
        counts = self.count_options(records)
        modes, mode_count = self.get_modes(counts)
        least, least_count = self.get_least_options(counts)

        return SummaryData(
            total=len(records),
            counts=counts,
            modes=modes,
            mode_count=mode_count,
            least=least,
            least_count=least_count,
        )

    def get_all_rounds(self, csv_path: Path) -> list[str]:
        """Get list of all unique rounds in the CSV."""
        records = self.storage.read_votes(csv_path)
        return self.sort_round_names(list(set(record.round for record in records)))

    def compare_rounds(self, csv_path: Path) -> dict[str, SummaryData]:
        """Compare statistics across all rounds."""
        rounds = self.get_all_rounds(csv_path)
        comparison: dict[str, SummaryData] = {}

        for round_name in rounds:
            records = self.storage.read_votes(csv_path, round_filter=round_name)
            comparison[round_name] = self.build_summary(records)

        return comparison

    def get_mode_changes(self, csv_path: Path) -> list[str]:
        """Analyze mode changes across rounds."""
        comparison = self.compare_rounds(csv_path)
        rounds = self.get_all_rounds(csv_path)

        if len(rounds) < 2:
            return []

        changes: list[str] = []
        previous_modes: list[str] | None = None

        for round_name in rounds:
            current_modes = comparison[round_name].modes
            if previous_modes is not None and current_modes != previous_modes:
                previous_set = set(previous_modes)
                current_set = set(current_modes)
                if previous_set.isdisjoint(current_set):
                    changes.append(
                        f"{round_name}：眾數由 {'/'.join(previous_modes)} 變為 {'/'.join(current_modes)}"
                    )
            previous_modes = current_modes

        return changes

    def sort_records_for_detail(self, records: list[VoteRecord]) -> list[VoteRecord]:
        """Sort records for detail table with mode-first behavior inside each round."""
        round_mode_map: dict[str, set[str]] = {}
        records_by_round: dict[str, list[VoteRecord]] = defaultdict(list)

        for record in records:
            records_by_round[record.round].append(record)

        for round_name, round_records in records_by_round.items():
            summary = self.build_summary(round_records)
            round_mode_map[round_name] = set(summary.modes)

        return sorted(
            records,
            key=lambda record: (
                self.get_round_sort_key(record.round),
                0 if record.option in round_mode_map.get(record.round, set()) else 1,
                record.option,
                record.name,
            ),
        )

    def get_statistics(self, csv_path: Path) -> StatisticsData:
        """Get comprehensive statistics of all votes."""
        records = self.storage.read_votes(csv_path)
        summary = self.build_summary(records)

        unique_voters = len(set(r.name for r in records))
        unique_options = len(summary.counts)

        return StatisticsData(
            total=summary.total,
            counts=summary.counts,
            modes=summary.modes,
            mode_count=summary.mode_count,
            least=summary.least,
            least_count=summary.least_count,
            unique_voters=unique_voters,
            unique_options=unique_options,
            rounds=self.get_all_rounds(csv_path),
        )


_analysis_service = VoteAnalysisService()


def get_round_sort_key(round_name: str) -> tuple[int, int | str]:
    """Backward-compatible wrapper for VoteAnalysisService.get_round_sort_key."""
    return _analysis_service.get_round_sort_key(round_name)


def sort_round_names(round_names: list[str]) -> list[str]:
    """Backward-compatible wrapper for VoteAnalysisService.sort_round_names."""
    return _analysis_service.sort_round_names(round_names)


def sort_records(records: list[VoteRecord]) -> list[VoteRecord]:
    """Backward-compatible wrapper for VoteAnalysisService.sort_records."""
    return _analysis_service.sort_records(records)


def count_options(records: list[VoteRecord]) -> dict[str, int]:
    """Backward-compatible wrapper for VoteAnalysisService.count_options."""
    return _analysis_service.count_options(records)


def get_modes(counts: dict[str, int]) -> tuple[list[str], int]:
    """Backward-compatible wrapper for VoteAnalysisService.get_modes."""
    return _analysis_service.get_modes(counts)


def get_least_options(counts: dict[str, int]) -> tuple[list[str], int]:
    """Backward-compatible wrapper for VoteAnalysisService.get_least_options."""
    return _analysis_service.get_least_options(counts)


def build_summary(records: list[VoteRecord]) -> SummaryData:
    """Backward-compatible wrapper for VoteAnalysisService.build_summary."""
    return _analysis_service.build_summary(records)


def get_all_rounds(csv_path: Path) -> list[str]:
    """Backward-compatible wrapper for VoteAnalysisService.get_all_rounds."""
    return _analysis_service.get_all_rounds(csv_path)


def compare_rounds(csv_path: Path) -> dict[str, SummaryData]:
    """Backward-compatible wrapper for VoteAnalysisService.compare_rounds."""
    return _analysis_service.compare_rounds(csv_path)


def get_mode_changes(csv_path: Path) -> list[str]:
    """Backward-compatible wrapper for VoteAnalysisService.get_mode_changes."""
    return _analysis_service.get_mode_changes(csv_path)


def sort_records_for_detail(records: list[VoteRecord]) -> list[VoteRecord]:
    """Backward-compatible wrapper for VoteAnalysisService.sort_records_for_detail."""
    return _analysis_service.sort_records_for_detail(records)


def get_statistics(csv_path: Path) -> StatisticsData:
    """Backward-compatible wrapper for VoteAnalysisService.get_statistics."""
    return _analysis_service.get_statistics(csv_path)
