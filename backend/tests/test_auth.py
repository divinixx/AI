"""
Authentication endpoint tests.
"""

import pytest
from httpx import AsyncClient


class TestAuthEndpoints:
    """Test authentication endpoints."""
    
    @pytest.mark.asyncio
    async def test_register_user(self, client: AsyncClient, test_user_data):
        """Test user registration."""
        response = await client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert "uuid" in data
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user_data):
        """Test registration with duplicate email."""
        # First registration
        await client.post("/auth/register", json=test_user_data)
        
        # Second registration with same email
        response = await client.post("/auth/register", json=test_user_data)
        
        assert response.status_code == 400
        assert "already registered" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user_data):
        """Test successful login."""
        # Register first
        await client.post("/auth/register", json=test_user_data)
        
        # Login
        response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
    
    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user_data):
        """Test login with invalid password."""
        # Register first
        await client.post("/auth/register", json=test_user_data)
        
        # Login with wrong password
        response = await client.post("/auth/login", json={
            "email": test_user_data["email"],
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
    
    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Test login with nonexistent user."""
        response = await client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401
