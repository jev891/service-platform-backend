"""Initial migration

Revision ID: 19bd9d4a8a44
Revises: 
Create Date: 2024-12-05 12:46:36.340423

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '19bd9d4a8a44'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Upgrade migration logic."""
    # Drop requests first to handle dependency on users
    op.drop_table('requests')  # Foreign key dependency on users handled

    # Drop users with CASCADE to ensure no dependency issues
    op.execute("DROP TABLE users CASCADE")


def downgrade() -> None:
    """Downgrade migration logic."""
    # Recreate users table
    op.create_table('users',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('email', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('hashed_password', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('role', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('mobile_number', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('name', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('company_name', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='users_pkey'),
        sa.UniqueConstraint('email', name='users_email_key'),
        sa.UniqueConstraint('mobile_number', name='users_mobile_number_key')
    )
    op.create_index('ix_users_id', 'users', ['id'], unique=False)

    # Recreate requests table
    op.create_table('requests',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column('title', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('description', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('status', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('budget', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('category', sa.VARCHAR(), autoincrement=False, nullable=False),
        sa.Column('approximate_time_required', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('help_day', sa.VARCHAR(), autoincrement=False, nullable=True),
        sa.Column('preferred_time', postgresql.TIME(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='requests_user_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='requests_pkey')
    )
    op.create_index('ix_requests_title', 'requests', ['title'], unique=False)
    op.create_index('ix_requests_id', 'requests', ['id'], unique=False)
