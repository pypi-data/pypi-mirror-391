import polars as pl

from pulka.api import Session
from pulka.logging import Recorder, RecorderConfig


def test_session_state_json_uses_viewer_snapshot(tmp_path):
    df = pl.DataFrame(
        {
            "a": [1, 2, 3, 4],
            "b": ["x", "y", "z", "w"],
            "c": [10, 20, 30, 40],
        }
    )
    dataset_path = tmp_path / "state.parquet"
    df.write_parquet(dataset_path)

    session = Session(str(dataset_path), viewport_rows=5, viewport_cols=3)
    viewer = session.viewer

    viewer.cur_row = 2
    viewer.row0 = 1
    viewer.cur_col = viewer.columns.index("b")
    viewer.col0 = 0
    viewer._hidden_cols.add("b")

    state = session.get_state_json()
    snapshot = viewer.snapshot()

    assert state["cursor_row"] == snapshot.cursor.row
    assert state["cursor_col"] == snapshot.cursor.col
    assert state["top_row"] == snapshot.viewport.row0
    assert state["left_col"] == snapshot.viewport.col0
    expected_rows = snapshot.total_rows or snapshot.visible_row_count
    expected_cols = snapshot.visible_column_count or snapshot.total_columns

    assert state["n_rows"] == expected_rows
    assert state["n_cols"] == expected_cols
    assert state["col_order"] == list(snapshot.visible_columns or snapshot.columns)


def test_session_tracks_dataset_path(tmp_path):
    df = pl.DataFrame({"a": [1, 2, 3]})
    first_path = tmp_path / "first.parquet"
    second_path = tmp_path / "second.parquet"
    df.write_parquet(first_path)
    pl.DataFrame({"a": [4, 5, 6]}).write_parquet(second_path)

    session = Session(str(first_path))
    assert session.dataset_path == first_path

    session.open(str(second_path))
    assert session.dataset_path == second_path

    lazyframe = pl.DataFrame({"b": [10]}).lazy()
    session.open_lazyframe(lazyframe, label="expr")
    assert session.dataset_path is None


def test_session_close_records_job_metrics(tmp_path):
    df = pl.DataFrame({"a": [1, 2, 3]})
    dataset_path = tmp_path / "metrics.parquet"
    df.write_parquet(dataset_path)
    recorder = Recorder(
        RecorderConfig(
            enabled=True,
            output_dir=tmp_path,
            compression="none",
            auto_flush_on_exit=False,
        )
    )
    session = Session(str(dataset_path), recorder=recorder)
    session.close()
    recorded_types = [event.type for event in recorder._buffer]
    assert "job_runner_metrics" in recorded_types
