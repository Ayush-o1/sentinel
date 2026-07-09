"""
SENTINEL — Models Package

Import all models here so that SQLAlchemy's mapper registry
can discover them when Base.metadata.create_all() or Alembic
inspects the schema.

Any model NOT imported here will be invisible to migrations.
"""

from app.models.audit_log import AuditLog
from app.models.model_version import ModelVersion
from app.models.prediction import Prediction
from app.models.refresh_token import RefreshToken
from app.models.user import User

__all__ = [
    "User",
    "Prediction",
    "RefreshToken",
    "ModelVersion",
    "AuditLog",
]
