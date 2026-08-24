from sqlalchemy.orm import Session

from backend.database.models import Article
from backend.repositories.article_repository import ArticleRepository


class ArticleService:

    @staticmethod
    def article_exists(
        db: Session,
        url: str,
    ) -> bool:

        article = ArticleRepository.get_by_url(
            db=db,
            url=url,
        )

        return article is not None

    @staticmethod
    def create_article(
        db: Session,
        article: Article,
    ) -> Article:

        if ArticleService.article_exists(
            db=db,
            url=article.url,
        ):
            raise ValueError(
                f"Article already exists: {article.url}"
            )

        return ArticleRepository.create(
            db=db,
            article=article,
        )

    @staticmethod
    def get_article(
        db: Session,
        article_id,
    ):

        return ArticleRepository.get_by_id(
            db=db,
            article_id=article_id,
        )
    

from backend.ingestion.models import ScrapedArticle


class ArticleService:

    ...

    @staticmethod
    def is_duplicate_url(
        existing_urls: set[str],
        article: ScrapedArticle,
    ) -> bool:

        return article.url in existing_urls