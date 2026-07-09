"""
SENTINEL — Analytics Router

GET /api/v1/analytics/summary                 — Aggregate stats
GET /api/v1/analytics/timeline                — Timeline data
GET /api/v1/analytics/confidence-distribution — Histogram data
"""

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.repositories.analytics_repository import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsSummary,
    ConfidenceBucket,
    ConfidenceDistributionResponse,
    TimelineDataPoint,
    TimelineResponse,
)

router = APIRouter()


@router.get(
    "/summary",
    response_model=AnalyticsSummary,
    summary="Get aggregate prediction statistics",
)
async def get_summary(current_user: CurrentUser, db: DbSession) -> AnalyticsSummary:
    repo = AnalyticsRepository(db)

    # Single DB round-trip for all aggregate stats (see analytics_repository)
    data = await repo.get_summary(current_user.id)

    # Top spam tokens — Python-side from last 100 SPAM predictions
    top_tokens = await repo.get_top_spam_tokens(current_user.id, limit=5)

    return AnalyticsSummary(
        **data,
        most_common_spam_tokens=top_tokens,
    )


@router.get(
    "/timeline",
    response_model=TimelineResponse,
    summary="Get prediction timeline data for charts",
)
async def get_timeline(
    current_user: CurrentUser,
    db: DbSession,
    period: str = Query(default="30d", pattern="^(7d|30d|90d)$"),
) -> TimelineResponse:
    days_map = {"7d": 7, "30d": 30, "90d": 90}
    days = days_map[period]

    repo = AnalyticsRepository(db)
    data = await repo.get_timeline(current_user.id, days=days)

    return TimelineResponse(
        period=period,
        data=[TimelineDataPoint(**point) for point in data],
    )


@router.get(
    "/confidence-distribution",
    response_model=ConfidenceDistributionResponse,
    summary="Get confidence score distribution for histogram",
)
async def get_confidence_distribution(
    current_user: CurrentUser,
    db: DbSession,
) -> ConfidenceDistributionResponse:
    # DB-side aggregation — no Python-level row loading (see analytics_repository)
    repo = AnalyticsRepository(db)
    buckets_data = await repo.get_confidence_distribution(current_user.id)

    return ConfidenceDistributionResponse(
        buckets=[ConfidenceBucket(**b) for b in buckets_data]
    )
