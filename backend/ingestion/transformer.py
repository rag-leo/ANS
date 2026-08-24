from backend.database.models import Article
from backend.ingestion.models import ScrapedArticle


class ArticleTransformer:
    """
    Converts scraped articles into
    ANIS database models.
    """

    @staticmethod
    def transform(
        scraped_article: ScrapedArticle,
        metadata: dict,
    ) -> Article:

        crop = None

        if metadata.get("crop"):
            crop = ", ".join(
                metadata["crop"]
            )

        return Article(
            title=scraped_article.title,
            content=scraped_article.content,
            source="Agrowon",
            url=scraped_article.url,
            category=metadata.get(
                "category"
            ),
            crop=crop,
        )