"""
SmartAmazon Search Platform - Main Application

Enterprise-grade FastAPI backend with:
- Comprehensive error handling
- Structured logging
- Rate limiting
- Security headers
- Prometheus metrics
- Health checks
- JWT authentication
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import uvicorn
import os

from .api.routes import router as api_router
from .database import init_db
from .init_data import init_sample_data
from .logging_config import setup_logging, get_logger
from .middleware import (
    RequestLoggingMiddleware,
    RateLimitMiddleware,
    SecurityHeadersMiddleware,
    PrometheusMiddleware
)
from .monitoring import get_metrics, HealthCheck, set_app_info
from .exceptions import SmartAmazonException, handle_exception


# Initialize logging
setup_logging(level=os.getenv("LOG_LEVEL", "INFO"))
logger = get_logger(__name__)

# Application metadata
VERSION = os.getenv("APP_VERSION", "1.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Create FastAPI app
app = FastAPI(
    title="SmartAmazon Search API",
    description="Enterprise-grade Amazon deal intelligence platform - find true deals without sponsored noise",
    version=VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Add middleware (order matters!)
app.add_middleware(PrometheusMiddleware)  # First - metrics collection
app.add_middleware(SecurityHeadersMiddleware)  # Security headers
app.add_middleware(RequestLoggingMiddleware)  # Request logging
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
)  # Rate limiting

# Configure CORS
allowed_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api", tags=["search"])


# Exception handlers
@app.exception_handler(SmartAmazonException)
async def smartamazon_exception_handler(request: Request, exc: SmartAmazonException):
    """
    Handle custom SmartAmazon exceptions
    """
    logger.error(
        f"SmartAmazon exception: {exc.message}",
        extra={'extra_data': {
            'error_code': exc.error_code,
            'details': exc.details,
            'path': str(request.url)
        }},
        exc_info=True
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=handle_exception(exc)
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic validation errors
    """
    logger.warning(
        "Validation error",
        extra={'extra_data': {
            'errors': exc.errors(),
            'path': str(request.url)
        }}
    )

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors()
            }
        }
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """
    Handle HTTP exceptions
    """
    logger.error(
        f"HTTP exception: {exc.detail}",
        extra={'extra_data': {
            'status_code': exc.status_code,
            'path': str(request.url)
        }}
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": "HTTP_ERROR",
                "message": exc.detail or "An error occurred"
            }
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for uncaught exceptions
    """
    logger.error(
        "Unhandled exception",
        extra={'extra_data': {
            'exception_type': type(exc).__name__,
            'path': str(request.url)
        }},
        exc_info=True
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An internal server error occurred",
                "detail": str(exc) if ENVIRONMENT == "development" else "Please contact support"
            }
        }
    )


# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup
    """
    logger.info("🚀 Starting SmartAmazon Search API...")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Version: {VERSION}")

    # Set application info for monitoring
    set_app_info(version=VERSION, environment=ENVIRONMENT)

    # Initialize database
    logger.info("📊 Initializing database...")
    try:
        init_db()
        logger.info("✅ Database tables created")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}", exc_info=True)
        raise

    # Load sample data
    if ENVIRONMENT in ["development", "staging"]:
        logger.info("📦 Loading sample data...")
        try:
            init_sample_data()
            logger.info("✅ Sample data loaded")
        except Exception as e:
            logger.warning(f"⚠️ Sample data loading failed: {e}")

    logger.info("🔍 API ready!")
    logger.info(f"📖 API Docs: http://localhost:8000/api/docs")
    logger.info(f"📊 Metrics: http://localhost:8000/metrics")
    logger.info(f"💚 Health: http://localhost:8000/health")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Cleanup on shutdown
    """
    logger.info("👋 Shutting down SmartAmazon Search API...")
    # Add cleanup tasks here if needed


# Core endpoints
@app.get("/")
async def root():
    """
    Root endpoint with API information
    """
    return {
        "name": "SmartAmazon Search API",
        "version": VERSION,
        "environment": ENVIRONMENT,
        "description": "Enterprise Amazon deal intelligence - find true deals without sponsored noise",
        "docs": "/api/docs",
        "metrics": "/metrics",
        "health": {
            "basic": "/health",
            "detailed": "/health/detailed"
        },
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
            "✅ Deal quality scoring",
            "✅ Price history tracking",
            "✅ Side-by-side product comparison",
            "✅ Email price alerts",
            "✅ Rate limiting & security",
            "✅ Prometheus metrics",
            "✅ Comprehensive logging"
        ]
    }


@app.get("/health")
async def health_check():
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "service": "smartamazon-api",
        "version": VERSION,
        "environment": ENVIRONMENT
    }


@app.get("/health/detailed")
async def detailed_health_check():
    """
    Detailed health check with all services
    """
    health = HealthCheck.get_comprehensive_health()
    status_code = 200 if health["status"] == "healthy" else 503
    return JSONResponse(content=health, status_code=status_code)


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    """
    return get_metrics()


@app.get("/version")
async def version():
    """
    Get application version information
    """
    return {
        "version": VERSION,
        "environment": ENVIRONMENT,
        "python_version": os.sys.version,
        "build_timestamp": os.getenv("BUILD_TIMESTAMP", "unknown")
    }


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=ENVIRONMENT == "development",
        log_level="info",
        access_log=True
    )
