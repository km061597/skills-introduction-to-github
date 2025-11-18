"""
Amazon Search Scraper Service

This module handles:
1. Scraping Amazon search results
2. Detecting sponsored listings
3. Extracting product data
4. Handling pagination

Note: This is a demonstration implementation. For production use:
- Use Amazon Product Advertising API when possible
- Implement proper rate limiting
- Use rotating proxies
- Handle CAPTCHAs
"""
import re
import time
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
import requests
from decimal import Decimal
from .unit_calculator import extract_and_calculate_unit_price


class AmazonScraper:
    """
    Scraper for Amazon search results
    """

    BASE_URL = "https://www.amazon.com"
    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    def __init__(self, use_proxies: bool = False):
        """
        Initialize scraper

        Args:
            use_proxies: Whether to use proxy rotation (requires proxy service)
        """
        self.use_proxies = use_proxies
        self.session = requests.Session()
        self.session.headers.update(self.HEADERS)

    def search(
        self,
        query: str,
        pages: int = 1,
        delay: float = 1.0
    ) -> List[Dict]:
        """
        Search Amazon and scrape results

        Args:
            query: Search query string
            pages: Number of pages to scrape (1-5 recommended)
            delay: Delay between requests in seconds

        Returns:
            List of product dictionaries
        """
        all_products = []

        for page in range(1, pages + 1):
            try:
                products = self._scrape_search_page(query, page)
                all_products.extend(products)

                # Respectful delay between requests
                if page < pages:
                    time.sleep(delay)

            except Exception as e:
                print(f"Error scraping page {page}: {e}")
                continue

        return all_products

    def _scrape_search_page(self, query: str, page: int = 1) -> List[Dict]:
        """
        Scrape a single search results page

        Args:
            query: Search query
            page: Page number

        Returns:
            List of product dictionaries
        """
        # Construct search URL
        url = f"{self.BASE_URL}/s"
        params = {
            'k': query,
            'page': page
        }

        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Parse HTML
            soup = BeautifulSoup(response.content, 'lxml')

            # Extract products
            products = self._extract_products(soup)

            return products

        except requests.RequestException as e:
            print(f"Request error: {e}")
            return []

    def _extract_products(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract product data from search results page

        Args:
            soup: BeautifulSoup object of page HTML

        Returns:
            List of product dictionaries
        """
        products = []

        # Find all product cards
        # Amazon uses different HTML structures, so we try multiple selectors
        product_cards = soup.select('[data-component-type="s-search-result"]')

        for card in product_cards:
            try:
                product = self._extract_product_data(card)
                if product and product.get('asin'):
                    products.append(product)
            except Exception as e:
                print(f"Error extracting product: {e}")
                continue

        return products

    def _extract_product_data(self, card) -> Optional[Dict]:
        """
        Extract data from a single product card

        Args:
            card: BeautifulSoup element of product card

        Returns:
            Dictionary with product data
        """
        product = {}

        # Extract ASIN
        asin = card.get('data-asin')
        if not asin:
            return None
        product['asin'] = asin

        # Check if sponsored
        product['is_sponsored'] = self._is_sponsored(card)

        # Extract title
        title_elem = card.select_one('h2 a span')
        if title_elem:
            product['title'] = title_elem.get_text(strip=True)
        else:
            return None  # Skip if no title

        # Extract price
        price_elem = card.select_one('.a-price .a-offscreen')
        if price_elem:
            price_text = price_elem.get_text(strip=True)
            price = self._parse_price(price_text)
            if price:
                product['current_price'] = price

        # Extract list price (was price / MSRP)
        list_price_elem = card.select_one('.a-price[data-a-strike="true"] .a-offscreen')
        if list_price_elem:
            list_price_text = list_price_elem.get_text(strip=True)
            list_price = self._parse_price(list_price_text)
            if list_price:
                product['list_price'] = list_price

        # Calculate discount
        if 'current_price' in product and 'list_price' in product:
            if product['list_price'] > 0:
                discount = ((product['list_price'] - product['current_price']) / product['list_price']) * 100
                product['discount_pct'] = round(discount, 2)

        # Extract rating
        rating_elem = card.select_one('.a-icon-star-small .a-icon-alt')
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating = self._parse_rating(rating_text)
            if rating:
                product['rating'] = rating

        # Extract review count
        review_elem = card.select_one('[aria-label*="stars"]')
        if review_elem:
            aria_label = review_elem.get('aria-label', '')
            review_count = self._parse_review_count(aria_label)
            if review_count:
                product['review_count'] = review_count

        # Extract image URL
        img_elem = card.select_one('.s-image')
        if img_elem:
            product['image_url'] = img_elem.get('src')

        # Check Prime eligibility
        prime_elem = card.select_one('[aria-label="Amazon Prime"]')
        product['is_prime'] = prime_elem is not None

        # Construct Amazon URL
        product['amazon_url'] = f"{self.BASE_URL}/dp/{asin}"

        # Extract brand (if available)
        brand_elem = card.select_one('.a-size-base-plus')
        if brand_elem:
            product['brand'] = brand_elem.get_text(strip=True)

        # Calculate unit price
        if 'current_price' in product and 'title' in product:
            unit_price, unit_type, quantity = extract_and_calculate_unit_price(
                product['title'],
                Decimal(str(product['current_price']))
            )
            if unit_price:
                product['unit_price'] = float(unit_price)
                product['unit_type'] = unit_type
                product['quantity'] = quantity

        # Stock status
        product['in_stock'] = True  # Assume in stock if listed

        return product

    def _is_sponsored(self, card) -> bool:
        """
        Detect if product card is sponsored

        Args:
            card: BeautifulSoup element

        Returns:
            True if sponsored, False otherwise
        """
        # Method 1: Check data attribute
        if card.get('data-component-type') == 'sp-sponsored-result':
            return True

        # Method 2: Check for sponsored text
        sponsored_badge = card.select_one('.s-label-popover-default')
        if sponsored_badge and 'sponsored' in sponsored_badge.get_text(strip=True).lower():
            return True

        # Method 3: Check for AdHolder class
        if 'AdHolder' in card.get('class', []):
            return True

        return False

    @staticmethod
    def _parse_price(price_text: str) -> Optional[float]:
        """
        Parse price from text

        Args:
            price_text: Price string like "$54.99"

        Returns:
            Price as float or None
        """
        if not price_text:
            return None

        # Remove currency symbols and parse
        price_clean = re.sub(r'[^0-9.]', '', price_text)
        try:
            return float(price_clean)
        except ValueError:
            return None

    @staticmethod
    def _parse_rating(rating_text: str) -> Optional[float]:
        """
        Parse rating from text

        Args:
            rating_text: Rating string like "4.6 out of 5 stars"

        Returns:
            Rating as float or None
        """
        if not rating_text:
            return None

        match = re.search(r'(\d+\.?\d*)', rating_text)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                return None
        return None

    @staticmethod
    def _parse_review_count(text: str) -> Optional[int]:
        """
        Parse review count from text

        Args:
            text: Text containing review count

        Returns:
            Review count as integer or None
        """
        if not text:
            return None

        # Look for numbers with commas (e.g., "12,403")
        match = re.search(r'([\d,]+)', text)
        if match:
            count_str = match.group(1).replace(',', '')
            try:
                return int(count_str)
            except ValueError:
                return None
        return None


# Mock scraper for development/testing without hitting Amazon
class MockAmazonScraper(AmazonScraper):
    """
    Mock scraper that returns sample data for testing
    """

    def search(self, query: str, pages: int = 1, delay: float = 1.0) -> List[Dict]:
        """
        Return mock product data

        Args:
            query: Search query (used to customize mock data)
            pages: Number of pages (affects result count)
            delay: Ignored in mock

        Returns:
            List of mock products
        """
        products = [
            {
                'asin': 'B000QSO98W',
                'title': f'Optimum Nutrition Gold Standard 100% Whey Protein Powder, {query}, 5 Pound',
                'brand': 'Optimum Nutrition',
                'current_price': 54.99,
                'list_price': 69.99,
                'discount_pct': 21.43,
                'unit_price': 0.69,
                'unit_type': 'oz',
                'quantity': 80.0,
                'rating': 4.6,
                'review_count': 124030,
                'image_url': 'https://via.placeholder.com/300',
                'amazon_url': 'https://amazon.com/dp/B000QSO98W',
                'is_prime': True,
                'is_sponsored': False,
                'in_stock': True,
                'subscribe_save_pct': 15.0
            },
            {
                'asin': 'B00SCO8XM0',
                'title': f'Dymatize ISO100 Hydrolyzed Protein Powder, {query}, 3 Pound',
                'brand': 'Dymatize',
                'current_price': 44.99,
                'list_price': 54.99,
                'discount_pct': 18.18,
                'unit_price': 0.94,
                'unit_type': 'oz',
                'quantity': 48.0,
                'rating': 4.5,
                'review_count': 82340,
                'image_url': 'https://via.placeholder.com/300',
                'amazon_url': 'https://amazon.com/dp/B00SCO8XM0',
                'is_prime': True,
                'is_sponsored': True,
                'in_stock': True,
                'subscribe_save_pct': 10.0
            },
            {
                'asin': 'B001RZP6LW',
                'title': f'MyProtein Impact Whey Protein, {query}, 2.2 Pound',
                'brand': 'MyProtein',
                'current_price': 29.99,
                'list_price': 39.99,
                'discount_pct': 25.0,
                'unit_price': 0.85,
                'unit_type': 'oz',
                'quantity': 35.2,
                'rating': 4.4,
                'review_count': 34210,
                'image_url': 'https://via.placeholder.com/300',
                'amazon_url': 'https://amazon.com/dp/B001RZP6LW',
                'is_prime': False,
                'is_sponsored': False,
                'in_stock': True,
                'subscribe_save_pct': 5.0
            },
            {
                'asin': 'B002DYJ0O6',
                'title': f'BSN SYNTHA-6 Protein Powder, {query}, 5.04 lb',
                'brand': 'BSN',
                'current_price': 49.99,
                'list_price': 59.99,
                'discount_pct': 16.67,
                'unit_price': 0.62,
                'unit_type': 'oz',
                'quantity': 80.64,
                'rating': 4.5,
                'review_count': 56780,
                'image_url': 'https://via.placeholder.com/300',
                'amazon_url': 'https://amazon.com/dp/B002DYJ0O6',
                'is_prime': True,
                'is_sponsored': True,
                'in_stock': True,
                'subscribe_save_pct': 15.0
            },
        ]

        # Multiply results by pages
        return products * pages
