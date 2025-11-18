"""
Product scoring algorithms for SmartAmazon

Implements:
- Hidden Gem Score: Finds great products buried by Amazon's algorithm
- Deal Quality Score: Overall value assessment
- Price Performance Score: How good is the current price
"""
import math
from decimal import Decimal
from typing import Optional
from datetime import datetime, timedelta

from .logging_config import get_logger


logger = get_logger(__name__)


class ProductScorer:
    """
    Calculate various scores for products to surface the best deals
    """

    @staticmethod
    def calculate_hidden_gem_score(
        rating: Optional[Decimal],
        review_count: int,
        search_position: int,
        unit_price: Optional[Decimal],
        category_median_unit_price: Optional[Decimal],
        is_sponsored: bool,
        sponsored_frequency: float = 0.0
    ) -> int:
        """
        Calculate Hidden Gem Score (0-100)

        Finds great products that Amazon buries because they don't buy ads.

        Algorithm from PRD:
        - High rating (4.5+): +30 points
        - High review count (500+): +20 points (log scale)
        - Low search position (page 3+): +variable points
        - Good unit price vs category: +30 points
        - Low sponsored frequency (<10%): +20 points

        Args:
            rating: Product rating (0-5)
            review_count: Number of reviews
            search_position: Position in search results (1-based)
            unit_price: Product unit price
            category_median_unit_price: Category median unit price
            is_sponsored: Whether product is currently sponsored
            sponsored_frequency: How often product appears as sponsored (0-1)

        Returns:
            Score from 0-100
        """
        score = 0

        # Rating bonus (max 30 points)
        if rating and rating >= Decimal('4.5'):
            score += 30
        elif rating and rating >= Decimal('4.0'):
            score += 20
        elif rating and rating >= Decimal('3.5'):
            score += 10

        # Review count bonus (max 20 points, log scale)
        if review_count > 0:
            review_score = min(20, math.log10(review_count) * 5)
            score += review_score

        # Position penalty/bonus (max 30 points)
        # Products buried deep that are actually good get bonusif search_position > 20:  # Page 3+
            # Bonus for being good despite being buried
            position_bonus = min(30, (search_position - 20) * 2)
            score += position_bonus

        # Unit price bonus vs category median (max 30 points)
        if unit_price and category_median_unit_price and category_median_unit_price > 0:
            try:
                # Calculate discount percentage
                discount = float((category_median_unit_price - unit_price) / category_median_unit_price * 100)
                if discount > 0:  # Cheaper than median
                    price_bonus = min(30, discount)
                    score += price_bonus
            except (ValueError, ZeroDivisionError):
                pass

        # Low ad spend bonus (max 20 points)
        if not is_sponsored and sponsored_frequency < 0.1:
            score += 20
        elif not is_sponsored:
            score += 10

        # Cap at 100
        score = min(100, int(score))

        logger.debug(
            f"Hidden gem score calculated: {score}",
            extra={
                'extra_data': {
                    'rating': float(rating) if rating else None,
                    'review_count': review_count,
                    'position': search_position,
                    'score': score
                }
            }
        )

        return score

    @staticmethod
    def calculate_deal_quality_score(
        unit_price: Optional[Decimal],
        category_median_unit_price: Optional[Decimal],
        discount_pct: Optional[Decimal],
        rating: Optional[Decimal],
        review_count: int,
        is_prime: bool
    ) -> int:
        """
        Calculate overall Deal Quality Score (0-100)

        Composite score considering multiple factors:
        - Unit price vs category (40%)
        - Discount percentage (30%)
        - Rating (20%)
        - Review count (10%)

        Args:
            unit_price: Product unit price
            category_median_unit_price: Category median unit price
            discount_pct: Current discount percentage
            rating: Product rating
            review_count: Number of reviews
            is_prime: Prime eligible

        Returns:
            Score from 0-100
        """
        score = 0.0

        # Unit price component (40% weight)
        if unit_price and category_median_unit_price and category_median_unit_price > 0:
            try:
                price_ratio = float(unit_price / category_median_unit_price)
                if price_ratio <= 0.7:  # 30%+ cheaper
                    score += 40
                elif price_ratio <= 0.8:  # 20%+ cheaper
                    score += 35
                elif price_ratio <= 0.9:  # 10%+ cheaper
                    score += 30
                elif price_ratio <= 1.0:  # At or below median
                    score += 25
                else:  # Above median
                    score += max(0, 25 - (price_ratio - 1.0) * 50)
            except (ValueError, ZeroDivisionError):
                pass

        # Discount component (30% weight)
        if discount_pct:
            discount_score = min(30, float(discount_pct) * 0.6)
            score += discount_score

        # Rating component (20% weight)
        if rating:
            rating_normalized = float(rating) / 5.0  # Normalize to 0-1
            score += rating_normalized * 20

        # Review count component (10% weight)
        if review_count > 0:
            review_score = min(10, math.log10(review_count) * 2.5)
            score += review_score

        # Prime bonus (+5 points)
        if is_prime:
            score += 5

        score = min(100, int(score))

        return score

    @staticmethod
    def calculate_price_performance_score(
        current_price: Decimal,
        price_history: list,
        days: int = 90
    ) -> int:
        """
        Calculate how good the current price is based on history (0-100)

        Args:
            current_price: Current product price
            price_history: List of (price, date) tuples
            days: Number of days to consider

        Returns:
            Score from 0-100 (100 = best price ever)
        """
        if not price_history:
            return 50  # Neutral score if no history

        try:
            # Filter to last N days
            cutoff_date = datetime.now() - timedelta(days=days)
            recent_prices = [
                float(price) for price, date in price_history
                if date >= cutoff_date
            ]

            if not recent_prices:
                return 50

            current = float(current_price)
            min_price = min(recent_prices)
            max_price = max(recent_prices)
            avg_price = sum(recent_prices) / len(recent_prices)

            # Calculate position in range
            if max_price == min_price:
                return 100  # Only one price point

            # Score based on how close to minimum
            position = (current - min_price) / (max_price - min_price)

            # Invert so lower price = higher score
            score = int((1 - position) * 100)

            # Bonus if at or near all-time low
            if current <= min_price * 1.02:  # Within 2% of minimum
                score = min(100, score + 10)

            # Penalty if above average
            if current > avg_price:
                penalty = min(20, ((current - avg_price) / avg_price) * 50)
                score -= int(penalty)

            return max(0, min(100, score))

        except (ValueError, ZeroDivisionError, TypeError):
            logger.error("Error calculating price performance score", exc_info=True)
            return 50

    @staticmethod
    def is_true_discount(
        current_price: Decimal,
        list_price: Decimal,
        price_history: list
    ) -> dict:
        """
        Validate if a discount is legitimate or fake MSRP inflation

        Args:
            current_price: Current price
            list_price: Listed "was" price
            price_history: Historical prices

        Returns:
            Dict with validation results
        """
        if not price_history:
            return {
                'is_legitimate': True,  # Benefit of doubt
                'confidence': 'low',
                'message': 'No price history available'
            }

        try:
            historical_prices = [float(p) for p, _ in price_history]
            max_historical = max(historical_prices)
            avg_price_90d = sum(historical_prices) / len(historical_prices)

            current = float(current_price)
            listed = float(list_price)

            # Check if list price ever existed
            if listed > max_historical * 1.1:  # 10% higher than ever sold
                real_discount = ((current / max_historical) - 1) * 100
                return {
                    'is_legitimate': False,
                    'confidence': 'high',
                    'message': f'Fake MSRP. Never sold above ${max_historical:.2f}',
                    'real_discount_pct': real_discount,
                    'inflated_by_pct': ((listed / max_historical) - 1) * 100
                }

            # Calculate real discount vs average
            real_discount = ((avg_price_90d - current) / avg_price_90d) * 100

            if real_discount > 15:  # Significant discount
                return {
                    'is_legitimate': True,
                    'confidence': 'high',
                    'message': f'Legitimate {real_discount:.0f}% discount vs 90-day average',
                    'real_discount_pct': real_discount
                }
            else:
                return {
                    'is_legitimate': True,
                    'confidence': 'medium',
                    'message': 'Modest discount',
                    'real_discount_pct': real_discount
                }

        except (ValueError, ZeroDivisionError, TypeError):
            return {
                'is_legitimate': True,
                'confidence': 'low',
                'message': 'Unable to validate discount'
            }
