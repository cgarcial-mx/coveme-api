from datetime import datetime
from typing import Optional, Dict, Any
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from core.schemas import TimestampedSchema


class BrandSchema(TimestampedSchema):
    """Brand schema"""
    id: Optional[int] = None
    client_id: int
    name: str


class SubBrandSchema(TimestampedSchema):
    """SubBrand schema"""
    id: Optional[int] = None
    client_id: int
    brand_id: int
    name: str
    brand_name: Optional[str] = None


class ProviderSchema(TimestampedSchema):
    """Provider schema"""
    id: Optional[int] = None
    client_id: int
    name: str
    email: Optional[str] = None
    contact_info: Dict[str, Any] = Field(default_factory=dict)


class ProductSchema(TimestampedSchema):
    """Product schema"""
    id: Optional[int] = None
    client_id: int
    internal_sku: str
    title: str
    description: Optional[str] = None
    brand_id: Optional[int] = None
    subbrand_id: Optional[int] = None
    provider_id: Optional[int] = None
    category: Optional[str] = None
    weight: Optional[Decimal] = None
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    barcode: Optional[str] = None
    cost: Optional[Decimal] = None
    cost_with_discount: Optional[Decimal] = None
    is_iva_included: bool = False
    is_supermarket: bool = False
    created_by_id: Optional[int] = None
    
    # Read-only fields for display
    brand_name: Optional[str] = None
    subbrand_name: Optional[str] = None
    provider_name: Optional[str] = None


class ProductCreateSchema(BaseModel):
    """Schema for creating a product"""
    client_id: int
    internal_sku: str
    title: str
    description: Optional[str] = None
    brand_id: Optional[int] = None
    subbrand_id: Optional[int] = None
    provider_id: Optional[int] = None
    category: Optional[str] = None
    weight: Optional[Decimal] = None
    dimensions: Dict[str, Any] = Field(default_factory=dict)
    barcode: Optional[str] = None
    cost: Optional[Decimal] = None
    cost_with_discount: Optional[Decimal] = None
    is_iva_included: bool = False
    is_supermarket: bool = False


class ProductUpdateSchema(BaseModel):
    """Schema for updating a product"""
    title: Optional[str] = None
    description: Optional[str] = None
    brand_id: Optional[int] = None
    subbrand_id: Optional[int] = None
    provider_id: Optional[int] = None
    category: Optional[str] = None
    weight: Optional[Decimal] = None
    dimensions: Optional[Dict[str, Any]] = None
    barcode: Optional[str] = None
    cost: Optional[Decimal] = None
    cost_with_discount: Optional[Decimal] = None
    is_iva_included: Optional[bool] = None
    is_supermarket: Optional[bool] = None
