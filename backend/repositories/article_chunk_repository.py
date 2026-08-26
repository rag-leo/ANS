from sqlalchemy import text

from backend.database.models import (
    ArticleChunk,
)

from backend.database.session import (
    SessionLocal,
)


class ArticleChunkRepository:

    def save_chunks(
        self,
        article_id: int,
        chunks: list[dict],
    ):

        with SessionLocal() as session:

            db_chunks = []

            for chunk in chunks:

                db_chunk = (
                    ArticleChunk(
                        article_id=article_id,
                        chunk_id=chunk["chunk_id"],
                        content=chunk["content"],
                        embedding=chunk["embedding"],
                    )
                )

                db_chunks.append(db_chunk)

            session.add_all(db_chunks)

            session.commit()

    def search_similar(
        self,
        query_embedding,
        crop=None,
        category=None,
        source=None,
        generation_type=None,
        max_age_days=None,
        top_k=5,
    ):

        with SessionLocal() as session:

            sql = text(
                """
                SELECT
                    ac.id,
                    ac.chunk_id,
                    ac.content,
                    a.id AS article_id,
                    a.title,
                    a.url,
                    a.crop,
                    a.category,
                    a.source,
                    ac.embedding <=> CAST(:embedding AS vector)
                        AS distance

                FROM article_chunks ac

                JOIN articles a
                    ON a.id = ac.article_id

                WHERE
                    (
                        :crop IS NULL
                        OR a.crop ILIKE '%' || :crop || '%'
                    )
                AND
                    (
                        :category IS NULL
                        OR a.category = :category
                    )
                AND
                    (
                        :source IS NULL
                        OR a.source = :source
                    )                    
                    
                AND
                (
                    :max_age_days IS NULL

                    OR

                    a.scrape_date >=
                    CURRENT_DATE -
                    (:max_age_days * INTERVAL '1 day')
                )

                AND a.id NOT IN (

                    SELECT article_id

                    FROM notification_history

                    WHERE generation_type =
                        :generation_type

                    AND is_published = TRUE

                )                
                                        
                ORDER BY ac.embedding <=> CAST(:embedding AS vector)

                LIMIT :top_k
                """
            )

            print(f"CROP = {crop}")
            print(f"CATEGORY = {category}")
            print(f"SOURCE = {source}")
            print(f"MAX_AGE_DAYS = {max_age_days}")
            print(f"TOP_K = {top_k}")

            results = (
                session.execute(
                    sql,
                    {
                        "embedding": str(query_embedding),
                        "crop": crop,
                        "category": category,
                        "source": source,
                        "max_age_days": max_age_days,                        
                        "generation_type": generation_type,
                        "top_k": top_k,
                    },
                )
                .mappings()
                .all()
            )

            print(f"Rows returned: {len(results)}")

            for row in results:
                print(
                    f"{row['title']} | Crop={row['crop']}"
                )            

from sqlalchemy import text

from backend.database.models import (
    ArticleChunk,
)

from backend.database.session import (
    SessionLocal,
)


class ArticleChunkRepository:

    def save_chunks(
        self,
        article_id: int,
        chunks: list[dict],
    ):

        with SessionLocal() as session:

            db_chunks = []

            for chunk in chunks:

                db_chunk = (
                    ArticleChunk(
                        article_id=article_id,
                        chunk_id=chunk["chunk_id"],
                        content=chunk["content"],
                        embedding=chunk["embedding"],
                    )
                )

                db_chunks.append(db_chunk)

            session.add_all(db_chunks)

            session.commit()

    def search_similar(
        self,
        query_embedding,
        crop=None,
        category=None,
        source=None,
        generation_type=None,
        max_age_days=None,
        top_k=5,
    ):

        with SessionLocal() as session:

            sql = text(
                """
                SELECT
                    ac.id,
                    ac.chunk_id,
                    ac.content,
                    a.id AS article_id,
                    a.title,
                    a.url,
                    a.crop,
                    a.category,
                    a.source,
                    ac.embedding <=> CAST(:embedding AS vector)
                        AS distance

                FROM article_chunks ac

                JOIN articles a
                    ON a.id = ac.article_id

                WHERE
                    (
                        :crop IS NULL
                        OR a.crop ILIKE '%' || :crop || '%'
                    )
                AND
                    (
                        :category IS NULL
                        OR a.category = :category
                    )
                AND
                    (
                        :source IS NULL
                        OR a.source = :source
                    )                    
                    
                AND
                (
                    :max_age_days IS NULL

                    OR

                    a.scrape_date >=
                    CURRENT_DATE -
                    (:max_age_days * INTERVAL '1 day')
                )

                AND a.id NOT IN (

                    SELECT article_id

                    FROM notification_history

                    WHERE generation_type =
                        :generation_type

                    AND is_published = TRUE

                )                
                                        
                ORDER BY ac.embedding <=> CAST(:embedding AS vector)

                LIMIT :top_k
                """
            )

            print(f"CROP = {crop}")
            print(f"CATEGORY = {category}")
            print(f"SOURCE = {source}")
            print(f"MAX_AGE_DAYS = {max_age_days}")
            print(f"TOP_K = {top_k}")

            results = (
                session.execute(
                    sql,
                    {
                        "embedding": str(query_embedding),
                        "crop": crop,
                        "category": category,
                        "source": source,
                        "max_age_days": max_age_days,                        
                        "generation_type": generation_type,
                        "top_k": top_k,
                    },
                )
                .mappings()
                .all()
            )

            for row in results:
                print(
                    f"{row['title']} | "
                    f"Crop={row['crop']} | "
                    f"Score={round(1 - row['distance'], 4)}"
                )          

            MIN_SIMILARITY_SCORE = 0.10

            processed_results = [
                {
                    "article_id": row["article_id"],
                    "title": row["title"],
                    "url": row["url"],
                    "crop": row["crop"],
                    "category": row["category"],
                    "source": row["source"],
                    "chunk_id": row["chunk_id"],
                    "content": row["content"],
                    "score": round(
                        1 - row["distance"],
                        4
                    ),
                }
                for row in results
            ]

            # Apply similarity threshold
            processed_results = [
                result
                for result in processed_results
                if result["score"]
                >= MIN_SIMILARITY_SCORE
            ]

            # Keep only the highest-scoring chunk
            # for each article
            unique_articles = {}

            for article in processed_results:

                article_id = article["article_id"]

                if (
                    article_id not in unique_articles
                    or
                    article["score"]
                    >
                    unique_articles[
                        article_id
                    ]["score"]
                ):

                    unique_articles[
                        article_id
                    ] = article

            final_results = list(
                unique_articles.values()
            )

            print(
                f"After threshold and deduplication: "
                f"{len(final_results)} articles"
            )

            return final_results