"""
Users router.
Handles user profile management endpoints.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models.user import User
from app.schemas.auth import UserResponse, UserUpdate, PasswordChange
from app.services.auth import (
    decode_token,
    get_user_by_uuid,
    verify_password,
    hash_password
)

router = APIRouter()
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload.type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type"
        )
    
    user = await get_user_by_uuid(db, payload.sub)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    return user


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile information.
    
    Requires authentication.
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update current user's profile.
    
    - **full_name**: New full name (optional)
    - **email**: New email address (optional, must be unique)
    """
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    
    if update_data.email is not None:
        # Check if email already exists
        from app.services.auth import get_user_by_email
        existing = await get_user_by_email(db, update_data.email)
        if existing and existing.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        current_user.email = update_data.email
    
    await db.flush()
    await db.refresh(current_user)
    
    return current_user


@router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Change current user's password.
    
    - **current_password**: Current password
    - **new_password**: New password (minimum 8 characters)
    """
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    current_user.password_hash = hash_password(password_data.new_password)
    await db.flush()
    
    return {"message": "Password changed successfully"}


@router.get("/me/stats")
async def get_user_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's usage statistics.
    
    Returns counts of images processed by status and style.
    """
    from app.services.image_job import ImageJobService
    
    stats = await ImageJobService.get_user_stats(db, current_user.id)
    return stats
