"""
Initialize database with sample data
"""
from decimal import Decimal
from .database import SessionLocal
from .models import Product, CategoryStats


def init_sample_data():
    """
    Insert sample products for testing
    """
    db = SessionLocal()

    try:
        # Check if data already exists
        existing = db.query(Product).first()
        if existing:
            print("Sample data already exists, skipping initialization")
            return

        # Sample products
        sample_products = [
            Product(
                asin='B000QSO98W',
                title='Optimum Nutrition Gold Standard 100% Whey Protein Powder, 5 lb',
                brand='Optimum Nutrition',
                category='Protein Powder',
                current_price=Decimal('54.99'),
                list_price=Decimal('69.99'),
                unit_price=Decimal('0.69'),
                unit_type='oz',
                unit_quantity=Decimal('80'),
                discount_pct=Decimal('21.43'),
                rating=Decimal('4.6'),
                review_count=12403,
                verified_review_count=10000,
                image_url='https://via.placeholder.com/300x300?text=Protein+Powder',
                amazon_url='https://amazon.com/dp/B000QSO98W',
                is_prime=True,
                is_sponsored=False,
                subscribe_save_pct=Decimal('15.0'),
                in_stock=True,
                hidden_gem_score=85,
                deal_quality_score=90
            ),
            Product(
                asin='B00SCO8XM0',
                title='Dymatize ISO100 Hydrolyzed Protein Powder, 3 lb',
                brand='Dymatize',
                category='Protein Powder',
                current_price=Decimal('44.99'),
                list_price=Decimal('54.99'),
                unit_price=Decimal('0.94'),
                unit_type='oz',
                unit_quantity=Decimal('48'),
                discount_pct=Decimal('18.18'),
                rating=Decimal('4.5'),
                review_count=8234,
                verified_review_count=7000,
                image_url='https://via.placeholder.com/300x300?text=Protein+Powder',
                amazon_url='https://amazon.com/dp/B00SCO8XM0',
                is_prime=True,
                is_sponsored=True,
                subscribe_save_pct=Decimal('10.0'),
                in_stock=True,
                hidden_gem_score=70,
                deal_quality_score=75
            ),
            Product(
                asin='B001RZP6LW',
                title='MyProtein Impact Whey Protein, 2.2 lb',
                brand='MyProtein',
                category='Protein Powder',
                current_price=Decimal('29.99'),
                list_price=Decimal('39.99'),
                unit_price=Decimal('0.85'),
                unit_type='oz',
                unit_quantity=Decimal('35.2'),
                discount_pct=Decimal('25.0'),
                rating=Decimal('4.4'),
                review_count=3421,
                verified_review_count=3000,
                image_url='https://via.placeholder.com/300x300?text=Protein+Powder',
                amazon_url='https://amazon.com/dp/B001RZP6LW',
                is_prime=False,
                is_sponsored=False,
                subscribe_save_pct=Decimal('5.0'),
                in_stock=True,
                hidden_gem_score=88,
                deal_quality_score=80
            ),
            Product(
                asin='B002DYJ0O6',
                title='BSN SYNTHA-6 Protein Powder, 5.04 lb',
                brand='BSN',
                category='Protein Powder',
                current_price=Decimal('49.99'),
                list_price=Decimal('59.99'),
                unit_price=Decimal('0.62'),
                unit_type='oz',
                unit_quantity=Decimal('80.64'),
                discount_pct=Decimal('16.67'),
                rating=Decimal('4.5'),
                review_count=5678,
                verified_review_count=5000,
                image_url='https://via.placeholder.com/300x300?text=Protein+Powder',
                amazon_url='https://amazon.com/dp/B002DYJ0O6',
                is_prime=True,
                is_sponsored=True,
                subscribe_save_pct=Decimal('15.0'),
                in_stock=True,
                hidden_gem_score=75,
                deal_quality_score=85
            ),
        ]

        # Add products
        for product in sample_products:
            db.add(product)

        # Add category stats
        stats = CategoryStats(
            category='Protein Powder',
            median_price=Decimal('49.99'),
            median_unit_price=Decimal('0.85'),
            avg_rating=Decimal('4.5'),
            product_count=4
        )
        db.add(stats)

        db.commit()
        print("✅ Sample data initialized successfully!")

    except Exception as e:
        print(f"❌ Error initializing sample data: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_sample_data()
