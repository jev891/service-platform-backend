"""Create users table

Revision ID: 39b1e58a0404
Revises: 
Create Date: 2024-11-30 22:17:48.321967
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# Revision identifiers, used by Alembic.
revision: str = '39b1e58a0404'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """
    Upgrade the database to this revision.
    Creates the 'users' table with the following columns:
        - id: Primary key
        - email: Unique and indexed
        - hashed_password: Stores the user's hashed password
        - role: Default value is 'client'
        - created_at: Timestamp when the user was created
        - updated_at: Timestamp when the user record was last updated
    """
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True, nullable=False),
        sa.Column('email', sa.String(255), unique=True, nullable=False, index=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, server_default='client'),
        sa.Column('created_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('NOW()')),
    )


def downgrade():
    """
    Downgrade the database by dropping the 'users' table.
    """
    op.drop_table('users')
