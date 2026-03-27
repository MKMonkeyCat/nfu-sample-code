from __future__ import annotations

import csv
from collections import Counter
from pathlib import Path


Record = tuple[str, str]


def ensure_csv(csv_path: Path) -> None:
	"""Create the CSV file with header when it does not exist yet."""
	csv_path.parent.mkdir(parents=True, exist_ok=True)
	if not csv_path.exists():
		with csv_path.open("w", newline="", encoding="utf-8") as file:
			writer = csv.writer(file)
			writer.writerow(["姓名", "選項"])


def add_vote(csv_path: Path, name: str, option: str) -> None:
	"""Append one vote record into the CSV file."""
	ensure_csv(csv_path)
	with csv_path.open("a", newline="", encoding="utf-8") as file:
		writer = csv.writer(file)
		writer.writerow([name.strip(), option.strip()])


def read_votes(csv_path: Path) -> list[Record]:
	"""Read vote records from CSV and return as (name, option) list."""
	ensure_csv(csv_path)
	records: list[Record] = []
	with csv_path.open("r", newline="", encoding="utf-8") as file:
		reader = csv.DictReader(file)
		for row in reader:
			name = (row.get("姓名") or "").strip()
			option = (row.get("選項") or "").strip()
			if name and option:
				records.append((name, option))
	return records


def count_options(records: list[Record]) -> dict[str, int]:
	"""Count votes per option."""
	return dict(Counter(option for _, option in records))


def get_modes(counts: dict[str, int]) -> tuple[list[str], int]:
	"""Return all modes and their vote count."""
	if not counts:
		return [], 0

	max_count = max(counts.values())
	modes = sorted([option for option, count in counts.items() if count == max_count])
	return modes, max_count


def get_least_options(counts: dict[str, int]) -> tuple[list[str], int]:
	"""Return all least-voted options and their vote count."""
	if not counts:
		return [], 0

	min_count = min(counts.values())
	least = sorted([option for option, count in counts.items() if count == min_count])
	return least, min_count


def build_summary(records: list[Record]) -> dict[str, object]:
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
