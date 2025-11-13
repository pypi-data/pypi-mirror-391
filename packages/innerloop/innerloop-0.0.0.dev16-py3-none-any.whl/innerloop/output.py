"""Utilities for assembling final output text from streamed events.

Provides a single implementation used by both function-first and class-based
paths to avoid drift.
"""

from __future__ import annotations

from typing import Any


def _append_safely(current: str, new: str) -> str:
    """Append text for delta or snapshot styles with minimal logic.

    Rules:
    - If ``current`` is empty → return ``new``
    - If ``new`` starts with ``current`` → snapshot → replace with ``new``
    - Otherwise → treat as delta and concatenate
    """
    if not current:
        return new
    if new.startswith(current):
        return new
    return current + new


def assemble_output(
    events: list[Any],
    *,
    reset_on_tool: bool = True,
    fallback_to_tool: bool = True,
) -> str:
    """Assemble final output text from event stream.

    Behavior:
      - Accumulates TextEvent.part.text via _append_safely
      - If reset_on_tool=True: resets on each ToolUseEvent
      - If fallback_to_tool=True: returns last tool output when no text exists
    """
    from .events import TextEvent as _TextEvent
    from .events import ToolUseEvent as _ToolUseEvent

    assembled_text = ""
    last_tool_output = ""

    for ev in events:
        if isinstance(ev, _ToolUseEvent):
            if reset_on_tool:
                assembled_text = ""
            last_tool_output = ev.part.state.output or last_tool_output
        elif isinstance(ev, _TextEvent):
            chunk = ev.part.text or ""
            assembled_text = _append_safely(assembled_text, chunk)

    if fallback_to_tool and not assembled_text and last_tool_output:
        return last_tool_output
    return assembled_text


__all__ = ["assemble_output"]
