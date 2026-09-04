from datetime import datetime

from pydantic import BaseModel


class ScrapedArticle(BaseModel):

    section: str | None = None

    title: str

    url: str

    content: str

    content_length: int

    published_datetime: datetime | None = None

    updated_datetime: datetime | None = None

    scrape_date: str | None = None