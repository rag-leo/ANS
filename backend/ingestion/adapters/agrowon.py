# backend/ingestion/adapters/agrowon.py

import re
import time

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from backend.config.logging_config import get_logger
from backend.ingestion.adapters.base import (
    FetchError,
    RawExtraction,
    ScraperAdapter,
)
from backend.ingestion.adapters.config import SourceConfig
from backend.ingestion.adapters.rate_limiter import RateLimiter
from backend.ingestion.adapters.robots import RobotsChecker

logger = get_logger(__name__)


class AgrowonAdapter(ScraperAdapter):
    """
    Agrowon News Scraper, adapter form.

    Selenium + BeautifulSoup, config-driven via SourceConfig
    (see backend/ingestion/configs/agrowon.yaml).
    """

    def __init__(self, config: SourceConfig) -> None:

        super().__init__(config)

        self._robots = RobotsChecker(
            config.resolved_robots_txt_url,
            config.user_agent,
        )

        self._rate_limiter: RateLimiter | None = None
        self._article_pattern = re.compile(config.article_url_pattern)

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
    # Selenium helpers
    # -----------------------------------------------------

    @staticmethod
    def _create_driver():

        options = Options()

        options.add_argument("--headless=new")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--disable-dev-shm-usage")

        return webdriver.Chrome(options=options)

    def _scroll_to_load_content(self, driver) -> None:
        """
        Scrolls to trigger lazy-loaded content, stopping as soon
        as the page stops growing instead of always waiting for
        a fixed number of iterations.
        """

        last_height = driver.execute_script(
            "return document.body.scrollHeight"
        )

        for _ in range(self.config.listing.max_scroll_attempts):

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(self.config.listing.scroll_pause_seconds)

            new_height = driver.execute_script(
                "return document.body.scrollHeight"
            )

            if new_height == last_height:
                break

            last_height = new_height

    # -----------------------------------------------------
    # ScraperAdapter interface
    # -----------------------------------------------------

    def collect_listing_urls(self) -> list[str]:

        driver = self._create_driver()

        article_urls = set()

        try:

            for section in self.config.listing.sections:

                if not self._robots.is_allowed(section.url):
                    logger.warning(
                        "Skipping section disallowed by robots.txt",
                        extra={"section": section.name, "url": section.url},
                    )
                    continue

                logger.info(
                    "Collecting URLs from section",
                    extra={"section": section.name},
                )

                self._get_rate_limiter().wait()

                try:
                    driver.get(section.url)

                    WebDriverWait(
                        driver, self.config.fetch.page_load_timeout_seconds
                    ).until(
                        EC.presence_of_element_located(
                            (
                                By.TAG_NAME,
                                self.config.fetch.listing_wait_for_selector,
                            )
                        )
                    )

                    self._scroll_to_load_content(driver)

                    soup = BeautifulSoup(driver.page_source, "html.parser")

                except Exception:
                    logger.exception(
                        "Failed to collect URLs from section",
                        extra={"section": section.name, "url": section.url},
                    )

                    if self.config.retry.on_listing_failure == "skip_section":
                        continue

                    raise

                for tag in soup.find_all(
                    self.config.listing.article_link_selector, href=True
                ):

                    href = tag["href"]

                    if href.startswith("/"):
                        href = self.config.base_url + href

                    if self._article_pattern.match(href):
                        article_urls.add(href)

        finally:

            driver.quit()

        logger.info(
            "Finished collecting article URLs",
            extra={"url_count": len(article_urls)},
        )

        return list(article_urls)

    def fetch(self, url: str) -> str:

        if not self._robots.is_allowed(url):
            raise FetchError(f"Disallowed by robots.txt: {url}")

        max_attempts = self.config.retry.max_attempts
        last_exc: Exception | None = None

        for attempt in range(1, max_attempts + 1):

            self._get_rate_limiter().wait()

            driver = self._create_driver()

            try:
                driver.get(url)

                WebDriverWait(
                    driver, self.config.fetch.page_load_timeout_seconds
                ).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME, self.config.fetch.wait_for_selector)
                    )
                )

                return driver.page_source

            except Exception as exc:

                last_exc = exc

                logger.warning(
                    "Fetch attempt failed",
                    extra={"url": url, "attempt": attempt},
                )

                if attempt < max_attempts:
                    time.sleep(self.config.retry.backoff_seconds)

            finally:

                driver.quit()

        raise FetchError(
            f"Failed to fetch {url} after {max_attempts} attempts"
        ) from last_exc

    def parse(self, html: str, url: str) -> RawExtraction:

        soup = BeautifulSoup(html, "html.parser")
        selectors = self.config.selectors

        title_tag = soup.select_one(selectors.title)
        title = self._clean(title_tag.get_text()) if title_tag else ""

        published_date_raw = self._extract_date(
            soup, selectors.published_date_container
        )
        updated_date_raw = self._extract_date(
            soup, selectors.updated_date_container
        )

        content = self._extract_paragraphs(soup)

        return RawExtraction(
            url=url,
            title=title,
            body_text=content,
            published_date_raw=published_date_raw,
            updated_date_raw=updated_date_raw,
            section=url.split("/")[3],
        )

    def _extract_date(self, soup: BeautifulSoup, container_selector: str | None) -> str | None:

        if not container_selector:
            return None

        block = soup.select_one(container_selector)

        if not block:
            return None

        selectors = self.config.selectors
        time_tag = block.find(selectors.date_element)

        if time_tag and time_tag.get(selectors.date_attribute):
            return time_tag[selectors.date_attribute]

        return None
