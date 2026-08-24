import time

from backend.ingestion.agrowon_scraper import (
    AgrowonScraper,
)

from backend.services.ingestion_service import (
    IngestionService,
)


class IngestionPipeline:

    def __init__(self) -> None:

        self.scraper = AgrowonScraper()

    def run(self):

        start_time = time.time()

        articles = self.scraper.scrape_articles()

        enriched_articles = []

        for article in articles:

            enriched_article = (
                IngestionService.enrich_article(
                    article
                )
            )

            enriched_articles.append(
                enriched_article
            )

        duration = round(
            time.time() - start_time,
            2,
        )

        stats = {
            "articles_scraped": len(articles),
            "articles_enriched": len(enriched_articles),
            "duration_seconds": duration,
        }

        print("\n=== INGESTION SUMMARY ===")

        print(
            f"Articles scraped: "
            f"{stats['articles_scraped']}"
        )

        print(
            f"Articles enriched: "
            f"{stats['articles_enriched']}"
        )

        print(
            f"Duration (sec): "
            f"{stats['duration_seconds']}"
        )

        return enriched_articles, stats