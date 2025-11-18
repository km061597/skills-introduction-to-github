"""
Custom exceptions for SmartAmazon API

Enterprise-grade exception handling with proper error codes and messages
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class SmartAmazonException(Exception):
    """Base exception for all SmartAmazon errors"""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(SmartAmazonException):
    """Raised when input validation fails"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="VALIDATION_ERROR",
            details=details
        )


class NotFoundError(SmartAmazonException):
    """Raised when a resource is not found"""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with identifier '{identifier}' not found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="NOT_FOUND",
            details={"resource": resource, "identifier": identifier}
        )


class DatabaseError(SmartAmazonException):
    """Raised when database operations fail"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="DATABASE_ERROR",
            details=details
        )


class ScraperError(SmartAmazonException):
    """Raised when scraping operations fail"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SCRAPER_ERROR",
            details=details
        )


class RateLimitError(SmartAmazonException):
    """Raised when rate limit is exceeded"""

    def __init__(self, retry_after: int = 60):
        super().__init__(
            message=f"Rate limit exceeded. Please try again in {retry_after} seconds.",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error_code="RATE_LIMIT_EXCEEDED",
            details={"retry_after": retry_after}
        )


class CacheError(SmartAmazonException):
    """Raised when cache operations fail"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="CACHE_ERROR",
            details=details
        )


class AuthenticationError(SmartAmazonException):
    """Raised when authentication fails"""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code="AUTHENTICATION_ERROR"
        )


class AuthorizationError(SmartAmazonException):
    """Raised when authorization fails"""

    def __init__(self, message: str = "Insufficient permissions"):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_code="AUTHORIZATION_ERROR"
        )


class ServiceUnavailableError(SmartAmazonException):
    """Raised when a service is temporarily unavailable"""

    def __init__(self, service: str, retry_after: int = 60):
        super().__init__(
            message=f"{service} is temporarily unavailable",
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            error_code="SERVICE_UNAVAILABLE",
            details={"service": service, "retry_after": retry_after}
        )


def handle_exception(exc: SmartAmazonException) -> Dict[str, Any]:
    """
    Convert SmartAmazonException to error response format

    Returns:
        Dict with error details for JSON response
    """
    return {
        "error": {
            "code": exc.error_code,
            "message": exc.message,
            "details": exc.details
        }
    }
