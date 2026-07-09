"""
SENTINEL — Prediction Repository
"""

import uuid

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.prediction import Prediction
from app.repositories.base import BaseRepository


class PredictionRepository(BaseRepository[Prediction]):
    """Data access layer for the predictions table."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(Prediction, db)

    async def get_by_id_for_user(
        self, prediction_id: uuid.UUID, user_id: uuid.UUID
    ) -> Prediction | None:
        """
        Fetch a prediction ensuring it belongs to the given user.

        This prevents horizontal privilege escalation — a user cannot
        access another user's predictions by guessing IDs.
        """
        result = await self._db.execute(
            select(Prediction).where(
                Prediction.id == prediction_id,
                Prediction.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def get_paginated_for_user(
        self,
        user_id: uuid.UUID,
        page: int = 1,
        page_size: int = 20,
        verdict_filter: str | None = None,
        message_type_filter: str | None = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> tuple[list[Prediction], int]:
        """
        Fetch paginated predictions for a user with optional filters.

        Returns:
            A tuple of (list of Prediction objects, total count).
        """
        base_query = select(Prediction).where(Prediction.user_id == user_id)

        if verdict_filter:
            base_query = base_query.where(Prediction.verdict == verdict_filter.upper())

        if message_type_filter:
            base_query = base_query.where(Prediction.message_type == message_type_filter)

        # Count total matching records
        count_result = await self._db.execute(
            select(func.count()).select_from(base_query.subquery())
        )
        total = count_result.scalar() or 0

        # Apply sorting
        sort_col = getattr(Prediction, sort_by, Prediction.created_at)
        if sort_order == "desc":
            base_query = base_query.order_by(desc(sort_col))
        else:
            base_query = base_query.order_by(sort_col)

        # Apply pagination
        offset = (page - 1) * page_size
        base_query = base_query.limit(page_size).offset(offset)

        result = await self._db.execute(base_query)
        return list(result.scalars().all()), total
