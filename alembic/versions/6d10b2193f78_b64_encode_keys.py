"""
This file was autogenerated by Alembic.

Revision ID: 6d10b2193f78
Revises: 50f8c42254d9
Create Date: 2024-09-08 02:06:06.512459
"""

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6d10b2193f78'
down_revision: str | None = '50f8c42254d9'
branch_labels: "str | Sequence[str] | None" = None
depends_on: "str | Sequence[str] | None" = None


def upgrade() -> None:
    """
    b64 encode keys
    """
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('groupings', 'encryption_key',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('groupings', 'encryption_key_nonce',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('items', 'content_nonce',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('sharings', 'encryption_key',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('sharings', 'encryption_key_nonce',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(),
               existing_nullable=False)
    op.alter_column('users', 'encryption_key',
               existing_type=postgresql.BYTEA(),
               type_=sa.String(),
               existing_nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    pass