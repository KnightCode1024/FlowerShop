"""update_quantity_default_and_sync_in_stock

Revision ID: 778fd875c4ec
Revises: f1bb2dd55b3f
Create Date: 2026-03-28 15:21:18.627245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '778fd875c4ec'
down_revision: Union[str, Sequence[str], None] = 'f1bb2dd55b3f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        UPDATE products
        SET quantity = 0
        WHERE in_stock = false AND quantity IS NULL
    """)
    
    op.execute("""
        UPDATE products
        SET in_stock = false
        WHERE quantity = 0 AND in_stock = true
    """)


def downgrade() -> None:
    """Downgrade schema."""
    pass
