from backend.ingestion.models import ScrapedArticle
from backend.repositories.article_repository import ArticleRepository


class ArticleService:

    def __init__(self) -> None:

        self.article_repository = ArticleRepository()

    def article_exists(
        self,
        url: str,
    ) -> bool:

        return self.article_repository.get_by_url(url) is not None

    @staticmethod
    def is_duplicate_url(
        existing_urls: set[str],
        article: ScrapedArticle,
    ) -> bool:

        return article.url in existing_urls
