"""
Tests for scoring algorithms
"""
import pytest
from decimal import Decimal
from datetime import datetime, timedelta

from app.scoring import ProductScorer


class TestHiddenGemScore:
    """Test hidden gem scoring algorithm"""

    def test_high_rating_high_reviews_buried(self):
        """Test that buried products with great stats get high scores"""
        score = ProductScorer.calculate_hidden_gem_score(
            rating=Decimal("4.7"),
            review_count=5000,
            search_position=50,  # Page 5
            unit_price=Decimal("0.50"),
            category_median_unit_price=Decimal("0.80"),  # 37.5% cheaper
            is_sponsored=False,
            sponsored_frequency=0.05
        )

        # Should get high score for being great but buried
        assert score >= 80
        assert score <= 100

    def test_low_rating_gets_low_score(self):
        """Test that low ratings result in low scores"""
        score = ProductScorer.calculate_hidden_gem_score(
            rating=Decimal("3.0"),
            review_count=100,
            search_position=10,
            unit_price=Decimal("1.00"),
            category_median_unit_price=Decimal("0.80"),  # More expensive
            is_sponsored=True,
            sponsored_frequency=0.8
        )

        assert score < 30

    def test_sponsored_products_penalized(self):
        """Test that sponsored products get lower scores"""
        score_not_sponsored = ProductScorer.calculate_hidden_gem_score(
            rating=Decimal("4.5"),
            review_count=1000,
            search_position=25,
            unit_price=Decimal("0.60"),
            category_median_unit_price=Decimal("0.80"),
            is_sponsored=False,
            sponsored_frequency=0.0
        )

        score_sponsored = ProductScorer.calculate_hidden_gem_score(
            rating=Decimal("4.5"),
            review_count=1000,
            search_position=25,
            unit_price=Decimal("0.60"),
            category_median_unit_price=Decimal("0.80"),
            is_sponsored=True,
            sponsored_frequency=0.9
        )

        assert score_not_sponsored > score_sponsored


class TestDealQualityScore:
    """Test deal quality scoring algorithm"""

    def test_perfect_deal_gets_high_score(self):
        """Test that perfect deals get high scores"""
        score = ProductScorer.calculate_deal_quality_score(
            unit_price=Decimal("0.40"),
            category_median_unit_price=Decimal("0.80"),  # 50% cheaper
            discount_pct=Decimal("50.0"),
            rating=Decimal("5.0"),
            review_count=10000,
            is_prime=True
        )

        assert score >= 90

    def test_average_deal_gets_medium_score(self):
        """Test that average deals get medium scores"""
        score = ProductScorer.calculate_deal_quality_score(
            unit_price=Decimal("0.75"),
            category_median_unit_price=Decimal("0.80"),  # Slightly cheaper
            discount_pct=Decimal("10.0"),
            rating=Decimal("4.0"),
            review_count=500,
            is_prime=True
        )

        assert 40 <= score <= 70

    def test_poor_deal_gets_low_score(self):
        """Test that poor deals get low scores"""
        score = ProductScorer.calculate_deal_quality_score(
            unit_price=Decimal("1.20"),
            category_median_unit_price=Decimal("0.80"),  # 50% more expensive
            discount_pct=Decimal("5.0"),
            rating=Decimal("3.0"),
            review_count=10,
            is_prime=False
        )

        assert score < 40


class TestPricePerformanceScore:
    """Test price performance scoring"""

    def test_at_lowest_price_gets_high_score(self):
        """Test that all-time low prices get high scores"""
        now = datetime.now()
        price_history = [
            (60.0, now - timedelta(days=90)),
            (55.0, now - timedelta(days=60)),
            (52.0, now - timedelta(days=30)),
            (50.0, now - timedelta(days=1)),
        ]

        score = ProductScorer.calculate_price_performance_score(
            current_price=Decimal("49.99"),  # New low
            price_history=price_history,
            days=90
        )

        assert score >= 90

    def test_at_highest_price_gets_low_score(self):
        """Test that high prices get low scores"""
        now = datetime.now()
        price_history = [
            (50.0, now - timedelta(days=90)),
            (52.0, now - timedelta(days=60)),
            (55.0, now - timedelta(days=30)),
            (60.0, now - timedelta(days=1)),
        ]

        score = ProductScorer.calculate_price_performance_score(
            current_price=Decimal("65.00"),  # New high
            price_history=price_history,
            days=90
        )

        assert score <= 20


class TestTrueDiscountValidator:
    """Test discount validation"""

    def test_legitimate_discount_identified(self):
        """Test that legitimate discounts are identified"""
        now = datetime.now()
        price_history = [
            (69.99, now - timedelta(days=90)),
            (69.99, now - timedelta(days=60)),
            (69.99, now - timedelta(days=30)),
        ]

        result = ProductScorer.is_true_discount(
            current_price=Decimal("49.99"),
            list_price=Decimal("69.99"),
            price_history=price_history
        )

        assert result["is_legitimate"] is True
        assert result["confidence"] in ["medium", "high"]

    def test_fake_msrp_detected(self):
        """Test that fake MSRP inflation is detected"""
        now = datetime.now()
        price_history = [
            (50.0, now - timedelta(days=90)),
            (52.0, now - timedelta(days=60)),
            (49.0, now - timedelta(days=30)),
        ]

        result = ProductScorer.is_true_discount(
            current_price=Decimal("49.99"),
            list_price=Decimal("99.99"),  # Fake - never sold this high
            price_history=price_history
        )

        assert result["is_legitimate"] is False
        assert "Fake MSRP" in result["message"]
