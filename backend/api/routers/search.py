from fastapi import APIRouter

from backend.schemas.search import (
    SearchRequest,
    SearchResponse,
)

from backend.services.retrieval_service import (
    RetrievalService,
)

router = APIRouter(
    prefix="/search",
    tags=["Search"],
)

service = RetrievalService()


@router.post(
    "",
    response_model=list[SearchResponse],
)
def search(
    request: SearchRequest,
):

    results = service.search(
        query=request.query,
        crop=request.crop,
        category=request.category,
        source=request.source,
        generation_type=request.generation_type,
        max_age_days=request.max_age_days,
        top_k=request.top_k,
    )

    return results