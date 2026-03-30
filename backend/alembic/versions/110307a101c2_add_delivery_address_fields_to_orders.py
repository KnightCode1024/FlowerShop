"""add_delivery_address_fields_to_orders

Revision ID: 110307a101c2
Revises: 778fd875c4ec
Create Date: 2026-03-28 16:26:03.932359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '110307a101c2'
down_revision: Union[str, Sequence[str], None] = '778fd875c4ec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "orders",
        sa.Column("recipient_name", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("recipient_phone", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_address", sa.Text(), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_city", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_zip", sa.String(length=20), nullable=True),
    )
    op.add_column(
        "orders",
        sa.Column("delivery_notes", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("orders", "delivery_notes")
    op.drop_column("orders", "delivery_zip")
    op.drop_column("orders", "delivery_city")
    op.drop_column("orders", "delivery_address")
    op.drop_column("orders", "recipient_phone")
    op.drop_column("orders", "recipient_name")
