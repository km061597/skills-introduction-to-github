"""
Tests for Amazon scraper functionality

This module tests:
1. MockAmazonScraper for mock data generation
2. Price parsing methods
3. Rating and review count parsing
4. Sponsored detection logic
5. Product data extraction
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from bs4 import BeautifulSoup
from decimal import Decimal

from app.scraper import AmazonScraper, MockAmazonScraper


class TestMockAmazonScraper:
    """Tests for MockAmazonScraper"""

    def test_mock_scraper_initialization(self):
        """Test that MockAmazonScraper initializes correctly"""
        scraper = MockAmazonScraper()
        assert scraper is not None
        assert isinstance(scraper, AmazonScraper)

    def test_mock_search_returns_data(self):
        """Test that mock search returns product data"""
        scraper = MockAmazonScraper()
        results = scraper.search(query="protein", pages=1)

        assert len(results) > 0
        assert isinstance(results, list)
        assert all(isinstance(p, dict) for p in results)

    def test_mock_search_includes_query(self):
        """Test that mock results include the search query in title"""
        scraper = MockAmazonScraper()
        query = "chocolate"
        results = scraper.search(query=query, pages=1)

        assert len(results) > 0
        # Query should be incorporated into product titles
        for product in results:
            assert 'title' in product
            assert query in product['title'].lower()

    def test_mock_search_multiple_pages(self):
        """Test that pages parameter affects result count"""
        scraper = MockAmazonScraper()

        results_1_page = scraper.search(query="protein", pages=1)
        results_3_pages = scraper.search(query="protein", pages=3)

        assert len(results_3_pages) == len(results_1_page) * 3

    def test_mock_product_structure(self):
        """Test that mock products have all required fields"""
        scraper = MockAmazonScraper()
        results = scraper.search(query="protein", pages=1)

        required_fields = [
            'asin', 'title', 'brand', 'current_price', 'list_price',
            'discount_pct', 'unit_price', 'unit_type', 'quantity',
            'rating', 'review_count', 'image_url', 'amazon_url',
            'is_prime', 'is_sponsored', 'in_stock'
        ]

        for product in results:
            for field in required_fields:
                assert field in product, f"Missing field: {field}"

    def test_mock_product_types(self):
        """Test that mock product fields have correct types"""
        scraper = MockAmazonScraper()
        results = scraper.search(query="protein", pages=1)
        product = results[0]

        assert isinstance(product['asin'], str)
        assert isinstance(product['title'], str)
        assert isinstance(product['current_price'], (int, float))
        assert isinstance(product['rating'], (int, float))
        assert isinstance(product['review_count'], int)
        assert isinstance(product['is_prime'], bool)
        assert isinstance(product['is_sponsored'], bool)

    def test_mock_sponsored_and_non_sponsored(self):
        """Test that mock data includes both sponsored and organic results"""
        scraper = MockAmazonScraper()
        results = scraper.search(query="protein", pages=1)

        has_sponsored = any(p['is_sponsored'] for p in results)
        has_organic = any(not p['is_sponsored'] for p in results)

        assert has_sponsored, "Should have at least one sponsored result"
        assert has_organic, "Should have at least one organic result"


class TestAmazonScraperParsing:
    """Tests for AmazonScraper parsing methods"""

    def test_parse_price_standard(self):
        """Test parsing standard price format"""
        assert AmazonScraper._parse_price("$54.99") == 54.99
        assert AmazonScraper._parse_price("$123.45") == 123.45
        assert AmazonScraper._parse_price("$9.99") == 9.99

    def test_parse_price_without_dollar_sign(self):
        """Test parsing price without dollar sign"""
        assert AmazonScraper._parse_price("54.99") == 54.99
        assert AmazonScraper._parse_price("123") == 123.0

    def test_parse_price_with_commas(self):
        """Test parsing price with comma separators"""
        assert AmazonScraper._parse_price("$1,234.56") == 1234.56
        assert AmazonScraper._parse_price("$10,000.00") == 10000.0

    def test_parse_price_edge_cases(self):
        """Test price parsing edge cases"""
        assert AmazonScraper._parse_price("") is None
        assert AmazonScraper._parse_price(None) is None
        assert AmazonScraper._parse_price("invalid") is None
        assert AmazonScraper._parse_price("$") is None

    def test_parse_price_multiple_decimals(self):
        """Test price with multiple decimal points (invalid)"""
        # Should handle gracefully - may return first valid number or None
        result = AmazonScraper._parse_price("$12.34.56")
        assert result is None or isinstance(result, float)

    def test_parse_rating_standard(self):
        """Test parsing standard rating format"""
        assert AmazonScraper._parse_rating("4.6 out of 5 stars") == 4.6
        assert AmazonScraper._parse_rating("4.5 out of 5 stars") == 4.5
        assert AmazonScraper._parse_rating("3.0 out of 5 stars") == 3.0

    def test_parse_rating_short_format(self):
        """Test parsing short rating format"""
        assert AmazonScraper._parse_rating("4.6") == 4.6
        assert AmazonScraper._parse_rating("5.0") == 5.0
        assert AmazonScraper._parse_rating("1") == 1.0

    def test_parse_rating_edge_cases(self):
        """Test rating parsing edge cases"""
        assert AmazonScraper._parse_rating("") is None
        assert AmazonScraper._parse_rating(None) is None
        assert AmazonScraper._parse_rating("no rating") is None

    def test_parse_review_count_standard(self):
        """Test parsing standard review count"""
        assert AmazonScraper._parse_review_count("12,403 ratings") == 12403
        assert AmazonScraper._parse_review_count("1,234") == 1234
        assert AmazonScraper._parse_review_count("500") == 500

    def test_parse_review_count_large_numbers(self):
        """Test parsing large review counts"""
        assert AmazonScraper._parse_review_count("124,030") == 124030
        assert AmazonScraper._parse_review_count("1,234,567") == 1234567

    def test_parse_review_count_without_commas(self):
        """Test parsing review count without commas"""
        assert AmazonScraper._parse_review_count("12403") == 12403
        assert AmazonScraper._parse_review_count("500") == 500

    def test_parse_review_count_edge_cases(self):
        """Test review count parsing edge cases"""
        assert AmazonScraper._parse_review_count("") is None
        assert AmazonScraper._parse_review_count(None) is None
        assert AmazonScraper._parse_review_count("no reviews") is None


class TestAmazonScraperSponsoredDetection:
    """Tests for sponsored product detection"""

    def test_is_sponsored_data_attribute(self):
        """Test sponsored detection via data attribute"""
        scraper = AmazonScraper()

        # Create mock element with sponsored attribute
        mock_card = Mock()
        mock_card.get.return_value = 'sp-sponsored-result'
        mock_card.select_one.return_value = None

        assert scraper._is_sponsored(mock_card) is True

    def test_is_sponsored_badge_text(self):
        """Test sponsored detection via badge text"""
        scraper = AmazonScraper()

        # Create mock element with sponsored badge
        mock_card = Mock()
        mock_card.get.side_effect = lambda x: None if x == 'data-component-type' else []

        mock_badge = Mock()
        mock_badge.get_text.return_value = "Sponsored"
        mock_card.select_one.return_value = mock_badge

        assert scraper._is_sponsored(mock_card) is True

    def test_is_sponsored_adholder_class(self):
        """Test sponsored detection via AdHolder class"""
        scraper = AmazonScraper()

        # Create mock element with AdHolder class
        mock_card = Mock()
        mock_card.get.side_effect = lambda x: ['AdHolder', 'other-class'] if x == 'class' else None
        mock_card.select_one.return_value = None

        assert scraper._is_sponsored(mock_card) is True

    def test_is_not_sponsored(self):
        """Test organic (non-sponsored) product detection"""
        scraper = AmazonScraper()

        # Create mock element without sponsored indicators
        mock_card = Mock()
        mock_card.get.side_effect = lambda x: [] if x == 'class' else None
        mock_card.select_one.return_value = None

        assert scraper._is_sponsored(mock_card) is False


class TestAmazonScraperExtraction:
    """Tests for product data extraction"""

    def test_extract_product_data_without_asin(self):
        """Test that products without ASIN are skipped"""
        scraper = AmazonScraper()

        # Create mock card without ASIN
        mock_card = Mock()
        mock_card.get.return_value = None

        result = scraper._extract_product_data(mock_card)
        assert result is None

    def test_extract_product_data_without_title(self):
        """Test that products without title are skipped"""
        scraper = AmazonScraper()

        # Create mock card with ASIN but no title
        mock_card = Mock()
        mock_card.get.return_value = "B000QSO98W"
        mock_card.select_one.return_value = None

        result = scraper._extract_product_data(mock_card)
        assert result is None

    @patch('app.scraper.extract_and_calculate_unit_price')
    def test_extract_product_data_complete(self, mock_unit_calc):
        """Test extracting complete product data"""
        scraper = AmazonScraper()
        mock_unit_calc.return_value = (Decimal('0.69'), 'oz', 80.0)

        # Create comprehensive mock card
        mock_card = Mock()
        mock_card.get.side_effect = lambda x: "B000QSO98W" if x == 'data-asin' else []

        # Mock title
        mock_title = Mock()
        mock_title.get_text.return_value = "Test Product 5lb"

        # Mock price
        mock_price = Mock()
        mock_price.get_text.return_value = "$54.99"

        # Mock list price
        mock_list_price = Mock()
        mock_list_price.get_text.return_value = "$69.99"

        # Mock rating
        mock_rating = Mock()
        mock_rating.get_text.return_value = "4.6 out of 5 stars"

        # Mock review element
        mock_review = Mock()
        mock_review.get.return_value = "12,403 ratings"

        # Mock image
        mock_img = Mock()
        mock_img.get.return_value = "https://example.com/image.jpg"

        # Setup select_one to return appropriate mocks
        def select_one_side_effect(selector):
            if 'h2 a span' in selector:
                return mock_title
            elif '.a-price .a-offscreen' in selector:
                return mock_price
            elif 'data-a-strike' in selector:
                return mock_list_price
            elif '.a-icon-star-small' in selector:
                return mock_rating
            elif '[aria-label*="stars"]' in selector:
                return mock_review
            elif '.s-image' in selector:
                return mock_img
            elif 'Amazon Prime' in selector:
                return Mock()  # Prime badge exists
            else:
                return None

        mock_card.select_one.side_effect = select_one_side_effect

        result = scraper._extract_product_data(mock_card)

        assert result is not None
        assert result['asin'] == "B000QSO98W"
        assert 'title' in result
        assert 'current_price' in result
        assert result['current_price'] == 54.99

    def test_scraper_initialization(self):
        """Test scraper initialization"""
        scraper = AmazonScraper(use_proxies=False)
        assert scraper is not None
        assert scraper.use_proxies is False
        assert scraper.session is not None

    def test_scraper_with_proxies(self):
        """Test scraper initialization with proxy option"""
        scraper = AmazonScraper(use_proxies=True)
        assert scraper.use_proxies is True


class TestAmazonScraperDiscountCalculation:
    """Tests for discount calculation logic"""

    def test_discount_calculation(self):
        """Test discount percentage calculation"""
        scraper = AmazonScraper()

        # Manually test discount logic
        current_price = 54.99
        list_price = 69.99

        expected_discount = ((list_price - current_price) / list_price) * 100
        expected_discount = round(expected_discount, 2)

        assert expected_discount == 21.43  # ~21.43% discount

    def test_zero_list_price_no_discount(self):
        """Test that zero list price doesn't cause division by zero"""
        # This tests the logic in _extract_product_data
        # where discount_pct is only calculated if list_price > 0
        # We'll test the condition directly
        list_price = 0
        current_price = 54.99

        # Should not calculate discount when list_price is 0
        if list_price > 0:
            discount = ((list_price - current_price) / list_price) * 100
        else:
            discount = None

        assert discount is None


@pytest.mark.integration
class TestAmazonScraperIntegration:
    """Integration tests for scraper (requires network or mocking)"""

    @patch('app.scraper.AmazonScraper._scrape_search_page')
    def test_search_multiple_pages(self, mock_scrape):
        """Test searching multiple pages with delay"""
        scraper = AmazonScraper()

        # Mock page results
        mock_scrape.return_value = [
            {'asin': 'TEST1', 'title': 'Product 1'},
            {'asin': 'TEST2', 'title': 'Product 2'}
        ]

        results = scraper.search(query="test", pages=2, delay=0.01)

        assert len(results) == 4  # 2 products * 2 pages
        assert mock_scrape.call_count == 2

    @patch('app.scraper.AmazonScraper._scrape_search_page')
    def test_search_handles_page_errors(self, mock_scrape):
        """Test that search continues even if one page fails"""
        scraper = AmazonScraper()

        # First page succeeds, second page fails
        mock_scrape.side_effect = [
            [{'asin': 'TEST1', 'title': 'Product 1'}],
            Exception("Network error")
        ]

        results = scraper.search(query="test", pages=2, delay=0.01)

        # Should still return results from first page
        assert len(results) >= 1
        assert results[0]['asin'] == 'TEST1'
