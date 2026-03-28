from __future__ import annotations

from typing import Any


def extract_editor_rows(editor_result: Any) -> list[dict[str, Any]]:
    if hasattr(editor_result, "to_dict"):
        data = editor_result.to_dict("records")
        return data if isinstance(data, list) else []
    if isinstance(editor_result, list):
        return [row for row in editor_result if isinstance(row, dict)]
    return []


def extract_editor_column_values(editor_result: Any, column_name: str) -> list[str]:
    rows = extract_editor_rows(editor_result)
    return [str(row.get(column_name, "")) for row in rows]
