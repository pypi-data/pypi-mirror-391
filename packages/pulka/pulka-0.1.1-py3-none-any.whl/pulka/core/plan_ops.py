"""Pure helpers to derive new :class:`~pulka.core.plan.QueryPlan` instances."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import replace

from .errors import PlanError
from .plan import QueryPlan


def reset(plan: QueryPlan | None = None) -> QueryPlan:
    """Return an empty plan, ignoring ``plan`` when provided."""

    return QueryPlan()


def set_filter(plan: QueryPlan, filter_text: str | None) -> QueryPlan:
    """Return ``plan`` with ``filter_text`` applied as the expression filter."""

    if filter_text is None:
        if not plan.filters and plan.sql_filter is None:
            return plan
        return replace(plan, filters=(), sql_filter=None)

    text = filter_text.strip()
    if not text:
        if not plan.filters and plan.sql_filter is None:
            return plan
        return replace(plan, filters=(), sql_filter=None)

    if plan.filters == (text,) and plan.sql_filter is None:
        return plan

    return replace(plan, filters=(text,), sql_filter=None)


def set_sql_filter(plan: QueryPlan, where_clause: str | None) -> QueryPlan:
    """Return ``plan`` with ``where_clause`` applied as an SQL filter."""

    if where_clause is None:
        if not plan.filters and plan.sql_filter is None:
            return plan
        return replace(plan, filters=(), sql_filter=None)

    where = where_clause.strip()
    if not where:
        if not plan.filters and plan.sql_filter is None:
            return plan
        return replace(plan, filters=(), sql_filter=None)

    if plan.sql_filter == where and not plan.filters:
        return plan

    return replace(plan, filters=(), sql_filter=where)


def set_search(plan: QueryPlan, text: str | None) -> QueryPlan:
    """Return ``plan`` with ``text`` recorded for search."""

    if text is None:
        search = None
    else:
        stripped = text.strip()
        search = stripped or None

    if search == plan.search_text:
        return plan

    return replace(plan, search_text=search)


def toggle_sort(
    plan: QueryPlan, column: str, cycle: Iterable[str] = ("asc", "desc", "none")
) -> QueryPlan:
    """Toggle sort on ``column`` cycling through ``cycle`` states."""

    if not column:
        return plan

    states = tuple(state.lower() for state in cycle)
    if not states:
        return plan

    current_entries = list(plan.sort)
    for name, desc in current_entries:
        if name == column:
            current_state = "desc" if desc else "asc"
            break
    else:
        current_state = None

    if current_state is None:
        next_state = states[0]
    else:
        try:
            state_pos = states.index(current_state)
        except ValueError:
            state_pos = -1
        next_state = states[(state_pos + 1) % len(states)]

    if next_state not in {"asc", "desc", "none"}:
        msg = f"unsupported sort state: {next_state!r}"
        raise PlanError(msg)

    remaining = [entry for entry in current_entries if entry[0] != column]
    if next_state == "asc":
        new_sort = tuple([(column, False)] + remaining)
    elif next_state == "desc":
        new_sort = tuple([(column, True)] + remaining)
    else:  # next_state == "none"
        new_sort = tuple(remaining)

    if tuple(new_sort) == plan.sort:
        return plan

    return replace(plan, sort=new_sort)


def clear_sort(plan: QueryPlan) -> QueryPlan:
    """Return ``plan`` with any sort removed."""

    if not plan.sort:
        return plan

    return replace(plan, sort=())


def set_projection(plan: QueryPlan, columns: Iterable[str]) -> QueryPlan:
    """Return ``plan`` constrained to ``columns``."""

    projection: list[str] = []
    for name in columns:
        if name not in projection:
            projection.append(name)

    new_projection = tuple(projection)
    if new_projection == plan.projection:
        return plan

    return replace(plan, projection=new_projection)


def reorder_columns(plan: QueryPlan, columns: Iterable[str]) -> QueryPlan:
    """Return ``plan`` with projected columns reordered according to ``columns``."""

    desired = []
    seen: set[str] = set()
    for name in columns:
        if name in seen:
            continue
        desired.append(name)
        seen.add(name)

    current_projection = list(plan.projection)
    if not current_projection:
        current_projection = desired
    else:
        current_projection = [col for col in current_projection if col not in seen]
        desired.extend(current_projection)

    new_projection = tuple(desired)
    if new_projection == plan.projection:
        return plan

    return replace(plan, projection=new_projection)


def set_limit(plan: QueryPlan, limit: int | None, offset: int = 0) -> QueryPlan:
    """Return ``plan`` with ``limit``/``offset`` applied."""

    if limit is None:
        normalized_limit: int | None = None
    else:
        coerced = int(limit)
        normalized_limit = None if coerced < 0 else coerced

    normalized_offset = max(0, int(offset))

    if normalized_limit == plan.limit and normalized_offset == plan.offset:
        return plan

    return replace(plan, limit=normalized_limit, offset=normalized_offset)


__all__ = [
    "clear_sort",
    "reset",
    "set_filter",
    "set_limit",
    "set_projection",
    "reorder_columns",
    "set_search",
    "set_sql_filter",
    "toggle_sort",
]
