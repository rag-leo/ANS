from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)

from sqlalchemy.sql import func

from backend.database.base import Base


class NotificationHistory(Base):

    __tablename__ = (
        "notification_history"
    )

    id = Column(
        Integer,
        primary_key=True,
    )

    article_id = Column(
        Integer,
        ForeignKey(
            "articles.id"
        ),
        nullable=False,
    )

    generation_type = Column(
        String,
        nullable=False,
    )

    language = Column(
        String,
        nullable=True,
    )

    generated_at = Column(
        DateTime,
        server_default=func.now(),
    )

    published_at = Column(
        DateTime,
        nullable=True,
    )

    is_published = Column(
        Boolean,
        default=False,
    )