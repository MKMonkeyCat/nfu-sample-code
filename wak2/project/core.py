from __future__ import annotations

import csv
import re
from collections import Counter
from pathlib import Path
from typing import NamedTuple, Optional


class VoteRecord(NamedTuple):
	"""Vote record with optional round/date support."""
	name: str
	option: str
	round: str = "default"


ROUND_OPTIONS = [f"day{i}" for i in range(1, 8)]
CUSTOM_ROUND_OPTION = "自訂輪次"
ROUND_NAME_PATTERN = re.compile(r"^[0-9A-Za-z\u4e00-\u9fff_-]+$")


def get_round_sort_key(round_name: str) -> tuple[int, int | str]:
	"""Build a stable sort key for round names."""
	if round_name == "單輪":
		return (0, 0)
	
	if round_name in ROUND_OPTIONS:
		return (1, ROUND_OPTIONS.index(round_name))
	
	return (2, round_name.lower())


def sort_round_names(round_names: list[str]) -> list[str]:
	"""Sort round names by the app's display order."""
	return sorted(round_names, key=get_round_sort_key)


def sort_records(records: list[VoteRecord]) -> list[VoteRecord]:
	"""Sort records by round, then by voter name and option."""
	return sorted(records, key=lambda record: (get_round_sort_key(record.round), record.name, record.option))


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


def add_vote(csv_path: Path, name: str, option: str, round_name: str = "default") -> None:
	"""Append one vote record into the CSV file.
	
	Args:
		csv_path: Path to the CSV file
		name: Voter's name (will be stripped and validated)
		option: Vote option (will be stripped and validated)
		round_name: Round/day identifier (will be stripped)
	
	Raises:
		ValueError: If name or option is empty after stripping
	"""
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


def read_votes(csv_path: Path, round_filter: Optional[str] = None) -> list[VoteRecord]:
	"""Read vote records from CSV and return as VoteRecord list.
	
	Args:
		csv_path: Path to the CSV file
		round_filter: Filter by specific round (None for all rounds)
	
	Returns:
		List of VoteRecord objects
	"""
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
				
				if name and option:
					if round_filter is None or round_val == round_filter:
						records.append(VoteRecord(name, option, round_val))
	except FileNotFoundError:
		return []
	
	return records


def get_all_rounds(csv_path: Path) -> list[str]:
	"""Get list of all unique rounds in the CSV."""
	records = read_votes(csv_path)
	return sort_round_names(list(set(record.round for record in records)))


def count_options(records: list[VoteRecord]) -> dict[str, int]:
	"""Count votes per option."""
	return dict(Counter(option for record in records for option in [record.option]))


def get_modes(counts: dict[str, int]) -> tuple[list[str], int]:
	"""Return all modes and their vote count.
	
	There may be multiple modes (tied for most votes).
	"""
	if not counts:
		return [], 0

	max_count = max(counts.values())
	modes = sorted([option for option, count in counts.items() if count == max_count])
	return modes, max_count


def get_least_options(counts: dict[str, int]) -> tuple[list[str], int]:
	"""Return all least-voted options and their vote count.
	
	There may be multiple least-voted options (tied for fewest votes).
	"""
	if not counts:
		return [], 0

	min_count = min(counts.values())
	least = sorted([option for option, count in counts.items() if count == min_count])
	return least, min_count


def build_summary(records: list[VoteRecord]) -> dict[str, object]:
	"""Build statistics summary for output and chart rendering."""
	counts = count_options(records)
	modes, mode_count = get_modes(counts)
	least, least_count = get_least_options(counts)

	return {
		"total": len(records),
		"counts": counts,
		"modes": modes,
		"mode_count": mode_count,
		"least": least,
		"least_count": least_count,
	}


def compare_rounds(csv_path: Path) -> dict[str, dict[str, object]]:
	"""Compare statistics across all rounds.
	
	Returns a dictionary with round names as keys and summaries as values.
	"""
	rounds = get_all_rounds(csv_path)
	comparison = {}
	
	for round_name in rounds:
		records = read_votes(csv_path, round_filter=round_name)
		comparison[round_name] = build_summary(records)
	
	return comparison


def get_mode_changes(csv_path: Path) -> list[str]:
	"""Analyze mode changes across rounds.
	
	Returns list of change descriptions.
	"""
	comparison = compare_rounds(csv_path)
	rounds = get_all_rounds(csv_path)
	
	if len(rounds) < 2:
		return []
	
	changes = []
	previous_modes = None
	
	for round_name in rounds:
		current_modes = comparison[round_name]["modes"]
		if previous_modes is not None and current_modes != previous_modes:
			previous_set = set(previous_modes)
			current_set = set(current_modes)
			if previous_set.isdisjoint(current_set):
				changes.append(
					f"{round_name}：眾數由 {'/'.join(previous_modes)} 變為 {'/'.join(current_modes)}"
				)
		previous_modes = current_modes
	
	return changes


# ============== 驗證與工具函數 ==============

def validate_vote_data(name: str, option: str) -> tuple[bool, str]:
	"""Validate vote input data.
	
	Args:
		name: Voter's name
		option: Vote option
	
	Returns:
		Tuple of (is_valid, error_message)
	"""
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


def get_statistics(csv_path: Path) -> dict[str, object]:
	"""Get comprehensive statistics of all votes.
	
	Args:
		csv_path: Path to the CSV file
	
	Returns:
		Dictionary with comprehensive statistics
	"""
	records = read_votes(csv_path)
	summary = build_summary(records)
	
	unique_voters = len(set(r.name for r in records))
	unique_options = len(summary["counts"])
	
	return {
		**summary,
		"unique_voters": unique_voters,
		"unique_options": unique_options,
		"rounds": get_all_rounds(csv_path),
	}


def delete_votes_by_indices(csv_path: Path, indices: list[int]) -> int:
	"""Delete multiple vote records by their indices.
	
	Args:
		csv_path: Path to the CSV file
		indices: Record indices to delete (0-based)
	
	Returns:
		Number of deleted records
	"""
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

