from backend.ingestion.models import (
    ScrapedArticle,
)

from backend.ingestion.transformer import (
    ArticleTransformer,
)


def test_transformer():

    article = ScrapedArticle(
        section="market-intelligence",
        title="केळी दरात वाढ",
        url="https://example.com",
        content="केळीच्या दरात वाढ झाली आहे",
        content_length=100,
    )

    metadata = {
        "crop": ["केळी"],
        "category": "Market News",
    }

    transformed = (
        ArticleTransformer.transform(
            article,
            metadata,
        )
    )

    print(
        transformed.title
    )

    print(
        transformed.crop
    )

    assert (
        transformed.source
        == "Agrowon"
    )

    print(
        "✅ Transformer validation passed"
    )


if __name__ == "__main__":
    test_transformer()