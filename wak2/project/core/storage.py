from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from project.csv import CSVManager
from project.csv import name as csv_name
from project.types import VoteRecord

from .constants import (
    CSV_COL_NAME,
    CSV_COL_OPTION,
    CSV_COL_ROUND,
    DEFAULT_ROUND,
    ERR_CUSTOM_ROUND_INVALID,
    ERR_CUSTOM_ROUND_TOO_LONG,
    ERR_DUPLICATE_VOTE,
    ERR_NAME_EMPTY,
    ERR_NAME_TOO_LONG,
    ERR_OPTION_EMPTY,
    ERR_OPTION_TOO_LONG,
    ERR_ROUND_EMPTY,
    MAX_CUSTOM_ROUND_LENGTH,
    MAX_NAME_LENGTH,
    MAX_OPTION_LENGTH,
    ROUND_NAME_PATTERN,
    ROUND_OPTIONS,
)


@dataclass
class VoteCsvRow:
    round_name: str = csv_name(CSV_COL_ROUND, default=DEFAULT_ROUND)
    name: str = csv_name(CSV_COL_NAME)
    option: str = csv_name(CSV_COL_OPTION)


class VoteStorageService:
    """Encapsulates CSV persistence and validation for vote records."""

    def _manager(self, csv_path: Path) -> CSVManager[VoteCsvRow]:
        return CSVManager(csv_path, VoteCsvRow)

    def read_votes(self, csv_path: Path, round_filter: Optional[str] = None) -> list[VoteRecord]:
        """Read vote records from CSV and return as VoteRecord list."""
        try:
            rows = self._manager(csv_path).read_all()
        except FileNotFoundError:
            return []

        records: list[VoteRecord] = []
        for row in rows:
            round_val = (row.round_name or DEFAULT_ROUND).strip() or DEFAULT_ROUND
            voter_name = (row.name or "").strip()
            option = (row.option or "").strip()

            if voter_name and option and (round_filter is None or round_val == round_filter):
                records.append(VoteRecord(voter_name, option, round_val))

        return records

    def add_vote(self, csv_path: Path, name: str, option: str, round_name: str = DEFAULT_ROUND) -> None:
        """Append one vote record into the CSV file."""
        name = name.strip()
        option = option.strip()
        round_name = round_name.strip() or DEFAULT_ROUND

        if not name:
            raise ValueError(ERR_NAME_EMPTY)

        if not option:
            raise ValueError(ERR_OPTION_EMPTY)

        existing_records = self.read_votes(csv_path)
        if any(record.name == name and record.round == round_name for record in existing_records):
            raise ValueError(ERR_DUPLICATE_VOTE)

        self._manager(csv_path).append(VoteCsvRow(round_name=round_name, name=name, option=option))

    def delete_votes_by_indices(self, csv_path: Path, indices: list[int]) -> int:
        """Delete multiple vote records by their indices."""
        if not indices:
            return 0

        records = self.read_votes(csv_path)
        delete_set = {index for index in indices if 0 <= index < len(records)}
        if not delete_set:
            return 0

        remaining_rows = [
            VoteCsvRow(round_name=record.round, name=record.name, option=record.option)
            for index, record in enumerate(records)
            if index not in delete_set
        ]
        self._manager(csv_path).write_all(remaining_rows)

        return len(delete_set)

    def validate_vote_data(self, name: str, option: str) -> tuple[bool, str]:
        """Validate vote input data."""
        if not name or not name.strip():
            return False, ERR_NAME_EMPTY

        if not option or not option.strip():
            return False, ERR_OPTION_EMPTY

        if len(name.strip()) > MAX_NAME_LENGTH:
            return False, ERR_NAME_TOO_LONG

        if len(option.strip()) > MAX_OPTION_LENGTH:
            return False, ERR_OPTION_TOO_LONG

        return True, ""

    def validate_round_name(self, round_name: str) -> tuple[bool, str]:
        """Validate round names for multi-round mode."""
        normalized = round_name.strip()

        if not normalized:
            return False, ERR_ROUND_EMPTY

        if normalized in ROUND_OPTIONS:
            return True, ""

        if len(normalized) > MAX_CUSTOM_ROUND_LENGTH:
            return False, ERR_CUSTOM_ROUND_TOO_LONG

        if not ROUND_NAME_PATTERN.fullmatch(normalized):
            return False, ERR_CUSTOM_ROUND_INVALID

        return True, ""


_storage_service = VoteStorageService()


def read_votes(csv_path: Path, round_filter: Optional[str] = None) -> list[VoteRecord]:
    """Backward-compatible wrapper for VoteStorageService.read_votes."""
    return _storage_service.read_votes(csv_path, round_filter)


def add_vote(csv_path: Path, name: str, option: str, round_name: str = DEFAULT_ROUND) -> None:
    """Backward-compatible wrapper for VoteStorageService.add_vote."""
    _storage_service.add_vote(csv_path, name, option, round_name)


def delete_votes_by_indices(csv_path: Path, indices: list[int]) -> int:
    """Backward-compatible wrapper for VoteStorageService.delete_votes_by_indices."""
    return _storage_service.delete_votes_by_indices(csv_path, indices)


def validate_vote_data(name: str, option: str) -> tuple[bool, str]:
    """Backward-compatible wrapper for VoteStorageService.validate_vote_data."""
    return _storage_service.validate_vote_data(name, option)


def validate_round_name(round_name: str) -> tuple[bool, str]:
    """Backward-compatible wrapper for VoteStorageService.validate_round_name."""
    return _storage_service.validate_round_name(round_name)
