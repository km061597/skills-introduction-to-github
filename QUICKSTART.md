# SmartAmazon - Quick Start Guide

Get the SmartAmazon platform up and running in 5 minutes!

## Prerequisites

- Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop/))
- Git installed
- 8GB RAM minimum
- 10GB free disk space

## Quick Start (Docker)

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd skills-introduction-to-github

# Copy environment files
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
```

### 2. Launch the Application

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
# Check status
docker-compose ps
```

### 3. Initialize Database

```bash
# Run database schema
docker-compose exec postgres psql -U postgres -d smartamazon -f /docker-entrypoint-initdb.d/schema.sql
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs

## Manual Setup (Without Docker)

### Backend

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up database
createdb smartamazon
psql -d smartamazon -f ../database/schema.sql

# Configure environment
cp .env.example .env
# Edit .env and update DATABASE_URL if needed

# Run server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### Frontend

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local

# Run development server
npm run dev
```

Frontend will be available at http://localhost:3000

## First Search

1. Open http://localhost:3000
2. Type "protein powder" in the search box
3. Click Search
4. Explore the results!

## Features to Try

- **Filter by Price**: Use the sidebar to set min/max price
- **Sort by Unit Price**: See products ranked by $/oz
- **Hide Sponsored**: Toggle to see/hide sponsored products
- **Filter by Rating**: Only show 4+ star products
- **Prime Only**: Filter to Prime-eligible items

## Common Issues

### Port Already in Use

If ports 3000, 8000, or 5432 are already in use:

```bash
# Stop conflicting services or change ports in docker-compose.yml
docker-compose down
# Edit docker-compose.yml to use different ports
docker-compose up -d
```

### Database Connection Error

```bash
# Restart database service
docker-compose restart postgres

# Check logs
docker-compose logs postgres
```

### Frontend Not Loading

```bash
# Rebuild frontend
docker-compose down
docker-compose up -d --build frontend
```

## Sample Searches

Try these searches to see the platform in action:

- `protein powder` - See unit price comparison
- `coffee beans` - Compare by weight
- `laundry detergent` - Bulk size analysis
- `vitamins` - Count-based comparison
- `dog food` - Price filtering

## Stopping the Application

```bash
# Stop all services
docker-compose down

# Stop and remove volumes (fresh start)
docker-compose down -v
```

## Next Steps

- Read the full documentation in [PROJECT_README.md](PROJECT_README.md)
- Explore the API at http://localhost:8000/api/docs
- Check out the source code structure
- Customize the frontend styling
- Add real Amazon scraping (see PRD)

## Getting Help

- Check logs: `docker-compose logs -f`
- API health: http://localhost:8000/health
- Database connection: `docker-compose exec postgres psql -U postgres -d smartamazon`

## Development

### Hot Reload

Both frontend and backend support hot reload:
- Edit files in `backend/app/` → API restarts automatically
- Edit files in `frontend/` → Browser refreshes automatically

### Adding Sample Data

```bash
# Access database
docker-compose exec postgres psql -U postgres -d smartamazon

# Insert sample products (already included in schema.sql)
# See database/schema.sql for examples
```

### Testing API Endpoints

Visit http://localhost:8000/api/docs for interactive API documentation (Swagger UI)

Example API calls:

```bash
# Search
curl "http://localhost:8000/api/search?q=protein&sort=unit_price_asc"

# Get product
curl "http://localhost:8000/api/product/B000001"

# Categories
curl "http://localhost:8000/api/categories"
```

---

**Time to First Search:** < 5 minutes

**Need Help?** Open an issue or check PROJECT_README.md for detailed documentation.
