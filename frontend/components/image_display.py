"""
Image Display Component.
Renders images side-by-side and in card format.
"""

import streamlit as st
from typing import Optional, Dict, Any
from io import BytesIO


def display_images_side_by_side(
    original_image: bytes,
    processed_image: bytes,
    original_label: str = "Original",
    processed_label: str = "Transformed"
) -> None:
    """
    Display original and processed images side by side.
    
    Args:
        original_image: Original image bytes
        processed_image: Processed image bytes
        original_label: Label for original image
        processed_label: Label for processed image
    """
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {original_label}")
        st.image(original_image, use_container_width=True)
    
    with col2:
        st.markdown(f"### {processed_label}")
        st.image(processed_image, use_container_width=True)


def display_image_card(
    job: Dict[str, Any],
    original_image: Optional[bytes] = None,
    processed_image: Optional[bytes] = None,
    show_download: bool = True
) -> None:
    """
    Display an image job in a card format.
    
    Args:
        job: Job data dictionary
        original_image: Original image bytes (optional)
        processed_image: Processed image bytes (optional)
        show_download: Whether to show download buttons
    """
    with st.container(border=True):
        # Header
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.markdown(f"**{job['original_filename']}**")
        
        with col2:
            status_colors = {
                "done": "🟢",
                "processing": "🟡",
                "failed": "🔴",
                "queued": "⚪"
            }
            emoji = status_colors.get(job['status'], "⚪")
            st.markdown(f"{emoji} {job['status'].title()}")
        
        # Style and date
        col1, col2 = st.columns(2)
        
        with col1:
            st.caption(f"🎨 Style: **{job['style'].replace('_', ' ').title()}**")
        
        with col2:
            created = job.get('created_at', '')
            if created:
                # Parse and format date
                date_str = created[:10] if len(created) >= 10 else created
                st.caption(f"📅 {date_str}")
        
        # Images
        if processed_image and job['status'] == 'done':
            st.image(processed_image, use_container_width=True)
        elif original_image:
            st.image(original_image, use_container_width=True, caption="Original")
        
        # Download buttons
        if show_download and job['status'] == 'done' and processed_image:
            col1, col2 = st.columns(2)
            
            with col1:
                st.download_button(
                    label="📥 Download",
                    data=processed_image,
                    file_name=f"toonify_{job['original_filename']}",
                    mime="image/jpeg",
                    use_container_width=True,
                    key=f"download_{job['uuid']}"
                )
            
            with col2:
                if job.get('is_hd_unlocked'):
                    st.button(
                        "💎 HD Ready",
                        disabled=True,
                        use_container_width=True,
                        key=f"hd_{job['uuid']}"
                    )
                else:
                    st.button(
                        "💎 Unlock HD",
                        use_container_width=True,
                        key=f"unlock_hd_{job['uuid']}"
                    )


def display_comparison_slider(
    original_image: bytes,
    processed_image: bytes
) -> None:
    """
    Display images with a comparison slider (requires additional JS).
    For now, shows side-by-side with tabs.
    """
    tab1, tab2, tab3 = st.tabs(["📊 Side by Side", "🖼️ Original", "🎨 Transformed"])
    
    with tab1:
        display_images_side_by_side(original_image, processed_image)
    
    with tab2:
        st.image(original_image, use_container_width=True)
    
    with tab3:
        st.image(processed_image, use_container_width=True)
