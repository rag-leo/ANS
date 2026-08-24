from fastapi import APIRouter

from backend.schemas.embedding import (
    EmbeddingRequest,
    EmbeddingResponse,
)

from backend.services.embedding_service import (
    EmbeddingService,
)

router = APIRouter(
    prefix="/embed",
    tags=["Embeddings"],
)

service = EmbeddingService()


@router.post(
    "",
    response_model=EmbeddingResponse,
)
def generate_embedding(
    request: EmbeddingRequest,
):

    embedding = service.generate_embedding(
        request.text
    )

    return EmbeddingResponse(
        embedding=embedding,
        dimensions=len(embedding),
    )
