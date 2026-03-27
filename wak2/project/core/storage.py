from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from project.types import VoteRecord

from .constants import (
    CSV_COL_NAME,
    CSV_COL_OPTION,
    CSV_COL_ROUND,
    CSV_HEADER_NO_ROUND,
    CSV_HEADER_WITH_ROUND,
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


def ensure_csv(csv_path: Path, with_round: bool = True) -> None:
    """Create the CSV file with header when it does not exist yet."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if csv_path.exists():
        return

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        if with_round:
            writer.writerow(CSV_HEADER_WITH_ROUND)
        else:
            writer.writerow(CSV_HEADER_NO_ROUND)


def read_votes(csv_path: Path, round_filter: Optional[str] = None) -> list[VoteRecord]:
    """Read vote records from CSV and return as VoteRecord list."""
    ensure_csv(csv_path)
    records: list[VoteRecord] = []

    try:
        with csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row is None:
                    continue

                round_val = (row.get(CSV_COL_ROUND) or DEFAULT_ROUND).strip() or DEFAULT_ROUND
                name = (row.get(CSV_COL_NAME) or "").strip()
                option = (row.get(CSV_COL_OPTION) or "").strip()

                if name and option and (round_filter is None or round_val == round_filter):
                    records.append(VoteRecord(name, option, round_val))
    except FileNotFoundError:
        return []

    return records


def add_vote(csv_path: Path, name: str, option: str, round_name: str = DEFAULT_ROUND) -> None:
    """Append one vote record into the CSV file."""
    name = name.strip()
    option = option.strip()
    round_name = round_name.strip() or DEFAULT_ROUND

    if not name:
        raise ValueError(ERR_NAME_EMPTY)

    if not option:
        raise ValueError(ERR_OPTION_EMPTY)

    existing_records = read_votes(csv_path)
    if any(record.name == name and record.round == round_name for record in existing_records):
        raise ValueError(ERR_DUPLICATE_VOTE)

    ensure_csv(csv_path)
    with csv_path.open("a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow([round_name, name, option])


def delete_votes_by_indices(csv_path: Path, indices: list[int]) -> int:
    """Delete multiple vote records by their indices."""
    if not indices:
        return 0

    records = read_votes(csv_path)
    delete_set = {index for index in indices if 0 <= index < len(records)}
    if not delete_set:
        return 0

    with csv_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(CSV_HEADER_WITH_ROUND)
        for index, record in enumerate(records):
            if index not in delete_set:
                writer.writerow([record.round, record.name, record.option])

    return len(delete_set)


def validate_vote_data(name: str, option: str) -> tuple[bool, str]:
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


def validate_round_name(round_name: str) -> tuple[bool, str]:
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
