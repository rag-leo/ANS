from pydantic import BaseModel


class SearchRequest(BaseModel):

    query: str

    crop: str | None = None

    category: str | None = None

    source: str | None = None


class SearchResponse(BaseModel):

    title: str

    content: str

    score: float

    crop: list[str] | None = None

    category: str | None = None

    source: str | None = None

    url: str | None = None