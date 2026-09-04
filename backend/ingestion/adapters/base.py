# backend/ingestion/adapters/base.py

import re
import time
from abc import ABC, abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import requests

from backend.config.logging_config import get_logger
from backend.ingestion.adapters.config import SourceConfig
from backend.ingestion.models import ScrapedArticle

logger = get_logger(__name__)


class FetchError(Exception):
    """
    Raised by fetch() when a page cannot be retrieved after the
    configured number of retry attempts. Callers decide whether a
    given FetchError is fatal (listing pages, per config.retry) or
    skippable (individual articles, always skippable).
    """


@dataclass
class RawExtraction:
    """
    Unprocessed fields pulled straight off a page by parse(),
    before normalize() cleans/parses them into a ScrapedArticle.
    """

    url: str
    title: str
    body_text: str
    published_date_raw: str | None
    updated_date_raw: str | None
    section: str | None


class ScraperAdapter(ABC):
    """
    Common interface every source-specific scraper implements.

    Subclasses own the source-specific mechanics (how to page through
    listings, how to fetch a page, how to pull fields out of its HTML).
    Orchestration and the steps that don't vary by source (quality
    gating, text/date normalization, threaded batch scraping) live here
    so they aren't reimplemented per adapter.
    """

    def __init__(self, config: SourceConfig) -> None:
        self.config = config

    # -----------------------------------------------------
    # Source-specific steps (implemented per adapter)
    # -----------------------------------------------------

    @abstractmethod
    def collect_listing_urls(self) -> list[str]:
        """
        Discover candidate article URLs across every configured
        section/page, following config.listing's pagination_type.
        """

    @abstractmethod
    def fetch(self, url: str) -> str:
        """
        Retrieve raw HTML for a URL.

        Must honor robots.txt, apply the configured rate limit before
        each real request, and retry up to config.retry.max_attempts
        with config.retry.backoff_seconds between attempts. Raises
        FetchError if all attempts are exhausted or robots.txt disallows
        the URL.
        """

    @abstractmethod
    def parse(self, html: str, url: str) -> RawExtraction:
        """
        Extract raw fields from an article page's HTML using
        config.selectors. Performs no cleaning or date parsing —
        that happens in normalize().
        """

    # -----------------------------------------------------
    # Shared steps (same for every source)
    # -----------------------------------------------------

    def validate(self, raw: RawExtraction) -> bool:
        """
        Quality gate applied after parse(), before normalize().
        Mirrors the original inline `content_length > 300` check
        (strict greater-than) as a shared, config-tunable step.
        """

        return len(raw.body_text) > self.config.quality.min_content_length

    @staticmethod
    def _clean(text: str) -> str:

        return re.sub(r"\s+", " ", text).strip()

    def _extract_paragraphs(self, soup) -> str:
        """
        Shared "paragraphs" body extraction: collect
        config.selectors.body_paragraph elements within
        config.selectors.body_container (or the whole page if unset),
        filtered by min_paragraph_length, joined with blank lines.
        Used by every adapter whose source renders body text in
        genuine <p> tags (Agrowon, Krishi Jagran) — ET Agriculture
        doesn't and uses its own "container_text" extraction instead.
        """

        selectors = self.config.selectors

        container = (
            soup.select_one(selectors.body_container)
            if selectors.body_container
            else soup
        )

        if container is None:
            return ""

        paragraphs = []

        for p in container.find_all(selectors.body_paragraph):

            text = self._clean(p.get_text())

            if len(text) > selectors.min_paragraph_length:
                paragraphs.append(text)

        return "\n\n".join(paragraphs)

    def _parse_date(self, raw_value: str | None) -> datetime | None:
        """
        Parses a raw date string into an aware UTC datetime.

        If the parsed value has no offset (a naive datetime.strptime
        result, or an ISO string with no offset), it's localized using
        the source's configured timezone (config.timezone) before
        converting to UTC — never a hardcoded assumption. If the raw
        value already carries an offset (e.g. an ISO string with "Z"
        or "+05:30"), that offset is trusted as-is and only converted,
        not reinterpreted.
        """

        if not raw_value:
            return None

        try:
            if self.config.selectors.date_format:
                parsed = datetime.strptime(
                    raw_value, self.config.selectors.date_format
                )
            else:
                parsed = datetime.fromisoformat(raw_value)

        except ValueError:
            logger.warning(
                "Failed to parse date; storing as missing",
                extra={"raw_value": raw_value, "source": self.config.name},
            )
            return None

        if parsed.tzinfo is None:
            parsed = parsed.replace(
                tzinfo=ZoneInfo(self.config.timezone)
            )

        return parsed.astimezone(timezone.utc)

    def normalize(self, raw: RawExtraction) -> ScrapedArticle:
        """
        Cleans extracted text and dates, and stamps source/language
        from config rather than hardcoding them per adapter.
        """

        return ScrapedArticle(
            section=raw.section,
            title=raw.title.strip(),
            url=raw.url,
            content=raw.body_text,
            content_length=len(raw.body_text),
            published_datetime=self._parse_date(raw.published_date_raw),
            updated_datetime=self._parse_date(raw.updated_date_raw),
            scrape_date=datetime.now().strftime("%Y-%m-%d"),
        )

    # -----------------------------------------------------
    # Orchestration
    # -----------------------------------------------------

    def scrape_article(self, url: str) -> ScrapedArticle | None:

        try:
            html = self.fetch(url)
            raw = self.parse(html, url)

        except FetchError:
            logger.warning(
                "Skipping article after fetch failure",
                extra={"url": url, "source": self.config.name},
            )
            return None

        except Exception:
            logger.exception(
                "Failed to parse article",
                extra={"url": url, "source": self.config.name},
            )
            return None

        if not self.validate(raw):
            return None

        return self.normalize(raw)

    def scrape_all(self) -> list[ScrapedArticle]:

        urls = self.collect_listing_urls()

        logger.info(
            "Scraping articles in parallel",
            extra={
                "source": self.config.name,
                "url_count": len(urls),
                "max_workers": self.config.concurrency,
            },
        )

        articles = []

        with ThreadPoolExecutor(
            max_workers=self.config.concurrency
        ) as executor:

            futures = [
                executor.submit(self.scrape_article, url) for url in urls
            ]

            for future in as_completed(futures):

                article = future.result()

                if article:
                    articles.append(article)

        logger.info(
            "Finished scraping source",
            extra={
                "source": self.config.name,
                "valid_article_count": len(articles),
            },
        )

        return articles


class HttpFetchMixin:
    """
    Shared fetch() for ScraperAdapter subclasses that retrieve pages
    over plain HTTP via `requests` rather than a browser (used by
    ETAgricultureAdapter and KrishiJagranAdapter — both confirmed
    server-rendered during recon, unlike Agrowon which needs Selenium).

    Expects the mixing class to set self._session (a requests.Session)
    and self._robots (a RobotsChecker), and to provide
    self._get_rate_limiter(), same as AgrowonAdapter's Selenium-based
    fetch() does independently.
    """

    config: SourceConfig
    _session: requests.Session

    def fetch(self, url: str) -> str:

        if not self._robots.is_allowed(url):
            raise FetchError(f"Disallowed by robots.txt: {url}")

        max_attempts = self.config.retry.max_attempts
        last_exc: Exception | None = None

        for attempt in range(1, max_attempts + 1):

            self._get_rate_limiter().wait()

            try:
                response = self._session.get(
                    url,
                    timeout=self.config.fetch.page_load_timeout_seconds,
                )
                response.raise_for_status()
                return response.text

            except Exception as exc:

                last_exc = exc

                logger.warning(
                    "Fetch attempt failed",
                    extra={"url": url, "attempt": attempt},
                )

                if attempt < max_attempts:
                    time.sleep(self.config.retry.backoff_seconds)

        raise FetchError(
            f"Failed to fetch {url} after {max_attempts} attempts"
        ) from last_exc
