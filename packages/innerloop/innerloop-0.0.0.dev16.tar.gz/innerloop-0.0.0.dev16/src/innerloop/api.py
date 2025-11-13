"""Public API: Loop class + convenience helpers.

Surface:
- Loop: run/arun, session/asession
- Functional wrappers: run/arun
- Helpers: allow (permissions), mcp (servers)
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Awaitable, Iterator
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Protocol, runtime_checkable

from pydantic import BaseModel

from .helper import to_session_id
from .invoke import async_invoke
from .mcp import LocalMcpServer, RemoteMcpServer
from .permissions import Permission, PermissionLevel
from .providers import ProviderConfig
from .request import Request
from .response import Response
from .structured import invoke_structured as async_invoke_structured


def allow(
    *tools: str,
    read: bool = True,
    write: bool = True,
    bash: bool | dict[str, PermissionLevel] = False,
    webfetch: bool = False,
) -> Permission:
    """Convenience builder for Permission.

    Semantics:
    - tools may contain "bash" or "webfetch" to allow them quickly
    - edit is ALLOW only when both read=True and write=True; otherwise DENY
    - passing a dict for `bash` enables fine‑grained tool policies
    """
    edit_level = Permission.ALLOW if write and read else Permission.DENY
    bash_level = (
        Permission.ALLOW
        if (bash is True or "bash" in tools)
        else Permission.DENY
    )
    web_level = (
        Permission.ALLOW
        if (webfetch or "webfetch" in tools)
        else Permission.DENY
    )
    return Permission(
        edit=edit_level,
        bash=bash if isinstance(bash, dict) else bash_level,
        webfetch=web_level,
    )


def mcp(**servers: str) -> dict[str, LocalMcpServer | RemoteMcpServer]:
    """Build MCP server definitions.

    - Remote: pass a URL string (http/https)
    - Local: pass a command string; optional "ENV=VALUE" tokens allowed before cmd

    Examples:
      mcp(context7="https://mcp.context7.com/mcp")
      mcp(biomcp="uvx --from biomcp-python biomcp run")
    """
    out: dict[str, LocalMcpServer | RemoteMcpServer] = {}
    for name, spec in servers.items():
        s = spec.strip()
        if s.startswith(("http://", "https://")):
            out[name] = RemoteMcpServer(name=name, url=s)  # type: ignore[arg-type]
            continue
        env: dict[str, str] = {}
        cmd: list[str] = []
        for tok in s.split():
            if "=" in tok and not cmd:
                k, _, v = tok.partition("=")
                env[k] = v
            else:
                cmd.append(tok)
        out[name] = LocalMcpServer(name=name, command=cmd, environment=env or None)
    return out


# providers(...) helper removed; prefer innerloop.providers.provider(name, **options)


class Loop:
    """Reusable loop that hides config and exposes simple methods."""

    def __init__(
        self,
        *,
        model: str,
        perms: Permission | None = None,
        providers: dict[str, ProviderConfig] | None = None,
        mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    ) -> None:
        self.model = model
        self.perms = perms or Permission()
        self.providers = providers
        self.mcp = mcp
        self.default_workdir: str | None = None
        self.default_response_format: type[BaseModel] | None = None
        self._last_session_id: str | None = None

    def run(
        self,
        prompt: str,
        *,
        response_format: type[BaseModel] | None = None,
        output_file: str | None = None,
        session: str | Response[Any] | None = None,
        workdir: str | None = None,
        max_retries: int = 3,
        total_timeout: float | None = None,
        idle_timeout: float | None = None,
    ) -> Response[Any]:
        # Avoid creating coroutine objects when running inside an event loop;
        # raising early prevents un-awaited coroutine warnings in async tests.
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # No running loop → safe to proceed with asyncio.run
            pass
        else:
            # Avoid creating coroutine objects that would trigger "never awaited"
            # warnings when raising from within an active event loop.
            raise RuntimeError(
                "asyncio.run() cannot be called from a running event loop"
            )
        sid = to_session_id(session)
        if sid is None:
            sid = self._last_session_id
        eff_workdir = workdir if workdir is not None else self.default_workdir
        eff_format = (
            response_format
            if response_format is not None
            else self.default_response_format
        )
        req = Request(
            model=self.model,
            prompt=prompt,
            permission=self.perms,
            providers=self.providers,
            mcp=self.mcp,
            response_format=eff_format,
            output_file=output_file,
            session=sid,
            workdir=eff_workdir,
        )
        if eff_format is not None:
            resp = asyncio.run(
                async_invoke_structured(req, max_retries=max_retries)
            )
        else:
            resp = asyncio.run(
                async_invoke(
                    req,
                    total_timeout=total_timeout,
                    idle_timeout=idle_timeout,
                )
            )
        if resp.session_id:
            self._last_session_id = resp.session_id
        return resp

    async def arun(
        self,
        prompt: str,
        *,
        response_format: type[BaseModel] | None = None,
        output_file: str | None = None,
        session: str | Response[Any] | None = None,
        workdir: str | None = None,
        max_retries: int = 3,
        total_timeout: float | None = None,
        idle_timeout: float | None = None,
    ) -> Response[Any]:
        sid = to_session_id(session)
        if sid is None:
            sid = self._last_session_id
        eff_workdir = workdir if workdir is not None else self.default_workdir
        eff_format = (
            response_format
            if response_format is not None
            else self.default_response_format
        )
        req = Request(
            model=self.model,
            prompt=prompt,
            permission=self.perms,
            providers=self.providers,
            mcp=self.mcp,
            response_format=eff_format,
            output_file=output_file,
            session=sid,
            workdir=eff_workdir,
        )
        if eff_format is not None:
            resp = await async_invoke_structured(req, max_retries=max_retries)
        else:
            resp = await async_invoke(
                req, total_timeout=total_timeout, idle_timeout=idle_timeout
            )
        if resp.session_id:
            self._last_session_id = resp.session_id
        return resp

    @runtime_checkable
    class AskSync(Protocol):
        def __call__(
            self,
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            workdir: str | None = None,
        ) -> Response[Any]: ...

    @runtime_checkable
    class AskAsync(Protocol):
        def __call__(
            self,
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            workdir: str | None = None,
        ) -> Awaitable[Response[Any]]: ...

    @contextmanager
    def session(self) -> Iterator[AskSync]:
        sid: str | None = None

        def ask(
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            workdir: str | None = None,
        ) -> Response[Any]:
            nonlocal sid
            if sid is None:
                # Empty string sentinel means: force new session (no reuse),
                # let CLI allocate a real session ID on first call.
                sid = ""
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            resp = self.run(
                prompt,
                response_format=eff_format,
                session=sid,
                workdir=(
                    workdir if workdir is not None else self.default_workdir
                ),
            )
            sid = resp.session_id or sid
            return resp

        yield ask

    @asynccontextmanager
    async def asession(self) -> AsyncIterator[AskAsync]:
        sid: str | None = None

        async def ask(
            prompt: str,
            response_format: type[BaseModel] | None = None,
            *,
            workdir: str | None = None,
        ) -> Response[Any]:
            nonlocal sid
            if sid is None:
                # Empty string sentinel means: force new session (no reuse),
                # let CLI allocate a real session ID on first call.
                sid = ""
            eff_format = (
                response_format
                if response_format is not None
                else self.default_response_format
            )
            resp = await self.arun(
                prompt,
                response_format=eff_format,
                session=sid,
                workdir=(
                    workdir if workdir is not None else self.default_workdir
                ),
            )
            sid = resp.session_id or sid
            return resp

        yield ask


def run(
    prompt: str,
    *,
    model: str,
    response_format: type[BaseModel] | None = None,
    output_file: str | None = None,
    session: str | Response[Any] | None = None,
    workdir: str | None = None,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    total_timeout: float | None = None,
    idle_timeout: float | None = None,
) -> Response[Any]:
    return Loop(model=model, perms=perms, providers=providers, mcp=mcp).run(
        prompt,
        response_format=response_format,
        output_file=output_file,
        session=session,
        workdir=workdir,
        total_timeout=total_timeout,
        idle_timeout=idle_timeout,
    )


async def arun(
    prompt: str,
    *,
    model: str,
    response_format: type[BaseModel] | None = None,
    output_file: str | None = None,
    session: str | Response[Any] | None = None,
    workdir: str | None = None,
    perms: Permission | None = None,
    providers: dict[str, ProviderConfig] | None = None,
    mcp: dict[str, LocalMcpServer | RemoteMcpServer] | None = None,
    total_timeout: float | None = None,
    idle_timeout: float | None = None,
) -> Response[Any]:
    return await Loop(
        model=model, perms=perms, providers=providers, mcp=mcp
    ).arun(
        prompt,
        response_format=response_format,
        output_file=output_file,
        session=session,
        workdir=workdir,
        total_timeout=total_timeout,
        idle_timeout=idle_timeout,
    )


__all__ = [
    "Loop",
    "run",
    "arun",
    "allow",
    "mcp",
]
