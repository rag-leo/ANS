# backend/data/pipeline.py

import argparse

from backend.config.logging_config import get_logger
from backend.ingestion.adapters.base import ScraperAdapter
from backend.ingestion.adapters.registry import load_all_adapters
from backend.ingestion.models import ScrapedArticle
from backend.repositories.article_chunk_repository import (
    ArticleChunkRepository,
)
from backend.repositories.article_repository import ArticleRepository
from backend.services.chunking_service import ChunkingService
from backend.services.embedding_service import EmbeddingService
from backend.services.llm_metadata_service import LLMMetadataService

logger = get_logger(__name__)


def _process_article(
    article: ScrapedArticle,
    source_label: str,
    chunking_service: ChunkingService,
    metadata_service: LLMMetadataService,
    embedding_service: EmbeddingService,
    article_repository: ArticleRepository,
    chunk_repository: ArticleChunkRepository,
    dry_run: bool = False,
) -> int | None:
    """
    Runs one scraped article through dedup, chunking, metadata
    classification, embedding, and (unless dry_run) save.

    Returns the number of chunks that were (or, in dry_run, would be)
    saved, or None if the article was skipped because its URL already
    exists.

    Dedup runs first, before chunking/classification/embedding: those
    steps have a real cost now that classification is an LLM call, so
    there's no reason to pay it for an article that's getting skipped
    anyway. This holds in dry_run too — a dry run still calls the real
    classification and embedding APIs (see run_pipeline's docstring),
    it just skips the database writes at the end, so skipping early
    for duplicates still matters for cost.
    """

    print(f"\nTITLE: {article.title}")
    print(f"SOURCE: {source_label}")

    existing_article = article_repository.get_by_url(article.url)

    if existing_article:
        print(f"Skipped (duplicate): {article.title}")
        return None

    chunks = chunking_service.chunk_text(article.content)

    # Classify from title + first chunk rather than the full article —
    # see Stage 9: crop/category is reliably established early in a
    # news article, and this reuses a boundary the pipeline already
    # computes instead of a separate truncation scheme.
    excerpt = chunks[0] if chunks else article.content[:1500]

    metadata = metadata_service.extract_metadata(
        title=article.title,
        excerpt=excerpt,
    )

    print(f"CATEGORY: {metadata['category']}")
    print(f"CROPS: {metadata['crop']}")

    chunk_records = []

    for index, chunk in enumerate(chunks, start=1):

        embedding = embedding_service.generate_embedding(chunk)

        chunk_records.append(
            {
                "chunk_id": index,
                "content": chunk,
                "embedding": embedding,
            }
        )

    if dry_run:
        print(f"Would insert: {article.title} | Chunks={len(chunk_records)}")
        return len(chunk_records)

    article_data = {
        "title": article.title,
        "content": article.content,
        "url": article.url,
        "section": article.section,
        "content_length": article.content_length,
        "published_datetime": article.published_datetime,
        "updated_datetime": article.updated_datetime,
        "scrape_date": article.scrape_date,
        "crop": ",".join(metadata.get("crop", [])),
        "category": metadata.get("category"),
        "keywords": ",".join(metadata.get("keywords", [])),
        "source": source_label,
    }

    saved_article = article_repository.save(article_data)

    chunk_repository.save_chunks(
        article_id=saved_article.id,
        chunks=chunk_records,
    )

    print(f"Saved: {article.title} | Chunks={len(chunk_records)}")

    return len(chunk_records)


def _run_source(
    adapter: ScraperAdapter,
    chunking_service: ChunkingService,
    metadata_service: LLMMetadataService,
    embedding_service: EmbeddingService,
    article_repository: ArticleRepository,
    chunk_repository: ArticleChunkRepository,
    dry_run: bool = False,
) -> dict:
    """
    Runs a single source end to end, isolated from the other sources:
    a whole-source failure (e.g. every listing fetch exhausting its
    retries) or a single article's processing failure is caught and
    logged here rather than propagating and stopping the other
    registered sources from running. dry_run only changes what
    _process_article does at the very end (write vs. log) — this
    isolation structure is identical either way.
    """

    source_name = adapter.config.name
    inserted = 0
    chunks_saved = 0
    skipped_duplicates = 0
    errored = 0

    print(f"\n=== {adapter.config.source_label} ===")

    try:
        scraped_articles = adapter.scrape_all()

    except Exception:
        logger.exception(
            "Source failed before any articles were processed",
            extra={"source": source_name},
        )
        return {
            "source": source_name,
            "inserted": 0,
            "chunks": 0,
            "skipped_duplicates": 0,
            "errored": 0,
            "failed": True,
        }

    for article in scraped_articles:

        try:
            chunk_count = _process_article(
                article,
                adapter.config.source_label,
                chunking_service,
                metadata_service,
                embedding_service,
                article_repository,
                chunk_repository,
                dry_run=dry_run,
            )

        except Exception:
            logger.exception(
                "Failed to process article; skipping",
                extra={"source": source_name, "url": article.url},
            )
            errored += 1
            continue

        if chunk_count is None:
            skipped_duplicates += 1
        else:
            inserted += 1
            chunks_saved += chunk_count

    return {
        "source": source_name,
        "inserted": inserted,
        "chunks": chunks_saved,
        "skipped_duplicates": skipped_duplicates,
        "errored": errored,
        "failed": False,
    }


def run_pipeline(dry_run: bool = False) -> list[dict]:
    """
    Runs every registered source (see
    backend.ingestion.adapters.registry) as an independent,
    config-driven job and reports a per-source summary.

    dry_run runs the real scrape -> parse -> normalize -> chunk ->
    classify -> embed flow for every source — including real network
    requests and real LLM/embedding API calls, so it's a genuine
    rehearsal, not a mock — but skips the two database writes
    (article_repository.save / chunk_repository.save_chunks) at the
    end of _process_article, logging what would have been inserted
    instead. Per-source and per-article failure isolation in
    _run_source is unchanged in either mode.
    """

    chunking_service = ChunkingService()
    metadata_service = LLMMetadataService()
    embedding_service = EmbeddingService()
    article_repository = ArticleRepository()
    chunk_repository = ArticleChunkRepository()

    adapters = load_all_adapters()

    print(
        "Registered sources: "
        f"{[a.config.source_label for a in adapters]}"
    )

    if dry_run:
        print(
            "DRY RUN — scraping, classifying, and embedding for real; "
            "no rows will be written to the database.\n"
        )

    results = [
        _run_source(
            adapter,
            chunking_service,
            metadata_service,
            embedding_service,
            article_repository,
            chunk_repository,
            dry_run=dry_run,
        )
        for adapter in adapters
    ]

    print("\n=== Pipeline summary ===")

    if dry_run:
        print("(DRY RUN — nothing below was actually written)")

    total_inserted = 0
    total_chunks = 0
    total_skipped = 0
    total_errored = 0

    for result in results:

        status = "FAILED" if result["failed"] else "ok"

        print(
            f"{result['source']}: "
            f"{'would_insert' if dry_run else 'inserted'}="
            f"{result['inserted']} "
            f"chunks={result['chunks']} "
            f"skipped_duplicates={result['skipped_duplicates']} "
            f"errored={result['errored']} "
            f"[{status}]"
        )

        total_inserted += result["inserted"]
        total_chunks += result["chunks"]
        total_skipped += result["skipped_duplicates"]
        total_errored += result["errored"]

    label = "Total would insert" if dry_run else "Total inserted"

    print(f"\n{label}: {total_inserted} articles")
    print(f"Total generated: {total_chunks} chunks")
    print(f"Total skipped as duplicates: {total_skipped}")
    print(f"Total errored: {total_errored}")

    return results


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Run the ANS multi-source ingestion pipeline."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Run the full pipeline (real scraping, classification, "
            "and embedding calls) without writing any rows to the "
            "database."
        ),
    )
    args = parser.parse_args()

    run_pipeline(dry_run=args.dry_run)
