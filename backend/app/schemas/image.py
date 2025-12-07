"""
Pydantic schemas for Image processing
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ImageStyleEnum(str, Enum):
    CARTOON = "cartoon"
    PENCIL_SKETCH = "pencil_sketch"
    COLOR_PENCIL = "color_pencil"
    EDGE_PRESERVE = "edge_preserve"
    WATERCOLOR = "watercolor"


class JobStatusEnum(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ImageProcessRequest(BaseModel):
    style: ImageStyleEnum = ImageStyleEnum.CARTOON


class ImageJobResponse(BaseModel):
    id: int
    original_filename: str
    style: str
    status: str
    created_at: datetime
    processed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    
    class Config:
        from_attributes = True


class ImageJobDetailResponse(ImageJobResponse):
    original_url: str
    processed_url: Optional[str] = None
    comparison_url: Optional[str] = None
    download_count: int = 0


class ImageUploadResponse(BaseModel):
    job_id: int
    message: str
    original_url: str


class ImageListResponse(BaseModel):
    jobs: List[ImageJobResponse]
    total: int
    page: int
    per_page: int


class StyleInfo(BaseModel):
    name: str
    value: str
    description: str


class StylesListResponse(BaseModel):
    styles: List[StyleInfo]
