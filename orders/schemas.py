from datetime import datetime
from typing import Optional, Dict, Any, List
from decimal import Decimal
from pydantic import BaseModel, Field, ConfigDict
from core.schemas import TimestampedSchema


class OrderSchema(TimestampedSchema):
    """Order schema"""
    id: Optional[int] = None
    client_id: int
    marketplace_type: str
    marketplace_order_id: str
    order_status: Optional[str] = None
    order_total: Optional[Decimal] = None
    currency: str = Field(default="USD")
    purchase_date: Optional[datetime] = None
    last_update_date: Optional[datetime] = None
    logistic_type: Optional[str] = None
    customer_info: Dict[str, Any] = Field(default_factory=dict)
    shipping_address: Dict[str, Any] = Field(default_factory=dict)
    billing_address: Dict[str, Any] = Field(default_factory=dict)
    payment_info: Dict[str, Any] = Field(default_factory=dict)
    fulfillment_status: Optional[str] = None
    tags: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrderItemSchema(TimestampedSchema):
    """Order item schema"""
    id: Optional[int] = None
    client_id: int
    order_id: int
    product_id: Optional[int] = None
    marketplace_item_id: Optional[str] = None
    title: Optional[str] = None
    sku: Optional[str] = None
    quantity: Decimal
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    sale_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    is_variation: bool = False
    variations_attributes: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrderWithItemsSchema(OrderSchema):
    """Order schema with items"""
    items: List[OrderItemSchema] = Field(default_factory=list)


class OrderCreateSchema(BaseModel):
    """Schema for creating an order"""
    client_id: int
    marketplace_type: str
    marketplace_order_id: str
    order_status: Optional[str] = None
    order_total: Optional[Decimal] = None
    currency: str = Field(default="USD")
    purchase_date: Optional[datetime] = None
    last_update_date: Optional[datetime] = None
    logistic_type: Optional[str] = None
    customer_info: Dict[str, Any] = Field(default_factory=dict)
    shipping_address: Dict[str, Any] = Field(default_factory=dict)
    billing_address: Dict[str, Any] = Field(default_factory=dict)
    payment_info: Dict[str, Any] = Field(default_factory=dict)
    fulfillment_status: Optional[str] = None
    tags: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrderUpdateSchema(BaseModel):
    """Schema for updating an order"""
    order_status: Optional[str] = None
    order_total: Optional[Decimal] = None
    currency: Optional[str] = None
    purchase_date: Optional[datetime] = None
    last_update_date: Optional[datetime] = None
    logistic_type: Optional[str] = None
    customer_info: Optional[Dict[str, Any]] = None
    shipping_address: Optional[Dict[str, Any]] = None
    billing_address: Optional[Dict[str, Any]] = None
    payment_info: Optional[Dict[str, Any]] = None
    fulfillment_status: Optional[str] = None
    tags: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class OrderItemCreateSchema(BaseModel):
    """Schema for creating an order item"""
    client_id: int
    order_id: int
    product_id: Optional[int] = None
    marketplace_item_id: Optional[str] = None
    title: Optional[str] = None
    sku: Optional[str] = None
    quantity: Decimal
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    sale_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    is_variation: bool = False
    variations_attributes: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class OrderItemUpdateSchema(BaseModel):
    """Schema for updating an order item"""
    product_id: Optional[int] = None
    marketplace_item_id: Optional[str] = None
    title: Optional[str] = None
    sku: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit_price: Optional[Decimal] = None
    total_price: Optional[Decimal] = None
    sale_fee: Optional[Decimal] = None
    shipment_fee: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    is_variation: Optional[bool] = None
    variations_attributes: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None
