"""
Tests for custom exception classes

This module tests:
1. SmartAmazonException base class
2. All specific exception types
3. Exception attributes (message, status_code, error_code)
4. Exception handler function
"""
import pytest
from fastapi import status

from app.exceptions import (
    SmartAmazonException,
    ValidationError,
    NotFoundError,
    DatabaseError,
    ScraperError,
    RateLimitError,
    CacheError,
    AuthenticationError,
    AuthorizationError,
    ServiceUnavailableError,
    handle_exception
)


class TestSmartAmazonException:
    """Tests for base SmartAmazonException class"""

    def test_base_exception_initialization(self):
        """Test that base exception initializes correctly"""
        exc = SmartAmazonException(
            message="Test error",
            status_code=500,
            error_code="TEST_ERROR"
        )

        assert exc.message == "Test error"
        assert exc.status_code == 500
        assert exc.error_code == "TEST_ERROR"
        assert exc.details == {}

    def test_base_exception_with_details(self):
        """Test base exception with details"""
        details = {"field": "value", "count": 42}
        exc = SmartAmazonException(
            message="Test error",
            error_code="TEST_ERROR",
            details=details
        )

        assert exc.details == details
        assert exc.details["field"] == "value"
        assert exc.details["count"] == 42

    def test_base_exception_default_status(self):
        """Test that default status code is 500"""
        exc = SmartAmazonException(message="Test", error_code="TEST")

        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_base_exception_string_representation(self):
        """Test that exception message is used for string representation"""
        exc = SmartAmazonException(message="Test error", error_code="TEST")

        assert str(exc) == "Test error"

    def test_base_exception_is_exception(self):
        """Test that SmartAmazonException inherits from Exception"""
        exc = SmartAmazonException(message="Test", error_code="TEST")

        assert isinstance(exc, Exception)


class TestValidationError:
    """Tests for ValidationError exception"""

    def test_validation_error_initialization(self):
        """Test ValidationError initialization"""
        exc = ValidationError(message="Invalid input")

        assert exc.message == "Invalid input"
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.error_code == "VALIDATION_ERROR"

    def test_validation_error_with_details(self):
        """Test ValidationError with validation details"""
        details = {
            "field": "email",
            "reason": "Invalid email format"
        }
        exc = ValidationError(message="Validation failed", details=details)

        assert exc.details == details
        assert exc.details["field"] == "email"

    def test_validation_error_is_smart_amazon_exception(self):
        """Test that ValidationError inherits from SmartAmazonException"""
        exc = ValidationError(message="Test")

        assert isinstance(exc, SmartAmazonException)


class TestNotFoundError:
    """Tests for NotFoundError exception"""

    def test_not_found_error_initialization(self):
        """Test NotFoundError initialization"""
        exc = NotFoundError(resource="Product", identifier="B000QSO98W")

        assert "Product" in exc.message
        assert "B000QSO98W" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.error_code == "NOT_FOUND"

    def test_not_found_error_details(self):
        """Test NotFoundError includes resource details"""
        exc = NotFoundError(resource="User", identifier="123")

        assert exc.details["resource"] == "User"
        assert exc.details["identifier"] == "123"

    def test_not_found_error_message_format(self):
        """Test NotFoundError message format"""
        exc = NotFoundError(resource="Product", identifier="ABC123")

        assert exc.message == "Product with identifier 'ABC123' not found"


class TestDatabaseError:
    """Tests for DatabaseError exception"""

    def test_database_error_initialization(self):
        """Test DatabaseError initialization"""
        exc = DatabaseError(message="Connection failed")

        assert exc.message == "Connection failed"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.error_code == "DATABASE_ERROR"

    def test_database_error_with_details(self):
        """Test DatabaseError with database details"""
        details = {"query": "SELECT * FROM products", "error": "timeout"}
        exc = DatabaseError(message="Query failed", details=details)

        assert exc.details == details
        assert exc.details["query"] == "SELECT * FROM products"


class TestScraperError:
    """Tests for ScraperError exception"""

    def test_scraper_error_initialization(self):
        """Test ScraperError initialization"""
        exc = ScraperError(message="Failed to scrape Amazon")

        assert exc.message == "Failed to scrape Amazon"
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.error_code == "SCRAPER_ERROR"

    def test_scraper_error_with_details(self):
        """Test ScraperError with scraping details"""
        details = {"url": "https://amazon.com/...", "status": 403}
        exc = ScraperError(message="Access denied", details=details)

        assert exc.details["url"] == "https://amazon.com/..."
        assert exc.details["status"] == 403


class TestRateLimitError:
    """Tests for RateLimitError exception"""

    def test_rate_limit_error_initialization(self):
        """Test RateLimitError initialization"""
        exc = RateLimitError()

        assert "Rate limit exceeded" in exc.message
        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert exc.error_code == "RATE_LIMIT_EXCEEDED"

    def test_rate_limit_error_default_retry_after(self):
        """Test RateLimitError default retry_after"""
        exc = RateLimitError()

        assert exc.details["retry_after"] == 60
        assert "60 seconds" in exc.message

    def test_rate_limit_error_custom_retry_after(self):
        """Test RateLimitError with custom retry_after"""
        exc = RateLimitError(retry_after=120)

        assert exc.details["retry_after"] == 120
        assert "120 seconds" in exc.message


class TestCacheError:
    """Tests for CacheError exception"""

    def test_cache_error_initialization(self):
        """Test CacheError initialization"""
        exc = CacheError(message="Redis connection failed")

        assert exc.message == "Redis connection failed"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.error_code == "CACHE_ERROR"

    def test_cache_error_with_details(self):
        """Test CacheError with cache details"""
        details = {"operation": "SET", "key": "product:123"}
        exc = CacheError(message="Cache write failed", details=details)

        assert exc.details["operation"] == "SET"
        assert exc.details["key"] == "product:123"


class TestAuthenticationError:
    """Tests for AuthenticationError exception"""

    def test_authentication_error_initialization(self):
        """Test AuthenticationError initialization"""
        exc = AuthenticationError()

        assert exc.message == "Authentication failed"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED
        assert exc.error_code == "AUTHENTICATION_ERROR"

    def test_authentication_error_custom_message(self):
        """Test AuthenticationError with custom message"""
        exc = AuthenticationError(message="Invalid token")

        assert exc.message == "Invalid token"
        assert exc.status_code == status.HTTP_401_UNAUTHORIZED


class TestAuthorizationError:
    """Tests for AuthorizationError exception"""

    def test_authorization_error_initialization(self):
        """Test AuthorizationError initialization"""
        exc = AuthorizationError()

        assert exc.message == "Insufficient permissions"
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.error_code == "AUTHORIZATION_ERROR"

    def test_authorization_error_custom_message(self):
        """Test AuthorizationError with custom message"""
        exc = AuthorizationError(message="Admin access required")

        assert exc.message == "Admin access required"
        assert exc.status_code == status.HTTP_403_FORBIDDEN


class TestServiceUnavailableError:
    """Tests for ServiceUnavailableError exception"""

    def test_service_unavailable_error_initialization(self):
        """Test ServiceUnavailableError initialization"""
        exc = ServiceUnavailableError(service="Amazon API")

        assert "Amazon API" in exc.message
        assert "unavailable" in exc.message
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.error_code == "SERVICE_UNAVAILABLE"

    def test_service_unavailable_error_details(self):
        """Test ServiceUnavailableError includes service details"""
        exc = ServiceUnavailableError(service="Database", retry_after=120)

        assert exc.details["service"] == "Database"
        assert exc.details["retry_after"] == 120

    def test_service_unavailable_error_default_retry(self):
        """Test ServiceUnavailableError default retry_after"""
        exc = ServiceUnavailableError(service="Redis")

        assert exc.details["retry_after"] == 60


class TestHandleException:
    """Tests for handle_exception function"""

    def test_handle_exception_format(self):
        """Test that handle_exception returns correct format"""
        exc = ValidationError(message="Invalid input")
        result = handle_exception(exc)

        assert "error" in result
        assert "code" in result["error"]
        assert "message" in result["error"]
        assert "details" in result["error"]

    def test_handle_exception_includes_code(self):
        """Test that error code is included"""
        exc = NotFoundError(resource="Product", identifier="123")
        result = handle_exception(exc)

        assert result["error"]["code"] == "NOT_FOUND"

    def test_handle_exception_includes_message(self):
        """Test that error message is included"""
        exc = DatabaseError(message="Connection timeout")
        result = handle_exception(exc)

        assert result["error"]["message"] == "Connection timeout"

    def test_handle_exception_includes_details(self):
        """Test that error details are included"""
        details = {"field": "email", "reason": "invalid format"}
        exc = ValidationError(message="Invalid", details=details)
        result = handle_exception(exc)

        assert result["error"]["details"] == details

    def test_handle_exception_empty_details(self):
        """Test handle_exception with no details"""
        exc = AuthenticationError()
        result = handle_exception(exc)

        assert result["error"]["details"] == {}

    def test_handle_exception_various_exceptions(self):
        """Test handle_exception with different exception types"""
        exceptions = [
            ValidationError(message="Test"),
            NotFoundError(resource="Test", identifier="123"),
            DatabaseError(message="Test"),
            ScraperError(message="Test"),
            RateLimitError(),
            CacheError(message="Test"),
            AuthenticationError(),
            AuthorizationError(),
            ServiceUnavailableError(service="Test")
        ]

        for exc in exceptions:
            result = handle_exception(exc)

            # All should have the standard format
            assert "error" in result
            assert "code" in result["error"]
            assert "message" in result["error"]
            assert "details" in result["error"]
            assert result["error"]["code"] == exc.error_code


class TestExceptionInheritance:
    """Tests for exception inheritance hierarchy"""

    def test_all_exceptions_inherit_from_base(self):
        """Test that all custom exceptions inherit from SmartAmazonException"""
        exception_classes = [
            ValidationError,
            NotFoundError,
            DatabaseError,
            ScraperError,
            RateLimitError,
            CacheError,
            AuthenticationError,
            AuthorizationError,
            ServiceUnavailableError
        ]

        for exc_class in exception_classes:
            # Create instance with appropriate args
            if exc_class == NotFoundError:
                exc = exc_class(resource="Test", identifier="123")
            elif exc_class == ServiceUnavailableError:
                exc = exc_class(service="Test")
            elif exc_class == RateLimitError:
                exc = exc_class()
            elif exc_class in [AuthenticationError, AuthorizationError]:
                exc = exc_class()
            else:
                exc = exc_class(message="Test")

            assert isinstance(exc, SmartAmazonException)
            assert isinstance(exc, Exception)

    def test_all_exceptions_have_required_attributes(self):
        """Test that all exceptions have required attributes"""
        exceptions = [
            ValidationError(message="Test"),
            NotFoundError(resource="Test", identifier="123"),
            DatabaseError(message="Test"),
            ScraperError(message="Test"),
            RateLimitError(),
            CacheError(message="Test"),
            AuthenticationError(),
            AuthorizationError(),
            ServiceUnavailableError(service="Test")
        ]

        for exc in exceptions:
            assert hasattr(exc, 'message')
            assert hasattr(exc, 'status_code')
            assert hasattr(exc, 'error_code')
            assert hasattr(exc, 'details')
            assert isinstance(exc.status_code, int)
            assert isinstance(exc.error_code, str)
            assert isinstance(exc.details, dict)


class TestExceptionStatusCodes:
    """Tests for exception HTTP status codes"""

    def test_validation_error_422(self):
        """Test ValidationError uses 422 status"""
        exc = ValidationError(message="Test")
        assert exc.status_code == 422

    def test_not_found_error_404(self):
        """Test NotFoundError uses 404 status"""
        exc = NotFoundError(resource="Test", identifier="123")
        assert exc.status_code == 404

    def test_rate_limit_error_429(self):
        """Test RateLimitError uses 429 status"""
        exc = RateLimitError()
        assert exc.status_code == 429

    def test_authentication_error_401(self):
        """Test AuthenticationError uses 401 status"""
        exc = AuthenticationError()
        assert exc.status_code == 401

    def test_authorization_error_403(self):
        """Test AuthorizationError uses 403 status"""
        exc = AuthorizationError()
        assert exc.status_code == 403

    def test_service_unavailable_error_503(self):
        """Test ServiceUnavailableError uses 503 status"""
        exc = ServiceUnavailableError(service="Test")
        assert exc.status_code == 503

    def test_server_errors_500(self):
        """Test that internal errors use 500 status"""
        exceptions = [
            DatabaseError(message="Test"),
            CacheError(message="Test"),
            SmartAmazonException(message="Test", error_code="TEST")
        ]

        for exc in exceptions:
            assert exc.status_code == 500
