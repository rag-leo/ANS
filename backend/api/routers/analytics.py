from fastapi import APIRouter

from backend.repositories.analytics_repository import (
    AnalyticsRepository,
)

router = APIRouter(
    prefix="/analytics",
    tags=["Analytics"],
)

repo = AnalyticsRepository()


@router.get("/summary")
def get_summary():

    return repo.get_summary()