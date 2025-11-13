"""Interactive viewer for post-run transcript exploration.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import click
from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

try:  # pragma: no cover - optional dependency
    import questionary
    from questionary import Choice
except Exception:  # pragma: no cover - optional dependency
    questionary = None  # type: ignore[assignment]
    Choice = None  # type: ignore[assignment]

from glaip_sdk.cli.transcript.cache import suggest_filename
from glaip_sdk.icons import ICON_AGENT, ICON_DELEGATE, ICON_TOOL_STEP
from glaip_sdk.rich_components import AIPPanel
from glaip_sdk.utils.rendering.formatting import (
    build_connector_prefix,
    glyph_for_status,
    normalise_display_label,
)
from glaip_sdk.utils.rendering.renderer.debug import render_debug_event
from glaip_sdk.utils.rendering.renderer.panels import create_final_panel
from glaip_sdk.utils.rendering.renderer.progress import (
    format_elapsed_time,
    is_delegation_tool,
)
from glaip_sdk.utils.rendering.steps import StepManager

EXPORT_CANCELLED_MESSAGE = "[dim]Export cancelled.[/dim]"


@dataclass(slots=True)
class ViewerContext:
    """Runtime context for the viewer session."""

    manifest_entry: dict[str, Any]
    events: list[dict[str, Any]]
    default_output: str
    final_output: str
    stream_started_at: float | None
    meta: dict[str, Any]


class PostRunViewer:  # pragma: no cover - interactive flows are not unit tested
    """Simple interactive session for inspecting agent run transcripts."""

    def __init__(
        self,
        console: Console,
        ctx: ViewerContext,
        export_callback: Callable[[Path], Path],
        *,
        initial_view: str = "default",
    ) -> None:
        """Initialize viewer state for a captured transcript."""
        self.console = console
        self.ctx = ctx
        self._export_callback = export_callback
        self._view_mode = initial_view if initial_view in {"default", "transcript"} else "default"

    def run(self) -> None:
        """Enter the interactive loop."""
        if not self.ctx.events and not (self.ctx.default_output or self.ctx.final_output):
            return
        if self._view_mode == "transcript":
            self._render()
        self._print_command_hint()
        self._fallback_loop()

    # ------------------------------------------------------------------
    # Rendering helpers
    # ------------------------------------------------------------------
    def _render(self) -> None:
        try:
            if self.console.is_terminal:
                self.console.clear()
        except Exception:  # pragma: no cover - platform quirks
            pass

        header = f"Agent transcript viewer · run {self.ctx.manifest_entry.get('run_id')}"
        agent_label = self.ctx.manifest_entry.get("agent_name") or "unknown agent"
        model = self.ctx.manifest_entry.get("model") or self.ctx.meta.get("model")
        agent_id = self.ctx.manifest_entry.get("agent_id")
        subtitle_parts = [agent_label]
        if model:
            subtitle_parts.append(str(model))
        if agent_id:
            subtitle_parts.append(agent_id)

        if self._view_mode == "transcript":
            self.console.rule(header)
            if subtitle_parts:
                self.console.print(f"[dim]{' · '.join(subtitle_parts)}[/]")
            self.console.print()

        query = self._get_user_query()

        if self._view_mode == "default":
            self._render_default_view(query)
        else:
            self._render_transcript_view(query)

    def _render_default_view(self, query: str | None) -> None:
        if query:
            self._render_user_query(query)
        self._render_steps_summary()
        self._render_final_panel()

    def _render_transcript_view(self, query: str | None) -> None:
        if not self.ctx.events:
            self.console.print("[dim]No SSE events were captured for this run.[/dim]")
            return

        if query:
            self._render_user_query(query)

        self._render_steps_summary()
        self._render_final_panel()

        self.console.print("[bold]Transcript Events[/bold]")
        self.console.print("[dim]────────────────────────────────────────────────────────[/dim]")

        base_received_ts: datetime | None = None
        for event in self.ctx.events:
            received_ts = self._parse_received_timestamp(event)
            if base_received_ts is None and received_ts is not None:
                base_received_ts = received_ts
            render_debug_event(
                event,
                self.console,
                received_ts=received_ts,
                baseline_ts=base_received_ts,
            )
        self.console.print()

    def _render_final_panel(self) -> None:
        content = self.ctx.final_output or self.ctx.default_output or "No response content captured."
        title = "Final Result"
        duration_text = self._extract_final_duration()
        if duration_text:
            title += f" · {duration_text}"
        panel = create_final_panel(content, title=title, theme="dark")
        self.console.print(panel)
        self.console.print()

    # ------------------------------------------------------------------
    # Interaction loops
    # ------------------------------------------------------------------
    def _fallback_loop(self) -> None:
        while True:
            try:
                ch = click.getchar()
            except (EOFError, KeyboardInterrupt):
                break

            if ch in {"\r", "\n"}:
                break

            if ch == "\x14" or ch.lower() == "t":  # Ctrl+T or t
                self.toggle_view()
                continue

            if ch.lower() == "e":
                self.export_transcript()
                self._print_command_hint()
            else:
                continue

    def _handle_command(self, raw: str) -> bool:
        lowered = raw.lower()
        if lowered in {"exit", "quit", "q"}:
            return True
        if lowered in {"export", "e"}:
            self.export_transcript()
            self._print_command_hint()
            return False
        self.console.print("[dim]Commands: export, exit.[/dim]")
        return False

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def toggle_view(self) -> None:
        """Switch between default result view and verbose transcript."""
        self._view_mode = "transcript" if self._view_mode == "default" else "default"
        self._render()
        self._print_command_hint()

    def export_transcript(self) -> None:
        """Prompt user for a destination and export the cached transcript."""
        entry = self.ctx.manifest_entry
        default_name = suggest_filename(entry)
        default_path = Path.cwd() / default_name

        def _display_path(path: Path) -> str:
            raw = str(path)
            return raw if len(raw) <= 80 else f"…{raw[-77:]}"

        selection = self._prompt_export_choice(default_path, _display_path(default_path))
        if selection is None:
            self._legacy_export_prompt(default_path, _display_path)
            return

        action, _ = selection
        if action == "cancel":
            self.console.print(EXPORT_CANCELLED_MESSAGE)
            return

        if action == "default":
            destination = default_path
        else:
            destination = self._prompt_custom_destination()
            if destination is None:
                self.console.print(EXPORT_CANCELLED_MESSAGE)
                return

        try:
            target = self._export_callback(destination)
            self.console.print(f"[green]Transcript exported to {target}[/green]")
        except FileNotFoundError as exc:
            self.console.print(f"[red]{exc}[/red]")
        except Exception as exc:  # pragma: no cover - unexpected IO failures
            self.console.print(f"[red]Failed to export transcript: {exc}[/red]")

    def _prompt_export_choice(self, default_path: Path, default_display: str) -> tuple[str, Any] | None:
        """Render interactive export menu with numeric shortcuts."""
        if not self.console.is_terminal or questionary is None or Choice is None:
            return None

        try:
            answer = questionary.select(
                "Export transcript",
                choices=[
                    Choice(
                        title=f"Save to default ({default_display})",
                        value=("default", default_path),
                        shortcut_key="1",
                    ),
                    Choice(
                        title="Choose a different path",
                        value=("custom", None),
                        shortcut_key="2",
                    ),
                    Choice(
                        title="Cancel",
                        value=("cancel", None),
                        shortcut_key="3",
                    ),
                ],
                use_shortcuts=True,
                instruction="Press 1-3 (or arrows) then Enter.",
            ).ask()
        except Exception:
            return None

        if answer is None:
            return ("cancel", None)
        return answer

    def _prompt_custom_destination(self) -> Path | None:
        """Prompt for custom export path with filesystem completion."""
        if not self.console.is_terminal:
            return None

        try:
            response = questionary.path(
                "Destination path (Tab to autocomplete):",
                default="",
                only_directories=False,
            ).ask()
        except Exception:
            return None

        if not response:
            return None

        candidate = Path(response.strip()).expanduser()
        if not candidate.is_absolute():
            candidate = Path.cwd() / candidate
        return candidate

    def _legacy_export_prompt(self, default_path: Path, formatter: Callable[[Path], str]) -> None:
        """Fallback export workflow when interactive UI is unavailable."""
        self.console.print("[dim]Export options (fallback mode)[/dim]")
        self.console.print(f"  1. Save to default ({formatter(default_path)})")
        self.console.print("  2. Choose a different path")
        self.console.print("  3. Cancel")

        try:
            choice = click.prompt(
                "Select option",
                type=click.Choice(["1", "2", "3"], case_sensitive=False),
                default="1",
                show_choices=False,
            )
        except (EOFError, KeyboardInterrupt):
            self.console.print(EXPORT_CANCELLED_MESSAGE)
            return

        if choice == "3":
            self.console.print(EXPORT_CANCELLED_MESSAGE)
            return

        if choice == "1":
            destination = default_path
        else:
            try:
                destination_str = click.prompt("Enter destination path", default="")
            except (EOFError, KeyboardInterrupt):
                self.console.print(EXPORT_CANCELLED_MESSAGE)
                return
            if not destination_str.strip():
                self.console.print(EXPORT_CANCELLED_MESSAGE)
                return
            destination = Path(destination_str.strip()).expanduser()
            if not destination.is_absolute():
                destination = Path.cwd() / destination

        try:
            target = self._export_callback(destination)
            self.console.print(f"[green]Transcript exported to {target}[/green]")
        except FileNotFoundError as exc:
            self.console.print(f"[red]{exc}[/red]")
        except Exception as exc:  # pragma: no cover - unexpected IO failures
            self.console.print(f"[red]Failed to export transcript: {exc}[/red]")

    def _print_command_hint(self) -> None:
        self.console.print("[dim]Ctrl+T to toggle transcript · type `e` to export · press Enter to exit[/dim]")
        self.console.print()

    def _get_user_query(self) -> str | None:
        meta = self.ctx.meta or {}
        manifest = self.ctx.manifest_entry or {}
        return meta.get("input_message") or meta.get("query") or meta.get("message") or manifest.get("input_message")

    def _render_user_query(self, query: str) -> None:
        panel = AIPPanel(
            Markdown(f"Query: {query}"),
            title="User Request",
            border_style="#d97706",
        )
        self.console.print(panel)
        self.console.print()

    def _render_steps_summary(self) -> None:
        stored_lines = self.ctx.meta.get("transcript_step_lines")
        if stored_lines:
            body = Text("\n".join(stored_lines), style="dim")
        else:
            tree_text = self._build_tree_summary_text()
            if tree_text is not None:
                body = tree_text
            else:
                panel_content = self._format_steps_summary(self._build_step_summary())
                body = Text(panel_content, style="dim")
        panel = AIPPanel(body, title="Steps", border_style="blue")
        self.console.print(panel)
        self.console.print()

    @staticmethod
    def _format_steps_summary(steps: list[dict[str, Any]]) -> str:
        if not steps:
            return "  No steps yet"

        lines = []
        for step in steps:
            icon = ICON_DELEGATE if step.get("is_delegate") else ICON_TOOL_STEP
            duration = step.get("duration")
            duration_str = f" [{duration}]" if duration else ""
            status = " ✓" if step.get("finished") else ""
            title = step.get("title") or step.get("name") or "Step"
            lines.append(f"  {icon} {title}{duration_str}{status}")
        return "\n".join(lines)

    @staticmethod
    def _extract_event_time(event: dict[str, Any]) -> float | None:
        metadata = event.get("metadata") or {}
        time_value = metadata.get("time")
        try:
            if isinstance(time_value, (int, float)):
                return float(time_value)
        except Exception:
            return None
        return None

    @staticmethod
    def _parse_received_timestamp(event: dict[str, Any]) -> datetime | None:
        value = event.get("received_at")
        if not value:
            return None
        if isinstance(value, str):
            try:
                normalised = value.replace("Z", "+00:00")
                parsed = datetime.fromisoformat(normalised)
            except ValueError:
                return None
            return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
        return None

    def _extract_final_duration(self) -> str | None:
        for event in self.ctx.events:
            metadata = event.get("metadata") or {}
            if metadata.get("kind") == "final_response":
                time_value = metadata.get("time")
                try:
                    if isinstance(time_value, (int, float)):
                        return f"{float(time_value):.2f}s"
                except Exception:
                    return None
        return None

    def _build_step_summary(self) -> list[dict[str, Any]]:
        stored = self.ctx.meta.get("transcript_steps")
        if isinstance(stored, list) and stored:
            return [
                {
                    "title": entry.get("display_name") or entry.get("name") or "Step",
                    "is_delegate": entry.get("kind") == "delegate",
                    "finished": entry.get("status") == "finished",
                    "duration": self._format_duration_from_ms(entry.get("duration_ms")),
                }
                for entry in stored
            ]

        steps: dict[str, dict[str, Any]] = {}
        order: list[str] = []

        for event in self.ctx.events:
            metadata = event.get("metadata") or {}
            if not self._is_step_event(metadata):
                continue

            for name, info in self._iter_step_candidates(event, metadata):
                step = self._ensure_step_entry(steps, order, name)
                self._apply_step_update(step, metadata, info, event)

        return [steps[name] for name in order]

    def _build_tree_summary_text(self) -> Text | None:
        """Render hierarchical tree from captured SSE events when available."""
        manager = StepManager()
        processed = False

        for event in self.ctx.events:
            payload = self._coerce_step_event(event)
            if not payload:
                continue
            try:
                manager.apply_event(payload)
                processed = True
            except ValueError:
                continue

        if not processed or not manager.order:
            return None

        lines: list[str] = []
        roots = manager.order
        total_roots = len(roots)
        for index, root_id in enumerate(roots):
            self._render_tree_branch(
                manager=manager,
                step_id=root_id,
                ancestor_state=(),
                is_last=index == total_roots - 1,
                lines=lines,
            )

        if not lines:
            return None

        self._decorate_root_presentation(manager, roots[0], lines)

        return Text("\n".join(lines), style="dim")

    def _render_tree_branch(
        self,
        *,
        manager: StepManager,
        step_id: str,
        ancestor_state: tuple[bool, ...],
        is_last: bool,
        lines: list[str],
    ) -> None:
        step = manager.by_id.get(step_id)
        if not step:
            return
        suppress = self._should_hide_step(step)
        children = manager.children.get(step_id, [])

        if not suppress:
            branch_state = ancestor_state
            if branch_state:
                branch_state = branch_state + (is_last,)
            lines.append(self._format_tree_line(step, branch_state))
            next_ancestor_state = ancestor_state + (is_last,)
        else:
            next_ancestor_state = ancestor_state

        if not children:
            return

        total_children = len(children)
        for idx, child_id in enumerate(children):
            self._render_tree_branch(
                manager=manager,
                step_id=child_id,
                ancestor_state=next_ancestor_state if not suppress else ancestor_state,
                is_last=idx == total_children - 1,
                lines=lines,
            )

    def _should_hide_step(self, step: Any) -> bool:
        if getattr(step, "parent_id", None) is None:
            return False
        name = getattr(step, "name", "") or ""
        return self._looks_like_uuid(name)

    def _decorate_root_presentation(
        self,
        manager: StepManager,
        root_id: str,
        lines: list[str],
    ) -> None:
        if not lines:
            return

        root_step = manager.by_id.get(root_id)
        if not root_step:
            return

        original_label = getattr(root_step, "display_label", None)
        root_step.display_label = self._friendly_root_label(root_step, original_label)
        lines[0] = self._format_tree_line(root_step, ())
        if original_label is not None:
            root_step.display_label = original_label

        query = self._get_user_query()
        if query:
            lines.insert(1, f"     {query}")

    def _coerce_step_event(self, event: dict[str, Any]) -> dict[str, Any] | None:
        metadata = event.get("metadata")
        if not isinstance(metadata, dict):
            return None
        if not isinstance(metadata.get("step_id"), str):
            return None
        return {
            "metadata": metadata,
            "status": event.get("status"),
            "task_state": event.get("task_state"),
            "content": event.get("content"),
            "task_id": event.get("task_id"),
            "context_id": event.get("context_id"),
        }

    def _format_tree_line(self, step: Any, branch_state: tuple[bool, ...]) -> str:
        prefix = build_connector_prefix(branch_state)
        raw_label = normalise_display_label(getattr(step, "display_label", None))
        title, summary = self._split_label(raw_label)
        line = f"{prefix}{title}"

        if summary:
            line += f" — {self._truncate_summary(summary)}"

        badge = self._format_duration_badge(step)
        if badge:
            line += f" {badge}"

        glyph = glyph_for_status(getattr(step, "status_icon", None))
        failure_reason = getattr(step, "failure_reason", None)
        if glyph and glyph != "spinner":
            if failure_reason and glyph == "✗":
                line += f" {glyph} {failure_reason}"
            else:
                line += f" {glyph}"
        elif failure_reason:
            line += f" ✗ {failure_reason}"

        return line

    def _friendly_root_label(self, step: Any, fallback: str | None) -> str:
        agent_name = self.ctx.manifest_entry.get("agent_name") or (self.ctx.meta or {}).get("agent_name")
        agent_id = self.ctx.manifest_entry.get("agent_id") or getattr(step, "name", "")

        if not agent_name:
            return fallback or agent_id or ICON_AGENT

        parts = [ICON_AGENT, agent_name]
        if agent_id and agent_id != agent_name:
            parts.append(f"({agent_id})")
        return " ".join(parts)

    @staticmethod
    def _format_duration_badge(step: Any) -> str | None:
        duration_ms = getattr(step, "duration_ms", None)
        if duration_ms is None:
            return None
        try:
            duration_ms = int(duration_ms)
        except Exception:
            return None

        if duration_ms <= 0:
            payload = "<1ms"
        elif duration_ms >= 1000:
            payload = f"{duration_ms / 1000:.2f}s"
        else:
            payload = f"{duration_ms}ms"

        return f"[{payload}]"

    @staticmethod
    def _split_label(label: str) -> tuple[str, str | None]:
        if " — " in label:
            title, summary = label.split(" — ", 1)
            return title.strip(), summary.strip()
        return label.strip(), None

    @staticmethod
    def _truncate_summary(summary: str, limit: int = 48) -> str:
        summary = summary.strip()
        if len(summary) <= limit:
            return summary
        return summary[: limit - 1].rstrip() + "…"

    @staticmethod
    def _looks_like_uuid(value: str) -> bool:
        stripped = value.replace("-", "").replace(" ", "")
        if len(stripped) not in {32, 36}:
            return False
        return all(ch in "0123456789abcdefABCDEF" for ch in stripped)

    @staticmethod
    def _format_duration_from_ms(value: Any) -> str | None:
        try:
            if value is None:
                return None
            duration_ms = float(value)
        except Exception:
            return None

        if duration_ms <= 0:
            return "<1ms"
        if duration_ms < 1000:
            return f"{int(duration_ms)}ms"
        return f"{duration_ms / 1000:.2f}s"

    @staticmethod
    def _is_step_event(metadata: dict[str, Any]) -> bool:
        kind = metadata.get("kind")
        return kind in {"agent_step", "agent_thinking_step"}

    def _iter_step_candidates(
        self, event: dict[str, Any], metadata: dict[str, Any]
    ) -> Iterable[tuple[str, dict[str, Any]]]:
        tool_info = metadata.get("tool_info") or {}

        yielded = False
        for candidate in self._iter_tool_call_candidates(tool_info):
            yielded = True
            yield candidate

        if yielded:
            return

        direct_tool = self._extract_direct_tool(tool_info)
        if direct_tool is not None:
            yield direct_tool
            return

        completed = self._extract_completed_name(event)
        if completed is not None:
            yield completed, {}

    @staticmethod
    def _iter_tool_call_candidates(
        tool_info: dict[str, Any],
    ) -> Iterable[tuple[str, dict[str, Any]]]:
        tool_calls = tool_info.get("tool_calls")
        if isinstance(tool_calls, list):
            for call in tool_calls:
                name = call.get("name")
                if name:
                    yield name, call

    @staticmethod
    def _extract_direct_tool(
        tool_info: dict[str, Any],
    ) -> tuple[str, dict[str, Any]] | None:
        if isinstance(tool_info, dict):
            name = tool_info.get("name")
            if name:
                return name, tool_info
        return None

    @staticmethod
    def _extract_completed_name(event: dict[str, Any]) -> str | None:
        content = event.get("content") or ""
        if isinstance(content, str) and content.startswith("Completed "):
            name = content.replace("Completed ", "").strip()
            if name:
                return name
        return None

    def _ensure_step_entry(
        self,
        steps: dict[str, dict[str, Any]],
        order: list[str],
        name: str,
    ) -> dict[str, Any]:
        if name not in steps:
            steps[name] = {
                "name": name,
                "title": name,
                "is_delegate": is_delegation_tool(name),
                "duration": None,
                "started_at": None,
                "finished": False,
            }
            order.append(name)
        return steps[name]

    def _apply_step_update(
        self,
        step: dict[str, Any],
        metadata: dict[str, Any],
        info: dict[str, Any],
        event: dict[str, Any],
    ) -> None:
        status = metadata.get("status")
        event_time = metadata.get("time")

        if status == "running" and step.get("started_at") is None and isinstance(event_time, (int, float)):
            try:
                step["started_at"] = float(event_time)
            except Exception:
                step["started_at"] = None

        if self._is_step_finished(metadata, event):
            step["finished"] = True

        duration = self._compute_step_duration(step, info, metadata)
        if duration is not None:
            step["duration"] = duration

    @staticmethod
    def _is_step_finished(metadata: dict[str, Any], event: dict[str, Any]) -> bool:
        status = metadata.get("status")
        return status == "finished" or bool(event.get("final"))

    def _compute_step_duration(
        self, step: dict[str, Any], info: dict[str, Any], metadata: dict[str, Any]
    ) -> str | None:
        """Calculate a formatted duration string for a step if possible."""
        event_time = metadata.get("time")
        started_at = step.get("started_at")
        duration_value: float | None = None

        if isinstance(event_time, (int, float)) and isinstance(started_at, (int, float)):
            try:
                delta = float(event_time) - float(started_at)
                if delta >= 0:
                    duration_value = delta
            except Exception:
                duration_value = None

        if duration_value is None:
            exec_time = info.get("execution_time")
            if isinstance(exec_time, (int, float)):
                duration_value = float(exec_time)

        if duration_value is None:
            return None

        try:
            return format_elapsed_time(duration_value)
        except Exception:
            return None


def run_viewer_session(
    console: Console,
    ctx: ViewerContext,
    export_callback: Callable[[Path], Path],
    *,
    initial_view: str = "default",
) -> None:
    """Entry point for creating and running the post-run viewer."""
    viewer = PostRunViewer(console, ctx, export_callback, initial_view=initial_view)
    viewer.run()
