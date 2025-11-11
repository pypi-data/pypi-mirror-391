"""Exception hierarchy for the Grasp SDK."""

from typing import Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx


class GraspError(Exception):
    """Base exception for all Grasp SDK errors."""

    pass


class APIError(GraspError):
    """Base class for API-related errors."""

    def __init__(
        self,
        message: str,
        response: Optional[Any] = None,  # httpx.Response when runtime
        body: Optional[str] = None,
    ):
        self.message = message
        self.response = response
        self.body = body
        super().__init__(message)


class APIConnectionError(GraspError):
    """Network connectivity issues."""

    pass


class APITimeoutError(APIConnectionError):
    """Request timeout."""

    pass


class APIResponseValidationError(APIError):
    """Raised when API response doesn't match expected schema."""

    pass


class APIStatusError(APIError):
    """Base class for HTTP status errors."""

    def __init__(
        self,
        message: str,
        response: Any,  # httpx.Response at runtime
        body: Optional[str] = None,
    ):
        super().__init__(message, response, body)
        self.status_code = response.status_code
        self.request_id = response.headers.get("x-request-id")


class BadRequestError(APIStatusError):
    """HTTP 400 - Bad Request."""

    pass


class AuthenticationError(APIStatusError, GraspError):
    """HTTP 401 - Unauthorized or missing API key."""

    def __init__(
        self,
        message: str,
        response: Optional[Any] = None,
        body: Optional[str] = None,
    ):
        if response is not None:
            # Called as APIStatusError
            super().__init__(message, response, body)
        else:
            # Called as simple exception (e.g., missing API key)
            GraspError.__init__(self, message)


class PermissionDeniedError(APIStatusError):
    """HTTP 403 - Forbidden."""

    pass


class NotFoundError(APIStatusError):
    """HTTP 404 - Not Found."""

    pass


class UnprocessableEntityError(APIStatusError):
    """HTTP 422 - Unprocessable Entity."""

    pass


class RateLimitError(APIStatusError):
    """HTTP 429 - Rate Limit Exceeded."""

    def __init__(
        self,
        message: str,
        response: Any,  # httpx.Response at runtime
        body: Optional[str] = None,
    ):
        super().__init__(message, response, body)
        self.retry_after = response.headers.get("retry-after")


class InternalServerError(APIStatusError):
    """HTTP 500 - Internal Server Error."""

    pass


class ServiceUnavailableError(APIStatusError):
    """HTTP 503 - Service Unavailable."""

    pass


# Status code to exception mapping
STATUS_CODE_TO_ERROR = {
    400: BadRequestError,
    401: AuthenticationError,
    403: PermissionDeniedError,
    404: NotFoundError,
    422: UnprocessableEntityError,
    429: RateLimitError,
    500: InternalServerError,
    503: ServiceUnavailableError,
}


def make_status_error(response: Any, body: Optional[str] = None) -> APIStatusError:  # response is httpx.Response at runtime
    """Create appropriate exception based on HTTP status code."""
    error_class = STATUS_CODE_TO_ERROR.get(response.status_code)
    if error_class is None:
        if 400 <= response.status_code < 500:
            error_class = APIStatusError
        elif 500 <= response.status_code < 600:
            error_class = InternalServerError
        else:
            error_class = APIStatusError

    message = f"API request failed with status code {response.status_code}"
    if body:
        message = f"{message}: {body}"

    return error_class(message, response, body)