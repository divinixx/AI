"""
Image job service.
Handles CRUD operations for image processing jobs.
"""

from typing import Optional, List
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi import HTTPException, status, UploadFile
import aiofiles
import os
import uuid
from pathlib import Path
import logging

from app.config import settings
from app.models.image_job import ImageJob, JobStatus, ImageStyle
from app.services.image_processing import ImageProcessor
from app.schemas.image import ImageJobFilter

logger = logging.getLogger(__name__)


class ImageJobService:
    """Service for managing image processing jobs."""
    
    @staticmethod
    def generate_file_path(filename: str, directory: str) -> str:
        """Generate a unique file path for uploaded/processed images."""
        ext = Path(filename).suffix.lower()
        unique_name = f"{uuid.uuid4()}{ext}"
        return os.path.join(directory, unique_name)
    
    @staticmethod
    async def save_upload_file(upload_file: UploadFile, destination: str) -> str:
        """Save an uploaded file to the destination path."""
        # Validate file extension
        ext = Path(upload_file.filename).suffix.lower().lstrip('.')
        if ext not in settings.ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type not allowed. Allowed types: {settings.ALLOWED_EXTENSIONS}"
            )
        
        # Create directory if needed
        Path(destination).parent.mkdir(parents=True, exist_ok=True)
        
        # Save file
        async with aiofiles.open(destination, 'wb') as out_file:
            content = await upload_file.read()
            
            # Check file size
            if len(content) > settings.MAX_FILE_SIZE_MB * 1024 * 1024:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: {settings.MAX_FILE_SIZE_MB}MB"
                )
            
            await out_file.write(content)
        
        return destination
    
    @staticmethod
    async def create_job(
        db: AsyncSession,
        user_id: int,
        original_filename: str,
        original_path: str,
        style: ImageStyle,
        params_json: Optional[dict] = None
    ) -> ImageJob:
        """Create a new image processing job."""
        job = ImageJob(
            user_id=user_id,
            original_filename=original_filename,
            original_path=original_path,
            style=style,
            params_json=params_json,
            status=JobStatus.QUEUED
        )
        db.add(job)
        await db.flush()
        await db.refresh(job)
        
        logger.info(f"Created image job {job.id} for user {user_id}")
        return job
    
    @staticmethod
    async def process_job(db: AsyncSession, job: ImageJob) -> ImageJob:
        """Process an image job synchronously."""
        try:
            # Update status to processing
            job.status = JobStatus.PROCESSING
            await db.flush()
            
            # Generate output path
            output_filename = f"{Path(job.original_filename).stem}_processed{Path(job.original_filename).suffix}"
            output_path = ImageJobService.generate_file_path(
                output_filename, 
                settings.PROCESSED_DIR
            )
            
            # Process the image
            ImageProcessor.process_image(
                input_path=job.original_path,
                output_path=output_path,
                style=job.style,
                params=job.params_json
            )
            
            # Update job with results
            job.output_path = output_path
            job.status = JobStatus.DONE
            job.processed_at = datetime.utcnow()
            
        except Exception as e:
            logger.error(f"Error processing job {job.id}: {str(e)}")
            job.status = JobStatus.FAILED
            job.error_message = str(e)
        
        await db.flush()
        await db.refresh(job)
        
        return job
    
    @staticmethod
    async def get_job_by_id(
        db: AsyncSession,
        job_id: int,
        user_id: Optional[int] = None
    ) -> Optional[ImageJob]:
        """Get a job by ID, optionally filtered by user."""
        query = select(ImageJob).where(ImageJob.id == job_id)
        if user_id:
            query = query.where(ImageJob.user_id == user_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_job_by_uuid(
        db: AsyncSession,
        job_uuid: str,
        user_id: Optional[int] = None
    ) -> Optional[ImageJob]:
        """Get a job by UUID, optionally filtered by user."""
        query = select(ImageJob).where(ImageJob.uuid == job_uuid)
        if user_id:
            query = query.where(ImageJob.user_id == user_id)
        
        result = await db.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_jobs(
        db: AsyncSession,
        user_id: int,
        filters: Optional[ImageJobFilter] = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[ImageJob], int]:
        """Get paginated list of jobs for a user with optional filters."""
        query = select(ImageJob).where(ImageJob.user_id == user_id)
        count_query = select(func.count(ImageJob.id)).where(ImageJob.user_id == user_id)
        
        # Apply filters
        if filters:
            if filters.style:
                query = query.where(ImageJob.style == filters.style)
                count_query = count_query.where(ImageJob.style == filters.style)
            if filters.status:
                query = query.where(ImageJob.status == filters.status)
                count_query = count_query.where(ImageJob.status == filters.status)
            if filters.date_from:
                query = query.where(ImageJob.created_at >= filters.date_from)
                count_query = count_query.where(ImageJob.created_at >= filters.date_from)
            if filters.date_to:
                query = query.where(ImageJob.created_at <= filters.date_to)
                count_query = count_query.where(ImageJob.created_at <= filters.date_to)
        
        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # Apply pagination
        offset = (page - 1) * page_size
        query = query.order_by(ImageJob.created_at.desc()).limit(page_size).offset(offset)
        
        result = await db.execute(query)
        jobs = result.scalars().all()
        
        return jobs, total
    
    @staticmethod
    async def get_user_stats(db: AsyncSession, user_id: int) -> dict:
        """Get processing statistics for a user."""
        # Total jobs
        total_result = await db.execute(
            select(func.count(ImageJob.id)).where(ImageJob.user_id == user_id)
        )
        total_jobs = total_result.scalar()
        
        # Jobs by status
        status_result = await db.execute(
            select(ImageJob.status, func.count(ImageJob.id))
            .where(ImageJob.user_id == user_id)
            .group_by(ImageJob.status)
        )
        status_counts = {row[0].value: row[1] for row in status_result}
        
        # Jobs by style
        style_result = await db.execute(
            select(ImageJob.style, func.count(ImageJob.id))
            .where(ImageJob.user_id == user_id)
            .group_by(ImageJob.style)
        )
        style_counts = {row[0].value: row[1] for row in style_result}
        
        return {
            "total_jobs": total_jobs,
            "by_status": status_counts,
            "by_style": style_counts
        }
    
    @staticmethod
    async def delete_job(db: AsyncSession, job: ImageJob) -> bool:
        """Delete a job and its associated files."""
        try:
            # Delete files
            if job.original_path and os.path.exists(job.original_path):
                os.remove(job.original_path)
            if job.output_path and os.path.exists(job.output_path):
                os.remove(job.output_path)
            
            # Delete record
            await db.delete(job)
            await db.flush()
            
            logger.info(f"Deleted job {job.id}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting job {job.id}: {str(e)}")
            return False
