from datetime import datetime, timezone
from unittest.mock import MagicMock

from backend.data.pipeline import _process_article, _run_source
from backend.ingestion.models import ScrapedArticle


def _make_article(url: str = "https://example.com/a") -> ScrapedArticle:

    return ScrapedArticle(
        section="news",
        title="Test Article",
        url=url,
        content="x" * 400,
        content_length=400,
        published_datetime=datetime(2026, 8, 11, 10, 0, tzinfo=timezone.utc),
        updated_datetime=None,
        scrape_date="2026-08-31",
    )


def _make_services():

    chunking_service = MagicMock()
    chunking_service.chunk_text.return_value = ["chunk one", "chunk two"]

    metadata_service = MagicMock()
    metadata_service.extract_metadata.return_value = {
        "category": "Market Intelligence",
        "crop": ["Wheat"],
        "keywords": ["Wheat"],
    }

    embedding_service = MagicMock()
    embedding_service.generate_embedding.return_value = [0.1, 0.2]

    article_repository = MagicMock()
    article_repository.get_by_url.return_value = None
    article_repository.save.return_value = MagicMock(id=42)

    chunk_repository = MagicMock()

    return (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    )


def test_process_article_uses_the_adapters_source_label_not_hardcoded():
    """
    Regression test for the Stage 1 finding: source used to be
    hardcoded "Agrowon" in two places. Confirms the value actually
    saved comes from whatever source_label is passed in.
    """

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    article = _make_article()

    _process_article(
        article,
        "ET Agriculture",
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    )

    saved_article_data = article_repository.save.call_args[0][0]
    assert saved_article_data["source"] == "ET Agriculture"


def test_process_article_classifies_from_title_and_first_chunk_only():
    """
    Regression test for the Stage 9/10 decision: classification uses
    title + first chunk, not the full article body — confirms the
    excerpt passed to the metadata service is chunks[0], not
    article.content.
    """

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    article = _make_article()

    _process_article(
        article,
        "Agrowon",
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    )

    metadata_service.extract_metadata.assert_called_once_with(
        title=article.title,
        excerpt="chunk one",
    )


def test_process_article_skips_existing_url_before_classifying():
    """
    Dedup must run before chunking/classification/embedding — those
    now have a real cost (an LLM call), so a duplicate shouldn't pay
    for any of them.
    """

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    article_repository.get_by_url.return_value = MagicMock()  # already exists

    result = _process_article(
        _make_article(),
        "Agrowon",
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    )

    assert result is None
    metadata_service.extract_metadata.assert_not_called()
    chunking_service.chunk_text.assert_not_called()
    embedding_service.generate_embedding.assert_not_called()
    article_repository.save.assert_not_called()
    chunk_repository.save_chunks.assert_not_called()


def test_process_article_saves_chunks_and_returns_count():

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    result = _process_article(
        _make_article(),
        "Krishi Jagran",
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    )

    assert result == 2
    article_repository.save.assert_called_once()

    saved_article_data = article_repository.save.call_args[0][0]
    assert saved_article_data["category"] == "Market Intelligence"
    assert saved_article_data["crop"] == "Wheat"

    chunk_repository.save_chunks.assert_called_once_with(
        article_id=42,
        chunks=[
            {"chunk_id": 1, "content": "chunk one", "embedding": [0.1, 0.2]},
            {"chunk_id": 2, "content": "chunk two", "embedding": [0.1, 0.2]},
        ],
    )


def test_run_source_isolates_a_whole_source_failure():
    """
    If adapter.scrape_all() raises (e.g. every listing fetch exhausted
    its retries), _run_source must catch it and report failure rather
    than letting the exception propagate and stop other sources.
    """

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    adapter = MagicMock()
    adapter.config.name = "broken_source"
    adapter.config.source_label = "Broken Source"
    adapter.scrape_all.side_effect = RuntimeError("listing fetch failed")

    result = _run_source(
        adapter,
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    )

    assert result == {
        "source": "broken_source",
        "inserted": 0,
        "chunks": 0,
        "skipped_duplicates": 0,
        "errored": 0,
        "failed": True,
    }


def test_run_source_isolates_a_single_article_failure():
    """
    One bad article (e.g. embedding call throws) shouldn't stop the
    rest of that source's articles from being processed.
    """

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    good_article_1 = _make_article("https://example.com/good-1")
    bad_article = _make_article("https://example.com/bad")
    good_article_2 = _make_article("https://example.com/good-2")

    adapter = MagicMock()
    adapter.config.name = "test_source"
    adapter.config.source_label = "Test Source"
    adapter.scrape_all.return_value = [
        good_article_1,
        bad_article,
        good_article_2,
    ]

    # Fail only for the bad article's URL, succeed otherwise.
    def get_by_url_side_effect(url):
        return None

    article_repository.get_by_url.side_effect = get_by_url_side_effect

    def save_side_effect(article_data):
        if article_data["url"] == "https://example.com/bad":
            raise RuntimeError("db write failed")
        return MagicMock(id=1)

    article_repository.save.side_effect = save_side_effect

    result = _run_source(
        adapter,
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    )

    assert result["failed"] is False
    assert result["inserted"] == 2  # the two good articles
    assert result["errored"] == 1  # the bad one, counted not silently dropped
    assert result["source"] == "test_source"


def test_process_article_dry_run_does_not_write_but_still_classifies_and_embeds():
    """
    dry_run must skip the two DB writes but still run the real
    classify/chunk/embed steps — it's a rehearsal of the full flow,
    not a mock of it (see run_pipeline's docstring).
    """

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    result = _process_article(
        _make_article(),
        "Agrowon",
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
        dry_run=True,
    )

    assert result == 2  # would-save chunk count, same shape as a real run
    metadata_service.extract_metadata.assert_called_once()
    assert embedding_service.generate_embedding.call_count == 2
    article_repository.save.assert_not_called()
    chunk_repository.save_chunks.assert_not_called()


def test_process_article_dry_run_still_skips_duplicates():

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    article_repository.get_by_url.return_value = MagicMock()  # already exists

    result = _process_article(
        _make_article(),
        "Agrowon",
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
        dry_run=True,
    )

    assert result is None
    metadata_service.extract_metadata.assert_not_called()


def test_run_source_dry_run_reports_would_insert_counts_without_writing():

    (
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
    ) = _make_services()

    adapter = MagicMock()
    adapter.config.name = "test_source"
    adapter.config.source_label = "Test Source"
    adapter.scrape_all.return_value = [
        _make_article("https://example.com/1"),
        _make_article("https://example.com/2"),
    ]

    result = _run_source(
        adapter,
        chunking_service,
        metadata_service,
        embedding_service,
        article_repository,
        chunk_repository,
        dry_run=True,
    )

    assert result["inserted"] == 2
    assert result["chunks"] == 4
    assert result["failed"] is False
    article_repository.save.assert_not_called()
    chunk_repository.save_chunks.assert_not_called()
