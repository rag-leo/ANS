from backend.services.metadata_service import (
    MetadataService,
)


class IngestionService:

    @staticmethod
    def enrich_article(article):

        metadata = (
            MetadataService.extract_metadata(
                title=article.title,
                content=article.content,
            )
        )

        return {
            "article": article,
            "metadata": metadata,
        }