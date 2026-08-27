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

@router.get(
    "/test-cases"
)
def get_test_cases():

    return (
        repository
        .get_test_cases()
    )


@router.get(
    "/summary"
)
def get_evaluation_summary():

    return (
        repository
        .get_evaluation_summary()
    )


@router.get(
    "/by-generation-type"
)
def get_evaluation_by_generation_type():

    return (
        repository
        .get_evaluation_by_generation_type()
    )

@router.get(
    "/by-language"
)
def get_evaluation_by_language():

    return (
        repository
        .get_evaluation_by_language()
    )

@router.get(
    "/lowest-rated"
)
def get_lowest_rated_evaluations():

    return (
        repository
        .get_lowest_rated_evaluations()
    )

