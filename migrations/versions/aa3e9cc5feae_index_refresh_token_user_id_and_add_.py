"""index refresh token user id and add cascade

Revision ID: aa3e9cc5feae
Revises: 1fe680399853
Create Date: 2026-08-28 12:56:21.743330
"""

from collections.abc import Sequence

from alembic import op

revision: str = "aa3e9cc5feae"
down_revision: str | Sequence[str] | None = "1fe680399853"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_index(
        op.f("ix_refresh_tokens_user_id"),
        "refresh_tokens",
        ["user_id"],
        unique=False,
    )

    op.drop_constraint(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "refresh_tokens_user_id_fkey",
        "refresh_tokens",
        "users",
        ["user_id"],
        ["id"],
    )

    op.drop_index(
        op.f("ix_refresh_tokens_user_id"),
        table_name="refresh_tokens",
    )
