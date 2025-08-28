from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from core.schemas import TimestampedSchema


class SaleChannelSchema(TimestampedSchema):
    """Sale channel schema"""
    id: Optional[int] = None
    name: str
    marketplace_type: str
    is_active: bool = True


class MarketplaceListingSchema(TimestampedSchema):
    """Marketplace listing schema"""
    id: Optional[int] = None
    client_id: Optional[int] = None  # Auto-populated by mixin
    product_id: Optional[int] = None
    marketplace_type: str
    marketplace_id: str
    external_sku: Optional[str] = None
    title: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = Field(default="USD")
    inventory_quantity: Optional[int] = None
    status: Optional[str] = None
    is_fulfillment: bool = False
    listing_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    listing_type: Optional[str] = None
    official_store_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Add images array
    images: Optional[List[Dict[str, Any]]] = None
    main_image_url: Optional[str] = None
    image_count: Optional[int] = None


class ProductMatchSchema(TimestampedSchema):
    """Product match schema"""
    id: Optional[int] = None
    client_id: Optional[int] = None  # Auto-populated by mixin
    product_id: int
    marketplace_listing_id: int
    confidence_score: Decimal
    match_type: str = Field(default="auto")
    match_criteria: Dict[str, Any] = Field(default_factory=dict)
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    status: str = Field(default="active")


class ProductPriceHistorySchema(TimestampedSchema):
    """Product price history schema"""
    id: Optional[int] = None
    client_id: Optional[int] = None  # Auto-populated by mixin
    product_id: int
    marketplace_listing_id: int
    previous_price: Optional[Decimal] = None
    new_price: Optional[Decimal] = None
    change_date: datetime
    total_sales: Optional[int] = None
    utility_percentage: Optional[Decimal] = None
    conversion_rate: Optional[Decimal] = None
    market_share: Optional[Decimal] = None


class ProductTracingSchema(TimestampedSchema):
    """Product tracing schema"""
    id: Optional[int] = None
    client_id: Optional[int] = None  # Auto-populated by mixin
    product_id: int
    marketplace_type: str
    marketplace_id: str
    seller_name: Optional[str] = None
    seller_id: Optional[str] = None
    power_seller_status: Optional[str] = None
    last_checked_price: Optional[Decimal] = None
    last_checked_at: datetime
    is_active: bool = True


class ProductTracingHistorySchema(TimestampedSchema):
    """Product tracing history schema"""
    id: Optional[int] = None
    client_id: Optional[int] = None  # Auto-populated by mixin
    product_tracing_id: int
    sales_count: Optional[int] = None
    inventory_quantity: Optional[Decimal] = None
    price: Optional[Decimal] = None
    checked_at: datetime


class MarketplaceListingCreateSchema(BaseModel):
    """Schema for creating a marketplace listing"""
    # client_id removed - auto-populated by ClientContextMixin
    product_id: Optional[int] = None
    marketplace_type: str
    marketplace_id: str
    external_sku: Optional[str] = None
    title: Optional[str] = None
    price: Optional[Decimal] = None
    currency: str = Field(default="USD")
    inventory_quantity: Optional[int] = None
    status: Optional[str] = None
    is_fulfillment: bool = False
    listing_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    listing_type: Optional[str] = None
    official_store_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MarketplaceListingUpdateSchema(BaseModel):
    """Schema for updating a marketplace listing"""
    product_id: Optional[int] = None
    external_sku: Optional[str] = None
    title: Optional[str] = None
    price: Optional[Decimal] = None
    currency: Optional[str] = None
    inventory_quantity: Optional[int] = None
    status: Optional[str] = None
    is_fulfillment: Optional[bool] = None
    listing_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    listing_type: Optional[str] = None
    official_store_name: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class ProductMatchCreateSchema(BaseModel):
    """Schema for creating a product match"""
    # client_id removed - auto-populated by ClientContextMixin
    product_id: int
    marketplace_listing_id: int
    confidence_score: Decimal
    match_type: str = Field(default="auto")
    match_criteria: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="active")


class ProductMatchUpdateSchema(BaseModel):
    """Schema for updating a product match"""
    confidence_score: Optional[Decimal] = None
    match_type: Optional[str] = None
    match_criteria: Optional[Dict[str, Any]] = None
    reviewed_by_id: Optional[int] = None
    reviewed_at: Optional[datetime] = None
    status: Optional[str] = None


class ProductTracingCreateSchema(BaseModel):
    """Schema for creating a product tracing"""
    # client_id removed - auto-populated by ClientContextMixin
    product_id: int
    marketplace_type: str
    marketplace_id: str
    seller_name: Optional[str] = None
    seller_id: Optional[str] = None
    power_seller_status: Optional[str] = None
    last_checked_price: Optional[Decimal] = None
    is_active: bool = True


class ProductTracingUpdateSchema(BaseModel):
    """Schema for updating a product tracing"""
    seller_name: Optional[str] = None
    seller_id: Optional[str] = None
    power_seller_status: Optional[str] = None
    last_checked_price: Optional[Decimal] = None
    last_checked_at: Optional[datetime] = None
    is_active: Optional[bool] = None
