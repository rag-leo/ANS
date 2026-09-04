"""articles published_datetime updated_datetime timestamptz

Converts articles.published_datetime and articles.updated_datetime from
naive `timestamp` to `timestamptz`, so timezone-aware datetimes written
by the ingestion adapters (see backend/ingestion/adapters/base.py,
ScraperAdapter._parse_date) survive round-tripping through the DB
instead of silently losing their offset on write.

Every existing row predates the multi-source adapter refactor, so every
existing row is Agrowon, an IST-based source. The `AT TIME ZONE
'Asia/Kolkata'` USING clause below backfills in the same statement as
the type change: it reinterprets each existing naive value as IST wall
clock time and converts it to the equivalent UTC instant that
timestamptz stores, rather than requiring a separate backfill pass.

Revision ID: 8de957629529
Revises: b20794795771
Create Date: 2026-08-31 17:11:33.488847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8de957629529'
down_revision: Union[str, Sequence[str], None] = 'b20794795771'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

_BACKFILL_TIMEZONE = "Asia/Kolkata"


def upgrade() -> None:
    """Upgrade schema."""

    op.alter_column(
        "articles",
        "published_datetime",
        type_=sa.DateTime(timezone=True),
        postgresql_using=(
            f"published_datetime AT TIME ZONE '{_BACKFILL_TIMEZONE}'"
        ),
    )

    op.alter_column(
        "articles",
        "updated_datetime",
        type_=sa.DateTime(timezone=True),
        postgresql_using=(
            f"updated_datetime AT TIME ZONE '{_BACKFILL_TIMEZONE}'"
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.alter_column(
        "articles",
        "published_datetime",
        type_=sa.DateTime(timezone=False),
        postgresql_using=(
            f"published_datetime AT TIME ZONE '{_BACKFILL_TIMEZONE}'"
        ),
    )

    op.alter_column(
        "articles",
        "updated_datetime",
        type_=sa.DateTime(timezone=False),
        postgresql_using=(
            f"updated_datetime AT TIME ZONE '{_BACKFILL_TIMEZONE}'"
        ),
    )
