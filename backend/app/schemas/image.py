"""
Image processing schemas.
Pydantic models for image upload, transformation, and job responses.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from enum import Enum


class ImageStyleEnum(str, Enum):
    """Available image transformation styles."""
    CARTOON = "cartoon"
    SKETCH = "sketch"
    COLOR_PENCIL = "color_pencil"
    OIL_PAINTING = "oil_painting"
    WATERCOLOR = "watercolor"
    POP_ART = "pop_art"


class JobStatusEnum(str, Enum):
    """Image job status values."""
    QUEUED = "queued"
    PROCESSING = "processing"
    DONE = "done"
    FAILED = "failed"


class CartoonParams(BaseModel):
    """Parameters for cartoon effect."""
    blur_kernel_size: int = Field(default=7, ge=3, le=21, description="Must be odd number")
    threshold_block_size: int = Field(default=9, ge=3, le=21, description="Must be odd number")
    threshold_c: int = Field(default=9, ge=1, le=20)
    bilateral_d: int = Field(default=9, ge=5, le=15)
    bilateral_sigma_color: int = Field(default=200, ge=50, le=300)
    bilateral_sigma_space: int = Field(default=200, ge=50, le=300)


class SketchParams(BaseModel):
    """Parameters for pencil sketch effect."""
    blur_kernel_size: int = Field(default=21, ge=3, le=51, description="Must be odd number")
    invert: bool = Field(default=True)


class ColorPencilParams(BaseModel):
    """Parameters for color pencil effect."""
    sketch_weight: float = Field(default=0.7, ge=0.0, le=1.0)
    color_weight: float = Field(default=0.3, ge=0.0, le=1.0)
    blur_kernel_size: int = Field(default=21, ge=3, le=51)


class ImageTransformRequest(BaseModel):
    """Schema for image transformation request."""
    style: ImageStyleEnum
    params: Optional[Dict[str, Any]] = Field(default=None, description="Style-specific parameters")


class ImageJobCreate(BaseModel):
    """Schema for creating an image job (internal use)."""
    original_filename: str
    original_path: str
    style: ImageStyleEnum
    params_json: Optional[Dict[str, Any]] = None


class ImageJobResponse(BaseModel):
    """Schema for image job response."""
    id: int
    uuid: str
    original_filename: str
    style: ImageStyleEnum
    status: JobStatusEnum
    params_json: Optional[Dict[str, Any]]
    original_url: Optional[str] = None
    output_url: Optional[str] = None
    is_hd_unlocked: bool = False
    error_message: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class ImageJobListResponse(BaseModel):
    """Schema for paginated image job list."""
    items: List[ImageJobResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class ImageJobFilter(BaseModel):
    """Schema for filtering image jobs."""
    style: Optional[ImageStyleEnum] = None
    status: Optional[JobStatusEnum] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
