"""make user token unique

Revision ID: 3d4e5f6a7b8c
Revises: 2c3d4e5f6a7b
Create Date: 2026-03-27 17:40:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "3d4e5f6a7b8c"
down_revision: Union[str, Sequence[str], None] = "2c3d4e5f6a7b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # If some users already share the same token (bug: uuid.uuid4() evaluated once),
    # keep the newest row's token and NULL-out the rest.
    op.execute(
        """
        WITH dup AS (
            SELECT token
            FROM users
            WHERE token IS NOT NULL
            GROUP BY token
            HAVING COUNT(*) > 1
        ),
        keep AS (
            SELECT MAX(id) AS id
            FROM users
            WHERE token IN (SELECT token FROM dup)
            GROUP BY token
        )
        UPDATE users
        SET token = NULL
        WHERE token IN (SELECT token FROM dup)
          AND id NOT IN (SELECT id FROM keep);
        """
    )

    # Unique for non-null tokens only.
    op.create_index(
        "uq_users_token_not_null",
        "users",
        ["token"],
        unique=True,
        postgresql_where=sa.text("token IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_index("uq_users_token_not_null", table_name="users")

