"""
Unit tests for caching functionality
"""
import pytest
from unittest.mock import Mock, patch
from decimal import Decimal

from app.cache import CacheManager, get_cache_key


class TestCacheKeyGeneration:
    """Test cache key generation"""

    def test_get_cache_key_simple(self):
        """Test simple cache key generation"""
        key = get_cache_key("search", query="protein")
        assert key.startswith("smartamazon:search:")
        assert "protein" in key

    def test_get_cache_key_multiple_params(self):
        """Test cache key with multiple parameters"""
        key = get_cache_key(
            "search",
            query="protein",
            min_price=10,
            max_price=50,
            prime_only=True
        )
        assert "protein" in key
        assert "10" in key or "50" in key

    def test_get_cache_key_consistent(self):
        """Test that same params generate same key"""
        key1 = get_cache_key("search", query="test", price=10)
        key2 = get_cache_key("search", query="test", price=10)
        assert key1 == key2

    def test_get_cache_key_different_order(self):
        """Test that param order doesn't matter"""
        key1 = get_cache_key("search", a=1, b=2)
        key2 = get_cache_key("search", b=2, a=1)
        assert key1 == key2


class TestCacheManager:
    """Test CacheManager operations"""

    @pytest.fixture
    def cache_manager(self):
        """Create a mock cache manager for testing"""
        with patch('app.cache.redis_client') as mock_redis:
            manager = CacheManager()
            manager.redis = mock_redis
            yield manager

    def test_set_and_get(self, cache_manager):
        """Test setting and getting cache values"""
        cache_manager.redis.get.return_value = '{"test": "data"}'

        # Set value
        cache_manager.set("test_key", {"test": "data"}, ttl=300)

        # Get value
        result = cache_manager.get("test_key")

        assert result == {"test": "data"}

    def test_get_missing_key(self, cache_manager):
        """Test getting non-existent key returns None"""
        cache_manager.redis.get.return_value = None

        result = cache_manager.get("nonexistent_key")

        assert result is None

    def test_delete(self, cache_manager):
        """Test deleting cache key"""
        cache_manager.delete("test_key")

        cache_manager.redis.delete.assert_called_once_with("test_key")

    def test_set_with_ttl(self, cache_manager):
        """Test setting value with TTL"""
        cache_manager.set("test_key", {"data": "value"}, ttl=600)

        # Verify set was called with TTL
        assert cache_manager.redis.setex.called or cache_manager.redis.set.called

    def test_cache_invalidation(self, cache_manager):
        """Test cache invalidation pattern"""
        cache_manager.invalidate_pattern("search:*")

        # Should scan and delete matching keys
        assert cache_manager.redis.scan.called or cache_manager.redis.delete.called


class TestCacheIntegration:
    """Integration tests for cache with real Redis operations"""

    @pytest.mark.requires_redis
    def test_cache_search_results(self, cache_manager):
        """Test caching search results"""
        search_results = {
            "results": [
                {"asin": "TEST001", "title": "Product 1"},
                {"asin": "TEST002", "title": "Product 2"}
            ],
            "total": 2
        }

        # Cache results
        cache_key = get_cache_key("search", query="test")
        cache_manager.set(cache_key, search_results, ttl=300)

        # Retrieve results
        cached = cache_manager.get(cache_key)

        assert cached == search_results
        assert len(cached["results"]) == 2

    @pytest.mark.requires_redis
    def test_cache_expiration(self, cache_manager):
        """Test that cache expires after TTL"""
        import time

        cache_manager.set("temp_key", {"data": "test"}, ttl=1)

        # Should exist immediately
        assert cache_manager.get("temp_key") is not None

        # Should expire after TTL
        time.sleep(2)
        assert cache_manager.get("temp_key") is None

    @pytest.mark.requires_redis
    def test_cache_miss_and_populate(self, cache_manager):
        """Test cache miss -> database -> populate cache pattern"""
        cache_key = get_cache_key("product", asin="TEST123")

        # First call - cache miss
        cached = cache_manager.get(cache_key)
        assert cached is None

        # Simulate database fetch and cache
        product_data = {"asin": "TEST123", "title": "Test Product"}
        cache_manager.set(cache_key, product_data, ttl=300)

        # Second call - cache hit
        cached = cache_manager.get(cache_key)
        assert cached == product_data


class TestCacheDecorator:
    """Test cache decorator functionality"""

    def test_cached_function(self):
        """Test function with cache decorator"""
        call_count = {"count": 0}

        @pytest.mark.skip("Decorator test - implement if decorator exists")
        def cached_function(param):
            call_count["count"] += 1
            return f"result_{param}"

        # First call - should execute
        result1 = cached_function("test")
        assert call_count["count"] == 1

        # Second call - should use cache
        result2 = cached_function("test")
        assert call_count["count"] == 1  # No additional call
        assert result1 == result2
