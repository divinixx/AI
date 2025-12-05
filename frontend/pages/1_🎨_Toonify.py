"""
Toonify Page - Main Image Transformation
Upload images and apply cartoon effects.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import APIClient, APIError
from components.image_upload import render_image_uploader, render_image_preview
from components.style_selector import render_style_selector, get_style_params
from components.image_display import display_images_side_by_side, display_comparison_slider
from utils.session import is_authenticated, get_current_job, set_current_job

# Page configuration
st.set_page_config(
    page_title="Toonify - Transform",
    page_icon="🎨",
    layout="wide"
)

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.stop()


def main():
    """Main page content."""
    st.title("🎨 Toonify - Transform Your Images")
    st.markdown("Upload an image and transform it into stunning cartoon-style artwork!")
    
    # Create two columns for layout
    col_upload, col_result = st.columns([1, 1])
    
    with col_upload:
        st.markdown("### 📤 Upload Image")
        
        # Image upload
        uploaded_file = render_image_uploader(key="toonify_upload")
        
        if uploaded_file:
            # Show preview
            st.image(uploaded_file, caption="Original Image", use_container_width=True)
            
            st.markdown("---")
            
            # Style selection
            selected_style = render_style_selector(key="toonify_style")
            
            st.markdown("---")
            
            # Parameters
            params = get_style_params(selected_style, key="toonify_params")
            
            st.markdown("---")
            
            # Transform button
            if st.button(
                "🚀 Transform Image",
                type="primary",
                use_container_width=True,
                key="transform_btn"
            ):
                transform_image(uploaded_file, selected_style, params)
    
    with col_result:
        st.markdown("### 🎨 Result")
        
        # Show current job result if available
        current_job = get_current_job()
        
        if current_job and current_job.get('status') == 'done':
            display_result(current_job)
        elif current_job and current_job.get('status') == 'processing':
            st.info("⏳ Processing... Please wait")
            
            # Poll for completion
            with st.spinner("Processing your image..."):
                check_job_status(current_job['uuid'])
        elif current_job and current_job.get('status') == 'failed':
            st.error(f"❌ Processing failed: {current_job.get('error_message', 'Unknown error')}")
        else:
            st.info("👆 Upload an image and click Transform to see the result")
            
            # Show placeholder
            st.markdown("""
            <div style="
                border: 2px dashed #ccc;
                border-radius: 10px;
                padding: 100px 20px;
                text-align: center;
                color: #888;
            ">
                <h3>🖼️</h3>
                <p>Your transformed image will appear here</p>
            </div>
            """, unsafe_allow_html=True)


def transform_image(uploaded_file, style: str, params: dict):
    """Transform the uploaded image."""
    try:
        with st.spinner("🎨 Transforming your image..."):
            client = APIClient()
            
            # Upload and transform
            job = client.transform_image(
                file=uploaded_file,
                style=style,
                params=params if params else None
            )
            
            # Save job to session
            set_current_job(job)
            
            if job['status'] == 'done':
                st.success("✅ Transformation complete!")
                st.rerun()
            elif job['status'] == 'failed':
                st.error(f"❌ Failed: {job.get('error_message', 'Unknown error')}")
            else:
                st.info("⏳ Processing...")
                st.rerun()
    
    except APIError as e:
        st.error(f"❌ Error: {e.message}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")


def check_job_status(job_uuid: str):
    """Check and update job status."""
    import time
    
    client = APIClient()
    max_attempts = 30
    
    for _ in range(max_attempts):
        try:
            job = client.get_job(job_uuid)
            set_current_job(job)
            
            if job['status'] == 'done':
                st.success("✅ Complete!")
                st.rerun()
                return
            elif job['status'] == 'failed':
                st.error(f"❌ Failed: {job.get('error_message')}")
                return
            
            time.sleep(2)
        except Exception:
            break
    
    st.warning("Processing is taking longer than expected. Check the Gallery for results.")


def display_result(job: dict):
    """Display the transformation result."""
    try:
        client = APIClient()
        
        # Fetch images
        original = client.get_original_image(job['uuid'])
        processed = client.get_processed_image(job['uuid'])
        
        # Display comparison
        display_comparison_slider(original, processed)
        
        st.markdown("---")
        
        # Info
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"**Style:** {job['style'].replace('_', ' ').title()}")
            st.markdown(f"**File:** {job['original_filename']}")
        
        with col2:
            created = job.get('created_at', '')[:19].replace('T', ' ')
            st.markdown(f"**Created:** {created}")
            
            if job.get('is_hd_unlocked'):
                st.markdown("**Quality:** 💎 HD Unlocked")
            else:
                st.markdown("**Quality:** Standard")
        
        st.markdown("---")
        
        # Download buttons
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.download_button(
                label="📥 Download Result",
                data=processed,
                file_name=f"toonify_{job['style']}_{job['original_filename']}",
                mime="image/jpeg",
                use_container_width=True
            )
        
        with col2:
            st.download_button(
                label="📥 Download Original",
                data=original,
                file_name=job['original_filename'],
                mime="image/jpeg",
                use_container_width=True
            )
        
        with col3:
            if not job.get('is_hd_unlocked'):
                if st.button("💎 Unlock HD ($2.99)", use_container_width=True):
                    st.info("Payment integration coming soon!")
            else:
                st.button("💎 HD Ready", disabled=True, use_container_width=True)
        
        # Transform another
        st.markdown("---")
        if st.button("🔄 Transform Another Image", use_container_width=True):
            set_current_job(None)
            st.rerun()
    
    except APIError as e:
        st.error(f"Error loading images: {e.message}")
    except Exception as e:
        st.error(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
