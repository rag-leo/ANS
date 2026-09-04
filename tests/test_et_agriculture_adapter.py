from datetime import datetime, timezone
from pathlib import Path

from backend.ingestion.adapters.config import load_source_config
from backend.ingestion.adapters.et_agriculture import ETAgricultureAdapter

_CONFIG_PATH = (
    Path(__file__).parent.parent
    / "backend"
    / "ingestion"
    / "configs"
    / "et_agriculture.yaml"
)

_FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "et_agriculture"
    / "ai_grading_tobacco_auctions.html"
)

_ARTICLE_URL = (
    "https://agriculture.economictimes.indiatimes.com/news/"
    "agri-tech-and-innovation/"
    "ai-grading-set-to-reshape-tobacco-auctions-in-andhra-pradesh/133150819"
)


def _build_adapter() -> ETAgricultureAdapter:

    config = load_source_config(_CONFIG_PATH)
    return ETAgricultureAdapter(config)


def test_parse_extracts_expected_fields():

    adapter = _build_adapter()
    html = _FIXTURE_PATH.read_text(encoding="utf-8")

    raw = adapter.parse(html, _ARTICLE_URL)

    assert raw.title == (
        "AI grading set to reshape tobacco auctions in Andhra Pradesh"
    )
    assert raw.section == "agri-tech-and-innovation"
    assert raw.published_date_raw == "Aug 11, 2026 at 03:48 PM"
    assert raw.updated_date_raw is None

    # Body should come from the .article-content container, not the
    # standfirst/lede div, and should not include navigation/share-menu
    # boilerplate or promo-slot HTML comments.
    assert "Tobacco Board" in raw.body_text
    assert "AI-based grading" in raw.body_text or "AI-based" in raw.body_text
    assert "PROMOSLOT" not in raw.body_text
    assert "Copy Link" not in raw.body_text
    assert "Share on Whatsapp" not in raw.body_text
    assert len(raw.body_text) > 300


def test_validate_passes_quality_gate():

    adapter = _build_adapter()
    html = _FIXTURE_PATH.read_text(encoding="utf-8")

    raw = adapter.parse(html, _ARTICLE_URL)

    assert adapter.validate(raw) is True


def test_normalize_sets_canonical_fields_and_parses_date():

    adapter = _build_adapter()
    html = _FIXTURE_PATH.read_text(encoding="utf-8")

    raw = adapter.parse(html, _ARTICLE_URL)
    article = adapter.normalize(raw)

    assert article.url == _ARTICLE_URL
    assert article.section == "agri-tech-and-innovation"
    assert article.content_length == len(article.content)

    # "Aug 11, 2026 at 03:48 PM" has no offset, so it's localized using
    # the source's configured timezone (Asia/Kolkata, IST = UTC+5:30)
    # and converted to UTC for storage.
    assert article.published_datetime == datetime(
        2026, 8, 11, 10, 18, 0, tzinfo=timezone.utc
    )


def test_sitemap_parsing_filters_to_article_urls():

    adapter = _build_adapter()

    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url>
            <loc>https://agriculture.economictimes.indiatimes.com/news/policy-and-rural-economy/wheat-industry-presses-fssai-for-crop-specific-testing-rules/133587607</loc>
        </url>
        <url>
            <loc>https://agriculture.economictimes.indiatimes.com/news/markets-and-trade</loc>
        </url>
    </urlset>"""

    urls = adapter._parse_sitemap_urls(sitemap_xml)

    assert urls == [
        "https://agriculture.economictimes.indiatimes.com/news/"
        "policy-and-rural-economy/"
        "wheat-industry-presses-fssai-for-crop-specific-testing-rules/133587607"
    ]
