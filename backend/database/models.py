# backend/database/models.py

import uuid
from datetime import datetime, date

from pgvector.sqlalchemy import Vector
from sqlalchemy import Date
from sqlalchemy import DateTime
from sqlalchemy import ForeignKey
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

from backend.database.base import Base

from sqlalchemy import Column, Integer, BigInteger


class Article(Base):
    """
    Knowledge Base Articles

    Stores:
    - Raw article content
    - Metadata
    - Source information
    """

    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    title: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True,
    )

    section: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    content_length: Mapped[int | None] = mapped_column(
        nullable=True,
    )

    published_datetime: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    updated_datetime: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    scrape_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    crop: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    keywords: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    source: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    generated_content = relationship(
        "GeneratedContent",
        back_populates="article",
        cascade="all, delete-orphan",
    )

    chunks = relationship(
        "ArticleChunk",
        back_populates="article",
        cascade="all, delete-orphan",
    )


class GeneratedContent(Base):
    """
    AI generated communication content.

    Supports:
    - WhatsApp
    - Push Notification
    - Bulletin

    Languages:
    - English
    - Hindi
    - Marathi
    """

    __tablename__ = "generated_content"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
    )

    channel: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    language: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    content_length: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    generated_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    article = relationship(
        "Article",
        back_populates="generated_content",
    )

class ArticleChunk(Base):

    __tablename__ = "article_chunks"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("articles.id"),
        nullable=False,
    )

    chunk_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    embedding: Mapped[list[float]] = mapped_column(
        Vector(1536),
        nullable=False,
    )

    article = relationship(
        "Article",
        back_populates="chunks",
    )

from sqlalchemy import (
    Boolean,
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    func,
)

from backend.database.base import Base


class EvaluationResult(Base):

    __tablename__ = "evaluation_results"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    query = Column(Text)

    crop = Column(String(255))

    category = Column(String(255))

    language = Column(String(50))

    generation_type = Column(String(50))

    retrieval_relevance = Column(Integer)

    crop_focus = Column(Integer)

    faithfulness = Column(Integer)

    communication_quality = Column(Integer)

    language_compliance = Column(Boolean)

    comments = Column(Text)

    evaluated_at = Column(
        TIMESTAMP,
        server_default=func.now(),
    )    