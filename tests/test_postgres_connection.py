# tests/test_postgres_connection.py

from sqlalchemy import create_engine, text

from backend.config.settings import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True
)

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print(result.fetchone())