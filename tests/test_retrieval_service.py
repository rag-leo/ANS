from backend.services.retrieval_service import (
    RetrievalService,
)


def test_retrieval_service():

    service = RetrievalService()

    results = service.search(
        query="banana market price",
        documents=[
            "Banana prices increased in Maharashtra.",
            "Cotton arrivals improved this week.",
            "Heavy rainfall expected in Konkan.",
            "Banana exports are expected to rise.",
        ],
    )

    print("\nResults:\n")

    for result in results:

        print(
            f"{result.score:.4f} | "
            f"{result.content}"
        )

    print(
        "\n✅ Retrieval service passed"
    )


if __name__ == "__main__":
    test_retrieval_service()