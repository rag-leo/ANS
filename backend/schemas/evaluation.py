from pydantic import BaseModel


class EvaluationRequest(BaseModel):

    query: str | None = None

    crop: str | None = None

    category: str | None = None

    language: str

    generation_type: str

    retrieval_relevance: int

    crop_focus: int

    faithfulness: int

    communication_quality: int

    language_compliance: bool

    comments: str | None = None
