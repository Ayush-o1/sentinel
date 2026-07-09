"""
SENTINEL — Base Repository

Provides generic CRUD operations shared by all repositories.

Design:
    Repositories are the ONLY place that touches the database.
    Services orchestrate business logic; repositories execute queries.
    This separation ensures services are testable without a real database.
"""

import uuid
from typing import Generic, List, Optional, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Generic async repository providing basic CRUD operations.

    Usage:
        class UserRepository(BaseRepository[User]):
            def __init__(self, db: AsyncSession):
                super().__init__(User, db)
    """

    def __init__(self, model: Type[ModelT], db: AsyncSession) -> None:
        self._model = model
        self._db = db

    async def get_by_id(self, record_id: uuid.UUID | str) -> Optional[ModelT]:
        """Fetch a single record by primary key. Returns None if not found."""
        if isinstance(record_id, str):
            record_id = uuid.UUID(record_id)
        result = await self._db.get(self._model, record_id)
        return result

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[ModelT]:
        """Fetch all records with pagination."""
        result = await self._db.execute(
            select(self._model).limit(limit).offset(offset)
        )
        return list(result.scalars().all())

    async def save(self, instance: ModelT) -> ModelT:
        """Persist a new or updated instance. Flushes to get DB-generated fields."""
        self._db.add(instance)
        await self._db.flush()
        await self._db.refresh(instance)
        return instance

    async def delete(self, instance: ModelT) -> None:
        """Delete a record from the database."""
        await self._db.delete(instance)
        await self._db.flush()
