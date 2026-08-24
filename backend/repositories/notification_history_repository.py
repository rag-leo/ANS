from datetime import datetime

from backend.database.session import (
    SessionLocal,
)

from backend.models.notification_history import (
    NotificationHistory,
)


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