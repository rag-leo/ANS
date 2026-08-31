"""
PostgreSQL Connectivity Check

Manual script, not part of the automated test suite: it opens a
real connection using the configured database_url.

Run:
    python -m scripts.manual.check_postgres_connection
"""

from sqlalchemy import create_engine, text

from backend.config.settings import settings


def check_postgres_connection() -> None:

    engine = create_engine(
        settings.database_url,
        pool_pre_ping=True,
    )

    with engine.connect() as conn:
        result = conn.execute(text("SELECT version();"))
        print(result.fetchone())


if __name__ == "__main__":
    check_postgres_connection()
