from datetime import datetime

from pydantic import BaseModel


class ScrapedArticle(BaseModel):

    section: str

    title: str

    url: str

    content: str

    content_length: int

    published_datetime: str | None = None

    updated_datetime: str | None = None

    scrape_date: str | None = None