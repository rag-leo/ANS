"""
Retrieval Service Check

Manual script, not part of the automated test suite: it makes
real calls against Azure OpenAI (for the query embedding) and
PostgreSQL/pgvector (for similarity search).

Run:
    python -m scripts.manual.check_retrieval_service
"""

from backend.services.retrieval_service import (
    RetrievalService,
)


def check_retrieval_service() -> None:

    service = RetrievalService()

    results = service.search(
        query="banana market price",
        top_k=5,
    )

    print("\nResults:\n")

    for result in results:

        print(
            f"{result['score']:.4f} | "
            f"{result['title']}"
        )

    print(
        "\n✅ Retrieval service check complete"
    )


if __name__ == "__main__":
    check_retrieval_service()
