from backend.services.embedding_service import (
    EmbeddingService,
)


def test_embeddings():

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
    test_embeddings()