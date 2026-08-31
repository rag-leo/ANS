"""
Embedding Generation Check

Manual script, not part of the automated test suite: it makes a
real call against Azure OpenAI and needs valid credentials in .env.

Run:
    python -m scripts.manual.check_embeddings
"""

from backend.services.embedding_service import (
    EmbeddingService,
)


def check_embeddings() -> None:

    service = EmbeddingService()

    embedding = (
        service.generate_embedding(
            "Banana prices increased in Maharashtra."
        )
    )

    print(
        f"Embedding Length: "
        f"{len(embedding)}"
    )

    print(
        f"First 5 values: "
        f"{embedding[:5]}"
    )

    assert len(embedding) == 1536

    print(
        "✅ Embedding generation passed"
    )


if __name__ == "__main__":
    check_embeddings()
