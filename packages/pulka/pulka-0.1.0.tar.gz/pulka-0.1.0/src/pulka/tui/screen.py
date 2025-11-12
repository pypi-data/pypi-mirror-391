"""
TUI screen management for Pulka.

This module manages the sheet stack, viewer state, and dialog handling
within the terminal user interface.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterator, Sequence
from contextlib import suppress
from dataclasses import dataclass, field
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from typing import TYPE_CHECKING, Protocol

import polars as pl
from prompt_toolkit import Application
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.filters import Condition
from prompt_toolkit.formatted_text import ANSI, StyleAndTextTuples
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.key_binding import KeyBindings, merge_key_bindings
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    Float,
    FloatContainer,
    HSplit,
    VSplit,
    Window,
)
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension
from prompt_toolkit.widgets import Box, Button, Dialog, Label, TextArea
from rich.console import Console
from rich.pretty import Pretty

from pulka_builtin_plugins.freq.plugin import open_frequency_viewer
from pulka_builtin_plugins.transpose.plugin import open_transpose_viewer

from .. import theme
from ..clipboard import copy_to_clipboard
from ..command.parser import CommandDispatchResult
from ..command.registry import CommandContext
from ..command.runtime import CommandRuntimeResult
from ..config import use_prompt_toolkit_table
from ..core.engine.contracts import TableSlice
from ..core.engine.polars_adapter import table_slice_from_dataframe
from ..core.viewer import Viewer, viewer_public_state
from ..data.filter_lang import FilterError
from ..logging import Recorder, frame_hash, viewer_state_snapshot

if TYPE_CHECKING:  # pragma: no cover - import for type checking only
    from ..api.session import Session
from .controllers.column_insight import ColumnInsightController
from .controls.column_insight_panel import ColumnInsightPanel
from .ui_hooks import PromptToolkitViewerUIHooks

# Constants
_STACK_MIN_SIZE = 2  # Minimum stack size for frequency view filters
_HISTORY_MAX_SIZE = 20  # Maximum size for search/filter history
_CELL_MODAL_CHROME_HEIGHT = 8  # Non-text area rows needed by the cell modal


def _select_source_viewer(viewers: Sequence[Viewer], column: str) -> Viewer | None:
    """Return the most recent non-derived viewer whose sheet exposes ``column``."""

    for viewer in reversed(viewers):
        if getattr(viewer, "is_hist_view", False) or getattr(viewer, "is_freq_view", False):
            continue
        schema = getattr(viewer.sheet, "schema", {}) or {}
        if column in schema:
            return viewer
    return None


@dataclass
class _ColumnSearchState:
    """Mutable state tracked while the column search feature is active."""

    query: str | None = None
    matches: list[int] = field(default_factory=list)
    position: int | None = None

    def clear(self) -> None:
        """Reset the stored query and matches."""

        self.query = None
        self.matches.clear()
        self.position = None

    def set(self, query: str, matches: list[int], *, current_col: int) -> None:
        """Store a fresh query and its matches."""

        self.query = query
        self._apply_matches(matches, current_col=current_col, preserve_position=False)

    def recompute(self, matches: list[int], *, current_col: int) -> None:
        """Refresh matches for an existing query while keeping position when possible."""

        self._apply_matches(matches, current_col=current_col, preserve_position=True)

    def _apply_matches(
        self, matches: list[int], *, current_col: int, preserve_position: bool
    ) -> None:
        previous_position = self.position if preserve_position else None
        self.matches = list(matches)
        if not self.matches:
            self.position = None
            return

        if current_col in self.matches:
            self.position = self.matches.index(current_col)
        elif previous_position is not None and previous_position < len(self.matches):
            self.position = previous_position
        else:
            self.position = 0


class ColumnNameCompleter(Completer):
    """Prompt-toolkit completer that suggests column names."""

    def __init__(self, columns, *, mode: str = "expr"):
        self._columns = list(columns)
        self._mode = mode
        # Pre-sort columns for better UX
        identifier_columns = [name for name in columns if name.isidentifier()]
        self._sorted_identifier_columns = sorted(
            identifier_columns, key=lambda x: (len(x), x.lower())
        )
        non_identifier_columns = [name for name in columns if not name.isidentifier()]
        self._sorted_non_identifier_columns = sorted(
            non_identifier_columns, key=lambda x: (len(x), x.lower())
        )
        self._sorted_all_columns = sorted(columns, key=lambda x: (len(x), x.lower()))

    def get_completions(self, document, complete_event):
        text = document.text_before_cursor

        if self._mode == "plain":
            prefix = text
            prefix_lower = prefix.lower()
            start = -len(prefix)

            candidates = self._sorted_all_columns
            matched = False
            for name in candidates:
                if not prefix_lower or prefix_lower in name.lower():
                    matched = True
                    yield Completion(name, start_position=start, display_meta="column")

            if not matched and complete_event.completion_requested:
                for name in candidates:
                    yield Completion(name, start_position=start, display_meta="column")
            return

        if self._mode == "sql":
            yield from self._sql_completions(text, complete_event)
            return

        # Expression mode completions (default)
        attr_match = re.search(r"c\.([A-Za-z_]\w*)?$", text)
        if attr_match:
            prefix = attr_match.group(1) or ""
            prefix_lower = prefix.lower()

            for name in self._sorted_identifier_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=-len(prefix), display_meta="column")
            return

        bracket_match = re.search(r"c\[(?:\s*['\"])([^'\"]*)$", text)
        if bracket_match:
            prefix = bracket_match.group(1)
            prefix_lower = prefix.lower()

            for name in self._sorted_all_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=-len(prefix), display_meta="column")

    def _sql_completions(self, text: str, complete_event):
        # Handle current token inside double quotes
        dq_match = re.search(r'"([^"\\]*)$', text)
        if dq_match:
            prefix = dq_match.group(1)
            prefix_lower = prefix.lower()
            start = -len(prefix)
            for name in self._sorted_all_columns:
                escaped_name = name.replace('"', '""')
                if escaped_name.lower().startswith(prefix_lower):
                    replacement = escaped_name + '"'
                    yield Completion(
                        replacement,
                        start_position=start,
                        display_meta="column",
                    )
            return

        # Handle table alias dot notation (e.g. data.col)
        dot_match = re.search(r"\.([A-Za-z_][A-Za-z0-9_]*)?$", text)
        if dot_match:
            prefix = dot_match.group(1) or ""
            prefix_lower = prefix.lower()
            start = -len(prefix)
            for name in self._sorted_identifier_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=start, display_meta="column")
            return

        # Handle bare identifiers
        ident_match = re.search(r"([A-Za-z_][A-Za-z0-9_]*)$", text)
        if ident_match:
            prefix = ident_match.group(1)
            prefix_lower = prefix.lower()
            start = -len(prefix)
            for name in self._sorted_identifier_columns:
                if name.lower().startswith(prefix_lower):
                    yield Completion(name, start_position=start, display_meta="column")
            return

        # Fallback: offer all columns when completion explicitly requested
        if complete_event.completion_requested:
            for name in self._sorted_identifier_columns:
                yield Completion(name, start_position=0, display_meta="column")
            for name in self._sorted_non_identifier_columns:
                yield Completion(
                    self._quote_identifier(name),
                    start_position=0,
                    display_meta="column",
                )

    @staticmethod
    def _quote_identifier(name: str) -> str:
        escaped = name.replace('"', '""')
        return f'"{escaped}"'


class Screen:
    def __init__(
        self,
        viewer: Viewer,
        recorder: Recorder | None = None,
        *,
        on_shutdown: Callable[[Session], None] | None = None,
    ):
        self.viewer = viewer
        self.session = viewer.session
        if self.session is None:
            raise RuntimeError("Screen requires a session-bound viewer")
        self._on_shutdown = on_shutdown
        self.commands = self.session.commands
        self._runtime = self.session.command_runtime
        self._recorder = recorder or self.session.recorder
        self._runtime.prepare_viewer(self.viewer)
        self.view_stack = self.session.view_stack
        self._insight_controller: ColumnInsightController | None = None
        self._insight_enabled = self._initial_insight_enabled()
        self._insight_allowed = len(self.view_stack) <= 1
        self._jobs: dict[Viewer, object] = {}  # Jobs for background processing
        self._view_stack_unsubscribe = self.view_stack.add_active_viewer_listener(
            self._on_active_viewer_changed
        )
        # Use a getter that applies queued moves per frame (capped)
        self._pending_row_delta = 0
        self._pending_col_delta = 0
        # Allow tuning via env; default to 3 steps/frame
        try:
            from ..utils import _get_int_env

            self._max_steps_per_frame = max(
                1, _get_int_env("PULKA_MAX_STEPS_PER_FRAME", "PD_MAX_STEPS_PER_FRAME", 3)
            )
        except Exception:
            self._max_steps_per_frame = 3
        self._base_max_steps_per_frame = self._max_steps_per_frame
        use_ptk_table = self._should_use_ptk_table()
        self._table_control = (
            self._build_table_control()
            if use_ptk_table
            else FormattedTextControl(self._get_table_text)
        )
        self._use_ptk_table = use_ptk_table
        self._status_control = FormattedTextControl(self._get_status_text)
        self._last_status_fragments: StyleAndTextTuples | None = None
        self._last_status_plain: str | None = None
        self._table_window = Window(
            content=self._table_control,
            wrap_lines=False,
            always_hide_cursor=not use_ptk_table,
        )
        self._insight_panel = ColumnInsightPanel()
        self._insight_control = FormattedTextControl(lambda: self._insight_panel.render_fragments())
        self._insight_window = Window(
            content=self._insight_control,
            width=Dimension.exact(self._insight_panel.width),
            wrap_lines=True,
            always_hide_cursor=True,
        )
        insight_filter = Condition(lambda: self._insight_enabled and self._insight_allowed)
        self._insight_border = ConditionalContainer(
            content=Window(
                width=Dimension.exact(1),
                char="│",
                style="class:table.separator",
                always_hide_cursor=True,
            ),
            filter=insight_filter,
        )
        self._insight_border_padding = ConditionalContainer(
            content=Window(
                width=Dimension.exact(1),
                char=" ",
                always_hide_cursor=True,
            ),
            filter=insight_filter,
        )
        self._insight_container = ConditionalContainer(
            content=self._insight_window,
            filter=insight_filter,
        )
        self._status_window = Window(
            height=1,
            content=self._status_control,
            wrap_lines=False,
            always_hide_cursor=True,
        )
        table_row = VSplit(
            [
                self._table_window,
                self._insight_border,
                self._insight_border_padding,
                self._insight_container,
            ],
            padding=0,
        )
        body = HSplit([table_row, self._status_window])
        self.window = FloatContainer(content=body, floats=[])
        self._modal_float: Float | None = None
        self._modal_context: dict[str, object] | None = None
        self._search_history: list[str] = []
        self._expr_filter_history: list[str] = []
        self._sql_filter_history: list[str] = []
        self._command_history: list[str] = []
        self._command_history.append("write output.parquet")
        self._col_search_history: list[str] = []
        self._col_search_state = _ColumnSearchState()

        kb = KeyBindings()
        modal_inactive = Condition(lambda: self._modal_float is None)

        @kb.add("escape", filter=~modal_inactive, eager=True)
        def _(event):
            self._record_key_event(event)
            ctx = self._modal_context
            ctx_type = ctx.get("type") if ctx else None
            if ctx and ctx_type in {"expr_filter", "sql_filter"}:
                # Check if filter field has text; if so, clear it first
                filter_field = ctx.get("field")
                if filter_field and filter_field.text:
                    filter_field.text = ""
                    filter_field.buffer.cursor_position = 0
                    return
            self._remove_modal(event.app)
            if ctx:
                if ctx_type == "search":
                    self.viewer.status_message = "search canceled"
                elif ctx_type == "expr_filter":
                    self.viewer.status_message = "filter canceled"
                elif ctx_type == "sql_filter":
                    self.viewer.status_message = "SQL filter canceled"
                elif ctx_type == "column_search":
                    self.viewer.status_message = "column search canceled"
                    self._clear_column_search()
                elif ctx_type == "command":
                    self.viewer.status_message = "command canceled"
            self.refresh()

        @kb.add("q", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            # Back if on a derived view; quit if at root
            if len(self.view_stack) > 1:
                self._pop_viewer()
                self.refresh()
            else:
                event.app.exit()

        @kb.add("c-r", filter=modal_inactive, eager=True)
        def _(event):
            self._record_key_event(event)
            self._reload_dataset()

        # Move
        @kb.add("j", filter=modal_inactive)
        @kb.add("down", filter=modal_inactive)
        def _(event):
            self._clear_g_buf()
            self._execute_command("down")
            self._record_key_event(event)
            self.refresh()

        @kb.add("k", filter=modal_inactive)
        @kb.add("up", filter=modal_inactive)
        def _(event):
            self._clear_g_buf()
            self._execute_command("up")
            self._record_key_event(event)
            self.refresh()

        def _handle_chorded_nav(event, primary: str, chord: str) -> None:
            buffer_flag = getattr(self, "_g_buf", 0)
            self._record_key_event(event)
            if buffer_flag == 1:
                self._execute_command(chord)
                self._g_buf = 0
            else:
                self._execute_command(primary)
            self.refresh()

        @kb.add("h", filter=modal_inactive)
        @kb.add("left", filter=modal_inactive)
        def _(event):
            _handle_chorded_nav(event, "left", "first_overall")

        @kb.add("H", filter=modal_inactive)
        def _(event):
            _handle_chorded_nav(event, "slide_left", "slide_first")

        @kb.add("l", filter=modal_inactive)
        @kb.add("right", filter=modal_inactive)
        def _(event):
            _handle_chorded_nav(event, "right", "last_overall")

        @kb.add("L", filter=modal_inactive)
        def _(event):
            _handle_chorded_nav(event, "slide_right", "slide_last")

        @kb.add("pageup", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            self._clear_g_buf()
            self._execute_command("pageup")
            self.refresh()

        @kb.add("pagedown", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            self._clear_g_buf()
            self._execute_command("pagedown")
            self.refresh()

        @kb.add("y", "y", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            self._clear_g_buf()
            self._execute_command("yank_cell")
            self.refresh()

        @kb.add("g", filter=modal_inactive, eager=True)  # gg top
        def _(event):
            self._record_key_event(event)
            buf = getattr(self, "_g_buf", 0)
            if buf == 1:
                self._execute_command("top")
                self._g_buf = 0
                self.refresh(skip_metrics=True)
            else:
                self._g_buf = 1
                buffer = getattr(event.app, "current_buffer", None)
                if buffer is not None:
                    buffer.reset(append_to_history=False)

        @kb.add("G", filter=modal_inactive)  # bottom (best effort)
        def _(event):
            self._record_key_event(event)
            self._clear_g_buf()
            self._execute_command("bottom")
            self.refresh()

        @kb.add("0", filter=modal_inactive)  # first col
        def _(event):
            self._record_key_event(event)
            self._clear_g_buf()
            self._execute_command("first")
            self.refresh()

        @kb.add("$", filter=modal_inactive)  # last col
        def _(event):
            self._record_key_event(event)
            self._clear_g_buf()
            self._execute_command("last")
            self.refresh()

        @kb.add("_", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            # Support both '_' and 'g_' using the existing g-buffer
            if getattr(self, "_g_buf", 0) == 1:
                # g_
                self._execute_command("maxall")
                self._g_buf = 0
            else:
                # _
                self._execute_command("maxcol")
            self.refresh()

        @kb.add("z", filter=modal_inactive)  # center current row
        def _(event):
            self._record_key_event(event)
            self._execute_command("center")
            self.refresh()

        @kb.add("<", filter=modal_inactive)  # prev different value
        def _(event):
            self._record_key_event(event)
            self._execute_command("prev_different")
            self.refresh()

        @kb.add(">", filter=modal_inactive)  # next different value
        def _(event):
            self._record_key_event(event)
            self._execute_command("next_different")
            self.refresh()

        @kb.add("s", filter=modal_inactive)  # sort toggle by current column
        def _(event):
            self._record_key_event(event)
            self._execute_command("sort")
            self.refresh()

        @kb.add("e", filter=modal_inactive)  # expression filter
        def _(event):
            self._record_key_event(event)
            self._open_filter_modal(event)

        @kb.add("f", filter=modal_inactive)  # SQL filter
        def _(event):
            self._record_key_event(event)
            self._open_sql_filter_modal(event)

        @kb.add("c", filter=modal_inactive)  # column search modal
        def _(event):
            self._record_key_event(event)
            self._open_column_search_modal(event)

        @kb.add("/", filter=modal_inactive)  # search current column
        def _(event):
            self._record_key_event(event)
            self._open_search_modal(event)

        @kb.add("n", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            if self._handle_column_search_navigation(forward=True):
                self.refresh()
                return
            self._execute_command("next_diff")
            self.refresh()

        @kb.add("N", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            if self._handle_column_search_navigation(forward=False):
                self.refresh()
                return
            self._execute_command("prev_diff")
            self.refresh()

        @kb.add("r", filter=modal_inactive)  # reset
        def _(event):
            self._record_key_event(event)
            self._execute_command("reset")
            self.refresh()

        @kb.add("@", filter=modal_inactive)  # flight recorder toggle
        def _(event):
            self._toggle_recorder(event)

        @kb.add(":", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            self._open_command_modal(event)

        @kb.add("?", filter=modal_inactive)  # schema
        def _(event):
            self._record_key_event(event)
            # In TUI mode, show schema in a modal rather than using the command
            schema_text = "\n".join(f"{k}: {v}" for k, v in self.viewer.sheet.schema.items())
            self._open_text_modal(event, "Schema", schema_text)

        @kb.add("i", filter=modal_inactive)  # toggle insight panel
        def _(event):
            self._record_key_event(event)
            self.set_insight_panel()

        @kb.add("C", filter=modal_inactive)  # column summary (Shift+C)
        def _(event):
            self._record_key_event(event)
            if not self.viewer.columns:
                return
            self._execute_command("summary")
            self.refresh()

        @kb.add("F", filter=modal_inactive)  # frequency table of the current column
        def _(event):
            self._record_key_event(event)
            if not self.viewer.columns:
                return
            colname = self.viewer.columns[self.viewer.cur_col]
            source_viewer = _select_source_viewer(self.view_stack.viewers, colname)
            if source_viewer is None:
                self.viewer.status_message = f"frequency view unavailable for column {colname}"
                self.refresh()
                return
            try:
                self.viewer = open_frequency_viewer(
                    source_viewer,
                    colname,
                    session=self.session,
                    view_stack=self.view_stack,
                    screen=self,
                )
            except Exception as exc:
                self.viewer.status_message = f"freq error: {exc}"[:120]
            self.refresh()

        @kb.add("T", filter=modal_inactive)  # transpose view (Shift+T)
        def _(event):
            self._record_key_event(event)
            if not self.viewer.columns:
                return
            try:
                self.viewer = open_transpose_viewer(
                    self.viewer,
                    session=self.session,
                    view_stack=self.view_stack,
                )
            except Exception as exc:
                self.viewer.status_message = f"transpose error: {exc}"[:120]
            self.refresh()

        @kb.add("-", filter=modal_inactive)  # hide current column
        def _(event):
            self._record_key_event(event)
            self._execute_command("hide")
            self.refresh()

        @kb.add("g", "v", filter=modal_inactive)  # unhide all columns
        def _(event):
            self._record_key_event(event)
            self._execute_command("unhide")
            self.refresh()

        @kb.add("u", filter=modal_inactive)  # undo last operation
        def _(event):
            self._record_key_event(event)
            self._execute_command("undo")
            self.refresh()

        @kb.add("U", filter=modal_inactive)  # redo last operation
        def _(event):
            self._record_key_event(event)
            self._execute_command("redo")
            self.refresh()

        # Enter key binding for frequency views and normal views
        @kb.add("enter", filter=modal_inactive)
        def _(event):
            self._record_key_event(event)
            # Preserve frequency view interaction semantics
            if (
                len(self.view_stack) > 1
                and hasattr(self.viewer, "is_freq_view")
                and getattr(self.viewer, "is_freq_view", False)
            ):
                self._filter_by_pick()
                return

            self._open_cell_value_modal(event)

        self.app = Application(
            layout=Layout(self.window, focused_element=self._table_window),
            key_bindings=kb,
            full_screen=True,
            mouse_support=False,
            style=theme.APP_STYLE,
        )

        self._viewer_ui_hooks = PromptToolkitViewerUIHooks(self.app)
        attach_hooks = getattr(self._table_control, "attach_ui_hooks", None)
        if callable(attach_hooks):
            hooks = attach_hooks(self._viewer_ui_hooks)
            if hooks is not None:
                self._viewer_ui_hooks = hooks
        self.session.set_viewer_ui_hooks(self._viewer_ui_hooks)

        self._insight_controller = ColumnInsightController(
            viewer=self.viewer,
            panel=self._insight_panel,
            recorder=self._recorder,
            invalidate=self.app.invalidate,
            call_soon=self._viewer_ui_hooks.call_soon,
        )
        self._apply_insight_state(refresh=True)

    def _should_use_ptk_table(self) -> bool:
        return use_prompt_toolkit_table()

    def _initial_insight_enabled(self) -> bool:
        env_value = os.getenv("PULKA_INSIGHT_PANEL")
        if env_value is None:
            return True
        normalized = env_value.strip().lower()
        if normalized in {"0", "false", "off", "no"}:
            return False
        if normalized in {"1", "true", "on", "yes"}:
            return True
        return True

    def _apply_budget_plan(self, plan) -> None:
        multiplier = float(getattr(plan, "coalesce_multiplier", 1.0) or 1.0)
        base = getattr(self, "_base_max_steps_per_frame", self._max_steps_per_frame)
        if multiplier > 1.0:
            boosted = max(base, int(round(base * multiplier)))
            self._max_steps_per_frame = max(base, min(12, boosted))
        else:
            self._max_steps_per_frame = base

    def _build_table_control(self):
        from .controls.table_control import TableControl

        return TableControl(
            self.viewer,
            apply_pending_moves=self._apply_pending_moves,
            poll_background_jobs=self._poll_background_jobs,
            set_status=self._set_status_from_table,
            apply_budget_plan=self._apply_budget_plan,
            recorder=self._recorder,
        )

    def _clear_g_buf(self) -> None:
        """Reset the pending g-command state."""
        if hasattr(self, "_g_buf"):
            self._g_buf = 0

    def _on_active_viewer_changed(self, viewer: Viewer) -> None:
        previous = getattr(self, "viewer", None)
        self.viewer = viewer
        self._runtime.prepare_viewer(viewer)
        table_control = getattr(self, "_table_control", None)
        update_viewer = getattr(table_control, "update_viewer", None)
        if callable(update_viewer):
            update_viewer(viewer)
        if previous is not None and previous is not viewer:
            self._clear_column_search()
        controller = getattr(self, "_insight_controller", None)
        if controller is not None:
            controller.on_viewer_changed(viewer)
        allowed = len(self.view_stack) <= 1
        if allowed != self._insight_allowed:
            self._insight_allowed = allowed
            self._apply_insight_state(refresh=allowed)
        self._prune_stale_jobs()

    def _prune_stale_jobs(self) -> None:
        active = set(self.view_stack.viewers)
        for stale_viewer, job in list(self._jobs.items()):
            if stale_viewer not in active:
                if job is not None and hasattr(job, "cancel"):
                    with suppress(Exception):
                        job.cancel()
                self._jobs.pop(stale_viewer, None)

    def _mutate_context(self, context: CommandContext) -> None:
        context.screen = self

    def _finalise_runtime_result(
        self, result: CommandRuntimeResult
    ) -> CommandDispatchResult | None:
        if result.message:
            self.viewer.status_message = result.message
        dispatch = result.dispatch
        if dispatch and dispatch.spec.name == "search":
            self._clear_column_search()
        return dispatch

    def _execute_command(
        self, name: str, args: list[str] | None = None, *, repeat: int = 1
    ) -> CommandDispatchResult | None:
        """Execute a command through the session command runtime."""

        invocation_args = list(args or [])
        result = self._runtime.invoke(
            name,
            args=invocation_args,
            repeat=repeat,
            source="tui",
            context_mutator=self._mutate_context,
        )
        return self._finalise_runtime_result(result)

    def _queue_move(self, dr: int = 0, dc: int = 0) -> None:
        # Accumulate deltas; they'll be applied (capped) during next paint
        if dr != 0:
            self._pending_row_delta += 1 if dr > 0 else -1
            # prevent runaway accumulation
            self._pending_row_delta = max(-100, min(100, self._pending_row_delta))
        if dc != 0:
            self._pending_col_delta += 1 if dc > 0 else -1
            self._pending_col_delta = max(-100, min(100, self._pending_col_delta))

    def _record_key_event(self, event) -> None:
        # Record with structured recorder if available
        if self._recorder and self._recorder.enabled:
            try:
                sequence = [kp.key for kp in event.key_sequence]
                data = [kp.data for kp in event.key_sequence]
            except Exception:
                sequence = []
                data = []
            payload = {"sequence": sequence, "data": data}
            payload["repeat"] = bool(getattr(event, "is_repeat", False))
            self._recorder.record("key", payload)

    def _toggle_recorder(self, event) -> None:
        """Toggle the structured recorder on/off from the TUI."""
        recorder = self._recorder
        if recorder is None:
            self.viewer.status_message = "recorder unavailable"
            self.refresh()
            return

        self._record_key_event(event)

        try:
            user_command = event.key_sequence[0].key if event.key_sequence else "@"
        except Exception:
            user_command = "@"

        if recorder.enabled:
            recorder.record(
                "control", {"action": "record_off", "source": "tui", "key": user_command}
            )
            path = recorder.flush_and_clear(reason="tui-toggle")
            recorder.disable()
            if path is not None:
                copied = self._copy_path_to_clipboard(path)
                if copied:
                    self.viewer.status_message = (
                        f"flight recorder stopped - {path.name} (path copied to clipboard)"
                    )
                else:
                    self.viewer.status_message = f"flight recorder stopped - saved to {path.name}"
            else:
                self.viewer.status_message = "flight recorder disabled"
            self.refresh()
            return

        recorder.enable()
        recorder.ensure_env_recorded()
        source_path = getattr(self.viewer, "_source_path", None)
        schema = getattr(self.viewer.sheet, "schema", {})
        if source_path is not None:
            recorder.record_dataset_open(path=source_path, schema=schema, lazy=True)
        recorder.record("control", {"action": "record_on", "source": "tui", "key": user_command})
        self.viewer.status_message = "flight recorder started"
        self.refresh()

    def _reload_dataset(self) -> None:
        """Reload the currently open dataset if it originated from a path."""

        dataset_path = getattr(self.session, "dataset_path", None)
        if dataset_path is None:
            self.viewer.status_message = "reload requires a file-backed dataset"
            self.refresh()
            return

        try:
            self.session.open(dataset_path)
        except Exception as exc:  # pragma: no cover - heavy IO guard
            self.viewer.status_message = f"reload failed: {exc}"
        else:
            self.viewer.status_message = f"reloaded {dataset_path}"
        self.refresh()

    def _apply_insight_state(self, *, refresh: bool = False) -> None:
        controller = getattr(self, "_insight_controller", None)
        effective = self._insight_enabled and self._insight_allowed
        if controller is not None:
            controller.set_enabled(effective)
            if effective and refresh:
                with suppress(Exception):
                    controller.on_refresh()
        if not effective and not self._insight_allowed:
            self._insight_panel.set_unavailable("Insight available on base sheet only.")
        self.app.invalidate()

    def set_insight_panel(self, enabled: bool | None = None) -> bool:
        """Toggle or explicitly set the insight sidecar visibility."""

        if enabled is None:
            enabled = not self._insight_enabled
        self._insight_enabled = bool(enabled)
        self._apply_insight_state(refresh=self._insight_enabled)
        return self._insight_enabled

    @staticmethod
    def _copy_path_to_clipboard(path: Path) -> bool:
        """Attempt to copy the given path to the system clipboard."""
        return copy_to_clipboard(str(path))

    def _apply_pending_moves(self) -> None:
        # Apply up to N moves per axis this frame, for smoother scrolling
        steps = min(self._max_steps_per_frame, abs(self._pending_row_delta))
        if steps:
            if self._pending_row_delta > 0:
                for _ in range(steps):
                    self.viewer.move_down()
                self._pending_row_delta -= steps
            else:
                for _ in range(steps):
                    self.viewer.move_up()
                self._pending_row_delta += steps
        steps = min(self._max_steps_per_frame, abs(self._pending_col_delta))
        if steps:
            if self._pending_col_delta > 0:
                for _ in range(steps):
                    self.viewer.move_right()
                self._pending_col_delta -= steps
            else:
                for _ in range(steps):
                    self.viewer.move_left()
                self._pending_col_delta += steps

    def _get_table_text(self):
        # Coalesce rapid key repeats by applying pending deltas here
        self._apply_pending_moves()
        self._poll_background_jobs()
        # Import the render table function here to avoid circular imports
        from ..render.table import render_table

        recorder = self._recorder if getattr(self, "_recorder", None) else None
        if recorder and recorder.enabled:
            with recorder.perf_timer(
                "render.table",
                payload={"context": "tui", "trigger": "refresh"},
            ):
                body = render_table(self.viewer)
        else:
            body = render_table(self.viewer)

        # Precompute status text so the footer stays in sync with the latest render
        from ..render.status_bar import render_status_line

        status_fragments: StyleAndTextTuples = []
        if recorder and recorder.enabled:
            with recorder.perf_timer(
                "render.status",
                payload={"context": "tui", "trigger": "refresh"},
            ):
                status_fragments = render_status_line(self.viewer)
        else:
            status_fragments = render_status_line(self.viewer)
        self._set_status_from_table(status_fragments)
        self.viewer.acknowledge_status_rendered()
        status_text = self._last_status_plain or ""
        if self._recorder and self._recorder.enabled:
            state_snapshot = viewer_state_snapshot(self.viewer)
            self._recorder.record_state(state_snapshot)
            if status_text:
                self._recorder.record_status(status_text)
            frame_capture = f"{body}\n{status_text}" if status_text else body
            if self._insight_enabled:
                panel_block = self._insight_panel.render_for_recorder()
                if panel_block:
                    frame_capture = f"{frame_capture}\n\n{panel_block}"
            self._recorder.record_frame(
                frame_text=frame_capture,
                frame_hash=frame_hash(frame_capture),
            )
        return ANSI(body).__pt_formatted_text__()

    def _get_status_text(self):
        viewer = self.viewer
        status_dirty = bool(viewer.is_status_dirty())
        if status_dirty:
            # Import lazily to avoid circular dependency at module import time
            from ..render.status_bar import render_status_line

            self._set_status_from_table(render_status_line(viewer))
            viewer.acknowledge_status_rendered()
        elif self._last_status_fragments is None:
            from ..render.status_bar import render_status_line

            self._set_status_from_table(render_status_line(viewer))
            viewer.acknowledge_status_rendered()
        return self._last_status_fragments or [("", "")]

    def _set_status_from_table(self, fragments: StyleAndTextTuples) -> None:
        stored = list(fragments)
        self._last_status_fragments = stored
        self._last_status_plain = "".join(part for _, part in stored)

    def _pop_viewer(self) -> None:
        removed = self.view_stack.pop()
        if removed is None:
            return
        job = self._jobs.pop(removed, None)
        if job is not None and hasattr(job, "cancel"):
            with suppress(Exception):
                job.cancel()

    def refresh(self, *, skip_metrics: bool = False):
        if not skip_metrics:
            self.viewer.update_terminal_metrics()
        self.viewer.clamp()
        controller = getattr(self, "_insight_controller", None)
        if controller is not None:
            controller.on_refresh()
        with suppress(Exception):
            self._viewer_ui_hooks.invalidate()

    def _poll_background_jobs(self) -> None:
        jobs = list(self._jobs.items())
        for v, job in jobs:
            if hasattr(job, "consume_update"):
                done = job.consume_update(v)
                if done:
                    self._jobs.pop(v, None)

    def run(self):
        try:
            self.app.run()
        finally:
            unsubscribe = getattr(self, "_view_stack_unsubscribe", None)
            if unsubscribe is not None:
                unsubscribe()
            session = self.session
            if session is not None and self._on_shutdown is not None:
                with suppress(Exception):
                    self._on_shutdown(session)
            if session is not None:
                with suppress(Exception):
                    session.close()
                recorder = getattr(session, "recorder", None)
                if recorder is not None and recorder.enabled:
                    with suppress(Exception):
                        recorder.on_process_exit(reason="tui")

    def _display_modal(
        self,
        app,
        container,
        *,
        focus=None,
        context_type: str | None = None,
        payload: dict[str, object] | None = None,
        width: int | None = None,
        height: int | None = None,
    ) -> None:
        if self._modal_float is not None:
            self._remove_modal(app, restore_focus=False)
        float_kwargs: dict[str, object] = {"z_index": 10}
        size = None
        try:
            size = app.output.get_size()
        except Exception:
            size = None

        base_container = getattr(container, "container", container)
        measured_width: int | None = None
        measured_height: int | None = None
        if hasattr(base_container, "preferred_width"):
            try:
                dim_w = base_container.preferred_width(size.columns if size else 80)
                measured_width = dim_w.preferred or dim_w.max or dim_w.min
            except Exception:
                measured_width = None
        if hasattr(base_container, "preferred_height"):
            try:
                dim_h = base_container.preferred_height(
                    size.columns if size else 80,
                    size.rows if size else 24,
                )
                measured_height = dim_h.preferred or dim_h.max or dim_h.min
            except Exception:
                measured_height = None

        actual_width = width if width is not None else measured_width
        if actual_width is not None:
            float_kwargs["width"] = actual_width

        if height is not None:
            float_kwargs["height"] = height

        if size is not None and actual_width is not None:
            float_kwargs["left"] = max(0, (size.columns - actual_width) // 2)
        if size is not None:
            target_height = height if height is not None else measured_height
            if target_height is not None:
                float_kwargs["top"] = max(0, (size.rows - target_height) // 3)
        modal = Float(content=container, **float_kwargs)
        self.window.floats.append(modal)
        self._modal_float = modal
        ctx: dict[str, object] = {}
        if payload:
            ctx.update(payload)
        if context_type is not None:
            ctx.setdefault("type", context_type)
        self._modal_context = ctx or None
        if focus is not None:
            app.layout.focus(focus)
        app.invalidate()

    def _calculate_modal_dimensions(
        self,
        app,
        *,
        target_width: int,
        target_height: int,
    ) -> tuple[int, int]:
        """Determine modal dimensions respecting terminal size constraints."""

        width = max(1, target_width)
        height = max(1, target_height)

        size = None
        try:
            size = app.output.get_size()
        except Exception:
            size = None

        if size is not None:
            columns = max(1, size.columns)
            rows = max(1, size.rows)

            if columns < target_width:
                width = max(10, int(columns * 0.8))
            else:
                width = min(target_width, columns)

            height = max(5, int(rows * 0.8)) if rows < target_height else min(target_height, rows)

            width = max(10, min(width, columns))
            height = max(5, min(height, rows))

        # Ensure there is always enough space for the dialog chrome and a
        # minimal text area.
        height = max(height, 3 + _CELL_MODAL_CHROME_HEIGHT)

        return width, height

    def _remove_modal(self, app, *, restore_focus: bool = True) -> None:
        if self._modal_float is None:
            return
        with suppress(ValueError):
            self.window.floats.remove(self._modal_float)
        self._modal_float = None
        self._modal_context = None
        if restore_focus:
            try:
                windows = list(app.layout.find_all_windows())
            except Exception:
                windows = []
            if self._table_window in windows:
                with suppress(Exception):
                    app.layout.focus(self._table_window)
        app.invalidate()

    def _build_read_only_modal_dialog(
        self,
        *,
        app,
        title: str,
        text_area: TextArea,
    ) -> tuple[Dialog, Button]:
        """Create a dialog with a read-only text area and shared controls."""

        def _close_modal(target_app) -> None:
            self._remove_modal(target_app)
            self.refresh()

        text_kb = KeyBindings()

        @text_kb.add("enter")
        def _close_from_enter(event_) -> None:
            _close_modal(event_.app)

        @text_kb.add("escape")
        def _close_from_escape(event_) -> None:
            _close_modal(event_.app)

        existing_kb = text_area.control.key_bindings
        if existing_kb is None:
            text_area.control.key_bindings = text_kb
        else:
            text_area.control.key_bindings = merge_key_bindings([existing_kb, text_kb])

        body = Box(body=HSplit([text_area], padding=1), padding=1)

        ok_button = Button(text="OK", handler=lambda: _close_modal(app))

        dialog = Dialog(title=title, body=body, buttons=[ok_button])
        return dialog, ok_button

    def _open_cell_value_modal(self, event) -> None:
        """Open a modal showing details about the currently focused cell."""

        if not self.viewer.columns:
            return

        column_name = self.viewer.columns[self.viewer.cur_col]
        row_index = self.viewer.cur_row

        value = None
        value_error: str | None = None
        try:
            slice_ = self.viewer.sheet.fetch_slice(row_index, 1, [column_name])
            if isinstance(slice_, TableSlice):
                table_slice = slice_
            elif isinstance(slice_, pl.DataFrame):
                schema = getattr(self.viewer.sheet, "schema", {})
                table_slice = table_slice_from_dataframe(slice_, schema)
            else:
                table_slice = table_slice_from_dataframe(
                    pl.DataFrame(slice_), getattr(self.viewer.sheet, "schema", {})
                )

            if table_slice.height > 0 and column_name in table_slice.column_names:
                value = table_slice.column(column_name).values[0]
        except Exception as exc:  # pragma: no cover - defensive
            value_error = str(exc)

        target_width = 60
        target_height = 40
        width, height = self._calculate_modal_dimensions(
            event.app,
            target_width=target_width,
            target_height=target_height,
        )
        content_width = max(20, width - 6)

        console_buffer = StringIO()
        console = Console(
            record=True,
            width=content_width,
            highlight=False,
            file=console_buffer,
        )
        if value_error is not None:
            console.print(f"Error: {value_error}")
        else:
            console.print(Pretty(value, expand_all=True, overflow="fold"))

        rendered_text = console.export_text(clear=False)

        # Account for dialog chrome (label, padding, frame, and buttons) so the
        # text area fits within the requested height without triggering the
        # "window too small" warning from prompt_toolkit.
        text_area_height = max(3, height - _CELL_MODAL_CHROME_HEIGHT)

        text_area = TextArea(
            text=rendered_text,
            read_only=True,
            scrollbar=True,
            wrap_lines=True,
            height=text_area_height,
        )

        dialog, ok_button = self._build_read_only_modal_dialog(
            app=event.app,
            title=f"Cell {column_name} @ row {row_index + 1}",
            text_area=text_area,
        )

        self._display_modal(
            event.app,
            dialog,
            focus=ok_button,
            context_type="cell_value",
            payload={"column": column_name, "row": row_index},
            width=width,
            height=height,
        )

    def _filter_by_pick(self) -> None:
        """Apply filter based on the currently selected value in a frequency view."""
        # Get the frequency viewer (current view) and the source viewer (parent)
        if len(self.view_stack) < _STACK_MIN_SIZE:
            return

        freq_viewer = self.viewer
        source_viewer = self.view_stack.parent
        if source_viewer is None:
            return

        # Ensure we're in a frequency view
        if not hasattr(freq_viewer, "is_freq_view") or not getattr(
            freq_viewer, "is_freq_view", False
        ):
            return

        # Get the selected value from the frequency view
        try:
            selected_value = freq_viewer.sheet.get_value_at(freq_viewer.cur_row)
        except Exception:
            self.viewer.status_message = "unable to pick value"
            return

        # Apply the filter to the source view
        try:
            # Build filter expression for the source column
            source_col = freq_viewer.freq_source_col
            if source_col is None:
                self.viewer.status_message = "unknown frequency source"
                return
            # Quote string values
            if isinstance(selected_value, str):
                filter_expr = f"c['{source_col}'] == '{selected_value}'"
            else:
                filter_expr = f"c['{source_col}'] == {selected_value}"

            result = self._runtime.invoke(
                "filter",
                args=[filter_expr],
                source="tui",
                viewer=source_viewer,
                context_mutator=self._mutate_context,
            )
        except Exception as exc:
            self.viewer.status_message = f"filter error: {exc}"
        else:
            if result.message:
                self.viewer.status_message = result.message
                return
            self.viewer.status_message = None
            self._pop_viewer()
            self.refresh()

    def _open_filter_modal(self, event, *, initial_text: str | None = None) -> None:
        # Implementation details omitted for brevity to focus on key logic
        title = "Expression Filter"
        prompt_text = "Polars expression (use c.<column>):"
        default_text = initial_text or ""
        if not default_text:
            kind = getattr(self.viewer, "filter_kind", None)
            if kind in (None, "expr"):
                default_text = getattr(self.viewer, "filter_text", "") or ""
            else:
                default_text = ""
        if not default_text:
            current_col = None
            with suppress(Exception):
                current_col = self.viewer.current_colname()
            if current_col:
                if current_col.isidentifier():
                    default_text = f"c.{current_col}"
                else:
                    safe_name = current_col.replace('"', '\\"')
                    default_text = f'c["{safe_name}"]'

        def accept(buff):
            text = buff.text.strip()
            if text.lower() == "cancel":
                self.viewer.status_message = "filter canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            try:
                result = self._runtime.invoke(
                    "filter",
                    args=[text],
                    source="tui",
                    context_mutator=self._mutate_context,
                    propagate=(FilterError,),
                )
            except FilterError as err:
                self._open_error_modal(
                    event,
                    "Filter Error",
                    str(err),
                    retry=lambda ev: self._open_filter_modal(ev, initial_text=text),
                )
            except Exception as exc:
                self._open_error_modal(
                    event,
                    "Unexpected Error",
                    str(exc),
                    retry=lambda ev: self._open_filter_modal(ev, initial_text=text),
                )
            else:
                dispatch = self._finalise_runtime_result(result)
                if result.message:
                    self._open_error_modal(
                        event,
                        "Filter Error",
                        result.message,
                        retry=lambda ev: self._open_filter_modal(ev, initial_text=text),
                    )
                    return True
                if dispatch is not None:
                    self._record_expr_filter(text)
                self.viewer.status_message = None
                self._remove_modal(event.app)
                self.refresh()
            return True

        history = InMemoryHistory()
        for item in self._expr_filter_history:
            history.append_string(item)

        filter_field = TextArea(
            text=default_text,
            multiline=True,
            height=2,
            accept_handler=accept,
            history=history,
            completer=ColumnNameCompleter(self.viewer.columns),
            complete_while_typing=True,
        )
        filter_field.buffer.cursor_position = len(default_text)

        field_kb = KeyBindings()

        @field_kb.add("enter")
        def _apply_from_enter(event_) -> None:
            event_.current_buffer.validate_and_handle()

        existing_field_kb = filter_field.control.key_bindings
        if existing_field_kb is None:
            filter_field.control.key_bindings = field_kb
        else:
            filter_field.control.key_bindings = merge_key_bindings([existing_field_kb, field_kb])

        content = HSplit(
            [
                Label(prompt_text, dont_extend_height=True),
                filter_field,
            ],
            padding=0,
        )
        body = Box(body=content, padding=1)
        dialog = Dialog(title=title, body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=filter_field,
            context_type="expr_filter",
            payload={"field": filter_field},
            width=60,
        )

    def _open_filter_modal_with_text(self, event, text: str) -> None:
        self._open_filter_modal(event, initial_text=text)

    def _open_sql_filter_modal(self, event, *, initial_text: str | None = None) -> None:
        title = "SQL Filter"
        prompt_text = "Polars SQL WHERE clause (omit the WHERE keyword):"
        default_text = initial_text or getattr(self.viewer, "sql_filter_text", "") or ""
        if not default_text:
            current_col = None
            with suppress(Exception):
                current_col = self.viewer.current_colname()
            if current_col:
                if current_col.isidentifier():
                    default_text = current_col
                else:
                    default_text = ColumnNameCompleter._quote_identifier(current_col)

        def accept(buff):
            raw_text = buff.text
            text = raw_text.strip()
            if text.lower() == "cancel":
                self.viewer.status_message = "SQL filter canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            args = [text] if text else []
            try:
                result = self._runtime.invoke(
                    "sql_filter",
                    args=args,
                    source="tui",
                    context_mutator=self._mutate_context,
                    propagate=(FilterError,),
                )
            except Exception as exc:
                self._open_error_modal(
                    event,
                    "SQL Filter Error",
                    str(exc),
                    retry=lambda ev: self._open_sql_filter_modal(ev, initial_text=raw_text),
                )
            else:
                dispatch = self._finalise_runtime_result(result)
                if result.message:
                    self._open_error_modal(
                        event,
                        "SQL Filter Error",
                        result.message,
                        retry=lambda ev: self._open_sql_filter_modal(ev, initial_text=raw_text),
                    )
                    return True
                if text and dispatch is not None:
                    self._record_sql_filter(text)
                self.viewer.status_message = None
                self._remove_modal(event.app)
                self.refresh()
            return True

        history = InMemoryHistory()
        for item in self._sql_filter_history:
            history.append_string(item)

        filter_field = TextArea(
            text=default_text,
            multiline=True,
            height=2,
            accept_handler=accept,
            history=history,
            completer=ColumnNameCompleter(self.viewer.columns, mode="sql"),
            complete_while_typing=True,
        )
        filter_field.buffer.cursor_position = len(default_text)

        field_kb = KeyBindings()

        @field_kb.add("enter")
        def _apply_from_enter(event_) -> None:
            event_.current_buffer.validate_and_handle()

        existing_field_kb = filter_field.control.key_bindings
        if existing_field_kb is None:
            filter_field.control.key_bindings = field_kb
        else:
            filter_field.control.key_bindings = merge_key_bindings([existing_field_kb, field_kb])

        content = HSplit(
            [
                Label(prompt_text, dont_extend_height=True),
                filter_field,
            ],
            padding=0,
        )
        body = Box(body=content, padding=1)
        dialog = Dialog(title=title, body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=filter_field,
            context_type="sql_filter",
            payload={"field": filter_field},
            width=60,
        )

    def _open_sql_filter_modal_with_text(self, event, text: str) -> None:
        self._open_sql_filter_modal(event, initial_text=text)

    def _open_command_modal(self, event) -> None:
        history = InMemoryHistory()
        for item in self._command_history:
            history.append_string(item)

        def accept(buff):
            raw_text = buff.text
            command_text = raw_text.strip()

            if not command_text:
                self._remove_modal(event.app)
                self.refresh()
                return True

            result = self._runtime.dispatch_raw(
                command_text,
                source="tui",
                context_mutator=self._mutate_context,
            )
            dispatch = self._finalise_runtime_result(result)
            if dispatch is not None:
                self._record_command(command_text)
            self._remove_modal(event.app)
            self.refresh()
            return True

        command_field = TextArea(
            text="",
            multiline=False,
            accept_handler=accept,
            history=history,
        )
        command_field.buffer.cursor_position = 0

        examples = []
        for spec in self.commands.iter_specs():
            hints = spec.ui_hints or {}
            example = hints.get("example") if isinstance(hints, dict) else hints.get("example")
            if example:
                examples.append(str(example))
        unique_examples: list[str] = []
        for example in examples:
            if example not in unique_examples:
                unique_examples.append(example)
        prompt = (
            "Command:"
            if not unique_examples
            else f"Command (e.g. {', '.join(unique_examples[:3])}):"
        )

        content = HSplit(
            [
                Label(prompt, dont_extend_height=True),
                command_field,
            ],
            padding=0,
        )
        body = Box(body=content, padding=1)
        dialog = Dialog(title="Command", body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=command_field,
            context_type="command",
            payload={"field": command_field},
            width=60,
        )

    def _open_search_modal(self, event) -> None:
        def accept(buff):
            text = buff.text.strip()
            if text.lower() == "cancel":
                self.viewer.status_message = "search canceled"
                self._remove_modal(event.app)
                self.refresh()
                return True

            # Apply search to the viewer
            try:
                self.viewer.set_search(text)
                self._clear_column_search()
                self._record_search(text)
                self.viewer.status_message = "search applied"
                self._remove_modal(event.app)
                self.refresh()
            except Exception as exc:
                self.viewer.status_message = f"Search error: {exc}"
            return True

        history = InMemoryHistory()
        for item in self._search_history:
            history.append_string(item)

        search_field = TextArea(
            text="",
            multiline=False,
            accept_handler=accept,
            history=history,
        )
        search_field.buffer.cursor_position = 0

        content = HSplit(
            [
                Label("Substring (current column, case-insensitive):", dont_extend_height=True),
                search_field,
            ],
            padding=0,
        )
        body = Box(body=content, padding=1)
        dialog = Dialog(title="Search", body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=search_field,
            context_type="search",
            payload={"field": search_field},
            width=60,
        )

    def _open_column_search_modal(self, event) -> None:
        """Open the column search modal with history and tab completion."""

        def accept(buff):
            raw_text = buff.text
            query = raw_text.strip()

            if not query or query.lower() == "cancel":
                self.viewer.status_message = "column search canceled"
                self._clear_column_search()
                self._remove_modal(event.app)
                self.refresh()
                return True

            self._remove_modal(event.app)
            success = self._apply_column_search(query)
            self._record_column_search(query)
            if not success:
                self._clear_column_search()
            self.refresh()
            return True

        history = InMemoryHistory()
        for item in self._col_search_history:
            history.append_string(item)

        search_field = TextArea(
            text="",
            multiline=False,
            accept_handler=accept,
            history=history,
            completer=ColumnNameCompleter(self.viewer.columns, mode="plain"),
            complete_while_typing=True,
        )
        search_field.buffer.cursor_position = 0

        content = HSplit(
            [
                Label("Column name (prefix or substring):", dont_extend_height=True),
                search_field,
            ],
            padding=0,
        )
        body = Box(body=content, padding=1)
        dialog = Dialog(title="Column Search", body=body, buttons=[])
        self._display_modal(
            event.app,
            dialog,
            focus=search_field,
            context_type="column_search",
            payload={"field": search_field},
            width=60,
        )

    def _record_search(self, text: str) -> None:
        text = text.strip()
        if not text:
            return
        with suppress(ValueError):
            self._search_history.remove(text)
        self._search_history.append(text)
        if len(self._search_history) > _HISTORY_MAX_SIZE:
            del self._search_history[0]

    def _record_command(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._command_history.remove(cleaned)
        self._command_history.append(cleaned)
        if len(self._command_history) > _HISTORY_MAX_SIZE:
            del self._command_history[0]

    def _record_column_search(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._col_search_history.remove(cleaned)
        self._col_search_history.append(cleaned)
        if len(self._col_search_history) > _HISTORY_MAX_SIZE:
            del self._col_search_history[0]

    def _visible_column_names(self) -> list[str]:
        """Return the names of columns currently visible in the viewport."""

        state = viewer_public_state(self.viewer)
        if state is None:  # pragma: no cover - defensive
            return list(getattr(self.viewer, "visible_cols", getattr(self.viewer, "columns", ())))

        return list(state.visible_columns or state.columns)

    def _apply_column_search(self, query: str) -> bool:
        """Compute matches for ``query`` and focus the first result."""

        matches = self._compute_column_search_matches(query)
        state = self._col_search_state
        state.set(query, matches, current_col=self.viewer.cur_col)
        if not matches:
            self.viewer.status_message = f"column search: no match for '{query}'"
            return False

        target = state.position or 0
        if self._focus_column_search_match(target):
            return True

        self.viewer.status_message = f"column search: unable to focus '{query}'"
        return False

    def _iter_column_search_candidates(self) -> Iterator[tuple[int, str]]:
        """Yield candidate column indices and names for column search ranking."""

        visible_columns = self._visible_column_names()

        visible_filter: set[str] | None = set(visible_columns) if visible_columns else None

        for idx, name in enumerate(self.viewer.columns):
            if visible_filter is not None and name not in visible_filter:
                continue
            yield idx, name

    def _compute_column_search_matches(self, query: str) -> list[int]:
        """Rank matching columns by how closely they match ``query``."""

        query_lower = query.lower()
        ranked: list[tuple[tuple[int, int], int]] = []

        for idx, name in self._iter_column_search_candidates():
            lowered = name.lower()
            if query_lower not in lowered:
                continue
            if lowered == query_lower:
                priority = 0
            elif lowered.startswith(query_lower):
                priority = 1
            else:
                priority = 2
            ranked.append(((priority, idx), idx))

        ranked.sort(key=lambda item: item[0])
        return [idx for _, idx in ranked]

    def _focus_column_search_match(self, position: int) -> bool:
        matches = self._col_search_state.matches
        if position < 0 or position >= len(matches):
            return False

        match_idx = matches[position]
        if match_idx >= len(self.viewer.columns):
            self._recompute_column_search_matches()
            matches = self._col_search_state.matches
            if position < 0 or position >= len(matches):
                return False
            match_idx = matches[position]

        col_name = self.viewer.columns[match_idx]
        moved = self.viewer.goto_col(col_name)
        if moved:
            self._col_search_state.position = position
            total = len(matches)
            self.viewer.status_message = f"column search: {col_name} ({position + 1}/{total})"
        return moved

    def _handle_column_search_navigation(self, *, forward: bool) -> bool:
        """Navigate among column search matches in response to ``n``/``N``."""

        state = self._col_search_state
        if not state.query or not state.matches:
            return False

        self._recompute_column_search_matches()
        matches = state.matches
        if not matches:
            self.viewer.status_message = f"column search: no match for '{state.query}'"
            self._clear_column_search()
            return True

        try:
            anchor = matches.index(self.viewer.cur_col)
        except ValueError:
            anchor = -1 if forward else len(matches)

        step = 1 if forward else -1
        target = anchor + step
        if 0 <= target < len(matches):
            if self._focus_column_search_match(target):
                return True
            self.viewer.status_message = "column search: unable to focus match"
            return True

        direction = "next" if forward else "previous"
        self.viewer.status_message = f"column search: no {direction} match"
        return True

    def _clear_column_search(self) -> None:
        """Reset column search bookkeeping so ``n``/``N`` fall back to row search."""

        self._col_search_state.clear()

    def _recompute_column_search_matches(self) -> None:
        """Refresh cached matches for the active column search query."""

        state = self._col_search_state
        if not state.query:
            state.clear()
            return

        matches = self._compute_column_search_matches(state.query)
        state.recompute(matches, current_col=self.viewer.cur_col)

    def _record_expr_filter(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._expr_filter_history.remove(cleaned)
        self._expr_filter_history.append(cleaned)
        if len(self._expr_filter_history) > _HISTORY_MAX_SIZE:
            del self._expr_filter_history[0]

    def _record_sql_filter(self, text: str) -> None:
        cleaned = text.strip()
        if not cleaned:
            return
        with suppress(ValueError):
            self._sql_filter_history.remove(cleaned)
        self._sql_filter_history.append(cleaned)
        if len(self._sql_filter_history) > _HISTORY_MAX_SIZE:
            del self._sql_filter_history[0]

    def _open_error_modal(self, event, title: str, error_message: str, *, retry=None) -> None:
        """Open a modal dialog to display error messages with proper formatting."""
        text_area = TextArea(
            text=error_message,
            read_only=True,
            scrollbar=True,
            wrap_lines=True,
        )
        msg_kb = KeyBindings()

        def _close(app, event_obj=None) -> None:
            self._remove_modal(app)
            if retry is not None:
                retry_event = event_obj
                if retry_event is None:
                    retry_event = SimpleNamespace(app=app)
                retry(retry_event)
            else:
                self.refresh()

        @msg_kb.add("escape")
        def _close_and_reopen_filter(event) -> None:
            _close(event.app, event)

        @msg_kb.add("enter")
        def _close_enter(event) -> None:
            _close(event.app, event)

        existing = text_area.control.key_bindings
        if existing is None:
            text_area.control.key_bindings = msg_kb
        else:
            text_area.control.key_bindings = merge_key_bindings([existing, msg_kb])

        content = HSplit([text_area], padding=0)
        body = Box(body=content, padding=1)
        go_back_button = Button(text="Go back", handler=lambda: _close(event.app))
        dialog = Dialog(title=f"⚠ Error: {title}", body=body, buttons=[go_back_button])
        self._display_modal(
            event.app,
            dialog,
            focus=go_back_button,
            context_type="error",
            width=80,
        )

    def _open_text_modal(self, event, title: str, text: str) -> None:
        target_width = 60
        target_height = 40
        width, height = self._calculate_modal_dimensions(
            event.app,
            target_width=target_width,
            target_height=target_height,
        )
        text_area_height = max(3, height - _CELL_MODAL_CHROME_HEIGHT)

        text_area = TextArea(
            text=text,
            read_only=True,
            scrollbar=True,
            wrap_lines=True,
            height=text_area_height,
        )

        dialog, ok_button = self._build_read_only_modal_dialog(
            app=event.app,
            title=title,
            text_area=text_area,
        )

        self._display_modal(
            event.app,
            dialog,
            focus=ok_button,
            context_type="message",
            width=width,
            height=height,
        )


# ---------------------------------------------------------------------------
# Background job handles


class _UiJobHandle(Protocol):
    """Protocol for background job handles polled by the screen."""

    def consume_update(self, viewer: Viewer) -> bool:
        """Apply an update to ``viewer``.

        Returns ``True`` once the job has been fully consumed so the screen can
        drop the handle.
        """


# ---------------------------------------------------------------------------
