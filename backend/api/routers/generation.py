from fastapi import APIRouter

from backend.schemas.generation import (
    ContentRequest,
    ContentResponse,
)

from backend.services.generation_service import (
    GenerationService,
)

generation_service = (
    GenerationService()
)

router = APIRouter(
    prefix="/generate",
    tags=["Generation"],
)


@router.post(
    "",
    response_model=ContentResponse,
)

def generate_content(
    request: ContentRequest,
):

    generated_response = (
        generation_service.generate(
            request
        )
    )

    return ContentResponse(
        title=generated_response["title"],
        content=generated_response["content"],
        article_count=generated_response["article_count"],
        article_ids=generated_response["article_ids"],
    )


    