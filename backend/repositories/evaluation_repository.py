from backend.database.session import (
    SessionLocal,
)

from backend.database.models import (
    EvaluationResult,
)


class EvaluationRepository:

    def save_evaluation(
        self,
        evaluation_data: dict,
    ):

        with SessionLocal() as session:

            evaluation = EvaluationResult(
                **evaluation_data
            )

            session.add(
                evaluation
            )

            session.commit()

            session.refresh(
                evaluation
            )

            return evaluation.id