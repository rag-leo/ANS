from datetime import date
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel
from pydantic import ConfigDict


class ArticleCreate(BaseModel):

    title: str
    content: str

    source: str
    url: str

    category: str | None = None
    crop: str | None = None

    published_date: date | None = None


class ArticleResponse(BaseModel):

    id: UUID

    title: str
    content: str

    source: str
    url: str

    category: str | None
    crop: str | None

    published_date: date | None

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )