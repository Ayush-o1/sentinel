"""
SENTINEL — AuditLog ORM Model
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import INET, JSONB, UUID
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
    """

    __tablename__ = "audit_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()"),
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
        INET,
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
        JSONB,
        nullable=True,
        comment="Additional context (error message, changed fields, etc.)",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=text("NOW()"),
        nullable=False,
        index=True,
    )

    def __repr__(self) -> str:
        return f"<AuditLog action={self.action} user_id={self.user_id} status={self.status}>"
