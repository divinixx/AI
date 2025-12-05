"""
Image Job database model.
Handles image processing jobs, status tracking, and file references.
"""

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Enum, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid

from app.db import Base


class ImageStyle(str, enum.Enum):
    """Available cartoon effect styles."""
    CARTOON = "cartoon"
    SKETCH = "sketch"
    COLOR_PENCIL = "color_pencil"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    POP_ART = "pop_art"


class JobStatus(str, enum.Enum):
    """Image processing job status."""
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class ImageJob(Base):
    """Image processing job model."""
    
    __tablename__ = "image_jobs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    uuid = Column(String(36), unique=True, default=lambda: str(uuid.uuid4()), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # File paths
    original_filename = Column(String(255), nullable=False)
    original_path = Column(String(512), nullable=False)
    output_path = Column(String(512), nullable=True)
    
    # Processing details
    style = Column(Enum(ImageStyle), nullable=False)
    params_json = Column(JSON, nullable=True)
    
    # Status tracking
    status = Column(Enum(JobStatus), default=JobStatus.QUEUED, nullable=False)
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # HD download
    is_hd_unlocked = Column(String(1), default="N", nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="image_jobs")
    payment = relationship("Payment", back_populates="image_job", uselist=False)
    
    def __repr__(self):
        return f"<ImageJob(id={self.id}, style={self.style}, status={self.status})>"
