# backend/database/connection.py

from sqlalchemy import create_engine

from backend.config.settings import settings


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    echo=False,
)