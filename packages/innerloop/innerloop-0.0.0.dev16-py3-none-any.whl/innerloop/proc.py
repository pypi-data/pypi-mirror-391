"""Minimal subprocess JSONL streamer with robust hang protection.

Adds two safeguards to ensure we never hang in the caller:
- total_timeout: hard wall-clock cap for the entire process
- idle_timeout: kill if no stdout activity for N seconds

Also starts the process in its own group (when supported) and escalates
termination from SIGTERM to SIGKILL to ensure teardown.
"""

from __future__ import annotations

import asyncio
import json
import os
import signal
import time
from asyncio.subprocess import PIPE
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any

from .errors import CliNotFoundError, CliTimeoutError


async def stream_jsonl_process(
    cmd: list[str],
    *,
    env: dict[str, str] | None = None,
    cwd: str | None = None,
    stdin_data: str | None = None,
    total_timeout: float | None = None,
    idle_timeout: float | None = None,
) -> AsyncIterator[dict[str, Any]]:
    try:
        # Separate process group for clean termination on POSIX
        start_new_session = True
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=PIPE if stdin_data is not None else None,
            stdout=PIPE,
            stderr=PIPE,
            env=env,
            cwd=cwd,
            start_new_session=start_new_session,
        )
    except FileNotFoundError as e:
        raise CliNotFoundError("Command not found") from e

    # Write stdin if provided
    if stdin_data is not None and proc.stdin is not None:
        with suppress(Exception):
            proc.stdin.write(stdin_data.encode("utf-8"))
            await proc.stdin.drain()
            proc.stdin.close()
            await proc.stdin.wait_closed()

    async def _drain_stderr() -> None:
        if proc.stderr is None:
            return
        while True:
            chunk = await proc.stderr.readline()
            if not chunk:
                break
            # Intentionally discard; caller consumes JSON from stdout only
            # but draining prevents blocked writers.
            _ = chunk

    stderr_task = asyncio.create_task(_drain_stderr())

    assert proc.stdout is not None
    first_line = True
    start_time = time.monotonic()
    last_activity = start_time

    async def _readline_with_idle() -> bytes:
        if idle_timeout and idle_timeout > 0:
            return await asyncio.wait_for(proc.stdout.readline(), timeout=idle_timeout)
        return await proc.stdout.readline()

    try:
        while True:
            # Enforce total timeout
            if total_timeout and (time.monotonic() - start_time) > total_timeout:
                raise TimeoutError("total timeout exceeded")

            line = await _readline_with_idle()
            if not line:
                break

            last_activity = time.monotonic()
            text = line.decode(
                "utf-8-sig" if first_line else "utf-8", errors="ignore"
            ).strip()
            first_line = False
            if not text:
                continue
            with suppress(json.JSONDecodeError):
                yield json.loads(text)
    except asyncio.TimeoutError:
        # Idle timeout tripped; terminate and raise structured error
        try:
            if os.name != "nt":
                os.killpg(proc.pid, signal.SIGTERM)
            else:
                proc.terminate()
        except ProcessLookupError:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=1.0)
        except Exception:
            try:
                if os.name != "nt":
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
            except ProcessLookupError:
                pass
        raise CliTimeoutError("idle timeout exceeded while waiting for output", float(idle_timeout or 0.0))
    except TimeoutError:
        # Total timeout tripped; terminate and raise structured error
        try:
            if os.name != "nt":
                os.killpg(proc.pid, signal.SIGTERM)
            else:
                proc.terminate()
        except ProcessLookupError:
            pass
        try:
            await asyncio.wait_for(proc.wait(), timeout=1.0)
        except Exception:
            try:
                if os.name != "nt":
                    os.killpg(proc.pid, signal.SIGKILL)
                else:
                    proc.kill()
            except ProcessLookupError:
                pass
        raise CliTimeoutError("total timeout exceeded for process run", float(total_timeout or 0.0))

    # Wait for process to exit; ignore return code
    with suppress(Exception):
        await proc.wait()
    with suppress(Exception):
        await asyncio.wait_for(stderr_task, timeout=0.5)


__all__ = ["stream_jsonl_process"]
