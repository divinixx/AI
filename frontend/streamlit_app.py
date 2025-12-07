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
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        height: 3rem;
        font-weight: bold;
    }
    .success-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    .error-box {
        padding: 1rem;
        border-radius: 10px;
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
    }
    .style-card {
        padding: 1rem;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
        margin: 0.5rem 0;
        cursor: pointer;
    }
    .style-card:hover {
        border-color: #667eea;
        background-color: #f8f9fa;
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
    st.markdown('<h1 class="main-header">🎨 Toonify</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Transform your photos into stunning cartoon art!</p>', unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
    
    with tab1:
        with st.form("login_form"):
            st.subheader("Welcome Back!")
            username = st.text_input("Username or Email", key="login_username")
            password = st.text_input("Password", type="password", key="login_password")
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    with st.spinner("Logging in..."):
                        success, error = login(username, password)
                        if success:
                            st.success("Login successful!")
                            st.rerun()
                        else:
                            st.error(f"Login failed: {error}")
                else:
                    st.warning("Please fill in all fields")
    
    with tab2:
        with st.form("signup_form"):
            st.subheader("Create Account")
            email = st.text_input("Email", key="signup_email")
            username = st.text_input("Username", key="signup_username")
            full_name = st.text_input("Full Name (optional)", key="signup_fullname")
            password = st.text_input("Password", type="password", key="signup_password",
                                    help="Min 8 chars, uppercase, lowercase, digit, special char")
            confirm_password = st.text_input("Confirm Password", type="password", key="signup_confirm")
            submit = st.form_submit_button("Sign Up", use_container_width=True)
            
            if submit:
                if email and username and password:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    else:
                        with st.spinner("Creating account..."):
                            success, error = signup(email, username, password, full_name or None)
                            if success:
                                st.success("Account created successfully!")
                                st.rerun()
                            else:
                                st.error(f"Signup failed: {error}")
                else:
                    st.warning("Please fill in all required fields")


def render_sidebar():
    """Render sidebar with user info and navigation"""
    with st.sidebar:
        st.markdown("### 👤 User Profile")
        if st.session_state.user:
            st.write(f"**{st.session_state.user.get('full_name') or st.session_state.user.get('username')}**")
            st.write(f"📧 {st.session_state.user.get('email')}")
        
        st.markdown("---")
        
        st.markdown("### 🎨 Available Styles")
        styles = [
            ("🎬 Cartoon", "Classic cartoon with bold edges"),
            ("✏️ Pencil Sketch", "Grayscale pencil drawing"),
            ("🖍️ Color Pencil", "Colored pencil art style"),
            ("🔲 Edge Preserve", "Enhanced detail preservation"),
            ("💧 Watercolor", "Soft watercolor painting"),
        ]
        
        for name, desc in styles:
            st.markdown(f"**{name}**")
            st.caption(desc)
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
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
        st.subheader("📤 Upload Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image",
            type=["jpg", "jpeg", "png", "webp"],
            help="Max file size: 10MB"
        )
        
        if uploaded_file:
            st.image(uploaded_file, caption="Original Image", use_container_width=True)
        
        st.subheader("🎨 Select Style")
        style = st.selectbox(
            "Choose transformation style",
            options=[
                ("cartoon", "🎬 Cartoon"),
                ("pencil_sketch", "✏️ Pencil Sketch"),
                ("color_pencil", "🖍️ Color Pencil"),
                ("edge_preserve", "🔲 Edge Preserve"),
                ("watercolor", "💧 Watercolor"),
            ],
            format_func=lambda x: x[1]
        )
        
        if st.button("🚀 Transform Image", use_container_width=True, disabled=not uploaded_file):
            if uploaded_file:
                with st.spinner("Uploading image..."):
                    result, error = upload_image(uploaded_file, style[0])
                    
                    if error:
                        st.error(f"Upload failed: {error}")
                    else:
                        job_id = result["job_id"]
                        st.success("Image uploaded! Starting processing...")
                        
                        # Start processing
                        with st.spinner("Processing image..."):
                            process_result, process_error = process_image(job_id)
                            
                            if process_error:
                                st.error(f"Processing failed: {process_error}")
                            else:
                                # Poll for completion
                                progress_bar = st.progress(0)
                                status_text = st.empty()
                                
                                for i in range(60):  # Max 60 seconds
                                    time.sleep(1)
                                    progress_bar.progress(min((i + 1) * 2, 100))
                                    
                                    job_status, _ = get_job_status(job_id)
                                    if job_status:
                                        status = job_status.get("status")
                                        status_text.text(f"Status: {status}")
                                        
                                        if status == "completed":
                                            st.session_state.current_job = job_status
                                            st.success("✅ Image transformed successfully!")
                                            st.rerun()
                                            break
                                        elif status == "failed":
                                            st.error(f"Processing failed: {job_status.get('error_message')}")
                                            break
                                else:
                                    st.warning("Processing is taking longer than expected. Check gallery later.")
    
    with col2:
        st.subheader("✨ Result")
        
        if st.session_state.current_job:
            job = st.session_state.current_job
            
            if job.get("status") == "completed":
                # Show comparison
                comparison_data, _ = get_image(job["id"], "comparison")
                if comparison_data:
                    st.image(comparison_data, caption="Original vs Toonified", use_container_width=True)
                
                # Show processed image
                processed_data, _ = get_image(job["id"], "processed")
                if processed_data:
                    st.image(processed_data, caption="Toonified Image", use_container_width=True)
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Toonified Image",
                        data=processed_data,
                        file_name=f"toonified_{job['original_filename']}",
                        mime="image/png",
                        use_container_width=True
                    )
        else:
            st.info("👆 Upload an image and select a style to get started!")
            
            # Show sample styles
            st.markdown("### 🎯 Style Preview")
            st.markdown("""
            - **Cartoon**: Bold outlines with flat, vibrant colors
            - **Pencil Sketch**: Classic grayscale pencil drawing effect
            - **Color Pencil**: Artistic colored pencil strokes
            - **Edge Preserve**: Smooth colors with sharp edge details
            - **Watercolor**: Soft, flowing watercolor painting effect
            """)


def render_gallery_tab():
    """Render user's image gallery"""
    st.subheader("📚 Your Transformations")
    
    # Fetch user's jobs
    result, error = api_request("GET", "/images/", data={"page": 1, "per_page": 20})
    
    if error:
        st.error(f"Failed to load gallery: {error}")
        return
    
    jobs = result.get("jobs", [])
    
    if not jobs:
        st.info("No transformations yet. Upload an image to get started!")
        return
    
    # Display jobs in grid
    cols = st.columns(3)
    for idx, job in enumerate(jobs):
        with cols[idx % 3]:
            with st.container():
                st.markdown(f"**{job['original_filename'][:20]}...**" if len(job['original_filename']) > 20 else f"**{job['original_filename']}**")
                st.caption(f"Style: {job['style'].replace('_', ' ').title()}")
                st.caption(f"Status: {job['status'].title()}")
                
                if job['status'] == 'completed':
                    # Load thumbnail
                    img_data, _ = get_image(job['id'], "processed")
                    if img_data:
                        st.image(img_data, use_container_width=True)
                    
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
                elif job['status'] == 'processing':
                    st.info("⏳ Processing...")
                elif job['status'] == 'failed':
                    st.error("❌ Failed")
                
                st.markdown("---")


# Main App Logic
def main():
    if not st.session_state.authenticated:
        render_auth_page()
    else:
        render_main_app()


if __name__ == "__main__":
    main()
