"""
Integration tests for authentication endpoints.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthEndpoints:

    async def test_register_success(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "newuser@sentinel.dev",
            "password": "NewPass1!",
            "full_name": "New User",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@sentinel.dev"
        assert "id" in data
        assert "hashed_password" not in data  # Never expose password hash

    async def test_register_duplicate_email(self, client: AsyncClient):
        payload = {
            "email": "duplicate@sentinel.dev",
            "password": "TestPass1!",
            "full_name": "Test User",
        }
        await client.post("/api/v1/auth/register", json=payload)
        response = await client.post("/api/v1/auth/register", json=payload)
        assert response.status_code == 409

    async def test_register_weak_password(self, client: AsyncClient):
        response = await client.post("/api/v1/auth/register", json={
            "email": "user@sentinel.dev",
            "password": "password",  # No uppercase, no digit
            "full_name": "Test",
        })
        assert response.status_code == 422

    async def test_login_success(self, client: AsyncClient):
        # Register first
        await client.post("/api/v1/auth/register", json={
            "email": "login@sentinel.dev",
            "password": "LoginPass1!",
            "full_name": "Login User",
        })
        # Login
        response = await client.post("/api/v1/auth/login", json={
            "email": "login@sentinel.dev",
            "password": "LoginPass1!",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_wrong_password(self, client: AsyncClient):
        await client.post("/api/v1/auth/register", json={
            "email": "wrong@sentinel.dev",
            "password": "RightPass1!",
            "full_name": "Test",
        })
        response = await client.post("/api/v1/auth/login", json={
            "email": "wrong@sentinel.dev",
            "password": "WrongPass1!",
        })
        assert response.status_code == 401

    async def test_me_requires_auth(self, client: AsyncClient):
        response = await client.get("/api/v1/auth/me")
        assert response.status_code == 401
