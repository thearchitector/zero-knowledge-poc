"""
This file was autogenerated by Alembic.

Revision ID: b3631510525c
Revises: 8e0bf8a511d4
Create Date: 2024-08-28 05:10:40.846293
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b3631510525c"
down_revision: str | None = "8e0bf8a511d4"
branch_labels: "str | Sequence[str] | None" = None
depends_on: "str | Sequence[str] | None" = None


def upgrade() -> None:
    """
    add keys
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "groupings", sa.Column("group_encryption_key", sa.LargeBinary(), nullable=False)
    )
    op.drop_index("ix_groupings_id", table_name="groupings")
    op.drop_index("ix_groups_id", table_name="groups")
    op.drop_index("ix_items_id", table_name="items")
    op.add_column(
        "sharings", sa.Column("item_encryption_key", sa.LargeBinary(), nullable=False)
    )
    op.drop_index("ix_sharings_id", table_name="sharings")
    op.drop_index("ix_users_id", table_name="users")
    # ### end Alembic commands ###


def downgrade() -> None:
    pass
