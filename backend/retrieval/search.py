from sklearn.metrics.pairwise import cosine_similarity

from backend.retrieval.models import SearchResult
from backend.services.embedding_service import (
    EmbeddingService,
)


class SemanticSearch:

    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )

    def search(
        self,
        query: str,
        documents: list[str],
    ) -> list:
        query_embedding = (
            self.embedding_service.generate_embedding(
                query
            )
        )


        document_embeddings = [

            self.embedding_service.generate_embedding(
                doc
            )

            for doc in documents

        ]

        scores = cosine_similarity(
            [query_embedding],
            document_embeddings,
        )[0]

        results = []

        for doc, score in zip(
            documents,
            scores,
        ):

            results.append(
                SearchResult(
                    title=doc[:60],
                    content=doc,
                    score=float(score),
                )
            )

        results = [
            result
            for result in results
            if result.score >= 0.20
        ]        

        results.sort(
            key=lambda x: x.score,
            reverse=True,
        )

        return results[:5]