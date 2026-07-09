"""
Integration tests for analytics endpoints.

GET /api/v1/analytics/summary
GET /api/v1/analytics/timeline
GET /api/v1/analytics/confidence-distribution
"""

import pytest
from httpx import AsyncClient

from tests.conftest import get_auth_headers


@pytest.mark.asyncio
class TestAnalyticsEndpoints:
    """Tests for the analytics dashboard endpoints."""

    async def _setup(self, client: AsyncClient) -> dict[str, str]:
        """Register, login, and create a prediction so analytics has data."""
        headers = await get_auth_headers(client, "analytics@sentinel.dev", "AnalyticsPass1!")

        # Seed one prediction so summary totals are non-zero
        await client.post(
            "/api/v1/predict",
            json={"text": "Congratulations! You have won a FREE prize. Click now!", "message_type": "sms"},
            headers=headers,
        )
        return headers

    async def test_summary_unauthenticated(self, client: AsyncClient) -> None:
        """Summary endpoint must require authentication."""
        response = await client.get("/api/v1/analytics/summary")
        assert response.status_code == 401

    async def test_summary_returns_expected_shape(self, client: AsyncClient) -> None:
        """Summary should return all required keys with correct types."""
        headers = await self._setup(client)
        response = await client.get("/api/v1/analytics/summary", headers=headers)
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["total_predictions"], int)
        assert isinstance(data["spam_count"], int)
        assert isinstance(data["ham_count"], int)
        assert isinstance(data["spam_rate"], float)
        assert isinstance(data["avg_confidence"], float)
        assert isinstance(data["high_confidence_spam"], int)
        assert isinstance(data["predictions_today"], int)
        assert isinstance(data["most_common_spam_tokens"], list)

    async def test_summary_totals_are_consistent(self, client: AsyncClient) -> None:
        """spam_count + ham_count must equal total_predictions."""
        headers = await self._setup(client)
        response = await client.get("/api/v1/analytics/summary", headers=headers)
        data = response.json()

        assert data["spam_count"] + data["ham_count"] == data["total_predictions"]
        assert data["total_predictions"] >= 1  # We seeded at least one

    async def test_summary_spam_rate_bounds(self, client: AsyncClient) -> None:
        """spam_rate must be in [0.0, 1.0]."""
        headers = await self._setup(client)
        response = await client.get("/api/v1/analytics/summary", headers=headers)
        data = response.json()
        assert 0.0 <= data["spam_rate"] <= 1.0

    async def test_summary_empty_user(self, client: AsyncClient) -> None:
        """A user with no predictions should get zeros, not an error."""
        headers = await get_auth_headers(client, "empty@sentinel.dev", "EmptyUser1!")
        response = await client.get("/api/v1/analytics/summary", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total_predictions"] == 0
        assert data["spam_rate"] == 0.0

    async def test_timeline_valid_periods(self, client: AsyncClient) -> None:
        """Timeline endpoint should accept 7d, 30d, 90d."""
        headers = await self._setup(client)
        for period in ["7d", "30d", "90d"]:
            response = await client.get(
                f"/api/v1/analytics/timeline?period={period}", headers=headers
            )
            assert response.status_code == 200, f"Failed for period={period}"
            data = response.json()
            assert data["period"] == period
            assert isinstance(data["data"], list)

    async def test_timeline_invalid_period(self, client: AsyncClient) -> None:
        """Timeline endpoint should reject invalid period values."""
        headers = await self._setup(client)
        response = await client.get("/api/v1/analytics/timeline?period=5d", headers=headers)
        assert response.status_code == 422

    async def test_timeline_data_shape(self, client: AsyncClient) -> None:
        """Each timeline data point must have date, spam, ham, total."""
        headers = await self._setup(client)
        response = await client.get("/api/v1/analytics/timeline?period=30d", headers=headers)
        assert response.status_code == 200
        data = response.json()

        for point in data["data"]:
            assert "date" in point
            assert "spam" in point
            assert "ham" in point
            assert "total" in point
            assert point["spam"] + point["ham"] == point["total"]

    async def test_confidence_distribution_shape(self, client: AsyncClient) -> None:
        """Confidence distribution should return 5 buckets."""
        headers = await self._setup(client)
        response = await client.get("/api/v1/analytics/confidence-distribution", headers=headers)
        assert response.status_code == 200
        data = response.json()

        assert "buckets" in data
        assert len(data["buckets"]) == 5
        for bucket in data["buckets"]:
            assert "range" in bucket
            assert "count" in bucket
            assert isinstance(bucket["count"], int)
            assert bucket["count"] >= 0

    async def test_analytics_data_isolation(self, client: AsyncClient) -> None:
        """User A's analytics should not include User B's predictions."""
        headers_a = await get_auth_headers(client, "usera@sentinel.dev", "UserAPass1!")
        headers_b = await get_auth_headers(client, "userb@sentinel.dev", "UserBPass1!")

        # User A makes 2 predictions
        for _ in range(2):
            await client.post(
                "/api/v1/predict",
                json={"text": "Win a free gift card now, click here!", "message_type": "email"},
                headers=headers_a,
            )

        # User B makes 0 predictions — their summary must be 0
        response_b = await client.get("/api/v1/analytics/summary", headers=headers_b)
        assert response_b.json()["total_predictions"] == 0
