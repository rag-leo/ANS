from backend.database.models import Article
from backend.database.models import GeneratedContent

from backend.repositories.article_repository import (
    ArticleRepository,
)

from backend.repositories.generated_content_repository import (
    GeneratedContentRepository,
)

from backend.services.article_service import (
    ArticleService,
)

from backend.services.embedding_service import (
    EmbeddingService,
)

from backend.services.retrieval_service import (
    RetrievalService,
)

from backend.services.generation_service import (
    GenerationService,
)

from backend.services.metadata_service import (
    MetadataService,
)


def test_imports():

    assert Article is not None
    assert GeneratedContent is not None

    assert ArticleRepository is not None
    assert GeneratedContentRepository is not None

    assert ArticleService is not None

    assert EmbeddingService is not None
    assert RetrievalService is not None
    assert GenerationService is not None
    assert MetadataService is not None

    print("✅ ANIS architecture validation passed")


if __name__ == "__main__":
    test_imports()