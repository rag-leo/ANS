from backend.ingestion.models import (
    ScrapedArticle,
)

from backend.ingestion.agrowon_scraper import (
    AgrowonScraper,
)


def test_imports():

    assert ScrapedArticle
    assert AgrowonScraper

    print(
        "✅ Ingestion architecture validation passed"
    )


if __name__ == "__main__":
    test_imports()