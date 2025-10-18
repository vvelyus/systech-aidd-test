"""Optimize chat database with indexes and SQLite WAL mode.

Revision ID: optimize_001
Revises: 798d96052738
Create Date: 2025-10-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'optimize_001'
down_revision = '798d96052738'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create indexes for better query performance."""
    # Create indexes on chat_messages table
    op.create_index(
        'idx_chat_messages_user_session_id',
        'chat_messages',
        ['user_session_id'],
        if_not_exists=True
    )

    op.create_index(
        'idx_chat_messages_created_at',
        'chat_messages',
        ['created_at'],
        if_not_exists=True
    )

    op.create_index(
        'idx_chat_messages_session_created',
        'chat_messages',
        ['user_session_id', 'created_at'],
        if_not_exists=True
    )

    # Create indexes on chat_sessions table
    op.create_index(
        'idx_chat_sessions_user_id',
        'chat_sessions',
        ['user_id'],
        if_not_exists=True
    )

    op.create_index(
        'idx_chat_sessions_created_at',
        'chat_sessions',
        ['created_at'],
        if_not_exists=True
    )


def downgrade() -> None:
    """Drop indexes."""
    op.drop_index('idx_chat_sessions_created_at', if_exists=True)
    op.drop_index('idx_chat_sessions_user_id', if_exists=True)
    op.drop_index('idx_chat_messages_session_created', if_exists=True)
    op.drop_index('idx_chat_messages_created_at', if_exists=True)
    op.drop_index('idx_chat_messages_user_session_id', if_exists=True)
