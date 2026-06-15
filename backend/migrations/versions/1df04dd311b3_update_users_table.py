"""update users table

Revision ID: 1df04dd311b3
Revises: f102dcbe7d1f
Create Date: 2026-06-14 06:24:54.681527

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1df04dd311b3"
down_revision: Union[str, Sequence[str], None] = "f102dcbe7d1f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "full_name",
            sa.String(length=255),
            nullable=False,
            server_default="",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "phone_number",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "preferred_language",
            sa.String(length=20),
            nullable=False,
            server_default="en",
        ),
    )

    op.add_column(
        "users",
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("users", "is_verified")
    op.drop_column("users", "preferred_language")
    op.drop_column("users", "phone_number")
    op.drop_column("users", "full_name")
    op.drop_column("users", "hashed_password")