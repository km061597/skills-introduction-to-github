"""
API endpoint tests for SmartAmazon
"""
import pytest
from fastapi.testclient import TestClient


class TestSearchEndpoint:
    """Test the /api/search endpoint"""

    def test_search_returns_products(self, client, sample_products):
        """Test basic search functionality"""
        response = client.get("/api/search?q=protein")
        assert response.status_code == 200

        data = response.json()
        assert "results" in data
        assert "total" in data
        assert data["total"] >= 2  # At least 2 protein products

    def test_search_hide_sponsored(self, client, sample_products):
        """Test hiding sponsored products"""
        response = client.get("/api/search?q=protein&hide_sponsored=true")
        assert response.status_code == 200

        data = response.json()
        # Should only return non-sponsored products
        assert all(not p["is_sponsored"] for p in data["results"])

    def test_search_price_filter(self, client, sample_products):
        """Test price range filtering"""
        response = client.get("/api/search?q=protein&min_price=40&max_price=60")
        assert response.status_code == 200

        data = response.json()
        for product in data["results"]:
            price = float(product["current_price"])
            assert 40 <= price <= 60

    def test_search_rating_filter(self, client, sample_products):
        """Test minimum rating filter"""
        response = client.get("/api/search?q=test&min_rating=4.5")
        assert response.status_code == 200

        data = response.json()
        for product in data["results"]:
            if product["rating"]:
                assert float(product["rating"]) >= 4.5

    def test_search_prime_filter(self, client, sample_products):
        """Test Prime-only filter"""
        response = client.get("/api/search?q=test&prime_only=true")
        assert response.status_code == 200

        data = response.json()
        assert all(p["is_prime"] for p in data["results"])

    def test_search_sort_unit_price(self, client, sample_products):
        """Test sorting by unit price"""
        response = client.get("/api/search?q=protein&sort=unit_price_asc")
        assert response.status_code == 200

        data = response.json()
        results = data["results"]

        # Check if sorted by unit price ascending
        if len(results) > 1:
            unit_prices = [float(p["unit_price"]) for p in results if p["unit_price"]]
            assert unit_prices == sorted(unit_prices)

    def test_search_pagination(self, client, sample_products):
        """Test pagination"""
        # Page 1
        response1 = client.get("/api/search?q=test&page=1&limit=2")
        assert response1.status_code == 200
        data1 = response1.json()
        assert len(data1["results"]) <= 2
        assert data1["page"] == 1

        # Page 2
        response2 = client.get("/api/search?q=test&page=2&limit=2")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["page"] == 2

    def test_search_empty_query(self, client):
        """Test search with empty query returns error"""
        response = client.get("/api/search?q=")
        assert response.status_code == 422  # Validation error


class TestProductDetailEndpoint:
    """Test the /api/product/{asin} endpoint"""

    def test_get_product_by_asin(self, client, sample_products):
        """Test retrieving product details"""
        response = client.get("/api/product/TEST001")
        assert response.status_code == 200

        data = response.json()
        assert data["asin"] == "TEST001"
        assert "title" in data
        assert "current_price" in data
        assert "unit_price" in data

    def test_get_nonexistent_product(self, client):
        """Test retrieving non-existent product returns 404"""
        response = client.get("/api/product/NONEXISTENT")
        assert response.status_code == 404

    def test_product_includes_price_history(self, client, sample_products):
        """Test product details include price history"""
        response = client.get("/api/product/TEST001")
        assert response.status_code == 200

        data = response.json()
        assert "price_history" in data
        assert isinstance(data["price_history"], list)

    def test_product_includes_similar_products(self, client, sample_products):
        """Test product details include similar products"""
        response = client.get("/api/product/TEST001")
        assert response.status_code == 200

        data = response.json()
        assert "similar_products" in data
        assert isinstance(data["similar_products"], list)


class TestCompareEndpoint:
    """Test the /api/compare endpoint"""

    def test_compare_multiple_products(self, client, sample_products):
        """Test comparing multiple products"""
        response = client.post(
            "/api/compare",
            json={"asins": ["TEST001", "TEST002"]}
        )
        assert response.status_code == 200

        data = response.json()
        assert "products" in data
        assert len(data["products"]) == 2
        assert "best_unit_price_asin" in data
        assert "best_rating_asin" in data

    def test_compare_single_product_error(self, client, sample_products):
        """Test comparing with less than 2 products returns error"""
        response = client.post(
            "/api/compare",
            json={"asins": ["TEST001"]}
        )
        assert response.status_code == 422  # Validation error

    def test_compare_identifies_best_values(self, client, sample_products):
        """Test that compare endpoint identifies best values"""
        response = client.post(
            "/api/compare",
            json={"asins": ["TEST001", "TEST002"]}
        )
        assert response.status_code == 200

        data = response.json()
        assert data["best_unit_price_asin"] == "TEST001"  # Lower unit price


class TestCategoriesEndpoint:
    """Test the /api/categories endpoint"""

    def test_get_categories(self, client, sample_products):
        """Test retrieving list of categories"""
        response = client.get("/api/categories")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert "Protein Powder" in data
        assert "Vitamins" in data


class TestBrandsEndpoint:
    """Test the /api/brands endpoint"""

    def test_get_brands(self, client, sample_products):
        """Test retrieving list of brands"""
        response = client.get("/api/brands")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)
        assert "TestBrand" in data

    def test_get_brands_by_category(self, client, sample_products):
        """Test filtering brands by category"""
        response = client.get("/api/brands?category=Protein+Powder")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)


class TestHealthEndpoints:
    """Test health check endpoints"""

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "features" in data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
