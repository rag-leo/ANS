from backend.database.models import Article
from backend.database.session import SessionLocal


class ArticleRepository:

    def save(
        self,
        article_data: dict,
    ) -> Article:

        with SessionLocal() as session:

            article = Article(
                title=article_data["title"],
                content=article_data["content"],
                url=article_data["url"],
                section=article_data["section"],
                content_length=article_data[
                    "content_length"
                ],
                published_datetime=article_data[
                    "published_datetime"
                ],
                updated_datetime=article_data[
                    "updated_datetime"
                ],
                scrape_date=article_data[
                    "scrape_date"
                ],
                crop=article_data["crop"],
                category=article_data[
                    "category"
                ],
                keywords=article_data[
                    "keywords"
                ],
                source=article_data["source"],
            )

            session.add(article)

            session.commit()

            session.refresh(article)

            return article

    def get_by_url(
        self,
        url: str,
    ):

        with SessionLocal() as session:

            return (
                session.query(Article)
                .filter(
                    Article.url == url
                )
                .first()
            )