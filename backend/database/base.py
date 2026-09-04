# backend/database/base.py

from datetime import datetime, timezone

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all ANIS ORM models.
    """
    pass


def utcnow() -> datetime:
    """
    Naive UTC timestamp for use with non-timezone-aware
    DateTime columns.

    `datetime.utcnow()` is deprecated; this produces an
    equivalent naive UTC value without relying on it.
    """

    return datetime.now(timezone.utc).replace(tzinfo=None)
