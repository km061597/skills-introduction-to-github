"""
Tests for middleware functionality

This module tests:
1. RequestLoggingMiddleware - request logging and tracing
2. RateLimitMiddleware - rate limiting by IP
3. SecurityHeadersMiddleware - security header injection
4. CORSSecurityMiddleware - CORS handling
5. PrometheusMiddleware - metrics collection
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.responses import Response, JSONResponse
from datetime import datetime, timedelta
import time

from app.middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    CORSSecurityMiddleware,
    PrometheusMiddleware
)
from app.exceptions import RateLimitError


@pytest.fixture
def app():
    """Create a test FastAPI application"""
    app = FastAPI()

    @app.get("/test")
    async def test_endpoint():
        return {"message": "success"}

    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}

    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return TestClient(app)


class TestRequestLoggingMiddleware:
    """Tests for RequestLoggingMiddleware"""

    def test_logging_middleware_adds_request_id(self, app, client):
        """Test that logging middleware adds request ID to response"""
        app.add_middleware(RequestLoggingMiddleware)

        response = client.get("/test")

        assert response.status_code == 200
        assert 'X-Request-ID' in response.headers
        assert len(response.headers['X-Request-ID']) > 0

    def test_logging_middleware_unique_request_ids(self, app, client):
        """Test that each request gets a unique request ID"""
        app.add_middleware(RequestLoggingMiddleware)

        response1 = client.get("/test")
        response2 = client.get("/test")

        assert response1.headers['X-Request-ID'] != response2.headers['X-Request-ID']

    @patch('app.middleware.get_logger')
    def test_logging_middleware_logs_request(self, mock_get_logger, app, client):
        """Test that middleware logs incoming requests"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        app.add_middleware(RequestLoggingMiddleware)

        client.get("/test")

        # Should log incoming request and completion
        assert mock_logger.info.call_count >= 2

    @patch('app.middleware.get_logger')
    def test_logging_middleware_logs_errors(self, mock_get_logger, app):
        """Test that middleware logs errors"""
        mock_logger = Mock()
        mock_get_logger.return_value = mock_logger

        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        app.add_middleware(RequestLoggingMiddleware)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/error")

        # Should log error
        assert mock_logger.error.called
        assert response.status_code == 500

    def test_logging_middleware_includes_duration(self, app, client):
        """Test that logged data includes request duration"""
        with patch('app.middleware.get_logger') as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            app.add_middleware(RequestLoggingMiddleware)

            client.get("/test")

            # Check that duration_ms was logged
            calls = mock_logger.info.call_args_list
            assert len(calls) >= 2

            # Check completion log includes duration
            completion_call = calls[-1]
            extra_data = completion_call[1]['extra']['extra_data']
            assert 'duration_ms' in extra_data


class TestRateLimitMiddleware:
    """Tests for RateLimitMiddleware"""

    def test_rate_limit_allows_under_limit(self, app, client):
        """Test that requests under limit are allowed"""
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)

        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

    def test_rate_limit_blocks_over_limit(self, app, client):
        """Test that requests over limit are blocked"""
        app.add_middleware(RateLimitMiddleware, requests_per_minute=5)

        # Make requests up to the limit
        for _ in range(5):
            response = client.get("/test")
            assert response.status_code == 200

        # Next request should be rate limited
        response = client.get("/test")
        assert response.status_code == 429

    def test_rate_limit_headers(self, app, client):
        """Test that rate limit headers are added"""
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)

        response = client.get("/test")

        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-RateLimit-Remaining' in response.headers
        assert 'X-RateLimit-Reset' in response.headers
        assert response.headers['X-RateLimit-Limit'] == '10'

    def test_rate_limit_remaining_decreases(self, app, client):
        """Test that remaining count decreases with each request"""
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)

        response1 = client.get("/test")
        remaining1 = int(response1.headers['X-RateLimit-Remaining'])

        response2 = client.get("/test")
        remaining2 = int(response2.headers['X-RateLimit-Remaining'])

        assert remaining2 < remaining1

    def test_rate_limit_skips_health_check(self, app, client):
        """Test that rate limiting skips health check endpoint"""
        app.add_middleware(RateLimitMiddleware, requests_per_minute=2)

        # Exhaust rate limit on regular endpoint
        client.get("/test")
        client.get("/test")

        # Health check should still work
        response = client.get("/health")
        assert response.status_code == 200

    def test_rate_limit_retry_after_header(self, app, client):
        """Test that rate limited response includes Retry-After header"""
        app.add_middleware(RateLimitMiddleware, requests_per_minute=2)

        # Exhaust limit
        client.get("/test")
        client.get("/test")

        # Get rate limited response
        response = client.get("/test")

        assert response.status_code == 429
        assert 'Retry-After' in response.headers
        assert response.headers['Retry-After'] == '60'

    def test_rate_limit_window_cleanup(self, app):
        """Test that old requests are cleaned from the window"""
        middleware = RateLimitMiddleware(app, requests_per_minute=5)

        # Create mock request
        mock_request = Mock(spec=Request)
        mock_request.client = Mock(host="127.0.0.1")
        mock_request.url = Mock(path="/test")

        # Add old timestamp (2 minutes ago)
        old_time = datetime.now() - timedelta(minutes=2)
        middleware.requests["127.0.0.1"] = [old_time]

        # Mock call_next
        async def mock_call_next(request):
            return Response(status_code=200)

        # Process request (should clean old timestamps)
        import asyncio
        response = asyncio.run(middleware.dispatch(mock_request, mock_call_next))

        # Old timestamp should be cleaned
        assert len(middleware.requests["127.0.0.1"]) == 1  # Only new request
        assert response.status_code == 200


class TestSecurityHeadersMiddleware:
    """Tests for SecurityHeadersMiddleware"""

    def test_security_headers_added(self, app, client):
        """Test that all security headers are added"""
        app.add_middleware(SecurityHeadersMiddleware)

        response = client.get("/test")

        # Check all security headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
        assert 'Strict-Transport-Security' in response.headers
        assert response.headers['Referrer-Policy'] == 'strict-origin-when-cross-origin'
        assert 'Permissions-Policy' in response.headers

    def test_security_headers_hsts(self, app, client):
        """Test HSTS header configuration"""
        app.add_middleware(SecurityHeadersMiddleware)

        response = client.get("/test")

        hsts = response.headers['Strict-Transport-Security']
        assert 'max-age=31536000' in hsts
        assert 'includeSubDomains' in hsts

    def test_security_headers_permissions_policy(self, app, client):
        """Test Permissions-Policy header"""
        app.add_middleware(SecurityHeadersMiddleware)

        response = client.get("/test")

        policy = response.headers['Permissions-Policy']
        assert 'geolocation=()' in policy
        assert 'microphone=()' in policy
        assert 'camera=()' in policy


class TestCORSSecurityMiddleware:
    """Tests for CORSSecurityMiddleware"""

    def test_cors_allowed_origin(self, app, client):
        """Test CORS headers for allowed origin"""
        allowed_origins = ["http://localhost:3000"]
        app.add_middleware(CORSSecurityMiddleware, allowed_origins=allowed_origins)

        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.headers['Access-Control-Allow-Origin'] == "http://localhost:3000"
        assert response.headers['Access-Control-Allow-Credentials'] == 'true'

    def test_cors_blocked_origin(self, app, client):
        """Test that disallowed origin doesn't get CORS headers"""
        allowed_origins = ["http://localhost:3000"]
        app.add_middleware(CORSSecurityMiddleware, allowed_origins=allowed_origins)

        response = client.get(
            "/test",
            headers={"Origin": "http://evil.com"}
        )

        assert 'Access-Control-Allow-Origin' not in response.headers

    def test_cors_no_origin_header(self, app, client):
        """Test request without Origin header"""
        allowed_origins = ["http://localhost:3000"]
        app.add_middleware(CORSSecurityMiddleware, allowed_origins=allowed_origins)

        response = client.get("/test")

        # Should still respond successfully, just no CORS headers
        assert response.status_code == 200
        assert 'Access-Control-Allow-Origin' not in response.headers

    def test_cors_allowed_methods(self, app, client):
        """Test that CORS allows specified methods"""
        allowed_origins = ["http://localhost:3000"]
        app.add_middleware(CORSSecurityMiddleware, allowed_origins=allowed_origins)

        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )

        methods = response.headers['Access-Control-Allow-Methods']
        assert 'GET' in methods
        assert 'POST' in methods
        assert 'PUT' in methods
        assert 'DELETE' in methods

    def test_cors_exposed_headers(self, app, client):
        """Test that CORS exposes specified headers"""
        allowed_origins = ["http://localhost:3000"]
        app.add_middleware(CORSSecurityMiddleware, allowed_origins=allowed_origins)

        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )

        exposed = response.headers['Access-Control-Expose-Headers']
        assert 'X-Request-ID' in exposed
        assert 'X-RateLimit-Limit' in exposed

    def test_cors_default_allowed_origin(self, app, client):
        """Test that default allowed origin is localhost:3000"""
        app.add_middleware(CORSSecurityMiddleware)

        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )

        assert response.headers['Access-Control-Allow-Origin'] == "http://localhost:3000"


class TestPrometheusMiddleware:
    """Tests for PrometheusMiddleware"""

    @patch('app.middleware.PROMETHEUS_AVAILABLE', True)
    @patch('app.middleware.http_requests_total')
    @patch('app.middleware.http_request_duration_seconds')
    @patch('app.middleware.http_requests_in_progress')
    def test_prometheus_records_metrics(
        self,
        mock_in_progress,
        mock_duration,
        mock_total,
        app,
        client
    ):
        """Test that Prometheus middleware records metrics"""
        app.add_middleware(PrometheusMiddleware)

        response = client.get("/test")

        assert response.status_code == 200
        assert mock_in_progress.inc.called
        assert mock_in_progress.dec.called
        assert mock_total.labels.called
        assert mock_duration.labels.called

    @patch('app.middleware.PROMETHEUS_AVAILABLE', False)
    def test_prometheus_graceful_when_unavailable(self, app, client):
        """Test that middleware works when Prometheus is unavailable"""
        app.add_middleware(PrometheusMiddleware)

        response = client.get("/test")

        # Should still work without Prometheus
        assert response.status_code == 200

    @patch('app.middleware.PROMETHEUS_AVAILABLE', True)
    @patch('app.middleware.http_requests_total')
    @patch('app.middleware.http_requests_in_progress')
    def test_prometheus_skips_metrics_endpoint(
        self,
        mock_in_progress,
        mock_total,
        app
    ):
        """Test that /metrics endpoint doesn't record its own metrics"""
        @app.get("/metrics")
        async def metrics():
            return {"metrics": "data"}

        app.add_middleware(PrometheusMiddleware)
        client = TestClient(app)

        response = client.get("/metrics")

        assert response.status_code == 200
        # Should not increment metrics for /metrics endpoint
        assert not mock_in_progress.inc.called

    @patch('app.middleware.PROMETHEUS_AVAILABLE', True)
    @patch('app.middleware.http_requests_total')
    @patch('app.middleware.http_request_duration_seconds')
    @patch('app.middleware.http_requests_in_progress')
    def test_prometheus_records_error_status(
        self,
        mock_in_progress,
        mock_duration,
        mock_total,
        app
    ):
        """Test that Prometheus records error status codes"""
        @app.get("/error")
        async def error_endpoint():
            raise ValueError("Test error")

        app.add_middleware(PrometheusMiddleware)
        client = TestClient(app, raise_server_exceptions=False)

        response = client.get("/error")

        # Should record 500 status
        assert mock_total.labels.called
        # Check that it was called with status 500
        call_kwargs = mock_total.labels.call_args
        assert call_kwargs[1]['status'] == 500


class TestMiddlewareIntegration:
    """Integration tests with multiple middleware"""

    def test_multiple_middleware_stack(self, app, client):
        """Test that multiple middleware work together"""
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(RequestLoggingMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=10)

        response = client.get("/test")

        # Check all middleware effects
        assert response.status_code == 200
        assert 'X-Request-ID' in response.headers  # From logging
        assert 'X-RateLimit-Limit' in response.headers  # From rate limiting
        assert 'X-Frame-Options' in response.headers  # From security headers

    def test_middleware_order_matters(self, app, client):
        """Test that middleware execution order is correct"""
        # Security headers should be last so they're applied to all responses
        app.add_middleware(RateLimitMiddleware, requests_per_minute=2)
        app.add_middleware(SecurityHeadersMiddleware)

        # Exhaust rate limit
        client.get("/test")
        client.get("/test")

        # Rate limited response should still have security headers
        response = client.get("/test")

        assert response.status_code == 429
        assert 'X-Frame-Options' in response.headers

    def test_all_middleware_together(self, app, client):
        """Test all middleware working together"""
        app.add_middleware(PrometheusMiddleware)
        app.add_middleware(CORSSecurityMiddleware, allowed_origins=["http://localhost:3000"])
        app.add_middleware(SecurityHeadersMiddleware)
        app.add_middleware(RateLimitMiddleware, requests_per_minute=100)
        app.add_middleware(RequestLoggingMiddleware)

        response = client.get(
            "/test",
            headers={"Origin": "http://localhost:3000"}
        )

        # Check that all middleware applied
        assert response.status_code == 200
        assert 'X-Request-ID' in response.headers
        assert 'X-RateLimit-Limit' in response.headers
        assert 'X-Frame-Options' in response.headers
        assert 'Access-Control-Allow-Origin' in response.headers
