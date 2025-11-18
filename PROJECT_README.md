# SmartAmazon Search & Deal Intelligence Platform

**Version:** 1.0.0
**Status:** MVP Complete

> The Amazon search engine Amazon should have built - minus the BS.

## Overview

SmartAmazon is an intelligent search platform that helps consumers find the best Amazon deals by:

- **Filtering out sponsored content** (30-60% of Amazon's results)
- **Calculating true unit economics** ($/oz, $/count comparison)
- **Discovering hidden gems** - great products buried by Amazon's algorithm
- **Providing advanced filtering** that Amazon refuses to implement

## Features

### Core Features (MVP)

- ✅ **Zero Sponsored Clutter**: Filter out all sponsored listings by default
- ✅ **True Unit Price Comparison**: Normalize all products to $/oz, $/count for fair comparison
- ✅ **Advanced Filtering**:
  - Price range (min/max)
  - Discount percentage (20%+, 50%+, 75%+)
  - Star rating (3+, 4+, 4.5+)
  - Prime eligible only
  - Hide/show sponsored
- ✅ **Smart Sorting**:
  - Best unit price (default)
  - Highest discount
  - Best rating
  - Most reviews
  - Hidden gems
- ✅ **Responsive Design**: Works on desktop, tablet, and mobile
- ✅ **Product Details**: Price history, similar products, deal quality
- ✅ **Side-by-Side Comparison**: Compare up to 10 products

## Tech Stack

### Backend
- **Framework**: FastAPI (Python 3.11)
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **ORM**: SQLAlchemy
- **Scraping**: BeautifulSoup4 + Requests (mock scraper for demo)

### Frontend
- **Framework**: Next.js 14 (React 18)
- **Styling**: Tailwind CSS
- **HTTP Client**: Native Fetch API
- **Deployment**: Vercel-ready

### Infrastructure
- **Containerization**: Docker + Docker Compose
- **Reverse Proxy**: Nginx (production)

## Project Structure

```
smartamazon/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes.py          # API endpoints
│   │   ├── database.py             # Database config
│   │   ├── models.py               # SQLAlchemy models
│   │   ├── schemas.py              # Pydantic schemas
│   │   ├── scraper.py              # Amazon scraper
│   │   ├── unit_calculator.py     # Unit price logic
│   │   └── main.py                 # FastAPI app
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── components/
│   │   ├── Header.js
│   │   ├── SearchBar.js
│   │   ├── ProductCard.js
│   │   ├── ProductGrid.js
│   │   ├── FilterSidebar.js
│   │   └── SortDropdown.js
│   ├── pages/
│   │   ├── index.js                # Home page
│   │   ├── search.js               # Search results
│   │   └── _app.js
│   ├── styles/
│   │   └── globals.css
│   ├── utils/
│   │   └── api.js                  # API client
│   ├── package.json
│   ├── Dockerfile
│   └── .env.example
├── database/
│   └── schema.sql                  # Database schema
├── docker-compose.yml
└── PROJECT_README.md
```

## Installation & Setup

### Option 1: Docker Compose (Recommended)

**Prerequisites:**
- Docker Desktop installed
- Docker Compose installed

**Steps:**

1. Clone the repository:
```bash
git clone <repository-url>
cd smartamazon
```

2. Create environment files:
```bash
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

3. Start all services:
```bash
docker-compose up -d
```

4. Initialize the database:
```bash
docker-compose exec postgres psql -U postgres -d smartamazon -f /docker-entrypoint-initdb.d/schema.sql
```

5. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/api/docs

### Option 2: Manual Setup

#### Backend Setup

1. Create a virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL:
```bash
createdb smartamazon
psql -d smartamazon -f ../database/schema.sql
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your database credentials
```

5. Run the backend:
```bash
uvicorn app.main:app --reload
```

#### Frontend Setup

1. Install dependencies:
```bash
cd frontend
npm install
```

2. Configure environment:
```bash
cp .env.example .env.local
```

3. Run the development server:
```bash
npm run dev
```

## Usage

### Basic Search

1. Go to http://localhost:3000
2. Enter a search query (e.g., "protein powder")
3. View results sorted by best unit price
4. Click "View on Amazon" to purchase

### Advanced Filtering

1. Use the sidebar filters to refine results:
   - Set price range
   - Filter by discount percentage
   - Select minimum rating
   - Toggle Prime-only
   - Hide sponsored ads

2. Sort results by:
   - Best unit price (default)
   - Highest discount
   - Best rating
   - Most reviews
   - Hidden gems

### Product Comparison

1. Click "Add to Compare" on product cards
2. Navigate to `/compare` page
3. View side-by-side comparison
4. See which product wins in each category

## API Documentation

### Endpoints

**Search Products**
```
GET /api/search?q=protein+powder&sort=unit_price_asc&min_rating=4.0&prime_only=true
```

**Get Product Details**
```
GET /api/product/{asin}
```

**Compare Products**
```
POST /api/compare
{
  "asins": ["B001", "B002", "B003"]
}
```

**Get Categories**
```
GET /api/categories
```

**Get Brands**
```
GET /api/brands?category=Protein+Powder
```

Full API documentation available at: http://localhost:8000/api/docs

## Development

### Running Tests

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Backend linting
cd backend
flake8 app/
black app/

# Frontend linting
cd frontend
npm run lint
```

### Database Migrations

```bash
# Create migration
cd backend
alembic revision --autogenerate -m "description"

# Apply migration
alembic upgrade head
```

## Unit Price Calculation

The core feature of this platform is accurate unit price calculation. Here's how it works:

### Extraction

1. Parse product title for quantity and unit (e.g., "5 lb", "24 oz", "12 count")
2. Use regex patterns to identify:
   - Weight: oz, lb, g, kg
   - Volume: fl oz, ml, L, gal
   - Count: pack, count, pieces

### Normalization

1. Convert all weights to ounces (oz)
2. Convert all volumes to fluid ounces (fl oz)
3. Keep count-based as is

### Calculation

```python
unit_price = product_price / normalized_quantity
```

### Example

```
Product: "Optimum Nutrition Whey Protein, 5 lb"
Price: $54.99
Calculation: 5 lb × 16 = 80 oz
Unit Price: $54.99 / 80 = $0.69/oz
```

## Scraping Strategy

**Current (MVP):** Mock scraper returning sample data

**Production:**
1. Use Amazon Product Advertising API (primary)
2. Fall back to web scraping with:
   - Rotating residential proxies
   - Request throttling (1 req/sec)
   - Randomized user agents
   - Headless browser (Playwright)

**Legal Compliance:**
- Use official API when possible
- Respect robots.txt
- Implement rate limiting
- No content caching (hotlink only)
- Clear "not affiliated with Amazon" disclaimers

## Monetization

### Amazon Associates Program

- All Amazon links tagged with affiliate ID
- 1-10% commission on purchases
- Transparent disclosure on all pages

### Premium Tier (Future)

- $4.99/month or $39/year
- Features:
  - Ad-free experience
  - Unlimited price alerts
  - Advanced analytics
  - API access

## Roadmap

### Phase 2 (Next 4-6 weeks)
- [ ] Price history charts
- [ ] Hidden gem scoring algorithm
- [ ] Email price drop alerts
- [ ] Bulk size comparison tool
- [ ] Subscribe & Save calculator

### Phase 3 (8-12 weeks)
- [ ] Multi-country support (CA, UK, DE)
- [ ] User accounts & preferences
- [ ] Saved searches
- [ ] Mobile apps (iOS/Android)
- [ ] Chrome extension

### Phase 4 (Future)
- [ ] ML-powered recommendations
- [ ] Community reviews
- [ ] Deal sharing
- [ ] Category deep dives

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Disclaimer

**SmartAmazon is not affiliated with Amazon.com, Inc. or its affiliates.**

We are an independent third-party service that helps consumers find deals on Amazon. We earn from qualifying purchases through the Amazon Associates program.

## Support

For issues, questions, or feature requests, please:

- Open an issue on GitHub
- Email: support@smartamazon.com
- Twitter: @smartamazon

## Acknowledgments

Built with ❤️ for smart shoppers who are tired of sponsored spam.

Special thanks to:
- The FastAPI team for an amazing framework
- Next.js team for making React development enjoyable
- The open-source community

---

**Last Updated:** November 18, 2025
**Version:** 1.0.0 (MVP)
