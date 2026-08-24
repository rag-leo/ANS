from backend.repositories.article_chunk_repository import (
    ArticleChunkRepository,
)

from backend.services.embedding_service import (
    EmbeddingService,
)


class RetrievalService:

    def __init__(self):

        self.embedding_service = (
            EmbeddingService()
        )

        self.chunk_repository = (
            ArticleChunkRepository()
        )

    def search(
        self,
        query: str,
        crop: str | None = None,
        category: str | None = None,
        source: str | None = None,
        generation_type: str | None = None,
        max_age_days: int | None = None,
        top_k: int = 5,
    ):

        query_embedding = (
            self.embedding_service.generate_embedding(
                query
            )
        )

        return self.chunk_repository.search_similar(
            query_embedding=query_embedding,
            crop=crop,
            category=category,
            source=source,
            generation_type=generation_type,
            max_age_days=max_age_days,
            top_k=top_k,
        )