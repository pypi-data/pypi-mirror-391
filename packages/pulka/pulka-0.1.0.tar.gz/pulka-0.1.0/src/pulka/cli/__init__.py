"""Command line entrypoint for Pulka."""

from __future__ import annotations

import argparse
import os
import sys
from collections.abc import Sequence
from contextlib import suppress
from pathlib import Path
from shutil import get_terminal_size
from typing import TYPE_CHECKING

import polars as pl

from ..api import Runtime
from ..core.engine.polars_adapter import (
    dataframe_from_table_slice,
    unwrap_lazyframe_handle,
    unwrap_physical_plan,
)
from ..data.export import write_view_to_path
from ..data.expr_lang import ExpressionError, evaluate_dataset_expression
from ..headless.runner import load_script_file
from ..logging import Recorder, RecorderConfig
from .generate import generate_main
from .spec import spec_main

if TYPE_CHECKING:  # pragma: no cover - import guard
    from ..api.session import Session
    from ..core.viewer import Viewer


def main(argv: Sequence[str] | None = None) -> int:
    args = list(argv if argv is not None else sys.argv[1:])
    if not args:
        return _run_classic(args)
    command = args[0]
    if command == "generate":
        return generate_main(args[1:])
    if command == "spec":
        return spec_main(args[1:])
    if command in {"-h", "--help"}:
        _print_main_help()
        return 0
    return _run_classic(args)


def _print_main_help() -> None:
    print("Pulka CLI")
    print()
    print("Usage:")
    print("  pulka <dataset> [options]     # open viewer (classic mode)")
    print("  pulka generate <spec> [...]   # materialize synthetic data")
    print("  pulka spec <command> [...]    # spec utilities")
    print()
    print("Run 'pulka spec --help' or 'pulka generate --help' for details.")


def _run_classic(argv: Sequence[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expr_text = args.expr.strip() if isinstance(args.expr, str) else None
    if expr_text == "":
        expr_text = None

    if args.replay and args.path is None:
        parser.error("--replay requires a dataset path")

    if args.path is None and expr_text is None:
        parser.error("Either PATH or --expr must be provided")

    if args.replay:
        from ..debug.replay import TUIReplayTool

        replay_tool = TUIReplayTool()
        try:
            replay_tool.load_session(args.replay)
            replay_tool.setup_tui(Path(args.path))

            if args.replay_step:
                final_state = replay_tool.replay_until(args.replay_step)
                print(f"Replayed to step {args.replay_step}")
                print(f"Cursor: ({final_state.cursor_row}, {final_state.cursor_col})")
                print(
                    f"Viewport: row_start={final_state.viewport_start_row}, "
                    f"col_start={final_state.viewport_start_col}"
                )
                print(f"Visible columns: {final_state.visible_columns}")
            else:
                step_count = 0
                while replay_tool.current_step < len(replay_tool.session_data):
                    replay_tool.replay_step()
                    step_count += 1
                print(f"Replayed entire session ({step_count} steps)")

        except Exception as exc:  # pragma: no cover - usability guard
            print(f"Replay error: {exc}", file=sys.stderr)
            return 1
        return 0

    record_enabled = bool(args.record or args.repro_export)
    cell_redaction = args.cell_redaction
    if cell_redaction is None:
        cell_redaction = os.getenv("PULKA_RECORDER_CELL_REDACTION", "hash_strings")

    config = RecorderConfig(enabled=record_enabled, cell_redaction=cell_redaction)
    if args.record_dir:
        config.output_dir = args.record_dir
    recorder = Recorder(config)

    runtime = Runtime()
    session: Session | None = None

    try:
        try:
            session = _create_session(runtime, recorder, args, expr_text)
        except ExpressionError as exc:
            print(f"expr error: {exc}", file=sys.stderr)
            if recorder.enabled:
                recorder.on_process_exit(reason="cli")
            return 2

        commands: list[str] = []
        if args.script_file:
            commands.extend(load_script_file(args.script_file))
        if args.commands:
            commands.extend(args.commands)

        if commands:
            outputs = session.run_script(commands, auto_render=not args.no_auto_render)
            for chunk in outputs:
                print(chunk)

            if not args.out:
                _finish_headless(session, args)
                return 0

        if args.out:
            exit_code = 0
            try:
                destination = write_view_to_path(
                    session.viewer,
                    args.out,
                    options=args.out_options,
                )
            except Exception as exc:
                print(f"Export failed: {exc}", file=sys.stderr)
                exit_code = 1
            else:
                print(f"Export saved to: {destination}")

            _finish_headless(session, args)
            return exit_code

        if args.schema or args.glimpse:
            _print_metadata_tables(session, args)
            _finish_headless(session, args)
            return 0

        if expr_text is not None and not args.tui:
            try:
                preview_df = _expr_preview_dataframe(session, max_rows=args.viewport_rows)
            except Exception as exc:  # pragma: no cover - defensive guard
                viewer = session.viewer
                if viewer is None:
                    print("expr error: session has no active viewer", file=sys.stderr)
                    return 1
                viewer.update_terminal_metrics()
                viewer.clamp()
                output = session.render()
                print(output)
                if recorder.enabled:
                    recorder.record(
                        "warning",
                        {
                            "context": "cli-expr",
                            "message": f"fallback to viewer render: {exc}",
                        },
                    )
            else:
                _print_polars_dataframe(preview_df)

            _finish_headless(session, args)
            return 0

        from ..tui.app import run_tui_app

        def _tui_on_shutdown(active_session: Session) -> None:
            if not args.repro_export or not active_session.recorder.enabled:
                return
            try:
                export_path = active_session.recorder.export_repro_slice(
                    session=active_session,
                    row_margin=10,
                    include_all_columns=False,
                )
                print(f"Repro export saved to: {export_path}")
            except Exception as exc:  # pragma: no cover - IO guard
                print(f"Repro export failed: {exc}")

        try:
            run_tui_app(
                session.viewer,
                recorder=session.recorder,
                on_shutdown=_tui_on_shutdown,
            )
        finally:
            if session.recorder.enabled:
                session.recorder.on_process_exit(reason="tui")
    finally:
        if session is not None:
            already_closed = getattr(session, "_closed", False)
            if not already_closed:
                with suppress(Exception):
                    session.close()
                if session.recorder.enabled:
                    session.recorder.on_process_exit(reason="tui")
        runtime.close()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Polars table viewer")
    parser.add_argument("path", nargs="?", help="Input data source")
    parser.add_argument(
        "-e",
        "--expr",
        dest="expr",
        default=None,
        help="Evaluate a Polars expression (use 'df' to reference PATH; headless by default)",
    )
    parser.add_argument(
        "--cmd",
        dest="commands",
        action="append",
        help="Headless command (repeatable)",
    )
    parser.add_argument(
        "--script",
        dest="script_file",
        help="Path to a command script (one command per line)",
    )
    parser.add_argument(
        "--no-auto-render",
        action="store_true",
        help="Skip automatic render after each command",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Write the active view to PATH and exit",
    )
    parser.add_argument(
        "--out-option",
        dest="out_options",
        action="append",
        help="Override export options (repeatable key=value)",
    )
    parser.add_argument(
        "--viewport-rows",
        type=int,
        help="Force the visible row count (ignores terminal height)",
    )
    parser.add_argument(
        "--viewport-cols",
        type=int,
        help="Force the number of visible columns",
    )
    parser.add_argument(
        "--record",
        action="store_true",
        help="Enable flight recorder logging",
    )
    parser.add_argument(
        "--record-dir",
        type=Path,
        help="Override recorder output directory",
    )
    parser.add_argument(
        "--cell-redaction",
        choices=["none", "hash_strings", "mask_patterns"],
        help="Configure cell redaction policy for flight recorder (default: hash_strings)",
    )
    parser.add_argument(
        "--repro-export",
        action="store_true",
        help="Export reproducible dataset slice at end of session",
    )
    parser.add_argument(
        "--tui",
        action="store_true",
        help="Force launching the TUI even when --expr is provided",
    )
    parser.add_argument(
        "--glimpse",
        action="store_true",
        help="Print a column-wise summary (via df.glimpse()) and exit",
    )
    parser.add_argument(
        "--schema",
        action="store_true",
        help="Print the column schema (name + dtype) and exit",
    )

    debug_group = parser.add_argument_group("debugging")
    debug_group.add_argument("--replay", type=Path, help="Replay flight recorder session")
    debug_group.add_argument("--replay-step", type=int, help="Stop replay at specific step")

    return parser


__all__ = ["build_parser", "main"]


def _create_session(
    runtime: Runtime,
    recorder: Recorder,
    args: argparse.Namespace,
    expr_text: str | None,
) -> Session:
    if expr_text:
        base_lazyframe: pl.LazyFrame | None = None
        base_label: str | None = None
        if args.path:
            base_label = str(Path(args.path))
            base_lazyframe = _lazyframe_from_path(runtime, args.path)
        if base_lazyframe is not None:
            try:
                base_schema = base_lazyframe.collect_schema()
            except Exception:  # pragma: no cover - schema fallback
                base_schema = base_lazyframe.schema
            columns = list(base_schema.keys())
        else:
            columns = None
        lazyframe = evaluate_dataset_expression(
            expr_text,
            df=base_lazyframe,
            columns=columns,
        )
        label = _expr_label(expr_text, base_label)
        _tag_lazyframe_metadata(lazyframe, label, expr_text)
        return runtime.open(
            None,
            viewport_rows=args.viewport_rows,
            viewport_cols=args.viewport_cols,
            recorder=recorder,
            lazyframe=lazyframe,
            source_label=label,
        )

    if args.path is None:  # pragma: no cover - parser guards above
        raise ValueError("path is required when --expr is not used")

    return runtime.open(
        args.path,
        viewport_rows=args.viewport_rows,
        viewport_cols=args.viewport_cols,
        recorder=recorder,
    )


def _lazyframe_from_path(runtime: Runtime, dataset_path: str) -> pl.LazyFrame:
    physical_plan = runtime.scanners.scan(Path(dataset_path))
    return unwrap_physical_plan(physical_plan).to_lazyframe()


def _expr_label(expr_text: str, base_label: str | None) -> str:
    snippet = _collapse_expr(expr_text)
    if base_label:
        return f"{base_label} | expr: {snippet}"
    return f"expr: {snippet}"


def _collapse_expr(expr_text: str, *, limit: int = 80) -> str:
    collapsed = " ".join(expr_text.strip().split())
    if len(collapsed) <= limit:
        return collapsed
    return f"{collapsed[: limit - 3]}..."


def _tag_lazyframe_metadata(lazyframe: pl.LazyFrame, label: str, expr_text: str) -> None:
    lazyframe._pulka_source_kind = "expr"  # type: ignore[attr-defined]
    lazyframe._pulka_path = label  # type: ignore[attr-defined]
    lazyframe._pulka_expr = _collapse_expr(expr_text, limit=256)  # type: ignore[attr-defined]


def _print_metadata_tables(session: Session, args: argparse.Namespace) -> None:
    viewer = session.viewer
    if viewer is None:  # pragma: no cover - defensive guard
        raise RuntimeError("session has no active viewer")

    if args.schema:
        schema_df = _schema_dataframe(viewer)
        _print_polars_dataframe(schema_df)

    if args.glimpse:
        max_rows = args.viewport_rows or getattr(viewer, "view_height", None) or 6
        _print_lazyframe_glimpse(viewer, max_rows=max_rows)


def _schema_dataframe(viewer: Viewer) -> pl.DataFrame:
    sheet = viewer.sheet
    schema = getattr(sheet, "schema", {}) or {}
    rows = [
        {
            "column": name,
            "dtype": str(dtype),
        }
        for name, dtype in schema.items()
    ]
    return pl.DataFrame(rows)


def _print_lazyframe_glimpse(viewer: Viewer, max_rows: int) -> None:
    sheet = viewer.sheet
    lazyframe = unwrap_lazyframe_handle(sheet.lf)
    lazyframe.glimpse(max_rows=max(1, int(max_rows)))


def _expr_preview_dataframe(session: Session, *, max_rows: int | None) -> pl.DataFrame:
    viewer = session.viewer
    if viewer is None:  # pragma: no cover - defensive guard
        raise RuntimeError("session has no active viewer")
    viewer.update_terminal_metrics()
    viewer.clamp()

    sheet = viewer.sheet
    columns = getattr(viewer, "visible_cols", None)
    if not columns:
        columns = list(getattr(sheet, "columns", []))
    if not columns:
        columns = list(sheet.schema.keys())

    row_limit = max_rows or getattr(viewer, "view_height", None) or 25
    row_limit = max(1, int(row_limit))

    table_slice = sheet.fetch_slice(0, row_limit, columns)
    return dataframe_from_table_slice(table_slice)


def _print_polars_dataframe(df: pl.DataFrame) -> None:
    tbl_rows = df.height
    tbl_cols = len(df.columns)
    config: dict[str, int] = {}
    if tbl_rows:
        config["tbl_rows"] = max(tbl_rows, 10)
    if tbl_cols:
        config["tbl_cols"] = tbl_cols
    width = get_terminal_size((160, 40)).columns
    if width:
        config["tbl_width_chars"] = max(80, width - 2)
    if config:
        with pl.Config(**config):
            print(df)
        return
    print(df)


def _finish_headless(session: Session, args: argparse.Namespace) -> None:
    if args.repro_export and session.recorder.enabled:
        try:
            export_path = session.recorder.export_repro_slice(
                session=session, row_margin=10, include_all_columns=False
            )
            print(f"Repro export saved to: {export_path}")
        except Exception as exc:  # pragma: no cover - IO guard
            print(f"Repro export failed: {exc}")

    if session.recorder.enabled:
        session.recorder.on_process_exit(reason="cli")
