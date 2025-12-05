"""
Streamlit Frontend Application
AI-Based Image Transformation Tool for Cartoon Effect Generation

Main entry point that handles authentication and navigation.
"""

import streamlit as st
from config import settings
from api.client import APIClient
from components.auth_forms import render_login_form, render_register_form
from utils.session import init_session_state, is_authenticated, clear_session

# Page configuration
st.set_page_config(
    page_title="Toonify - AI Image Transformation",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
init_session_state()


def main():
    """Main application entry point."""
    
    # Sidebar
    with st.sidebar:
        st.title("🎨 Toonify")
        st.markdown("---")
        
        if is_authenticated():
            # Show user info
            user = st.session_state.get("user")
            if user:
                st.write(f"👤 **{user.get('full_name') or user.get('email')}**")
                st.caption(user.get('email'))
            
            st.markdown("---")
            
            # Navigation info
            st.markdown("""
            ### 📍 Navigation
            - **🎨 Toonify** - Transform images
            - **🖼️ Gallery** - View history
            - **📊 Dashboard** - Statistics
            """)
            
            st.markdown("---")
            
            # Logout button
            if st.button("🚪 Logout", use_container_width=True):
                clear_session()
                st.rerun()
        else:
            st.info("Please login to access the app")
    
    # Main content
    if is_authenticated():
        render_home_page()
    else:
        render_auth_page()


def render_auth_page():
    """Render authentication page with login/register tabs."""
    
    st.title("🎨 Welcome to Toonify")
    st.markdown("Transform your photos into stunning cartoon-style artwork!")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
        
        with tab1:
            render_login_form()
        
        with tab2:
            render_register_form()
    
    # Features showcase
    st.markdown("---")
    st.subheader("✨ Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🖼️ Multiple Styles
        - Classic Cartoon
        - Pencil Sketch
        - Color Pencil
        - Oil Painting
        - Watercolor
        - Pop Art
        """)
    
    with col2:
        st.markdown("""
        ### ⚙️ Customizable
        - Adjust effect parameters
        - Real-time preview
        - Fine-tune results
        - Multiple formats
        """)
    
    with col3:
        st.markdown("""
        ### 📊 Track Progress
        - Image gallery
        - Processing history
        - Usage statistics
        - Easy downloads
        """)


def render_home_page():
    """Render the home page for authenticated users."""
    
    st.title("🎨 Toonify - AI Image Transformation")
    st.markdown("Transform your photos into amazing cartoon-style artwork!")
    
    # Quick stats
    try:
        client = APIClient()
        stats = client.get_user_stats()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Images", stats.get("total_jobs", 0))
        
        with col2:
            completed = stats.get("by_status", {}).get("done", 0)
            st.metric("Completed", completed)
        
        with col3:
            processing = stats.get("by_status", {}).get("processing", 0)
            st.metric("Processing", processing)
        
        with col4:
            failed = stats.get("by_status", {}).get("failed", 0)
            st.metric("Failed", failed)
    
    except Exception:
        pass  # Stats not critical
    
    st.markdown("---")
    
    # Quick actions
    st.subheader("🚀 Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        ### 🎨 Transform Image
        Upload and transform your photos with various cartoon effects.
        """)
        if st.button("Go to Toonify →", key="goto_toonify", use_container_width=True):
            st.switch_page("pages/1_🎨_Toonify.py")
    
    with col2:
        st.markdown("""
        ### 🖼️ View Gallery
        Browse your transformation history and download images.
        """)
        if st.button("Go to Gallery →", key="goto_gallery", use_container_width=True):
            st.switch_page("pages/2_🖼️_Gallery.py")
    
    with col3:
        st.markdown("""
        ### 📊 Dashboard
        View usage statistics and processing analytics.
        """)
        if st.button("Go to Dashboard →", key="goto_dashboard", use_container_width=True):
            st.switch_page("pages/3_📊_Dashboard.py")
    
    # Recent transformations
    st.markdown("---")
    st.subheader("🕐 Recent Transformations")
    
    try:
        client = APIClient()
        response = client.list_jobs(page=1, page_size=6)
        jobs = response.get("items", [])
        
        if jobs:
            cols = st.columns(3)
            for i, job in enumerate(jobs[:6]):
                with cols[i % 3]:
                    with st.container(border=True):
                        st.caption(f"**{job['style'].upper()}**")
                        st.text(job['original_filename'][:20] + "..." if len(job['original_filename']) > 20 else job['original_filename'])
                        status_emoji = {"done": "✅", "processing": "⏳", "failed": "❌", "queued": "📋"}.get(job['status'], "❓")
                        st.caption(f"{status_emoji} {job['status'].title()}")
        else:
            st.info("No transformations yet. Upload your first image to get started!")
    
    except Exception as e:
        st.warning("Could not load recent transformations")


if __name__ == "__main__":
    main()
