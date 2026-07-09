"""
SENTINEL — Admin Router (Role: admin only)

GET /api/v1/admin/users         — List all users
GET /api/v1/admin/predictions   — List all predictions
GET /api/v1/admin/analytics/global — Platform-wide stats
"""

from fastapi import APIRouter, Query

from app.core.dependencies import AdminUser, DbSession
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
    import math
    from sqlalchemy import func, select
    from app.models.user import User

    count_result = await db.execute(select(func.count()).select_from(User))
    total = count_result.scalar() or 0

    offset = (page - 1) * page_size
    result = await db.execute(select(User).limit(page_size).offset(offset))
    users = list(result.scalars().all())

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
    from sqlalchemy import func, select
    from app.models.prediction import Prediction
    from app.models.user import User

    pred_count = await db.execute(select(func.count()).select_from(Prediction))
    user_count = await db.execute(select(func.count()).select_from(User))
    spam_count = await db.execute(
        select(func.count()).where(Prediction.verdict == "SPAM")
    )

    total_preds = pred_count.scalar() or 0
    total_users = user_count.scalar() or 0
    total_spam = spam_count.scalar() or 0

    return {
        "total_users": total_users,
        "total_predictions": total_preds,
        "total_spam": total_spam,
        "total_ham": total_preds - total_spam,
        "global_spam_rate": round(total_spam / total_preds, 4) if total_preds > 0 else 0.0,
    }
