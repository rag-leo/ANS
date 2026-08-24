import os
import re
import ssl
import time
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from backend.ingestion.models import ScrapedArticle

#----------------------------

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

    ARTICLE_PATTERN = re.compile(
        r"https://agrowon\.esakal\.com/.+/.+-[a-z0-9]+$"
    )

    MAX_WORKERS = 3

    def __init__(self) -> None:

        os.environ["WDM_SSL_VERIFY"] = "0"

        ssl._create_default_https_context = (
            ssl._create_unverified_context
        )

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

    def collect_article_urls(
        self,
    ) -> list[str]:
        driver = self._create_driver()


        article_urls = set()

        try:

            for section_name, section_url in self.SECTIONS.items():

                print(
                    f"\n🔎 Collecting URLs from: "
                    f"{section_name}"
                )

                driver.get(section_url)

                time.sleep(3)

                for _ in range(4):

                    driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )

                    time.sleep(2)

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

        print(
            f"\n✅ Total unique URLs collected: "
            f"{len(article_urls)}"
        )

        return list(article_urls)


    def scrape_article(
        self,
        url: str,
    ) -> ScrapedArticle | None:

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

            return None

        finally:

            driver.quit()

    def scrape_articles(
        self,
    ) -> list:
        urls = self.collect_article_urls()


        print(
            "\n⚡ Scraping articles in parallel...\n"
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

                    print(
                        f"✔ {article.title[:70]}"
                    )

        print(
            "\n================ SUMMARY ================"
        )

        print(
            f"Total valid articles: "
            f"{len(articles)}"
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