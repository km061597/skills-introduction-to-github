"""
Tests for price history service

This module tests:
1. Recording price history
2. Retrieving price history
3. Calculating price statistics
4. Finding best price times
5. Detecting price drop alerts
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from unittest.mock import Mock, MagicMock

from app.services.price_history import PriceHistoryService
from app.models import Product, PriceHistory


class TestRecordPrice:
    """Tests for record_price method"""

    def test_record_price_new_product(self, db_session):
        """Test recording first price for a product"""
        # Create a product
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Record price
        price_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("54.99"),
            unit_price=Decimal("0.69"),
            is_prime=True
        )

        assert price_record is not None
        assert price_record.product_id == product.id
        assert price_record.price == Decimal("54.99")
        assert price_record.unit_price == Decimal("0.69")
        assert price_record.is_prime is True

    def test_record_price_unchanged(self, db_session):
        """Test that unchanged price within 24h is not recorded"""
        # Create product and initial price
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Record first price
        first_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("54.99")
        )

        # Try to record same price immediately
        second_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("54.99")
        )

        # Should return the same record
        assert first_record.id == second_record.id

    def test_record_price_changed(self, db_session):
        """Test that changed price is recorded"""
        # Create product and initial price
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Record first price
        first_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("54.99")
        )

        # Record different price
        second_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("49.99")
        )

        # Should create new record
        assert first_record.id != second_record.id
        assert second_record.price == Decimal("49.99")

    def test_record_price_with_all_fields(self, db_session):
        """Test recording price with all optional fields"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        price_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("54.99"),
            unit_price=Decimal("0.69"),
            is_prime=True,
            is_sponsored=True,
            in_stock=False
        )

        assert price_record.price == Decimal("54.99")
        assert price_record.unit_price == Decimal("0.69")
        assert price_record.is_prime is True
        assert price_record.is_sponsored is True
        assert price_record.in_stock is False

    def test_record_price_small_change(self, db_session):
        """Test that very small price changes (< $0.01) are not recorded"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Record first price
        first_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("54.99")
        )

        # Try to record price with tiny difference
        second_record = PriceHistoryService.record_price(
            db=db_session,
            product_id=product.id,
            price=Decimal("54.995")
        )

        # Should return same record (change < 0.01)
        assert first_record.id == second_record.id


class TestGetPriceHistory:
    """Tests for get_price_history method"""

    def test_get_price_history_empty(self, db_session):
        """Test getting price history for product with no history"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        history = PriceHistoryService.get_price_history(
            db=db_session,
            product_id=product.id,
            days=30
        )

        assert history == []

    def test_get_price_history_with_records(self, db_session):
        """Test getting price history with multiple records"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Create multiple price records
        prices = [
            (Decimal("54.99"), datetime.now() - timedelta(days=5)),
            (Decimal("49.99"), datetime.now() - timedelta(days=3)),
            (Decimal("44.99"), datetime.now() - timedelta(days=1))
        ]

        for price, timestamp in prices:
            record = PriceHistory(
                product_id=product.id,
                price=price,
                recorded_at=timestamp
            )
            db_session.add(record)
        db_session.commit()

        history = PriceHistoryService.get_price_history(
            db=db_session,
            product_id=product.id,
            days=30
        )

        assert len(history) == 3
        # Should be ordered by date ascending
        assert history[0]["price"] == 54.99
        assert history[-1]["price"] == 44.99

    def test_get_price_history_respects_days_filter(self, db_session):
        """Test that days parameter filters old records"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Create records: one recent, one old
        recent_record = PriceHistory(
            product_id=product.id,
            price=Decimal("49.99"),
            recorded_at=datetime.now() - timedelta(days=5)
        )
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("54.99"),
            recorded_at=datetime.now() - timedelta(days=40)
        )
        db_session.add_all([recent_record, old_record])
        db_session.commit()

        # Get history for last 30 days
        history = PriceHistoryService.get_price_history(
            db=db_session,
            product_id=product.id,
            days=30
        )

        # Should only include recent record
        assert len(history) == 1
        assert history[0]["price"] == 49.99

    def test_get_price_history_includes_all_fields(self, db_session):
        """Test that history includes all record fields"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        record = PriceHistory(
            product_id=product.id,
            price=Decimal("54.99"),
            unit_price=Decimal("0.69"),
            is_prime=True,
            is_sponsored=False,
            in_stock=True,
            recorded_at=datetime.now()
        )
        db_session.add(record)
        db_session.commit()

        history = PriceHistoryService.get_price_history(
            db=db_session,
            product_id=product.id
        )

        assert len(history) == 1
        assert "date" in history[0]
        assert "price" in history[0]
        assert "unit_price" in history[0]
        assert "is_prime" in history[0]
        assert "is_sponsored" in history[0]
        assert "in_stock" in history[0]


class TestGetPriceStatistics:
    """Tests for get_price_statistics method"""

    def test_price_statistics_no_data(self, db_session):
        """Test price statistics with no price history"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        stats = PriceHistoryService.get_price_statistics(
            db=db_session,
            product_id=product.id,
            days=30
        )

        assert stats["min_price"] is None
        assert stats["max_price"] is None
        assert stats["avg_price"] is None
        assert stats["data_points"] == 0

    def test_price_statistics_calculates_correctly(self, db_session):
        """Test price statistics calculations"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Create price records
        prices = [Decimal("50.00"), Decimal("60.00"), Decimal("40.00")]
        for i, price in enumerate(prices):
            record = PriceHistory(
                product_id=product.id,
                price=price,
                recorded_at=datetime.now() - timedelta(days=i)
            )
            db_session.add(record)
        db_session.commit()

        stats = PriceHistoryService.get_price_statistics(
            db=db_session,
            product_id=product.id,
            days=30
        )

        assert stats["min_price"] == 40.00
        assert stats["max_price"] == 60.00
        assert stats["avg_price"] == 50.00  # (50+60+40)/3
        assert stats["data_points"] == 3

    def test_price_statistics_current_price(self, db_session):
        """Test that statistics includes current price"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Add older price
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("60.00"),
            recorded_at=datetime.now() - timedelta(days=5)
        )
        # Add current price
        current_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([old_record, current_record])
        db_session.commit()

        stats = PriceHistoryService.get_price_statistics(
            db=db_session,
            product_id=product.id,
            days=30
        )

        assert stats["current_price"] == 50.00

    def test_price_statistics_is_lowest(self, db_session):
        """Test is_lowest flag when current price is lowest"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Current price is lowest
        record1 = PriceHistory(
            product_id=product.id,
            price=Decimal("60.00"),
            recorded_at=datetime.now() - timedelta(days=5)
        )
        record2 = PriceHistory(
            product_id=product.id,
            price=Decimal("45.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([record1, record2])
        db_session.commit()

        stats = PriceHistoryService.get_price_statistics(
            db=db_session,
            product_id=product.id
        )

        assert stats["is_lowest"] is True
        assert stats["is_highest"] is False

    def test_price_statistics_trend(self, db_session):
        """Test price trend calculation"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Price dropped from 60 to 50 (>5% drop = "down")
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("60.00"),
            recorded_at=datetime.now() - timedelta(days=10)
        )
        current_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([old_record, current_record])
        db_session.commit()

        stats = PriceHistoryService.get_price_statistics(
            db=db_session,
            product_id=product.id
        )

        # 60 -> 50 is -16.67% change
        assert stats["price_change_pct"] < -5
        assert stats["trend"] == "down"

    def test_price_statistics_stable_trend(self, db_session):
        """Test stable price trend"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Price changed slightly (within -5% to +5% = "stable")
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now() - timedelta(days=10)
        )
        current_record = PriceHistory(
            product_id=product.id,
            price=Decimal("51.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([old_record, current_record])
        db_session.commit()

        stats = PriceHistoryService.get_price_statistics(
            db=db_session,
            product_id=product.id
        )

        # 50 -> 51 is +2% change
        assert stats["trend"] == "stable"


class TestGetBestPriceTime:
    """Tests for get_best_price_time method"""

    def test_best_price_time_no_data(self, db_session):
        """Test best price time with no history"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        result = PriceHistoryService.get_best_price_time(
            db=db_session,
            product_id=product.id
        )

        assert result["best_price"] is None
        assert result["best_price_date"] is None
        assert result["days_ago"] is None

    def test_best_price_time_finds_lowest(self, db_session):
        """Test that best price time finds the lowest price"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Create price records with different prices
        prices_and_days = [
            (Decimal("60.00"), 10),
            (Decimal("45.00"), 5),  # Lowest
            (Decimal("55.00"), 1)
        ]

        for price, days_ago in prices_and_days:
            record = PriceHistory(
                product_id=product.id,
                price=price,
                recorded_at=datetime.now() - timedelta(days=days_ago)
            )
            db_session.add(record)
        db_session.commit()

        result = PriceHistoryService.get_best_price_time(
            db=db_session,
            product_id=product.id
        )

        assert result["best_price"] == 45.00
        assert result["days_ago"] == 5

    def test_best_price_time_calculates_savings(self, db_session):
        """Test savings calculation from current price"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Best price was 40, current is 50
        best_record = PriceHistory(
            product_id=product.id,
            price=Decimal("40.00"),
            recorded_at=datetime.now() - timedelta(days=10)
        )
        current_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([best_record, current_record])
        db_session.commit()

        result = PriceHistoryService.get_best_price_time(
            db=db_session,
            product_id=product.id
        )

        # Savings = current - best = 50 - 40 = 10
        assert result["savings_from_current"] == 10.00

    def test_best_price_time_recommendation_buy_now(self, db_session):
        """Test 'Buy now' recommendation when at/near best price"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Best price was 50 recently (< 7 days), current is 50.50
        best_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now() - timedelta(days=3)
        )
        current_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.50"),
            recorded_at=datetime.now()
        )
        db_session.add_all([best_record, current_record])
        db_session.commit()

        result = PriceHistoryService.get_best_price_time(
            db=db_session,
            product_id=product.id
        )

        # Recent best price (<7 days) + small difference (<$1)
        assert result["recommendation"] == "Buy now!"

    def test_best_price_time_recommendation_wait(self, db_session):
        """Test 'Wait' recommendation when price is high"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Best price was 40, current is 50 (savings > $5)
        best_record = PriceHistory(
            product_id=product.id,
            price=Decimal("40.00"),
            recorded_at=datetime.now() - timedelta(days=20)
        )
        current_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([best_record, current_record])
        db_session.commit()

        result = PriceHistoryService.get_best_price_time(
            db=db_session,
            product_id=product.id
        )

        # Savings > $5 should recommend waiting
        assert result["recommendation"] == "Wait for better price"


class TestGetPriceDropAlerts:
    """Tests for get_price_drop_alerts method"""

    def test_price_drop_alerts_no_drops(self, db_session):
        """Test when there are no price drops"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Price went up, not down
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now() - timedelta(hours=12)
        )
        new_record = PriceHistory(
            product_id=product.id,
            price=Decimal("60.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([old_record, new_record])
        db_session.commit()

        alerts = PriceHistoryService.get_price_drop_alerts(
            db=db_session,
            min_drop_percentage=10.0,
            hours=24
        )

        assert len(alerts) == 0

    def test_price_drop_alerts_finds_drops(self, db_session):
        """Test finding products with price drops"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Price dropped 20% (from 50 to 40)
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now() - timedelta(hours=12)
        )
        new_record = PriceHistory(
            product_id=product.id,
            price=Decimal("40.00"),
            recorded_at=datetime.now()
        )
        db_session.add_all([old_record, new_record])
        db_session.commit()

        alerts = PriceHistoryService.get_price_drop_alerts(
            db=db_session,
            min_drop_percentage=10.0,
            hours=24
        )

        assert len(alerts) == 1
        assert alerts[0]["asin"] == "TEST123"
        assert alerts[0]["old_price"] == 50.00
        assert alerts[0]["new_price"] == 40.00
        assert alerts[0]["drop_percentage"] == 20.00
        assert alerts[0]["savings"] == 10.00

    def test_price_drop_alerts_respects_threshold(self, db_session):
        """Test that minimum drop percentage is respected"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Price dropped 5% (from 50 to 47.50)
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("50.00"),
            recorded_at=datetime.now() - timedelta(hours=12)
        )
        new_record = PriceHistory(
            product_id=product.id,
            price=Decimal("47.50"),
            recorded_at=datetime.now()
        )
        db_session.add_all([old_record, new_record])
        db_session.commit()

        # Look for drops >= 10%
        alerts = PriceHistoryService.get_price_drop_alerts(
            db=db_session,
            min_drop_percentage=10.0,
            hours=24
        )

        # 5% drop should not trigger 10% threshold
        assert len(alerts) == 0

    def test_price_drop_alerts_sorted_by_percentage(self, db_session):
        """Test that alerts are sorted by drop percentage"""
        # Create two products with different drop percentages
        product1 = Product(asin="TEST1", title="Product 1")
        product2 = Product(asin="TEST2", title="Product 2")
        db_session.add_all([product1, product2])
        db_session.commit()

        # Product 1: 20% drop
        db_session.add_all([
            PriceHistory(
                product_id=product1.id,
                price=Decimal("50.00"),
                recorded_at=datetime.now() - timedelta(hours=12)
            ),
            PriceHistory(
                product_id=product1.id,
                price=Decimal("40.00"),
                recorded_at=datetime.now()
            )
        ])

        # Product 2: 30% drop
        db_session.add_all([
            PriceHistory(
                product_id=product2.id,
                price=Decimal("60.00"),
                recorded_at=datetime.now() - timedelta(hours=12)
            ),
            PriceHistory(
                product_id=product2.id,
                price=Decimal("42.00"),
                recorded_at=datetime.now()
            )
        ])
        db_session.commit()

        alerts = PriceHistoryService.get_price_drop_alerts(
            db=db_session,
            min_drop_percentage=10.0,
            hours=24
        )

        # Should be sorted by drop percentage (highest first)
        assert len(alerts) == 2
        assert alerts[0]["asin"] == "TEST2"  # 30% drop
        assert alerts[1]["asin"] == "TEST1"  # 20% drop

    def test_price_drop_alerts_respects_time_window(self, db_session):
        """Test that time window parameter is respected"""
        product = Product(asin="TEST123", title="Test Product")
        db_session.add(product)
        db_session.commit()

        # Price drop happened 48 hours ago
        old_record = PriceHistory(
            product_id=product.id,
            price=Decimal("60.00"),
            recorded_at=datetime.now() - timedelta(hours=50)
        )
        new_record = PriceHistory(
            product_id=product.id,
            price=Decimal("40.00"),
            recorded_at=datetime.now() - timedelta(hours=48)
        )
        db_session.add_all([old_record, new_record])
        db_session.commit()

        # Look for drops in last 24 hours
        alerts = PriceHistoryService.get_price_drop_alerts(
            db=db_session,
            min_drop_percentage=10.0,
            hours=24
        )

        # Drop happened outside time window
        assert len(alerts) == 0
