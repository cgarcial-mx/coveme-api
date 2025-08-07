from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from core.schemas import TimestampedSchema


class CustomerFeedbackSchema(TimestampedSchema):
    """Customer feedback schema"""
    id: Optional[int] = None
    client_id: int
    marketplace_type: str
    feedback_type: str
    marketplace_feedback_id: Optional[str] = None
    product_id: Optional[int] = None
    marketplace_product_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    feedback_date: Optional[datetime] = None
    status: str = Field(default="pending")
    answer_text: Optional[str] = None
    answer_date: Optional[datetime] = None
    verified_purchase: bool = False
    helpful_votes: int = Field(default=0)
    total_votes: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CustomerFeedbackCreateSchema(BaseModel):
    """Schema for creating customer feedback"""
    client_id: int
    marketplace_type: str
    feedback_type: str
    marketplace_feedback_id: Optional[str] = None
    product_id: Optional[int] = None
    marketplace_product_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    feedback_date: Optional[datetime] = None
    status: str = Field(default="pending")
    verified_purchase: bool = False
    helpful_votes: int = Field(default=0)
    total_votes: int = Field(default=0)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class CustomerFeedbackUpdateSchema(BaseModel):
    """Schema for updating customer feedback"""
    marketplace_feedback_id: Optional[str] = None
    product_id: Optional[int] = None
    marketplace_product_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    rating: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    feedback_date: Optional[datetime] = None
    status: Optional[str] = None
    answer_text: Optional[str] = None
    answer_date: Optional[datetime] = None
    verified_purchase: Optional[bool] = None
    helpful_votes: Optional[int] = None
    total_votes: Optional[int] = None
    metadata: Optional[Dict[str, Any]] = None


class CustomerFeedbackFilterSchema(BaseModel):
    """Schema for filtering customer feedback"""
    client_id: Optional[int] = None
    marketplace_type: Optional[str] = None
    feedback_type: Optional[str] = None
    product_id: Optional[int] = None
    rating: Optional[int] = None
    status: Optional[str] = None
    verified_purchase: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
