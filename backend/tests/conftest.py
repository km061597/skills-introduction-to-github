"""
Pytest configuration and fixtures for SmartAmazon tests
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.database import Base, get_db
from app.models import Product, CategoryStats
from decimal import Decimal


# Test database URL (SQLite in-memory for fast tests)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

# Create test database engine
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """
    Create a fresh database session for each test
    """
    # Create tables
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Drop tables after test
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    Create a test client with dependency override
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def sample_products(db_session):
    """
    Create sample products for testing
    """
    products = [
        Product(
            asin="TEST001",
            title="Test Protein Powder 5lb",
            brand="TestBrand",
            category="Protein Powder",
            current_price=Decimal("49.99"),
            list_price=Decimal("69.99"),
            unit_price=Decimal("0.62"),
            unit_type="oz",
            unit_quantity=Decimal("80"),
            discount_pct=Decimal("28.57"),
            rating=Decimal("4.6"),
            review_count=1000,
            is_prime=True,
            is_sponsored=False,
            in_stock=True
        ),
        Product(
            asin="TEST002",
            title="Test Protein Powder 2lb",
            brand="TestBrand",
            category="Protein Powder",
            current_price=Decimal("29.99"),
            list_price=Decimal("39.99"),
            unit_price=Decimal("0.94"),
            unit_type="oz",
            unit_quantity=Decimal("32"),
            discount_pct=Decimal("25.0"),
            rating=Decimal("4.4"),
            review_count=500,
            is_prime=False,
            is_sponsored=True,
            in_stock=True
        ),
        Product(
            asin="TEST003",
            title="Test Vitamins 100 Count",
            brand="TestBrand",
            category="Vitamins",
            current_price=Decimal("19.99"),
            list_price=Decimal("24.99"),
            unit_price=Decimal("0.20"),
            unit_type="count",
            unit_quantity=Decimal("100"),
            discount_pct=Decimal("20.0"),
            rating=Decimal("4.8"),
            review_count=2000,
            is_prime=True,
            is_sponsored=False,
            in_stock=True
        ),
    ]

    for product in products:
        db_session.add(product)

    # Add category stats
    stats = CategoryStats(
        category="Protein Powder",
        median_price=Decimal("39.99"),
        median_unit_price=Decimal("0.75"),
        avg_rating=Decimal("4.5"),
        product_count=2
    )
    db_session.add(stats)

    db_session.commit()

    return products


@pytest.fixture
def auth_headers():
    """
    Create authentication headers for testing protected endpoints
    """
    # In a real test, you'd create a valid JWT token
    # For now, this is a placeholder
    return {"Authorization": "Bearer test-token"}
