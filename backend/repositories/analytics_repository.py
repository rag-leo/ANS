from sqlalchemy import text

from backend.database.session import (
    SessionLocal,
)


class AnalyticsRepository:

    def get_summary(self):

        with SessionLocal() as session:

            total_articles = (
                session.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM articles
                        """
                    )
                )
                .scalar()
            )

            total_chunks = (
                session.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM article_chunks
                        """
                    )
                )
                .scalar()
            )

            published_notifications = (
                session.execute(
                    text(
                        """
                        SELECT COUNT(*)
                        FROM notification_history
                        WHERE is_published = TRUE
                       """
                    )
                )
                .scalar()
            )

            generation_counts = session.execute(
                text(
                    """
                        SELECT
                        generation_type,
                        COUNT(*) AS count
                        FROM notification_history
                        WHERE is_published = TRUE
                        GROUP BY generation_type
                        ORDER BY count DESC
                  """
                )
            ).mappings().all()
            

            top_crops = session.execute(
                text(
                    """
                    SELECT
                        a.crop,
                        COUNT(*) count
                    FROM notification_history nh
                    JOIN articles a
                        ON nh.article_id = a.id
                    WHERE nh.is_published = TRUE
                    GROUP BY a.crop
                    ORDER BY count DESC
                    LIMIT 5
                    """
                )
            ).mappings().all()

            top_sources = session.execute(
                text(
                    """
                    SELECT
                        a.source,
                        COUNT(*) count
                    FROM notification_history nh
                    JOIN articles a
                        ON nh.article_id = a.id
                    WHERE nh.is_published = TRUE
                    GROUP BY a.source
                    ORDER BY count DESC
                    LIMIT 5
                    """
                )
            ).mappings().all()

            language_counts = (
                session.execute(
                  text(
                        """
                     SELECT
                        language,
                        COUNT(*) AS count
                        FROM notification_history
                        WHERE is_published = TRUE
                        GROUP BY language
                        ORDER BY count DESC
                    """
                    )
                )
                .mappings()
                .all()
            )

            publication_trend = (
                session.execute(
                    text(
                        """
                        SELECT
                           DATE(published_at) AS publish_date,
                            COUNT(*) AS count
                        FROM notification_history
                        WHERE is_published = TRUE
                        GROUP BY DATE(published_at)
                        ORDER BY publish_date
                        """
                        )
                )
                .mappings()
                .all()
            )            

            return {
                "total_articles":
                    total_articles,

                "total_chunks":
                    total_chunks,

                "published_notifications":
                    published_notifications,

                "generation_counts":
                generation_counts, 

                "top_crops":
                top_crops,

                "top_sources":
                top_sources,

                "language_counts":
                language_counts,

                "publication_trend":
                publication_trend,
                  
            }

