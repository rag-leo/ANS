# backend/ingestion/adapters/et_agriculture.py

import re
import xml.etree.ElementTree as ET

import requests
from bs4 import BeautifulSoup
from bs4 import Comment

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


class ETAgricultureAdapter(HttpFetchMixin, ScraperAdapter):
    """
    ET Agriculture scraper.

    Article pages are server-rendered (Next.js), so this adapter fetches
    plain HTML over HTTP rather than driving a browser. Discovery uses
    the site's Google News sitemap instead of scraping/scrolling a
    listing page, since the listing page's articles beyond the first
    few are loaded via an unexposed client-side call.
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

        page_text = soup.get_text()

        published_date_raw = self._extract_date_text(
            page_text, selectors.published_date_pattern
        )
        updated_date_raw = self._extract_date_text(
            page_text, selectors.updated_date_pattern
        )

        content = self._extract_body(soup, selectors)

        parts = url.split("/")
        section = parts[4] if len(parts) > 4 else None

        return RawExtraction(
            url=url,
            title=title,
            body_text=content,
            published_date_raw=published_date_raw,
            updated_date_raw=updated_date_raw,
            section=section,
        )

    @staticmethod
    def _extract_date_text(page_text: str, pattern: str | None) -> str | None:

        if not pattern:
            return None

        match = re.search(pattern, page_text)

        return match.group(1) if match else None

    def _extract_body(self, soup: BeautifulSoup, selectors) -> str:

        if selectors.body_mode == "container_text":

            container = (
                soup.select_one(selectors.body_container)
                if selectors.body_container
                else None
            )

            if not container:
                return ""

            for tag in container.find_all(["script", "style", "figure", "img"]):
                tag.decompose()

            for comment in container.find_all(
                string=lambda text: isinstance(text, Comment)
            ):
                comment.extract()

            return self._clean(container.get_text(separator=" "))

        return self._extract_paragraphs(soup)
