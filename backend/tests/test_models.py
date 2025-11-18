"""
Unit tests for database models
"""
import pytest
from decimal import Decimal
from datetime import datetime

from app.models import Product, PriceHistory, CategoryStats, SearchCache, UserSearch


class TestProductModel:
    """Test Product model"""

    def test_create_product(self, db_session):
        """Test creating a product"""
        product = Product(
            asin="TEST123",
            title="Test Product",
            brand="TestBrand",
            category="Test Category",
            current_price=Decimal("29.99"),
            list_price=Decimal("39.99"),
            unit_price=Decimal("0.50"),
            unit_type="oz",
            quantity=Decimal("60"),
            discount_pct=Decimal("25.0"),
            rating=Decimal("4.5"),
            review_count=100,
            is_prime=True,
            is_sponsored=False,
            in_stock=True
        )

        db_session.add(product)
        db_session.commit()

        assert product.asin == "TEST123"
        assert product.title == "Test Product"
        assert product.discount_pct == Decimal("25.0")

    def test_product_price_history_relationship(self, db_session):
        """Test product-price_history relationship"""
        product = Product(
            asin="TEST456",
            title="Test Product 2",
            current_price=Decimal("19.99")
        )
        db_session.add(product)
        db_session.commit()

        # Add price history
        history = PriceHistory(
            asin="TEST456",
            price=Decimal("24.99"),
            unit_price=Decimal("0.60")
        )
        db_session.add(history)
        db_session.commit()

        # Check relationship
        assert len(product.price_history) == 1
        assert product.price_history[0].price == Decimal("24.99")

    def test_product_timestamps(self, db_session):
        """Test that timestamps are automatically set"""
        product = Product(
            asin="TEST789",
            title="Test Product 3",
            current_price=Decimal("9.99")
        )
        db_session.add(product)
        db_session.commit()

        assert product.created_at is not None
        assert product.updated_at is not None
        assert isinstance(product.created_at, datetime)


class TestPriceHistoryModel:
    """Test PriceHistory model"""

    def test_create_price_history(self, db_session, sample_products):
        """Test creating price history entry"""
        history = PriceHistory(
            asin="TEST001",
            price=Decimal("54.99"),
            unit_price=Decimal("0.69")
        )

        db_session.add(history)
        db_session.commit()

        assert history.id is not None
        assert history.asin == "TEST001"
        assert history.price == Decimal("54.99")

    def test_price_history_timestamp(self, db_session, sample_products):
        """Test price history has recorded_at timestamp"""
        history = PriceHistory(
            asin="TEST001",
            price=Decimal("49.99")
        )

        db_session.add(history)
        db_session.commit()

        assert history.recorded_at is not None
        assert isinstance(history.recorded_at, datetime)


class TestCategoryStatsModel:
    """Test CategoryStats model"""

    def test_create_category_stats(self, db_session):
        """Test creating category statistics"""
        stats = CategoryStats(
            category="Protein Powder",
            median_price=Decimal("49.99"),
            median_unit_price=Decimal("0.75"),
            avg_rating=Decimal("4.5"),
            product_count=100
        )

        db_session.add(stats)
        db_session.commit()

        assert stats.category == "Protein Powder"
        assert stats.product_count == 100

    def test_category_stats_last_updated(self, db_session):
        """Test category stats has last_updated timestamp"""
        stats = CategoryStats(
            category="Vitamins",
            product_count=50
        )

        db_session.add(stats)
        db_session.commit()

        assert stats.last_updated is not None


class TestSearchCacheModel:
    """Test SearchCache model"""

    def test_create_search_cache(self, db_session):
        """Test creating search cache entry"""
        from datetime import timedelta

        cache = SearchCache(
            query_hash="abc123def456",
            results={"products": []},
            total_count=0,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )

        db_session.add(cache)
        db_session.commit()

        assert cache.query_hash == "abc123def456"
        assert cache.total_count == 0

    def test_search_cache_json_results(self, db_session):
        """Test that cache can store JSON results"""
        from datetime import timedelta

        cache = SearchCache(
            query_hash="test_query",
            results={
                "products": [
                    {"asin": "TEST001", "title": "Product 1"},
                    {"asin": "TEST002", "title": "Product 2"}
                ],
                "filters": {"min_price": 10, "max_price": 50}
            },
            total_count=2,
            expires_at=datetime.utcnow() + timedelta(hours=1)
        )

        db_session.add(cache)
        db_session.commit()

        assert len(cache.results["products"]) == 2
        assert cache.results["filters"]["min_price"] == 10


class TestUserSearchModel:
    """Test UserSearch model"""

    def test_create_user_search(self, db_session):
        """Test creating saved user search"""
        search = UserSearch(
            user_id=1,
            name="My Protein Search",
            query="protein powder",
            filters={"min_rating": 4.5, "prime_only": True}
        )

        db_session.add(search)
        db_session.commit()

        assert search.name == "My Protein Search"
        assert search.filters["min_rating"] == 4.5

    def test_user_search_timestamp(self, db_session):
        """Test user search has created_at timestamp"""
        search = UserSearch(
            user_id=1,
            name="Test Search",
            query="test"
        )

        db_session.add(search)
        db_session.commit()

        assert search.created_at is not None
