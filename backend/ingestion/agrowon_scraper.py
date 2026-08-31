# backend/ingestion/agrowon_scraper.py
#
# Backward-compatible wrapper preserving the original AgrowonScraper
# API. The actual scraping logic now lives in the config-driven
# AgrowonAdapter (backend/ingestion/adapters/agrowon.py), configured
# from backend/ingestion/configs/agrowon.yaml.

from pathlib import Path

from backend.ingestion.adapters.agrowon import AgrowonAdapter
from backend.ingestion.adapters.config import load_source_config
from backend.ingestion.models import ScrapedArticle

_CONFIG_PATH = Path(__file__).parent / "configs" / "agrowon.yaml"


class AgrowonScraper:
    """
    Agrowon News Scraper
    """

    def __init__(self) -> None:

        config = load_source_config(_CONFIG_PATH)
        self._adapter = AgrowonAdapter(config)

    def collect_article_urls(self) -> list[str]:

        return self._adapter.collect_listing_urls()

    def scrape_article(self, url: str) -> ScrapedArticle | None:

        return self._adapter.scrape_article(url)

    def scrape_articles(self) -> list:

        return self._adapter.scrape_all()


if __name__ == "__main__":

    scraper = AgrowonScraper()

    articles = scraper.scrape_articles()

    print(f"\nTotal articles scraped: {len(articles)}")

    if articles:

        first = articles[0]

        print("\nSample Article")
        print(f"Title: {first.title}")
        print(f"Length: {first.content_length}")
        print(f"URL: {first.url}")
