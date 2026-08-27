from backend.database.session import (
    SessionLocal,
)

from backend.database.models import (
    EvaluationResult,
)

from sqlalchemy import text

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

    def get_test_cases(
        self,
    ):

        with SessionLocal() as session:

            results = (
                session.execute(
                    text(
                        """
                        SELECT
                            id,
                            query,
                            crop,
                            category,
                            language,
                            generation_type,
                            expected_outcome
                        FROM evaluation_test_cases
                        ORDER BY id
                        """
                    )
                )
                .mappings()
                .all()
            )

            return [
                dict(row)
                for row in results
                ]    
            
    def get_evaluation_summary(
        self,
    ):

        with SessionLocal() as session:

            result = (
                session.execute(
                    text(
                        """
                        SELECT

                            ROUND(
                                AVG(
                                    retrieval_relevance
                                )::numeric,
                                2
                            ) AS avg_retrieval_relevance,

                            ROUND(
                                AVG(
                                    crop_focus
                                )::numeric,
                                2
                            ) AS avg_crop_focus,

                            ROUND(
                                AVG(
                                    faithfulness
                                )::numeric,
                                2
                            ) AS avg_faithfulness,

                            ROUND(
                                AVG(
                                    communication_quality
                                )::numeric,
                                2
                            ) AS avg_communication_quality,

                            ROUND(
                                (
                                    100.0 *
                                    AVG(
                                        CASE
                                            WHEN language_compliance
                                            THEN 1
                                            ELSE 0
                                        END
                                    )
                                )::numeric,
                                2
                            ) AS language_compliance_pct,

                            COUNT(*) AS total_evaluations

                        FROM evaluation_results
                        """
                    )
                )
                .mappings()
                .first()
            )

            return dict(result)        

    def get_evaluation_by_generation_type(
        self,
    ):

        with SessionLocal() as session:

            results = (
                session.execute(
                    text(
                        """
                        SELECT
                            generation_type,

                            ROUND(
                                AVG(
                                    retrieval_relevance
                                )::numeric,
                                2
                            ) AS retrieval_relevance,

                            ROUND(
                                AVG(
                                    crop_focus
                                )::numeric,
                                2
                            ) AS crop_focus,

                            ROUND(
                                AVG(
                                    faithfulness
                                )::numeric,
                                2
                            ) AS faithfulness,

                            ROUND(
                                AVG(
                                    communication_quality
                                )::numeric,
                                2
                            ) AS communication_quality,

                            COUNT(*) AS evaluations

                        FROM evaluation_results

                        GROUP BY generation_type

                        ORDER BY generation_type
                        """
                    )
                )
                .mappings()
                .all()
            )

            return [
                dict(row)
                for row in results
            ]

    def get_evaluation_by_language(
        self,
    ):

        with SessionLocal() as session:

            results = (
                session.execute(
                    text(
                        """
                        SELECT

                            language,

                            ROUND(
                                AVG(
                                    retrieval_relevance
                                )::numeric,
                                2
                            ) AS retrieval_relevance,

                            ROUND(
                                AVG(
                                    faithfulness
                                )::numeric,
                                2
                            ) AS faithfulness,

                            ROUND(
                                AVG(
                                    communication_quality
                                )::numeric,
                                2
                            ) AS communication_quality,

                            ROUND(
                                (
                                    100.0 *
                                    AVG(
                                        CASE
                                            WHEN language_compliance
                                            THEN 1
                                            ELSE 0
                                        END
                                    )
                                )::numeric,
                                2
                            ) AS language_compliance_pct,

                            COUNT(*) AS evaluations

                        FROM evaluation_results

                        GROUP BY language

                        ORDER BY language
                        """
                    )
                )
                .mappings()
                .all()
            )

            return [
                dict(row)
                for row in results
            ]                

    def get_lowest_rated_evaluations(
        self,
    ):

        with SessionLocal() as session:

            results = (
                session.execute(
                    text(
                        """
                        SELECT

                            id,

                            query,

                            crop,

                            language,

                            generation_type,

                            retrieval_relevance,

                            faithfulness,

                            communication_quality,

                            comments

                        FROM evaluation_results

                        ORDER BY

                            communication_quality ASC,

                            faithfulness ASC

                        LIMIT 10
                        """
                    )
                )
                .mappings()
                .all()
            )

            return [
                dict(row)
                for row in results
            ]        