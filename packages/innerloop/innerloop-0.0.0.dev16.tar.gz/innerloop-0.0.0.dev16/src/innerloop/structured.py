from __future__ import annotations

import json
import logging
import os
import re
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from .events import ErrorEvent, OpenCodeEvent, TimeInfo
from .helper import unix_ms
from .request import Request
from .response import Response
from .usage import compute_usage

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)

JSON_TAG_RE = re.compile(r"<json>\s*(.*?)\s*</json>", re.DOTALL | re.IGNORECASE)


def _extract_json_snippet(text: str) -> str:
    """Extract JSON only from <json>...</json> tags.

    Keeping a single, explicit protocol makes behavior predictable. If the
    model does not return tags, the caller should reprompt.
    """
    m = JSON_TAG_RE.search(text)
    if not m:
        raise ValueError("No <json>...</json> block found in the response.")
    return m.group(1).strip()


def _extract_and_parse_json(text: str, model_cls: type[T]) -> T:
    """Extract the best JSON snippet then validate against the model."""
    snippet = _extract_json_snippet(text)
    try:
        return model_cls.model_validate_json(snippet)
    except ValidationError as e:
        # Surface the original validation message so the model/user can correct it
        raise ValueError(str(e)) from e


def _resolve_output_path(workdir: str | None, session: str | None, override: str | None) -> str:
    wd = workdir or os.getcwd()
    if override:
        target = override
    else:
        sid = session or "default"
        safe = "".join(c if c.isalnum() else "_" for c in sid)
        target = os.path.join(wd, ".innerloop", f"structured_{safe}_{unix_ms()}.json")
    abs_path = os.path.abspath(target)
    abs_wd = os.path.abspath(wd)
    if not abs_wd.endswith(os.sep):
        abs_wd += os.sep
    if not abs_path.startswith(abs_wd):
        raise ValueError(
            f"Structured output file must be under workdir. File: {abs_path}, Workdir: {abs_wd.rstrip(os.sep)}"
        )
    os.makedirs(os.path.dirname(abs_path), exist_ok=True)
    return abs_path


def _can_write(perms) -> bool:
    if perms.edit == perms.ALLOW:
        return True
    if perms.bash == perms.ALLOW:
        return True
    if isinstance(perms.bash, dict) and any(v == perms.ALLOW for v in perms.bash.values()):
        return True
    return False


def _compose_prompt(prompt: str, model_cls: type[BaseModel], abs_path: str, can_write: bool) -> str:
    schema = json.dumps(model_cls.model_json_schema(), indent=2)
    if can_write:
        instr = (
            f"Write a valid JSON matching this schema to: {abs_path}.\n"
            "If you cannot write files, return ONLY JSON inside <json>...</json> tags."
        )
    else:
        instr = (
            "Return ONLY JSON inside <json>...</json> tags matching the schema.\n"
            "No extra text."
        )
    return f"{prompt}\n\n{instr}\nSchema:\n<schema>\n{schema}\n</schema>"


def _compose_retry(base_prompt: str, err: str, model_cls: type[BaseModel]) -> str:
    """Compose a neutral, validation-driven retry prompt.

    - Keep the original task context (base_prompt)
    - Surface the exact validation error so the model can correct
    - Instruct to return ONLY JSON in <json> tags (no prose)
    - Do not bake in test-specific hints or field names
    """
    return (
        f"{base_prompt}\n\n"
        "Your previous JSON failed validation.\n"
        f"Error: {err}.\n"
        "Use the validation error as the source of truth.\n"
        "Return ONLY corrected JSON in <json>...</json> tags that validates."
    )


async def _attempt(
    request: Request,
    *,
    prompt: str,
    abs_path: str,
    model_cls: type[BaseModel],
    session: str | None,
) -> tuple[Response[Any], BaseModel | None, str | None]:
    from .invoke import async_invoke  # local import to avoid cycles

    resp = await async_invoke(
        Request(
            model=request.model,
            prompt=prompt,
            permission=request.permission,
            providers=request.providers,
            mcp=request.mcp,
            response_format=None,
            session=session,
            workdir=request.workdir,
        )
    )

    # File mode if file exists
    if os.path.exists(abs_path):
        try:
            with open(abs_path) as f:
                content = f.read()
            out = model_cls.model_validate_json(content)
            return resp, out, None
        except (ValidationError, ValueError, OSError) as e:
            return resp, None, str(e)

    # Fallback: extract from textual output
    try:
        out = _extract_and_parse_json(str(resp.output), model_cls)
        with open(abs_path, "w") as f:
            f.write(out.model_dump_json(indent=2))
        return resp, out, None
    except (ValidationError, ValueError) as e:
        return resp, None, str(e)


async def invoke_structured(
    request: Request,
    *,
    max_retries: int = 3,
) -> Response[Any]:
    if request.response_format is None:
        from .invoke import async_invoke  # local import

        return await async_invoke(request)

    abs_path = _resolve_output_path(request.workdir, request.session, request.output_file)
    can_write = _can_write(request.permission)
    base_prompt = _compose_prompt(request.prompt, request.response_format, abs_path, can_write)

    attempts = 0
    total_events: list[OpenCodeEvent] = []
    final_session: str | None = request.session
    final_output: BaseModel | None = None
    wall_start = unix_ms()
    last_err = "invalid"

    while attempts < max_retries:
        attempts += 1
        prompt = base_prompt if attempts == 1 else _compose_retry(base_prompt, last_err, request.response_format)
        resp, out, err = await _attempt(
            request,
            prompt=prompt,
            abs_path=abs_path,
            model_cls=request.response_format,
            session=final_session,
        )
        total_events.extend(resp.events)
        final_session = resp.session_id
        if out is not None:
            final_output = out
            break
        last_err = err or last_err

        total_events.append(
            ErrorEvent(
                timestamp=unix_ms(),
                sessionID=final_session or "",
                type="error",
                message=last_err,
                code=None,
                severity="error",
            )
        )

    if final_output is None:
        raise RuntimeError(
            f"Structured output validation failed after {attempts} attempts. Expected file: {abs_path}\nError: {last_err}"
        )

    wall_end = unix_ms()
    out_resp = Response(
        session_id=final_session or "",
        input=request.prompt,
        output=final_output,
        structured_output_file=abs_path,
        events=total_events,
        attempts=attempts,
        time=TimeInfo(start=wall_start, end=wall_end),
    )
    out_resp.usage = compute_usage(total_events)
    return out_resp
