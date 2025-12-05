"""
Payment schemas.
Pydantic models for payment creation, webhooks, and responses.
"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


class PaymentStatusEnum(str, Enum):
    """Payment status values."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentCreate(BaseModel):
    """Schema for creating a payment intent."""
    job_id: int = Field(..., description="Image job ID to unlock HD for")


class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: int
    uuid: str
    job_id: int
    amount: Decimal
    currency: str
    status: PaymentStatusEnum
    gateway_reference: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PaymentIntentResponse(BaseModel):
    """Schema for payment intent creation response."""
    payment_id: int
    client_secret: str
    amount: Decimal
    currency: str


class WebhookPayload(BaseModel):
    """Schema for payment gateway webhook payload."""
    event_type: str
    gateway_reference: str
    status: str
    metadata: Optional[dict] = None


class PaymentConfirm(BaseModel):
    """Schema for manual payment confirmation."""
    payment_id: int
    gateway_reference: str
