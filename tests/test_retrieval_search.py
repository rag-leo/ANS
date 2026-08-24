from backend.retrieval.search import (
    SemanticSearch,
)


def test_search():

    query = "banana market rates"

    documents = [

        "Banana prices increased in Maharashtra.",

        "Heavy rainfall expected in Konkan.",

        "Cotton arrivals improved this week.",

        "Banana exports are expected to rise.",
    ]

    search = SemanticSearch()

    results = search.search(
        query=query,
        documents=documents,
    )

    print("\nResults:\n")

    for result in results:

        print(
            f"{result.score:.4f} | "
            f"{result.content}"
        )


if __name__ == "__main__":
    test_search()
