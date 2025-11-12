from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional, Union


@dataclass
class ColumnStats:
    """Column statistics such as type, null counts, and min/max values."""

    name: str
    type: str
    null_count: int
    num_values: int
    min: Optional[Union[int, float, str]] = None
    max: Optional[Union[int, float, str]] = None
    metadata: Optional[dict] = None

    @classmethod
    def from_dict(cls, data: Union[ColumnStats, dict]) -> ColumnStats:
        """Coerce a mapping into a ColumnStats instance."""

        if isinstance(data, cls):
            return data
        if not isinstance(data, dict):
            raise TypeError(f"Cannot initialise ColumnStats from {type(data)!r}")
        return cls(**data)

    def dict(self) -> dict:
        """Return a plain dictionary representation."""

        return asdict(self)


@dataclass
class TableStats:
    """Table statistics including row counts, size, and per-column stats."""

    num_rows: int
    size: int
    columns: list[ColumnStats] = field(default_factory=list)
    _table: Any = field(default=None, init=False, repr=False, compare=False)

    def __post_init__(self):
        self.columns = [ColumnStats.from_dict(column) for column in self.columns or []]

    @classmethod
    def from_dict(cls, data: Union[TableStats, dict, None]) -> TableStats:
        """Coerce a mapping into a TableStats instance."""

        if isinstance(data, cls):
            return data
        if not isinstance(data, dict):
            raise TypeError(f"Cannot initialise TableStats from {type(data)!r}")

        return cls(
            num_rows=data.get("num_rows", 0),
            size=data.get("size", 0),
            columns=data.get("columns", []),
        )

    def dict(self) -> dict:
        """Return a plain dictionary representation."""

        return {
            "num_rows": self.num_rows,
            "size": self.size,
            "columns": [column.dict() for column in self.columns],
        }
