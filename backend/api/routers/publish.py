from fastapi import APIRouter

from backend.schemas.generation import (
    PublishRequest,
)

from backend.repositories.notification_history_repository import (
    NotificationHistoryRepository,
)

router = APIRouter(
    prefix="/publish",
    tags=["Publishing"],
)

repository = (
    NotificationHistoryRepository()
)


@router.post("")
def publish_content(
    request: PublishRequest,
):

    repository.mark_published(
        article_ids=request.article_ids,
        generation_type=request.generation_type,
        language=request.language,
    )

    return {
        "status": "success",
        "message": "Content marked as published",
    }


@router.get(
    "/history"
)
def get_history():

    return repository.get_published_notifications()