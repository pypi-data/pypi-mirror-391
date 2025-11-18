"""
Zetsubou.life SDK Exceptions

Custom exception classes for handling API errors and SDK issues.
"""

from typing import Optional, Dict, Any


class ZetsubouError(Exception):
    """Base exception for all Zetsubou SDK errors."""
    
    def __init__(self, message: str, error_data: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_data = error_data or {}
        self.code = error_data.get('code', 'UNKNOWN_ERROR') if error_data else 'UNKNOWN_ERROR'
        self.status_code = error_data.get('status_code') if error_data else None


class AuthenticationError(ZetsubouError):
    """Raised when authentication fails (401 Unauthorized)."""
    pass


class RateLimitError(ZetsubouError):
    """Raised when rate limit is exceeded (429 Too Many Requests)."""
    
    def __init__(self, message: str, error_data: Optional[Dict[str, Any]] = None, retry_after: int = 60):
        super().__init__(message, error_data)
        self.retry_after = retry_after


class ValidationError(ZetsubouError):
    """Raised when request validation fails (400 Bad Request)."""
    pass


class NotFoundError(ZetsubouError):
    """Raised when a resource is not found (404 Not Found)."""
    pass


class ServerError(ZetsubouError):
    """Raised when server encounters an error (5xx status codes)."""
    pass


class WebhookError(ZetsubouError):
    """Raised when webhook operations fail."""
    pass


class TimeoutError(ZetsubouError):
    """Raised when a request times out."""
    pass


class ConnectionError(ZetsubouError):
    """Raised when connection to the API fails."""
    pass