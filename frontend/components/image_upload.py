"""
Image Upload Component.
Handles image file upload with validation.
"""

import streamlit as st
from typing import Optional
from config import settings


def render_image_uploader(key: str = "image_upload") -> Optional[st.runtime.uploaded_file_manager.UploadedFile]:
    """
    Render an image uploader component.
    
    Args:
        key: Unique key for the uploader widget
    
    Returns:
        Uploaded file or None
    """
    
    allowed_types = ["jpg", "jpeg", "png", "webp"]
    allowed_mime = ["image/jpeg", "image/png", "image/webp"]
    
    uploaded_file = st.file_uploader(
        "📤 Choose an image file",
        type=allowed_types,
        accept_multiple_files=False,
        key=key,
        help=f"Supported formats: {', '.join(allowed_types).upper()}"
    )
    
    if uploaded_file is not None:
        # Validate file type
        if uploaded_file.type not in allowed_mime:
            st.error(f"Invalid file type: {uploaded_file.type}")
            return None
        
        # Check file size (10MB max)
        max_size = 10 * 1024 * 1024  # 10MB
        if uploaded_file.size > max_size:
            st.error(f"File too large. Maximum size: 10MB")
            return None
        
        # Show file info
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"📁 **File:** {uploaded_file.name}")
        with col2:
            size_mb = uploaded_file.size / (1024 * 1024)
            st.caption(f"📊 **Size:** {size_mb:.2f} MB")
        
        return uploaded_file
    
    return None


def render_image_preview(uploaded_file) -> None:
    """
    Render a preview of the uploaded image.
    
    Args:
        uploaded_file: Streamlit uploaded file object
    """
    if uploaded_file is not None:
        st.image(
            uploaded_file,
            caption="Original Image",
            use_container_width=True
        )
