# backend/ingestion/adapters/krishi_jagran.py

import json
import re
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup

from backend.config.logging_config import get_logger
from backend.ingestion.adapters.base import (
    FetchError,
    HttpFetchMixin,
    RawExtraction,
    ScraperAdapter,
)
from backend.ingestion.adapters.config import SourceConfig
from backend.ingestion.adapters.rate_limiter import RateLimiter
from backend.ingestion.adapters.robots import RobotsChecker

logger = get_logger(__name__)

_SITEMAP_NS = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}

# Krishi Jagran's JSON-LD dates use a non-zero-padded hour offset
# (e.g. "+5:30" instead of "+05:30"), which neither datetime.fromisoformat
# nor strptime's %z will accept. Pads it before it reaches base.py's
# generic date parsing.
_SHORT_OFFSET_PATTERN = re.compile(r"([+-])(\d):(\d{2})$")


class KrishiJagranAdapter(HttpFetchMixin, ScraperAdapter):
    """
    Krishi Jagran News scraper.

    Article pages are server-rendered plain HTML (confirmed during
    recon), so this fetches over HTTP rather than driving a browser.
    Discovery uses the site's news sitemap rather than its listing
    page's "View More" button, which loads further pages via a
    client-side call with no exposed endpoint.

    Krishi Jagran exposes no structural category/crop signal (no
    breadcrumb category level, no populated JSON-LD keywords) — unlike
    Agrowon and ET Agriculture, section is left unset here rather than
    guessed from the URL, since the URL carries no category segment
    either (see Stage 4 recon).
    """

    def __init__(self, config: SourceConfig) -> None:

        super().__init__(config)

        self._robots = RobotsChecker(
            config.resolved_robots_txt_url,
            config.user_agent,
        )

        self._rate_limiter: RateLimiter | None = None
        self._article_pattern = re.compile(config.article_url_pattern)

        self._session = requests.Session()
        self._session.headers.update({"User-Agent": config.user_agent})

    # -----------------------------------------------------
    # Rate limiting
    # -----------------------------------------------------

    def _get_rate_limiter(self) -> RateLimiter:

        if self._rate_limiter is None:

            crawl_delay = (
                self._robots.crawl_delay()
                if self.config.rate_limit.respect_crawl_delay
                else None
            )

            self._rate_limiter = RateLimiter(
                crawl_delay
                if crawl_delay
                else self.config.rate_limit.min_interval_seconds
            )

        return self._rate_limiter

    # -----------------------------------------------------
    # ScraperAdapter interface
    # -----------------------------------------------------

    def collect_listing_urls(self) -> list[str]:

        sitemap_url = self.config.listing.sitemap_url

        if not sitemap_url:
            raise ValueError(
                "listing.sitemap_url is required for sitemap pagination"
            )

        if not self._robots.is_allowed(sitemap_url):
            logger.warning(
                "Sitemap disallowed by robots.txt",
                extra={"url": sitemap_url},
            )
            return []

        try:
            xml_text = self.fetch(sitemap_url)
        except FetchError:
            logger.exception(
                "Failed to fetch sitemap", extra={"url": sitemap_url}
            )
            return []

        urls = self._parse_sitemap_urls(xml_text)

        max_urls = self.config.listing.sitemap_max_urls

        if max_urls is not None:
            urls = urls[:max_urls]

        logger.info(
            "Finished collecting article URLs from sitemap",
            extra={"url_count": len(urls)},
        )

        return urls

    def _parse_sitemap_urls(self, xml_text: str) -> list[str]:

        try:
            root = ET.fromstring(xml_text)
        except ET.ParseError:
            logger.exception("Failed to parse sitemap XML")
            return []

        locs = [
            loc.text.strip()
            for loc in root.findall(".//sm:url/sm:loc", _SITEMAP_NS)
            if loc.text
        ]

        return [u for u in locs if self._article_pattern.match(u)]

    def parse(self, html: str, url: str) -> RawExtraction:

        soup = BeautifulSoup(html, "html.parser")
        selectors = self.config.selectors

        title_tag = soup.select_one(selectors.title)
        title = self._clean(title_tag.get_text()) if title_tag else ""

        news_article = self._find_news_article_ld(soup)

        published_date_raw = self._pad_offset(
            news_article.get("datePublished") if news_article else None
        )
        updated_date_raw = self._pad_offset(
            news_article.get("dateModified") if news_article else None
        )

        content = self._extract_paragraphs(soup)

        return RawExtraction(
            url=url,
            title=title,
            body_text=content,
            published_date_raw=published_date_raw,
            updated_date_raw=updated_date_raw,
            # No structural category/crop signal exists on this site
            # (see class docstring) — left unset rather than guessed.
            section=None,
        )

    @staticmethod
    def _find_news_article_ld(soup: BeautifulSoup) -> dict | None:

        for script in soup.find_all(
            "script", attrs={"type": "application/ld+json"}
        ):

            try:
                data = json.loads(script.string or "")
            except (TypeError, ValueError):
                continue

            if isinstance(data, dict) and data.get("@type") == "NewsArticle":
                return data

        return None

    @staticmethod
    def _pad_offset(raw_value: str | None) -> str | None:
        """
        "2026-08-19T17:06+5:30" -> "2026-08-19T17:06+05:30" so
        datetime.fromisoformat (used downstream in base.py when no
        date_format is configured) can parse it.
        """

        if not raw_value:
            return None

        return _SHORT_OFFSET_PATTERN.sub(r"\g<1>0\2:\3", raw_value)
