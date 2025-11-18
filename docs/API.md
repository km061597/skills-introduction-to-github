# SmartAmazon API Documentation

**Version:** 1.0.0
**Base URL:** `http://localhost:8000/api`
**Production URL:** `https://api.smartamazon.com/api`

## Table of Contents

- [Authentication](#authentication)
- [Rate Limiting](#rate-limiting)
- [Error Handling](#error-handling)
- [Endpoints](#endpoints)
  - [Health & Monitoring](#health--monitoring)
  - [Search](#search)
  - [Products](#products)
  - [Categories](#categories)
  - [Price History](#price-history)
  - [Comparison](#comparison)
- [Data Models](#data-models)
- [Pagination](#pagination)
- [Filtering & Sorting](#filtering--sorting)

---

## Authentication

Currently, the API is public and does not require authentication for read operations.

**Future:** JWT-based authentication will be required for:
- Price alerts
- Saved searches
- User preferences
- Admin operations

### Headers

```http
Authorization: Bearer <token>
X-Request-ID: <unique-request-id>
```

---

## Rate Limiting

**Default Limits:**
- 60 requests per minute per IP address
- Rate limit headers are included in all responses

**Response Headers:**
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1640995200
```

**429 Too Many Requests Response:**
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again in 60 seconds.",
    "details": {
      "retry_after": 60
    }
  }
}
```

---

## Error Handling

All errors follow a consistent JSON format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    }
  }
}
```

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request succeeded |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request parameters |
| 401 | Unauthorized | Authentication required |
| 403 | Forbidden | Insufficient permissions |
| 404 | Not Found | Resource not found |
| 422 | Unprocessable Entity | Validation error |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Server error |
| 503 | Service Unavailable | Service temporarily unavailable |

### Error Codes

| Code | Description |
|------|-------------|
| `VALIDATION_ERROR` | Input validation failed |
| `NOT_FOUND` | Resource not found |
| `DATABASE_ERROR` | Database operation failed |
| `SCRAPER_ERROR` | Amazon scraping failed |
| `RATE_LIMIT_EXCEEDED` | Too many requests |
| `CACHE_ERROR` | Redis cache error |
| `AUTHENTICATION_ERROR` | Authentication failed |
| `AUTHORIZATION_ERROR` | Insufficient permissions |
| `SERVICE_UNAVAILABLE` | Service temporarily down |

---

## Endpoints

### Health & Monitoring

#### GET /health

Health check endpoint for monitoring and load balancers.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": 1640995200.123,
  "version": "1.0.0",
  "environment": "production",
  "checks": {
    "database": {
      "status": "healthy",
      "message": "Database connection OK"
    },
    "redis": {
      "status": "healthy",
      "message": "Redis connection OK",
      "stats": {
        "hits": 1000,
        "misses": 100,
        "hit_rate": 0.91
      }
    },
    "disk": {
      "status": "healthy",
      "message": "Disk space OK: 45.2% used",
      "percent_used": 45.2
    },
    "memory": {
      "status": "healthy",
      "message": "Memory OK: 62.3% used",
      "percent_used": 62.3
    }
  }
}
```

**Status Values:**
- `healthy` - All systems operational
- `degraded` - Some non-critical issues (e.g., disk > 80%)
- `unhealthy` - Critical issues detected

---

#### GET /metrics

Prometheus metrics endpoint for monitoring.

**Response:** (Prometheus text format)
```
# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",endpoint="/api/search",status="200"} 1523

# HELP http_request_duration_seconds HTTP request latency
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",endpoint="/api/search",le="0.1"} 1200
```

---

### Search

#### GET /search

Search for products by keyword with advanced filtering and sorting.

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `q` | string | Yes | - | Search query |
| `sort` | string | No | `unit_price_asc` | Sort option |
| `min_price` | number | No | - | Minimum price filter |
| `max_price` | number | No | - | Maximum price filter |
| `min_unit_price` | number | No | - | Minimum unit price filter |
| `max_unit_price` | number | No | - | Maximum unit price filter |
| `min_rating` | number | No | - | Minimum rating (0-5) |
| `min_review_count` | number | No | - | Minimum review count |
| `prime_only` | boolean | No | `false` | Filter Prime-eligible only |
| `hide_sponsored` | boolean | No | `true` | Hide sponsored listings |
| `min_discount` | number | No | - | Minimum discount percentage (0-100) |
| `brands` | array[string] | No | - | Filter by brand names |
| `exclude_brands` | array[string] | No | - | Exclude brand names |
| `in_stock_only` | boolean | No | `false` | Show only in-stock items |
| `page` | integer | No | `1` | Page number (≥1) |
| `limit` | integer | No | `48` | Results per page (1-100) |

**Sort Options:**
- `unit_price_asc` - Lowest unit price first
- `unit_price_desc` - Highest unit price first
- `price_asc` - Lowest price first
- `price_desc` - Highest price first
- `discount_desc` - Highest discount first
- `rating_desc` - Highest rating first
- `review_count_desc` - Most reviewed first
- `hidden_gem_desc` - Hidden gems first

**Example Request:**
```http
GET /api/search?q=protein+powder&sort=unit_price_asc&min_rating=4.5&prime_only=true&page=1&limit=24
```

**Response:**
```json
{
  "results": [
    {
      "asin": "B000QSO98W",
      "title": "Optimum Nutrition Gold Standard 100% Whey Protein Powder, Chocolate, 5 Pound",
      "brand": "Optimum Nutrition",
      "category": "Protein Powder",
      "current_price": 54.99,
      "list_price": 69.99,
      "unit_price": 0.69,
      "unit_type": "oz",
      "quantity": 80.0,
      "discount_pct": 21.43,
      "rating": 4.6,
      "review_count": 124030,
      "verified_review_count": 85000,
      "image_url": "https://m.media-amazon.com/images/I/...",
      "amazon_url": "https://amazon.com/dp/B000QSO98W",
      "is_prime": true,
      "is_sponsored": false,
      "subscribe_save_pct": 15.0,
      "in_stock": true,
      "hidden_gem_score": 85,
      "deal_quality_score": 92,
      "is_best_value": true,
      "savings_vs_category": 12.50,
      "last_scraped_at": "2025-01-18T10:30:00Z",
      "created_at": "2025-01-15T08:00:00Z",
      "updated_at": "2025-01-18T10:30:00Z"
    }
  ],
  "total": 150,
  "page": 1,
  "pages": 7,
  "sponsored_hidden": 12,
  "query": "protein powder"
}
```

---

### Products

#### GET /products/{asin}

Get detailed information about a specific product.

**Path Parameters:**
- `asin` (string, required) - Amazon Standard Identification Number

**Example Request:**
```http
GET /api/products/B000QSO98W
```

**Response:**
```json
{
  "asin": "B000QSO98W",
  "title": "Optimum Nutrition Gold Standard 100% Whey Protein Powder, Chocolate, 5 Pound",
  "brand": "Optimum Nutrition",
  "category": "Protein Powder",
  "current_price": 54.99,
  "list_price": 69.99,
  "unit_price": 0.69,
  "unit_type": "oz",
  "quantity": 80.0,
  "discount_pct": 21.43,
  "rating": 4.6,
  "review_count": 124030,
  "image_url": "https://m.media-amazon.com/images/I/...",
  "amazon_url": "https://amazon.com/dp/B000QSO98W",
  "is_prime": true,
  "is_best_value": true,
  "savings_vs_category": 12.50,
  "last_scraped_at": "2025-01-18T10:30:00Z",
  "created_at": "2025-01-15T08:00:00Z",
  "updated_at": "2025-01-18T10:30:00Z",
  "price_history": [
    {
      "id": 1,
      "asin": "B000QSO98W",
      "price": 54.99,
      "unit_price": 0.69,
      "recorded_at": "2025-01-18T10:30:00Z"
    }
  ],
  "similar_products": []
}
```

**Error Responses:**
- `404 Not Found` - Product not found

---

### Categories

#### GET /categories

Get statistics for all product categories.

**Response:**
```json
[
  {
    "category": "Protein Powder",
    "median_price": 54.99,
    "median_unit_price": 0.75,
    "avg_rating": 4.5,
    "product_count": 150,
    "last_updated": "2025-01-18T10:30:00Z"
  },
  {
    "category": "Pre-Workout",
    "median_price": 29.99,
    "median_unit_price": 0.50,
    "avg_rating": 4.3,
    "product_count": 85,
    "last_updated": "2025-01-18T10:30:00Z"
  }
]
```

---

#### GET /categories/{category}

Get statistics for a specific category.

**Path Parameters:**
- `category` (string, required) - Category name

**Example Request:**
```http
GET /api/categories/Protein%20Powder
```

**Response:**
```json
{
  "category": "Protein Powder",
  "median_price": 54.99,
  "median_unit_price": 0.75,
  "avg_rating": 4.5,
  "product_count": 150,
  "last_updated": "2025-01-18T10:30:00Z"
}
```

---

### Price History

#### GET /products/{asin}/history

Get price history for a product.

**Path Parameters:**
- `asin` (string, required) - Amazon Standard Identification Number

**Query Parameters:**
- `days` (integer, optional, default: 30) - Number of days to retrieve

**Example Request:**
```http
GET /api/products/B000QSO98W/history?days=30
```

**Response:**
```json
{
  "asin": "B000QSO98W",
  "history": [
    {
      "date": "2025-01-01T00:00:00Z",
      "price": 59.99,
      "unit_price": 0.75,
      "is_prime": true,
      "in_stock": true
    },
    {
      "date": "2025-01-15T00:00:00Z",
      "price": 54.99,
      "unit_price": 0.69,
      "is_prime": true,
      "in_stock": true
    }
  ],
  "statistics": {
    "min_price": 54.99,
    "max_price": 69.99,
    "avg_price": 60.25,
    "current_price": 54.99,
    "price_change_pct": -8.33,
    "is_lowest": true,
    "is_highest": false,
    "data_points": 15,
    "days_analyzed": 30,
    "trend": "down"
  }
}
```

---

### Comparison

#### POST /compare

Compare multiple products side-by-side.

**Request Body:**
```json
{
  "asins": [
    "B000QSO98W",
    "B00SCO8XM0",
    "B001RZP6LW"
  ]
}
```

**Constraints:**
- Minimum 2 ASINs
- Maximum 10 ASINs

**Response:**
```json
{
  "products": [
    {
      "asin": "B000QSO98W",
      "title": "Optimum Nutrition Gold Standard...",
      "current_price": 54.99,
      "unit_price": 0.69,
      "rating": 4.6,
      "review_count": 124030
    },
    {
      "asin": "B00SCO8XM0",
      "title": "Dymatize ISO100 Hydrolyzed...",
      "current_price": 44.99,
      "unit_price": 0.94,
      "rating": 4.5,
      "review_count": 82340
    }
  ],
  "best_unit_price_asin": "B000QSO98W",
  "best_rating_asin": "B000QSO98W",
  "best_value_asin": "B000QSO98W"
}
```

**Error Responses:**
- `422 Unprocessable Entity` - Too few/many ASINs
- `404 Not Found` - One or more products not found

---

## Data Models

### Product

```typescript
{
  asin: string;                    // Amazon Standard Identification Number
  title: string;                   // Product title
  brand?: string;                  // Brand name
  category?: string;               // Product category
  current_price?: number;          // Current price in USD
  list_price?: number;             // Original/list price
  unit_price?: number;             // Price per unit (oz, count, etc.)
  unit_type?: string;              // Unit type (oz, lb, count, serving)
  quantity?: number;               // Quantity in package
  discount_pct?: number;           // Discount percentage
  rating?: number;                 // Average rating (0-5)
  review_count: number;            // Total review count
  verified_review_count: number;   // Verified review count
  image_url?: string;              // Product image URL
  amazon_url?: string;             // Amazon product page URL
  is_prime: boolean;               // Prime eligible
  is_sponsored: boolean;           // Sponsored listing
  subscribe_save_pct?: number;     // Subscribe & Save discount
  in_stock: boolean;               // In stock status
  hidden_gem_score?: number;       // Hidden gem score (0-100)
  deal_quality_score?: number;     // Deal quality score (0-100)
  is_best_value?: boolean;         // Best value in category
  savings_vs_category?: number;    // Savings vs category median
  last_scraped_at: datetime;       // Last scrape timestamp
  created_at: datetime;            // Creation timestamp
  updated_at: datetime;            // Last update timestamp
}
```

### Price History Entry

```typescript
{
  id: number;                      // History entry ID
  asin: string;                    // Product ASIN
  price: number;                   // Price at this time
  unit_price?: number;             // Unit price at this time
  recorded_at: datetime;           // Timestamp of recording
}
```

### Category Statistics

```typescript
{
  category: string;                // Category name
  median_price?: number;           // Median price in category
  median_unit_price?: number;      // Median unit price
  avg_rating?: number;             // Average rating
  product_count: number;           // Number of products
  last_updated: datetime;          // Last update timestamp
}
```

---

## Pagination

All list endpoints support pagination with consistent parameters:

**Request:**
```http
GET /api/search?q=protein&page=2&limit=24
```

**Response:**
```json
{
  "results": [...],
  "total": 150,
  "page": 2,
  "pages": 7
}
```

**Pagination Fields:**
- `page` - Current page number (1-indexed)
- `pages` - Total number of pages
- `total` - Total number of results
- `limit` - Results per page

---

## Filtering & Sorting

### Price Filters

```http
GET /api/search?q=protein&min_price=30&max_price=70
```

### Unit Price Filters

```http
GET /api/search?q=protein&min_unit_price=0.50&max_unit_price=1.00
```

### Rating Filters

```http
GET /api/search?q=protein&min_rating=4.5&min_review_count=1000
```

### Brand Filters

```http
GET /api/search?q=protein&brands=Optimum+Nutrition,Dymatize
GET /api/search?q=protein&exclude_brands=Generic
```

### Boolean Filters

```http
GET /api/search?q=protein&prime_only=true&in_stock_only=true&hide_sponsored=true
```

### Discount Filter

```http
GET /api/search?q=protein&min_discount=20
```

---

## Code Examples

### Python

```python
import requests

# Search for products
response = requests.get(
    "http://localhost:8000/api/search",
    params={
        "q": "protein powder",
        "sort": "unit_price_asc",
        "min_rating": 4.5,
        "prime_only": True,
        "limit": 24
    }
)

data = response.json()
for product in data["results"]:
    print(f"{product['title']}: ${product['unit_price']}/{product['unit_type']}")
```

### JavaScript

```javascript
const searchProducts = async (query) => {
  const response = await fetch(
    `http://localhost:8000/api/search?q=${encodeURIComponent(query)}&sort=unit_price_asc`
  );

  const data = await response.json();
  return data.results;
};

// Usage
searchProducts("protein powder").then(products => {
  products.forEach(product => {
    console.log(`${product.title}: $${product.unit_price}/${product.unit_type}`);
  });
});
```

### cURL

```bash
# Simple search
curl "http://localhost:8000/api/search?q=protein+powder"

# Advanced search with filters
curl "http://localhost:8000/api/search?q=protein+powder&sort=unit_price_asc&min_rating=4.5&prime_only=true&limit=24"

# Get product details
curl "http://localhost:8000/api/products/B000QSO98W"

# Compare products
curl -X POST "http://localhost:8000/api/compare" \
  -H "Content-Type: application/json" \
  -d '{"asins": ["B000QSO98W", "B00SCO8XM0"]}'
```

---

## Best Practices

### 1. Use Unit Price for Comparisons

Always use `unit_price` instead of `current_price` to compare true value:

```http
GET /api/search?q=protein+powder&sort=unit_price_asc
```

### 2. Filter Sponsored Listings

Sponsored listings may not be the best deals:

```http
GET /api/search?q=protein&hide_sponsored=true
```

### 3. Consider Review Quality

Filter by both rating and review count for confidence:

```http
GET /api/search?q=protein&min_rating=4.5&min_review_count=1000
```

### 4. Monitor Price History

Check price history before buying to ensure you're getting a good deal:

```http
GET /api/products/B000QSO98W/history?days=90
```

### 5. Use Pagination Efficiently

Request only what you need to reduce load:

```http
GET /api/search?q=protein&limit=24&page=1
```

### 6. Cache Responses

Responses include `last_scraped_at` - cache until this time has passed significantly.

### 7. Handle Rate Limits

Implement exponential backoff when you receive 429 responses.

---

## Versioning

The API version is included in responses as `X-API-Version` header.

**Current Version:** `1.0.0`

**Deprecation Policy:**
- Deprecated endpoints will be supported for at least 6 months
- Breaking changes will result in a new major version
- Clients should monitor deprecation headers

---

## Support

**Documentation:** https://docs.smartamazon.com
**API Status:** https://status.smartamazon.com
**Issues:** https://github.com/smartamazon/api/issues

---

**Last Updated:** 2025-01-18
**Maintained By:** SmartAmazon Engineering Team
