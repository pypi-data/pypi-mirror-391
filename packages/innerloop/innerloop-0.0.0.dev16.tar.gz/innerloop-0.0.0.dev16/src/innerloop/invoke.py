from __future__ import annotations

import logging
import os
import tempfile
from collections.abc import AsyncIterator
from contextlib import suppress
from typing import Any, cast
import difflib

from .config import InvokeConfig
from .events import OpenCodeEvent, TimeInfo
from .events import parse_event as _parse_event
from .helper import unix_ms
from .mcp import LocalMcpServer, McpServer, RemoteMcpServer
from .output import assemble_output
from .permissions import Permission
from .providers import ProviderConfig
from .request import Request
from .response import Response
from .usage import compute_usage

logger = logging.getLogger(__name__)


def write_config_file(cfg: InvokeConfig) -> str:
    """Write config JSON to a temp file and return its path (0600 perms)."""
    data = cfg.to_json().encode("utf-8")
    tmp = tempfile.NamedTemporaryFile(
        prefix="opencode-config-", suffix=".json", delete=False
    )
    path = tmp.name
    try:
        with tmp:
            with suppress(Exception):
                os.chmod(path, 0o600)
            tmp.write(data)
            tmp.flush()
            with suppress(Exception):
                os.fsync(tmp.fileno())
        return path
    except Exception:
        with suppress(Exception):
            os.unlink(path)
        raise


def build_env_with_config_path(
    config_path: str, base: dict[str, str] | None = None
) -> dict[str, str]:
    """Return env dict with OPENCODE_CONFIG and a minimal, safe runtime.

    We aggressively disable optional subsystems so subprocess runs do not hang
    even if OpenCode has bugs or long‑running background services.
    """
    env = dict(base or os.environ)
    env["OPENCODE_CONFIG"] = config_path
    env.setdefault("OPENCODE_EXPERIMENTAL_MCP", "1")

    # Minimize OpenCode side‑effects and background activity
    env.setdefault("OPENCODE_EXPERIMENTAL_NO_BOOTSTRAP", "1")
    env.setdefault("OPENCODE_DISABLE_DEFAULT_PLUGINS", "1")
    env.setdefault("OPENCODE_DISABLE_LSP_DOWNLOAD", "1")
    env.setdefault("OPENCODE_DISABLE_AUTOCOMPACT", "1")
    env.setdefault("OPENCODE_DISABLE_PRUNE", "1")
    env.setdefault("OPENCODE_AUTO_SHARE", "0")
    # Ensure watcher is off unless explicitly enabled elsewhere
    env.setdefault("OPENCODE_EXPERIMENTAL_WATCHER", "0")

    return env


def build_opencode_cmd(model: str, session_id: str | None = None) -> list[str]:
    """Build opencode command without prompt (prompt passed via stdin)."""
    # --print-logs keeps logs on stderr instead of file writers that may
    # interfere with clean process exit in edge cases.
    cmd = [
        "opencode",
        "run",
        "--format",
        "json",
        "--print-logs",
        "--model",
        model,
    ]
    if session_id:
        cmd += ["--session", session_id]
    return cmd


async def run_opencode_jsonl(
    prompt: str,
    *,
    model: str,
    permission: Permission,
    providers: dict[str, ProviderConfig] | None = None,
    mcp_servers: list[McpServer] | dict[str, McpServer] | None = None,
    session_id: str | None = None,
    cwd: str | None = None,
    total_timeout: float | None = 120.0,
    idle_timeout: float | None = 20.0,
) -> AsyncIterator[dict[str, Any]]:
    """
    Pure functional runner: build config -> write file -> run -> JSONL stream.
    Yields parsed JSON objects from the CLI, one per line.
    Minimal guardrails here; callers can layer policies as needed.

    The prompt is passed via stdin to avoid argv length limits and issues
    with special characters like YAML frontmatter (---).
    """
    def _parse_model(s: str) -> tuple[str, str]:
        if "/" not in s:
            return s, ""
        p, m = s.split("/", 1)
        return p, m

    def _preflight_model(
        model_id: str, providers_map: dict[str, ProviderConfig] | None
    ) -> tuple[bool, str | None, list[str]]:
        if not providers_map:
            return True, None, []
        provider_id, model_only = _parse_model(model_id)
        prov = providers_map.get(provider_id)
        if not prov:
            # Unknown provider in provided config; let CLI decide (may be external env)
            return True, None, []
        # ProviderConfig allows extra fields; inspect dump for models map
        dump = prov.model_dump(by_alias=True, exclude_none=True)
        models = dump.get("models")
        if not isinstance(models, dict) or not models:
            # No opinionated model list provided → skip
            return True, None, []
        if model_only in models.keys():
            return True, None, []
        # simple suggestions using difflib
        keys = list(models.keys())
        close = difflib.get_close_matches(model_only, keys, n=5, cutoff=0.4)
        suggestions = [f"{provider_id}/{k}" for k in close]
        return (
            False,
            f"Model not found in provided config: {provider_id}/{model_only}",
            suggestions,
        )

    typed_mcp = cast(
        dict[str, LocalMcpServer | RemoteMcpServer] | None, mcp_servers
    )
    # Note: Request.providers (plural, user-facing) maps to InvokeConfig.provider
    # (singular) because the CLI schema uses a single top-level "provider" object.
    # Keep naming as-is to avoid API churn.
    cfg = InvokeConfig(
        permission=permission, provider=providers, mcp=typed_mcp
    )
    config_path = write_config_file(cfg)
    env = build_env_with_config_path(config_path)
    cmd = build_opencode_cmd(model, session_id=session_id)

    # Delegate to the generic process streamer
    from .proc import stream_jsonl_process as _stream

    ok, reason, suggestions = _preflight_model(model, providers)
    if not ok:
        from .errors import ModelNotFoundError
        logger.error("preflight failed: %s", reason)
        # Raise structured error; caller can catch and react.
        provider_id, model_only = _parse_model(model)
        raise ModelNotFoundError(
            provider_id=provider_id,
            model_id=model_only,
            suggestions=suggestions,
            source="preflight",
        )

    try:
        async for obj in _stream(
            cmd,
            env=env,
            cwd=cwd,
            stdin_data=prompt,
            total_timeout=(
                total_timeout
                if total_timeout is not None
                else float(os.getenv("IL_OPENCODE_TOTAL_TIMEOUT", "0") or 0) or None
            ),
            idle_timeout=(
                idle_timeout
                if idle_timeout is not None
                else float(os.getenv("IL_OPENCODE_IDLE_TIMEOUT", "0") or 0) or None
            ),
        ):
            yield obj
    finally:
        # Best‑effort cleanup of the temp config file in all code paths
        with suppress(Exception):
            os.unlink(config_path)


async def async_invoke(
    request: Request,
    *,
    resume: str | None = None,
    total_timeout: float | None = 120.0,
    idle_timeout: float | None = 30.0,
) -> Response[Any]:
    """Run a single CLI invocation and return a typed Response.

    - resume: optional session id to continue
    Structured parsing and retries live in `async_invoke_structured`/`Loop.run`
    and are not applied here.
    """
    # Always stream and assemble raw text here; structured parsing and retries
    # are handled by async_invoke_structured.
    effective_session = resume or request.session
    if effective_session == "":
        effective_session = None
    prompt = request.prompt

    # Auto-inject permission statement if permissions are non-default
    from .capabilities import _build_permission_statement

    perm_statement = _build_permission_statement(request.permission)
    if perm_statement:
        prompt = f"{prompt}\n\n{perm_statement}"

    # Stream events
    events: list[OpenCodeEvent] = []
    response_session: str | None = effective_session

    wall_start = unix_ms()
    async for raw in run_opencode_jsonl(
        prompt,
        model=request.model,
        permission=request.permission,
        providers=request.providers,
        mcp_servers=cast(
            dict[str, McpServer] | list[McpServer] | None, request.mcp
        ),
        session_id=effective_session,
        cwd=request.workdir,
        total_timeout=total_timeout,
        idle_timeout=idle_timeout,
    ):
        # Intercept CLI error events and raise structured exceptions when possible
        if raw.get("type") == "error":
            err = raw.get("error") or {}
            code = raw.get("code") or err.get("name") or ""
            if code == "ProviderModelNotFoundError":
                from .errors import ModelNotFoundError
                data = err.get("data") or {}
                prov = str(data.get("providerID") or "")
                mid = str(data.get("modelID") or "")
                # opencode may include suggestions in data in the future; honor if present
                suggestions = data.get("suggestions") or []
                raise ModelNotFoundError(
                    provider_id=prov,
                    model_id=mid,
                    suggestions=list(suggestions) if isinstance(suggestions, list) else [],
                    source="cli",
                )
        ev = _parse_event(raw)
        ev.seq = len(events) + 1
        events.append(ev)
        if response_session is None:
            response_session = getattr(ev, "sessionID", None) or None
    wall_end = unix_ms()

    # Build output
    text = assemble_output(events, reset_on_tool=True, fallback_to_tool=True)
    out: Any = text

    resp: Response[Any] = Response(
        session_id=response_session or "",
        input=request.prompt,
        output=out,
        events=events,
        time=TimeInfo(start=wall_start, end=wall_end),
    )

    # Populate usage once based on events
    resp.usage = compute_usage(events)
    return resp


## Legacy sync `invoke()` removed; use api.Loop.run/api.run instead.

# Re-export structured invoke here for API stability
from .structured import invoke_structured as async_invoke_structured  # noqa: E402

__all__ = [
    # helpers
    "InvokeConfig",
    "write_config_file",
    "build_env_with_config_path",
    "build_opencode_cmd",
    "run_opencode_jsonl",
    "Request",
    "async_invoke",
    "async_invoke_structured",
]
