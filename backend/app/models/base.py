"""
SENTINEL — SQLAlchemy Declarative Base & Common Mixins

All ORM models inherit from `Base`.
Common columns (id, created_at, updated_at) are provided by mixins
to avoid repetition across models.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, String, DateTime, text, Uuid as UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedColumn, mapped_column


class Base(DeclarativeBase):
    """Declarative base class for all SQLAlchemy models."""
    pass


class UUIDMixin:
    """
    Provides a UUID primary key column.

    Uses gen_random_uuid() at the database level (PostgreSQL built-in).
    The Python-side default (uuid4) is a fallback for testing with SQLite.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )


class TimestampMixin:
    """
    Provides created_at and updated_at timestamp columns.

    Both are timezone-aware (TIMESTAMPTZ in PostgreSQL).
    updated_at is refreshed automatically on every UPDATE via a trigger
    (set up in the initial Alembic migration).
    """
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
