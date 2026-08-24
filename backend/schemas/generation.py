from pydantic import BaseModel

from enum import Enum

class GenerationType(
    str,
    Enum,
):

    PUSH = "push"

    WHATSAPP = "whatsapp"

    NEWSLETTER = "newsletter"

class ContentRequest(
    BaseModel
):

    query: str

    crop: str | None = None

    category: str | None = None

    source: str | None = None

    language: str

    generation_type: GenerationType




class ContentResponse(BaseModel):

    title: str

    content: str

    article_count: int

    article_ids: list[int]


class PublishRequest(
    BaseModel
):

    article_ids: list[int]

    generation_type: str

    language: str