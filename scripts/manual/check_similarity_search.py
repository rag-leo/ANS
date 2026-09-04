"""
Ad-hoc Similarity Ranking Check

Manual script, not part of the automated test suite: it makes
real calls against Azure OpenAI to embed a query and a small set
of in-memory documents, then ranks them by cosine similarity.
Useful for eyeballing embedding quality without touching the DB.

Run:
    python -m scripts.manual.check_similarity_search
"""

from sklearn.metrics.pairwise import cosine_similarity

from backend.services.embedding_service import (
    EmbeddingService,
)


def check_similarity() -> None:

    service = EmbeddingService()

    query = (
        "banana market price"
    )

    documents = [

        "Banana prices increased in Maharashtra.",

        "Cotton arrivals have improved this week.",

        "Heavy rainfall expected in Konkan.",

        "Banana exports are expected to rise.",

    ]

    query_embedding = (
        service.generate_embedding(
            query
        )
    )

    document_embeddings = [

        service.generate_embedding(
            doc
        )

        for doc in documents

    ]

    scores = cosine_similarity(
        [query_embedding],
        document_embeddings,
    )[0]

    results = sorted(
        zip(documents, scores),
        key=lambda x: x[1],
        reverse=True,
    )

    print("\nSimilarity Rankings:\n")

    for doc, score in results:

        print(
            f"{score:.4f} | {doc}"
        )


if __name__ == "__main__":
    check_similarity()
