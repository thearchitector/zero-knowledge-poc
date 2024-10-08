"""
This file was autogenerated by Alembic.

Revision ID: 773d6ac381de
Revises: b3e0e6211624
Create Date: 2024-08-30 03:17:00.701944
"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '773d6ac381de'
down_revision: str | None = 'b3e0e6211624'
branch_labels: "str | Sequence[str] | None" = None
depends_on: "str | Sequence[str] | None" = None


def upgrade() -> None:
    """
    add nonces
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('items', sa.Column('content_nonce', sa.LargeBinary(), nullable=False))
    op.add_column('sharings', sa.Column('encryption_key_nonce', sa.LargeBinary(), nullable=False))
    # ### end Alembic commands ###


def downgrade() -> None:
    pass