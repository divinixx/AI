"""
Frontend configuration settings.
"""

import os
from dataclasses import dataclass


@dataclass
class Settings:
    """Frontend application settings."""
    
    # Backend API
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    
    # Timeouts
    REQUEST_TIMEOUT: int = 30
    UPLOAD_TIMEOUT: int = 120
    
    # UI Settings
    MAX_DISPLAY_WIDTH: int = 800
    THUMBNAIL_SIZE: tuple = (200, 200)
    
    # Allowed file types
    ALLOWED_EXTENSIONS: list = None
    
    def __post_init__(self):
        if self.ALLOWED_EXTENSIONS is None:
            self.ALLOWED_EXTENSIONS = ["jpg", "jpeg", "png", "webp"]


settings = Settings()
