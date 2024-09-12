"""
This file was autogenerated by Alembic.

Revision ID: e6d231a89924
Revises: 2a6411bd2710
Create Date: 2024-09-10 03:20:27.205797
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'e6d231a89924'
down_revision: str | None = '2a6411bd2710'
branch_labels: "str | Sequence[str] | None" = None
depends_on: "str | Sequence[str] | None" = None


def upgrade() -> None:
    """
    nullable group host
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('groups', 'host_user_id',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    pass