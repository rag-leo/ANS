import json

from backend.ingestion.agrowon_scraper import (
    AgrowonScraper,
)

from backend.services.metadata_service import (
    MetadataService,
)

from backend.services.chunking_service import (
    ChunkingService,
)

from backend.services.embedding_service import (
    EmbeddingService,
)

from backend.repositories.article_repository import (
    ArticleRepository,
)

from backend.repositories.article_chunk_repository import (
    ArticleChunkRepository,
)

OUTPUT_FILE = (
    "backend/data/articles.json"
)


def load_articles():

    scraper = AgrowonScraper()

    chunking_service = (
        ChunkingService()
    )

    embedding_service = (
        EmbeddingService()
    )
    article_repository = (
        ArticleRepository()
    )

    chunk_repository = (
        ArticleChunkRepository()
    )
    scraped_articles = (
        scraper.scrape_articles()
    )


    total_chunks = 0

    inserted_articles = 0

    for article in scraped_articles:

        metadata = (
            MetadataService.extract_metadata(
                title=article.title,
                content=article.content,
            )
        )

        print(
            f"\nTITLE: {article.title}"
        )

        print(
            f"CATEGORY: {metadata['category']}"
        )

        print(
            f"CROPS: {metadata['crop']}"
        )

        print(
            f"CONFIDENCE: {metadata['confidence']}"
        )

        chunks = (
            chunking_service.chunk_text(
                article.content
            )
        )

        chunk_records = []

        for index, chunk in enumerate(
            chunks,
            start=1,
        ):

            embedding = (
                embedding_service.generate_embedding(
                    chunk
                )
            )

            chunk_records.append(
                {
                    "chunk_id": index,
                    "content": chunk,
                    "embedding": embedding,
                }
            )

        article_data = {
            "title": article.title,
            "content": article.content,
            "url": article.url,
            "section": article.section,
            "content_length": (
                article.content_length
            ),
            "published_datetime": (
                article.published_datetime
            ),
            "updated_datetime": (
                article.updated_datetime
            ),
            "scrape_date": (
                article.scrape_date
            ),
            "crop": ",".join(
                metadata.get("crop", [])
            ),
            "category": (
                metadata.get(
                    "category"
                )
            ),
            "keywords": ",".join(
                metadata.get(
                    "keywords",
                    []
                )
            ),
            "source": "Agrowon",
        }

        existing_article = (
            article_repository.get_by_url(
                article.url
            )
        )

        if existing_article:

            print(
                f"Skipped: "
                f"{article.title}"
            )

            continue

        saved_article = (
            article_repository.save(
                article_data
            )
        )

        chunk_repository.save_chunks(
            article_id=saved_article.id,
            chunks=chunk_records,
        )

        total_chunks += len(
            chunk_records
        )

        inserted_articles += 1

        print(
            f"Saved: {article.title}"
            f" | Chunks={len(chunk_records)}"
        )

    print(
        f"\nInserted "
        f"{inserted_articles} articles"
    )

    print(
        f"Generated "
        f"{total_chunks} chunks"
    )


if __name__ == "__main__":

    load_articles()