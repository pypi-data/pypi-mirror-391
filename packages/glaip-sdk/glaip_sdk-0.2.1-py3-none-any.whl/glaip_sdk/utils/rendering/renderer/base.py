"""Base renderer class that orchestrates all rendering components.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import json
import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from time import monotonic
from typing import Any

from rich.console import Console as RichConsole
from rich.console import Group
from rich.live import Live
from rich.markdown import Markdown
from rich.measure import Measurement
from rich.spinner import Spinner
from rich.text import Text

from glaip_sdk.icons import ICON_AGENT, ICON_AGENT_STEP, ICON_DELEGATE, ICON_TOOL_STEP
from glaip_sdk.rich_components import AIPPanel
from glaip_sdk.utils.rendering.formatting import (
    build_connector_prefix,
    format_main_title,
    get_spinner_char,
    glyph_for_status,
    is_step_finished,
    normalise_display_label,
    pretty_args,
    redact_sensitive,
)
from glaip_sdk.utils.rendering.models import RunStats, Step
from glaip_sdk.utils.rendering.renderer.config import RendererConfig
from glaip_sdk.utils.rendering.renderer.debug import render_debug_event
from glaip_sdk.utils.rendering.renderer.panels import (
    create_final_panel,
    create_main_panel,
    create_tool_panel,
)
from glaip_sdk.utils.rendering.renderer.progress import (
    format_elapsed_time,
    format_tool_title,
    format_working_indicator,
    get_spinner,
    is_delegation_tool,
)
from glaip_sdk.utils.rendering.renderer.stream import StreamProcessor
from glaip_sdk.utils.rendering.renderer.summary_window import clamp_step_nodes
from glaip_sdk.utils.rendering.steps import UNKNOWN_STEP_DETAIL, StepManager

DEFAULT_RENDERER_THEME = "dark"
_NO_STEPS_TEXT = Text("No steps yet", style="dim")

# Configure logger
logger = logging.getLogger("glaip_sdk.run_renderer")

# Constants
LESS_THAN_1MS = "[<1ms]"
FINISHED_STATUS_HINTS = {
    "finished",
    "success",
    "succeeded",
    "completed",
    "failed",
    "stopped",
    "error",
}
RUNNING_STATUS_HINTS = {"running", "started", "pending", "working"}
ARGS_VALUE_MAX_LEN = 160
STATUS_ICON_STYLES = {
    "success": "green",
    "failed": "red",
    "warning": "yellow",
}


def _coerce_received_at(value: Any) -> datetime | None:
    """Coerce a received_at value to an aware datetime if possible."""
    if value is None:
        return None

    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)

    if isinstance(value, str):
        try:
            normalised = value.replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalised)
        except ValueError:
            return None
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)

    return None


def _truncate_display(text: str | None, limit: int = 160) -> str:
    """Return text capped at the given character limit with ellipsis."""
    if not text:
        return ""
    stripped = str(text).strip()
    if len(stripped) <= limit:
        return stripped
    return stripped[: limit - 1] + "…"


@dataclass
class RendererState:
    """Internal state for the renderer."""

    buffer: list[str] | None = None
    final_text: str = ""
    streaming_started_at: float | None = None
    printed_final_output: bool = False
    finalizing_ui: bool = False
    final_duration_seconds: float | None = None
    final_duration_text: str | None = None
    events: list[dict[str, Any]] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    streaming_started_event_ts: datetime | None = None

    def __post_init__(self) -> None:
        """Initialize renderer state after dataclass creation.

        Ensures buffer is initialized as an empty list if not provided.
        """
        if self.buffer is None:
            self.buffer = []


@dataclass
class ThinkingScopeState:
    """Runtime bookkeeping for deterministic thinking spans."""

    anchor_id: str
    task_id: str | None
    context_id: str | None
    anchor_started_at: float | None = None
    anchor_finished_at: float | None = None
    idle_started_at: float | None = None
    idle_started_monotonic: float | None = None
    active_thinking_id: str | None = None
    running_children: set[str] = field(default_factory=set)
    closed: bool = False


class TrailingSpinnerLine:
    """Render a text line with a trailing animated Rich spinner."""

    def __init__(self, base_text: Text, spinner: Spinner) -> None:
        """Initialize spinner line with base text and spinner component."""
        self._base_text = base_text
        self._spinner = spinner

    def __rich_console__(self, console: RichConsole, options: Any) -> Any:
        """Render the text with trailing animated spinner."""
        spinner_render = self._spinner.render(console.get_time())
        combined = Text.assemble(self._base_text.copy(), " ", spinner_render)
        yield combined

    def __rich_measure__(self, console: RichConsole, options: Any) -> Measurement:
        """Measure the combined text and spinner dimensions."""
        snapshot = self._spinner.render(0)
        combined = Text.assemble(self._base_text.copy(), " ", snapshot)
        return Measurement.get(console, options, combined)


class RichStreamRenderer:
    """Live, modern terminal renderer for agent execution with rich visual output."""

    def __init__(
        self,
        console: RichConsole | None = None,
        *,
        cfg: RendererConfig | None = None,
        verbose: bool = False,
    ) -> None:
        """Initialize the renderer.

        Args:
            console: Rich console instance
            cfg: Renderer configuration
            verbose: Whether to enable verbose mode
        """
        self.console = console or RichConsole()
        self.cfg = cfg or RendererConfig()
        self.verbose = verbose

        # Initialize components
        self.stream_processor = StreamProcessor()
        self.state = RendererState()

        # Initialize step manager and other state
        self.steps = StepManager(max_steps=self.cfg.summary_max_steps)
        # Live display instance (single source of truth)
        self.live: Live | None = None
        self._step_spinners: dict[str, Spinner] = {}

        # Tool tracking and thinking scopes
        self.tool_panels: dict[str, dict[str, Any]] = {}
        self._thinking_scopes: dict[str, ThinkingScopeState] = {}
        self._root_agent_friendly: str | None = None
        self._root_agent_step_id: str | None = None
        self._root_query: str | None = None
        self._root_query_attached: bool = False

        # Timing
        self._started_at: float | None = None

        # Header/text
        self.header_text: str = ""
        # Track per-step server start times for accurate elapsed labels
        self._step_server_start_times: dict[str, float] = {}

        # Output formatting constants
        self.OUTPUT_PREFIX: str = "**Output:**\n"

        # Transcript toggling
        self._transcript_mode_enabled: bool = False
        self._transcript_render_cursor: int = 0
        self.transcript_controller: Any | None = None
        self._transcript_hint_message = "[dim]Transcript view · Press Ctrl+T to return to the summary.[/dim]"
        self._summary_hint_message = "[dim]Press Ctrl+T to inspect raw transcript events.[/dim]"
        self._summary_hint_printed_once: bool = False
        self._transcript_hint_printed_once: bool = False
        self._transcript_header_printed: bool = False
        self._transcript_enabled_message_printed: bool = False

    def on_start(self, meta: dict[str, Any]) -> None:
        """Handle renderer start event."""
        if self.cfg.live:
            # Defer creating Live to _ensure_live so tests and prod both work
            pass

        # Set up initial state
        self._started_at = monotonic()
        try:
            self.state.meta = json.loads(json.dumps(meta))
        except Exception:
            self.state.meta = dict(meta)

        meta_payload = meta or {}
        self.steps.set_root_agent(meta_payload.get("agent_id"))
        self._root_agent_friendly = self._humanize_agent_slug(meta_payload.get("agent_name"))
        self._root_query = _truncate_display(
            meta_payload.get("input_message")
            or meta_payload.get("query")
            or meta_payload.get("message")
            or (meta_payload.get("meta") or {}).get("input_message")
            or ""
        )
        if not self._root_query:
            self._root_query = None
        self._root_query_attached = False

        # Print compact header and user request (parity with old renderer)
        self._render_header(meta)
        self._render_user_query(meta)

    def _render_header(self, meta: dict[str, Any]) -> None:
        """Render the agent header with metadata."""
        parts = self._build_header_parts(meta)
        self.header_text = " ".join(parts)

        if not self.header_text:
            return

        # Use a rule-like header for readability with fallback
        if not self._render_header_rule():
            self._render_header_fallback()

    def _build_header_parts(self, meta: dict[str, Any]) -> list[str]:
        """Build header text parts from metadata."""
        parts: list[str] = [ICON_AGENT]
        agent_name = meta.get("agent_name", "agent")
        if agent_name:
            parts.append(agent_name)

        model = meta.get("model", "")
        if model:
            parts.extend(["•", model])

        run_id = meta.get("run_id", "")
        if run_id:
            parts.extend(["•", run_id])

        return parts

    def _render_header_rule(self) -> bool:
        """Render header as a rule. Returns True if successful."""
        try:
            self.console.rule(self.header_text)
            return True
        except Exception:  # pragma: no cover - defensive fallback
            logger.exception("Failed to render header rule")
            return False

    def _render_header_fallback(self) -> None:
        """Fallback header rendering."""
        try:
            self.console.print(self.header_text)
        except Exception:
            logger.exception("Failed to print header fallback")

    def _extract_query_from_meta(self, meta: dict[str, Any] | None) -> str | None:
        """Extract the primary query string from a metadata payload."""
        if not meta:
            return None
        query = (
            meta.get("input_message")
            or meta.get("query")
            or meta.get("message")
            or (meta.get("meta") or {}).get("input_message")
        )
        if isinstance(query, str) and query.strip():
            return query
        return None

    def _build_user_query_panel(self, query: str) -> AIPPanel:
        """Create the panel used to display the user request."""
        return AIPPanel(
            Markdown(f"**Query:** {query}"),
            title="User Request",
            border_style="#d97706",
            padding=(0, 1),
        )

    def _render_user_query(self, meta: dict[str, Any]) -> None:
        """Render the user query panel."""
        query = self._extract_query_from_meta(meta)
        if not query:
            return
        self.console.print(self._build_user_query_panel(query))

    def _render_summary_static_sections(self) -> None:
        """Re-render header and user query when returning to summary mode."""
        meta = getattr(self.state, "meta", None)
        if meta:
            self._render_header(meta)
        elif self.header_text and not self._render_header_rule():
            self._render_header_fallback()

        query = self._extract_query_from_meta(meta) or self._root_query
        if query:
            self.console.print(self._build_user_query_panel(query))

    def _render_summary_after_transcript_toggle(self) -> None:
        """Render the summary panel after leaving transcript mode."""
        if self.state.finalizing_ui:
            self._render_final_summary_panels()
        elif self.live:
            self._refresh_live_panels()
        else:
            self._render_static_summary_panels()

    def _render_final_summary_panels(self) -> None:
        """Render a static summary and disable live mode for final output."""
        self.cfg.live = False
        self.live = None
        self._render_static_summary_panels()

    def _render_static_summary_panels(self) -> None:
        """Render the steps and main panels in a static (non-live) layout."""
        steps_renderable = self._render_steps_text()
        steps_panel = AIPPanel(
            steps_renderable,
            title="Steps",
            border_style="blue",
        )
        self.console.print(steps_panel)
        self.console.print(self._render_main_panel())

    def _ensure_streaming_started_baseline(self, timestamp: float) -> None:
        """Synchronize streaming start state across renderer components."""
        self.state.streaming_started_at = timestamp
        self.stream_processor.streaming_started_at = timestamp
        self._started_at = timestamp

    def on_event(self, ev: dict[str, Any]) -> None:
        """Handle streaming events from the backend."""
        received_at = self._resolve_received_timestamp(ev)
        self._capture_event(ev, received_at)
        self.stream_processor.reset_event_tracking()

        self._sync_stream_start(ev, received_at)

        metadata = self.stream_processor.extract_event_metadata(ev)

        self._maybe_render_debug(ev, received_at)
        try:
            self._dispatch_event(ev, metadata)
        finally:
            self.stream_processor.update_timing(metadata.get("context_id"))

    def _resolve_received_timestamp(self, ev: dict[str, Any]) -> datetime:
        """Return the timestamp an event was received, normalising inputs."""
        received_at = _coerce_received_at(ev.get("received_at"))
        if received_at is None:
            received_at = datetime.now(timezone.utc)

        if self.state.streaming_started_event_ts is None:
            self.state.streaming_started_event_ts = received_at

        return received_at

    def _sync_stream_start(self, ev: dict[str, Any], received_at: datetime | None) -> None:
        """Ensure renderer and stream processor share a streaming baseline."""
        baseline = self.state.streaming_started_at
        if baseline is None:
            baseline = monotonic()
            self._ensure_streaming_started_baseline(baseline)
        elif getattr(self.stream_processor, "streaming_started_at", None) is None:
            self._ensure_streaming_started_baseline(baseline)

        if ev.get("status") == "streaming_started":
            self.state.streaming_started_event_ts = received_at
            self._ensure_streaming_started_baseline(monotonic())

    def _maybe_render_debug(
        self, ev: dict[str, Any], received_at: datetime
    ) -> None:  # pragma: no cover - guard rails for verbose mode
        """Render debug view when verbose mode is enabled."""
        if not self.verbose:
            return

        self._ensure_transcript_header()
        render_debug_event(
            ev,
            self.console,
            received_ts=received_at,
            baseline_ts=self.state.streaming_started_event_ts,
        )
        self._print_transcript_hint()

    def _dispatch_event(self, ev: dict[str, Any], metadata: dict[str, Any]) -> None:
        """Route events to the appropriate renderer handlers."""
        kind = metadata["kind"]
        content = metadata["content"]

        if kind == "status":
            self._handle_status_event(ev)
        elif kind == "content":
            self._handle_content_event(content)
        elif kind == "final_response":
            self._handle_final_response_event(content, metadata)
        elif kind in {"agent_step", "agent_thinking_step"}:
            self._handle_agent_step_event(ev, metadata)
        else:
            self._ensure_live()

    def _handle_status_event(self, ev: dict[str, Any]) -> None:
        """Handle status events."""
        status = ev.get("status")
        if status == "streaming_started":
            return

    def _handle_content_event(self, content: str) -> None:
        """Handle content streaming events."""
        if content:
            self.state.buffer.append(content)
            self._ensure_live()

    def _handle_final_response_event(self, content: str, metadata: dict[str, Any]) -> None:
        """Handle final response events."""
        if content:
            self.state.buffer.append(content)
            self.state.final_text = content

            meta_payload = metadata.get("metadata") or {}
            final_time = self._coerce_server_time(meta_payload.get("time"))
            self._update_final_duration(final_time)
            self._close_active_thinking_scopes(final_time)
            self._finish_running_steps()
            self._finish_tool_panels()
            self._normalise_finished_icons()

        self._ensure_live()
        self._print_final_panel_if_needed()

    def _normalise_finished_icons(self) -> None:
        """Ensure finished steps do not keep spinner icons."""
        for step in self.steps.by_id.values():
            if getattr(step, "status", None) == "finished" and getattr(step, "status_icon", None) == "spinner":
                step.status_icon = "success"
            if getattr(step, "status", None) != "running":
                self._step_spinners.pop(step.step_id, None)

    def _handle_agent_step_event(self, ev: dict[str, Any], metadata: dict[str, Any]) -> None:
        """Handle agent step events."""
        # Extract tool information
        (
            tool_name,
            tool_args,
            tool_out,
            tool_calls_info,
        ) = self.stream_processor.parse_tool_calls(ev)

        payload = metadata.get("metadata") or {}

        tracked_step: Step | None = None
        try:
            tracked_step = self.steps.apply_event(ev)
        except ValueError:
            logger.debug("Malformed step event skipped", exc_info=True)
        else:
            self._record_step_server_start(tracked_step, payload)
            self._update_thinking_timeline(tracked_step, payload)
            self._maybe_override_root_agent_label(tracked_step, payload)
            self._maybe_attach_root_query(tracked_step)

        # Track tools and sub-agents for transcript/debug context
        self.stream_processor.track_tools_and_agents(tool_name, tool_calls_info, is_delegation_tool)

        # Handle tool execution
        self._handle_agent_step(
            ev,
            tool_name,
            tool_args,
            tool_out,
            tool_calls_info,
            tracked_step=tracked_step,
        )

        # Update live display
        self._ensure_live()

    def _maybe_attach_root_query(self, step: Step | None) -> None:
        """Attach the user query to the root agent step for display."""
        if not step or self._root_query_attached or not self._root_query or step.kind != "agent" or step.parent_id:
            return

        args = dict(getattr(step, "args", {}) or {})
        args.setdefault("query", self._root_query)
        step.args = args
        self._root_query_attached = True

    def _record_step_server_start(self, step: Step | None, payload: dict[str, Any]) -> None:
        """Store server-provided start times for elapsed calculations."""
        if not step:
            return
        server_time = payload.get("time")
        if not isinstance(server_time, (int, float)):
            return
        self._step_server_start_times.setdefault(step.step_id, float(server_time))

    def _maybe_override_root_agent_label(self, step: Step | None, payload: dict[str, Any]) -> None:
        """Ensure the root agent row uses the human-friendly name and shows the ID."""
        if not step or step.kind != "agent" or step.parent_id:
            return
        friendly = self._root_agent_friendly or self._humanize_agent_slug((payload or {}).get("agent_name"))
        if not friendly:
            return
        agent_identifier = step.name or step.step_id
        if not agent_identifier:
            return
        step.display_label = normalise_display_label(f"{ICON_AGENT} {friendly} ({agent_identifier})")
        if not self._root_agent_step_id:
            self._root_agent_step_id = step.step_id

    def _update_thinking_timeline(self, step: Step | None, payload: dict[str, Any]) -> None:
        """Maintain deterministic thinking spans for each agent/delegate scope."""
        if not self.cfg.render_thinking or not step:
            return

        now_monotonic = monotonic()
        server_time = self._coerce_server_time(payload.get("time"))
        status_hint = (payload.get("status") or "").lower()

        if self._is_scope_anchor(step):
            self._update_anchor_thinking(
                step=step,
                server_time=server_time,
                status_hint=status_hint,
                now_monotonic=now_monotonic,
            )
            return

        self._update_child_thinking(
            step=step,
            server_time=server_time,
            status_hint=status_hint,
            now_monotonic=now_monotonic,
        )

    def _update_anchor_thinking(
        self,
        *,
        step: Step,
        server_time: float | None,
        status_hint: str,
        now_monotonic: float,
    ) -> None:
        """Handle deterministic thinking bookkeeping for agent/delegate anchors."""
        scope = self._get_or_create_scope(step)
        if scope.anchor_started_at is None and server_time is not None:
            scope.anchor_started_at = server_time

        if not scope.closed and scope.active_thinking_id is None:
            self._start_scope_thinking(
                scope,
                start_server_time=scope.anchor_started_at or server_time,
                start_monotonic=now_monotonic,
            )

        is_anchor_finished = status_hint in FINISHED_STATUS_HINTS or (not status_hint and is_step_finished(step))
        if is_anchor_finished:
            scope.anchor_finished_at = server_time or scope.anchor_finished_at
            self._finish_scope_thinking(scope, server_time, now_monotonic)
            scope.closed = True

        parent_anchor_id = self._resolve_anchor_id(step)
        if parent_anchor_id:
            self._cascade_anchor_update(
                parent_anchor_id=parent_anchor_id,
                child_step=step,
                server_time=server_time,
                now_monotonic=now_monotonic,
                is_finished=is_anchor_finished,
            )

    def _cascade_anchor_update(
        self,
        *,
        parent_anchor_id: str,
        child_step: Step,
        server_time: float | None,
        now_monotonic: float,
        is_finished: bool,
    ) -> None:
        """Propagate anchor state changes to the parent scope."""
        parent_scope = self._thinking_scopes.get(parent_anchor_id)
        if not parent_scope or parent_scope.closed:
            return
        if is_finished:
            self._mark_child_finished(parent_scope, child_step.step_id, server_time, now_monotonic)
        else:
            self._mark_child_running(parent_scope, child_step, server_time, now_monotonic)

    def _update_child_thinking(
        self,
        *,
        step: Step,
        server_time: float | None,
        status_hint: str,
        now_monotonic: float,
    ) -> None:
        """Update deterministic thinking state for non-anchor steps."""
        anchor_id = self._resolve_anchor_id(step)
        if not anchor_id:
            return

        scope = self._thinking_scopes.get(anchor_id)
        if not scope or scope.closed or step.kind == "thinking":
            return

        is_finish_event = status_hint in FINISHED_STATUS_HINTS or (not status_hint and is_step_finished(step))
        if is_finish_event:
            self._mark_child_finished(scope, step.step_id, server_time, now_monotonic)
        else:
            self._mark_child_running(scope, step, server_time, now_monotonic)

    def _resolve_anchor_id(self, step: Step) -> str | None:
        """Return the nearest agent/delegate ancestor for a step."""
        parent_id = step.parent_id
        while parent_id:
            parent = self.steps.by_id.get(parent_id)
            if not parent:
                return None
            if self._is_scope_anchor(parent):
                return parent.step_id
            parent_id = parent.parent_id
        return None

    def _get_or_create_scope(self, step: Step) -> ThinkingScopeState:
        """Fetch (or create) thinking state for the given anchor step."""
        scope = self._thinking_scopes.get(step.step_id)
        if scope:
            if scope.task_id is None:
                scope.task_id = step.task_id
            if scope.context_id is None:
                scope.context_id = step.context_id
            return scope
        scope = ThinkingScopeState(
            anchor_id=step.step_id,
            task_id=step.task_id,
            context_id=step.context_id,
        )
        self._thinking_scopes[step.step_id] = scope
        return scope

    def _is_scope_anchor(self, step: Step) -> bool:
        """Return True when a step should host its own thinking timeline."""
        if step.kind in {"agent", "delegate"}:
            return True
        name = (step.name or "").lower()
        return name.startswith(("delegate_to_", "delegate_", "delegate "))

    def _start_scope_thinking(
        self,
        scope: ThinkingScopeState,
        *,
        start_server_time: float | None,
        start_monotonic: float,
    ) -> None:
        """Open a deterministic thinking node beneath the scope anchor."""
        if scope.closed or scope.active_thinking_id or not scope.anchor_id:
            return
        step = self.steps.start_or_get(
            task_id=scope.task_id,
            context_id=scope.context_id,
            kind="thinking",
            name=f"agent_thinking_step::{scope.anchor_id}",
            parent_id=scope.anchor_id,
            args={"reason": "deterministic_timeline"},
        )
        step.display_label = "💭 Thinking…"
        step.status_icon = "spinner"
        scope.active_thinking_id = step.step_id
        scope.idle_started_at = start_server_time
        scope.idle_started_monotonic = start_monotonic

    def _finish_scope_thinking(
        self,
        scope: ThinkingScopeState,
        end_server_time: float | None,
        end_monotonic: float,
    ) -> None:
        """Close the currently running thinking node if one exists."""
        if not scope.active_thinking_id:
            return
        thinking_step = self.steps.by_id.get(scope.active_thinking_id)
        if not thinking_step:
            scope.active_thinking_id = None
            scope.idle_started_at = None
            scope.idle_started_monotonic = None
            return

        duration = self._calculate_timeline_duration(
            scope.idle_started_at,
            end_server_time,
            scope.idle_started_monotonic,
            end_monotonic,
        )
        thinking_step.display_label = thinking_step.display_label or "💭 Thinking…"
        if duration is not None:
            thinking_step.finish(duration, source="timeline")
        else:
            thinking_step.finish(None, source="timeline")
        thinking_step.status_icon = "success"
        scope.active_thinking_id = None
        scope.idle_started_at = None
        scope.idle_started_monotonic = None

    def _mark_child_running(
        self,
        scope: ThinkingScopeState,
        step: Step,
        server_time: float | None,
        now_monotonic: float,
    ) -> None:
        """Mark a direct child as running and close any open thinking node."""
        if step.step_id in scope.running_children:
            return
        scope.running_children.add(step.step_id)
        if not scope.active_thinking_id:
            return

        start_server = self._step_server_start_times.get(step.step_id)
        if start_server is None:
            start_server = server_time
        self._finish_scope_thinking(scope, start_server, now_monotonic)

    def _mark_child_finished(
        self,
        scope: ThinkingScopeState,
        step_id: str,
        server_time: float | None,
        now_monotonic: float,
    ) -> None:
        """Handle completion for a scope child and resume thinking if idle."""
        if step_id in scope.running_children:
            scope.running_children.discard(step_id)
        if scope.running_children or scope.closed:
            return
        self._start_scope_thinking(
            scope,
            start_server_time=server_time,
            start_monotonic=now_monotonic,
        )

    def _close_active_thinking_scopes(self, server_time: float | None) -> None:
        """Finish any in-flight thinking nodes during finalization."""
        now = monotonic()
        for scope in self._thinking_scopes.values():
            if not scope.active_thinking_id:
                continue
            self._finish_scope_thinking(scope, server_time, now)
            scope.closed = True
            # Parent scopes resume thinking via _cascade_anchor_update

    def _apply_root_duration(self, duration_seconds: float | None) -> None:
        """Propagate the final run duration to the root agent step."""
        if duration_seconds is None or not self._root_agent_step_id:
            return
        root_step = self.steps.by_id.get(self._root_agent_step_id)
        if not root_step:
            return
        try:
            duration_ms = max(0, int(round(float(duration_seconds) * 1000)))
        except Exception:
            return
        root_step.duration_ms = duration_ms
        root_step.duration_source = root_step.duration_source or "run"
        root_step.status = "finished"

    @staticmethod
    def _coerce_server_time(value: Any) -> float | None:
        """Convert a raw SSE time payload into a float if possible."""
        if isinstance(value, (int, float)):
            return float(value)
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _calculate_timeline_duration(
        start_server: float | None,
        end_server: float | None,
        start_monotonic: float | None,
        end_monotonic: float,
    ) -> float | None:
        """Pick the most reliable pair of timestamps to derive duration seconds."""
        if start_server is not None and end_server is not None:
            return max(0.0, float(end_server) - float(start_server))
        if start_monotonic is not None:
            try:
                return max(0.0, float(end_monotonic) - float(start_monotonic))
            except Exception:
                return None
        return None

    @staticmethod
    def _humanize_agent_slug(value: Any) -> str | None:
        """Convert a slugified agent name into Title Case."""
        if not isinstance(value, str):
            return None
        cleaned = value.replace("_", " ").replace("-", " ").strip()
        if not cleaned:
            return None
        parts = [part for part in cleaned.split() if part]
        return " ".join(part[:1].upper() + part[1:] for part in parts)

    def _finish_running_steps(self) -> None:
        """Mark any running steps as finished to avoid lingering spinners."""
        for st in self.steps.by_id.values():
            if not is_step_finished(st):
                self._mark_incomplete_step(st)

    def _mark_incomplete_step(self, step: Step) -> None:
        """Mark a lingering step as incomplete/warning with unknown duration."""
        step.status = "finished"
        step.duration_unknown = True
        if step.duration_ms is None:
            step.duration_ms = 0
        step.duration_source = step.duration_source or "unknown"
        step.status_icon = "warning"

    def _finish_tool_panels(self) -> None:
        """Mark unfinished tool panels as finished."""
        try:
            items = list(self.tool_panels.items())
        except Exception:  # pragma: no cover - defensive guard
            logger.exception("Failed to iterate tool panels during cleanup")
            return

        for _sid, meta in items:
            if meta.get("status") != "finished":
                meta["status"] = "finished"

    def _stop_live_display(self) -> None:
        """Stop live display and clean up."""
        self._shutdown_live()

    def _print_final_panel_if_needed(self) -> None:
        """Print final result when configuration requires it."""
        if self.state.printed_final_output:
            return

        body = (self.state.final_text or "".join(self.state.buffer) or "").strip()
        if not body:
            return

        if getattr(self, "_transcript_mode_enabled", False):
            return

        if self.verbose:
            final_panel = create_final_panel(
                body,
                title=self._final_panel_title(),
                theme=DEFAULT_RENDERER_THEME,
            )
            self.console.print(final_panel)
            self.state.printed_final_output = True

    def on_complete(self, stats: RunStats) -> None:
        """Handle completion event."""
        self.state.finalizing_ui = True

        self._handle_stats_duration(stats)
        self._close_active_thinking_scopes(self.state.final_duration_seconds)
        self._cleanup_ui_elements()
        self._finalize_display()
        self._print_completion_message()

    def _handle_stats_duration(self, stats: RunStats) -> None:
        """Handle stats processing and duration calculation."""
        if not isinstance(stats, RunStats):
            return

        duration = None
        try:
            if stats.finished_at is not None and stats.started_at is not None:
                duration = max(0.0, float(stats.finished_at) - float(stats.started_at))
        except Exception:
            duration = None

        if duration is not None:
            self._update_final_duration(duration, overwrite=True)

    def _cleanup_ui_elements(self) -> None:
        """Clean up running UI elements."""
        # Mark any running steps as finished to avoid lingering spinners
        self._finish_running_steps()

        # Mark unfinished tool panels as finished
        self._finish_tool_panels()

    def _finalize_display(self) -> None:
        """Finalize live display and render final output."""
        # Final refresh
        self._ensure_live()

        # Stop live display
        self._stop_live_display()

        # Render final output based on configuration
        self._print_final_panel_if_needed()

    def _print_completion_message(self) -> None:
        """Print completion message based on current mode."""
        if self._transcript_mode_enabled:
            try:
                self.console.print(
                    "[dim]Run finished. Press Ctrl+T to return to the summary view or stay here to inspect events. "
                    "Use the post-run viewer for export.[/dim]"
                )
            except Exception:
                pass
        else:
            # No transcript toggle in summary mode; nothing to print here.
            return

    def _ensure_live(self) -> None:
        """Ensure live display is updated."""
        if getattr(self, "_transcript_mode_enabled", False):
            return
        if not self._ensure_live_stack():
            return

        self._start_live_if_needed()

        if self.live:
            self._refresh_live_panels()
            if (
                not self._transcript_mode_enabled
                and not self.state.finalizing_ui
                and not self._summary_hint_printed_once
            ):
                self._print_summary_hint(force=True)

    def _ensure_live_stack(self) -> bool:
        """Guarantee the console exposes the internal live stack Rich expects."""
        live_stack = getattr(self.console, "_live_stack", None)
        if isinstance(live_stack, list):
            return True

        try:
            self.console._live_stack = []  # type: ignore[attr-defined]
            return True
        except Exception:
            # If the console forbids attribute assignment we simply skip the live
            # update for this cycle and fall back to buffered printing.
            logger.debug(
                "Console missing _live_stack; skipping live UI initialisation",
                exc_info=True,
            )
            return False

    def _start_live_if_needed(self) -> None:
        """Create and start a Live instance when configuration allows."""
        if self.live is not None or not self.cfg.live:
            return

        try:
            self.live = Live(
                console=self.console,
                refresh_per_second=1 / self.cfg.refresh_debounce,
                transient=not self.cfg.persist_live,
            )
            self.live.start()
        except Exception:
            self.live = None

    def _refresh_live_panels(self) -> None:
        """Render panels and push them to the active Live display."""
        if not self.live:
            return

        main_panel = self._render_main_panel()
        steps_renderable = self._render_steps_text()
        steps_panel = AIPPanel(
            steps_renderable,
            title="Steps",
            border_style="blue",
        )
        panels = self._build_live_panels(main_panel, steps_panel)

        self.live.update(Group(*panels))

    def _build_live_panels(
        self,
        main_panel: Any,
        steps_panel: Any,
    ) -> list[Any]:
        """Assemble the panel order for the live display."""
        if self.verbose:
            return [main_panel, steps_panel]

        return [steps_panel, main_panel]

    def _render_main_panel(self) -> Any:
        """Render the main content panel."""
        body = "".join(self.state.buffer).strip()
        if not self.verbose:
            final_content = (self.state.final_text or "").strip()
            if final_content:
                title = self._final_panel_title()
                return create_final_panel(
                    final_content,
                    title=title,
                    theme=DEFAULT_RENDERER_THEME,
                )
        # Dynamic title with spinner + elapsed/hints
        title = self._format_enhanced_main_title()
        return create_main_panel(body, title, DEFAULT_RENDERER_THEME)

    def _final_panel_title(self) -> str:
        """Compose title for the final result panel including duration."""
        title = "Final Result"
        if self.state.final_duration_text:
            title = f"{title} · {self.state.final_duration_text}"
        return title

    def apply_verbosity(self, verbose: bool) -> None:
        """Update verbose behaviour at runtime."""
        if self.verbose == verbose:
            return

        self.verbose = verbose
        desired_live = not verbose
        if desired_live != self.cfg.live:
            self.cfg.live = desired_live
            if not desired_live:
                self._shutdown_live()
            else:
                self._ensure_live()

        if self.cfg.live:
            self._ensure_live()

    # ------------------------------------------------------------------
    # Transcript helpers
    # ------------------------------------------------------------------
    @property
    def transcript_mode_enabled(self) -> bool:
        """Return True when transcript mode is currently active."""
        return self._transcript_mode_enabled

    def toggle_transcript_mode(self) -> None:
        """Flip transcript mode on/off."""
        self.set_transcript_mode(not self._transcript_mode_enabled)

    def set_transcript_mode(self, enabled: bool) -> None:
        """Set transcript mode explicitly."""
        if enabled == self._transcript_mode_enabled:
            return

        self._transcript_mode_enabled = enabled
        self.apply_verbosity(enabled)

        if enabled:
            self._summary_hint_printed_once = False
            self._transcript_hint_printed_once = False
            self._transcript_header_printed = False
            self._transcript_enabled_message_printed = False
            self._stop_live_display()
            self._clear_console_safe()
            self._print_transcript_enabled_message()
            self._render_transcript_backfill()
        else:
            self._transcript_hint_printed_once = False
            self._transcript_header_printed = False
            self._transcript_enabled_message_printed = False
            self._clear_console_safe()
        self._render_summary_static_sections()
        summary_notice = (
            "[dim]Returning to the summary view. Streaming will continue here.[/dim]"
            if not self.state.finalizing_ui
            else "[dim]Returning to the summary view.[/dim]"
        )
        self.console.print(summary_notice)
        self._render_summary_after_transcript_toggle()
        if not self.state.finalizing_ui:
            self._print_summary_hint(force=True)

    def _clear_console_safe(self) -> None:
        """Best-effort console clear that ignores platform quirks."""
        try:
            self.console.clear()
        except Exception:
            pass

    def _print_transcript_hint(self) -> None:
        """Render the transcript toggle hint, keeping it near the bottom."""
        if not self._transcript_mode_enabled:
            return
        try:
            self.console.print(self._transcript_hint_message)
        except Exception:
            pass
        else:
            self._transcript_hint_printed_once = True

    def _print_transcript_enabled_message(self) -> None:
        if self._transcript_enabled_message_printed:
            return
        try:
            self.console.print("[dim]Transcript mode enabled — streaming raw transcript events.[/dim]")
        except Exception:
            pass
        else:
            self._transcript_enabled_message_printed = True

    def _ensure_transcript_header(self) -> None:
        if self._transcript_header_printed:
            return
        try:
            self.console.rule("Transcript Events")
        except Exception:
            self._transcript_header_printed = True
            return
        self._transcript_header_printed = True

    def _print_summary_hint(self, force: bool = False) -> None:
        """Show the summary-mode toggle hint."""
        controller = getattr(self, "transcript_controller", None)
        if controller and not getattr(controller, "enabled", False):
            if not force:
                self._summary_hint_printed_once = True
            return
        if not force and self._summary_hint_printed_once:
            return
        try:
            self.console.print(self._summary_hint_message)
        except Exception:
            return
        self._summary_hint_printed_once = True

    def _render_transcript_backfill(self) -> None:
        """Render any captured events that haven't been shown in transcript mode."""
        pending = self.state.events[self._transcript_render_cursor :]
        self._ensure_transcript_header()
        if not pending:
            self._print_transcript_hint()
            return

        baseline = self.state.streaming_started_event_ts
        for ev in pending:
            received_ts = _coerce_received_at(ev.get("received_at"))
            render_debug_event(
                ev,
                self.console,
                received_ts=received_ts,
                baseline_ts=baseline,
            )

        self._transcript_render_cursor = len(self.state.events)
        self._print_transcript_hint()

    def _capture_event(self, ev: dict[str, Any], received_at: datetime | None = None) -> None:
        """Capture a deep copy of SSE events for transcript replay."""
        try:
            captured = json.loads(json.dumps(ev))
        except Exception:
            captured = ev

        if received_at is not None:
            try:
                captured["received_at"] = received_at.isoformat()
            except Exception:
                try:
                    captured["received_at"] = str(received_at)
                except Exception:
                    captured["received_at"] = repr(received_at)

        self.state.events.append(captured)
        if self._transcript_mode_enabled:
            self._transcript_render_cursor = len(self.state.events)

    def get_aggregated_output(self) -> str:
        """Return the concatenated assistant output collected so far."""
        return ("".join(self.state.buffer or [])).strip()

    def get_transcript_events(self) -> list[dict[str, Any]]:
        """Return captured SSE events."""
        return list(self.state.events)

    def _ensure_tool_panel(self, name: str, args: Any, task_id: str, context_id: str) -> str:
        """Ensure a tool panel exists and return its ID."""
        formatted_title = format_tool_title(name)
        is_delegation = is_delegation_tool(name)
        tool_sid = f"tool_{name}_{task_id}_{context_id}"

        if tool_sid not in self.tool_panels:
            self.tool_panels[tool_sid] = {
                "title": formatted_title,
                "status": "running",
                "started_at": monotonic(),
                "server_started_at": self.stream_processor.server_elapsed_time,
                "chunks": [],
                "args": args or {},
                "output": None,
                "is_delegation": is_delegation,
            }
            # Add Args section once
            if args:
                try:
                    args_content = "**Args:**\n```json\n" + json.dumps(args, indent=2) + "\n```\n\n"
                except Exception:
                    args_content = f"**Args:**\n{args}\n\n"
                self.tool_panels[tool_sid]["chunks"].append(args_content)

        return tool_sid

    def _start_tool_step(
        self,
        task_id: str,
        context_id: str,
        tool_name: str,
        tool_args: Any,
        _tool_sid: str,
        *,
        tracked_step: Step | None = None,
    ) -> Step | None:
        """Start or get a step for a tool."""
        if tracked_step is not None:
            return tracked_step

        if is_delegation_tool(tool_name):
            st = self.steps.start_or_get(
                task_id=task_id,
                context_id=context_id,
                kind="delegate",
                name=tool_name,
                args=tool_args,
            )
        else:
            st = self.steps.start_or_get(
                task_id=task_id,
                context_id=context_id,
                kind="tool",
                name=tool_name,
                args=tool_args,
            )

        # Record server start time for this step if available
        if st and self.stream_processor.server_elapsed_time is not None:
            self._step_server_start_times[st.step_id] = self.stream_processor.server_elapsed_time

        return st

    def _process_additional_tool_calls(
        self,
        tool_calls_info: list[tuple[str, Any, Any]],
        tool_name: str,
        task_id: str,
        context_id: str,
    ) -> None:
        """Process additional tool calls to avoid duplicates."""
        for call_name, call_args, _ in tool_calls_info or []:
            if call_name and call_name != tool_name:
                self._process_single_tool_call(call_name, call_args, task_id, context_id)

    def _process_single_tool_call(self, call_name: str, call_args: Any, task_id: str, context_id: str) -> None:
        """Process a single additional tool call."""
        self._ensure_tool_panel(call_name, call_args, task_id, context_id)

        st2 = self._create_step_for_tool_call(call_name, call_args, task_id, context_id)

        if self.stream_processor.server_elapsed_time is not None and st2:
            self._step_server_start_times[st2.step_id] = self.stream_processor.server_elapsed_time

    def _create_step_for_tool_call(self, call_name: str, call_args: Any, task_id: str, context_id: str) -> Any:
        """Create appropriate step for tool call."""
        if is_delegation_tool(call_name):
            return self.steps.start_or_get(
                task_id=task_id,
                context_id=context_id,
                kind="delegate",
                name=call_name,
                args=call_args,
            )
        else:
            return self.steps.start_or_get(
                task_id=task_id,
                context_id=context_id,
                kind="tool",
                name=call_name,
                args=call_args,
            )

    def _detect_tool_completion(self, metadata: dict, content: str) -> tuple[bool, str | None, Any]:
        """Detect if a tool has completed and return completion info."""
        tool_info = metadata.get("tool_info", {}) if isinstance(metadata, dict) else {}

        if tool_info.get("status") == "finished" and tool_info.get("name"):
            return True, tool_info.get("name"), tool_info.get("output")
        elif content and isinstance(content, str) and content.startswith("Completed "):
            # content like "Completed google_serper"
            tname = content.replace("Completed ", "").strip()
            if tname:
                output = tool_info.get("output") if tool_info.get("name") == tname else None
                return True, tname, output
        elif metadata.get("status") == "finished" and tool_info.get("name"):
            return True, tool_info.get("name"), tool_info.get("output")

        return False, None, None

    def _get_tool_session_id(self, finished_tool_name: str, task_id: str, context_id: str) -> str:
        """Generate tool session ID."""
        return f"tool_{finished_tool_name}_{task_id}_{context_id}"

    def _calculate_tool_duration(self, meta: dict[str, Any]) -> float | None:
        """Calculate tool duration from metadata."""
        server_now = self.stream_processor.server_elapsed_time
        server_start = meta.get("server_started_at")
        dur = None

        try:
            if isinstance(server_now, (int, float)) and server_start is not None:
                dur = max(0.0, float(server_now) - float(server_start))
            else:
                started_at = meta.get("started_at")
                if started_at is not None:
                    started_at_float = float(started_at)
                    dur = max(0.0, float(monotonic()) - started_at_float)
        except (TypeError, ValueError):
            logger.exception("Failed to calculate tool duration")
            return None

        return dur

    def _update_tool_metadata(self, meta: dict[str, Any], dur: float | None) -> None:
        """Update tool metadata with duration information."""
        if dur is not None:
            meta["duration_seconds"] = dur
            meta["server_finished_at"] = (
                self.stream_processor.server_elapsed_time
                if isinstance(self.stream_processor.server_elapsed_time, (int, float))
                else None
            )
            meta["finished_at"] = monotonic()

    def _add_tool_output_to_panel(
        self, meta: dict[str, Any], finished_tool_output: Any, finished_tool_name: str
    ) -> None:
        """Add tool output to panel metadata."""
        if finished_tool_output is not None:
            meta["chunks"].append(self._format_output_block(finished_tool_output, finished_tool_name))
            meta["output"] = finished_tool_output

    def _mark_panel_as_finished(self, meta: dict[str, Any], tool_sid: str) -> None:
        """Mark panel as finished and ensure visibility."""
        if meta.get("status") != "finished":
            meta["status"] = "finished"

            dur = self._calculate_tool_duration(meta)
            self._update_tool_metadata(meta, dur)

        # Ensure this finished panel is visible in this frame
        self.stream_processor.current_event_finished_panels.add(tool_sid)

    def _finish_tool_panel(
        self,
        finished_tool_name: str,
        finished_tool_output: Any,
        task_id: str,
        context_id: str,
    ) -> None:
        """Finish a tool panel and update its status."""
        tool_sid = self._get_tool_session_id(finished_tool_name, task_id, context_id)
        if tool_sid not in self.tool_panels:
            return

        meta = self.tool_panels[tool_sid]
        self._mark_panel_as_finished(meta, tool_sid)
        self._add_tool_output_to_panel(meta, finished_tool_output, finished_tool_name)

    def _get_step_duration(self, finished_tool_name: str, task_id: str, context_id: str) -> float | None:
        """Get step duration from tool panels."""
        tool_sid = f"tool_{finished_tool_name}_{task_id}_{context_id}"
        return self.tool_panels.get(tool_sid, {}).get("duration_seconds")

    def _finish_delegation_step(
        self,
        finished_tool_name: str,
        finished_tool_output: Any,
        task_id: str,
        context_id: str,
        step_duration: float | None,
    ) -> None:
        """Finish a delegation step."""
        self.steps.finish(
            task_id=task_id,
            context_id=context_id,
            kind="delegate",
            name=finished_tool_name,
            output=finished_tool_output,
            duration_raw=step_duration,
        )

    def _finish_tool_step_type(
        self,
        finished_tool_name: str,
        finished_tool_output: Any,
        task_id: str,
        context_id: str,
        step_duration: float | None,
    ) -> None:
        """Finish a regular tool step."""
        self.steps.finish(
            task_id=task_id,
            context_id=context_id,
            kind="tool",
            name=finished_tool_name,
            output=finished_tool_output,
            duration_raw=step_duration,
        )

    def _finish_tool_step(
        self,
        finished_tool_name: str,
        finished_tool_output: Any,
        task_id: str,
        context_id: str,
        *,
        tracked_step: Step | None = None,
    ) -> None:
        """Finish the corresponding step for a completed tool."""
        if tracked_step is not None:
            return

        step_duration = self._get_step_duration(finished_tool_name, task_id, context_id)

        if is_delegation_tool(finished_tool_name):
            self._finish_delegation_step(
                finished_tool_name,
                finished_tool_output,
                task_id,
                context_id,
                step_duration,
            )
        else:
            self._finish_tool_step_type(
                finished_tool_name,
                finished_tool_output,
                task_id,
                context_id,
                step_duration,
            )

    def _should_create_snapshot(self, tool_sid: str) -> bool:
        """Check if a snapshot should be created."""
        return self.cfg.append_finished_snapshots and not self.tool_panels.get(tool_sid, {}).get("snapshot_printed")

    def _get_snapshot_title(self, meta: dict[str, Any], finished_tool_name: str) -> str:
        """Get the title for the snapshot."""
        adjusted_title = meta.get("title") or finished_tool_name

        # Add elapsed time to title
        dur = meta.get("duration_seconds")
        if isinstance(dur, (int, float)):
            elapsed_str = self._format_snapshot_duration(dur)
            adjusted_title = f"{adjusted_title}  · {elapsed_str}"

        return adjusted_title

    def _format_snapshot_duration(self, dur: int | float) -> str:
        """Format duration for snapshot title."""
        try:
            # Handle invalid types
            if not isinstance(dur, (int, float)):
                return "<1ms"

            if dur >= 1:
                return f"{dur:.2f}s"
            elif int(dur * 1000) > 0:
                return f"{int(dur * 1000)}ms"
            else:
                return "<1ms"
        except (TypeError, ValueError, OverflowError):
            return "<1ms"

    def _clamp_snapshot_body(self, body_text: str) -> str:
        """Clamp snapshot body to configured limits."""
        max_lines = int(self.cfg.snapshot_max_lines or 0)
        lines = body_text.splitlines()
        if max_lines > 0 and len(lines) > max_lines:
            lines = lines[:max_lines] + ["… (truncated)"]
            body_text = "\n".join(lines)

        max_chars = int(self.cfg.snapshot_max_chars or 0)
        if max_chars > 0 and len(body_text) > max_chars:
            suffix = "\n… (truncated)"
            body_text = body_text[: max_chars - len(suffix)] + suffix

        return body_text

    def _create_snapshot_panel(self, adjusted_title: str, body_text: str, finished_tool_name: str) -> Any:
        """Create the snapshot panel."""
        return create_tool_panel(
            title=adjusted_title,
            content=body_text or "(no output)",
            status="finished",
            theme=DEFAULT_RENDERER_THEME,
            is_delegation=is_delegation_tool(finished_tool_name),
        )

    def _print_and_mark_snapshot(self, tool_sid: str, snapshot_panel: Any) -> None:
        """Print snapshot and mark as printed."""
        self.console.print(snapshot_panel)
        self.tool_panels[tool_sid]["snapshot_printed"] = True

    def _create_tool_snapshot(self, finished_tool_name: str, task_id: str, context_id: str) -> None:
        """Create and print a snapshot for a finished tool."""
        tool_sid = f"tool_{finished_tool_name}_{task_id}_{context_id}"

        if not self._should_create_snapshot(tool_sid):
            return

        meta = self.tool_panels[tool_sid]
        adjusted_title = self._get_snapshot_title(meta, finished_tool_name)

        # Compose body from chunks and clamp
        body_text = "".join(meta.get("chunks") or [])
        body_text = self._clamp_snapshot_body(body_text)

        snapshot_panel = self._create_snapshot_panel(adjusted_title, body_text, finished_tool_name)

        self._print_and_mark_snapshot(tool_sid, snapshot_panel)

    def _handle_agent_step(
        self,
        event: dict[str, Any],
        tool_name: str | None,
        tool_args: Any,
        _tool_out: Any,
        tool_calls_info: list[tuple[str, Any, Any]],
        *,
        tracked_step: Step | None = None,
    ) -> None:
        """Handle agent step event."""
        metadata = event.get("metadata", {})
        task_id = event.get("task_id") or metadata.get("task_id")
        context_id = event.get("context_id") or metadata.get("context_id")
        content = event.get("content", "")

        # Create steps and panels for the primary tool
        if tool_name:
            tool_sid = self._ensure_tool_panel(tool_name, tool_args, task_id, context_id)
            self._start_tool_step(
                task_id,
                context_id,
                tool_name,
                tool_args,
                tool_sid,
                tracked_step=tracked_step,
            )

        # Handle additional tool calls
        self._process_additional_tool_calls(tool_calls_info, tool_name, task_id, context_id)

        # Check for tool completion
        (
            is_tool_finished,
            finished_tool_name,
            finished_tool_output,
        ) = self._detect_tool_completion(metadata, content)

        if is_tool_finished and finished_tool_name:
            self._finish_tool_panel(finished_tool_name, finished_tool_output, task_id, context_id)
            self._finish_tool_step(
                finished_tool_name,
                finished_tool_output,
                task_id,
                context_id,
                tracked_step=tracked_step,
            )
            self._create_tool_snapshot(finished_tool_name, task_id, context_id)

    def _spinner(self) -> str:
        """Return spinner character."""
        return get_spinner()

    def _format_working_indicator(self, started_at: float | None) -> str:
        """Format working indicator."""
        return format_working_indicator(
            started_at,
            self.stream_processor.server_elapsed_time,
            self.state.streaming_started_at,
        )

    def close(self) -> None:
        """Gracefully stop any live rendering and release resources."""
        self._shutdown_live()

    def __del__(self) -> None:
        """Destructor that ensures live rendering is properly shut down.

        This is a safety net to prevent resource leaks if the renderer
        is not explicitly stopped.
        """
        # Destructors must never raise
        try:
            self._shutdown_live(reset_attr=False)
        except Exception:  # pragma: no cover - destructor safety net
            pass

    def _shutdown_live(self, reset_attr: bool = True) -> None:
        """Stop the live renderer without letting exceptions escape."""
        live = getattr(self, "live", None)
        if not live:
            if reset_attr and not hasattr(self, "live"):
                self.live = None
            return

        try:
            live.stop()
        except Exception:
            logger.exception("Failed to stop live display")
        finally:
            if reset_attr:
                self.live = None

    def _get_analysis_progress_info(self) -> dict[str, Any]:
        total_steps = len(self.steps.order)
        completed_steps = sum(1 for sid in self.steps.order if is_step_finished(self.steps.by_id[sid]))
        current_step = None
        for sid in self.steps.order:
            if not is_step_finished(self.steps.by_id[sid]):
                current_step = sid
                break
        # Prefer server elapsed time when available
        elapsed = 0.0
        if isinstance(self.stream_processor.server_elapsed_time, (int, float)):
            elapsed = float(self.stream_processor.server_elapsed_time)
        elif self._started_at is not None:
            elapsed = monotonic() - self._started_at
        progress_percent = int((completed_steps / total_steps) * 100) if total_steps else 0
        return {
            "total_steps": total_steps,
            "completed_steps": completed_steps,
            "current_step": current_step,
            "progress_percent": progress_percent,
            "elapsed_time": elapsed,
            "has_running_steps": self._has_running_steps(),
        }

    def _format_enhanced_main_title(self) -> str:
        base = format_main_title(
            header_text=self.header_text,
            has_running_steps=self._has_running_steps(),
            get_spinner_char=get_spinner_char,
        )
        # Add elapsed time and subtle progress hints for long operations
        info = self._get_analysis_progress_info()
        elapsed = info.get("elapsed_time", 0.0)
        if elapsed and elapsed > 0:
            base += f" · {format_elapsed_time(elapsed)}"
        if info.get("total_steps", 0) > 1 and info.get("has_running_steps"):
            if elapsed > 60:
                base += " 🐌"
            elif elapsed > 30:
                base += " ⚠️"
        return base

    # Modern interface only — no legacy helper shims below

    def _refresh(self, _force: bool | None = None) -> None:
        # In the modular renderer, refreshing simply updates the live group
        self._ensure_live()

    def _has_running_steps(self) -> bool:
        """Check if any steps are still running."""
        for _sid, st in self.steps.by_id.items():
            if not is_step_finished(st):
                return True
        return False

    def _get_step_icon(self, step_kind: str) -> str:
        """Get icon for step kind."""
        if step_kind == "tool":
            return ICON_TOOL_STEP
        elif step_kind == "delegate":
            return ICON_DELEGATE
        elif step_kind == "agent":
            return ICON_AGENT_STEP
        return ""

    def _format_step_status(self, step: Step) -> str:
        """Format step status with elapsed time or duration."""
        if is_step_finished(step):
            return self._format_finished_badge(step)
        else:
            # Calculate elapsed time for running steps
            elapsed = self._calculate_step_elapsed_time(step)
            if elapsed >= 0.1:
                return f"[{elapsed:.2f}s]"
            ms = int(round(elapsed * 1000))
            if ms <= 0:
                return ""
            return f"[{ms}ms]"

    def _format_finished_badge(self, step: Step) -> str:
        """Compose duration badge for finished steps including source tagging."""
        if getattr(step, "duration_unknown", False) is True:
            payload = "??s"
        else:
            duration_ms = step.duration_ms
            if duration_ms is None:
                payload = "<1ms"
            elif duration_ms < 0:
                payload = "<1ms"
            elif duration_ms >= 100:
                payload = f"{duration_ms / 1000:.2f}s"
            elif duration_ms > 0:
                payload = f"{duration_ms}ms"
            else:
                payload = "<1ms"

        return f"[{payload}]"

    def _calculate_step_elapsed_time(self, step: Step) -> float:
        """Calculate elapsed time for a running step."""
        server_elapsed = self.stream_processor.server_elapsed_time
        server_start = self._step_server_start_times.get(step.step_id)

        if isinstance(server_elapsed, (int, float)) and isinstance(server_start, (int, float)):
            return max(0.0, float(server_elapsed) - float(server_start))

        try:
            return max(0.0, float(monotonic() - step.started_at))
        except Exception:
            return 0.0

    def _get_step_display_name(self, step: Step) -> str:
        """Get display name for a step."""
        if step.name and step.name != "step":
            return step.name
        return "thinking..." if step.kind == "agent" else f"{step.kind} step"

    def _resolve_step_label(self, step: Step) -> str:
        """Return the display label for a step with sensible fallbacks."""
        raw_label = getattr(step, "display_label", None)
        label = raw_label.strip() if isinstance(raw_label, str) else ""
        if label:
            return normalise_display_label(label)

        if not (step.name or "").strip():
            return UNKNOWN_STEP_DETAIL

        icon = self._get_step_icon(step.kind)
        base_name = self._get_step_display_name(step)
        fallback = " ".join(part for part in (icon, base_name) if part).strip()
        return normalise_display_label(fallback)

    def _check_parallel_tools(self) -> dict[tuple[str | None, str | None], list]:
        """Check for parallel running tools."""
        running_by_ctx: dict[tuple[str | None, str | None], list] = {}
        for sid in self.steps.order:
            st = self.steps.by_id[sid]
            if st.kind == "tool" and not is_step_finished(st):
                key = (st.task_id, st.context_id)
                running_by_ctx.setdefault(key, []).append(st)
        return running_by_ctx

    def _is_parallel_tool(
        self,
        step: Step,
        running_by_ctx: dict[tuple[str | None, str | None], list],
    ) -> bool:
        """Return True if multiple tools are running in the same context."""
        key = (step.task_id, step.context_id)
        return len(running_by_ctx.get(key, [])) > 1

    def _compose_step_renderable(
        self,
        step: Step,
        branch_state: tuple[bool, ...],
    ) -> Any:
        """Compose a single renderable for the hierarchical steps panel."""
        prefix = build_connector_prefix(branch_state)
        text_line = self._build_step_text_line(step, prefix)
        renderables = self._wrap_step_text(step, text_line)

        args_renderable = self._build_args_renderable(step, prefix)
        if args_renderable is not None:
            renderables.append(args_renderable)

        return self._collapse_renderables(renderables)

    def _build_step_text_line(
        self,
        step: Step,
        prefix: str,
    ) -> Text:
        """Create the textual portion of a step renderable."""
        text_line = Text()
        text_line.append(prefix, style="dim")
        text_line.append(self._resolve_step_label(step))

        status_badge = self._format_step_status(step)
        self._append_status_badge(text_line, step, status_badge)
        self._append_state_glyph(text_line, step)
        return text_line

    def _append_status_badge(self, text_line: Text, step: Step, status_badge: str) -> None:
        """Append the formatted status badge when available."""
        glyph_key = getattr(step, "status_icon", None)
        glyph = glyph_for_status(glyph_key)

        if status_badge:
            text_line.append(" ")
            text_line.append(status_badge, style="cyan")

        if glyph:
            text_line.append(" ")
            style = self._status_icon_style(glyph_key)
            if style:
                text_line.append(glyph, style=style)
            else:
                text_line.append(glyph)

    def _append_state_glyph(self, text_line: Text, step: Step) -> None:
        """Append glyph/failure markers in a single place."""
        failure_reason = (step.failure_reason or "").strip()
        if failure_reason:
            text_line.append(f" {failure_reason}")

    @staticmethod
    def _status_icon_style(icon_key: str | None) -> str | None:
        """Return style for a given status icon."""
        if not icon_key:
            return None
        return STATUS_ICON_STYLES.get(icon_key)

    def _wrap_step_text(self, step: Step, text_line: Text) -> list[Any]:
        """Return the base text, optionally decorated with a trailing spinner."""
        if getattr(step, "status", None) == "running":
            spinner = self._step_spinners.get(step.step_id)
            if spinner is None:
                spinner = Spinner("dots", style="dim")
                self._step_spinners[step.step_id] = spinner
            return [TrailingSpinnerLine(text_line, spinner)]

        self._step_spinners.pop(step.step_id, None)
        return [text_line]

    def _collapse_renderables(self, renderables: list[Any]) -> Any:
        """Collapse a list of renderables into a single object."""
        if not renderables:
            return None

        if len(renderables) == 1:
            return renderables[0]

        return Group(*renderables)

    def _build_args_renderable(self, step: Step, prefix: str) -> Text | Group | None:
        """Build a dimmed argument line for tool or agent steps."""
        if step.kind not in {"tool", "delegate", "agent"}:
            return None
        if step.kind == "agent" and step.parent_id:
            return None
        formatted_args = self._format_step_args(step)
        if not formatted_args:
            return None
        if isinstance(formatted_args, list):
            return self._build_arg_list(prefix, formatted_args)

        args_text = Text()
        args_text.append(prefix, style="dim")
        args_text.append(" " * 5)
        args_text.append(formatted_args, style="dim")
        return args_text

    def _build_arg_list(self, prefix: str, formatted_args: list[str | tuple[int, str]]) -> Group | None:
        """Render multi-line argument entries preserving indentation."""
        arg_lines: list[Text] = []
        for indent_level, text_value in self._iter_arg_entries(formatted_args):
            arg_text = Text()
            arg_text.append(prefix, style="dim")
            arg_text.append(" " * 5)
            arg_text.append(" " * (indent_level * 2))
            arg_text.append(text_value, style="dim")
            arg_lines.append(arg_text)
        if not arg_lines:
            return None
        return Group(*arg_lines)

    @staticmethod
    def _iter_arg_entries(
        formatted_args: list[str | tuple[int, str]],
    ) -> Iterable[tuple[int, str]]:
        """Yield normalized indentation/value pairs for argument entries."""
        for value in formatted_args:
            if isinstance(value, tuple) and len(value) == 2:
                indent_level, text_value = value
                yield indent_level, str(text_value)
            else:
                yield 0, str(value)

    def _format_step_args(self, step: Step) -> str | list[str] | list[tuple[int, str]] | None:
        """Return a printable representation of tool arguments."""
        args = getattr(step, "args", None)
        if args is None:
            return None

        if isinstance(args, dict):
            return self._format_dict_args(args, step=step)

        if isinstance(args, (list, tuple)):
            return self._safe_pretty_args(list(args))

        if isinstance(args, (str, int, float)):
            return self._stringify_args(args)

        return None

    def _format_dict_args(self, args: dict[str, Any], *, step: Step) -> str | list[str] | list[tuple[int, str]] | None:
        """Format dictionary arguments with guardrails."""
        if not args:
            return None

        masked_args = self._redact_arg_payload(args)

        if self._should_collapse_single_query(step):
            single_query = self._extract_single_query_arg(masked_args)
            if single_query:
                return single_query

        return self._format_dict_arg_lines(masked_args)

    @staticmethod
    def _extract_single_query_arg(args: dict[str, Any]) -> str | None:
        """Return a trimmed query argument when it is the only entry."""
        if len(args) != 1:
            return None
        key, value = next(iter(args.items()))
        if key != "query" or not isinstance(value, str):
            return None
        stripped = value.strip()
        return stripped or None

    @staticmethod
    def _redact_arg_payload(args: dict[str, Any]) -> dict[str, Any]:
        """Apply best-effort masking before rendering arguments."""
        try:
            cleaned = redact_sensitive(args)
            return cleaned if isinstance(cleaned, dict) else args
        except Exception:
            return args

    @staticmethod
    def _should_collapse_single_query(step: Step) -> bool:
        """Return True when we should display raw query text."""
        if step.kind == "agent":
            return True
        if step.kind == "delegate":
            return True
        return False

    def _format_dict_arg_lines(self, args: dict[str, Any]) -> list[tuple[int, str]] | None:
        """Render dictionary arguments as nested YAML-style lines."""
        lines: list[tuple[int, str]] = []
        for raw_key, value in args.items():
            key = str(raw_key)
            lines.extend(self._format_nested_entry(key, value, indent=0))
        return lines or None

    def _format_nested_entry(self, key: str, value: Any, indent: int) -> list[tuple[int, str]]:
        """Format a mapping entry recursively."""
        lines: list[tuple[int, str]] = []

        if isinstance(value, dict):
            if value:
                lines.append((indent, f"{key}:"))
                lines.extend(self._format_nested_mapping(value, indent + 1))
            else:
                lines.append((indent, f"{key}: {{}}"))
            return lines

        if isinstance(value, (list, tuple, set)):
            seq_lines = self._format_sequence_entries(list(value), indent + 1)
            if seq_lines:
                lines.append((indent, f"{key}:"))
                lines.extend(seq_lines)
            else:
                lines.append((indent, f"{key}: []"))
            return lines

        formatted_value = self._format_arg_value(value)
        if formatted_value is not None:
            lines.append((indent, f"{key}: {formatted_value}"))
        return lines

    def _format_nested_mapping(self, mapping: dict[str, Any], indent: int) -> list[tuple[int, str]]:
        """Format nested dictionary values."""
        nested_lines: list[tuple[int, str]] = []
        for raw_key, value in mapping.items():
            key = str(raw_key)
            nested_lines.extend(self._format_nested_entry(key, value, indent))
        return nested_lines

    def _format_sequence_entries(self, sequence: list[Any], indent: int) -> list[tuple[int, str]]:
        """Format list/tuple/set values with YAML-style bullets."""
        if not sequence:
            return []

        lines: list[tuple[int, str]] = []
        for item in sequence:
            lines.extend(self._format_sequence_item(item, indent))
        return lines

    def _format_sequence_item(self, item: Any, indent: int) -> list[tuple[int, str]]:
        """Format a single list entry."""
        if isinstance(item, dict):
            return self._format_dict_sequence_item(item, indent)

        if isinstance(item, (list, tuple, set)):
            return self._format_nested_sequence_item(list(item), indent)

        formatted = self._format_arg_value(item)
        if formatted is not None:
            return [(indent, f"- {formatted}")]
        return []

    def _format_dict_sequence_item(self, mapping: dict[str, Any], indent: int) -> list[tuple[int, str]]:
        """Format a dictionary entry within a list."""
        child_lines = self._format_nested_mapping(mapping, indent + 1)
        if child_lines:
            return self._prepend_sequence_prefix(child_lines, indent)
        return [(indent, "- {}")]

    def _format_nested_sequence_item(self, sequence: list[Any], indent: int) -> list[tuple[int, str]]:
        """Format a nested sequence entry within a list."""
        child_lines = self._format_sequence_entries(sequence, indent + 1)
        if child_lines:
            return self._prepend_sequence_prefix(child_lines, indent)
        return [(indent, "- []")]

    @staticmethod
    def _prepend_sequence_prefix(child_lines: list[tuple[int, str]], indent: int) -> list[tuple[int, str]]:
        """Attach a sequence bullet to the first child line."""
        _, first_text = child_lines[0]
        prefixed: list[tuple[int, str]] = [(indent, f"- {first_text}")]
        prefixed.extend(child_lines[1:])
        return prefixed

    def _format_arg_value(self, value: Any) -> str | None:
        """Format a single argument value with per-value truncation."""
        if value is None:
            return "null"
        if isinstance(value, (bool, int, float)):
            return json.dumps(value, ensure_ascii=False)
        if isinstance(value, str):
            return self._format_string_arg_value(value)
        return _truncate_display(str(value), limit=ARGS_VALUE_MAX_LEN)

    @staticmethod
    def _format_string_arg_value(value: str) -> str:
        """Return a trimmed, quoted representation of a string argument."""
        sanitised = value.replace("\n", " ").strip()
        sanitised = sanitised.replace('"', '\\"')
        trimmed = _truncate_display(sanitised, limit=ARGS_VALUE_MAX_LEN)
        return f'"{trimmed}"'

    @staticmethod
    def _safe_pretty_args(args: dict[str, Any]) -> str | None:
        """Defensively format argument dictionaries."""
        try:
            return pretty_args(args, max_len=160)
        except Exception:
            return str(args)

    @staticmethod
    def _stringify_args(args: Any) -> str | None:
        """Format non-dictionary argument payloads."""
        text = str(args).strip()
        if not text:
            return None
        return _truncate_display(text)

    def _render_steps_text(self) -> Any:
        """Render the steps panel content."""
        if not (self.steps.order or self.steps.children):
            return _NO_STEPS_TEXT.copy()

        nodes = list(self.steps.iter_tree())
        if not nodes:
            return _NO_STEPS_TEXT.copy()

        window = self._summary_window_size()
        display_nodes, header_notice, footer_notice = clamp_step_nodes(
            nodes,
            window=window,
            get_label=self._get_step_label,
            get_parent=self._get_step_parent,
        )
        step_renderables = self._build_step_renderables(display_nodes)

        if not step_renderables and not header_notice and not footer_notice:
            return _NO_STEPS_TEXT.copy()

        return self._assemble_step_renderables(step_renderables, header_notice, footer_notice)

    def _get_step_label(self, step_id: str) -> str:
        """Get label for a step by ID."""
        step = self.steps.by_id.get(step_id)
        if step:
            return self._resolve_step_label(step)
        return UNKNOWN_STEP_DETAIL

    def _get_step_parent(self, step_id: str) -> str | None:
        """Get parent ID for a step by ID."""
        step = self.steps.by_id.get(step_id)
        return step.parent_id if step else None

    def _summary_window_size(self) -> int:
        """Return the active window size for step display."""
        if self.state.finalizing_ui:
            return 0
        return int(self.cfg.summary_display_window or 0)

    def _assemble_step_renderables(self, step_renderables: list[Any], header_notice: Any, footer_notice: Any) -> Any:
        """Assemble step renderables with header and footer into final output."""
        renderables: list[Any] = []
        if header_notice is not None:
            renderables.append(header_notice)
        renderables.extend(step_renderables)
        if footer_notice is not None:
            renderables.append(footer_notice)

        if len(renderables) == 1:
            return renderables[0]

        return Group(*renderables)

    def _build_step_renderables(self, display_nodes: list[tuple[str, tuple[bool, ...]]]) -> list[Any]:
        """Convert step nodes to renderables for the steps panel."""
        renderables: list[Any] = []
        for step_id, branch_state in display_nodes:
            step = self.steps.by_id.get(step_id)
            if not step:
                continue
            renderable = self._compose_step_renderable(step, branch_state)
            if renderable is not None:
                renderables.append(renderable)
        return renderables

    def _update_final_duration(self, duration: float | None, *, overwrite: bool = False) -> None:
        """Store formatted duration for eventual final panels."""
        if duration is None:
            return

        try:
            duration_val = max(0.0, float(duration))
        except Exception:
            return

        existing = self.state.final_duration_seconds

        if not overwrite and existing is not None:
            return

        if overwrite and existing is not None:
            duration_val = max(existing, duration_val)

        self.state.final_duration_seconds = duration_val
        self.state.final_duration_text = self._format_elapsed_time(duration_val)
        self._apply_root_duration(duration_val)

    def _format_elapsed_time(self, elapsed: float) -> str:
        """Format elapsed time as a readable string."""
        if elapsed >= 1:
            return f"{elapsed:.2f}s"
        elif int(elapsed * 1000) > 0:
            return f"{int(elapsed * 1000)}ms"
        else:
            return "<1ms"

    def _format_dict_or_list_output(self, output_value: dict | list) -> str:
        """Format dict/list output as pretty JSON."""
        try:
            return self.OUTPUT_PREFIX + "```json\n" + json.dumps(output_value, indent=2) + "\n```\n"
        except Exception:
            return self.OUTPUT_PREFIX + str(output_value) + "\n"

    def _clean_sub_agent_prefix(self, output: str, tool_name: str | None) -> str:
        """Clean sub-agent name prefix from output."""
        if not (tool_name and is_delegation_tool(tool_name)):
            return output

        sub = tool_name
        if tool_name.startswith("delegate_to_"):
            sub = tool_name.replace("delegate_to_", "")
        elif tool_name.startswith("delegate_"):
            sub = tool_name.replace("delegate_", "")
        prefix = f"[{sub}]"
        if output.startswith(prefix):
            return output[len(prefix) :].lstrip()

        return output

    def _format_json_string_output(self, output: str) -> str:
        """Format string that looks like JSON."""
        try:
            parsed = json.loads(output)
            return self.OUTPUT_PREFIX + "```json\n" + json.dumps(parsed, indent=2) + "\n```\n"
        except Exception:
            return self.OUTPUT_PREFIX + output + "\n"

    def _format_string_output(self, output: str, tool_name: str | None) -> str:
        """Format string output with optional prefix cleaning."""
        s = output.strip()
        s = self._clean_sub_agent_prefix(s, tool_name)

        # If looks like JSON, pretty print it
        if (s.startswith("{") and s.endswith("}")) or (s.startswith("[") and s.endswith("]")):
            return self._format_json_string_output(s)

        return self.OUTPUT_PREFIX + s + "\n"

    def _format_other_output(self, output_value: Any) -> str:
        """Format other types of output."""
        try:
            return self.OUTPUT_PREFIX + json.dumps(output_value, indent=2) + "\n"
        except Exception:
            return self.OUTPUT_PREFIX + str(output_value) + "\n"

    def _format_output_block(self, output_value: Any, tool_name: str | None) -> str:
        """Format an output value for panel display."""
        if isinstance(output_value, (dict, list)):
            return self._format_dict_or_list_output(output_value)
        elif isinstance(output_value, str):
            return self._format_string_output(output_value, tool_name)
        else:
            return self._format_other_output(output_value)
