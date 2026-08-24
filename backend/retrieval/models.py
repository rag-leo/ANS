from pydantic import BaseModel


class SearchResult(BaseModel):

    title: str

    content: str

    score: float