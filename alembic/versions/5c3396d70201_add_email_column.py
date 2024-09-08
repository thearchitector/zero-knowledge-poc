"""
This file was autogenerated by Alembic.

Revision ID: 5c3396d70201
Revises: 773d6ac381de
Create Date: 2024-08-30 04:11:22.947251
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '5c3396d70201'
down_revision: str | None = '773d6ac381de'
branch_labels: "str | Sequence[str] | None" = None
depends_on: "str | Sequence[str] | None" = None


def upgrade() -> None:
    """
    add email column
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    pass