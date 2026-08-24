from pydantic import BaseModel
from pydantic import ConfigDict


class EmbeddingRequest(BaseModel):

    text: str


class EmbeddingResponse(BaseModel):

    embedding: list[float]

    dimensions: int

    model_config = ConfigDict(
        from_attributes=True
    )