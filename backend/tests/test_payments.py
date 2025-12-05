"""
Payment endpoint tests.
"""

import pytest
from httpx import AsyncClient


class TestPaymentEndpoints:
    """Test payment endpoints."""
    
    async def get_auth_headers(self, client: AsyncClient, test_user_data: dict) -> dict:
        """Helper to get authentication headers."""
        await client.post("/auth/register", json=test_user_data)
        
        response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        tokens = response.json()
        return {"Authorization": f"Bearer {tokens['access_token']}"}
    
    @pytest.mark.asyncio
    async def test_create_payment_nonexistent_job(self, client: AsyncClient, test_user_data):
        """Test creating payment for nonexistent job."""
        headers = await self.get_auth_headers(client, test_user_data)
        
        response = await client.post(
            "/payments/create",
            headers=headers,
            json={"job_id": 99999}
        )
        
        assert response.status_code == 404
    
    @pytest.mark.asyncio
    async def test_create_payment_unauthorized(self, client: AsyncClient):
        """Test creating payment without authentication."""
        response = await client.post(
            "/payments/create",
            json={"job_id": 1}
        )
        
        assert response.status_code == 403
