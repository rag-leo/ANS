# `generated_content_repository.py`


#```python
from uuid import UUID

from sqlalchemy.orm import Session

from backend.database.models import GeneratedContent


class GeneratedContentRepository:

    @staticmethod
    def create(
        db: Session,
        content: GeneratedContent,
    ) -> GeneratedContent:

        db.add(content)
        db.commit()
        db.refresh(content)

        return content

    @staticmethod
    def get_by_id(
        db: Session,
        content_id: UUID,
    ) -> GeneratedContent | None:

        return (
            db.query(GeneratedContent)
            .filter(
                GeneratedContent.id == content_id
            )
            .first()
        )

    @staticmethod
    def get_by_article(
        db: Session,
        article_id: UUID,
    ) -> list : (
            db.query(GeneratedContent)
            .filter(
                GeneratedContent.article_id == article_id
            )
            .all()
        )

    @staticmethod
    def delete(
        db: Session,
        content: GeneratedContent,
    ) -> None:

        db.delete(content)
        db.commit()