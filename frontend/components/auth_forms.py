"""
Authentication Forms Component.
Login and registration form rendering.
"""

import streamlit as st
from api.client import APIClient, APIError
from utils.session import save_auth_tokens


def render_login_form():
    """Render the login form."""
    
    st.markdown("### 🔐 Login to Your Account")
    
    with st.form("login_form"):
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            key="login_email"
        )
        
        password = st.text_input(
            "Password",
            type="password",
            placeholder="Enter your password",
            key="login_password"
        )
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submitted = st.form_submit_button(
                "🔑 Login",
                use_container_width=True,
                type="primary"
            )
        
        if submitted:
            if not email or not password:
                st.error("Please enter both email and password")
                return
            
            try:
                client = APIClient()
                tokens = client.login(email, password)
                
                # Save tokens and user info
                save_auth_tokens(tokens)
                
                # Get user profile
                user = client.get_current_user()
                st.session_state["user"] = user
                
                st.success("✅ Login successful!")
                st.rerun()
                
            except APIError as e:
                st.error(f"❌ Login failed: {e.message}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")


def render_register_form():
    """Render the registration form."""
    
    st.markdown("### 📝 Create New Account")
    
    with st.form("register_form"):
        full_name = st.text_input(
            "Full Name",
            placeholder="John Doe",
            key="register_name"
        )
        
        email = st.text_input(
            "Email",
            placeholder="your@email.com",
            key="register_email"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Min 8 characters",
                key="register_password"
            )
        
        with col2:
            confirm_password = st.text_input(
                "Confirm Password",
                type="password",
                placeholder="Repeat password",
                key="register_confirm"
            )
        
        submitted = st.form_submit_button(
            "📝 Create Account",
            use_container_width=True,
            type="primary"
        )
        
        if submitted:
            # Validation
            if not email or not password:
                st.error("Email and password are required")
                return
            
            if len(password) < 8:
                st.error("Password must be at least 8 characters")
                return
            
            if password != confirm_password:
                st.error("Passwords do not match")
                return
            
            try:
                client = APIClient()
                user = client.register(email, password, full_name or None)
                
                st.success("✅ Account created successfully! Please login.")
                
            except APIError as e:
                st.error(f"❌ Registration failed: {e.message}")
            except Exception as e:
                st.error(f"❌ Connection error: {str(e)}")
