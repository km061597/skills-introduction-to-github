"""
Tests for monitoring and observability

This module tests:
1. Prometheus metrics
2. Health checks (database, Redis, disk, memory)
3. System metrics collection
4. Metrics endpoint
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from prometheus_client import REGISTRY

from app.monitoring import (
    collect_system_metrics,
    get_metrics,
    HealthCheck,
    set_app_info
)


class TestSystemMetricsCollection:
    """Tests for collect_system_metrics function"""

    @patch('app.monitoring.psutil.cpu_percent')
    @patch('app.monitoring.psutil.virtual_memory')
    def test_collect_system_metrics_success(self, mock_memory, mock_cpu):
        """Test successful system metrics collection"""
        mock_cpu.return_value = 45.5
        mock_memory.return_value = Mock(percent=62.3)

        collect_system_metrics()

        # Verify metrics were called
        assert mock_cpu.called
        assert mock_memory.called

    @patch('app.monitoring.psutil.cpu_percent')
    @patch('app.monitoring.psutil.virtual_memory')
    def test_collect_system_metrics_handles_error(self, mock_memory, mock_cpu):
        """Test that errors in metrics collection are handled gracefully"""
        mock_cpu.side_effect = Exception("psutil error")

        # Should not raise exception
        collect_system_metrics()


class TestGetMetrics:
    """Tests for get_metrics endpoint"""

    @patch('app.monitoring.collect_system_metrics')
    @patch('app.monitoring.generate_latest')
    def test_get_metrics_success(self, mock_generate, mock_collect):
        """Test successful metrics generation"""
        mock_generate.return_value = b"# Prometheus metrics\n"

        response = get_metrics()

        assert mock_collect.called
        assert mock_generate.called
        assert response.status_code == 200

    @patch('app.monitoring.collect_system_metrics')
    @patch('app.monitoring.generate_latest')
    def test_get_metrics_content_type(self, mock_generate, mock_collect):
        """Test that metrics have correct content type"""
        mock_generate.return_value = b"metrics"

        response = get_metrics()

        # Should have Prometheus content type
        assert "text/plain" in response.media_type or "text" in response.media_type


class TestHealthCheckDatabase:
    """Tests for database health check"""

    def test_check_database_healthy(self):
        """Test database health check when database is healthy"""
        mock_db = Mock()
        mock_db.execute.return_value = None

        result = HealthCheck.check_database(mock_db)

        assert result["status"] == "healthy"
        assert "OK" in result["message"]
        assert mock_db.execute.called

    def test_check_database_unhealthy(self):
        """Test database health check when database fails"""
        mock_db = Mock()
        mock_db.execute.side_effect = Exception("Connection failed")

        result = HealthCheck.check_database(mock_db)

        assert result["status"] == "unhealthy"
        assert "error" in result["message"].lower()

    def test_check_database_connection_error(self):
        """Test database health check with connection error"""
        mock_db = Mock()
        mock_db.execute.side_effect = ConnectionError("Cannot connect")

        result = HealthCheck.check_database(mock_db)

        assert result["status"] == "unhealthy"
        assert "Cannot connect" in result["message"]


class TestHealthCheckRedis:
    """Tests for Redis health check"""

    def test_check_redis_healthy(self):
        """Test Redis health check when Redis is healthy"""
        mock_cache = Mock()
        mock_cache.is_available.return_value = True
        mock_cache.client.ping.return_value = True
        mock_cache.get_stats.return_value = {
            "hits": 1000,
            "misses": 100,
            "hit_rate": 0.91
        }

        result = HealthCheck.check_redis(mock_cache)

        assert result["status"] == "healthy"
        assert "OK" in result["message"]
        assert "stats" in result

    def test_check_redis_unavailable(self):
        """Test Redis health check when Redis is unavailable"""
        mock_cache = Mock()
        mock_cache.is_available.return_value = False

        result = HealthCheck.check_redis(mock_cache)

        assert result["status"] == "unhealthy"
        assert "unavailable" in result["message"]

    def test_check_redis_ping_fails(self):
        """Test Redis health check when ping fails"""
        mock_cache = Mock()
        mock_cache.is_available.return_value = True
        mock_cache.client.ping.side_effect = Exception("Connection timeout")

        result = HealthCheck.check_redis(mock_cache)

        assert result["status"] == "unhealthy"
        assert "error" in result["message"].lower()

    def test_check_redis_includes_stats(self):
        """Test that Redis health check includes statistics"""
        mock_cache = Mock()
        mock_cache.is_available.return_value = True
        mock_cache.client.ping.return_value = True
        mock_cache.get_stats.return_value = {"hits": 100, "misses": 10}

        result = HealthCheck.check_redis(mock_cache)

        assert "stats" in result
        assert result["stats"]["hits"] == 100


class TestHealthCheckDiskSpace:
    """Tests for disk space health check"""

    @patch('app.monitoring.psutil.disk_usage')
    def test_check_disk_space_healthy(self, mock_disk):
        """Test disk space check when space is adequate"""
        mock_disk.return_value = Mock(percent=50.0)

        result = HealthCheck.check_disk_space()

        assert result["status"] == "healthy"
        assert result["percent_used"] == 50.0

    @patch('app.monitoring.psutil.disk_usage')
    def test_check_disk_space_degraded(self, mock_disk):
        """Test disk space check when space is running low"""
        mock_disk.return_value = Mock(percent=85.0)

        result = HealthCheck.check_disk_space()

        assert result["status"] == "degraded"
        assert "running low" in result["message"]
        assert result["percent_used"] == 85.0

    @patch('app.monitoring.psutil.disk_usage')
    def test_check_disk_space_unhealthy(self, mock_disk):
        """Test disk space check when space is critically low"""
        mock_disk.return_value = Mock(percent=95.0)

        result = HealthCheck.check_disk_space()

        assert result["status"] == "unhealthy"
        assert "critically low" in result["message"]
        assert result["percent_used"] == 95.0

    @patch('app.monitoring.psutil.disk_usage')
    def test_check_disk_space_error(self, mock_disk):
        """Test disk space check when check fails"""
        mock_disk.side_effect = Exception("Permission denied")

        result = HealthCheck.check_disk_space()

        assert result["status"] == "unknown"
        assert "Could not check" in result["message"]

    @patch('app.monitoring.psutil.disk_usage')
    def test_check_disk_space_threshold_80(self, mock_disk):
        """Test that 80% threshold triggers degraded status"""
        mock_disk.return_value = Mock(percent=80.1)

        result = HealthCheck.check_disk_space()

        assert result["status"] == "degraded"

    @patch('app.monitoring.psutil.disk_usage')
    def test_check_disk_space_threshold_90(self, mock_disk):
        """Test that 90% threshold triggers unhealthy status"""
        mock_disk.return_value = Mock(percent=90.1)

        result = HealthCheck.check_disk_space()

        assert result["status"] == "unhealthy"


class TestHealthCheckMemory:
    """Tests for memory health check"""

    @patch('app.monitoring.psutil.virtual_memory')
    def test_check_memory_healthy(self, mock_memory):
        """Test memory check when usage is normal"""
        mock_memory.return_value = Mock(percent=60.0)

        result = HealthCheck.check_memory()

        assert result["status"] == "healthy"
        assert result["percent_used"] == 60.0

    @patch('app.monitoring.psutil.virtual_memory')
    def test_check_memory_degraded(self, mock_memory):
        """Test memory check when usage is high"""
        mock_memory.return_value = Mock(percent=85.0)

        result = HealthCheck.check_memory()

        assert result["status"] == "degraded"
        assert "running high" in result["message"]

    @patch('app.monitoring.psutil.virtual_memory')
    def test_check_memory_unhealthy(self, mock_memory):
        """Test memory check when usage is critically high"""
        mock_memory.return_value = Mock(percent=95.0)

        result = HealthCheck.check_memory()

        assert result["status"] == "unhealthy"
        assert "critically high" in result["message"]

    @patch('app.monitoring.psutil.virtual_memory')
    def test_check_memory_error(self, mock_memory):
        """Test memory check when check fails"""
        mock_memory.side_effect = Exception("Cannot read memory info")

        result = HealthCheck.check_memory()

        assert result["status"] == "unknown"

    @patch('app.monitoring.psutil.virtual_memory')
    def test_check_memory_thresholds(self, mock_memory):
        """Test memory check thresholds"""
        # 80% threshold
        mock_memory.return_value = Mock(percent=80.1)
        result = HealthCheck.check_memory()
        assert result["status"] == "degraded"

        # 90% threshold
        mock_memory.return_value = Mock(percent=90.1)
        result = HealthCheck.check_memory()
        assert result["status"] == "unhealthy"


class TestComprehensiveHealth:
    """Tests for get_comprehensive_health method"""

    @patch('app.monitoring.HealthCheck.check_database')
    @patch('app.monitoring.HealthCheck.check_redis')
    @patch('app.monitoring.HealthCheck.check_disk_space')
    @patch('app.monitoring.HealthCheck.check_memory')
    @patch('app.monitoring.SessionLocal')
    @patch('app.monitoring.get_cache')
    @patch.dict('os.environ', {'APP_VERSION': '1.2.3', 'ENVIRONMENT': 'production'})
    def test_comprehensive_health_all_healthy(
        self,
        mock_get_cache,
        mock_session,
        mock_memory_check,
        mock_disk_check,
        mock_redis_check,
        mock_db_check
    ):
        """Test comprehensive health when all checks pass"""
        # Mock all checks to return healthy
        mock_db_check.return_value = {"status": "healthy", "message": "OK"}
        mock_redis_check.return_value = {"status": "healthy", "message": "OK"}
        mock_disk_check.return_value = {"status": "healthy", "message": "OK"}
        mock_memory_check.return_value = {"status": "healthy", "message": "OK"}

        # Mock database session
        mock_db = Mock()
        mock_session.return_value = mock_db

        result = HealthCheck.get_comprehensive_health()

        assert result["status"] == "healthy"
        assert result["version"] == "1.2.3"
        assert result["environment"] == "production"
        assert "checks" in result
        assert "timestamp" in result
        assert mock_db.close.called

    @patch('app.monitoring.HealthCheck.check_database')
    @patch('app.monitoring.HealthCheck.check_redis')
    @patch('app.monitoring.HealthCheck.check_disk_space')
    @patch('app.monitoring.HealthCheck.check_memory')
    @patch('app.monitoring.SessionLocal')
    @patch('app.monitoring.get_cache')
    def test_comprehensive_health_one_unhealthy(
        self,
        mock_get_cache,
        mock_session,
        mock_memory_check,
        mock_disk_check,
        mock_redis_check,
        mock_db_check
    ):
        """Test comprehensive health when one check fails"""
        mock_db_check.return_value = {"status": "unhealthy", "message": "Failed"}
        mock_redis_check.return_value = {"status": "healthy", "message": "OK"}
        mock_disk_check.return_value = {"status": "healthy", "message": "OK"}
        mock_memory_check.return_value = {"status": "healthy", "message": "OK"}

        mock_db = Mock()
        mock_session.return_value = mock_db

        result = HealthCheck.get_comprehensive_health()

        # Overall status should be unhealthy
        assert result["status"] == "unhealthy"
        assert result["checks"]["database"]["status"] == "unhealthy"

    @patch('app.monitoring.HealthCheck.check_database')
    @patch('app.monitoring.HealthCheck.check_redis')
    @patch('app.monitoring.HealthCheck.check_disk_space')
    @patch('app.monitoring.HealthCheck.check_memory')
    @patch('app.monitoring.SessionLocal')
    @patch('app.monitoring.get_cache')
    def test_comprehensive_health_degraded(
        self,
        mock_get_cache,
        mock_session,
        mock_memory_check,
        mock_disk_check,
        mock_redis_check,
        mock_db_check
    ):
        """Test comprehensive health with degraded services"""
        mock_db_check.return_value = {"status": "healthy", "message": "OK"}
        mock_redis_check.return_value = {"status": "healthy", "message": "OK"}
        mock_disk_check.return_value = {"status": "degraded", "message": "Low space"}
        mock_memory_check.return_value = {"status": "healthy", "message": "OK"}

        mock_db = Mock()
        mock_session.return_value = mock_db

        result = HealthCheck.get_comprehensive_health()

        # Overall status should be degraded
        assert result["status"] == "degraded"

    @patch('app.monitoring.HealthCheck.check_database')
    @patch('app.monitoring.HealthCheck.check_redis')
    @patch('app.monitoring.HealthCheck.check_disk_space')
    @patch('app.monitoring.HealthCheck.check_memory')
    @patch('app.monitoring.SessionLocal')
    @patch('app.monitoring.get_cache')
    def test_comprehensive_health_includes_all_checks(
        self,
        mock_get_cache,
        mock_session,
        mock_memory_check,
        mock_disk_check,
        mock_redis_check,
        mock_db_check
    ):
        """Test that comprehensive health includes all check results"""
        mock_db_check.return_value = {"status": "healthy"}
        mock_redis_check.return_value = {"status": "healthy"}
        mock_disk_check.return_value = {"status": "healthy"}
        mock_memory_check.return_value = {"status": "healthy"}

        mock_db = Mock()
        mock_session.return_value = mock_db

        result = HealthCheck.get_comprehensive_health()

        assert "database" in result["checks"]
        assert "redis" in result["checks"]
        assert "disk" in result["checks"]
        assert "memory" in result["checks"]

    @patch('app.monitoring.HealthCheck.check_database')
    @patch('app.monitoring.HealthCheck.check_redis')
    @patch('app.monitoring.HealthCheck.check_disk_space')
    @patch('app.monitoring.HealthCheck.check_memory')
    @patch('app.monitoring.SessionLocal')
    @patch('app.monitoring.get_cache')
    def test_comprehensive_health_closes_db(
        self,
        mock_get_cache,
        mock_session,
        mock_memory_check,
        mock_disk_check,
        mock_redis_check,
        mock_db_check
    ):
        """Test that database session is closed after health check"""
        mock_db_check.return_value = {"status": "healthy"}
        mock_redis_check.return_value = {"status": "healthy"}
        mock_disk_check.return_value = {"status": "healthy"}
        mock_memory_check.return_value = {"status": "healthy"}

        mock_db = Mock()
        mock_session.return_value = mock_db

        HealthCheck.get_comprehensive_health()

        # Verify database session was closed
        assert mock_db.close.called


class TestSetAppInfo:
    """Tests for set_app_info function"""

    def test_set_app_info_default_values(self):
        """Test setting app info with default values"""
        set_app_info()

        # Should not raise exception

    def test_set_app_info_custom_values(self):
        """Test setting app info with custom values"""
        set_app_info(version="2.0.0", environment="staging")

        # Should not raise exception

    def test_set_app_info_production(self):
        """Test setting app info for production"""
        set_app_info(version="1.0.0", environment="production")

        # Should not raise exception


class TestPrometheusMetrics:
    """Tests for Prometheus metrics"""

    def test_http_requests_total_exists(self):
        """Test that http_requests_total metric exists"""
        from app.monitoring import http_requests_total

        assert http_requests_total is not None
        assert http_requests_total._name == 'http_requests_total'

    def test_http_request_duration_exists(self):
        """Test that http_request_duration_seconds metric exists"""
        from app.monitoring import http_request_duration_seconds

        assert http_request_duration_seconds is not None
        assert http_request_duration_seconds._name == 'http_request_duration_seconds'

    def test_active_requests_exists(self):
        """Test that active_requests metric exists"""
        from app.monitoring import active_requests

        assert active_requests is not None
        assert active_requests._name == 'active_requests'

    def test_database_queries_total_exists(self):
        """Test that database_queries_total metric exists"""
        from app.monitoring import database_queries_total

        assert database_queries_total is not None
        assert database_queries_total._name == 'database_queries_total'

    def test_cache_operations_total_exists(self):
        """Test that cache_operations_total metric exists"""
        from app.monitoring import cache_operations_total

        assert cache_operations_total is not None
        assert cache_operations_total._name == 'cache_operations_total'

    def test_system_cpu_usage_exists(self):
        """Test that system_cpu_usage metric exists"""
        from app.monitoring import system_cpu_usage

        assert system_cpu_usage is not None
        assert system_cpu_usage._name == 'system_cpu_usage_percent'

    def test_system_memory_usage_exists(self):
        """Test that system_memory_usage metric exists"""
        from app.monitoring import system_memory_usage

        assert system_memory_usage is not None
        assert system_memory_usage._name == 'system_memory_usage_percent'


class TestMetricLabels:
    """Tests for metric labels"""

    def test_http_requests_has_correct_labels(self):
        """Test that http_requests_total has correct label names"""
        from app.monitoring import http_requests_total

        # Get label names from metric
        label_names = http_requests_total._labelnames
        assert 'method' in label_names
        assert 'endpoint' in label_names
        assert 'status' in label_names

    def test_http_duration_has_correct_labels(self):
        """Test that http_request_duration_seconds has correct labels"""
        from app.monitoring import http_request_duration_seconds

        label_names = http_request_duration_seconds._labelnames
        assert 'method' in label_names
        assert 'endpoint' in label_names

    def test_database_queries_has_correct_labels(self):
        """Test that database_queries_total has correct labels"""
        from app.monitoring import database_queries_total

        label_names = database_queries_total._labelnames
        assert 'operation' in label_names

    def test_cache_operations_has_correct_labels(self):
        """Test that cache_operations_total has correct labels"""
        from app.monitoring import cache_operations_total

        label_names = cache_operations_total._labelnames
        assert 'operation' in label_names
        assert 'status' in label_names
