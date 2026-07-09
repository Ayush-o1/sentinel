"""
Integration tests for prediction history endpoints.

GET    /api/v1/predictions          — List paginated history
GET    /api/v1/predictions/{id}     — Get single prediction detail
DELETE /api/v1/predictions/{id}     — Delete a prediction
"""

import pytest
from httpx import AsyncClient

from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestHistoryEndpoints:
    """Tests for the prediction history CRUD endpoints."""

    async def _seed_prediction(self, client: AsyncClient, headers: dict) -> dict:
        """Create a prediction and return the response data."""
        response = await client.post(
            "/api/v1/predict",
            json={"text": "Congratulations! You've won a prize. Claim it now!", "message_type": "sms"},
            headers=headers,
        )
        assert response.status_code == 200
        return response.json()

    # -----------------------------------------------------------------------
    # GET /api/v1/predictions
    # -----------------------------------------------------------------------

    async def test_history_requires_auth(self, client: AsyncClient) -> None:
        """History endpoint must reject unauthenticated requests."""
        response = await client.get("/api/v1/predictions")
        assert response.status_code == 401

    async def test_history_empty_for_new_user(self, client: AsyncClient) -> None:
        """A new user should get an empty list, not an error."""
        headers = await get_auth_headers(client, "history_empty@sentinel.dev", "HistoryPass1!")
        response = await client.get("/api/v1/predictions", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["items"] == []

    async def test_history_returns_paginated_shape(self, client: AsyncClient) -> None:
        """History response must include pagination metadata."""
        headers = await get_auth_headers(client, "history_page@sentinel.dev", "HistoryPass1!")
        await self._seed_prediction(client, headers)

        response = await client.get("/api/v1/predictions", headers=headers)
        assert response.status_code == 200
        data = response.json()

        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "page_size" in data
        assert "total_pages" in data
        assert len(data["items"]) == 1

    async def test_history_item_shape(self, client: AsyncClient) -> None:
        """Each history item must include the expected fields."""
        headers = await get_auth_headers(client, "history_shape@sentinel.dev", "HistoryPass1!")
        await self._seed_prediction(client, headers)

        response = await client.get("/api/v1/predictions", headers=headers)
        item = response.json()["items"][0]

        assert "id" in item
        assert "verdict" in item
        assert "confidence" in item
        assert "risk_level" in item
        assert "message_type" in item
        assert "created_at" in item
        assert item["verdict"] in ("SPAM", "HAM")

    async def test_history_filter_by_verdict(self, client: AsyncClient) -> None:
        """Filtering by verdict=SPAM should only return SPAM predictions."""
        headers = await get_auth_headers(client, "history_filter@sentinel.dev", "HistoryPass1!")
        await self._seed_prediction(client, headers)

        for verdict_filter in ["SPAM", "HAM"]:
            response = await client.get(
                f"/api/v1/predictions?verdict={verdict_filter}", headers=headers
            )
            assert response.status_code == 200
            for item in response.json()["items"]:
                assert item["verdict"] == verdict_filter

    async def test_history_invalid_verdict_filter(self, client: AsyncClient) -> None:
        """An invalid verdict filter should return 422."""
        headers = await get_auth_headers(client, "history_inv@sentinel.dev", "HistoryPass1!")
        response = await client.get("/api/v1/predictions?verdict=MAYBE", headers=headers)
        assert response.status_code == 422

    async def test_history_pagination(self, client: AsyncClient) -> None:
        """page and page_size parameters should control results."""
        headers = await get_auth_headers(client, "history_pag@sentinel.dev", "HistoryPass1!")

        # Create 3 predictions
        for _ in range(3):
            await self._seed_prediction(client, headers)

        # First page of 2
        response = await client.get("/api/v1/predictions?page=1&page_size=2", headers=headers)
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 2
        assert data["total_pages"] == 2

        # Second page
        response2 = await client.get("/api/v1/predictions?page=2&page_size=2", headers=headers)
        data2 = response2.json()
        assert len(data2["items"]) == 1

    # -----------------------------------------------------------------------
    # GET /api/v1/predictions/{id}
    # -----------------------------------------------------------------------

    async def test_get_prediction_detail(self, client: AsyncClient) -> None:
        """GET by ID should return full prediction detail."""
        headers = await get_auth_headers(client, "history_det@sentinel.dev", "HistoryPass1!")
        pred = await self._seed_prediction(client, headers)

        prediction_id = pred["prediction_id"]
        response = await client.get(f"/api/v1/predictions/{prediction_id}", headers=headers)
        assert response.status_code == 200

        detail = response.json()
        assert detail["id"] == prediction_id
        assert "original_text" in detail
        assert "processed_text" in detail
        assert "explanation" in detail

    async def test_get_prediction_not_found(self, client: AsyncClient) -> None:
        """Fetching a non-existent prediction ID should return 404."""
        headers = await get_auth_headers(client, "history_nf@sentinel.dev", "HistoryPass1!")
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.get(f"/api/v1/predictions/{fake_id}", headers=headers)
        assert response.status_code == 404

    async def test_get_prediction_other_user_returns_404(self, client: AsyncClient) -> None:
        """A user cannot access another user's prediction — must get 404 (not 403)."""
        headers_a = await get_auth_headers(client, "hist_a@sentinel.dev", "HistAPass1!")
        headers_b = await get_auth_headers(client, "hist_b@sentinel.dev", "HistBPass1!")

        # User A creates a prediction
        pred = await self._seed_prediction(client, headers_a)
        prediction_id = pred["prediction_id"]

        # User B tries to access it — must get 404 (no privilege leak via 403)
        response = await client.get(f"/api/v1/predictions/{prediction_id}", headers=headers_b)
        assert response.status_code == 404

    # -----------------------------------------------------------------------
    # DELETE /api/v1/predictions/{id}
    # -----------------------------------------------------------------------

    async def test_delete_prediction(self, client: AsyncClient) -> None:
        """Deleting a prediction should return 204 and remove it from history."""
        headers = await get_auth_headers(client, "history_del@sentinel.dev", "HistoryPass1!")
        pred = await self._seed_prediction(client, headers)
        prediction_id = pred["prediction_id"]

        # Delete
        response = await client.delete(f"/api/v1/predictions/{prediction_id}", headers=headers)
        assert response.status_code == 204

        # Confirm it's gone
        response = await client.get(f"/api/v1/predictions/{prediction_id}", headers=headers)
        assert response.status_code == 404

    async def test_delete_nonexistent_returns_404(self, client: AsyncClient) -> None:
        """Deleting a non-existent ID should return 404."""
        headers = await get_auth_headers(client, "hist_del_nf@sentinel.dev", "HistoryPass1!")
        fake_id = "00000000-0000-0000-0000-000000000000"
        response = await client.delete(f"/api/v1/predictions/{fake_id}", headers=headers)
        assert response.status_code == 404

    async def test_delete_other_users_prediction_returns_404(self, client: AsyncClient) -> None:
        """A user cannot delete another user's prediction."""
        headers_a = await get_auth_headers(client, "hist_da@sentinel.dev", "HistDAPass1!")
        headers_b = await get_auth_headers(client, "hist_db@sentinel.dev", "HistDBPass1!")

        pred = await self._seed_prediction(client, headers_a)
        prediction_id = pred["prediction_id"]

        response = await client.delete(f"/api/v1/predictions/{prediction_id}", headers=headers_b)
        assert response.status_code == 404
