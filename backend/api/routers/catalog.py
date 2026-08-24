from fastapi import APIRouter

from backend.data.article_catalog import (
    get_articles,
)

router = APIRouter(
    prefix="/catalog",
    tags=["Catalog"],
)


@router.get("")
def catalog_status():

    articles = get_articles()

    return {
        "article_count": len(
            articles
        ),
        "sample_titles": [
            article["title"]
            for article in articles[:5]
        ],
    }