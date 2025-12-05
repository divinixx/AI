"""
Application configuration settings.
Environment-based settings for database, JWT, payments, and other configurations.
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_ENV: str = "local"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://user:password@localhost:5432/toonify"
    
    # JWT Authentication
    JWT_SECRET: str = "your_jwt_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:8501", "http://localhost:3000"]
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    PROCESSED_DIR: str = "processed"
    MAX_FILE_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "webp"]
    
    # Payment Provider (Optional)
    PAYMENT_PROVIDER: str = "stripe"  # or "razorpay"
    PAYMENT_PROVIDER_KEY: str = ""
    PAYMENT_PROVIDER_SECRET: str = ""
    PAYMENT_WEBHOOK_SECRET: str = ""
    
    # Image Processing
    DEFAULT_OUTPUT_QUALITY: int = 85
    HD_OUTPUT_QUALITY: int = 100
    MAX_IMAGE_DIMENSION: int = 4096
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

# Create upload directories if they don't exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PROCESSED_DIR, exist_ok=True)
