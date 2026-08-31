"""
Ad-hoc Search Check

Manual script, not part of the automated test suite: it makes
real calls against Azure OpenAI (for the query embedding) and
PostgreSQL/pgvector (for similarity search).

Run:
    python -m scripts.manual.check_sugarcane_search
"""

from backend.services.retrieval_service import (
    RetrievalService,
)


def check_sugarcane_search() -> None:

    service = RetrievalService()

    results = service.search(
        query="Sugarcane news",
        crop="ऊस",
    )

    for result in results:
        print(result["title"])
        print(result["score"])
        print(result["content"][:200])
        print("-" * 80)


if __name__ == "__main__":
    check_sugarcane_search()
