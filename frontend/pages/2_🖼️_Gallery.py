"""
Gallery Page - Image History
Browse and manage processed images.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.client import APIClient, APIError
from components.image_display import display_image_card
from utils.session import is_authenticated

# Page configuration
st.set_page_config(
    page_title="Toonify - Gallery",
    page_icon="🖼️",
    layout="wide"
)

# Check authentication
if not is_authenticated():
    st.warning("⚠️ Please login to access this page")
    st.stop()


def main():
    """Main page content."""
    st.title("🖼️ Gallery - Your Transformations")
    st.markdown("Browse your image transformation history")
    
    # Filters
    with st.expander("🔍 Filters", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            style_filter = st.selectbox(
                "Style",
                options=[None, "cartoon", "sketch", "color_pencil", "oil_painting", "watercolor", "pop_art"],
                format_func=lambda x: "All Styles" if x is None else x.replace("_", " ").title(),
                key="gallery_style_filter"
            )
        
        with col2:
            status_filter = st.selectbox(
                "Status",
                options=[None, "done", "processing", "queued", "failed"],
                format_func=lambda x: "All Status" if x is None else x.title(),
                key="gallery_status_filter"
            )
        
        with col3:
            page_size = st.selectbox(
                "Per Page",
                options=[12, 24, 48],
                key="gallery_page_size"
            )
    
    # Pagination state
    if "gallery_page" not in st.session_state:
        st.session_state.gallery_page = 1
    
    # Load jobs
    load_gallery(style_filter, status_filter, page_size)


def load_gallery(style_filter, status_filter, page_size):
    """Load and display gallery images."""
    try:
        client = APIClient()
        
        # Fetch jobs
        response = client.list_jobs(
            page=st.session_state.gallery_page,
            page_size=page_size,
            style=style_filter,
            status=status_filter
        )
        
        jobs = response.get("items", [])
        total = response.get("total", 0)
        total_pages = response.get("total_pages", 1)
        
        if not jobs:
            st.info("📭 No images found. Start by transforming an image!")
            
            if st.button("🎨 Go to Toonify"):
                st.switch_page("pages/1_🎨_Toonify.py")
            return
        
        # Stats
        st.markdown(f"**Showing {len(jobs)} of {total} images** | Page {st.session_state.gallery_page} of {total_pages}")
        
        st.markdown("---")
        
        # Display grid
        cols = st.columns(3)
        
        for i, job in enumerate(jobs):
            with cols[i % 3]:
                display_job_card(job, client)
        
        # Pagination
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.gallery_page > 1:
                if st.button("⬅️ Previous", use_container_width=True):
                    st.session_state.gallery_page -= 1
                    st.rerun()
        
        with col2:
            st.markdown(f"<center>Page {st.session_state.gallery_page} of {total_pages}</center>", unsafe_allow_html=True)
        
        with col3:
            if st.session_state.gallery_page < total_pages:
                if st.button("Next ➡️", use_container_width=True):
                    st.session_state.gallery_page += 1
                    st.rerun()
    
    except APIError as e:
        st.error(f"❌ Error loading gallery: {e.message}")
    except Exception as e:
        st.error(f"❌ Connection error: {str(e)}")


def display_job_card(job: dict, client: APIClient):
    """Display a single job card."""
    with st.container(border=True):
        # Status indicator
        status_emoji = {
            "done": "✅",
            "processing": "⏳",
            "queued": "📋",
            "failed": "❌"
        }.get(job['status'], "❓")
        
        # Header
        col1, col2 = st.columns([3, 1])
        
        with col1:
            filename = job['original_filename']
            if len(filename) > 20:
                filename = filename[:17] + "..."
            st.markdown(f"**{filename}**")
        
        with col2:
            st.markdown(f"{status_emoji}")
        
        # Style badge
        style_name = job['style'].replace('_', ' ').title()
        st.caption(f"🎨 {style_name}")
        
        # Image preview
        if job['status'] == 'done':
            try:
                processed = client.get_processed_image(job['uuid'])
                st.image(processed, use_container_width=True)
            except Exception:
                st.info("Image preview unavailable")
        else:
            st.markdown(f"""
            <div style="
                background: #f0f0f0;
                border-radius: 5px;
                padding: 40px;
                text-align: center;
                color: #888;
            ">
                {status_emoji} {job['status'].title()}
            </div>
            """, unsafe_allow_html=True)
        
        # Date
        created = job.get('created_at', '')[:10]
        st.caption(f"📅 {created}")
        
        # Actions
        col1, col2 = st.columns(2)
        
        with col1:
            if job['status'] == 'done':
                try:
                    processed = client.get_processed_image(job['uuid'])
                    st.download_button(
                        "📥",
                        data=processed,
                        file_name=f"toonify_{job['original_filename']}",
                        mime="image/jpeg",
                        key=f"dl_{job['uuid']}",
                        use_container_width=True
                    )
                except Exception:
                    pass
        
        with col2:
            if st.button("🗑️", key=f"del_{job['uuid']}", use_container_width=True):
                delete_job(job['uuid'], client)


def delete_job(job_uuid: str, client: APIClient):
    """Delete a job."""
    try:
        client.delete_job(job_uuid)
        st.success("Deleted!")
        st.rerun()
    except APIError as e:
        st.error(f"Failed to delete: {e.message}")


if __name__ == "__main__":
    main()
