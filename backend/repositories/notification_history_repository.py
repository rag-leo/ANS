from datetime import datetime

from backend.database.session import (
    SessionLocal,
)

from backend.models.notification_history import (
    NotificationHistory,
)

from backend.models.notification_history import (
    NotificationHistory,
)

from backend.database.models import Article

class NotificationHistoryRepository:

    def mark_published(
        self,
        article_ids: list[int],
        generation_type: str,
        language: str,
    ):

        with SessionLocal() as session:

            for article_id in article_ids:

                record = (
                    NotificationHistory(
                        article_id=article_id,
                        generation_type=generation_type,
                        language=language,
                        is_published=True,
                        published_at=datetime.utcnow(),
                    )
                )

                session.add(record)

            session.commit()


    def get_published_notifications(
        self,
    ):

        with SessionLocal() as session:

            records = (
                session.query(
                    NotificationHistory,
                    Article,
                )
                .join(
                    Article,
                    NotificationHistory.article_id
                    == Article.id,
                )
                .order_by(
                    NotificationHistory
                    .published_at
                    .desc()
                )
                .all()
            )

            return [
                {
                    "id":
                        history.id,

                    "article_id":
                        history.article_id,

                    "title":
                        article.title,

                    "crop":
                        article.crop,

                    "source":
                        article.source,

                    "generation_type":
                        history.generation_type,

                    "language":
                        history.language,

                    "published_at":
                        history.published_at,
                }
                for history, article
                in records
            ]