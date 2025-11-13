"""Generate minimal permission statements from Permission objects.

This module provides a simple permission statement that's automatically
injected into prompts to inform the LLM what tools are allowed/denied.
"""

from __future__ import annotations

from .permissions import Permission


def _build_permission_statement(perms: Permission) -> str | None:
    """Build a clear permission statement from Permission object.

    Returns an instructive statement that explicitly tells the LLM what it CAN
    and CANNOT do, with warnings about attempting denied operations.

    Args:
        perms: The Permission object defining tool access

    Returns:
        Permission statement string, or None if all defaults (nothing to say)

    Example output:
        ## Permissions

        ✓ Allowed tools:
        - webfetch: Fetch content from URLs via HTTP/HTTPS

        ✗ Denied tools:
        - bash: Do not attempt shell commands, scripts, or command-line utilities
        - edit: Do not attempt file operations (read, write, create, or edit files)

        Allowed domains: en.wikipedia.org

        IMPORTANT: Use ONLY the allowed tools listed above. Do not attempt to use denied tools - they will fail.
    """
    # Tool information with explicit avoidance instructions
    TOOL_INFO = {
        "bash": {
            "desc": "Execute shell commands",
            "avoid": "Do not attempt shell commands, scripts, or command-line utilities",
        },
        "webfetch": {
            "desc": "Fetch content from URLs via HTTP/HTTPS",
            "avoid": "Do not attempt to fetch web content or make HTTP requests",
        },
        "edit": {
            "desc": "Read, write, and modify files",
            "avoid": "Do not attempt file operations (read, write, create, or edit files)",
        },
    }

    # Map permission attributes to actual OpenCode CLI tool names
    allowed_tools: list[str] = []
    denied_tools: list[str] = []

    if perms.bash == Permission.ALLOW:
        allowed_tools.append("bash")
    elif perms.bash == Permission.DENY:
        denied_tools.append("bash")

    if perms.webfetch == Permission.ALLOW:
        allowed_tools.append("webfetch")
    elif perms.webfetch == Permission.DENY:
        denied_tools.append("webfetch")

    if perms.edit == Permission.ALLOW:
        allowed_tools.append("edit")
    elif perms.edit == Permission.DENY:
        denied_tools.append("edit")

    # If all defaults (edit=ALLOW, bash=DENY, webfetch=DENY), skip
    # This matches the default Permission() with no customization
    if (
        perms.edit == Permission.ALLOW
        and perms.bash == Permission.DENY
        and perms.webfetch == Permission.DENY
    ):
        return None

    lines = ["## Permissions\n\n"]

    if allowed_tools:
        lines.append("✓ Allowed tools:\n")
        for tool in allowed_tools:
            lines.append(f"- {tool}: {TOOL_INFO[tool]['desc']}\n")
        lines.append("\n")

    if denied_tools:
        lines.append("✗ Denied tools:\n")
        for tool in denied_tools:
            lines.append(f"- {tool}: {TOOL_INFO[tool]['avoid']}\n")
        lines.append("\n")

    lines.append("IMPORTANT: Use ONLY the allowed tools listed above. ")
    lines.append("Do not attempt to use denied tools - they will fail.\n")

    return "".join(lines)


__all__ = ["_build_permission_statement"]
