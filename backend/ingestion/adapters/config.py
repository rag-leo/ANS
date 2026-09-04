# backend/ingestion/adapters/config.py

from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel


class SectionConfig(BaseModel):
    """One listing page to crawl for article links (e.g. a category page)."""

    name: str
    url: str


class ListingConfig(BaseModel):

    pagination_type: Literal[
        "infinite_scroll",
        "query_param",
        "single_page",
        "sitemap",
    ]

    sections: list[SectionConfig] = []

    # infinite_scroll settings
    max_scroll_attempts: int = 8
    scroll_pause_seconds: float = 1.5

    # query_param pagination settings (e.g. "?page=2")
    page_param: str | None = None
    max_pages: int | None = None

    # CSS selector for candidate article links within a listing page
    article_link_selector: str = "a"

    # sitemap pagination settings: a Google News (or plain) sitemap URL
    # listing recent article <loc> entries directly, used instead of
    # scraping/scrolling a listing page.
    sitemap_url: str | None = None

    # Some sitemaps cover a source's entire historical archive rather
    # than a recent window (e.g. Krishi Jagran's, ~19k URLs, sorted
    # newest-first). Cap how many of the (recency-ordered) entries a
    # single run processes, rather than re-walking the whole archive
    # every time — downstream URL-based dedup makes this safe even if
    # the cap and a source's true publish cadence don't align exactly.
    sitemap_max_urls: int | None = None


class SelectorConfig(BaseModel):

    title: str = "h1"

    # CSS selector scoping the article body.
    # "paragraphs" mode (Agrowon-style): collect body_paragraph elements
    # within body_container (or the whole page if unset).
    # "container_text" mode (ET-style, no <p> tags in the body): take
    # body_container's full text as one cleaned block.
    body_mode: Literal["paragraphs", "container_text"] = "paragraphs"
    body_container: str | None = None
    body_paragraph: str = "p"
    min_paragraph_length: int = 40

    # time-element date extraction (Agrowon-style): a container selector
    # holding a <time datetime="..."> element.
    published_date_container: str | None = None
    updated_date_container: str | None = None
    date_element: str = "time"
    date_attribute: str = "datetime"

    # free-text date extraction (ET-style): a regex with one capture
    # group, searched against the full page text rather than a specific
    # element, for sites that render the date as plain text with no
    # dedicated container or machine-readable attribute.
    published_date_pattern: str | None = None
    updated_date_pattern: str | None = None

    # strptime format for the raw/extracted date string, if it isn't
    # already ISO-8601. None means "use the raw string as-is" (current
    # Agrowon behavior).
    date_format: str | None = None


class FetchConfig(BaseModel):

    render_js: bool = True
    page_load_timeout_seconds: int = 20
    wait_for_selector: str = "h1"
    listing_wait_for_selector: str = "a"


class RetryConfig(BaseModel):

    max_attempts: int = 2
    backoff_seconds: float = 2.0

    # What to do when an entire listing/section page fails after retries:
    # skip just that section, or abort the whole source run.
    on_listing_failure: Literal["abort_source", "skip_section"] = "skip_section"


class RateLimitConfig(BaseModel):

    min_interval_seconds: float = 1.0
    respect_crawl_delay: bool = True


class QualityConfig(BaseModel):

    min_content_length: int = 300


class SourceConfig(BaseModel):
    """Full per-source configuration, loaded from a YAML file."""

    name: str
    source_label: str
    language: str

    # IANA timezone the source publishes wall-clock times in (e.g. a
    # date string with no offset, or a naive datetime attribute). Used
    # to localize such values before converting to UTC for storage —
    # see ScraperAdapter._parse_date(). Defaults to Asia/Kolkata since
    # all current sources are India-based agri-news publishers, but is
    # explicit and overridable per source rather than assumed in code.
    timezone: str = "Asia/Kolkata"

    base_url: str
    robots_txt_url: str | None = None
    user_agent: str

    article_url_pattern: str
    concurrency: int = 3

    listing: ListingConfig
    selectors: SelectorConfig
    fetch: FetchConfig = FetchConfig()
    retry: RetryConfig = RetryConfig()
    rate_limit: RateLimitConfig = RateLimitConfig()
    quality: QualityConfig = QualityConfig()

    @property
    def resolved_robots_txt_url(self) -> str:

        if self.robots_txt_url:
            return self.robots_txt_url

        return f"{self.base_url.rstrip('/')}/robots.txt"


def load_source_config(path: str | Path) -> SourceConfig:

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return SourceConfig(**raw)
