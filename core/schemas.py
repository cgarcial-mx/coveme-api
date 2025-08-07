from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class TimestampedSchema(BaseModel):
    """Base schema with timestamps"""
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class UserSchema(TimestampedSchema):
    """User schema"""
    id: Optional[int] = None
    username: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    client_id: Optional[int] = None
    role: str = Field(default="operator")
    permissions: Dict[str, Any] = Field(default_factory=dict)
    status: str = Field(default="active")
    is_active: bool = True
    is_staff: bool = False
    is_superuser: bool = False
    date_joined: Optional[datetime] = None
    last_login: Optional[datetime] = None


class ClientSchema(TimestampedSchema):
    """Client schema"""
    id: Optional[int] = None
    name: str
    tax_id: Optional[str] = None
    subscription_plan: str = Field(default="basic")
    api_quota: int = Field(default=10000)
    status: str = Field(default="active")


class ClientMarketplaceCredentialsSchema(TimestampedSchema):
    """Client marketplace credentials schema"""
    id: Optional[int] = None
    client_id: int
    marketplace_type: str
    marketplace_name: Optional[str] = None
    credentials: Dict[str, Any]
    settings: Dict[str, Any] = Field(default_factory=dict)
    webhook_url: Optional[str] = None
    connection_status: str = Field(default="disconnected")
    last_sync_at: Optional[datetime] = None
    last_error: Optional[str] = None
    created_by_id: Optional[int] = None
