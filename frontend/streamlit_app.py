"""
Toonify - Streamlit Frontend Application
AI-based Image Transformation Tool
"""
import streamlit as st
import requests
from PIL import Image
import io
import time

# Configuration
API_BASE_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Toonify - AI Image Transformation",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    /* Main Headers */
    .main-header {
        font-size: 3.5rem;
        font-weight: 900;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        text-align: center;
        color: #555;
        font-size: 1.2rem;
        margin-bottom: 2.5rem;
    }
    
    /* Buttons */
    .stButton > button {
        width: 100%;
        border-radius: 12px;
        height: 3.5rem;
        font-weight: 700;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        border: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
    }
    
    /* Forms */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        padding: 12px;
        font-size: 1rem;
    }
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Cards & Containers */
    .style-card {
        padding: 1.5rem;
        border-radius: 15px;
        border: 3px solid #e8e8e8;
        margin: 1rem 0;
        cursor: pointer;
        transition: all 0.3s ease;
        background: white;
    }
    .style-card:hover {
        border-color: #667eea;
        background: linear-gradient(135deg, #f8f9ff 0%, #fef5ff 100%);
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.2);
    }
    
    /* Sidebar Styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 100%);
    }
    
    /* File Uploader */
    .stFileUploader {
        border: 3px dashed #667eea;
        border-radius: 15px;
        padding: 2rem;
        background: #f8f9ff;
        transition: all 0.3s ease;
    }
    .stFileUploader:hover {
        border-color: #764ba2;
        background: #fef5ff;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px 10px 0 0;
        padding: 12px 24px;
        font-weight: 600;
    }
    
    /* Images */
    img {
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
def init_session_state():
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'access_token' not in st.session_state:
        st.session_state.access_token = None
    if 'refresh_token' not in st.session_state:
        st.session_state.refresh_token = None
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'current_job' not in st.session_state:
        st.session_state.current_job = None


init_session_state()


# API Helper Functions
def api_request(method, endpoint, data=None, files=None, auth=True):
    """Make API request with optional authentication"""
    headers = {}
    if auth and st.session_state.access_token:
        headers["Authorization"] = f"Bearer {st.session_state.access_token}"
    
    url = f"{API_BASE_URL}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=data)
        elif method == "POST":
            if files:
                response = requests.post(url, headers=headers, data=data, files=files)
            else:
                response = requests.post(url, headers=headers, json=data)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        else:
            return None, "Invalid method"
        
        if response.status_code == 200 or response.status_code == 201:
            return response.json(), None
        else:
            error_detail = response.json().get("detail", "Unknown error")
            return None, error_detail
    except requests.exceptions.ConnectionError:
        return None, "Cannot connect to server. Make sure the backend is running."
    except Exception as e:
        return None, str(e)


def login(username, password):
    """Login user"""
    data = {"username": username, "password": password}
    result, error = api_request("POST", "/auth/login", data=data, auth=False)
    
    if result:
        st.session_state.authenticated = True
        st.session_state.access_token = result["access_token"]
        st.session_state.refresh_token = result["refresh_token"]
        st.session_state.user = result["user"]
        return True, None
    return False, error


def signup(email, username, password, full_name=None):
    """Register new user"""
    data = {
        "email": email,
        "username": username,
        "password": password,
        "full_name": full_name
    }
    result, error = api_request("POST", "/auth/signup", data=data, auth=False)
    
    if result:
        st.session_state.authenticated = True
        st.session_state.access_token = result["access_token"]
        st.session_state.refresh_token = result["refresh_token"]
        st.session_state.user = result["user"]
        return True, None
    return False, error


def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.session_state.access_token = None
    st.session_state.refresh_token = None
    st.session_state.user = None
    st.session_state.current_job = None


def upload_image(file, style):
    """Upload image for processing"""
    files = {"file": (file.name, file.getvalue(), file.type)}
    data = {"style": style}
    
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    url = f"{API_BASE_URL}/images/upload?style={style}"
    
    try:
        response = requests.post(url, headers=headers, files=files)
        if response.status_code in [200, 201]:
            return response.json(), None
        return None, response.json().get("detail", "Upload failed")
    except Exception as e:
        return None, str(e)


def process_image(job_id):
    """Start image processing"""
    result, error = api_request("POST", f"/images/{job_id}/process")
    return result, error


def get_job_status(job_id):
    """Get job status"""
    result, error = api_request("GET", f"/images/{job_id}")
    return result, error


def get_image(job_id, file_type):
    """Get image file"""
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    url = f"{API_BASE_URL}/images/file/{job_id}/{file_type}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content, None
        return None, "Failed to load image"
    except Exception as e:
        return None, str(e)


def download_image(job_id):
    """Download processed image"""
    headers = {"Authorization": f"Bearer {st.session_state.access_token}"}
    url = f"{API_BASE_URL}/images/download/{job_id}"
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.content, None
        return None, response.json().get("detail", "Download failed")
    except Exception as e:
        return None, str(e)


# UI Components
def render_auth_page():
    """Render login/signup page"""
    # Hero Section
    st.markdown('<h1 class="main-header">🎨 Toonify</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your photos into stunning cartoon art with AI!</p>', unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 🚀 Fast")
        st.caption("Transform images in seconds")
    with col2:
        st.markdown("### 🎨 5 Styles")
        st.caption("Multiple artistic effects")
    with col3:
        st.markdown("### 📱 Easy")
        st.caption("Simple drag & drop interface")
    
    st.markdown("---")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            with st.form("login_form"):
                st.markdown("### 👋 Welcome Back!")
                st.markdown("")
                
                username = st.text_input("📧 Username or Email", 
                                        placeholder="Enter your username or email",
                                        key="login_username")
                password = st.text_input("🔒 Password", 
                                        type="password",
                                        placeholder="Enter your password",
                                        key="login_password")
                
                st.markdown("")
                submit = st.form_submit_button("🚀 Login", use_container_width=True)
                
                if submit:
                    if username and password:
                        with st.spinner("🔄 Logging in..."):
                            success, error = login(username, password)
                            if success:
                                st.success("✅ Login successful!")
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                st.error(f"❌ Login failed: {error}")
                    else:
                        st.warning("⚠️ Please fill in all fields")
    
    with tab2:
        col_left, col_center, col_right = st.columns([1, 2, 1])
        with col_center:
            with st.form("signup_form"):
                st.markdown("### 🎉 Create Your Account")
                st.markdown("")
                
                email = st.text_input("📧 Email Address", 
                                     placeholder="your.email@example.com",
                                     key="signup_email")
                username = st.text_input("👤 Username", 
                                        placeholder="Choose a unique username",
                                        key="signup_username")
                full_name = st.text_input("📝 Full Name (optional)", 
                                         placeholder="Your full name",
                                         key="signup_fullname")
                
                col_pass1, col_pass2 = st.columns(2)
                with col_pass1:
                    password = st.text_input("🔒 Password", 
                                            type="password",
                                            placeholder="Min 8 characters",
                                            key="signup_password",
                                            help="Min 8 chars with uppercase, lowercase, digit & special char")
                with col_pass2:
                    confirm_password = st.text_input("🔒 Confirm Password", 
                                                    type="password",
                                                    placeholder="Re-enter password",
                                                    key="signup_confirm")
                
                st.markdown("")
                submit = st.form_submit_button("🎨 Create Account", use_container_width=True)
                
                if submit:
                    if email and username and password:
                        if len(password) < 8:
                            st.error("❌ Password must be at least 8 characters long")
                        elif password != confirm_password:
                            st.error("❌ Passwords do not match")
                        else:
                            with st.spinner("🔄 Creating your account..."):
                                success, error = signup(email, username, password, full_name or None)
                                if success:
                                    st.success("✅ Account created successfully!")
                                    st.balloons()
                                    time.sleep(1)
                                    st.rerun()
                                else:
                                    st.error(f"❌ Signup failed: {error}")
                    else:
                        st.warning("⚠️ Please fill in all required fields")


def render_sidebar():
    """Render sidebar with user info and navigation"""
    with st.sidebar:
        # User Profile Card
        st.markdown("### 👤 User Profile")
        if st.session_state.user:
            user = st.session_state.user
            st.markdown(f"""
            <div style='padding: 1rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 12px; color: white; margin-bottom: 1rem;'>
                <h3 style='margin: 0; color: white;'>👋 {user.get('full_name') or user.get('username')}</h3>
                <p style='margin: 0.5rem 0 0 0; opacity: 0.9;'>📧 {user.get('email')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Style Guide
        st.markdown("### 🎨 Available Styles")
        st.markdown("")
        
        styles_info = [
            ("🎬", "Cartoon", "Bold edges & vibrant colors", "#FF6B6B"),
            ("✏️", "Pencil Sketch", "Classic grayscale drawing", "#95A5A6"),
            ("🖍️", "Color Pencil", "Artistic colored strokes", "#FFA07A"),
            ("🔲", "Edge Preserve", "Sharp detail enhancement", "#4ECDC4"),
            ("💧", "Watercolor", "Soft flowing painting", "#A8E6CF"),
        ]
        
        for emoji, name, desc, color in styles_info:
            st.markdown(f"""
            <div style='padding: 0.8rem; margin: 0.5rem 0; border-left: 4px solid {color}; 
                        background: rgba(0,0,0,0.02); border-radius: 8px;'>
                <div style='font-size: 1.1rem; font-weight: 600;'>{emoji} {name}</div>
                <div style='font-size: 0.85rem; color: #666; margin-top: 0.2rem;'>{desc}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Logout Button
        if st.button("🚪 Logout", use_container_width=True, type="primary"):
            logout()
            st.rerun()


def render_main_app():
    """Render main application"""
    render_sidebar()
    
    st.markdown('<h1 class="main-header">🎨 Toonify</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your photos into stunning cartoon art!</p>', unsafe_allow_html=True)
    
    # Main tabs
    tab1, tab2 = st.tabs(["🖼️ Transform Image", "📚 My Gallery"])
    
    with tab1:
        render_transform_tab()
    
    with tab2:
        render_gallery_tab()


def render_transform_tab():
    """Render image transformation tab"""
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📤 Upload Your Image")
        st.markdown("")
        
        uploaded_file = st.file_uploader(
            "Drag and drop or click to browse",
            type=["jpg", "jpeg", "png", "webp"],
            help="Supported formats: JPG, PNG, WEBP | Max size: 10MB",
            label_visibility="collapsed"
        )
        
        if uploaded_file:
            st.markdown("#### 🖼️ Original Image")
            st.image(uploaded_file, use_container_width=True)
            
            # Image info
            file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # MB
            st.caption(f"📁 {uploaded_file.name} ({file_size:.2f} MB)")
        else:
            st.info("👆 Upload an image to get started")
        
        st.markdown("")
        st.markdown("### 🎨 Choose Your Style")
        
        # Style selector with visual cards
        style_options = [
            ("cartoon", "🎬 Cartoon", "Bold edges with vibrant flat colors"),
            ("pencil_sketch", "✏️ Pencil Sketch", "Classic grayscale pencil drawing"),
            ("color_pencil", "🖍️ Color Pencil", "Artistic colored pencil strokes"),
            ("edge_preserve", "🔲 Edge Preserve", "Smooth with sharp edge details"),
            ("watercolor", "💧 Watercolor", "Soft flowing watercolor painting"),
        ]
        
        style = st.radio(
            "Select transformation style",
            options=[s[0] for s in style_options],
            format_func=lambda x: next((f"{s[1]}" for s in style_options if s[0] == x), x),
            label_visibility="collapsed"
        )
        
        # Show selected style description
        selected_style_desc = next((s[2] for s in style_options if s[0] == style), "")
        st.caption(f"ℹ️ {selected_style_desc}")
        
        st.markdown("")
        transform_btn = st.button("🚀 Transform Image", 
                                 use_container_width=True, 
                                 disabled=not uploaded_file,
                                 type="primary")
        
        if transform_btn and uploaded_file:
            with st.spinner("📤 Uploading your image..."):
                result, error = upload_image(uploaded_file, style)
                
                if error:
                    st.error(f"❌ Upload failed: {error}")
                else:
                    job_id = result["job_id"]
                    st.success("✅ Image uploaded successfully!")
                    
                    # Start processing
                    with st.spinner("🎨 Transforming your image with AI magic..."):
                        process_result, process_error = process_image(job_id)
                        
                        if process_error:
                            st.error(f"❌ Processing failed: {process_error}")
                        else:
                            # Poll for completion with animated progress
                            progress_bar = st.progress(0)
                            status_text = st.empty()
                            
                            for i in range(60):  # Max 60 seconds
                                time.sleep(1)
                                progress = min((i + 1) * 2, 100)
                                progress_bar.progress(progress)
                                
                                job_status, _ = get_job_status(job_id)
                                if job_status:
                                    status = job_status.get("status")
                                    
                                    if status == "processing":
                                        status_text.text(f"🔄 Processing... {progress}%")
                                    elif status == "completed":
                                        progress_bar.progress(100)
                                        st.session_state.current_job = job_status
                                        st.success("✨ Image transformed successfully!")
                                        st.balloons()
                                        time.sleep(1)
                                        st.rerun()
                                        break
                                    elif status == "failed":
                                        st.error(f"❌ Processing failed: {job_status.get('error_message')}")
                                        break
                            else:
                                st.warning("⏰ Processing is taking longer than expected. Check your gallery later.")
    
    with col2:
        st.markdown("### ✨ Transformed Result")
        st.markdown("")
        
        if st.session_state.current_job:
            job = st.session_state.current_job
            
            if job.get("status") == "completed":
                # Show comparison image
                st.markdown("#### 🔄 Before & After Comparison")
                comparison_data, _ = get_image(job["id"], "comparison")
                if comparison_data:
                    st.image(comparison_data, use_container_width=True)
                    st.caption("Side-by-side comparison: Original (left) vs Transformed (right)")
                
                st.markdown("")
                st.markdown("---")
                st.markdown("")
                
                # Show processed image
                st.markdown("#### 🎨 Final Result")
                processed_data, _ = get_image(job["id"], "processed")
                if processed_data:
                    st.image(processed_data, use_container_width=True)
                    
                    # Job details
                    st.caption(f"🎭 Style: **{job['style'].replace('_', ' ').title()}**")
                    st.caption(f"📁 File: **{job['original_filename']}**")
                    
                    st.markdown("")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Transformed Image",
                        data=processed_data,
                        file_name=f"toonified_{job['original_filename']}",
                        mime="image/png",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    # Reset button
                    if st.button("🔄 Transform Another Image", use_container_width=True):
                        st.session_state.current_job = None
                        st.rerun()
        else:
            # Welcome message with instructions
            st.info("👈 Upload an image and select a style to see the magic!")
            
            st.markdown("")
            st.markdown("### 🎯 How It Works")
            st.markdown("""
            1. **📤 Upload** - Choose an image from your device
            2. **🎨 Select** - Pick your favorite artistic style
            3. **🚀 Transform** - Let AI do the magic
            4. **📥 Download** - Save your masterpiece
            """)
            
            st.markdown("")
            st.markdown("### 🌟 Style Features")
            
            features = [
                ("🎬", "Cartoon", "Perfect for profile pictures & avatars"),
                ("✏️", "Pencil Sketch", "Ideal for artistic portraits"),
                ("🖍️", "Color Pencil", "Great for creative artwork"),
                ("🔲", "Edge Preserve", "Best for detailed photos"),
                ("💧", "Watercolor", "Beautiful for landscapes"),
            ]
            
            for emoji, name, desc in features:
                st.markdown(f"**{emoji} {name}**")
                st.caption(desc)
                st.markdown("")


def render_gallery_tab():
    """Render user's image gallery"""
    st.markdown("### 📚 Your Transformation Gallery")
    st.markdown("")
    
    # Filter options
    col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 1])
    
    with col_filter1:
        filter_status = st.selectbox(
            "🔍 Filter by Status",
            options=["All", "Completed", "Processing", "Failed"],
            key="gallery_status_filter"
        )
    
    with col_filter2:
        filter_style = st.selectbox(
            "🎨 Filter by Style",
            options=["All", "Cartoon", "Pencil Sketch", "Color Pencil", "Edge Preserve", "Watercolor"],
            key="gallery_style_filter"
        )
    
    with col_filter3:
        sort_order = st.selectbox(
            "📅 Sort",
            options=["Newest", "Oldest"],
            key="gallery_sort"
        )
    
    st.markdown("---")
    
    # Fetch user's jobs
    result, error = api_request("GET", "/images/", data={"page": 1, "per_page": 50})
    
    if error:
        st.error(f"❌ Failed to load gallery: {error}")
        return
    
    jobs = result.get("jobs", [])
    
    # Apply filters
    if filter_status != "All":
        jobs = [j for j in jobs if j['status'] == filter_status.lower()]
    
    if filter_style != "All":
        style_map = {
            "Cartoon": "cartoon",
            "Pencil Sketch": "pencil_sketch",
            "Color Pencil": "color_pencil",
            "Edge Preserve": "edge_preserve",
            "Watercolor": "watercolor"
        }
        jobs = [j for j in jobs if j['style'] == style_map.get(filter_style)]
    
    # Sort jobs
    jobs = sorted(jobs, key=lambda x: x.get('created_at', ''), 
                 reverse=(sort_order == "Newest"))
    
    if not jobs:
        st.info("🎨 No transformations found. Upload an image to get started!")
        return
    
    # Stats summary
    st.markdown(f"**Found {len(jobs)} transformation{'s' if len(jobs) != 1 else ''}**")
    st.markdown("")
    
    # Display jobs in grid
    cols = st.columns(3)
    for idx, job in enumerate(jobs):
        with cols[idx % 3]:
            # Card container
            with st.container():
                # Filename
                filename = job['original_filename']
                display_name = f"{filename[:18]}..." if len(filename) > 18 else filename
                st.markdown(f"**📄 {display_name}**")
                
                # Style and status badges
                style_emoji = {"cartoon": "🎬", "pencil_sketch": "✏️", "color_pencil": "🖍️", 
                              "edge_preserve": "🔲", "watercolor": "💧"}
                st.caption(f"{style_emoji.get(job['style'], '🎨')} {job['style'].replace('_', ' ').title()}")
                
                # Status indicator
                status = job['status']
                if status == 'completed':
                    st.success("✅ Completed", icon="✅")
                    
                    # Load and display thumbnail
                    img_data, _ = get_image(job['id'], "processed")
                    if img_data:
                        st.image(img_data, use_container_width=True)
                    
                    # Action buttons
                    col_a, col_b = st.columns(2)
                    with col_a:
                        if st.button("👁️ View", key=f"view_{job['id']}", use_container_width=True):
                            st.session_state.current_job = job
                            st.rerun()
                    with col_b:
                        if img_data:
                            st.download_button(
                                "📥",
                                data=img_data,
                                file_name=f"toonified_{job['original_filename']}",
                                mime="image/png",
                                key=f"dl_{job['id']}",
                                use_container_width=True
                            )
                
                elif status == 'processing':
                    st.info("⏳ Processing...", icon="⏳")
                    st.progress(50)
                    
                elif status == 'failed':
                    st.error("❌ Failed", icon="❌")
                    if job.get('error_message'):
                        st.caption(f"Error: {job['error_message'][:50]}")
                
                st.markdown("---")


# Main App Logic
def main():
    if not st.session_state.authenticated:
        render_auth_page()
    else:
        render_main_app()


if __name__ == "__main__":
    main()
