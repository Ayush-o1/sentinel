"""
SENTINEL — AuditLog ORM Model
"""

import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import JSON, DateTime, ForeignKey, String, Text
from sqlalchemy import Uuid as UUID
from sqlalchemy.dialects.postgresql import INET, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AuditLog(Base):
    """
    Immutable audit trail for security-relevant user actions.

    Records who did what, when, from where, and whether it succeeded.
    This table is append-only — records are never updated or deleted.

    Indexed for:
    - Per-user audit reviews (user_id, created_at)
    - Security incident investigation (action, created_at)

    NOTE: As of Release 2, this model is migrated but not yet populated.
    Audit log writes are planned for a future release that threads
    request context through the service layer.
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    # Nullable: events like failed login attempts may have no valid user_id
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    action: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
        comment="'LOGIN' | 'LOGOUT' | 'REGISTER' | 'PREDICT' | 'DELETE_PREDICTION' | ...",
    )
    resource_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    resource_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    ip_address: Mapped[str | None] = mapped_column(
        String(45).with_variant(INET(), "postgresql"),
        nullable=True,
        comment="Client IP (INET type for both IPv4 and IPv6)",
    )
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="'SUCCESS' | 'FAILURE'",
    )
    metadata_: Mapped[dict[str, Any] | None] = mapped_column(
        "metadata",
        JSON().with_variant(JSONB(), "postgresql"),
        nullable=True,
        comment="Additional context (error message, changed fields, etc.)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action} user_id={self.user_id} status={self.status}>"
