from __future__ import annotations

import csv
from pathlib import Path
from typing import Optional

from project.types import VoteRecord

from .constants import ROUND_NAME_PATTERN, ROUND_OPTIONS


def ensure_csv(csv_path: Path, with_round: bool = True) -> None:
    """Create the CSV file with header when it does not exist yet."""
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        with csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if with_round:
                writer.writerow(["輪次", "姓名", "選項"])
            else:
                writer.writerow(["姓名", "選項"])


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
                round_val = (row.get("輪次") or "default").strip() or "default"
                name = (row.get("姓名") or "").strip()
                option = (row.get("選項") or "").strip()

                if name and option and (round_filter is None or round_val == round_filter):
                    records.append(VoteRecord(name, option, round_val))
    except FileNotFoundError:
        return []

    return records


def add_vote(csv_path: Path, name: str, option: str, round_name: str = "default") -> None:
    """Append one vote record into the CSV file."""
    name = name.strip()
    option = option.strip()
    round_name = round_name.strip() or "default"

    if not name:
        raise ValueError("姓名不能為空")
    if not option:
        raise ValueError("選項不能為空")

    existing_records = read_votes(csv_path)
    if any(record.name == name and record.round == round_name for record in existing_records):
        raise ValueError("同一位投票者在同一輪次只能投一次")

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
        writer.writerow(["輪次", "姓名", "選項"])
        for index, record in enumerate(records):
            if index not in delete_set:
                writer.writerow([record.round, record.name, record.option])

    return len(delete_set)


def validate_vote_data(name: str, option: str) -> tuple[bool, str]:
    """Validate vote input data."""
    if not name or not name.strip():
        return False, "姓名不能為空"
    if not option or not option.strip():
        return False, "選項不能為空"
    if len(name.strip()) > 50:
        return False, "姓名長度不能超過50字"
    if len(option.strip()) > 50:
        return False, "選項長度不能超過50字"
    return True, ""


def validate_round_name(round_name: str) -> tuple[bool, str]:
    """Validate round names for multi-round mode."""
    normalized = round_name.strip()

    if not normalized:
        return False, "輪次名稱不能為空"
    if normalized in ROUND_OPTIONS:
        return True, ""
    if len(normalized) > 20:
        return False, "自訂輪次名稱不能超過20字"
    if not ROUND_NAME_PATTERN.fullmatch(normalized):
        return False, "自訂輪次只允許中文、英文、數字、-、_"

    return True, ""
