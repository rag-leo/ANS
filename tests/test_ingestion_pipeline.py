from backend.ingestion.pipeline import (
    IngestionPipeline,
)


def test_pipeline():

    pipeline = IngestionPipeline()

    articles = pipeline.run()

    assert articles

    print(
        f"\n✅ Pipeline processed "
        f"{len(articles)} articles"
    )


if __name__ == "__main__":
    test_pipeline()