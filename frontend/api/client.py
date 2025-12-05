"""
API Client for Backend Communication.
Handles all HTTP requests to the FastAPI backend.
"""

import requests
from typing import Optional, Dict, Any
import streamlit as st

from config import settings


class APIClient:
    """HTTP client for backend API communication."""
    
    def __init__(self):
        self.base_url = settings.BACKEND_URL
        self.timeout = settings.REQUEST_TIMEOUT
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers with authentication token if available."""
        headers = {"Content-Type": "application/json"}
        
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def _get_upload_headers(self) -> Dict[str, str]:
        """Get headers for file upload (no Content-Type)."""
        headers = {}
        
        token = st.session_state.get("access_token")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        return headers
    
    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """Handle API response and raise errors if needed."""
        if response.status_code == 401:
            # Token expired or invalid
            st.session_state.pop("access_token", None)
            st.session_state.pop("user", None)
            raise APIError("Session expired. Please login again.", 401)
        
        if response.status_code >= 400:
            try:
                error_detail = response.json().get("detail", "Unknown error")
            except Exception:
                error_detail = response.text or "Unknown error"
            raise APIError(error_detail, response.status_code)
        
        try:
            return response.json()
        except Exception:
            return {}
    
    # ==================== AUTH ====================
    
    def register(self, email: str, password: str, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Register a new user."""
        data = {
            "email": email,
            "password": password,
        }
        if full_name:
            data["full_name"] = full_name
        
        response = requests.post(
            f"{self.base_url}/auth/register",
            json=data,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login and get tokens."""
        response = requests.post(
            f"{self.base_url}/auth/login",
            json={"email": email, "password": password},
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token."""
        response = requests.post(
            f"{self.base_url}/auth/refresh",
            params={"refresh_token": refresh_token},
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    # ==================== USERS ====================
    
    def get_current_user(self) -> Dict[str, Any]:
        """Get current user profile."""
        response = requests.get(
            f"{self.base_url}/users/me",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def update_profile(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user profile."""
        response = requests.put(
            f"{self.base_url}/users/me",
            headers=self._get_headers(),
            json=data,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def change_password(self, current_password: str, new_password: str) -> Dict[str, Any]:
        """Change user password."""
        response = requests.post(
            f"{self.base_url}/users/me/change-password",
            headers=self._get_headers(),
            json={
                "current_password": current_password,
                "new_password": new_password
            },
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    # ==================== IMAGES ====================
    
    def transform_image(
        self,
        file,
        style: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Upload and transform an image."""
        import json
        
        files = {"file": (file.name, file.getvalue(), file.type)}
        data = {"style": style}
        
        if params:
            data["params"] = json.dumps(params)
        
        response = requests.post(
            f"{self.base_url}/images/transform",
            headers=self._get_upload_headers(),
            files=files,
            data=data,
            timeout=settings.UPLOAD_TIMEOUT
        )
        return self._handle_response(response)
    
    def list_jobs(
        self,
        page: int = 1,
        page_size: int = 20,
        style: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """List user's image jobs."""
        params = {"page": page, "page_size": page_size}
        
        if style:
            params["style"] = style
        if status:
            params["status"] = status
        
        response = requests.get(
            f"{self.base_url}/images",
            headers=self._get_headers(),
            params=params,
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_job(self, job_uuid: str) -> Dict[str, Any]:
        """Get a specific job by UUID."""
        response = requests.get(
            f"{self.base_url}/images/{job_uuid}",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def get_original_image(self, job_uuid: str) -> bytes:
        """Download original image."""
        response = requests.get(
            f"{self.base_url}/images/{job_uuid}/original",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        
        if response.status_code >= 400:
            raise APIError("Failed to download image", response.status_code)
        
        return response.content
    
    def get_processed_image(self, job_uuid: str, hd: bool = False) -> bytes:
        """Download processed image."""
        response = requests.get(
            f"{self.base_url}/images/{job_uuid}/processed",
            headers=self._get_headers(),
            params={"hd": hd},
            timeout=self.timeout
        )
        
        if response.status_code == 402:
            raise APIError("HD download requires payment", 402)
        
        if response.status_code >= 400:
            raise APIError("Failed to download image", response.status_code)
        
        return response.content
    
    def delete_job(self, job_uuid: str) -> None:
        """Delete an image job."""
        response = requests.delete(
            f"{self.base_url}/images/{job_uuid}",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        
        if response.status_code >= 400:
            self._handle_response(response)
    
    def get_user_stats(self) -> Dict[str, Any]:
        """Get user statistics."""
        response = requests.get(
            f"{self.base_url}/users/me/stats",
            headers=self._get_headers(),
            timeout=self.timeout
        )
        
        try:
            return self._handle_response(response)
        except APIError:
            # Stats endpoint might not exist yet
            return {"total_jobs": 0, "by_status": {}, "by_style": {}}
    
    # ==================== PAYMENTS ====================
    
    def create_payment(self, job_id: int) -> Dict[str, Any]:
        """Create a payment intent for HD download."""
        response = requests.post(
            f"{self.base_url}/payments/create",
            headers=self._get_headers(),
            json={"job_id": job_id},
            timeout=self.timeout
        )
        return self._handle_response(response)
    
    def confirm_payment(self, payment_id: int, gateway_reference: str) -> Dict[str, Any]:
        """Confirm a payment."""
        response = requests.post(
            f"{self.base_url}/payments/confirm",
            headers=self._get_headers(),
            json={
                "payment_id": payment_id,
                "gateway_reference": gateway_reference
            },
            timeout=self.timeout
        )
        return self._handle_response(response)


class APIError(Exception):
    """Custom exception for API errors."""
    
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)
