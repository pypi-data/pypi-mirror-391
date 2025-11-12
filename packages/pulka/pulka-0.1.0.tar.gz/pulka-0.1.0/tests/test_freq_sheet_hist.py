from __future__ import annotations

import time
from datetime import date, timedelta

import polars as pl

from pulka.api.session import Session
from pulka.command.registry import CommandContext
from pulka.core.engine.contracts import TableSlice
from pulka.core.engine.polars_adapter import unwrap_lazyframe_handle
from pulka.core.formatting import _format_large_number_compact
from pulka.core.viewer import Viewer, ViewStack
from pulka.sheets.data_sheet import DataSheet
from pulka.sheets.hist_sheet import HistogramSheet
from pulka_builtin_plugins.freq.plugin import (
    _SMALL_CARDINALITY_THRESHOLD,
    FreqSheet,
    _format_freq_status_message,
    _freq_cmd,
    _FrequencyUiHandle,
    open_frequency_viewer,
)


def make_data_sheet(lazy_frame, runner):
    return DataSheet(lazy_frame, runner=runner)


def _wait_for_frequency(freq_sheet: FreqSheet) -> None:
    sheet_id = getattr(freq_sheet.source_sheet, "sheet_id", None)
    if sheet_id is None:
        return
    tag = f"freq:{freq_sheet.freq_column}:auto"
    runner = freq_sheet.job_runner
    deadline = time.time() + 5.0
    while time.time() < deadline:
        result = runner.get(sheet_id, tag)
        if result is not None and result.error is None and result.value is not None:
            freq_sheet.fetch_slice(0, 1, list(freq_sheet.columns))
            return
        time.sleep(0.01)
    raise TimeoutError("frequency computation timed out")


def test_freq_sheet_includes_hist_for_moderate_cardinality(job_runner) -> None:
    # Build a column with more than 100 distinct values to exercise the relaxed
    # histogram threshold. Each value is unique, so the miniature bar chart
    # should still appear for the frequency view.
    values = [date(2020, 1, 1) + timedelta(days=i) for i in range(150)]
    df = pl.DataFrame({"date_col": values}, schema={"date_col": pl.Date})

    sheet = make_data_sheet(df.lazy(), job_runner)
    freq_sheet = FreqSheet(sheet, "date_col", runner=job_runner)
    _wait_for_frequency(freq_sheet)

    lazy_frame = unwrap_lazyframe_handle(freq_sheet.lf0)
    schema = lazy_frame.collect_schema()
    assert "hist" in schema

    bars = lazy_frame.select("hist").head(5).collect()["hist"].to_list()
    assert bars and all(any(ch != " " for ch in bar) for bar in bars)


def test_freq_command_reports_high_cardinality_status_message(job_runner) -> None:
    column = "category"
    unique_values = _SMALL_CARDINALITY_THRESHOLD + 5
    df = pl.DataFrame({column: [f"item-{i}" for i in range(unique_values)]})

    sheet = make_data_sheet(df.lazy(), job_runner)
    viewer = Viewer(sheet, runner=sheet.job_runner)
    stack = ViewStack()
    stack.push(viewer)
    context = CommandContext(sheet, viewer, view_stack=stack)

    _freq_cmd(context, [column])
    assert isinstance(context.viewer.sheet, FreqSheet)
    _wait_for_frequency(context.viewer.sheet)
    context.viewer.status_message = _format_freq_status_message(context.viewer.sheet, column)

    assert context.viewer.status_message == (
        f"High cardinality: {_format_large_number_compact(unique_values)} unique values"
    )
    assert len(stack.viewers) == 2
    assert context.viewer is stack.active


def test_freq_command_sets_status_message_when_session_present(tmp_path) -> None:
    column = "category"
    unique_values = _SMALL_CARDINALITY_THRESHOLD + 5
    df = pl.DataFrame({column: [f"item-{i}" for i in range(unique_values)]})

    path = tmp_path / "freq_session.csv"
    df.write_csv(path)

    session = Session(str(path), viewport_rows=10)
    context = CommandContext(
        session.sheet,
        session.viewer,
        session=session,
        view_stack=session.view_stack,
    )

    _freq_cmd(context, [column])
    active_viewer = session.viewer
    assert isinstance(active_viewer.sheet, FreqSheet)
    _wait_for_frequency(active_viewer.sheet)
    active_viewer.status_message = _format_freq_status_message(active_viewer.sheet, column)

    assert active_viewer.status_message == (
        f"High cardinality: {_format_large_number_compact(unique_values)} unique values"
    )
    assert len(session.view_stack.viewers) == 2
    assert active_viewer is session.view_stack.active


def test_format_freq_status_message_reports_high_cardinality(job_runner) -> None:
    column = "category"
    unique_values = _SMALL_CARDINALITY_THRESHOLD + 5
    df = pl.DataFrame({column: [f"item-{i}" for i in range(unique_values)]})

    sheet = make_data_sheet(df.lazy(), job_runner)
    freq_sheet = FreqSheet(sheet, column, runner=job_runner)
    _wait_for_frequency(freq_sheet)

    assert _format_freq_status_message(freq_sheet, column) == (
        f"High cardinality: {_format_large_number_compact(unique_values)} unique values"
    )


def test_frequency_handle_refreshes_viewer_after_job_completion(job_runner) -> None:
    column = "category"
    df = pl.DataFrame({column: ["x", "y", "x", "z"]})

    base_sheet = make_data_sheet(df.lazy(), job_runner)
    freq_sheet = FreqSheet(base_sheet, column, runner=job_runner)
    viewer = Viewer(freq_sheet, runner=freq_sheet.job_runner)

    future = freq_sheet._pending_future
    assert future is not None

    viewer._row_cache.table = TableSlice.empty(["placeholder"], {"placeholder": pl.Int64})

    handle = _FrequencyUiHandle(freq_sheet, None)
    freq_sheet.attach_ui_handle(handle)

    future.result(timeout=5)

    assert handle.consume_update(viewer) is True
    assert viewer._row_cache.table is None
    assert freq_sheet._display_df.height == 3
    assert viewer.status_message == _format_freq_status_message(freq_sheet, column)


def test_frequency_row_provider_populates_without_screen(job_runner) -> None:
    column = "category"
    df = pl.DataFrame({column: ["x", "y", "x", "z"]})

    base_sheet = make_data_sheet(df.lazy(), job_runner)
    freq_sheet = FreqSheet(base_sheet, column, runner=job_runner)
    viewer = Viewer(freq_sheet, runner=freq_sheet.job_runner)

    _wait_for_frequency(freq_sheet)
    plan = viewer._current_plan()
    assert plan is not None

    table_slice, _status = viewer.row_provider.get_slice(plan, viewer.columns, 0, 10)
    assert table_slice.height == 3
    values = list(table_slice.column(column).values)
    counts = list(table_slice.column("count").values)
    assert values[0] == "x"
    assert counts[0] == 2
    remaining = sorted(zip(values[1:], counts[1:], strict=False))
    assert remaining == [("y", 1), ("z", 1)]


def test_session_open_sheet_view_frequency(tmp_path) -> None:
    df = pl.DataFrame(
        {
            "category": ["x", "y", "x", "z"],
            "value": [1, 2, 3, 4],
        }
    )
    path = tmp_path / "freq_view.csv"
    df.write_csv(path)

    session = Session(str(path), viewport_rows=8)
    base_viewer = session.viewer

    freq_viewer = session.open_sheet_view(
        "freq",
        base_viewer=base_viewer,
        viewer_options={"source_path": None},
        column_name="category",
    )

    assert freq_viewer is session.view_stack.active
    assert isinstance(freq_viewer.sheet, FreqSheet)
    _wait_for_frequency(freq_viewer.sheet)


def test_session_open_sheet_view_histogram(tmp_path) -> None:
    df = pl.DataFrame(
        {
            "numbers": [1, 2, 3, 4, 5, 6],
            "category": ["a", "b", "a", "b", "c", "c"],
        }
    )
    path = tmp_path / "hist_view.csv"
    df.write_csv(path)

    session = Session(str(path), viewport_rows=10)
    base_viewer = session.viewer

    hist_viewer = session.open_sheet_view(
        "histogram",
        base_viewer=base_viewer,
        viewer_options={"source_path": None},
        column_name="numbers",
        preferred_height=getattr(base_viewer, "view_height", None),
        preferred_width=getattr(base_viewer, "view_width_chars", None),
    )

    assert hist_viewer is session.view_stack.active
    assert isinstance(hist_viewer.sheet, HistogramSheet)


def test_open_frequency_viewer_without_session_uses_view_stack(job_runner) -> None:
    df = pl.DataFrame({"category": ["x", "y", "x", "z"]})

    sheet = make_data_sheet(df.lazy(), job_runner)
    base_viewer = Viewer(sheet, runner=sheet.job_runner)
    stack = ViewStack()
    stack.push(base_viewer)

    derived_viewer = open_frequency_viewer(
        base_viewer,
        "category",
        view_stack=stack,
    )

    assert derived_viewer is stack.active
    assert isinstance(derived_viewer.sheet, FreqSheet)
    _wait_for_frequency(derived_viewer.sheet)
    assert derived_viewer.status_message.startswith("frequency table")


def test_open_frequency_viewer_with_session_uses_helper(tmp_path) -> None:
    df = pl.DataFrame(
        {
            "category": ["x", "y", "x", "z"],
            "value": [1, 2, 3, 4],
        }
    )
    path = tmp_path / "freq_helper.csv"
    df.write_csv(path)

    session = Session(str(path), viewport_rows=8)
    base_viewer = session.viewer

    derived_viewer = open_frequency_viewer(
        base_viewer,
        "category",
        session=session,
        view_stack=session.view_stack,
        screen=None,
    )

    assert derived_viewer is session.view_stack.active
    assert derived_viewer is session.viewer
    assert isinstance(derived_viewer.sheet, FreqSheet)
