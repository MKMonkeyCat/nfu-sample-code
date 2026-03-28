from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import (
    Any,
    Generic,
    Iterable,
    Mapping,
    Sequence,
    TypeVar,
    get_args,
    get_origin,
)

import _csv

T = TypeVar("T")
_MISSING = object()


class CsvName:
    """Marker for mapping an attribute to a specific CSV column name."""

    def __init__(self, column_name: str, default: Any = _MISSING) -> None:
        if not column_name or not column_name.strip():
            raise ValueError("column_name cannot be empty")

        self.column_name = column_name.strip()
        self.default = default


def name(column_name: str, default: Any = _MISSING) -> Any:
    """Declare CSV column alias for a class attribute.

    Example:
        class Test:
            a: str
            b: int
            c: list[str] = name("xxx")
    """

    return CsvName(column_name=column_name, default=default)


@dataclass(frozen=True)
class CsvField:
    attr_name: str
    column_name: str
    annotation: Any
    has_default: bool
    default: Any


def _get_model_annotations(model_cls: type[Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    for base in reversed(model_cls.__mro__):
        annotations = getattr(base, "__annotations__", None)
        if annotations:
            merged.update(annotations)
    return merged


def get_model_fields(model_cls: type[Any]) -> list[CsvField]:
    """Resolve CSV field definitions from a model class."""

    annotations = _get_model_annotations(model_cls)
    fields: list[CsvField] = []

    for attr_name, annotation in annotations.items():
        if attr_name.startswith("_"):
            continue

        value = getattr(model_cls, attr_name, _MISSING)
        column_name = attr_name
        has_default = False
        default = _MISSING

        if isinstance(value, CsvName):
            column_name = value.column_name
            if value.default is not _MISSING:
                has_default = True
                default = value.default
        elif value is not _MISSING:
            has_default = True
            default = value

        fields.append(
            CsvField(
                attr_name=attr_name,
                column_name=column_name,
                annotation=annotation,
                has_default=has_default,
                default=default,
            )
        )

    return fields


def _unwrap_optional(annotation: Any) -> tuple[Any, bool]:
    origin = get_origin(annotation)
    if origin is None:
        return annotation, False

    args = get_args(annotation)
    if origin in (set, tuple, list, dict):
        return annotation, False

    if str(origin).endswith("Union"):
        non_none = [arg for arg in args if arg is not type(None)]
        if len(non_none) == 1 and len(non_none) != len(args):
            return non_none[0], True

    return annotation, False


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Cannot parse bool value: {value}")


def _cast_value(text: str, annotation: Any, *, has_default: bool, default: Any) -> Any:
    raw = text.strip()

    if raw == "":
        if has_default:
            return default
        annotation, is_optional = _unwrap_optional(annotation)
        if is_optional:
            return None
        if annotation is str:
            return ""
        raise ValueError("Missing value for non-optional field")

    annotation, _ = _unwrap_optional(annotation)
    origin = get_origin(annotation)
    args = get_args(annotation)

    if annotation is str:
        return raw
    if annotation is int:
        return int(raw)
    if annotation is float:
        return float(raw)
    if annotation is bool:
        return _parse_bool(raw)

    if origin is list:
        item_type = args[0] if args else str
        loaded = json.loads(raw)
        if not isinstance(loaded, list):
            raise ValueError("List field must be stored as a JSON array")
        return [_cast_value(str(item), item_type, has_default=False, default=_MISSING) for item in loaded]

    if callable(annotation):
        return annotation(raw)

    return raw


def _to_csv_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _build_instance(model_cls: type[T], values: Mapping[str, Any]) -> T:
    try:
        return model_cls(**values)
    except TypeError:
        obj = model_cls.__new__(model_cls)
        for key, value in values.items():
            setattr(obj, key, value)
        return obj


class CSVManager(Generic[T]):
    """A class-based CSV manager with typed model mapping."""

    def __init__(self, csv_path: str | Path, model_cls: type[T]) -> None:
        self.csv_path = Path(csv_path)
        self.model_cls = model_cls
        self.fields = get_model_fields(model_cls)

        if not self.fields:
            raise ValueError("model class must define annotated fields")

    @property
    def header(self) -> list[str]:
        return [field.column_name for field in self.fields]

    def remove_file(self) -> None:
        if self.csv_path.exists():
            self.csv_path.unlink()

    def ensure_file(self) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        if self.csv_path.exists():
            return
        with self.csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = _csv.writer(file)
            writer.writerow(self.header)

    def read_all(self) -> list[T]:
        self.ensure_file()
        items: list[T] = []

        with self.csv_path.open("r", newline="", encoding="utf-8") as file:
            reader = _csv.reader(file)
            header = next(reader, None)
            if header is None:
                return items

            index_map = {col: idx for idx, col in enumerate(header)}
            for raw_row in reader:
                row: dict[str, str] = {}
                for col_name, idx in index_map.items():
                    row[col_name] = raw_row[idx] if idx < len(raw_row) else ""

                values: dict[str, Any] = {}
                for field in self.fields:
                    cell = row.get(field.column_name, "")
                    values[field.attr_name] = _cast_value(
                        cell or "",
                        field.annotation,
                        has_default=field.has_default,
                        default=field.default,
                    )

                items.append(_build_instance(self.model_cls, values))

        return items

    def append(self, item: T) -> None:
        self.ensure_file()
        row = self._to_row(item)
        with self.csv_path.open("a", newline="", encoding="utf-8") as file:
            writer = _csv.writer(file)
            writer.writerow([row.get(col, "") for col in self.header])

    def append_many(self, items: Iterable[T]) -> None:
        self.ensure_file()
        with self.csv_path.open("a", newline="", encoding="utf-8") as file:
            writer = _csv.writer(file)
            for item in items:
                row = self._to_row(item)
                writer.writerow([row.get(col, "") for col in self.header])

    def write_all(self, items: Sequence[T]) -> None:
        self.csv_path.parent.mkdir(parents=True, exist_ok=True)
        with self.csv_path.open("w", newline="", encoding="utf-8") as file:
            writer = _csv.writer(file)
            writer.writerow(self.header)
            for item in items:
                row = self._to_row(item)
                writer.writerow([row.get(col, "") for col in self.header])

    def _to_row(self, item: T) -> dict[str, str]:
        row: dict[str, str] = {}
        for field in self.fields:
            value = getattr(item, field.attr_name, _MISSING)
            if value is _MISSING:
                if field.has_default:
                    value = field.default
                else:
                    raise ValueError(f"Missing field value: {field.attr_name}")
            row[field.column_name] = _to_csv_text(value)
        return row


__all__ = ["CSVManager", "CsvName", "CsvField", "get_model_fields", "name"]
