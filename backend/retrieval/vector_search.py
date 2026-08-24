from typing import Any

import numpy as np


class VectorSearch:
    """
    Searches stored chunk embeddings using
    cosine similarity.
    """

    @staticmethod
    def cosine_similarity(
        vector_a: list[float],
        vector_b: list[float],
    ) -> float:
        """
        Computes cosine similarity
        between two vectors.
        """

        vector_a = np.array(vector_a)
        vector_b = np.array(vector_b)

        denominator = (
            np.linalg.norm(vector_a)
            * np.linalg.norm(vector_b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(vector_a, vector_b)
            / denominator
        )

    def search(
        self,
        query_embedding: list[float],
        articles: list[dict],
        top_k: int = 5,
        score_threshold: float = 0.20,
    ) -> list[dict[str, Any]]:
        """
        Searches chunk embeddings and
        returns the most relevant chunks.
        """

        results = []

        for article in articles:

            chunks = article.get(
                "chunks",
                []
            )

            for chunk in chunks:

                chunk_embedding = chunk.get(
                    "embedding"
                )

                if not chunk_embedding:
                    continue

                score = (
                    self.cosine_similarity(
                        query_embedding,
                        chunk_embedding,
                    )
                )

                if score < score_threshold:
                    continue

                results.append(
                    {
                        "title": article.get(
                            "title"
                        ),
                        "url": article.get(
                            "url"
                        ),
                        "crop": article.get(
                            "crop"
                        ),
                        "category": article.get(
                            "category"
                        ),
                        "source": article.get(
                            "source"
                        ),
                        "score": score,
                        "chunk_id": chunk.get(
                            "chunk_id"
                        ),
                        "content": chunk.get(
                            "content"
                        ),
                    }
                )

        results.sort(
            key=lambda result: result[
                "score"
            ],
            reverse=True,
        )

        return results[:top_k]
