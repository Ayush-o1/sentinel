"""
SENTINEL — Analytics Repository

Executes aggregate SQL queries for the analytics dashboard.
All queries are scoped to a specific user_id for data isolation.
"""

import uuid
from datetime import date, datetime, timedelta, timezone
from typing import Any, Dict, List

from sqlalchemy import cast, func, select, text, Integer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import JSONB

from app.models.prediction import Prediction


class AnalyticsRepository:
    """Aggregate query layer for analytics endpoints."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_summary(self, user_id: uuid.UUID) -> Dict[str, Any]:
        """Return aggregate statistics for a user's predictions."""
        today = date.today()

        result = await self._db.execute(
            select(
                func.count().label("total"),
                func.sum(
                    cast(Prediction.verdict == "SPAM", Integer)
                ).label("spam_count"),
                func.avg(Prediction.confidence).label("avg_confidence"),
            ).where(Prediction.user_id == user_id)
        )
        row = result.one()

        # High confidence spam (confidence >= 0.90)
        hc_result = await self._db.execute(
            select(func.count()).where(
                Prediction.user_id == user_id,
                Prediction.verdict == "SPAM",
                Prediction.confidence >= 0.90,
            )
        )
        high_conf_spam = hc_result.scalar() or 0

        # Today's predictions
        today_result = await self._db.execute(
            select(func.count()).where(
                Prediction.user_id == user_id,
                func.date(Prediction.created_at) == today,
            )
        )
        today_count = today_result.scalar() or 0

        total = row.total or 0
        spam_count = row.spam_count or 0
        ham_count = total - spam_count

        return {
            "total_predictions": total,
            "spam_count": spam_count,
            "ham_count": ham_count,
            "spam_rate": round(spam_count / total, 4) if total > 0 else 0.0,
            "avg_confidence": round(float(row.avg_confidence or 0), 4),
            "high_confidence_spam": high_conf_spam,
            "predictions_today": today_count,
        }

    async def get_timeline(
        self, user_id: uuid.UUID, days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        Return daily prediction counts (spam/ham) for the past N days.

        Uses PostgreSQL's date_trunc for grouping by calendar day.
        """
        since = datetime.now(timezone.utc) - timedelta(days=days)

        result = await self._db.execute(
            select(
                func.date(Prediction.created_at).label("date"),
                func.sum(
                    cast(Prediction.verdict == "SPAM", Integer)
                ).label("spam"),
                func.sum(
                    cast(Prediction.verdict == "HAM", Integer)
                ).label("ham"),
                func.count().label("total"),
            )
            .where(Prediction.user_id == user_id, Prediction.created_at >= since)
            .group_by(func.date(Prediction.created_at))
            .order_by(func.date(Prediction.created_at))
        )

        return [
            {
                "date": str(row.date),
                "spam": int(row.spam or 0),
                "ham": int(row.ham or 0),
                "total": int(row.total or 0),
            }
            for row in result.all()
        ]
