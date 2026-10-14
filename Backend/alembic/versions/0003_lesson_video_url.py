"""add optional video URLs to lessons

Revision ID: 0003_lesson_video_url
Revises: 0002_password_reset_tokens
"""
from alembic import op
import sqlalchemy as sa

revision = "0003_lesson_video_url"
down_revision = "0002_password_reset_tokens"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("lessons", sa.Column("video_url", sa.String(length=2048), nullable=True))


def downgrade() -> None:
    op.drop_column("lessons", "video_url")
