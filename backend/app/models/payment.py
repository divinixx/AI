"""
Payment database model.
Handles payment records for HD image downloads.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from app.db import Base


class PaymentStatus(str, enum.Enum):
    """Payment status states."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class Payment(Base):
    """Payment model for HD download purchases."""
    
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("image_jobs.id", ondelete="CASCADE"), nullable=False)
    
    # Payment details
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="USD", nullable=False)
    
    # Status and gateway
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    gateway_reference = Column(String(255), nullable=True)
    gateway_response = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User", back_populates="payments")
    image_job = relationship("ImageJob", back_populates="payment")
    
    def __repr__(self):
        return f"<Payment(id={self.id}, amount={self.amount}, status={self.status})>"
