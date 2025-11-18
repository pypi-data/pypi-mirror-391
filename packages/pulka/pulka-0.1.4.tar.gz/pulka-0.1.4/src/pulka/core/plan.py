"""Immutable query plan shared by the core engine and sheets."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable
from dataclasses import dataclass, replace
from typing import Any


def normalized_columns_key(columns: Iterable[str]) -> str:
    """Return a stable signature for a sequence of columns."""

    return "\u241f".join(columns)


@dataclass(frozen=True, slots=True)
class QueryPlan:
    """Immutable description of how to transform a LazyFrame for display."""

    filters: tuple[str, ...] = ()
    sql_filter: str | None = None
    sort: tuple[tuple[str, bool], ...] = ()  # (column, desc)
    projection: tuple[str, ...] = ()
    search_text: str | None = None
    limit: int | None = None
    offset: int = 0

    def with_limit(self, limit: int | None) -> QueryPlan:
        return replace(self, limit=limit)

    def with_offset(self, offset: int) -> QueryPlan:
        return replace(self, offset=offset)

    def with_projection(self, projection: Iterable[str]) -> QueryPlan:
        return replace(self, projection=tuple(projection))

    def projection_or(self, fallback: Iterable[str]) -> tuple[str, ...]:
        """Return the plan projection or ``fallback`` when not specified."""

        if self.projection:
            return self.projection
        return tuple(fallback)

    def sort_columns(self) -> tuple[str, ...]:
        """Return the ordered list of sort columns."""

        return tuple(column for column, _ in self.sort)

    def sort_descending(self) -> tuple[bool, ...]:
        """Return the tuple of descending flags for the configured sort."""

        return tuple(desc for _, desc in self.sort)

    def snapshot_payload(self) -> dict[str, Any]:
        """Return a JSON-serialisable payload describing the plan."""

        return {
            "filters": list(self.filters),
            "sql_filter": self.sql_filter,
            "sort": list(self.sort),
            "projection": list(self.projection),
            "search_text": self.search_text,
            "limit": self.limit,
            "offset": self.offset,
        }

    def snapshot(self) -> dict[str, Any]:
        """Return the payload and a stable hash for recorder snapshots."""

        payload = self.snapshot_payload()
        serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        digest = hashlib.sha1(serialized.encode("utf-8")).hexdigest()
        return {"hash": digest, "plan": payload}


__all__ = ["QueryPlan", "normalized_columns_key"]
