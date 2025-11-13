"""
Custom exceptions for the Avela SDK.
"""


class AvelaError(Exception):
    """Base exception for all Avela SDK errors."""

    pass


class AuthenticationError(AvelaError):
    """Raised when authentication fails."""

    def __init__(self, message: str = 'Authentication failed'):
        self.message = message
        super().__init__(self.message)


class APIError(AvelaError):
    """Raised when an API request fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_body: str | None = None,
    ):
        self.message = message
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(self.message)

    def __str__(self) -> str:
        error_msg = self.message
        if self.status_code:
            error_msg = f'[{self.status_code}] {error_msg}'
        if self.response_body:
            error_msg = f'{error_msg}\nResponse: {self.response_body}'
        return error_msg


class ValidationError(AvelaError):
    """Raised when request validation fails."""

    pass


class NotFoundError(APIError):
    """Raised when a resource is not found (404)."""

    def __init__(
        self, message: str = 'Resource not found', response_body: str | None = None
    ):
        super().__init__(message, status_code=404, response_body=response_body)


class RateLimitError(APIError):
    """Raised when rate limit is exceeded (429)."""

    def __init__(
        self, message: str = 'Rate limit exceeded', response_body: str | None = None
    ):
        super().__init__(message, status_code=429, response_body=response_body)


class ServerError(APIError):
    """Raised when server returns 5xx error."""

    def __init__(
        self,
        message: str = 'Server error',
        status_code: int = 500,
        response_body: str | None = None,
    ):
        super().__init__(message, status_code=status_code, response_body=response_body)
