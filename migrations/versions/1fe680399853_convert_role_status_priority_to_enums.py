"""convert role status priority to enums

Revision ID: 1fe680399853
Revises: 93dea0665de4
Create Date: 2026-08-25 16:14:35.779623

"""

from collections.abc import Sequence

from alembic import op

revision: str = "1fe680399853"
down_revision: str | Sequence[str] | None = "93dea0665de4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Convert role, status, and priority to PostgreSQL enums."""

    # The existing role_name type contains ADMIN/USER.
    # Rename it temporarily so we can create the new type
    # with the API values: admin/user.
    op.execute(
        "ALTER TYPE role_name RENAME TO role_name_old",
    )

    op.execute(
        """
        CREATE TYPE role_name AS ENUM (
            'admin',
            'user'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role
        TYPE role_name
        USING lower(role::text)::role_name
        """
    )

    op.execute(
        "DROP TYPE role_name_old",
    )

    # Create task status enum.
    op.execute(
        """
        CREATE TYPE task_status AS ENUM (
            'Todo',
            'In Progress',
            'Done'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status
        TYPE task_status
        USING status::text::task_status
        """
    )

    # Create task priority enum.
    op.execute(
        """
        CREATE TYPE task_priority AS ENUM (
            'Low',
            'Medium',
            'High'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN priority
        TYPE task_priority
        USING priority::text::task_priority
        """
    )


def downgrade() -> None:
    """Convert PostgreSQL enums back to VARCHAR."""

    # Convert task priority back to VARCHAR.
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN priority
        TYPE VARCHAR(20)
        USING priority::text
        """
    )

    op.execute(
        "DROP TYPE task_priority",
    )

    # Convert task status back to VARCHAR.
    op.execute(
        """
        ALTER TABLE tasks
        ALTER COLUMN status
        TYPE VARCHAR(20)
        USING status::text
        """
    )

    op.execute(
        "DROP TYPE task_status",
    )

    # Convert role back to VARCHAR first.
    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role
        TYPE VARCHAR(20)
        USING role::text
        """
    )

    # Recreate the original enum definition used by the
    # previous migration.
    op.execute(
        """
        CREATE TYPE role_name_old AS ENUM (
            'ADMIN',
            'USER'
        )
        """
    )

    op.execute(
        """
        ALTER TABLE users
        ALTER COLUMN role
        TYPE role_name_old
        USING upper(role)::role_name_old
        """
    )

    op.execute(
        "DROP TYPE role_name",
    )

    op.execute(
        "ALTER TYPE role_name_old RENAME TO role_name",
    )
