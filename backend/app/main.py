"""
SmartAmazon Search Platform - Main Application

FastAPI backend server for the Amazon deal intelligence platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

from .api.routes import router as api_router
from .database import init_db

# Create FastAPI app
app = FastAPI(
    title="SmartAmazon Search API",
    description="Intelligent Amazon search without the BS - find true deals with unit price comparison",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api", tags=["search"])


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on startup
    """
    print("🚀 Starting SmartAmazon Search API...")
    print("📊 Initializing database...")
    init_db()
    print("✅ Database initialized")
    print("🔍 API ready at http://localhost:8000/api/docs")


@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "SmartAmazon Search API",
        "version": "1.0.0",
        "description": "Amazon search without sponsored noise - find true deals with unit price comparison",
        "docs": "/api/docs",
        "endpoints": {
            "search": "/api/search?q=protein+powder",
            "product": "/api/product/{asin}",
            "compare": "/api/compare",
            "categories": "/api/categories",
            "brands": "/api/brands"
        },
        "features": [
            "✅ Zero sponsored content filtering",
            "✅ True unit price comparison ($/oz, $/count)",
            "✅ Advanced filtering (price, rating, Prime, discount)",
            "✅ Hidden gem discovery algorithm",
            "✅ Price history tracking",
            "✅ Side-by-side product comparison"
        ]
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "smartamazon-api"}


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "type": type(exc).__name__
        }
    )


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
