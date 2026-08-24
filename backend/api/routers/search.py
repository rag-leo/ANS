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

    articles = get_articles()

    if request.crop:

        articles = [
            article
            for article in articles
            if request.crop in article.get(
                "crop",
                []
            )
        ]

    if request.category:

        articles = [
            article
            for article in articles
            if article.get(
                "category"
            ) == request.category
        ]

    if request.source:

        articles = [
            article
            for article in articles
            if article.get(
                "source"
            ) == request.source
        ]

    if not articles:

        return []

    results = service.search(
        query=request.query,
        crop=request.crop,
        category=request.category,
        source=request.source,
    )

    return results