"""
SENTINEL — User Repository
"""

import uuid
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access layer for the users table."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(User, db)

    async def get_by_email(self, email: str) -> Optional[User]:
        """
        Find a user by email address.

        Used during login and registration uniqueness check.
        Email lookup is case-insensitive via the lower() index in PostgreSQL.
        """
        result = await self._db.execute(
            select(User).where(User.email == email.lower().strip())
        )
        return result.scalar_one_or_none()

    async def get_by_id(self, user_id: uuid.UUID | str) -> Optional[User]:
        """Fetch user by UUID. Overrides base to accept string UUIDs."""
        if isinstance(user_id, str):
            user_id = uuid.UUID(user_id)
        return await self._db.get(User, user_id)

    async def email_exists(self, email: str) -> bool:
        """Check if an email is already registered."""
        result = await self._db.execute(
            select(func.count()).where(User.email == email.lower().strip())
        )
        return (result.scalar() or 0) > 0

    async def get_prediction_count(self, user_id: uuid.UUID) -> int:
        """Return the total number of predictions for a user."""
        from app.models.prediction import Prediction
        result = await self._db.execute(
            select(func.count()).where(Prediction.user_id == user_id)
        )
        return result.scalar() or 0
