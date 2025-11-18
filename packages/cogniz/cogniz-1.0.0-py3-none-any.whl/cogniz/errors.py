"""Cogniz SDK exception classes."""


class CognizError(Exception):
    """Base exception for all Cogniz errors."""

    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class AuthenticationError(CognizError):
    """Authentication failed - invalid or missing API key."""
    pass


class NotFoundError(CognizError):
    """Requested resource not found."""
    pass


class RateLimitError(CognizError):
    """API rate limit exceeded."""
    pass


class ValidationError(CognizError):
    """Input validation failed."""
    pass


class ServerError(CognizError):
    """Server-side error occurred."""
    pass


class NetworkError(CognizError):
    """Network connection failed."""
    pass


class QuotaExceededError(CognizError):
    """Storage or memory quota exceeded."""
    pass
