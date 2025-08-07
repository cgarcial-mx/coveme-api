from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from core.schemas import TimestampedSchema


class ApiLogSchema(TimestampedSchema):
    """API log schema"""
    id: Optional[int] = None
    client_id: int
    user_id: Optional[int] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[int] = None  # in milliseconds
    quota_used: Optional[int] = None


class ApiLogCreateSchema(BaseModel):
    """Schema for creating an API log"""
    client_id: int
    user_id: Optional[int] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[int] = None
    quota_used: Optional[int] = None


class ApiLogUpdateSchema(BaseModel):
    """Schema for updating an API log"""
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[int] = None
    quota_used: Optional[int] = None


class ApiLogFilterSchema(BaseModel):
    """Schema for filtering API logs"""
    client_id: Optional[int] = None
    user_id: Optional[int] = None
    endpoint: Optional[str] = None
    method: Optional[str] = None
    status_code: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    min_response_time: Optional[int] = None
    max_response_time: Optional[int] = None
