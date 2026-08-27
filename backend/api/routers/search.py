from fastapi import APIRouter

from backend.data.article_catalog import (
    get_articles,
)

from backend.schemas.search import (
    SearchRequest,
)

from backend.services.retrieval_service import (
    RetrievalService,
)

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

service = RetrievalService()


@router.post("")
def search(
    request: SearchRequest,
):

    results = service.search(
        query=request.query,
        crop=request.crop,
        category=request.category,
        source=request.source,
    )

    return results