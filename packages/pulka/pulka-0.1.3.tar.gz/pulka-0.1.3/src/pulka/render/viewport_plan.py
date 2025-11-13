"""Viewport planning for tabular renders.

This module computes a UI-neutral representation of the visible portion of a
table so renderers (Rich, prompt_toolkit, headless) can share sizing and cell
formatting logic without duplicating width calculations.
"""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Literal

from ..core.engine.contracts import TableSlice
from ..core.formatting import _is_numeric_dtype
from .decimal_alignment import apply_decimal_alignment, compute_decimal_alignment
from .display import (
    display_width,
    pad_left_display,
    pad_right_display,
    truncate_grapheme_safe,
)

if TYPE_CHECKING:
    from ..core.viewer import Viewer


@dataclass(slots=True)
class Cell:
    """Rendered cell payload for a viewport column/row intersection."""

    text: str
    role: Literal["header", "body"]
    active_row: bool
    active_col: bool
    active_cell: bool
    numeric: bool
    is_null: bool


@dataclass(slots=True)
class _ColumnMeta:
    """Internal helper metadata for planning column layout."""

    name: str
    dtype: Any
    is_numeric: bool
    has_nulls: bool
    min_width: int
    original_width: int
    header_active: bool
    is_sorted: bool
    is_frozen: bool


@dataclass(slots=True)
class ColumnPlan:
    """Metadata for a visible column within the viewport."""

    name: str
    width: int
    min_width: int
    original_width: int
    is_numeric: bool
    has_nulls: bool
    header_active: bool
    is_sorted: bool


@dataclass(slots=True)
class ViewportPlan:
    """Collection of visible cells and sizing metadata for a table viewport."""

    columns: list[ColumnPlan]
    frozen_boundary_idx: int | None
    rows: int
    row_offset: int
    col_offset: int
    cells: list[list[Cell]]
    active_row_index: int


def fetch_visible_for_viewer(viewer: Viewer) -> TableSlice:
    """Return the visible slice for ``viewer`` honouring column visibility."""

    if hasattr(viewer, "visible_cols") and viewer.visible_cols:
        cols = list(viewer.visible_cols)
    else:
        cols = list(viewer.columns)
    return viewer.get_visible_table_slice(cols)


def _table_border_overhead(column_count: int) -> int:
    """Return the width contribution of table borders and separators."""

    if column_count <= 0:
        return 0
    return column_count + 1


def _shrink_widths_to_fit(
    widths: list[int],
    minimums: list[int],
    target_total: int,
) -> list[int]:
    """Reduce widths while respecting per-column minimums."""

    if not widths or target_total <= 0:
        return widths

    total = sum(widths)
    if total <= target_total:
        return widths

    overflow = total - target_total
    while overflow > 0:
        slack = [(idx, w - minimums[idx]) for idx, w in enumerate(widths)]
        slack = [item for item in slack if item[1] > 0]
        if not slack:
            break

        share = max(1, overflow // len(slack))
        for idx, available in slack:
            delta = min(available, share, overflow)
            if delta <= 0:
                continue
            widths[idx] -= delta
            overflow -= delta
            if overflow <= 0:
                break

    return widths


def _allocate_widths(
    widths: list[int],
    caps: list[int],
    weights: list[int],
    remaining: int,
) -> int:
    """Grow ``widths`` toward ``caps`` using ``weights`` while columns remain."""

    if remaining <= 0:
        return 0

    size = len(widths)
    while remaining > 0:
        eligible = [idx for idx in range(size) if widths[idx] < caps[idx]]
        if not eligible:
            break

        total_weight = sum(max(0, weights[idx]) for idx in eligible)
        if total_weight <= 0:
            total_weight = len(eligible)
            weight_map = dict.fromkeys(eligible, 1)
        else:
            weight_map = {idx: max(0, weights[idx]) for idx in eligible}

        allocated = 0
        for idx in eligible:
            cap = caps[idx]
            if widths[idx] >= cap:
                continue
            weight = weight_map[idx] or 0
            if weight <= 0:
                continue
            share = int(remaining * weight / total_weight)
            gap = cap - widths[idx]
            if share <= 0:
                share = 1
            share = min(gap, share)
            if share <= 0:
                continue
            widths[idx] += share
            remaining -= share
            allocated += share
            if remaining <= 0:
                break

        if allocated == 0:
            # Fallback: allocate single columns in priority order to avoid stalls.
            eligible.sort(key=lambda idx: (-(weight_map[idx] or 0), idx))
            for idx in eligible:
                if remaining <= 0:
                    break
                if widths[idx] >= caps[idx]:
                    continue
                widths[idx] += 1
                remaining -= 1
            if remaining > 0 and not any(widths[idx] < caps[idx] for idx in eligible):
                break

    return remaining


def compute_viewport_plan(viewer: Viewer, width: int, height: int) -> ViewportPlan:
    """Compute a viewport plan for ``viewer`` constrained to ``width``×``height``."""

    sheet = getattr(viewer, "sheet", None)
    if sheet is not None and hasattr(sheet, "update_layout_for_view"):
        try:
            sheet.update_layout_for_view(
                view_width=width,
                view_height=height,
                viewer=viewer,
            )
        except TypeError:
            sheet.update_layout_for_view(width)

    table_slice = fetch_visible_for_viewer(viewer)
    cols = list(table_slice.column_names)

    frozen_cols = getattr(viewer, "frozen_columns", []) if hasattr(viewer, "frozen_columns") else []
    frozen_name_set = set(frozen_cols)
    frozen_boundary_idx: int | None = None
    if frozen_cols:
        boundary_name = frozen_cols[-1]
        if boundary_name in cols:
            frozen_boundary_idx = cols.index(boundary_name)

    header_widths = getattr(viewer, "_header_widths", [])
    autosized = getattr(viewer, "_autosized_widths", None)
    sticky_widths = getattr(viewer, "_sticky_column_widths", {})
    if not isinstance(sticky_widths, dict):
        sticky_widths = {}
    col_widths: list[int] = []
    seed_widths: list[int] = []
    original_widths: list[int] = []
    for idx, col_name in enumerate(cols):
        try:
            col_idx = viewer.columns.index(col_name)
        except ValueError:
            base_width = max(4, display_width(col_name) + 2)
        else:
            base_width = (
                header_widths[col_idx]
                if col_idx < len(header_widths)
                else max(4, display_width(col_name) + 2)
            )
            if autosized:
                base_width = autosized.get(col_idx, base_width)
        original_widths.append(base_width)
        sticky = sticky_widths.get(col_name)
        seed = base_width
        if isinstance(sticky, int) and sticky > 0:
            if frozen_boundary_idx is not None and idx == frozen_boundary_idx:
                seed = max(1, sticky - 1)
            else:
                seed = sticky
        col_widths.append(seed)
        seed_widths.append(seed)

    if frozen_boundary_idx is not None and 0 <= frozen_boundary_idx < len(col_widths):
        col_widths[frozen_boundary_idx] += 1
        seed_widths[frozen_boundary_idx] += 1
        original_widths[frozen_boundary_idx] += 1

    sheet_obj = getattr(viewer, "sheet", None)
    fill_column_name: str | None = None
    if sheet_obj is not None:
        preferred_fill = None
        if hasattr(sheet_obj, "preferred_fill_column"):
            preferred = sheet_obj.preferred_fill_column
            preferred_fill = preferred() if callable(preferred) else preferred
        if preferred_fill is None:
            preferred_fill = getattr(sheet_obj, "fill_column_name", None)
        if isinstance(preferred_fill, str) and preferred_fill in cols:
            fill_column_name = preferred_fill
    fill_idx = cols.index(fill_column_name) if fill_column_name else None

    all_maximized = getattr(viewer, "all_columns_maximized", False)
    col_maximized = getattr(viewer, "maximized_column_index", None)
    maximized_column_name: str | None = None
    if col_maximized is not None and 0 <= col_maximized < len(viewer.columns):
        maximized_column_name = viewer.columns[col_maximized]

    if (
        cols
        and fill_idx is None
        and not (col_maximized is not None or all_maximized)
        and hasattr(viewer, "_last_col_fits_completely")
        and not getattr(viewer, "_last_col_fits_completely", True)
    ):
        border_overhead = _table_border_overhead(len(cols))
        available_width = max(1, width - border_overhead)
        used_width = sum(col_widths[:-1])
        remaining_width = available_width - used_width
        min_last_width = max(4, len(cols[-1]) + 2)
        extended_width = max(min_last_width, remaining_width)
        col_widths[-1] = extended_width

    if all_maximized and cols:
        border_overhead = _table_border_overhead(len(cols))
        available_inner = max(1, width - border_overhead)
        current_total = sum(col_widths)
        if current_total < available_inner:
            extra = available_inner - current_total
            share, remainder = divmod(extra, len(col_widths))
            if share:
                for idx in range(len(col_widths)):
                    col_widths[idx] += share
            if remainder:
                for idx in range(remainder):
                    col_widths[-(idx + 1)] += 1

    sort_col = getattr(viewer, "sort_col", None)
    schema = getattr(viewer, "schema", None) or getattr(viewer.sheet, "schema", {})
    columns_data = [table_slice.column(name) for name in cols]

    current_visible_col_index: int | None = None
    if 0 <= viewer.cur_col < len(viewer.columns):
        current_col_name = viewer.columns[viewer.cur_col]
        try:
            current_visible_col_index = cols.index(current_col_name)
        except ValueError:
            current_visible_col_index = 0 if cols else None

    if current_visible_col_index is None and cols:
        current_visible_col_index = min(viewer.cur_col, len(cols) - 1)

    column_meta: list[_ColumnMeta] = []
    for idx, column_name in enumerate(cols):
        is_frozen = column_name in frozen_name_set
        dtype = schema.get(column_name)
        is_numeric = bool(dtype and _is_numeric_dtype(dtype))
        col_has_nulls = table_slice.height > 0 and columns_data[idx].null_count > 0
        header_display = display_width(column_name)
        min_width = max(4, min(original_widths[idx], header_display + 2))
        if is_numeric:
            min_width = max(min_width, min(original_widths[idx], 8))
        header_active = idx == current_visible_col_index
        column_meta.append(
            _ColumnMeta(
                name=column_name,
                dtype=dtype,
                is_numeric=is_numeric,
                has_nulls=col_has_nulls,
                min_width=min_width,
                original_width=original_widths[idx],
                header_active=header_active,
                is_sorted=sort_col == column_name,
                is_frozen=is_frozen,
            )
        )

    border_overhead = _table_border_overhead(len(cols))
    available_inner = max(1, width - border_overhead) if cols else width

    allow_partial_last = (
        cols
        and fill_idx is None
        and not (col_maximized is not None or all_maximized)
        and hasattr(viewer, "_last_col_fits_completely")
        and not getattr(viewer, "_last_col_fits_completely", True)
    )

    min_widths: list[int] = []
    minimum_targets: list[int] = []
    for idx, meta in enumerate(column_meta):
        seed = seed_widths[idx] if idx < len(seed_widths) else meta.original_width
        base_min = max(meta.min_width, seed) if meta.is_frozen else meta.min_width
        min_widths.append(base_min)
        minimum_targets.append(base_min if meta.is_frozen else meta.min_width)

    if maximized_column_name:
        for idx, meta in enumerate(column_meta):
            if meta.name != maximized_column_name:
                continue
            max_target = max(seed_widths[idx], meta.original_width, min_widths[idx])
            min_widths[idx] = max_target
            seed_widths[idx] = max_target
            minimum_targets[idx] = max_target
            break

    if (
        allow_partial_last
        and min_widths
        and not column_meta[-1].is_frozen
        and not (maximized_column_name and column_meta[-1].name == maximized_column_name)
    ):
        min_widths[-1] = 1
        minimum_targets[-1] = 1

    col_widths = list(min_widths)

    total_min = sum(col_widths)
    if total_min > available_inner:
        col_widths = _shrink_widths_to_fit(col_widths, minimum_targets, available_inner)
    else:
        remaining = available_inner - total_min
        weights: list[int] = []
        targets: list[int] = []
        for idx, meta in enumerate(column_meta):
            sticky = sticky_widths.get(meta.name)
            seed = seed_widths[idx] if idx < len(seed_widths) else meta.original_width
            if meta.is_frozen:
                target = col_widths[idx]
                weights_val = 0
            else:
                target = max(meta.min_width, seed)
                if isinstance(sticky, int) and sticky > 0:
                    target = max(target, sticky)
                weights_val = 1
                if meta.is_numeric:
                    weights_val += 1
                if meta.header_active:
                    weights_val += 2
                if fill_idx is not None and idx == fill_idx:
                    weights_val += 1
                if maximized_column_name and meta.name == maximized_column_name:
                    weights_val += 3
                    target = max(target, available_inner)
                if getattr(viewer, "is_hist_view", False):
                    weights_val += 1
                if getattr(viewer, "freq_source_col", None) == meta.name:
                    weights_val += 1
                if all_maximized:
                    weights_val += 1
            weights.append(weights_val)
            targets.append(max(target, meta.min_width))

        remaining = _allocate_widths(col_widths, targets, weights, remaining)

        if remaining > 0:
            if (
                fill_idx is not None
                and 0 <= fill_idx < len(col_widths)
                and not column_meta[fill_idx].is_frozen
            ):
                col_widths[fill_idx] += remaining
                remaining = 0
            else:
                expanded_caps = []
                for idx in range(len(targets)):
                    if column_meta[idx].is_frozen:
                        expanded_caps.append(col_widths[idx])
                    else:
                        expanded_caps.append(targets[idx] + remaining)
                remaining = _allocate_widths(col_widths, expanded_caps, weights, remaining)

    column_plans: list[ColumnPlan] = []
    for idx, meta in enumerate(column_meta):
        column_plans.append(
            ColumnPlan(
                name=meta.name,
                width=col_widths[idx],
                min_width=meta.min_width,
                original_width=meta.original_width,
                is_numeric=meta.is_numeric,
                has_nulls=meta.has_nulls,
                header_active=meta.header_active,
                is_sorted=meta.is_sorted,
            )
        )

    viewer._sticky_column_widths = {plan.name: plan.width for plan in column_plans}

    header_row: list[Cell] = []
    for column in column_plans:
        cell = Cell(
            text=column.name,
            role="header",
            active_row=False,
            active_col=column.header_active,
            active_cell=column.header_active,
            numeric=False,
            is_null=False,
        )
        header_row.append(cell)

    pad = 1
    formatted_columns: list[Sequence[str]] = []
    column_inner_widths: list[int] = []
    for idx, column in enumerate(column_plans):
        column_width = max(1, column.width)
        border_offset = 1 if frozen_boundary_idx is not None and idx == frozen_boundary_idx else 0
        content_width = max(0, column_width - border_offset)
        padding = pad if content_width >= (pad * 2 + 1) else 0
        inner_width = max(0, content_width - (padding * 2))
        safe_max_chars = max(inner_width, 1, 20)
        formatted_columns.append(columns_data[idx].formatted(safe_max_chars))
        column_inner_widths.append(inner_width)

    decimal_cache = getattr(viewer, "_decimal_alignment_cache", None)
    if decimal_cache is None:
        decimal_cache = {}
        viewer._decimal_alignment_cache = decimal_cache

    decimal_alignments: list[tuple[int, int] | None] = []
    for idx, column in enumerate(column_plans):
        if not column.is_numeric:
            decimal_alignments.append(None)
            continue
        inner_width = column_inner_widths[idx]
        viewport_alignment = compute_decimal_alignment(formatted_columns[idx], inner_width)
        cached_alignment = decimal_cache.get(column.name)

        merged_alignment: tuple[int, int] | None = None
        if cached_alignment and viewport_alignment:
            merged_alignment = (
                max(cached_alignment[0], viewport_alignment[0]),
                cached_alignment[1],
            )
        elif cached_alignment:
            merged_alignment = cached_alignment
        else:
            merged_alignment = viewport_alignment

        if merged_alignment is not None:
            required_width = merged_alignment[0] + 1 + merged_alignment[1]
            if inner_width >= required_width:
                decimal_cache[column.name] = merged_alignment
                decimal_alignments.append(merged_alignment)
                continue

        decimal_alignments.append(None)

    row_positions = getattr(viewer, "visible_row_positions", [])
    visible_frozen_rows = min(getattr(viewer, "visible_frozen_row_count", 0), table_slice.height)

    body_rows: list[list[Cell]] = []
    for r in range(table_slice.height):
        row_cells: list[Cell] = []
        row_index = row_positions[r] if r < len(row_positions) else viewer.row0 + r
        row_active = row_index == viewer.cur_row
        for ci, column in enumerate(column_plans):
            meta = column_meta[ci]
            dtype = meta.dtype
            is_numeric = column.is_numeric
            width_hint = max(1, column.width)
            border_offset = (
                1 if frozen_boundary_idx is not None and ci == frozen_boundary_idx else 0
            )
            content_width = max(0, width_hint - border_offset)
            padding = pad if content_width >= (pad * 2 + 1) else 0
            inner_width = max(0, content_width - padding * 2)
            precomputed_txt = formatted_columns[ci][r]
            raw_value = columns_data[ci].values[r]

            is_null = raw_value is None or precomputed_txt == ""
            if is_null:
                base_txt = "null"
            elif isinstance(raw_value, float) and (math.isnan(raw_value) or math.isinf(raw_value)):
                base_txt = "NaN" if math.isnan(raw_value) else ("inf" if raw_value > 0 else "-inf")
            else:
                base_txt = precomputed_txt

            visible_txt = truncate_grapheme_safe(base_txt, inner_width) if inner_width > 0 else ""
            alignment = decimal_alignments[ci] if ci < len(decimal_alignments) else None
            aligned_candidate = (
                apply_decimal_alignment(base_txt, alignment, inner_width)
                if alignment is not None and inner_width > 0 and not is_null
                else None
            )
            if aligned_candidate is not None:
                aligned_txt = aligned_candidate
            elif is_numeric and inner_width > 0:
                aligned_txt = pad_left_display(visible_txt, inner_width)
            elif inner_width > 0:
                aligned_txt = pad_right_display(visible_txt, inner_width)
            else:
                aligned_txt = visible_txt

            cell_text = (" " * padding) + aligned_txt + (" " * padding)
            cell_width = display_width(cell_text)
            if content_width > 0 and cell_width < content_width:
                cell_text = pad_right_display(cell_text, content_width)
            elif content_width > 0 and cell_width > content_width:
                cell_text = truncate_grapheme_safe(cell_text, content_width)
            elif content_width == 0:
                cell_text = ""

            col_active = ci == current_visible_col_index
            cell = Cell(
                text=cell_text,
                role="body",
                active_row=row_active,
                active_col=col_active,
                active_cell=row_active and col_active,
                numeric=is_numeric,
                is_null=is_null,
            )
            row_cells.append(cell)
        body_rows.append(row_cells)

    cells: list[list[Cell]] = []
    if header_row:
        cells.append(header_row)
    cells.extend(body_rows)

    row_offset = max(0, viewer.row0)
    if visible_frozen_rows:
        row_offset = max(row_offset, visible_frozen_rows)

    col_offset = max(0, viewer.col0)

    return ViewportPlan(
        columns=column_plans,
        frozen_boundary_idx=frozen_boundary_idx,
        rows=table_slice.height,
        row_offset=row_offset,
        col_offset=col_offset,
        cells=cells,
        active_row_index=getattr(viewer, "cur_row", 0),
    )
