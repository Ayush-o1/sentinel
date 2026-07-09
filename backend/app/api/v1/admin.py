"""
SENTINEL — Admin Router (Role: admin only)

GET /api/v1/admin/users             — List all users (paginated)
GET /api/v1/analytics/global        — Platform-wide aggregate stats
"""

import math

from fastapi import APIRouter, Query

from app.core.dependencies import AdminUser, DbSession
from app.repositories.admin_repository import AdminRepository
from app.schemas.auth import UserResponse
from app.schemas.common import PaginatedResponse

router = APIRouter()


@router.get(
    "/users",
    response_model=PaginatedResponse[UserResponse],
    summary="[Admin] List all users",
)
async def list_users(
    admin: AdminUser,
    db: DbSession,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> PaginatedResponse[UserResponse]:
    repo = AdminRepository(db)
    users, total = await repo.get_paginated_users(page=page, page_size=page_size)

    return PaginatedResponse(
        items=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=math.ceil(total / page_size) if total > 0 else 1,
    )


@router.get(
    "/analytics/global",
    summary="[Admin] Platform-wide analytics",
)
async def global_analytics(
    admin: AdminUser,
    db: DbSession,
) -> dict:
    repo = AdminRepository(db)
    return await repo.get_global_stats()
