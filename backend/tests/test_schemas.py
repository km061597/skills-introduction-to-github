"""
Tests for Pydantic schema validation

This module tests:
1. Request validation (SearchRequest, CompareRequest)
2. Response serialization (ProductResponse, SearchResponse, etc.)
3. Field validators and constraints
4. Edge cases and invalid inputs
"""
import pytest
from pydantic import ValidationError
from decimal import Decimal
from datetime import datetime
from typing import List

from app.schemas import (
    ProductBase,
    ProductResponse,
    PriceHistoryResponse,
    SearchRequest,
    SearchResponse,
    ProductDetailResponse,
    CategoryStatsResponse,
    CompareRequest,
    CompareResponse
)


class TestProductBase:
    """Tests for ProductBase schema"""

    def test_product_base_minimal(self):
        """Test creating product with minimal required fields"""
        product = ProductBase(
            asin="B000QSO98W",
            title="Test Product"
        )

        assert product.asin == "B000QSO98W"
        assert product.title == "Test Product"
        assert product.is_prime is False
        assert product.is_sponsored is False
        assert product.in_stock is True

    def test_product_base_complete(self):
        """Test creating product with all fields"""
        product = ProductBase(
            asin="B000QSO98W",
            title="Test Product",
            brand="Test Brand",
            category="Protein",
            current_price=Decimal("54.99"),
            list_price=Decimal("69.99"),
            unit_price=Decimal("0.69"),
            unit_type="oz",
            quantity=Decimal("80"),
            discount_pct=Decimal("21.43"),
            rating=Decimal("4.6"),
            review_count=12403,
            verified_review_count=8500,
            image_url="https://example.com/image.jpg",
            amazon_url="https://amazon.com/dp/B000QSO98W",
            is_prime=True,
            is_sponsored=False,
            subscribe_save_pct=Decimal("15"),
            in_stock=True,
            hidden_gem_score=85,
            deal_quality_score=92
        )

        assert product.asin == "B000QSO98W"
        assert product.current_price == Decimal("54.99")
        assert product.rating == Decimal("4.6")
        assert product.is_prime is True

    def test_product_base_default_values(self):
        """Test that default values are set correctly"""
        product = ProductBase(
            asin="TEST123",
            title="Test"
        )

        assert product.brand is None
        assert product.category is None
        assert product.current_price is None
        assert product.review_count == 0
        assert product.is_prime is False
        assert product.in_stock is True

    def test_product_base_decimal_fields(self):
        """Test that decimal fields accept various numeric types"""
        product = ProductBase(
            asin="TEST123",
            title="Test",
            current_price=49.99,  # float
            rating=4.5,  # float
            unit_price="0.62"  # string
        )

        assert isinstance(product.current_price, Decimal)
        assert isinstance(product.rating, Decimal)
        assert isinstance(product.unit_price, Decimal)


class TestProductResponse:
    """Tests for ProductResponse schema"""

    def test_product_response_with_timestamps(self):
        """Test ProductResponse includes timestamp fields"""
        now = datetime.now()

        product = ProductResponse(
            asin="B000QSO98W",
            title="Test Product",
            last_scraped_at=now,
            created_at=now,
            updated_at=now
        )

        assert product.last_scraped_at == now
        assert product.created_at == now
        assert product.updated_at == now

    def test_product_response_computed_fields(self):
        """Test ProductResponse computed fields"""
        now = datetime.now()

        product = ProductResponse(
            asin="B000QSO98W",
            title="Test Product",
            last_scraped_at=now,
            created_at=now,
            updated_at=now,
            is_best_value=True,
            savings_vs_category=Decimal("12.50")
        )

        assert product.is_best_value is True
        assert product.savings_vs_category == Decimal("12.50")


class TestSearchRequest:
    """Tests for SearchRequest validation"""

    def test_search_request_minimal(self):
        """Test search request with minimal fields"""
        request = SearchRequest(q="protein")

        assert request.q == "protein"
        assert request.sort == "unit_price_asc"
        assert request.page == 1
        assert request.limit == 48
        assert request.prime_only is False
        assert request.hide_sponsored is True

    def test_search_request_empty_query_fails(self):
        """Test that empty query is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SearchRequest(q="")

        assert "q" in str(exc_info.value)

    def test_search_request_valid_sort_options(self):
        """Test all valid sort options"""
        valid_sorts = [
            'unit_price_asc', 'unit_price_desc',
            'price_asc', 'price_desc',
            'discount_desc', 'rating_desc',
            'review_count_desc', 'hidden_gem_desc'
        ]

        for sort_option in valid_sorts:
            request = SearchRequest(q="test", sort=sort_option)
            assert request.sort == sort_option

    def test_search_request_invalid_sort_fails(self):
        """Test that invalid sort option is rejected"""
        with pytest.raises(ValidationError) as exc_info:
            SearchRequest(q="protein", sort="invalid_sort")

        assert "sort" in str(exc_info.value).lower()

    def test_search_request_price_filters(self):
        """Test price filter fields"""
        request = SearchRequest(
            q="protein",
            min_price=Decimal("20.00"),
            max_price=Decimal("60.00"),
            min_unit_price=Decimal("0.50"),
            max_unit_price=Decimal("1.00")
        )

        assert request.min_price == Decimal("20.00")
        assert request.max_price == Decimal("60.00")
        assert request.min_unit_price == Decimal("0.50")
        assert request.max_unit_price == Decimal("1.00")

    def test_search_request_rating_constraints(self):
        """Test rating field constraints"""
        # Valid ratings
        for rating in [0, 2.5, 4.0, 5.0]:
            request = SearchRequest(q="test", min_rating=rating)
            assert request.min_rating == rating

        # Invalid ratings
        for invalid_rating in [-1, 5.1, 10]:
            with pytest.raises(ValidationError):
                SearchRequest(q="test", min_rating=invalid_rating)

    def test_search_request_discount_constraints(self):
        """Test discount field constraints"""
        # Valid discounts
        for discount in [0, 25, 50, 100]:
            request = SearchRequest(q="test", min_discount=discount)
            assert request.min_discount == discount

        # Invalid discounts
        for invalid_discount in [-1, 101, 200]:
            with pytest.raises(ValidationError):
                SearchRequest(q="test", min_discount=invalid_discount)

    def test_search_request_page_constraints(self):
        """Test page field constraints"""
        # Valid pages
        request = SearchRequest(q="test", page=1)
        assert request.page == 1

        request = SearchRequest(q="test", page=100)
        assert request.page == 100

        # Invalid pages
        with pytest.raises(ValidationError):
            SearchRequest(q="test", page=0)

        with pytest.raises(ValidationError):
            SearchRequest(q="test", page=-1)

    def test_search_request_limit_constraints(self):
        """Test limit field constraints"""
        # Valid limits
        request = SearchRequest(q="test", limit=1)
        assert request.limit == 1

        request = SearchRequest(q="test", limit=100)
        assert request.limit == 100

        # Invalid limits
        with pytest.raises(ValidationError):
            SearchRequest(q="test", limit=0)

        with pytest.raises(ValidationError):
            SearchRequest(q="test", limit=101)

    def test_search_request_boolean_filters(self):
        """Test boolean filter fields"""
        request = SearchRequest(
            q="protein",
            prime_only=True,
            hide_sponsored=False,
            in_stock_only=True
        )

        assert request.prime_only is True
        assert request.hide_sponsored is False
        assert request.in_stock_only is True

    def test_search_request_brand_filters(self):
        """Test brand filter fields"""
        request = SearchRequest(
            q="protein",
            brands=["Optimum Nutrition", "Dymatize"],
            exclude_brands=["Generic Brand"]
        )

        assert len(request.brands) == 2
        assert "Optimum Nutrition" in request.brands
        assert len(request.exclude_brands) == 1

    def test_search_request_comprehensive(self):
        """Test search request with all filters"""
        request = SearchRequest(
            q="protein powder",
            sort="unit_price_asc",
            min_price=Decimal("30.00"),
            max_price=Decimal("70.00"),
            min_unit_price=Decimal("0.50"),
            max_unit_price=Decimal("1.00"),
            min_rating=Decimal("4.0"),
            min_review_count=1000,
            prime_only=True,
            hide_sponsored=True,
            min_discount=20,
            brands=["Optimum Nutrition"],
            exclude_brands=["Generic"],
            in_stock_only=True,
            page=2,
            limit=24
        )

        assert request.q == "protein powder"
        assert request.min_rating == Decimal("4.0")
        assert request.page == 2


class TestSearchResponse:
    """Tests for SearchResponse schema"""

    def test_search_response_empty_results(self):
        """Test search response with no results"""
        response = SearchResponse(
            results=[],
            total=0,
            page=1,
            pages=0,
            query="nonexistent"
        )

        assert len(response.results) == 0
        assert response.total == 0
        assert response.pages == 0

    def test_search_response_with_results(self):
        """Test search response with results"""
        now = datetime.now()

        products = [
            ProductResponse(
                asin=f"TEST{i}",
                title=f"Product {i}",
                last_scraped_at=now,
                created_at=now,
                updated_at=now
            )
            for i in range(5)
        ]

        response = SearchResponse(
            results=products,
            total=50,
            page=1,
            pages=3,
            sponsored_hidden=10,
            query="protein"
        )

        assert len(response.results) == 5
        assert response.total == 50
        assert response.pages == 3
        assert response.sponsored_hidden == 10


class TestPriceHistoryResponse:
    """Tests for PriceHistoryResponse schema"""

    def test_price_history_response(self):
        """Test price history response"""
        now = datetime.now()

        history = PriceHistoryResponse(
            id=1,
            asin="B000QSO98W",
            price=Decimal("54.99"),
            unit_price=Decimal("0.69"),
            recorded_at=now
        )

        assert history.id == 1
        assert history.asin == "B000QSO98W"
        assert history.price == Decimal("54.99")
        assert history.recorded_at == now

    def test_price_history_optional_unit_price(self):
        """Test price history without unit price"""
        now = datetime.now()

        history = PriceHistoryResponse(
            id=1,
            asin="B000QSO98W",
            price=Decimal("54.99"),
            recorded_at=now
        )

        assert history.unit_price is None


class TestProductDetailResponse:
    """Tests for ProductDetailResponse schema"""

    def test_product_detail_with_history(self):
        """Test product detail with price history"""
        now = datetime.now()

        history = [
            PriceHistoryResponse(
                id=i,
                asin="B000QSO98W",
                price=Decimal(f"{50 + i}.99"),
                recorded_at=now
            )
            for i in range(3)
        ]

        detail = ProductDetailResponse(
            asin="B000QSO98W",
            title="Test Product",
            last_scraped_at=now,
            created_at=now,
            updated_at=now,
            price_history=history
        )

        assert len(detail.price_history) == 3
        assert detail.price_history[0].price == Decimal("50.99")

    def test_product_detail_with_similar_products(self):
        """Test product detail with similar products"""
        now = datetime.now()

        similar = [
            ProductResponse(
                asin=f"SIMILAR{i}",
                title=f"Similar Product {i}",
                last_scraped_at=now,
                created_at=now,
                updated_at=now
            )
            for i in range(3)
        ]

        detail = ProductDetailResponse(
            asin="B000QSO98W",
            title="Test Product",
            last_scraped_at=now,
            created_at=now,
            updated_at=now,
            similar_products=similar
        )

        assert len(detail.similar_products) == 3


class TestCategoryStatsResponse:
    """Tests for CategoryStatsResponse schema"""

    def test_category_stats_response(self):
        """Test category stats response"""
        now = datetime.now()

        stats = CategoryStatsResponse(
            category="Protein Powder",
            median_price=Decimal("54.99"),
            median_unit_price=Decimal("0.75"),
            avg_rating=Decimal("4.5"),
            product_count=150,
            last_updated=now
        )

        assert stats.category == "Protein Powder"
        assert stats.median_price == Decimal("54.99")
        assert stats.product_count == 150

    def test_category_stats_minimal(self):
        """Test category stats with minimal data"""
        now = datetime.now()

        stats = CategoryStatsResponse(
            category="Unknown",
            last_updated=now
        )

        assert stats.category == "Unknown"
        assert stats.median_price is None
        assert stats.product_count == 0


class TestCompareRequest:
    """Tests for CompareRequest validation"""

    def test_compare_request_valid(self):
        """Test valid compare request"""
        request = CompareRequest(
            asins=["B000QSO98W", "B00SCO8XM0"]
        )

        assert len(request.asins) == 2

    def test_compare_request_too_few_asins(self):
        """Test that fewer than 2 ASINs is rejected"""
        with pytest.raises(ValidationError):
            CompareRequest(asins=["B000QSO98W"])

    def test_compare_request_too_many_asins(self):
        """Test that more than 10 ASINs is rejected"""
        asins = [f"ASIN{i:02d}" for i in range(11)]

        with pytest.raises(ValidationError):
            CompareRequest(asins=asins)

    def test_compare_request_max_allowed(self):
        """Test maximum allowed ASINs (10)"""
        asins = [f"ASIN{i:02d}" for i in range(10)]

        request = CompareRequest(asins=asins)
        assert len(request.asins) == 10


class TestCompareResponse:
    """Tests for CompareResponse schema"""

    def test_compare_response(self):
        """Test compare response"""
        now = datetime.now()

        products = [
            ProductResponse(
                asin=f"TEST{i}",
                title=f"Product {i}",
                current_price=Decimal(f"{50 + i}.99"),
                unit_price=Decimal(f"{0.60 + i * 0.1}"),
                rating=Decimal(f"{4.0 + i * 0.1}"),
                last_scraped_at=now,
                created_at=now,
                updated_at=now
            )
            for i in range(3)
        ]

        response = CompareResponse(
            products=products,
            best_unit_price_asin="TEST0",
            best_rating_asin="TEST2",
            best_value_asin="TEST0"
        )

        assert len(response.products) == 3
        assert response.best_unit_price_asin == "TEST0"
        assert response.best_rating_asin == "TEST2"

    def test_compare_response_optional_fields(self):
        """Test compare response with optional fields as None"""
        response = CompareResponse(products=[])

        assert response.best_unit_price_asin is None
        assert response.best_rating_asin is None
        assert response.best_value_asin is None


class TestSchemaEdgeCases:
    """Tests for edge cases and boundary conditions"""

    def test_very_large_numbers(self):
        """Test handling of very large numbers"""
        product = ProductBase(
            asin="TEST",
            title="Test",
            current_price=Decimal("999999.99"),
            review_count=9999999
        )

        assert product.current_price == Decimal("999999.99")
        assert product.review_count == 9999999

    def test_very_small_decimals(self):
        """Test handling of very small decimal values"""
        product = ProductBase(
            asin="TEST",
            title="Test",
            unit_price=Decimal("0.0001"),
            rating=Decimal("0.1")
        )

        assert product.unit_price == Decimal("0.0001")

    def test_special_characters_in_strings(self):
        """Test handling of special characters"""
        product = ProductBase(
            asin="TEST",
            title="Product with 'quotes' and \"double quotes\" & symbols!",
            brand="Brand™ Name®"
        )

        assert "quotes" in product.title
        assert "™" in product.brand

    def test_unicode_characters(self):
        """Test handling of unicode characters"""
        product = ProductBase(
            asin="TEST",
            title="Café Latté Protein 日本語",
            brand="Müller"
        )

        assert "Café" in product.title
        assert "Müller" == product.brand
