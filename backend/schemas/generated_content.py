from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class GeneratedContentCreate(BaseModel):

    article_id: UUID

    channel: str

    language: str

    content_length: str

    generated_text: str


class GeneratedContentResponse(BaseModel):

    id: UUID

    article_id: UUID

    channel: str

    language: str

    content_length: str

    generated_text: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )