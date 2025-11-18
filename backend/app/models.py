"""
SQLAlchemy ORM Models
"""
from sqlalchemy import Boolean, Column, Integer, String, DECIMAL, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class Product(Base):
    __tablename__ = "products"

    asin = Column(String(10), primary_key=True, index=True)
    title = Column(Text, nullable=False)
    brand = Column(String(255), index=True)
    category = Column(String(255), index=True)
    current_price = Column(DECIMAL(10, 2))
    list_price = Column(DECIMAL(10, 2))
    unit_price = Column(DECIMAL(10, 4), index=True)
    unit_type = Column(String(10))
    unit_quantity = Column(DECIMAL(10, 2))
    discount_pct = Column(DECIMAL(5, 2))
    rating = Column(DECIMAL(3, 2), index=True)
    review_count = Column(Integer, default=0)
    verified_review_count = Column(Integer, default=0)
    image_url = Column(Text)
    amazon_url = Column(Text)
    is_prime = Column(Boolean, default=False, index=True)
    is_sponsored = Column(Boolean, default=False, index=True)
    subscribe_save_pct = Column(DECIMAL(5, 2))
    in_stock = Column(Boolean, default=True)
    last_scraped_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    hidden_gem_score = Column(Integer)
    deal_quality_score = Column(Integer)

    # Relationships
    price_history = relationship("PriceHistory", back_populates="product", cascade="all, delete-orphan")


class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    asin = Column(String(10), ForeignKey("products.asin"), nullable=False)
    price = Column(DECIMAL(10, 2), nullable=False)
    unit_price = Column(DECIMAL(10, 4))
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Relationships
    product = relationship("Product", back_populates="price_history")


class SearchCache(Base):
    __tablename__ = "search_cache"

    id = Column(Integer, primary_key=True, index=True)
    query_hash = Column(String(64), unique=True, nullable=False, index=True)
    results = Column(JSON)
    total_count = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)


class CategoryStats(Base):
    __tablename__ = "category_stats"

    category = Column(String(255), primary_key=True, index=True)
    median_price = Column(DECIMAL(10, 2))
    median_unit_price = Column(DECIMAL(10, 4))
    avg_rating = Column(DECIMAL(3, 2))
    product_count = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class UserSearch(Base):
    __tablename__ = "user_searches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    name = Column(String(255))
    query = Column(Text)
    filters = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
