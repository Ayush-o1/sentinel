"""
SENTINEL — Analytics Repository

Executes aggregate SQL queries for the analytics dashboard.
All queries are scoped to a specific user_id for data isolation.

Performance notes:
    - get_summary() executes a SINGLE round-trip using conditional aggregation
      (FILTER clauses on a single SELECT), replacing the previous 3 sequential
      queries. This cuts analytics page load latency by ~2 DB round-trips.
    - get_confidence_distribution() uses DB-side CASE/WHEN bucketing, avoiding
      loading all confidence values into Python memory.
"""

import uuid
from datetime import UTC, date, datetime, timedelta
from typing import Any

from sqlalchemy import Integer, case, cast, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction


class AnalyticsRepository:
    """Aggregate query layer for analytics endpoints."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_summary(self, user_id: uuid.UUID) -> dict[str, Any]:
        """
        Return aggregate statistics for a user's predictions.

        Uses a SINGLE query with conditional aggregation (FILTER / CASE) to
        compute total, spam, high-confidence spam, and today's count in one
        DB round-trip instead of three.
        """
        today = date.today()

        result = await self._db.execute(
            select(
                func.count().label("total"),
                func.sum(
                    cast(Prediction.verdict == "SPAM", Integer)
                ).label("spam_count"),
                func.avg(Prediction.confidence).label("avg_confidence"),
                func.sum(
                    cast(
                        (Prediction.verdict == "SPAM") & (Prediction.confidence >= 0.90),
                        Integer,
                    )
                ).label("high_conf_spam"),
                func.sum(
                    cast(func.date(Prediction.created_at) == today, Integer)
                ).label("today_count"),
            ).where(Prediction.user_id == user_id)
        )
        row = result.one()

        total = row.total or 0
        spam_count = row.spam_count or 0
        ham_count = total - spam_count

        return {
            "total_predictions": total,
            "spam_count": spam_count,
            "ham_count": ham_count,
            "spam_rate": round(spam_count / total, 4) if total > 0 else 0.0,
            "avg_confidence": round(float(row.avg_confidence or 0), 4),
            "high_confidence_spam": row.high_conf_spam or 0,
            "predictions_today": row.today_count or 0,
        }

    async def get_timeline(
        self, user_id: uuid.UUID, days: int = 30
    ) -> list[dict[str, Any]]:
        """
        Return daily prediction counts (spam/ham) for the past N days.

        Uses PostgreSQL's date_trunc for grouping by calendar day.
        """
        since = datetime.now(UTC) - timedelta(days=days)

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

    async def get_top_spam_tokens(
        self, user_id: uuid.UUID, limit: int = 5
    ) -> list[str]:
        """
        Return the most frequent tokens from SPAM predictions' suspicious_tokens JSONB.

        Aggregation is done in Python over the last 100 SPAM predictions.
        Moving this to pure SQL would require unnesting JSONB arrays, which
        is not portable across SQLite (tests) and PostgreSQL (production).
        """
        result = await self._db.execute(
            select(Prediction.suspicious_tokens)
            .where(Prediction.user_id == user_id, Prediction.verdict == "SPAM")
            .limit(100)
        )
        token_counts: dict[str, int] = {}
        for (tokens,) in result.all():
            for t in (tokens or []):
                token = t.get("token", "")
                if token:
                    token_counts[token] = token_counts.get(token, 0) + 1

        return sorted(token_counts, key=token_counts.get, reverse=True)[:limit]  # type: ignore[arg-type]

    async def get_confidence_distribution(
        self, user_id: uuid.UUID
    ) -> list[dict[str, Any]]:
        """
        Return a histogram of confidence scores bucketed into 5 ranges.

        Uses DB-side CASE/WHEN aggregation to avoid loading all confidence
        rows into Python memory — O(1) memory instead of O(n).
        """
        buckets_def = [
            ("0.5–0.6", 0.5, 0.6),
            ("0.6–0.7", 0.6, 0.7),
            ("0.7–0.8", 0.7, 0.8),
            ("0.8–0.9", 0.8, 0.9),
            ("0.9–1.0", 0.9, 1.01),
        ]

        result = await self._db.execute(
            select(
                *[
                    func.sum(
                        case(
                            (
                                (Prediction.confidence >= low)
                                & (Prediction.confidence < high),
                                1,
                            ),
                            else_=0,
                        )
                    ).label(label.replace("–", "_").replace(".", "p"))
                    for label, low, high in buckets_def
                ]
            ).where(Prediction.user_id == user_id)
        )

        row = result.one()
        return [
            {
                "range": label,
                "count": int(getattr(row, label.replace("–", "_").replace(".", "p")) or 0),
            }
            for label, _, _ in buckets_def
        ]
