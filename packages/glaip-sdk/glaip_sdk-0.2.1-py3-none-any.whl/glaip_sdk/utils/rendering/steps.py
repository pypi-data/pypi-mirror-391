"""Rendering utilities.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from copy import deepcopy
from time import monotonic
from typing import Any

from glaip_sdk.icons import ICON_AGENT_STEP, ICON_DELEGATE, ICON_TOOL_STEP
from glaip_sdk.utils.rendering.models import Step
from glaip_sdk.utils.rendering.step_tree_state import StepTreeState

logger = logging.getLogger(__name__)
UNKNOWN_STEP_DETAIL = "Unknown step detail"


class StepManager:
    """Manages the lifecycle and organization of execution steps.

    Tracks step creation, parent-child relationships, and execution state
    with automatic pruning of old steps when limits are reached.
    """

    def __init__(self, max_steps: int = 200) -> None:
        """Initialize the step manager.

        Args:
            max_steps: Maximum number of steps to retain before pruning
        """
        normalised_max = int(max_steps) if isinstance(max_steps, (int, float)) else 0
        self.state = StepTreeState(max_steps=normalised_max)
        self.by_id: dict[str, Step] = self.state.step_index
        self.key_index: dict[tuple, str] = {}
        self.slot_counter: dict[tuple, int] = {}
        self.max_steps = normalised_max
        self._last_running: dict[tuple, str] = {}
        self._step_aliases: dict[str, str] = {}
        self.root_agent_id: str | None = None
        self._scope_anchors: dict[str, list[str]] = {}
        self._step_scope_map: dict[str, str] = {}

    def set_root_agent(self, agent_id: str | None) -> None:
        """Record the root agent identifier for scope-aware parenting."""
        if isinstance(agent_id, str) and agent_id.strip():
            self.root_agent_id = agent_id.strip()

    def _alloc_slot(
        self,
        task_id: str | None,
        context_id: str | None,
        kind: str,
        name: str,
    ) -> int:
        k = (task_id, context_id, kind, name)
        self.slot_counter[k] = self.slot_counter.get(k, 0) + 1
        return self.slot_counter[k]

    def _key(
        self,
        task_id: str | None,
        context_id: str | None,
        kind: str,
        name: str,
        slot: int,
    ) -> tuple[str | None, str | None, str, str, int]:
        return (task_id, context_id, kind, name, slot)

    def _make_id(
        self,
        task_id: str | None,
        context_id: str | None,
        kind: str,
        name: str,
        slot: int,
    ) -> str:
        return f"{task_id or 't'}::{context_id or 'c'}::{kind}::{name}::{slot}"

    def start_or_get(
        self,
        *,
        task_id: str | None,
        context_id: str | None,
        kind: str,
        name: str,
        parent_id: str | None = None,
        args: dict[str, object] | None = None,
    ) -> Step:
        """Start a new step or return existing running step with same parameters.

        Args:
            task_id: Task identifier
            context_id: Context identifier
            kind: Step kind (tool, delegate, agent)
            name: Step name
            parent_id: Parent step ID if this is a child step
            args: Step arguments

        Returns:
            The Step instance (new or existing)
        """
        existing = self.find_running(task_id=task_id, context_id=context_id, kind=kind, name=name)
        if existing:
            if args and existing.args != args:
                existing.args = args
            return existing
        slot = self._alloc_slot(task_id, context_id, kind, name)
        key = self._key(task_id, context_id, kind, name, slot)
        step_id = self._make_id(task_id, context_id, kind, name, slot)
        st = Step(
            step_id=step_id,
            kind=kind,
            name=name,
            parent_id=parent_id,
            task_id=task_id,
            context_id=context_id,
            args=args or {},
        )
        self.by_id[step_id] = st
        if parent_id:
            self.children.setdefault(parent_id, []).append(step_id)
        else:
            self.order.append(step_id)
        self.key_index[key] = step_id
        self.state.retained_ids.add(step_id)
        self._prune_steps()
        self._last_running[(task_id, context_id, kind, name)] = step_id
        return st

    def _calculate_total_steps(self) -> int:
        """Calculate total number of steps."""
        return len(self.order) + sum(len(v) for v in self.children.values())

    def _get_subtree_size(self, root_id: str) -> int:
        """Get the size of a subtree (including root)."""
        subtree = [root_id]
        stack = list(self.children.get(root_id, []))
        while stack:
            x = stack.pop()
            subtree.append(x)
            stack.extend(self.children.get(x, []))
        return len(subtree)

    def _remove_subtree(self, root_id: str) -> None:
        """Remove a complete subtree from all data structures."""
        for step_id in self._collect_subtree_ids(root_id):
            self._purge_step_references(step_id)

    def _collect_subtree_ids(self, root_id: str) -> list[str]:
        """Return a flat list of step ids contained within a subtree."""
        stack = [root_id]
        collected: list[str] = []
        while stack:
            sid = stack.pop()
            collected.append(sid)
            stack.extend(self.children.pop(sid, []))
        return collected

    def _purge_step_references(self, step_id: str) -> None:
        """Remove a single step id from all indexes and helper structures."""
        st = self.by_id.pop(step_id, None)
        if st:
            key = (st.task_id, st.context_id, st.kind, st.name)
            self._last_running.pop(key, None)
            self.state.retained_ids.discard(step_id)
            self.state.discard_running(step_id)
        self._remove_parent_links(step_id)
        if step_id in self.order:
            self.order.remove(step_id)
        self.state.buffered_children.pop(step_id, None)
        self.state.pending_branch_failures.discard(step_id)

    def _remove_parent_links(self, child_id: str) -> None:
        """Detach a child id from any parent lists."""
        for parent, kids in self.children.copy().items():
            if child_id not in kids:
                continue
            kids.remove(child_id)
            if not kids:
                self.children.pop(parent, None)

    def _should_prune_steps(self, total: int) -> bool:
        """Check if steps should be pruned."""
        if self.max_steps <= 0:
            return False
        return total > self.max_steps

    def _get_oldest_step_id(self) -> str | None:
        """Get the oldest step ID for pruning."""
        return self.order[0] if self.order else None

    def _prune_steps(self) -> None:
        """Prune steps when total exceeds maximum."""
        total = self._calculate_total_steps()
        if not self._should_prune_steps(total):
            return

        while self._should_prune_steps(total) and self.order:
            sid = self._get_oldest_step_id()
            if not sid:
                break

            subtree_size = self._get_subtree_size(sid)
            self._remove_subtree(sid)
            total -= subtree_size

    def remove_step(self, step_id: str) -> None:
        """Remove a single step from the tree and cached indexes."""
        step = self.by_id.pop(step_id, None)
        if not step:
            return

        if step.parent_id:
            self.state.unlink_child(step.parent_id, step_id)
        else:
            self.state.unlink_root(step_id)

        self.children.pop(step_id, None)
        self.state.buffered_children.pop(step_id, None)
        self.state.retained_ids.discard(step_id)
        self.state.pending_branch_failures.discard(step_id)
        self.state.discard_running(step_id)

        self.key_index = {key: sid for key, sid in self.key_index.items() if sid != step_id}
        for key, last_sid in self._last_running.copy().items():
            if last_sid == step_id:
                self._last_running.pop(key, None)

        aliases = [alias for alias, target in self._step_aliases.items() if alias == step_id or target == step_id]
        for alias in aliases:
            self._step_aliases.pop(alias, None)

    def get_child_count(self, step_id: str) -> int:
        """Get the number of child steps for a given step.

        Args:
            step_id: The parent step ID

        Returns:
            Number of child steps
        """
        return len(self.children.get(step_id, []))

    def find_running(
        self,
        *,
        task_id: str | None,
        context_id: str | None,
        kind: str,
        name: str,
    ) -> Step | None:
        """Find a currently running step with the given parameters.

        Args:
            task_id: Task identifier
            context_id: Context identifier
            kind: Step kind (tool, delegate, agent)
            name: Step name

        Returns:
            The running Step if found, None otherwise
        """
        key = (task_id, context_id, kind, name)
        step_id = self._last_running.get(key)
        if step_id:
            st = self.by_id.get(step_id)
            if st and st.status != "finished":
                return st
        for sid in reversed(list(self._iter_all_steps())):
            st = self.by_id.get(sid)
            if (
                st
                and (st.task_id, st.context_id, st.kind, st.name)
                == (
                    task_id,
                    context_id,
                    kind,
                    name,
                )
                and st.status != "finished"
            ):
                return st
        return None

    def finish(
        self,
        *,
        task_id: str | None,
        context_id: str | None,
        kind: str,
        name: str,
        output: object | None = None,
        duration_raw: float | None = None,
    ) -> Step:
        """Finish a step with the given parameters.

        Args:
            task_id: Task identifier
            context_id: Context identifier
            kind: Step kind (tool, delegate, agent)
            name: Step name
            output: Step output data
            duration_raw: Raw duration in seconds

        Returns:
            The finished Step instance

        Raises:
            RuntimeError: If no matching step is found
        """
        st = self.find_running(task_id=task_id, context_id=context_id, kind=kind, name=name)
        if not st:
            # Try to find any existing step with matching parameters, even if not running
            for sid in reversed(list(self._iter_all_steps())):
                st_check = self.by_id.get(sid)
                if (
                    st_check
                    and st_check.task_id == task_id
                    and st_check.context_id == context_id
                    and st_check.kind == kind
                    and st_check.name == name
                ):
                    st = st_check
                    break

            # If still no step found, create a new one
            if not st:
                st = self.start_or_get(task_id=task_id, context_id=context_id, kind=kind, name=name)

        if output:
            st.output = output
        st.finish(duration_raw)
        key = (task_id, context_id, kind, name)
        if self._last_running.get(key) == st.step_id:
            self._last_running.pop(key, None)
        return st

    def _iter_all_steps(self) -> Iterator[str]:
        for root in self.order:
            yield root
            stack = list(self.children.get(root, []))
            while stack:
                sid = stack.pop()
                yield sid
                stack.extend(self.children.get(sid, []))

    def iter_tree(self) -> Iterator[tuple[str, tuple[bool, ...]]]:
        """Expose depth-first traversal info for rendering."""
        yield from self.state.iter_visible_tree()

    @property
    def order(self) -> list[str]:
        """Root step ordering accessor backed by StepTreeState."""
        return self.state.root_order

    @order.setter
    def order(self, value: list[str]) -> None:
        self.state.root_order = list(value)

    @property
    def children(self) -> dict[str, list[str]]:
        """Child mapping accessor backed by StepTreeState."""
        return self.state.child_map

    @children.setter
    def children(self, value: dict[str, list[str]]) -> None:
        self.state.child_map = value

    # ------------------------------------------------------------------
    # SSE-aware helpers
    # ------------------------------------------------------------------

    def apply_event(self, event: dict[str, Any]) -> Step:
        """Apply an SSE step event and return the updated step."""
        cloned_events = self._split_multi_tool_event(event)
        if cloned_events:
            last_step: Step | None = None
            for cloned in cloned_events:
                last_step = self._apply_single_event(cloned)
            if last_step:
                return last_step
        return self._apply_single_event(event)

    def _split_multi_tool_event(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        """Split events that describe multiple tool calls into per-call clones."""
        metadata = event.get("metadata") or {}
        tool_info = metadata.get("tool_info") or {}
        tool_calls = tool_info.get("tool_calls")
        if not self._should_split_tool_calls(tool_calls):
            return []
        if self._all_delegate_calls(tool_calls):
            return []

        base_step_id = metadata.get("step_id") or "step"
        clones: list[dict[str, Any]] = []
        for index, call in enumerate(tool_calls):
            clone = self._clone_tool_call(event, tool_info, call, base_step_id, index)
            if clone is not None:
                clones.append(clone)
        return clones

    @staticmethod
    def _should_split_tool_calls(tool_calls: Any) -> bool:
        """Return True when an event references more than one tool call."""
        return isinstance(tool_calls, list) and len(tool_calls) > 1

    def _all_delegate_calls(self, tool_calls: Any) -> bool:
        """Return True when an event batch only contains delegate tools."""
        if not isinstance(tool_calls, list) or not tool_calls:
            return False
        for call in tool_calls:
            if not isinstance(call, dict):
                return False
            name = (call.get("name") or "").lower()
            if not self._is_delegate_tool(name):
                return False
        return True

    def _clone_tool_call(
        self,
        event: dict[str, Any],
        tool_info: dict[str, Any],
        call: Any,
        base_step_id: str,
        index: int,
    ) -> dict[str, Any] | None:
        """Create a per-call clone of a multi-tool event."""
        if not isinstance(call, dict):
            return None

        cloned = deepcopy(event)
        cloned_meta = cloned.setdefault("metadata", {})
        cloned_tool_info = dict(tool_info)
        cloned_tool_info["tool_calls"] = [dict(call)]
        self._copy_tool_call_field(call, cloned_tool_info, "name")
        self._copy_tool_call_field(call, cloned_tool_info, "args")
        self._copy_tool_call_field(call, cloned_tool_info, "id")
        cloned_meta["tool_info"] = cloned_tool_info
        cloned_meta["step_id"] = self._derive_call_step_id(call, base_step_id, index)
        return cloned

    @staticmethod
    def _copy_tool_call_field(call: dict[str, Any], target: dict[str, Any], field: str) -> None:
        """Copy a field from the tool call when it exists."""
        value = call.get(field)
        if value:
            target[field] = value

    @staticmethod
    def _derive_call_step_id(call: dict[str, Any], base_step_id: str, index: int) -> str:
        """Determine the per-call step identifier."""
        call_id = call.get("id")
        if isinstance(call_id, str):
            stripped = call_id.strip()
            if stripped:
                return stripped
        return f"{base_step_id}#{index}"

    def _apply_single_event(self, event: dict[str, Any]) -> Step:
        metadata, step_id, tool_info, args = self._parse_event_payload(event)
        tool_name = self._resolve_tool_name(tool_info, metadata, step_id)
        kind = self._derive_step_kind(tool_name, metadata)
        parent_hint = self._coerce_parent_id(metadata.get("previous_step_ids"))

        step = self._get_or_create_step(
            step_id=step_id,
            kind=kind,
            tool_name=tool_name,
            event=event,
            metadata=metadata,
            args=args,
        )
        parent_id = self._determine_parent_id(step, metadata, parent_hint)
        self._link_step(step, parent_id)

        self.state.retained_ids.add(step.step_id)
        step.display_label = self._compose_display_label(step.kind, tool_name, args, metadata)
        self._flush_buffered_children(step.step_id)
        self._apply_pending_branch_flags(step.step_id)

        status = self._normalise_status(metadata.get("status"), event.get("status"), event.get("task_state"))
        status = self._apply_failure_state(step, status, event)

        server_time = self._coerce_server_time(metadata.get("time"))
        self._update_server_timestamps(step, server_time, status)

        self._apply_duration(
            step=step,
            status=status,
            tool_info=tool_info,
            args=args,
            server_time=server_time,
        )

        self._update_scope_bindings(
            step=step,
            metadata=metadata,
            tool_name=tool_name,
            status=status,
        )

        step.status_icon = self._status_icon_for_step(step)
        self._update_parallel_tracking(step)
        self._update_running_index(step)
        self._prune_steps()
        return step

    def _parse_event_payload(self, event: dict[str, Any]) -> tuple[dict[str, Any], str, dict[str, Any], dict[str, Any]]:
        metadata = event.get("metadata") or {}
        if not isinstance(metadata, dict):
            raise ValueError("Step event missing metadata payload")

        step_id = metadata.get("step_id")
        if not isinstance(step_id, str) or not step_id:
            raise ValueError("Step event missing step_id")

        tool_info = metadata.get("tool_info") or {}
        if not isinstance(tool_info, dict):
            tool_info = {}

        canonical_step_id = self._canonicalize_step_id(step_id, tool_info)
        metadata["step_id"] = canonical_step_id
        step_id = canonical_step_id

        args = self._resolve_tool_args(tool_info)

        return metadata, step_id, tool_info, args

    def _resolve_tool_name(self, tool_info: dict[str, Any], metadata: dict[str, Any], step_id: str) -> str:
        name = tool_info.get("name")
        if not name:
            call = self._first_tool_call(tool_info)
            if call:
                name = call.get("name")
        if isinstance(name, str) and name.strip():
            return name
        if name is not None:
            return str(name)

        agent_name = metadata.get("agent_name")
        if isinstance(agent_name, str) and agent_name.strip():
            return agent_name
        return step_id

    def _resolve_tool_args(self, tool_info: dict[str, Any]) -> dict[str, Any]:
        args = tool_info.get("args")
        if isinstance(args, dict):
            return args
        call = self._first_tool_call(tool_info)
        if call:
            call_args = call.get("args")
            if isinstance(call_args, dict):
                return call_args
        return {}

    def _first_tool_call(self, tool_info: dict[str, Any]) -> dict[str, Any] | None:
        tool_calls = tool_info.get("tool_calls")
        if isinstance(tool_calls, list) and tool_calls:
            candidate = tool_calls[0]
            if isinstance(candidate, dict):
                return candidate
        return None

    def _get_or_create_step(
        self,
        step_id: str,
        kind: str,
        tool_name: str,
        event: dict[str, Any],
        metadata: dict[str, Any],
        args: dict[str, Any],
    ) -> Step:
        existing = self.by_id.get(step_id)
        if existing:
            return self._update_existing_step(existing, kind, tool_name, event, metadata, args)
        return self._create_step_from_event(step_id, kind, tool_name, event, metadata, args)

    def _create_step_from_event(
        self,
        step_id: str,
        kind: str,
        tool_name: str,
        event: dict[str, Any],
        metadata: dict[str, Any],
        args: dict[str, Any],
    ) -> Step:
        step = Step(
            step_id=step_id,
            kind=kind,
            name=tool_name or step_id,
            task_id=self._coalesce_metadata_value("task_id", event, metadata, fallback=None),
            context_id=self._coalesce_metadata_value("context_id", event, metadata, fallback=None),
            args=args or {},
        )
        self.by_id[step_id] = step
        self.state.retained_ids.add(step_id)
        return step

    def _update_existing_step(
        self,
        step: Step,
        kind: str,
        tool_name: str,
        event: dict[str, Any],
        metadata: dict[str, Any],
        args: dict[str, Any],
    ) -> Step:
        step.kind = step.kind or kind
        step.name = tool_name or step.name
        if args:
            step.args = args
        step.task_id = self._coalesce_metadata_value("task_id", event, metadata, fallback=step.task_id)
        step.context_id = self._coalesce_metadata_value("context_id", event, metadata, fallback=step.context_id)
        return step

    def _apply_failure_state(self, step: Step, status: str, event: dict[str, Any]) -> str:
        failure_reason = self._extract_failure_reason(status, event.get("task_state"), event.get("content"))
        if not failure_reason:
            step.status = status
            return status

        step.failure_reason = failure_reason
        if status not in {"failed", "stopped"}:
            status = "failed"
        self._set_branch_warning(step.parent_id)
        step.status = status
        return status

    def _apply_duration(
        self,
        step: Step,
        status: str,
        tool_info: dict[str, Any],
        args: dict[str, Any],
        server_time: float | None,
    ) -> None:
        duration_ms, duration_source = self._resolve_duration_from_event(tool_info, args)
        if duration_ms is not None:
            step.duration_ms = duration_ms
            step.duration_source = duration_source
            return

        if status in {"finished", "failed", "stopped"} and step.duration_ms is None:
            timeline_ms = self._calculate_server_duration(step, server_time)
            if timeline_ms is not None:
                step.duration_ms = timeline_ms
                step.duration_source = "timeline"
                return
            try:
                step.duration_ms = int((monotonic() - step.started_at) * 1000)
            except Exception:
                step.duration_ms = 0
            step.duration_source = step.duration_source or "monotonic"

    def _update_running_index(self, step: Step) -> None:
        key = (step.task_id, step.context_id, step.kind, step.name)
        if step.status == "finished":
            if self._last_running.get(key) == step.step_id:
                self._last_running.pop(key, None)
        else:
            self._last_running[key] = step.step_id

    def _coalesce_metadata_value(
        self,
        key: str,
        event: dict[str, Any],
        metadata: dict[str, Any],
        *,
        fallback: Any = None,
    ) -> Any:
        if event.get(key) is not None:
            return event[key]
        if metadata.get(key) is not None:
            return metadata[key]
        return fallback

    def _coerce_parent_id(self, parent_value: Any) -> str | None:
        if isinstance(parent_value, list):
            for candidate in parent_value:
                if isinstance(candidate, str) and candidate.strip():
                    return self._canonical_parent_id(candidate)
        elif isinstance(parent_value, str) and parent_value.strip():
            return self._canonical_parent_id(parent_value)
        return None

    def _canonical_parent_id(self, value: str) -> str:
        return self._step_aliases.get(value, value)

    def _derive_step_kind(self, tool_name: str | None, metadata: dict[str, Any]) -> str:
        metadata_kind = metadata.get("kind")
        kind = self._clean_kind(metadata_kind)
        tool = (tool_name or "").lower()

        if self._is_thinking_step(kind, tool):
            return "thinking"
        if self._is_delegate_tool(tool):
            return "delegate"
        if kind == "agent_thinking_step" and tool:
            return "tool"
        if self._is_top_level_agent(tool_name, metadata, kind):
            return "agent"
        if kind == "agent_step" and tool.startswith("delegate"):
            return "delegate"
        if tool.startswith("agent_"):
            return "agent"
        if kind == "agent_step":
            return "tool" if tool else "agent_step"
        return kind or "tool"

    def _clean_kind(self, metadata_kind: Any) -> str:
        return metadata_kind.lower() if isinstance(metadata_kind, str) else ""

    def _is_thinking_step(self, kind: str, tool: str) -> bool:
        if tool.startswith("agent_thinking"):
            return True
        return kind == "agent_thinking_step" and not tool

    def _is_delegate_tool(self, tool: str) -> bool:
        return tool.startswith(("delegate_to_", "delegate-", "delegate ", "delegate_"))

    def _is_top_level_agent(self, tool_name: str | None, metadata: dict[str, Any], kind: str) -> bool:
        if kind != "agent_step":
            return False
        agent_name = metadata.get("agent_name")
        if isinstance(agent_name, str) and agent_name and tool_name == agent_name:
            return True
        return self._looks_like_uuid(tool_name or "")

    @staticmethod
    def _looks_like_uuid(value: str) -> bool:
        stripped = value.replace("-", "")
        if len(stripped) not in {32, 36}:
            return False
        return all(ch in "0123456789abcdefABCDEF" for ch in stripped)

    def _step_icon_for_kind(self, step_kind: str) -> str:
        if step_kind == "agent":
            return ICON_AGENT_STEP
        if step_kind == "delegate":
            return ICON_DELEGATE
        if step_kind == "thinking":
            return "💭"
        return ICON_TOOL_STEP

    def _humanize_tool_name(self, raw_name: str | None) -> str:
        if not raw_name:
            return UNKNOWN_STEP_DETAIL
        name = raw_name
        if name.startswith("delegate_to_"):
            name = name.removeprefix("delegate_to_")
        elif name.startswith("delegate_"):
            name = name.removeprefix("delegate_")
        cleaned = name.replace("_", " ").replace("-", " ").strip()
        if not cleaned:
            return UNKNOWN_STEP_DETAIL
        return cleaned[:1].upper() + cleaned[1:]

    def _compose_display_label(
        self,
        step_kind: str,
        tool_name: str | None,
        args: dict[str, Any],
        metadata: dict[str, Any],
    ) -> str:
        icon = self._step_icon_for_kind(step_kind)
        body = self._resolve_label_body(step_kind, tool_name, metadata)
        label = f"{icon} {body}".strip()
        if isinstance(args, dict) and args:
            label = f"{label} —"
        return label or UNKNOWN_STEP_DETAIL

    def _resolve_label_body(
        self,
        step_kind: str,
        tool_name: str | None,
        metadata: dict[str, Any],
    ) -> str:
        if step_kind == "thinking":
            thinking_text = metadata.get("thinking_and_activity_info")
            if isinstance(thinking_text, str) and thinking_text.strip():
                return thinking_text.strip()
            return "Thinking…"

        if step_kind == "delegate":
            return self._humanize_tool_name(tool_name)

        if step_kind == "agent":
            agent_name = metadata.get("agent_name")
            if isinstance(agent_name, str) and agent_name.strip():
                return agent_name.strip()

        friendly = self._humanize_tool_name(tool_name)
        return friendly

    def _normalise_status(
        self,
        metadata_status: Any,
        event_status: Any,
        task_state: Any,
    ) -> str:
        for candidate in (metadata_status, event_status, task_state):
            status = (candidate or "").lower() if isinstance(candidate, str) else ""
            if status in {"running", "started", "pending", "working"}:
                return "running"
            if status in {"finished", "success", "succeeded", "completed"}:
                return "finished"
            if status in {"failed", "error"}:
                return "failed"
            if status in {"stopped", "cancelled", "canceled"}:
                return "stopped"
        return "running"

    def _extract_failure_reason(
        self,
        status: str,
        task_state: Any,
        content: Any,
    ) -> str | None:
        failure_states = {"failed", "stopped", "error"}
        task_state_str = (task_state or "").lower() if isinstance(task_state, str) else ""
        if status in failure_states or task_state_str in failure_states:
            if isinstance(content, str) and content.strip():
                return content.strip()
            if task_state_str:
                return task_state_str
        return None

    def _resolve_duration_from_event(
        self,
        tool_info: dict[str, Any],
        args: dict[str, Any],
    ) -> tuple[int | None, str | None]:
        exec_time = tool_info.get("execution_time")
        if isinstance(exec_time, (int, float)):
            return max(0, int(round(float(exec_time) * 1000))), "metadata"

        duration_seconds = tool_info.get("duration_seconds")
        if isinstance(duration_seconds, (int, float)):
            return max(0, int(round(float(duration_seconds) * 1000))), "metadata"

        wait_seconds = args.get("wait_seconds")
        if isinstance(wait_seconds, (int, float)):
            return max(0, int(round(float(wait_seconds) * 1000))), "argument"

        return None, None

    def _determine_parent_id(self, step: Step, metadata: dict[str, Any], parent_hint: str | None) -> str | None:
        scope_parent = self._lookup_scope_parent(metadata, step)
        candidate = scope_parent or parent_hint
        if candidate == step.step_id:
            logger.debug("Step %s cannot parent itself; dropping parent hint", candidate)
            return None
        return candidate

    def _lookup_scope_parent(self, metadata: dict[str, Any], step: Step) -> str | None:
        agent_name = metadata.get("agent_name")
        if not isinstance(agent_name, str) or not agent_name.strip():
            return None
        stack = self._scope_anchors.get(agent_name.strip())
        if not stack:
            return None
        anchor_id = stack[-1]
        if anchor_id == step.step_id:
            return None
        return anchor_id

    def _link_step(self, step: Step, parent_id: str | None) -> None:
        """Attach a step to the resolved parent, buffering when necessary."""
        parent_id = self._sanitize_parent_reference(step, parent_id)
        if self._ensure_existing_link(step, parent_id):
            return

        self._detach_from_current_parent(step)
        self._attach_to_parent(step, parent_id)

    def _sanitize_parent_reference(self, step: Step, parent_id: str | None) -> str | None:
        """Guard against self-referential parent assignments."""
        if parent_id != step.step_id:
            return parent_id

        logger.debug(
            "Ignoring self-referential parent_id %s for step %s",
            parent_id,
            step.step_id,
        )
        return step.parent_id

    def _ensure_existing_link(self, step: Step, parent_id: str | None) -> bool:
        """Keep existing parent/child wiring in sync when the parent is unchanged."""
        if parent_id != step.parent_id:
            return False

        if parent_id is None:
            if step.step_id not in self.state.root_order:
                self.state.link_root(step.step_id)
            return True

        if parent_id not in self.by_id:
            return False

        children = self.children.get(parent_id, [])
        if step.step_id not in children:
            self.state.link_child(parent_id, step.step_id)
        return True

    def _detach_from_current_parent(self, step: Step) -> None:
        """Remove the step from its current parent/root collection."""
        if step.parent_id:
            self.state.unlink_child(step.parent_id, step.step_id)
            return
        self.state.unlink_root(step.step_id)

    def _attach_to_parent(self, step: Step, parent_id: str | None) -> None:
        """Attach the step to the requested parent, buffering when needed."""
        if parent_id is None:
            step.parent_id = None
            self.state.link_root(step.step_id)
            return

        if parent_id not in self.by_id:
            self.state.buffer_child(parent_id, step.step_id)
            step.parent_id = None
            return

        step.parent_id = parent_id
        self.state.link_child(parent_id, step.step_id)
        self.state.unlink_root(step.step_id)

    def _update_scope_bindings(
        self,
        *,
        step: Step,
        metadata: dict[str, Any],
        tool_name: str,
        status: str,
    ) -> None:
        agent_name = metadata.get("agent_name")
        if step.kind == "agent" and isinstance(agent_name, str) and agent_name.strip():
            self._register_scope_anchor(agent_name.strip(), step.step_id)
            return

        if step.kind == "delegate":
            slug = self._derive_delegate_slug(tool_name)
            if not slug:
                return
            # Ensure the delegate anchor exists even if the first event we see is already finished
            if status == "running" or step.step_id not in self._step_scope_map:
                self._register_scope_anchor(slug, step.step_id)
            elif status in {"finished", "failed", "stopped"}:
                self._release_scope_anchor(step.step_id)
            return

        if status in {"finished", "failed", "stopped"}:
            self._release_scope_anchor(step.step_id)

    def _register_scope_anchor(self, scope_key: str, step_id: str) -> None:
        scope = scope_key.strip()
        stack = self._scope_anchors.setdefault(scope, [])
        if step_id not in stack:
            stack.append(step_id)
        self._step_scope_map[step_id] = scope

    def _release_scope_anchor(self, step_id: str) -> None:
        scope = self._step_scope_map.get(step_id)
        if not scope or scope == (self.root_agent_id or "").strip():
            return
        stack = self._scope_anchors.get(scope)
        if stack:
            if stack[-1] == step_id:
                stack.pop()
            elif step_id in stack:
                stack.remove(step_id)
            # Clean up if stack is now empty
            if len(stack) == 0:
                self._scope_anchors.pop(scope, None)
        self._step_scope_map.pop(step_id, None)

    @staticmethod
    def _derive_delegate_slug(tool_name: str | None) -> str | None:
        if not isinstance(tool_name, str):
            return None
        slug = tool_name.strip()
        if slug.startswith("delegate_to_"):
            slug = slug.removeprefix("delegate_to_")
        elif slug.startswith("delegate_"):
            slug = slug.removeprefix("delegate_")
        elif slug.startswith("delegate-"):
            slug = slug.removeprefix("delegate-")
        slug = slug.replace("-", "_").strip()
        return slug or None

    @staticmethod
    def _coerce_server_time(value: Any) -> float | None:
        """Convert a raw SSE time payload into a float if possible."""
        # Reuse the implementation from base renderer
        from glaip_sdk.utils.rendering.renderer.base import RichStreamRenderer

        return RichStreamRenderer._coerce_server_time(value)

    def _update_server_timestamps(self, step: Step, server_time: float | None, status: str) -> None:
        if server_time is None:
            return
        if status == "running" and step.server_started_at is None:
            step.server_started_at = server_time
        elif status in {"finished", "failed", "stopped"}:
            step.server_finished_at = server_time
            if step.server_started_at is None:
                step.server_started_at = server_time

    def _calculate_server_duration(self, step: Step, server_time: float | None) -> int | None:
        start = step.server_started_at
        end = server_time if server_time is not None else step.server_finished_at
        if start is None or end is None:
            return None
        try:
            return max(0, int(round((float(end) - float(start)) * 1000)))
        except Exception:
            return None

    def _flush_buffered_children(self, parent_id: str) -> None:
        for child_id in self.state.pop_buffered_children(parent_id):
            child = self.by_id.get(child_id)
            if not child:
                continue
            child.parent_id = parent_id
            self.state.link_child(parent_id, child_id)
            self.state.unlink_root(child_id)

    def _apply_pending_branch_flags(self, step_id: str) -> None:
        if step_id not in self.state.pending_branch_failures:
            return
        step = self.by_id.get(step_id)
        if step:
            step.branch_failed = True
            step.status_icon = "warning"
        self.state.pending_branch_failures.discard(step_id)

    def _set_branch_warning(self, parent_id: str | None) -> None:
        if not parent_id:
            return
        parent = self.by_id.get(parent_id)
        if parent:
            parent.branch_failed = True
            parent.status_icon = "warning"
        else:
            self.state.pending_branch_failures.add(parent_id)

    def _update_parallel_tracking(self, step: Step) -> None:
        if step.kind != "tool":
            step.is_parallel = False
            return

        key = (step.task_id, step.context_id)
        running = self.state.running_by_context.get(key)

        if step.status == "running":
            if running is None:
                running = set()
                self.state.running_by_context[key] = running
            running.add(step.step_id)
        elif running:
            running.discard(step.step_id)
            step.is_parallel = False

        if not running:
            self.state.running_by_context.pop(key, None)
            step.is_parallel = False
            return

        is_parallel = len(running) > 1
        for sid in running:
            current = self.by_id.get(sid)
            if current:
                current.is_parallel = is_parallel

    def _status_icon_for_step(self, step: Step) -> str:
        if step.status == "finished":
            return "warning" if step.branch_failed else "success"
        if step.status == "failed":
            return "failed"
        if step.status == "stopped":
            return "warning"
        return "spinner"

    def _canonicalize_step_id(self, step_id: str, tool_info: dict[str, Any]) -> str:
        alias = self._lookup_alias(step_id)
        if alias:
            return alias

        candidate_ids = self._collect_instance_ids(tool_info)
        alias = self._find_existing_candidate_alias(candidate_ids)
        if alias:
            self._step_aliases[step_id] = alias
            return alias

        return self._register_new_alias(step_id, candidate_ids)

    def _lookup_alias(self, step_id: str) -> str | None:
        alias = self._step_aliases.get(step_id)
        return alias if alias else None

    def _find_existing_candidate_alias(self, candidate_ids: list[str]) -> str | None:
        for candidate in candidate_ids:
            mapped = self._step_aliases.get(candidate)
            if mapped:
                return mapped
        return None

    def _register_new_alias(self, step_id: str, candidate_ids: list[str]) -> str:
        if candidate_ids:
            canonical = step_id if len(candidate_ids) > 1 else candidate_ids[0]
            self._step_aliases[step_id] = canonical
            for candidate in candidate_ids:
                self._step_aliases.setdefault(candidate, canonical)
            return canonical

        self._step_aliases.setdefault(step_id, step_id)
        return step_id

    def _collect_instance_ids(self, tool_info: dict[str, Any]) -> list[str]:
        """Collect all potential identifiers for a tool invocation."""
        candidates: list[str] = []
        identifier = self._normalise_identifier(tool_info.get("id"))
        if identifier:
            candidates.append(identifier)

        candidates.extend(self._extract_tool_call_ids(tool_info.get("tool_calls")))
        return self._deduplicate_candidates(candidates)

    def _extract_tool_call_ids(self, tool_calls: Any) -> list[str]:
        """Extract unique IDs from tool_calls payloads."""
        if not isinstance(tool_calls, list):
            return []
        collected: list[str] = []
        for call in tool_calls:
            if not isinstance(call, dict):
                continue
            identifier = self._normalise_identifier(call.get("id"))
            if identifier:
                collected.append(identifier)
        return collected

    @staticmethod
    def _normalise_identifier(value: Any) -> str | None:
        if isinstance(value, str):
            stripped = value.strip()
            return stripped or None
        return None

    @staticmethod
    def _deduplicate_candidates(candidates: list[str]) -> list[str]:
        seen: set[str] = set()
        ordered: list[str] = []
        for candidate in candidates:
            if candidate in seen:
                continue
            seen.add(candidate)
            ordered.append(candidate)
        return ordered
