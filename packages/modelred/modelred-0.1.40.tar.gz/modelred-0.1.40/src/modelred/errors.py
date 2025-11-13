from __future__ import annotations


class ModelRedError(Exception):
    """Base SDK error."""


class APIError(ModelRedError):
    """HTTP/API error."""

    def __init__(
        self,
        status: int,
        message: str,
        code: str | None = None,
        details: object | None = None,
    ):
        super().__init__(f"{status}: {message}" + (f" [code={code}]" if code else ""))
        self.status = status
        self.message = message
        self.code = code
        self.details = details


class Unauthorized(APIError):
    """401 Unauthorized."""


class Forbidden(APIError):
    """403 Forbidden."""


class NotAllowedForApiKey(Forbidden):
    """403 where the action is disallowed for API key auth."""


class NotFound(APIError):
    """404 Not Found."""


class Conflict(APIError):
    """409 Conflict."""


class ValidationFailed(APIError):
    """400 Validation or 422 Unprocessable."""


class RateLimited(APIError):
    """429 Too Many Requests."""


class LimitExceeded(Forbidden):
    """Plan/limit enforcement returned as 403 with code or message."""


class ServerError(APIError):
    """5xx errors."""
