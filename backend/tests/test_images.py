"""
Image processing endpoint tests.
"""

import pytest
from httpx import AsyncClient
import io


class TestImageEndpoints:
    """Test image processing endpoints."""
    
    async def get_auth_headers(self, client: AsyncClient, test_user_data: dict) -> dict:
        """Helper to get authentication headers."""
        # Register and login
        await client.post("/auth/register", json=test_user_data)
        
        response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}
    
    @pytest.mark.asyncio
    async def test_list_jobs_empty(self, client: AsyncClient, test_user_data):
        """Test listing jobs when none exist."""
        headers = await self.get_auth_headers(client, test_user_data)
        
        response = await client.get("/images", headers=headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_list_jobs_unauthorized(self, client: AsyncClient):
        """Test listing jobs without authentication."""
        response = await client.get("/images")
        
        assert response.status_code == 403  # No auth header
    
    @pytest.mark.asyncio
    async def test_get_nonexistent_job(self, client: AsyncClient, test_user_data):
        """Test getting a job that doesn't exist."""
        headers = await self.get_auth_headers(client, test_user_data)
        
        response = await client.get("/images/nonexistent-uuid", headers=headers)
        
        assert response.status_code == 404


class TestImageProcessing:
    """Test image processing functions."""
    
    def test_cartoon_effect_params(self):
        """Test cartoon effect parameter validation."""
        from app.schemas.image import CartoonParams
        
        params = CartoonParams(
            blur_kernel_size=7,
            threshold_block_size=9,
            threshold_c=9
        )
        
        assert params.blur_kernel_size == 7
        assert params.threshold_block_size == 9
    
    def test_sketch_effect_params(self):
        """Test sketch effect parameter validation."""
        from app.schemas.image import SketchParams
        
        params = SketchParams(
            blur_kernel_size=21,
            invert=True
        )
        
        assert params.blur_kernel_size == 21
        assert params.invert is True
