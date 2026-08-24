from backend.ingestion.models import (
    ScrapedArticle,
)

from backend.ingestion.transformer import (
    ArticleTransformer,
)

from backend.services.metadata_service import (
    MetadataService,
)


def test_flow():

    article = ScrapedArticle(
        section="market-intelligence",
        title="केळी दरात वाढ",
        url="https://example.com",
        content="केळीचे दर वाढले आहेत",
        content_length=100,
    )

    metadata = (
        MetadataService.extract_metadata(
            article.title,
            article.content,
        )
    )

    transformed = (
        ArticleTransformer.transform(
            article,
            metadata,
        )
    )

    print(
        f"Title: {transformed.title}"
    )

    print(
        f"Crop: {transformed.crop}"
    )

    print(
        f"Source: {transformed.source}"
    )

    print(
        "✅ Full ingestion flow passed"
    )


if __name__ == "__main__":
    test_flow()