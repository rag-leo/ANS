# backend/database/session.py

from collections.abc import Generator

from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from backend.database.connection import engine


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency.

    Example:

        @router.get("/")
        async def get_items(
            db: Session = Depends(get_db)
        ):
            ...
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()