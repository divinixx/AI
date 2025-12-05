"""
Images router.
Handles image upload, transformation, and job management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
import os

from app.db import get_db
from app.config import settings
from app.models.user import User
from app.models.image_job import ImageStyle
from app.schemas.image import (
    ImageStyleEnum,
    ImageJobResponse,
    ImageJobListResponse,
    ImageJobFilter
)
from app.services.image_job import ImageJobService
from app.routers.users import get_current_user

router = APIRouter()


def job_to_response(job, base_url: str = "") -> ImageJobResponse:
    """Convert ImageJob model to response schema."""
    return ImageJobResponse(
        id=job.id,
        uuid=job.uuid,
        original_filename=job.original_filename,
        style=ImageStyleEnum(job.style.value),
        status=job.status.value,
        params_json=job.params_json,
        original_url=f"{base_url}/images/{job.uuid}/original" if job.original_path else None,
        output_url=f"{base_url}/images/{job.uuid}/processed" if job.output_path else None,
        is_hd_unlocked=job.is_hd_unlocked == "Y",
        error_message=job.error_message,
        created_at=job.created_at,
        processed_at=job.processed_at
    )


@router.post("/transform", response_model=ImageJobResponse, status_code=status.HTTP_201_CREATED)
async def transform_image(
    file: UploadFile = File(..., description="Image file to transform"),
    style: ImageStyleEnum = Query(..., description="Cartoon style to apply"),
    params: Optional[str] = Query(None, description="JSON string of style parameters"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload an image and create a transformation job.
    
    - **file**: Image file (JPG, PNG, WEBP)
    - **style**: Transformation style (cartoon, sketch, color_pencil, etc.)
    - **params**: Optional JSON string with style-specific parameters
    
    Returns the created job with status and preview URLs.
    """
    import json
    
    # Parse params if provided
    params_dict = None
    if params:
        try:
            params_dict = json.loads(params)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid params JSON format"
            )
    
    # Save uploaded file
    upload_path = ImageJobService.generate_file_path(
        file.filename,
        settings.UPLOAD_DIR
    )
    await ImageJobService.save_upload_file(file, upload_path)
    
    # Create job
    job = await ImageJobService.create_job(
        db=db,
        user_id=current_user.id,
        original_filename=file.filename,
        original_path=upload_path,
        style=ImageStyle(style.value),
        params_json=params_dict
    )
    
    # Process immediately (sync for now, could be background task)
    job = await ImageJobService.process_job(db, job)
    
    return job_to_response(job)


@router.get("", response_model=ImageJobListResponse)
async def list_jobs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    style: Optional[ImageStyleEnum] = Query(None, description="Filter by style"),
    status: Optional[str] = Query(None, description="Filter by status"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all image jobs for the current user.
    
    Supports pagination and filtering by style/status.
    """
    filters = ImageJobFilter(
        style=style,
        status=status
    ) if style or status else None
    
    jobs, total = await ImageJobService.get_user_jobs(
        db=db,
        user_id=current_user.id,
        filters=filters,
        page=page,
        page_size=page_size
    )
    
    total_pages = (total + page_size - 1) // page_size
    
    return ImageJobListResponse(
        items=[job_to_response(job) for job in jobs],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )


@router.get("/{job_uuid}", response_model=ImageJobResponse)
async def get_job(
    job_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get details of a specific image job.
    
    - **job_uuid**: UUID of the job
    """
    job = await ImageJobService.get_job_by_uuid(db, job_uuid, current_user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    return job_to_response(job)


@router.get("/{job_uuid}/original")
async def get_original_image(
    job_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download the original uploaded image.
    """
    job = await ImageJobService.get_job_by_uuid(db, job_uuid, current_user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not job.original_path or not os.path.exists(job.original_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Original image not found"
        )
    
    return FileResponse(
        job.original_path,
        filename=job.original_filename,
        media_type="image/jpeg"
    )


@router.get("/{job_uuid}/processed")
async def get_processed_image(
    job_uuid: str,
    hd: bool = Query(False, description="Request HD quality"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Download the processed/transformed image.
    
    - **hd**: If true, returns HD quality (requires payment)
    """
    job = await ImageJobService.get_job_by_uuid(db, job_uuid, current_user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    if not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Processed image not found"
        )
    
    # Check HD access
    if hd and job.is_hd_unlocked != "Y":
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="HD download requires payment"
        )
    
    return FileResponse(
        job.output_path,
        filename=f"processed_{job.original_filename}",
        media_type="image/jpeg"
    )


@router.delete("/{job_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_uuid: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete an image job and its associated files.
    
    - **job_uuid**: UUID of the job to delete
    """
    job = await ImageJobService.get_job_by_uuid(db, job_uuid, current_user.id)
    
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )
    
    success = await ImageJobService.delete_job(db, job)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete job"
        )
