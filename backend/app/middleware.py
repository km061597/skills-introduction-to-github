"""
Middleware for SmartAmazon API

Includes rate limiting, request logging, and security headers
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
import time
from typing import Callable
import uuid
from collections import defaultdict
from datetime import datetime, timedelta

from .logging_config import set_request_context, clear_request_context, get_logger
from .exceptions import RateLimitError, handle_exception

# Try to import prometheus metrics, but don't fail if not available
try:
    from .monitoring import (
        http_requests_total,
        http_request_duration_seconds,
        http_requests_in_progress
    )
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


logger = get_logger(__name__)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all incoming requests and responses
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID
        request_id = str(uuid.uuid4())
        set_request_context(request_id=request_id)

        # Log incoming request
        start_time = time.time()
        logger.info(
            "Incoming request",
            extra={
                'extra_data': {
                    'method': request.method,
                    'url': str(request.url),
                    'client_ip': request.client.host if request.client else None,
                    'user_agent': request.headers.get('user-agent')
                }
            }
        )

        try:
            # Process request
            response = await call_next(request)

            # Calculate duration
            duration = time.time() - start_time

            # Log response
            logger.info(
                "Request completed",
                extra={
                    'extra_data': {
                        'method': request.method,
                        'url': str(request.url),
                        'status_code': response.status_code,
                        'duration_ms': round(duration * 1000, 2)
                    }
                }
            )

            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id

            return response

        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Request failed",
                extra={
                    'extra_data': {
                        'method': request.method,
                        'url': str(request.url),
                        'duration_ms': round(duration * 1000, 2),
                        'error': str(e)
                    }
                },
                exc_info=True
            )
            raise
        finally:
            clear_request_context()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using token bucket algorithm

    Limits requests per IP address
    """

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)  # IP -> list of request timestamps

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"

        # Skip rate limiting for health checks
        if request.url.path in ["/health", "/api/docs", "/api/redoc"]:
            return await call_next(request)

        # Current time
        now = datetime.now()

        # Clean old requests (older than 1 minute)
        cutoff = now - timedelta(minutes=1)
        self.requests[client_ip] = [
            ts for ts in self.requests[client_ip]
            if ts > cutoff
        ]

        # Check rate limit
        if len(self.requests[client_ip]) >= self.requests_per_minute:
            logger.warning(
                "Rate limit exceeded",
                extra={
                    'extra_data': {
                        'client_ip': client_ip,
                        'requests_count': len(self.requests[client_ip])
                    }
                }
            )
            exc = RateLimitError(retry_after=60)
            return JSONResponse(
                status_code=exc.status_code,
                content=handle_exception(exc),
                headers={"Retry-After": "60"}
            )

        # Add current request
        self.requests[client_ip].append(now)

        # Process request
        response = await call_next(request)

        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.requests[client_ip])
        response.headers['X-RateLimit-Limit'] = str(self.requests_per_minute)
        response.headers['X-RateLimit-Remaining'] = str(max(0, remaining))
        response.headers['X-RateLimit-Reset'] = str(int((now + timedelta(minutes=1)).timestamp()))

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Permissions-Policy'] = 'geolocation=(), microphone=(), camera=()'

        return response


class CORSSecurityMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS with security best practices
    """

    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["http://localhost:3000"]

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        origin = request.headers.get('origin')

        response = await call_next(request)

        # Only add CORS headers if origin is allowed
        if origin in self.allowed_origins:
            response.headers['Access-Control-Allow-Origin'] = origin
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-Request-ID'
            response.headers['Access-Control-Expose-Headers'] = 'X-Request-ID, X-RateLimit-Limit, X-RateLimit-Remaining'
            response.headers['Access-Control-Max-Age'] = '3600'

        return response


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Prometheus metrics collection middleware

    Tracks:
    - Request count by method, endpoint, and status
    - Request duration histogram
    - Requests in progress gauge
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if not PROMETHEUS_AVAILABLE:
            # If Prometheus monitoring is not available, just pass through
            return await call_next(request)

        # Skip metrics for the metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Increment in-progress gauge
        http_requests_in_progress.inc()

        start_time = time.time()
        status_code = 500  # Default to 500 in case of exception

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception as e:
            # Record the exception
            status_code = 500
            raise
        finally:
            # Record metrics
            duration = time.time() - start_time

            # Get endpoint path (remove query params)
            endpoint = request.url.path
            method = request.method

            # Increment request counter
            http_requests_total.labels(
                method=method,
                endpoint=endpoint,
                status=status_code
            ).inc()

            # Record request duration
            http_request_duration_seconds.labels(
                method=method,
                endpoint=endpoint
            ).observe(duration)

            # Decrement in-progress gauge
            http_requests_in_progress.dec()
