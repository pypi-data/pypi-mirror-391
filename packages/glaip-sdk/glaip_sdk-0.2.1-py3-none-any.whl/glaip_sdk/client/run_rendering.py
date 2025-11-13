#!/usr/bin/env python3
"""Rendering helpers for agent streaming flows.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import io
import json
import logging
from time import monotonic
from typing import Any

import httpx
from rich.console import Console as _Console

from glaip_sdk.config.constants import DEFAULT_AGENT_RUN_TIMEOUT
from glaip_sdk.utils.client_utils import iter_sse_events
from glaip_sdk.utils.rendering.models import RunStats
from glaip_sdk.utils.rendering.renderer import RichStreamRenderer
from glaip_sdk.utils.rendering.renderer.config import RendererConfig


def _coerce_to_string(value: Any) -> str:
    """Return a best-effort string representation for transcripts."""
    try:
        return str(value)
    except Exception:
        return f"{value}"


def _has_visible_text(value: Any) -> bool:
    """Return True when the value is a non-empty string."""
    return isinstance(value, str) and bool(value.strip())


def _update_state_transcript(state: Any, text_value: str) -> bool:
    """Inject transcript text into renderer state if possible."""
    if state is None:
        return False

    updated = False

    if hasattr(state, "final_text") and not _has_visible_text(getattr(state, "final_text", "")):
        try:
            state.final_text = text_value
            updated = True
        except Exception:
            pass

    buffer = getattr(state, "buffer", None)
    if isinstance(buffer, list) and not any(_has_visible_text(item) for item in buffer):
        buffer.append(text_value)
        updated = True

    return updated


def _update_renderer_transcript(renderer: Any, text_value: str) -> None:
    """Populate the renderer (or its state) with the supplied text."""
    state = getattr(renderer, "state", None)
    if _update_state_transcript(state, text_value):
        return

    if hasattr(renderer, "final_text") and not _has_visible_text(getattr(renderer, "final_text", "")):
        try:
            renderer.final_text = text_value
        except Exception:
            pass


class AgentRunRenderingManager:
    """Coordinate renderer creation and streaming event handling."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize the rendering manager.

        Args:
            logger: Optional logger instance, creates default if None
        """
        self._logger = logger or logging.getLogger(__name__)

    # --------------------------------------------------------------------- #
    # Renderer setup helpers
    # --------------------------------------------------------------------- #
    def create_renderer(
        self,
        renderer_spec: RichStreamRenderer | str | None,
        *,
        verbose: bool = False,
    ) -> RichStreamRenderer:
        """Create an appropriate renderer based on the supplied spec."""
        if isinstance(renderer_spec, RichStreamRenderer):
            return renderer_spec

        if isinstance(renderer_spec, str):
            if renderer_spec == "silent":
                return self._create_silent_renderer()
            if renderer_spec == "minimal":
                return self._create_minimal_renderer()
            return self._create_default_renderer(verbose)

        return self._create_default_renderer(verbose)

    def build_initial_metadata(
        self,
        agent_id: str,
        message: str,
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """Construct the initial renderer metadata payload."""
        return {
            "agent_name": kwargs.get("agent_name", agent_id),
            "model": kwargs.get("model"),
            "run_id": None,
            "input_message": message,
        }

    @staticmethod
    def start_renderer(renderer: RichStreamRenderer, meta: dict[str, Any]) -> None:
        """Notify renderer that streaming is starting."""
        renderer.on_start(meta)

    def _create_silent_renderer(self) -> RichStreamRenderer:
        silent_config = RendererConfig(
            live=False,
            persist_live=False,
            render_thinking=False,
        )
        return RichStreamRenderer(
            console=_Console(file=io.StringIO(), force_terminal=False),
            cfg=silent_config,
            verbose=False,
        )

    def _create_minimal_renderer(self) -> RichStreamRenderer:
        minimal_config = RendererConfig(
            live=False,
            persist_live=False,
            render_thinking=False,
        )
        return RichStreamRenderer(
            console=_Console(),
            cfg=minimal_config,
            verbose=False,
        )

    def _create_verbose_renderer(self) -> RichStreamRenderer:
        verbose_config = RendererConfig(
            live=False,
            append_finished_snapshots=False,
        )
        return RichStreamRenderer(
            console=_Console(),
            cfg=verbose_config,
            verbose=True,
        )

    def _create_default_renderer(self, verbose: bool) -> RichStreamRenderer:
        if verbose:
            return self._create_verbose_renderer()
        default_config = RendererConfig()
        return RichStreamRenderer(console=_Console(), cfg=default_config)

    # --------------------------------------------------------------------- #
    # Streaming event handling
    # --------------------------------------------------------------------- #
    def process_stream_events(
        self,
        stream_response: httpx.Response,
        renderer: RichStreamRenderer,
        timeout_seconds: float,
        agent_name: str | None,
        meta: dict[str, Any],
    ) -> tuple[str, dict[str, Any], float | None, float | None]:
        """Process streaming events and accumulate response."""
        final_text = ""
        stats_usage: dict[str, Any] = {}
        started_monotonic: float | None = None

        self._capture_request_id(stream_response, meta, renderer)

        controller = getattr(renderer, "transcript_controller", None)
        if controller and getattr(controller, "enabled", False):
            controller.on_stream_start(renderer)

        try:
            for event in iter_sse_events(stream_response, timeout_seconds, agent_name):
                if started_monotonic is None:
                    started_monotonic = self._maybe_start_timer(event)

                final_text, stats_usage = self._process_single_event(
                    event,
                    renderer,
                    final_text,
                    stats_usage,
                    meta,
                )

                if controller and getattr(controller, "enabled", False):
                    controller.poll(renderer)
        finally:
            if controller and getattr(controller, "enabled", False):
                controller.on_stream_complete()

        finished_monotonic = monotonic()
        return final_text, stats_usage, started_monotonic, finished_monotonic

    def _capture_request_id(
        self,
        stream_response: httpx.Response,
        meta: dict[str, Any],
        renderer: RichStreamRenderer,
    ) -> None:
        req_id = stream_response.headers.get("x-request-id") or stream_response.headers.get("x-run-id")
        if req_id:
            meta["run_id"] = req_id
            renderer.on_start(meta)

    def _maybe_start_timer(self, event: dict[str, Any]) -> float | None:
        try:
            ev = json.loads(event["data"])
        except json.JSONDecodeError:
            return None

        if "content" in ev or "status" in ev or ev.get("metadata"):
            return monotonic()
        return None

    def _process_single_event(
        self,
        event: dict[str, Any],
        renderer: RichStreamRenderer,
        final_text: str,
        stats_usage: dict[str, Any],
        meta: dict[str, Any],
    ) -> tuple[str, dict[str, Any]]:
        try:
            ev = json.loads(event["data"])
        except json.JSONDecodeError:
            self._logger.debug("Non-JSON SSE fragment skipped")
            return final_text, stats_usage

        kind = (ev.get("metadata") or {}).get("kind")
        renderer.on_event(ev)

        handled = self._handle_metadata_kind(
            kind,
            ev,
            final_text,
            stats_usage,
            meta,
            renderer,
        )
        if handled is not None:
            return handled

        if ev.get("content"):
            final_text = self._handle_content_event(ev, final_text)

        return final_text, stats_usage

    def _handle_metadata_kind(
        self,
        kind: str | None,
        ev: dict[str, Any],
        final_text: str,
        stats_usage: dict[str, Any],
        meta: dict[str, Any],
        renderer: RichStreamRenderer,
    ) -> tuple[str, dict[str, Any]] | None:
        """Process well-known metadata kinds and return updated state."""
        if kind == "artifact":
            return final_text, stats_usage

        if kind == "final_response":
            content = ev.get("content")
            if content:
                return content, stats_usage
            return final_text, stats_usage

        if kind == "usage":
            stats_usage.update(ev.get("usage") or {})
            return final_text, stats_usage

        if kind == "run_info":
            self._handle_run_info_event(ev, meta, renderer)
            return final_text, stats_usage

        return None

    def _handle_content_event(self, ev: dict[str, Any], final_text: str) -> str:
        content = ev.get("content", "")
        if not content.startswith("Artifact received:"):
            return content
        return final_text

    def _handle_run_info_event(
        self,
        ev: dict[str, Any],
        meta: dict[str, Any],
        renderer: RichStreamRenderer,
    ) -> None:
        if ev.get("model"):
            meta["model"] = ev["model"]
            renderer.on_start(meta)
        if ev.get("run_id"):
            meta["run_id"] = ev["run_id"]
            renderer.on_start(meta)

    def _ensure_renderer_final_content(self, renderer: RichStreamRenderer, text: str) -> None:
        """Populate renderer state with final output when the stream omits it."""
        if not text:
            return

        text_value = _coerce_to_string(text)
        _update_renderer_transcript(renderer, text_value)

    # --------------------------------------------------------------------- #
    # Finalisation helpers
    # --------------------------------------------------------------------- #
    def finalize_renderer(
        self,
        renderer: RichStreamRenderer,
        final_text: str,
        stats_usage: dict[str, Any],
        started_monotonic: float | None,
        finished_monotonic: float | None,
    ) -> str:
        """Complete rendering and return the textual result."""
        st = RunStats()
        st.started_at = started_monotonic or st.started_at
        st.finished_at = finished_monotonic or st.started_at
        st.usage = stats_usage

        rendered_text = ""
        buffer_values: Any | None = None

        if hasattr(renderer, "state") and hasattr(renderer.state, "buffer"):
            buffer_values = renderer.state.buffer
        elif hasattr(renderer, "buffer"):
            buffer_values = renderer.buffer

        if buffer_values is not None:
            try:
                rendered_text = "".join(buffer_values)
            except TypeError:
                rendered_text = ""

        fallback_text = final_text or rendered_text
        if fallback_text:
            self._ensure_renderer_final_content(renderer, fallback_text)

        renderer.on_complete(st)
        return final_text or rendered_text or "No response content received."


def compute_timeout_seconds(kwargs: dict[str, Any]) -> float:
    """Determine the execution timeout for agent runs.

    Args:
        kwargs: Dictionary containing execution parameters, including timeout.

    Returns:
        The timeout value in seconds, defaulting to DEFAULT_AGENT_RUN_TIMEOUT
        if not specified in kwargs.
    """
    return kwargs.get("timeout", DEFAULT_AGENT_RUN_TIMEOUT)
