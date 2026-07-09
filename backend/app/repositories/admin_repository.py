"""
SENTINEL — Admin Repository

Data access layer for admin-only aggregate queries.
Keeps admin.py router thin and the DB logic testable.
"""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction
from app.models.user import User
from app.repositories.base import BaseRepository


class AdminRepository(BaseRepository[User]):
    """Admin-scoped queries across all users and predictions."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_paginated_users(
        self, page: int = 1, page_size: int = 20
    ) -> tuple[list[User], int]:
        """Return a paginated list of all users with total count."""
        count_result = await self._db.execute(
            select(func.count()).select_from(User)
        )
        total = count_result.scalar() or 0

        offset = (page - 1) * page_size
        result = await self._db.execute(
            select(User).order_by(User.created_at.desc()).limit(page_size).offset(offset)
        )
        return list(result.scalars().all()), total

    async def get_global_stats(self) -> dict[str, Any]:
        """Return platform-wide aggregate statistics."""
        result = await self._db.execute(
            select(
                func.count(User.id).label("total_users"),
                func.count(Prediction.id).label("total_predictions"),
                func.sum(
                    func.cast(Prediction.verdict == "SPAM", func.Integer())
                ).label("total_spam"),
            ).select_from(User).outerjoin(Prediction, Prediction.user_id == User.id)
        )
        row = result.one()

        total_preds = row.total_predictions or 0
        total_spam = row.total_spam or 0
        total_users = row.total_users or 0

        return {
            "total_users": total_users,
            "total_predictions": total_preds,
            "total_spam": total_spam,
            "total_ham": total_preds - total_spam,
            "global_spam_rate": round(total_spam / total_preds, 4) if total_preds > 0 else 0.0,
        }
