from fastapi import APIRouter


from backend.schemas.generation import (
    PublishRequest,
)

from backend.repositories.notification_history_repository import (
    NotificationHistoryRepository,
)

router = APIRouter(
    prefix="/publish",
    tags=["Publish"],
)

@router.post(
    "/publish"
)
def mark_published(
    request: PublishRequest,
):

    repository = (
        NotificationHistoryRepository()
    )

    repository.mark_published(
        article_ids=request.article_ids,
        generation_type=request.generation_type,
        language=request.language,
    )

    return {
        "message":
        "Published successfully"
    }