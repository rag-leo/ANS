import re
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime

from protego import Protego

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from backend.config.logging_config import get_logger
from backend.ingestion.models import ScrapedArticle

logger = get_logger(__name__)

# A browser UA is required here: this site's CDN returns 403 for
# non-browser User-Agents, including on robots.txt itself. Selenium's
# headless Chrome already presents a browser UA for the actual scrape
# requests below; this just makes the robots.txt check consistent
# with that, rather than a separate, more bot-like request.
_BROWSER_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

_DEFAULT_MIN_REQUEST_INTERVAL_SECONDS = 1.0


class _RateLimiter:
    """
    Thread-safe minimum-interval limiter, shared across all worker
    threads so concurrent scraping still spaces out real requests
    to the target site.
    """

    def __init__(self, min_interval_seconds: float) -> None:

        self._min_interval = min_interval_seconds
        self._lock = threading.Lock()
        self._last_request_at = 0.0

    def wait(self) -> None:

        with self._lock:

            now = time.monotonic()
            remaining = (
                self._min_interval
                - (now - self._last_request_at)
            )

            if remaining > 0:
                time.sleep(remaining)

            self._last_request_at = time.monotonic()


class AgrowonScraper:
    """
    Agrowon News Scraper
    """

    SECTIONS = {
        "market-intelligence": "https://agrowon.esakal.com/market-intelligence",
        "agro-special": "https://agrowon.esakal.com/agro-special",
        "weather-news": "https://agrowon.esakal.com/weather-news",
    }

    BASE_URL = "https://agrowon.esakal.com"

    ROBOTS_TXT_URL = f"{BASE_URL}/robots.txt"

    ARTICLE_PATTERN = re.compile(
        r"https://agrowon\.esakal\.com/.+/.+-[a-z0-9]+$"
    )

    MAX_WORKERS = 3

    MAX_SCROLL_ATTEMPTS = 8

    SCROLL_PAUSE_SECONDS = 1.5

    def __init__(self) -> None:

        self._robot_parser: Protego | None = None
        self._rate_limiter: _RateLimiter | None = None

    # -----------------------------------------------------
    # robots.txt / rate limiting
    # -----------------------------------------------------

    def _get_robot_parser(self) -> Protego | None:
        """
        Lazily fetches and caches robots.txt for this instance.

        Uses `protego` rather than the standard library's
        `urllib.robotparser`: this site's robots.txt relies
        heavily on `*` wildcard Disallow patterns (e.g.
        `/search*`), which `robotparser` silently fails to
        match at all (it treats `*` as a literal character),
        making it effectively a no-op against this file.
        `protego` implements the wildcard-aware matching real
        crawlers use.

        Returns None if robots.txt can't be retrieved at all, in
        which case callers should fail open rather than block
        scraping over a transient network issue.
        """

        if self._robot_parser is not None:
            return self._robot_parser

        try:
            request = urllib.request.Request(
                self.ROBOTS_TXT_URL,
                headers={"User-Agent": _BROWSER_USER_AGENT},
            )

            with urllib.request.urlopen(
                request, timeout=10
            ) as response:
                content = response.read().decode(
                    "utf-8", errors="replace"
                )

            parser = Protego.parse(content)

        except Exception:
            logger.exception(
                "Failed to fetch robots.txt; "
                "proceeding without robots.txt checks"
            )
            return None

        self._robot_parser = parser
        return parser

    def _is_allowed(self, url: str) -> bool:

        parser = self._get_robot_parser()

        if parser is None:
            return True

        return parser.can_fetch(url, _BROWSER_USER_AGENT)

    def _get_rate_limiter(self) -> _RateLimiter:

        if self._rate_limiter is None:

            parser = self._get_robot_parser()

            crawl_delay = (
                parser.crawl_delay(_BROWSER_USER_AGENT)
                if parser is not None
                else None
            )

            self._rate_limiter = _RateLimiter(
                float(crawl_delay)
                if crawl_delay
                else _DEFAULT_MIN_REQUEST_INTERVAL_SECONDS
            )

        return self._rate_limiter

    @staticmethod
    def _clean(text: str) -> str:

        return re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

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

        for _ in range(self.MAX_SCROLL_ATTEMPTS):

            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )

            time.sleep(self.SCROLL_PAUSE_SECONDS)

            new_height = driver.execute_script(
                "return document.body.scrollHeight"
            )

            if new_height == last_height:
                break

            last_height = new_height

    def collect_article_urls(
        self,
    ) -> list[str]:
        driver = self._create_driver()

        article_urls = set()

        try:

            for section_name, section_url in self.SECTIONS.items():

                if not self._is_allowed(section_url):
                    logger.warning(
                        "Skipping section disallowed by robots.txt",
                        extra={"section": section_name, "url": section_url},
                    )
                    continue

                logger.info(
                    "Collecting URLs from section",
                    extra={"section": section_name},
                )

                self._get_rate_limiter().wait()

                driver.get(section_url)

                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located(
                        (By.TAG_NAME, "a")
                    )
                )

                self._scroll_to_load_content(driver)

                soup = BeautifulSoup(
                    driver.page_source,
                    "html.parser",
                )

                for tag in soup.find_all(
                    "a",
                    href=True,
                ):

                    href = tag["href"]

                    if href.startswith("/"):
                        href = self.BASE_URL + href

                    if self.ARTICLE_PATTERN.match(href):
                        article_urls.add(href)

        finally:

            driver.quit()

        logger.info(
            "Finished collecting article URLs",
            extra={"url_count": len(article_urls)},
        )

        return list(article_urls)

    def scrape_article(
        self,
        url: str,
    ) -> ScrapedArticle | None:

        if not self._is_allowed(url):
            logger.warning(
                "Skipping article disallowed by robots.txt",
                extra={"url": url},
            )
            return None

        self._get_rate_limiter().wait()

        driver = self._create_driver()

        try:

            driver.get(url)

            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located(
                    (By.TAG_NAME, "h1")
                )
            )

            soup = BeautifulSoup(
                driver.page_source,
                "html.parser",
            )

            title_tag = soup.find("h1")

            title = (
                self._clean(title_tag.get_text())
                if title_tag
                else ""
            )

            published_date = None

            publish_block = soup.find(
                "div",
                {"data-test-id": "publishDetails"},
            )

            if publish_block:

                time_tag = publish_block.find("time")

                if (
                    time_tag
                    and time_tag.get("datetime")
                ):
                    published_date = (
                        time_tag["datetime"]
                    )

            updated_date = None

            update_block = soup.find(
                "div",
                {"data-test-id": "updateDetails"},
            )

            if update_block:

                time_tag = update_block.find("time")

                if (
                    time_tag
                    and time_tag.get("datetime")
                ):
                    updated_date = (
                        time_tag["datetime"]
                    )

            paragraphs = []

            for p in soup.find_all("p"):

                text = self._clean(
                    p.get_text()
                )

                if len(text) > 40:
                    paragraphs.append(text)

            content = "\n\n".join(
                paragraphs
            )

            return ScrapedArticle(
                section=url.split("/")[3],
                title=title,
                url=url,
                content=content,
                content_length=len(content),
                published_datetime=published_date,
                updated_datetime=updated_date,
                scrape_date=datetime.now().strftime(
                    "%Y-%m-%d"
                ),
            )

        except Exception:

            logger.exception(
                "Failed to scrape article",
                extra={"url": url},
            )

            return None

        finally:

            driver.quit()

    def scrape_articles(
        self,
    ) -> list:
        urls = self.collect_article_urls()

        logger.info(
            "Scraping articles in parallel",
            extra={"url_count": len(urls), "max_workers": self.MAX_WORKERS},
        )

        articles = []

        with ThreadPoolExecutor(
            max_workers=self.MAX_WORKERS
        ) as executor:

            futures = [
                executor.submit(
                    self.scrape_article,
                    url
                )
                for url in urls
            ]

            for future in as_completed(
                futures
            ):

                article = future.result()

                if (
                    article
                    and article.content_length > 300
                ):

                    articles.append(
                        article
                    )

                    logger.info(
                        "Scraped article",
                        extra={"title": article.title[:70]},
                    )

        logger.info(
            "Finished scraping articles",
            extra={"valid_article_count": len(articles)},
        )

        return articles

if __name__ == "__main__":

    scraper = AgrowonScraper()

    articles = scraper.scrape_articles()

    print(
        f"\nTotal articles scraped: "
        f"{len(articles)}"
    )

    if articles:

        first = articles[0]

        print("\nSample Article")

        print(
            f"Title: {first.title}"
        )

        print(
            f"Length: "
            f"{first.content_length}"
        )

        print(
            f"URL: {first.url}"
        )
