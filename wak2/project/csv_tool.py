from __future__ import annotations

import csv
import json
from dataclasses import MISSING, dataclass, field, fields
from pathlib import Path
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    Mapping,
    ParamSpec,
    TypeVar,
    cast,
    overload,
)

T = TypeVar("T")
P = ParamSpec("P")
FT = TypeVar("FT")

_MISSING = object()
_CSV_METADATA_KEY = "__csv_column_name__"


def csv_field(
    column_name: str,
    *,
    default: FT | Any = MISSING,
    default_factory: Any = MISSING,
    init: bool = True,
    repr: bool = True,  # pylint: disable=redefined-builtin
    hash: bool | None = None,  # pylint: disable=redefined-builtin
    compare: bool = True,
    metadata: Mapping[Any, Any] | None = None,
    kw_only: Any = MISSING,
) -> FT:
    actual_metadata = dict(metadata) if metadata else {}
    actual_metadata[_CSV_METADATA_KEY] = column_name.strip()

    return cast(
        FT,
        field(  # pylint: disable=invalid-field-call
            default=default,
            default_factory=default_factory,
            init=init,
            repr=repr,
            hash=hash,
            compare=compare,
            metadata=actual_metadata,
            kw_only=kw_only,
        ),
    )


@dataclass(frozen=True)
class CsvFieldInfo:
    attr_name: str
    column_name: str
    annotation: Any
    has_default: bool
    default: Any
    default_factory: Any = _MISSING


def get_model_fields(model_cls: type) -> list[CsvFieldInfo]:
    res: list[CsvFieldInfo] = []

    for f in fields(model_cls):
        if f.name.startswith("_"):
            continue

        column_name = f.metadata.get(_CSV_METADATA_KEY, f.name)
        has_default = f.default is not MISSING or f.default_factory is not MISSING

        res.append(
            CsvFieldInfo(
                attr_name=f.name,
                column_name=column_name,
                annotation=f.type,
                has_default=has_default,
                default=f.default,
                default_factory=f.default_factory,
            )
        )
    return res


def _to_csv_text(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (dict, list, tuple, set, frozenset)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _cast_value(text: str, field_info: CsvFieldInfo) -> Any:
    raw = text.strip()
    if raw == "" and field_info.has_default:
        return field_info.default if field_info.default is not MISSING else field_info.default_factory()
    return raw


class CSVManager(Generic[T, P]):
    def __init__(self, csv_path: str | Path, model_cls: Callable[P, T]) -> None:
        self.csv_path = Path(csv_path)
        self.model_cls = cast(type[T], model_cls)
        self.fields = get_model_fields(self.model_cls)

    @property
    def header(self) -> list[str]:
        return [f.column_name for f in self.fields]

    def ensure_file(self) -> None:
        if not self.csv_path.exists():
            self.csv_path.parent.mkdir(parents=True, exist_ok=True)
            with self.csv_path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(self.header)

    def _make_row(self, item: T) -> list[str]:
        return [_to_csv_text(getattr(item, f.attr_name)) for f in self.fields]

    @overload
    def append(self, item: T, /) -> None: ...
    @overload
    def append(self, items: Iterable[T], /) -> None: ...
    @overload
    def append(self, *args: P.args, **kwargs: P.kwargs) -> None: ...

    def append(self, *args: Any, **kwargs: Any) -> None:
        items_to_write: list[T] = []

        if len(args) == 1 and isinstance(args[0], self.model_cls):
            items_to_write = [args[0]]
        elif (
            len(args) == 1
            and isinstance(args[0], (list, tuple))
            and args[0]
            and isinstance(args[0][0], self.model_cls)
        ):
            items_to_write = list(args[0])
        else:
            new_item = self.model_cls(*args, **kwargs)
            items_to_write = [new_item]

        self.ensure_file()
        with self.csv_path.open("a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            for item in items_to_write:
                writer.writerow(self._make_row(item))

    def read_all(self) -> list[T]:
        self.ensure_file()
        items: list[T] = []
        with self.csv_path.open("r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            file_header = next(reader, None)
            if not file_header:
                return items
            index_map = {col: idx for idx, col in enumerate(file_header)}
            for raw_row in reader:
                values: dict[str, Any] = {}
                for f_info in self.fields:
                    idx = index_map.get(f_info.column_name)
                    cell = raw_row[idx] if idx is not None and idx < len(raw_row) else ""
                    values[f_info.attr_name] = _cast_value(cell, f_info)
                items.append(self.model_cls(**values))
        return items

    def __repr__(self) -> str:
        return f"CSVManager(path={self.csv_path}, model={self.model_cls.__name__})"


__all__ = ["CSVManager", "csv_field"]
