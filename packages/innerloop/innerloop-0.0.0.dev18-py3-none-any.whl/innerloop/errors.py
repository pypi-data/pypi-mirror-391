"""Library-specific exceptions to avoid swallowing errors.

Define clear, typed exceptions that callers can handle precisely.
"""


class InnerLoopError(Exception):
    """Base exception for all library-specific errors."""


class CliNotFoundError(InnerLoopError):
    """Raised when the 'opencode' executable is not found on PATH."""


class CliExitError(InnerLoopError):
    """Raised when the 'opencode' CLI exits with a non-zero status code."""

    def __init__(self, message: str, return_code: int, stderr: str) -> None:
        super().__init__(message)
        self.return_code = return_code
        self.stderr = stderr


class CliTimeoutError(InnerLoopError):
    """Raised when the CLI operation exceeds the specified timeout."""

    def __init__(self, message: str, timeout: float) -> None:
        super().__init__(message)
        self.timeout = timeout


class ModelNotFoundError(InnerLoopError):
    """Raised when the requested provider/model is not available.

    Attributes:
        provider_id: Provider identifier (e.g., "anthropic")
        model_id: Model identifier without provider prefix (e.g., "claude-haiku-4-5")
        suggestions: Optional list of suggested alternatives (provider/model format)
        source: "preflight" when thrown by local check, "cli" when emitted by opencode
    """

    def __init__(
        self,
        *,
        provider_id: str,
        model_id: str,
        suggestions: list[str] | None = None,
        source: str = "preflight",
    ) -> None:
        msg = f"Model not found: {provider_id}/{model_id}"
        if suggestions:
            msg += "; suggestions: " + ", ".join(suggestions)
        super().__init__(msg)
        self.provider_id = provider_id
        self.model_id = model_id
        self.suggestions = suggestions or []
        self.source = source
