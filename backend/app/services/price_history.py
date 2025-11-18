"""
Price History Service

Tracks and analyzes product price changes over time
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from ..models import Product, PriceHistory
from ..database import get_db
from ..logging_config import get_logger

logger = get_logger(__name__)


class PriceHistoryService:
    """
    Service for managing product price history
    """

    @staticmethod
    def record_price(
        db: Session,
        product_id: int,
        price: Decimal,
        unit_price: Optional[Decimal] = None,
        is_prime: bool = False,
        is_sponsored: bool = False,
        in_stock: bool = True
    ) -> PriceHistory:
        """
        Record a price observation for a product

        Args:
            db: Database session
            product_id: Product ID
            price: Current price
            unit_price: Unit price ($/oz, $/count, etc.)
            is_prime: Prime eligible
            is_sponsored: Sponsored listing
            in_stock: In stock status

        Returns:
            Created PriceHistory record
        """
        # Get product to get ASIN
        product = db.query(Product).filter(Product.id == product_id).first()
        if not product:
            raise ValueError(f"Product with id {product_id} not found")

        # Check if price changed from last record
        last_record = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).order_by(PriceHistory.recorded_at.desc()).first()

        # Only record if price changed or it's been more than 24 hours
        should_record = True
        if last_record:
            time_diff = datetime.now() - last_record.recorded_at
            price_changed = abs(float(last_record.price) - float(price)) > 0.01

            if not price_changed and time_diff < timedelta(hours=24):
                should_record = False

        if not should_record:
            logger.debug(f"Skipping price record for product {product_id} - no significant change")
            return last_record

        # Create new price record
        price_record = PriceHistory(
            product_id=product_id,
            asin=product.asin,
            price=price,
            unit_price=unit_price,
            is_prime=is_prime,
            is_sponsored=is_sponsored,
            in_stock=in_stock,
            recorded_at=datetime.now()
        )

        db.add(price_record)
        db.commit()
        db.refresh(price_record)

        logger.info(f"Recorded price ${price} for product {product_id}")
        return price_record

    @staticmethod
    def get_price_history(
        db: Session,
        product_id: int,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Get price history for a product

        Args:
            db: Database session
            product_id: Product ID
            days: Number of days to look back

        Returns:
            List of price history records
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        history = db.query(PriceHistory).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= cutoff_date
            )
        ).order_by(PriceHistory.recorded_at.asc()).all()

        return [
            {
                "date": record.recorded_at.isoformat(),
                "price": float(record.price),
                "unit_price": float(record.unit_price) if record.unit_price else None,
                "is_prime": record.is_prime,
                "is_sponsored": record.is_sponsored,
                "in_stock": record.in_stock
            }
            for record in history
        ]

    @staticmethod
    def get_price_statistics(
        db: Session,
        product_id: int,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Calculate price statistics for a product

        Args:
            db: Database session
            product_id: Product ID
            days: Number of days to analyze

        Returns:
            Dictionary with price statistics
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get price statistics
        stats = db.query(
            func.min(PriceHistory.price).label('min_price'),
            func.max(PriceHistory.price).label('max_price'),
            func.avg(PriceHistory.price).label('avg_price'),
            func.count(PriceHistory.id).label('data_points')
        ).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= cutoff_date
            )
        ).first()

        if not stats or stats.data_points == 0:
            return {
                "min_price": None,
                "max_price": None,
                "avg_price": None,
                "current_price": None,
                "price_change_pct": None,
                "is_lowest": None,
                "is_highest": None,
                "data_points": 0,
                "days_analyzed": days
            }

        # Get current price
        current_record = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).order_by(PriceHistory.recorded_at.desc()).first()

        current_price = float(current_record.price) if current_record else None

        # Get oldest price in period for trend calculation
        oldest_record = db.query(PriceHistory).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= cutoff_date
            )
        ).order_by(PriceHistory.recorded_at.asc()).first()

        # Calculate price change percentage
        price_change_pct = None
        if oldest_record and current_price:
            old_price = float(oldest_record.price)
            if old_price > 0:
                price_change_pct = ((current_price - old_price) / old_price) * 100

        return {
            "min_price": float(stats.min_price),
            "max_price": float(stats.max_price),
            "avg_price": float(stats.avg_price),
            "current_price": current_price,
            "price_change_pct": round(price_change_pct, 2) if price_change_pct else None,
            "is_lowest": current_price == float(stats.min_price) if current_price else None,
            "is_highest": current_price == float(stats.max_price) if current_price else None,
            "data_points": stats.data_points,
            "days_analyzed": days,
            "trend": "down" if price_change_pct and price_change_pct < -5 else "up" if price_change_pct and price_change_pct > 5 else "stable"
        }

    @staticmethod
    def get_best_price_time(
        db: Session,
        product_id: int,
        days: int = 90
    ) -> Dict[str, Any]:
        """
        Analyze when the product was at its lowest price

        Args:
            db: Database session
            product_id: Product ID
            days: Number of days to analyze

        Returns:
            Best price time analysis
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        # Get lowest price record
        lowest_price_record = db.query(PriceHistory).filter(
            and_(
                PriceHistory.product_id == product_id,
                PriceHistory.recorded_at >= cutoff_date
            )
        ).order_by(PriceHistory.price.asc()).first()

        if not lowest_price_record:
            return {
                "best_price": None,
                "best_price_date": None,
                "days_ago": None,
                "savings_from_current": None
            }

        # Get current price
        current_record = db.query(PriceHistory).filter(
            PriceHistory.product_id == product_id
        ).order_by(PriceHistory.recorded_at.desc()).first()

        savings = None
        if current_record:
            savings = float(current_record.price) - float(lowest_price_record.price)

        days_ago = (datetime.now() - lowest_price_record.recorded_at).days

        return {
            "best_price": float(lowest_price_record.price),
            "best_price_date": lowest_price_record.recorded_at.isoformat(),
            "days_ago": days_ago,
            "savings_from_current": round(savings, 2) if savings else None,
            "recommendation": "Buy now!" if days_ago < 7 and savings and savings < 1 else "Wait for better price" if savings and savings > 5 else "Good time to buy"
        }

    @staticmethod
    def get_price_drop_alerts(
        db: Session,
        min_drop_percentage: float = 10.0,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Find products with recent significant price drops

        Args:
            db: Database session
            min_drop_percentage: Minimum drop percentage to alert
            hours: Time window to check

        Returns:
            List of products with price drops
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        # Get products with recent price changes
        products_with_drops = []

        # This would be more efficient with a subquery, but keeping it simple
        products = db.query(Product).all()

        for product in products:
            # Get recent price records
            recent_records = db.query(PriceHistory).filter(
                and_(
                    PriceHistory.product_id == product.id,
                    PriceHistory.recorded_at >= cutoff_time
                )
            ).order_by(PriceHistory.recorded_at.asc()).all()

            if len(recent_records) >= 2:
                old_price = float(recent_records[0].price)
                new_price = float(recent_records[-1].price)

                if old_price > 0:
                    drop_pct = ((old_price - new_price) / old_price) * 100

                    if drop_pct >= min_drop_percentage:
                        products_with_drops.append({
                            "product_id": product.id,
                            "asin": product.asin,
                            "title": product.title,
                            "old_price": old_price,
                            "new_price": new_price,
                            "drop_percentage": round(drop_pct, 2),
                            "savings": round(old_price - new_price, 2),
                            "timestamp": recent_records[-1].recorded_at.isoformat()
                        })

        # Sort by drop percentage (highest first)
        products_with_drops.sort(key=lambda x: x['drop_percentage'], reverse=True)

        return products_with_drops
