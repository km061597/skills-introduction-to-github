"""
Pydantic schemas for request/response validation
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class ProductBase(BaseModel):
    asin: str
    title: str
    brand: Optional[str] = None
    category: Optional[str] = None
    current_price: Optional[Decimal] = None
    list_price: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    unit_type: Optional[str] = None
    unit_quantity: Optional[Decimal] = None
    discount_pct: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    review_count: Optional[int] = 0
    verified_review_count: Optional[int] = 0
    image_url: Optional[str] = None
    amazon_url: Optional[str] = None
    is_prime: bool = False
    is_sponsored: bool = False
    subscribe_save_pct: Optional[Decimal] = None
    in_stock: bool = True
    hidden_gem_score: Optional[int] = None
    deal_quality_score: Optional[int] = None


class ProductResponse(ProductBase):
    last_scraped_at: datetime
    created_at: datetime
    updated_at: datetime

    # Computed fields
    is_best_value: Optional[bool] = False
    savings_vs_category: Optional[Decimal] = None

    class Config:
        from_attributes = True


class PriceHistoryResponse(BaseModel):
    id: int
    asin: str
    price: Decimal
    unit_price: Optional[Decimal] = None
    recorded_at: datetime

    class Config:
        from_attributes = True


class SearchRequest(BaseModel):
    q: str = Field(..., min_length=1, description="Search query")
    sort: str = Field(default="unit_price_asc", description="Sort option")
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    min_unit_price: Optional[Decimal] = None
    max_unit_price: Optional[Decimal] = None
    min_rating: Optional[Decimal] = Field(None, ge=0, le=5)
    min_review_count: Optional[int] = None
    prime_only: bool = False
    hide_sponsored: bool = True
    min_discount: Optional[int] = Field(None, ge=0, le=100)
    brands: Optional[List[str]] = None
    exclude_brands: Optional[List[str]] = None
    in_stock_only: bool = False
    page: int = Field(default=1, ge=1)
    limit: int = Field(default=48, ge=1, le=100)

    @validator('sort')
    def validate_sort(cls, v):
        valid_sorts = [
            'unit_price_asc', 'unit_price_desc',
            'price_asc', 'price_desc',
            'discount_desc', 'rating_desc',
            'review_count_desc', 'hidden_gem_desc'
        ]
        if v not in valid_sorts:
            raise ValueError(f'Sort must be one of: {", ".join(valid_sorts)}')
        return v


class SearchResponse(BaseModel):
    results: List[ProductResponse]
    total: int
    page: int
    pages: int
    sponsored_hidden: int = 0
    query: str


class ProductDetailResponse(ProductResponse):
    price_history: List[PriceHistoryResponse] = []
    similar_products: List[ProductResponse] = []


class CategoryStatsResponse(BaseModel):
    category: str
    median_price: Optional[Decimal] = None
    median_unit_price: Optional[Decimal] = None
    avg_rating: Optional[Decimal] = None
    product_count: int = 0
    last_updated: datetime

    class Config:
        from_attributes = True


class CompareRequest(BaseModel):
    asins: List[str] = Field(..., min_items=2, max_items=10)


class CompareResponse(BaseModel):
    products: List[ProductResponse]
    best_unit_price_asin: Optional[str] = None
    best_rating_asin: Optional[str] = None
    best_value_asin: Optional[str] = None
