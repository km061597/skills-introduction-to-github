"""
Monitoring and observability for SmartAmazon API

Provides Prometheus metrics, health checks, and performance monitoring
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response, Request
from starlette.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import psutil
import os

from .logging_config import get_logger


logger = get_logger(__name__)


# Prometheus Metrics
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint']
)

active_requests = Gauge(
    'active_requests',
    'Number of active requests'
)

database_queries_total = Counter(
    'database_queries_total',
    'Total database queries',
    ['operation']
)

cache_operations_total = Counter(
    'cache_operations_total',
    'Total cache operations',
    ['operation', 'status']
)

scraper_requests_total = Counter(
    'scraper_requests_total',
    'Total scraper requests',
    ['status']
)

system_cpu_usage = Gauge(
    'system_cpu_usage_percent',
    'System CPU usage percentage'
)

system_memory_usage = Gauge(
    'system_memory_usage_percent',
    'System memory usage percentage'
)

application_info = Gauge(
    'application_info',
    'Application information',
    ['version', 'environment']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware to collect Prometheus metrics for all requests
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)

        # Increment active requests
        active_requests.inc()

        # Start timer
        start_time = time.time()

        try:
            # Process request
            response = await call_next(request)

            # Record metrics
            duration = time.time() - start_time

            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)

            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=response.status_code
            ).inc()

            return response

        except Exception as e:
            # Record failed request
            duration = time.time() - start_time

            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)

            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=500
            ).inc()

            raise

        finally:
            # Decrement active requests
            active_requests.dec()


def collect_system_metrics():
    """
    Collect system-level metrics
    """
    try:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        system_cpu_usage.set(cpu_percent)

        # Memory usage
        memory = psutil.virtual_memory()
        system_memory_usage.set(memory.percent)

    except Exception as e:
        logger.error(f"Error collecting system metrics: {e}")


def get_metrics() -> Response:
    """
    Get Prometheus metrics

    Returns:
        Response with metrics in Prometheus format
    """
    # Collect system metrics
    collect_system_metrics()

    # Generate metrics
    metrics = generate_latest()

    return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)


# Health check utilities
class HealthCheck:
    """
    Health check provider for various services
    """

    @staticmethod
    def check_database(db) -> dict:
        """
        Check database connectivity

        Args:
            db: Database session

        Returns:
            Health check result
        """
        try:
            # Try a simple query
            db.execute("SELECT 1")
            return {
                "status": "healthy",
                "message": "Database connection OK"
            }
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Database error: {str(e)}"
            }

    @staticmethod
    def check_redis(cache) -> dict:
        """
        Check Redis connectivity

        Args:
            cache: Cache service

        Returns:
            Health check result
        """
        if not cache.is_available():
            return {
                "status": "unhealthy",
                "message": "Redis unavailable"
            }

        try:
            cache.client.ping()
            stats = cache.get_stats()
            return {
                "status": "healthy",
                "message": "Redis connection OK",
                "stats": stats
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {
                "status": "unhealthy",
                "message": f"Redis error: {str(e)}"
            }

    @staticmethod
    def check_disk_space() -> dict:
        """
        Check disk space

        Returns:
            Health check result
        """
        try:
            disk = psutil.disk_usage('/')
            percent_used = disk.percent

            if percent_used > 90:
                return {
                    "status": "unhealthy",
                    "message": f"Disk space critically low: {percent_used}% used",
                    "percent_used": percent_used
                }
            elif percent_used > 80:
                return {
                    "status": "degraded",
                    "message": f"Disk space running low: {percent_used}% used",
                    "percent_used": percent_used
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Disk space OK: {percent_used}% used",
                    "percent_used": percent_used
                }
        except Exception as e:
            logger.error(f"Disk space check failed: {e}")
            return {
                "status": "unknown",
                "message": f"Could not check disk space: {str(e)}"
            }

    @staticmethod
    def check_memory() -> dict:
        """
        Check memory usage

        Returns:
            Health check result
        """
        try:
            memory = psutil.virtual_memory()
            percent_used = memory.percent

            if percent_used > 90:
                return {
                    "status": "unhealthy",
                    "message": f"Memory critically high: {percent_used}% used",
                    "percent_used": percent_used
                }
            elif percent_used > 80:
                return {
                    "status": "degraded",
                    "message": f"Memory running high: {percent_used}% used",
                    "percent_used": percent_used
                }
            else:
                return {
                    "status": "healthy",
                    "message": f"Memory OK: {percent_used}% used",
                    "percent_used": percent_used
                }
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return {
                "status": "unknown",
                "message": f"Could not check memory: {str(e)}"
            }

    @staticmethod
    def get_comprehensive_health() -> dict:
        """
        Get comprehensive health status

        Returns:
            Complete health check results
        """
        from .cache import get_cache
        from .database import SessionLocal

        db = SessionLocal()
        cache = get_cache()

        try:
            health = {
                "status": "healthy",
                "timestamp": time.time(),
                "version": os.getenv("APP_VERSION", "1.0.0"),
                "environment": os.getenv("ENVIRONMENT", "development"),
                "checks": {
                    "database": HealthCheck.check_database(db),
                    "redis": HealthCheck.check_redis(cache),
                    "disk": HealthCheck.check_disk_space(),
                    "memory": HealthCheck.check_memory()
                }
            }

            # Determine overall status
            statuses = [check["status"] for check in health["checks"].values()]
            if "unhealthy" in statuses:
                health["status"] = "unhealthy"
            elif "degraded" in statuses:
                health["status"] = "degraded"

            return health

        finally:
            db.close()


# Application info metric
def set_app_info(version: str = "1.0.0", environment: str = "development"):
    """
    Set application info metric

    Args:
        version: Application version
        environment: Environment name
    """
    application_info.labels(version=version, environment=environment).set(1)
