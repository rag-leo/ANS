from pydantic import BaseModel


class SearchRequest(BaseModel):

    query: str

    crop: str | None = None

    category: str | None = None

    source: str | None = None

    generation_type: str | None = None

    max_age_days: int | None = None

    top_k: int = 5


class SearchResponse(BaseModel):

    article_id: int

    chunk_id: int

    title: str

    content: str

    score: float

    crop: str | None = None

    category: str | None = None

    source: str | None = None

    url: str | None = None
