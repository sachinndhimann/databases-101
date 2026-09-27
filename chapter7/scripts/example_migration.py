"""
Chapter 7: a worked example of an Alembic revision file, shown here as a
standalone script for reading (a real project would put this under
migrations/versions/ and run it via `alembic upgrade head`).

Scenario: add a `weight_kg` column to `products` using the expand/contract
pattern so it can be deployed with zero downtime.
"""

# --- migrations/versions/0001_add_weight_kg.py -----------------------------
"""add weight_kg to products (expand phase)

Revision ID: 0001
Revises:
Create Date: 2026-01-01
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None


def upgrade():
    # Nullable, no default -> instant metadata-only change on PG 11+/MySQL 8+
    op.add_column("products", sa.Column("weight_kg", sa.Numeric(6, 2), nullable=True))


def downgrade():
    op.drop_column("products", "weight_kg")


# --- migrations/versions/0002_backfill_weight_kg.py ------------------------
"""backfill weight_kg in batches (backfill phase — run as a script, not inline DDL)

Revision ID: 0002
Revises: 0001
"""

revision = "0002"
down_revision = "0001"


def upgrade():
    """
    Real backfills are usually run as a separate maintenance script rather
    than inside the migration itself, so they can be paused/resumed and
    don't hold the migration's own transaction open for a long time.
    See scripts/batched_backfill.py for the runnable version.
    """
    pass


def downgrade():
    pass


# --- migrations/versions/0003_make_weight_kg_not_null.py -------------------
"""contract phase: enforce NOT NULL once backfill is verified complete

Revision ID: 0003
Revises: 0002
"""

revision = "0003"
down_revision = "0002"


def upgrade():
    op.alter_column("products", "weight_kg", nullable=False, server_default="0")


def downgrade():
    op.alter_column("products", "weight_kg", nullable=True, server_default=None)
