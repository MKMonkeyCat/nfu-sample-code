from __future__ import annotations

from collections.abc import Iterable


def normalize_option_text(text: str) -> str:
    return " ".join(text.strip().split())


def normalize_option_list(options: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for option in options:
        item = normalize_option_text(option)
        if item and item not in seen:
            normalized.append(item)
            seen.add(item)
    return normalized


def normalize_option_set(options: Iterable[str]) -> set[str]:
    return set(normalize_option_list(options))


def parse_options_text(raw_text: str) -> set[str]:
    raw = raw_text.replace("\n", ",").replace("、", ",").replace("，", ",")
    return set(normalize_option_list(raw.split(",")))
