"""
SENTINEL — API v1 Aggregate Router

Collects all v1 sub-routers into a single router mounted at /api/v1
"""

from fastapi import APIRouter

from app.api.v1 import admin, analytics, auth, history, model, predict

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(predict.router, prefix="/predict", tags=["Prediction"])
api_router.include_router(history.router, prefix="/predictions", tags=["History"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(model.router, prefix="/model", tags=["Model"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
