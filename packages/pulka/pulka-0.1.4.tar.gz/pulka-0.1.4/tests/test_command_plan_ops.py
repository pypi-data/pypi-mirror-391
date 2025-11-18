import polars as pl
import pytest

from pulka.command.builtins import (
    handle_filter,
    handle_next_diff,
    handle_prev_diff,
    handle_reset,
    handle_search,
    handle_sort,
)
from pulka.command.registry import CommandContext
from pulka.core.viewer import Viewer, ViewStack
from pulka.sheets.data_sheet import DataSheet


def _make_context(
    job_runner, df: pl.DataFrame | None = None
) -> tuple[DataSheet, Viewer, CommandContext]:
    if df is None:
        df = pl.DataFrame({"a": [1, 2, 3], "b": ["x", "y", "z"]})
    sheet = DataSheet(df.lazy(), runner=job_runner)
    viewer = Viewer(sheet, viewport_rows=5, viewport_cols=5, runner=job_runner)
    stack = ViewStack()
    stack.push(viewer)
    return sheet, viewer, CommandContext(sheet, viewer, view_stack=stack)


def _plan_hash(sheet: DataSheet) -> str:
    return sheet.plan.snapshot()["hash"]


def test_handle_filter_updates_plan(job_runner) -> None:
    sheet, viewer, context = _make_context(job_runner)
    baseline = sheet.plan
    baseline_hash = _plan_hash(sheet)

    handle_filter(context, ["c.a > 1"])

    assert context.sheet is viewer.sheet
    updated_plan = context.sheet.plan
    assert updated_plan.filters == ("c.a > 1",)
    assert updated_plan.sql_filter is None
    assert updated_plan != baseline
    assert _plan_hash(context.sheet) != baseline_hash


def test_handle_filter_clear_is_idempotent(job_runner) -> None:
    sheet, _, context = _make_context(job_runner)
    baseline_hash = _plan_hash(sheet)

    handle_filter(context, [" "])

    assert _plan_hash(context.sheet) == baseline_hash


def test_apply_filter_invalid_expression_reports_error(job_runner) -> None:
    sheet, viewer, _ = _make_context(job_runner)
    baseline_hash = _plan_hash(sheet)

    viewer.apply_filter("c.a >")

    assert _plan_hash(viewer.sheet) == baseline_hash
    assert viewer.status_message is not None
    assert viewer.status_message.startswith("filter error:")


def test_handle_sort_cycles_plan(job_runner) -> None:
    sheet, viewer, context = _make_context(job_runner)
    baseline_plan = sheet.plan

    handle_sort(context, [])
    first_plan = context.sheet.plan
    assert first_plan.sort == (("a", False),)
    assert first_plan != baseline_plan

    handle_sort(context, [])
    second_plan = context.sheet.plan
    assert second_plan.sort == (("a", True),)

    handle_sort(context, [])
    final_plan = context.sheet.plan
    assert final_plan.sort == ()
    assert final_plan == baseline_plan
    assert context.sheet is viewer.sheet


def test_handle_search_updates_viewer_state(job_runner) -> None:
    sheet, viewer, context = _make_context(job_runner)
    baseline = _plan_hash(sheet)

    handle_search(context, ["needle"])

    assert _plan_hash(context.sheet) == baseline
    assert viewer.search_text == "needle"

    handle_search(context, ["needle"])
    assert context.viewer.status_message == "search unchanged"


def test_handle_search_moves_cursor_to_first_match(job_runner) -> None:
    _, viewer, context = _make_context(job_runner)
    viewer.cur_col = 1  # column 'b'
    viewer.cur_row = 0

    handle_search(context, ["y"])

    assert viewer.cur_row == 1


def test_handle_reset_restores_default_plan(job_runner) -> None:
    sheet, _, context = _make_context(job_runner)

    handle_filter(context, ["c.a > 1"])
    filtered_plan = context.sheet.plan

    handle_reset(context, [])
    reset_plan = context.sheet.plan

    assert reset_plan.filters == ()
    assert reset_plan.sort == ()
    assert reset_plan.search_text is None
    assert reset_plan != filtered_plan


def test_handle_next_diff_advances_to_next_match(job_runner) -> None:
    df = pl.DataFrame({"a": [1, 2, 3, 4], "b": ["foo", "bar", "foo", "bar"]})
    _, viewer, context = _make_context(job_runner, df=df)
    viewer.cur_col = 1
    handle_search(context, ["foo"])
    assert viewer.cur_row == 0

    handle_next_diff(context, [])

    assert viewer.cur_row == 2


def test_handle_prev_diff_moves_to_previous_match(job_runner) -> None:
    df = pl.DataFrame({"a": [1, 2, 3, 4], "b": ["foo", "bar", "foo", "bar"]})
    _, viewer, context = _make_context(job_runner, df=df)
    viewer.cur_col = 1
    handle_search(context, ["foo"])
    handle_next_diff(context, [])
    assert viewer.cur_row == 2

    handle_prev_diff(context, [])

    assert viewer.cur_row == 0


def test_handle_next_diff_does_not_wrap(job_runner) -> None:
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["foo", "foo", "bar"]})
    _, viewer, context = _make_context(job_runner, df=df)
    viewer.cur_col = 1
    handle_search(context, ["foo"])
    handle_next_diff(context, [])
    assert viewer.cur_row == 1

    handle_next_diff(context, [])

    assert viewer.cur_row == 1
    assert viewer.status_message == "no more matches"


def test_handle_prev_diff_does_not_wrap(job_runner) -> None:
    df = pl.DataFrame({"a": [1, 2, 3], "b": ["bar", "foo", "foo"]})
    _, viewer, context = _make_context(job_runner, df=df)
    viewer.cur_col = 1
    handle_search(context, ["foo"])
    handle_prev_diff(context, [])
    assert viewer.cur_row == 1

    handle_prev_diff(context, [])

    assert viewer.cur_row == 1
    assert viewer.status_message == "no more matches"


def test_apply_sql_filter_invalid_clause_reports_error(job_runner) -> None:
    sheet, viewer, _ = _make_context(job_runner)
    if getattr(viewer.sheet, "_sql_executor", None) is None:
        pytest.skip("Polars SQL support not available")

    baseline_hash = _plan_hash(sheet)

    viewer.apply_sql_filter("bad syntax")

    assert _plan_hash(viewer.sheet) == baseline_hash
    assert viewer.status_message is not None
    assert viewer.status_message.startswith("sql filter error:")
