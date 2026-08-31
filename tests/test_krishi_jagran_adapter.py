from datetime import datetime, timezone
from pathlib import Path

from backend.ingestion.adapters.config import load_source_config
from backend.ingestion.adapters.krishi_jagran import KrishiJagranAdapter

_CONFIG_PATH = (
    Path(__file__).parent.parent
    / "backend"
    / "ingestion"
    / "configs"
    / "krishi_jagran.yaml"
)

_FIXTURE_PATH = (
    Path(__file__).parent
    / "fixtures"
    / "krishi_jagran"
    / "bayer_xivana_smart.html"
)

_ARTICLE_URL = (
    "https://krishijagran.com/news/"
    "bayer-launches-xivana-smart-a-next-generation-fungicide-to-help-"
    "horticulture-farmers-combat-devastating-crop-diseases/"
)


def _build_adapter() -> KrishiJagranAdapter:

    config = load_source_config(_CONFIG_PATH)
    return KrishiJagranAdapter(config)


def test_parse_extracts_expected_fields():

    adapter = _build_adapter()
    html = _FIXTURE_PATH.read_text(encoding="utf-8")

    raw = adapter.parse(html, _ARTICLE_URL)

    assert raw.title == (
        "Bayer launches Xivana™ Smart, a next-generation fungicide "
        "to help horticulture farmers combat devastating crop diseases"
    )

    # No structural category signal exists on this site (see Stage 4/6
    # recon) — section should be left unset, not guessed.
    assert raw.section is None

    # Non-zero-padded offset from JSON-LD ("+5:30") should be padded
    # to a form datetime.fromisoformat can parse ("+05:30").
    assert raw.published_date_raw == "2026-08-19T17:06+05:30"
    assert raw.updated_date_raw == "2026-08-19T17:06+05:30"

    # Body should come from the <article> container, excluding
    # footer/sidebar CTAs that sit outside it.
    assert "Xivana" in raw.body_text
    assert "Downy mildew" in raw.body_text
    assert "Subscribe to our Newsletter" not in raw.body_text
    assert "We're on WhatsApp" not in raw.body_text
    assert "Krishi Jagran Mobile App" not in raw.body_text
    assert len(raw.body_text) > 300


def test_validate_passes_quality_gate():

    adapter = _build_adapter()
    html = _FIXTURE_PATH.read_text(encoding="utf-8")

    raw = adapter.parse(html, _ARTICLE_URL)

    assert adapter.validate(raw) is True


def test_normalize_converts_ist_offset_to_utc():

    adapter = _build_adapter()
    html = _FIXTURE_PATH.read_text(encoding="utf-8")

    raw = adapter.parse(html, _ARTICLE_URL)
    article = adapter.normalize(raw)

    assert article.url == _ARTICLE_URL
    assert article.section is None
    assert article.content_length == len(article.content)

    # "2026-08-19T17:06+05:30" -> UTC
    assert article.published_datetime == datetime(
        2026, 8, 19, 11, 36, 0, tzinfo=timezone.utc
    )
    assert article.updated_datetime == datetime(
        2026, 8, 19, 11, 36, 0, tzinfo=timezone.utc
    )


def test_sitemap_parsing_filters_and_caps_urls():

    adapter = _build_adapter()

    sitemap_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://krishijagran.com/news/article-one/</loc></url>
        <url><loc>https://krishijagran.com/news/article-two/</loc></url>
        <url><loc>https://krishijagran.com/agripedia/not-news/</loc></url>
    </urlset>"""

    urls = adapter._parse_sitemap_urls(sitemap_xml)

    assert urls == [
        "https://krishijagran.com/news/article-one/",
        "https://krishijagran.com/news/article-two/",
    ]


def test_pad_offset_zero_pads_single_digit_hour():

    assert (
        KrishiJagranAdapter._pad_offset("2026-08-19T17:06+5:30")
        == "2026-08-19T17:06+05:30"
    )
    assert (
        KrishiJagranAdapter._pad_offset("2026-08-19T17:06+05:30")
        == "2026-08-19T17:06+05:30"
    )
    assert KrishiJagranAdapter._pad_offset(None) is None
