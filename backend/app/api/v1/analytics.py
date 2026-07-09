"""
SENTINEL — Analytics Router

GET /api/v1/analytics/summary                 — Aggregate stats
GET /api/v1/analytics/timeline                — Timeline data
GET /api/v1/analytics/confidence-distribution — Histogram data
"""

from fastapi import APIRouter, Query

from app.core.dependencies import CurrentUser, DbSession
from app.repositories.analytics_repository import AnalyticsRepository
from app.repositories.prediction_repository import PredictionRepository
from app.schemas.analytics import (
    AnalyticsSummary,
    ConfidenceBucket,
    ConfidenceDistributionResponse,
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
    data = await repo.get_summary(current_user.id)

    # Get most common spam tokens from recent predictions
    # (simplified: from prediction JSONB suspicious_tokens — aggregation done in Python for MVP)
    from sqlalchemy import select
    from app.models.prediction import Prediction

    spam_preds_result = await db.execute(
        select(Prediction.suspicious_tokens)
        .where(Prediction.user_id == current_user.id, Prediction.verdict == "SPAM")
        .limit(100)
    )
    token_counts: dict = {}
    for (tokens,) in spam_preds_result.all():
        for t in (tokens or []):
            token = t.get("token", "")
            if token:
                token_counts[token] = token_counts.get(token, 0) + 1

    top_tokens = sorted(token_counts, key=token_counts.get, reverse=True)[:5]  # type: ignore

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

    from app.schemas.analytics import TimelineDataPoint
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
    from sqlalchemy import select, func
    from app.models.prediction import Prediction

    result = await db.execute(
        select(Prediction.confidence).where(Prediction.user_id == current_user.id)
    )
    confidences = [float(row[0]) for row in result.all()]

    # Build buckets manually for clarity and control
    buckets_def = [
        ("0.5–0.6", 0.5, 0.6),
        ("0.6–0.7", 0.6, 0.7),
        ("0.7–0.8", 0.7, 0.8),
        ("0.8–0.9", 0.8, 0.9),
        ("0.9–1.0", 0.9, 1.01),
    ]
    buckets = [
        ConfidenceBucket(
            range=label,
            count=sum(1 for c in confidences if low <= c < high),
        )
        for label, low, high in buckets_def
    ]

    return ConfidenceDistributionResponse(buckets=buckets)
