"""
API Routes for SmartAmazon Search Platform
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_
from typing import List, Optional
from decimal import Decimal
import math
import hashlib
import json
from datetime import datetime, timedelta

from ..database import get_db
from ..models import Product, PriceHistory, SearchCache, CategoryStats
from ..schemas import (
    SearchRequest, SearchResponse, ProductResponse,
    ProductDetailResponse, PriceHistoryResponse,
    CompareRequest, CompareResponse, CategoryStatsResponse
)
from ..scraper import MockAmazonScraper
from ..unit_calculator import UnitCalculator

router = APIRouter()


@router.get("/search", response_model=SearchResponse)
async def search_products(
    q: str = Query(..., min_length=1, description="Search query"),
    sort: str = Query(default="unit_price_asc", description="Sort option"),
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    min_unit_price: Optional[float] = None,
    max_unit_price: Optional[float] = None,
    min_rating: Optional[float] = Query(None, ge=0, le=5),
    min_review_count: Optional[int] = None,
    prime_only: bool = False,
    hide_sponsored: bool = True,
    min_discount: Optional[int] = Query(None, ge=0, le=100),
    brands: Optional[List[str]] = Query(None),
    exclude_brands: Optional[List[str]] = Query(None),
    in_stock_only: bool = False,
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=48, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Main search endpoint with filtering and sorting

    This endpoint searches for products and applies various filters.
    Results are cached for 15 minutes to reduce load.
    """

    # Check cache first
    cache_key = _generate_cache_key(
        q, sort, min_price, max_price, min_unit_price, max_unit_price,
        min_rating, min_review_count, prime_only, hide_sponsored,
        min_discount, brands, exclude_brands, in_stock_only
    )

    cached = db.query(SearchCache).filter(
        SearchCache.query_hash == cache_key,
        SearchCache.expires_at > datetime.now()
    ).first()

    # If cache miss or expired, scrape and store in DB
    if not cached:
        # Scrape Amazon (using mock for demo)
        scraper = MockAmazonScraper()
        scraped_products = scraper.search(q, pages=2)

        # Store in database
        for product_data in scraped_products:
            _upsert_product(db, product_data)

        db.commit()

    # Build query
    query = db.query(Product).filter(
        or_(
            Product.title.ilike(f'%{q}%'),
            Product.brand.ilike(f'%{q}%')
        )
    )

    # Apply filters
    if hide_sponsored:
        query = query.filter(Product.is_sponsored == False)

    sponsored_count = db.query(func.count(Product.asin)).filter(
        Product.is_sponsored == True,
        or_(
            Product.title.ilike(f'%{q}%'),
            Product.brand.ilike(f'%{q}%')
        )
    ).scalar() or 0

    if min_price is not None:
        query = query.filter(Product.current_price >= min_price)

    if max_price is not None:
        query = query.filter(Product.current_price <= max_price)

    if min_unit_price is not None:
        query = query.filter(Product.unit_price >= min_unit_price)

    if max_unit_price is not None:
        query = query.filter(Product.unit_price <= max_unit_price)

    if min_rating is not None:
        query = query.filter(Product.rating >= min_rating)

    if min_review_count is not None:
        query = query.filter(Product.review_count >= min_review_count)

    if prime_only:
        query = query.filter(Product.is_prime == True)

    if min_discount is not None:
        query = query.filter(Product.discount_pct >= min_discount)

    if brands:
        query = query.filter(Product.brand.in_(brands))

    if exclude_brands:
        query = query.filter(~Product.brand.in_(exclude_brands))

    if in_stock_only:
        query = query.filter(Product.in_stock == True)

    # Apply sorting
    sort_map = {
        'unit_price_asc': Product.unit_price.asc(),
        'unit_price_desc': Product.unit_price.desc(),
        'price_asc': Product.current_price.asc(),
        'price_desc': Product.current_price.desc(),
        'discount_desc': Product.discount_pct.desc(),
        'rating_desc': Product.rating.desc(),
        'review_count_desc': Product.review_count.desc(),
        'hidden_gem_desc': Product.hidden_gem_score.desc()
    }

    if sort in sort_map:
        # Handle NULL values by sorting them last
        query = query.order_by(sort_map[sort].nullslast())

    # Get total count
    total = query.count()

    # Paginate
    offset = (page - 1) * limit
    results = query.offset(offset).limit(limit).all()

    # Get category stats for comparison
    category_stats = {}
    if results:
        categories = {p.category for p in results if p.category}
        for category in categories:
            stats = db.query(CategoryStats).filter(
                CategoryStats.category == category
            ).first()
            if stats:
                category_stats[category] = stats

    # Convert to response format and add computed fields
    product_responses = []
    for product in results:
        response = ProductResponse.from_orm(product)

        # Add computed fields
        if product.category and product.category in category_stats:
            stats = category_stats[product.category]
            if product.unit_price and stats.median_unit_price:
                savings = ((stats.median_unit_price - product.unit_price) / stats.median_unit_price) * 100
                response.savings_vs_category = Decimal(str(round(savings, 2)))

        # Check if best value
        response.is_best_value = (product.unit_price == results[0].unit_price if results else False)

        product_responses.append(response)

    return SearchResponse(
        results=product_responses,
        total=total,
        page=page,
        pages=math.ceil(total / limit) if limit > 0 else 0,
        sponsored_hidden=sponsored_count if hide_sponsored else 0,
        query=q
    )


@router.get("/product/{asin}", response_model=ProductDetailResponse)
async def get_product_detail(
    asin: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed product information including price history
    """
    product = db.query(Product).filter(Product.asin == asin).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Get price history (last 90 days)
    ninety_days_ago = datetime.now() - timedelta(days=90)
    price_history = db.query(PriceHistory).filter(
        PriceHistory.asin == asin,
        PriceHistory.recorded_at >= ninety_days_ago
    ).order_by(PriceHistory.recorded_at.desc()).limit(90).all()

    # Get similar products (same category, similar price range)
    similar_products = []
    if product.category and product.current_price:
        price_range = product.current_price * Decimal('0.2')  # +/- 20%
        similar = db.query(Product).filter(
            Product.category == product.category,
            Product.asin != asin,
            Product.current_price >= product.current_price - price_range,
            Product.current_price <= product.current_price + price_range
        ).order_by(Product.unit_price.asc()).limit(5).all()
        similar_products = [ProductResponse.from_orm(p) for p in similar]

    response = ProductDetailResponse.from_orm(product)
    response.price_history = [PriceHistoryResponse.from_orm(ph) for ph in price_history]
    response.similar_products = similar_products

    return response


@router.post("/compare", response_model=CompareResponse)
async def compare_products(
    request: CompareRequest,
    db: Session = Depends(get_db)
):
    """
    Compare multiple products side-by-side
    """
    products = db.query(Product).filter(
        Product.asin.in_(request.asins)
    ).all()

    if not products:
        raise HTTPException(status_code=404, detail="No products found")

    product_responses = [ProductResponse.from_orm(p) for p in products]

    # Find best values
    best_unit_price_asin = None
    best_rating_asin = None

    # Find product with best unit price
    products_with_unit_price = [p for p in products if p.unit_price is not None]
    if products_with_unit_price:
        best_unit_price_product = min(products_with_unit_price, key=lambda p: p.unit_price)
        best_unit_price_asin = best_unit_price_product.asin

    # Find product with best rating
    products_with_rating = [p for p in products if p.rating is not None]
    if products_with_rating:
        best_rating_product = max(products_with_rating, key=lambda p: p.rating)
        best_rating_asin = best_rating_product.asin

    return CompareResponse(
        products=product_responses,
        best_unit_price_asin=best_unit_price_asin,
        best_rating_asin=best_rating_asin,
        best_value_asin=best_unit_price_asin  # For now, use unit price
    )


@router.get("/categories", response_model=List[str])
async def get_categories(db: Session = Depends(get_db)):
    """
    Get list of all available categories
    """
    categories = db.query(Product.category).distinct().filter(
        Product.category.isnot(None)
    ).all()

    return [c[0] for c in categories]


@router.get("/brands", response_model=List[str])
async def get_brands(
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get list of all brands, optionally filtered by category
    """
    query = db.query(Product.brand).distinct().filter(
        Product.brand.isnot(None)
    )

    if category:
        query = query.filter(Product.category == category)

    brands = query.all()
    return sorted([b[0] for b in brands])


@router.get("/category-stats/{category}", response_model=CategoryStatsResponse)
async def get_category_stats(
    category: str,
    db: Session = Depends(get_db)
):
    """
    Get statistics for a specific category
    """
    stats = db.query(CategoryStats).filter(
        CategoryStats.category == category
    ).first()

    if not stats:
        # Calculate stats on the fly
        products = db.query(Product).filter(Product.category == category).all()

        if not products:
            raise HTTPException(status_code=404, detail="Category not found")

        prices = [p.current_price for p in products if p.current_price]
        unit_prices = [p.unit_price for p in products if p.unit_price]
        ratings = [p.rating for p in products if p.rating]

        stats = CategoryStats(
            category=category,
            median_price=Decimal(str(_median(prices))) if prices else None,
            median_unit_price=Decimal(str(_median(unit_prices))) if unit_prices else None,
            avg_rating=Decimal(str(sum(ratings) / len(ratings))) if ratings else None,
            product_count=len(products)
        )

        db.add(stats)
        db.commit()

    return CategoryStatsResponse.from_orm(stats)


# Helper functions

def _generate_cache_key(*args) -> str:
    """
    Generate cache key from query parameters
    """
    cache_data = json.dumps(args, sort_keys=True, default=str)
    return hashlib.md5(cache_data.encode()).hexdigest()


def _upsert_product(db: Session, product_data: dict):
    """
    Insert or update product in database
    """
    asin = product_data.get('asin')

    existing = db.query(Product).filter(Product.asin == asin).first()

    if existing:
        # Update existing product
        for key, value in product_data.items():
            if hasattr(existing, key) and value is not None:
                # Convert floats to Decimal for price fields
                if key in ['current_price', 'list_price', 'unit_price', 'discount_pct', 'rating', 'subscribe_save_pct']:
                    value = Decimal(str(value))
                setattr(existing, key, value)

        existing.last_scraped_at = datetime.now()

        # Add to price history if price changed
        if existing.current_price and product_data.get('current_price'):
            new_price = Decimal(str(product_data['current_price']))
            if new_price != existing.current_price:
                price_history = PriceHistory(
                    asin=asin,
                    price=new_price,
                    unit_price=Decimal(str(product_data.get('unit_price'))) if product_data.get('unit_price') else None
                )
                db.add(price_history)
    else:
        # Create new product
        # Convert floats to Decimal
        for key in ['current_price', 'list_price', 'unit_price', 'discount_pct', 'rating', 'subscribe_save_pct']:
            if key in product_data and product_data[key] is not None:
                product_data[key] = Decimal(str(product_data[key]))

        product = Product(**product_data)
        db.add(product)

        # Add initial price history
        if product_data.get('current_price'):
            price_history = PriceHistory(
                asin=asin,
                price=Decimal(str(product_data['current_price'])),
                unit_price=Decimal(str(product_data.get('unit_price'))) if product_data.get('unit_price') else None
            )
            db.add(price_history)


def _median(values: list) -> float:
    """
    Calculate median of a list
    """
    if not values:
        return 0

    sorted_values = sorted(values)
    n = len(sorted_values)

    if n % 2 == 0:
        return (float(sorted_values[n//2 - 1]) + float(sorted_values[n//2])) / 2
    else:
        return float(sorted_values[n//2])
