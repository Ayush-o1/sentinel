import pytest
from httpx import AsyncClient

from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestPredictionEndpoints:
    async def _get_auth_headers(self, client: AsyncClient) -> dict[str, str]:
        return await get_auth_headers(client, "predtest@sentinel.dev", "TestPassword1!")

    @pytest.mark.asyncio
    async def test_predict_spam(self, client: AsyncClient):
        headers = await self._get_auth_headers(client)
        response = await client.post(
            "/api/v1/predict",
            json={"text": "CONGRATULATIONS! You've won a $1000 Walmart gift card. Click here to claim your prize!", "message_type": "email"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] == "SPAM"
        assert data["confidence"] >= 0.5
        assert len(data["explanation"]["suspicious_tokens"]) > 0

    @pytest.mark.asyncio
    async def test_predict_ham(self, client: AsyncClient):
        headers = await self._get_auth_headers(client)
        response = await client.post(
            "/api/v1/predict",
            json={"text": "Hey man, are we still on for lunch at 12 tomorrow?", "message_type": "sms"},
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] == "HAM"
        assert data["confidence"] >= 0.5

    @pytest.mark.asyncio
    async def test_predict_edge_cases(self, client: AsyncClient):
        headers = await self._get_auth_headers(client)
        
        # Empty string (should fail validation because text length < 10)
        response = await client.post("/api/v1/predict", json={"text": "   ", "message_type": "text"}, headers=headers)
        assert response.status_code == 422
        
        # Only punctuation/emojis (should pass validation and be classified by ML pipeline)
        # Note: length >= 10 to pass length validation
        response = await client.post("/api/v1/predict", json={"text": "🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔🤔", "message_type": "text"}, headers=headers)
        assert response.status_code == 200
        
        # Extremely long string (should fail validation because length > 5000)
        long_str = "spam " * 2000
        response = await client.post("/api/v1/predict", json={"text": long_str, "message_type": "email"}, headers=headers)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_get_history(self, client: AsyncClient):
        headers = await self._get_auth_headers(client)
        # Create a prediction first
        await client.post("/api/v1/predict", json={"text": "Hello, how are you today?", "message_type": "sms"}, headers=headers)
        response = await client.get("/api/v1/predictions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) >= 1
