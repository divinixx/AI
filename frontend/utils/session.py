"""
Session State Management.
Handles Streamlit session state for authentication and app state.
"""

import streamlit as st
from typing import Dict, Any, Optional


def init_session_state() -> None:
    """Initialize session state with default values."""
    defaults = {
        "access_token": None,
        "refresh_token": None,
        "user": None,
        "current_job": None,
        "gallery_page": 1,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def is_authenticated() -> bool:
    """Check if user is authenticated."""
    return st.session_state.get("access_token") is not None


def save_auth_tokens(tokens: Dict[str, Any]) -> None:
    """
    Save authentication tokens to session state.
    
    Args:
        tokens: Dictionary containing access_token, refresh_token, etc.
    """
    st.session_state["access_token"] = tokens.get("access_token")
    st.session_state["refresh_token"] = tokens.get("refresh_token")


def get_access_token() -> Optional[str]:
    """Get the current access token."""
    return st.session_state.get("access_token")


def get_refresh_token() -> Optional[str]:
    """Get the current refresh token."""
    return st.session_state.get("refresh_token")


def get_current_user() -> Optional[Dict[str, Any]]:
    """Get the current user data."""
    return st.session_state.get("user")


def set_current_user(user: Dict[str, Any]) -> None:
    """Set the current user data."""
    st.session_state["user"] = user


def clear_session() -> None:
    """Clear all session state (logout)."""
    keys_to_clear = [
        "access_token",
        "refresh_token", 
        "user",
        "current_job"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            st.session_state[key] = None


def set_current_job(job: Dict[str, Any]) -> None:
    """Set the current job being viewed/processed."""
    st.session_state["current_job"] = job


def get_current_job() -> Optional[Dict[str, Any]]:
    """Get the current job."""
    return st.session_state.get("current_job")
