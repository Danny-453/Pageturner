"""remove student nicknames

Revision ID: 0005_remove_nickname
Revises: 0004_lesson_quizzes
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_remove_nickname"
down_revision = "0004_lesson_quizzes"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_column("users", "nickname")


def downgrade() -> None:
    op.add_column("users", sa.Column("nickname", sa.String(length=40), nullable=True))
