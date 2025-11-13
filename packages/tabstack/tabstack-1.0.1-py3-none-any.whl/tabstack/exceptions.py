"""Custom exceptions for TABStack AI SDK."""

from typing import Optional


class TABStackError(Exception):
    """Base exception for all TABStack AI errors."""

    def __init__(self, message: str, status_code: Optional[int] = None) -> None:
        """Initialize error.

        Args:
            message: Error message
            status_code: HTTP status code if applicable
        """
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class BadRequestError(TABStackError):
    """Exception for 400 Bad Request errors.

    Raised when the request is malformed or missing required fields
    (e.g., invalid JSON schema, missing task description, invalid parameters).

    This error indicates a client-side problem. Do not retry.
    """

    def __init__(self, message: str) -> None:
        """Initialize bad request error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=400)


class UnauthorizedError(TABStackError):
    """Exception for 401 Unauthorized errors.

    Raised when the API key is invalid or missing. Verify your API key
    is correct and has not expired.

    This error indicates an authentication problem. Do not retry without
    fixing the API key.
    """

    def __init__(self, message: str = "Unauthorized - Invalid or missing API key") -> None:
        """Initialize unauthorized error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=401)


class InvalidURLError(TABStackError):
    """Exception for 422 Unprocessable Entity errors related to URLs.

    Raised when the provided URL is invalid, inaccessible, or returns an error
    (e.g., 404 Not Found, connection timeout, invalid domain).

    This error indicates a problem with the URL itself. Do not retry without
    fixing the URL.
    """

    def __init__(self, message: str = "Invalid or inaccessible URL") -> None:
        """Initialize invalid URL error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=422)


class ServerError(TABStackError):
    """Exception for 500 Internal Server Error.

    Raised when the server encounters an error processing the request.
    This is typically a temporary issue.

    This error is retryable. Consider implementing exponential backoff
    when retrying.
    """

    def __init__(self, message: str = "Internal server error") -> None:
        """Initialize server error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=500)


class ServiceUnavailableError(TABStackError):
    """Exception for 503 Service Unavailable errors.

    Raised when a service (e.g., automate) is temporarily unavailable,
    overloaded, or not configured for your account.

    This error may be retryable after a delay. Check service status or
    contact support if the issue persists.
    """

    def __init__(self, message: str = "Service unavailable") -> None:
        """Initialize service unavailable error.

        Args:
            message: Error message
        """
        super().__init__(message, status_code=503)


class APIError(TABStackError):
    """Generic API error for unexpected status codes."""

    def __init__(self, message: str, status_code: int) -> None:
        """Initialize API error.

        Args:
            message: Error message
            status_code: HTTP status code
        """
        super().__init__(message, status_code=status_code)
