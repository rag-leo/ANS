from fastapi import APIRouter

from backend.repositories.evaluation_repository import (
    EvaluationRepository,
)

from backend.schemas.evaluation import (
    EvaluationRequest,
)

router = APIRouter(
    prefix="/evaluation",
    tags=["Evaluation"],
)

repository = (
    EvaluationRepository()
)


@router.post("/submit")
def submit_evaluation(
    request: EvaluationRequest,
):

    evaluation_id = (
        repository.save_evaluation(
            request.model_dump()
        )
    )

    return {
        "status": "success",
        "evaluation_id":
            evaluation_id,
    }