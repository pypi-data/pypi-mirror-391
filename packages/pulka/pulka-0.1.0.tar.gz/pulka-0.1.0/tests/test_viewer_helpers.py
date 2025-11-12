from __future__ import annotations

import polars as pl

from pulka.core.viewer import Viewer
from pulka.core.viewer.public_state import viewer_public_state
from pulka.core.viewer.row_count_tracker import RowCountTracker
from pulka.core.viewer.state import ViewerSnapshot
from pulka.core.viewer.ui_hooks import NullViewerUIHooks
from pulka.sheets.data_sheet import DataSheet


def _make_plan_viewer(job_runner) -> Viewer:
    df = pl.DataFrame({"id": [1, 2, 3], "name": ["a", "b", "c"]})
    sheet = DataSheet(df.lazy(), runner=job_runner)
    return Viewer(sheet, viewport_rows=5, viewport_cols=5, runner=job_runner)


class _LegacySheet:
    def __init__(self) -> None:
        self.columns = ["id", "name"]
        self.schema = {"id": pl.Int64, "name": pl.Utf8}

    def fetch_slice(self, row_start: int, row_count: int, columns: list[str]) -> pl.DataFrame:
        return pl.DataFrame({name: [] for name in columns})


def _make_legacy_viewer(job_runner) -> Viewer:
    sheet = _LegacySheet()
    return Viewer(sheet, viewport_rows=5, viewport_cols=5, runner=job_runner)


def test_state_snapshot_roundtrip_restores_hidden_columns(job_runner):
    viewer = _make_legacy_viewer(job_runner)
    state = viewer.state_controller

    baseline_widths = tuple(viewer._header_widths)
    viewer._local_hidden_cols = {"name"}
    viewer._update_hidden_column_cache(set(viewer._local_hidden_cols))
    viewer.cur_row = 2
    viewer.row0 = 1
    viewer.cur_col = 0
    viewer.col0 = 0

    snapshot = state.capture_snapshot()

    viewer._hidden_cols.clear()
    viewer._local_hidden_cols.clear()
    viewer._header_widths = [1, 1]
    viewer.cur_row = 0
    viewer.row0 = 0

    state.restore_snapshot(snapshot)

    assert viewer._hidden_cols == {"name"}
    assert viewer._local_hidden_cols == {"name"}
    assert tuple(viewer._header_widths) == baseline_widths
    assert viewer.cur_row == 2
    assert viewer.row0 == 1


def test_state_clamp_skips_hidden_columns(job_runner):
    viewer = _make_legacy_viewer(job_runner)
    viewer.cur_col = viewer.columns.index("name")
    viewer._local_hidden_cols = {"name"}
    viewer._update_hidden_column_cache(set(viewer._local_hidden_cols), ensure_cursor=False)

    viewer.clamp()

    assert viewer.columns[viewer.cur_col] == "id"


def test_state_restore_trims_unknown_hidden_columns_and_extends_widths(job_runner):
    viewer = _make_legacy_viewer(job_runner)
    controller = viewer.state_controller

    viewer.columns.append("extra")
    viewer._default_header_widths.append(12)
    viewer._header_widths = [8, 9]  # shorter than columns on purpose
    viewer.cur_row = 0
    viewer.row0 = 0

    snapshot = ViewerSnapshot(
        hidden_cols=("missing",),
        header_widths=(5,),
        cur_col=0,
        col0=0,
        cur_row=2,
        row0=1,
    )

    controller.restore_snapshot(snapshot)

    assert viewer._hidden_cols == set()
    assert viewer._local_hidden_cols == set()
    assert len(viewer._header_widths) == len(viewer.columns)
    assert viewer._header_widths[-1] >= viewer._min_col_width


def test_viewer_public_snapshot_exposes_sanitised_state(job_runner):
    viewer = _make_legacy_viewer(job_runner)
    viewer.cur_row = 1
    viewer.row0 = 1
    viewer.cur_col = viewer.columns.index("name")
    viewer.col0 = 0
    viewer._local_hidden_cols = {"name"}
    viewer._update_hidden_column_cache(set(viewer._local_hidden_cols), ensure_cursor=False)

    state = viewer.snapshot()

    assert isinstance(state.visible_columns, tuple)
    assert isinstance(state.hidden_columns, tuple)
    assert state.cursor.row == 1
    assert state.cursor.col == viewer.columns.index("name")
    assert state.viewport.row0 == 1
    assert state.hidden_column_count == len(state.hidden_columns)
    assert "name" in state.hidden_columns
    assert "name" not in state.visible_columns


def test_viewer_public_state_helper_handles_missing_snapshot(job_runner):
    viewer = _make_legacy_viewer(job_runner)

    state = viewer_public_state(viewer)

    assert state is not None
    assert state.cursor.row == viewer.cur_row

    class _LegacyViewer:
        def __init__(self) -> None:
            self.cur_row = 0
            self.cur_col = 1
            self.row0 = 2
            self.col0 = 3
            self.columns = ["x", "y"]
            self.visible_cols = ["x"]
            self._hidden_cols = {"y"}
            self.sort_col = "x"
            self.sort_asc = True

    legacy = _LegacyViewer()

    legacy_state = viewer_public_state(legacy)

    assert legacy_state is not None
    assert legacy_state.cursor.row == 0
    assert legacy_state.cursor.col == 1
    assert legacy_state.viewport.row0 == 2
    assert legacy_state.visible_columns == ("x",)
    assert legacy_state.hidden_columns == ("y",)


def test_reconcile_schema_changes_respects_plan_projection(job_runner):
    viewer = _make_plan_viewer(job_runner)
    viewer.hide_current_column()
    viewer._reconcile_schema_changes()

    projection = tuple(viewer.sheet.plan.projection_or(viewer.columns))
    assert projection == tuple(viewer.visible_columns())
    assert viewer._local_hidden_cols == set()


def test_reconcile_schema_changes_unhides_everything_for_planless_sheet(job_runner):
    viewer = _make_legacy_viewer(job_runner)
    viewer._local_hidden_cols = set(viewer.columns)
    viewer._update_hidden_column_cache(set(viewer._local_hidden_cols))

    viewer._reconcile_schema_changes()

    assert set(viewer.visible_columns()) == set(viewer.columns)
    assert viewer._local_hidden_cols == set()


def test_plan_controller_apply_plan_update_sets_limit(job_runner):
    viewer = _make_plan_viewer(job_runner)
    controller = viewer.plan_controller

    result = controller.apply_plan_update("limit", lambda plan: plan.with_limit(1))

    assert result is not None
    assert result.plan_changed is True
    assert viewer.sheet.plan.limit == 1


class _DummySheet:
    sheet_id = None

    def __len__(self) -> int:  # pragma: no cover - trivial
        return 8


class _DummyViewer:
    def __init__(self, runner) -> None:
        self.sheet = _DummySheet()
        self._total_rows: int | None = None
        self._row_count_stale = True
        self._row_count_future = None
        self._row_count_display_pending = False
        self._status_dirty = False
        self._ui_hooks = NullViewerUIHooks()
        self.invalidate_called = False
        self.job_runner = runner

    def invalidate_row_cache(self) -> None:
        self.invalidate_called = True

    def clamp(self) -> None:  # pragma: no cover - exercised indirectly
        pass

    @property
    def ui_hooks(self) -> NullViewerUIHooks:
        return self._ui_hooks

    def mark_status_dirty(self) -> None:
        self._status_dirty = True

    def acknowledge_status_rendered(self) -> None:
        self._status_dirty = False

    def is_status_dirty(self) -> bool:
        return self._status_dirty


def test_row_count_tracker_invalidates_and_counts(job_runner):
    dummy = _DummyViewer(job_runner)
    tracker = RowCountTracker(dummy, runner=job_runner)

    tracker.invalidate()

    assert dummy.is_status_dirty() is True
    assert dummy.invalidate_called is True
    assert dummy._total_rows is None

    total = tracker.ensure_total_rows()

    assert total == 8
    assert tracker.total_rows == 8
    assert dummy._total_rows == 8
    assert dummy._row_count_stale is False
    assert dummy._row_count_display_pending is False
    assert dummy.is_status_dirty() is True


def test_configure_terminal_clears_status_and_resets_cache(job_runner):
    viewer = _make_legacy_viewer(job_runner)
    viewer.mark_status_dirty()
    viewer._visible_key = (1, 2, 3)
    viewer.configure_terminal(72, 10)

    assert viewer.view_width_chars == 72
    assert viewer.view_height == 10
    assert viewer._visible_key is None
    assert viewer.is_status_dirty() is False


def test_acknowledge_status_rendered_resets_flag(job_runner):
    viewer = _make_legacy_viewer(job_runner)
    viewer.mark_status_dirty()
    assert viewer.is_status_dirty() is True

    viewer.acknowledge_status_rendered()

    assert viewer.is_status_dirty() is False
