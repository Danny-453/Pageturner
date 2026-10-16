"""add student nicknames and generated quiz source lessons

Revision ID: 0004_nicknames_and_lesson_quizzes
Revises: 0003_lesson_video_url
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_nicknames_and_lesson_quizzes"
down_revision = "0003_lesson_video_url"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("nickname", sa.String(length=40), nullable=True))
    op.add_column("questions", sa.Column("source_lesson_id", sa.String(length=36), nullable=True))
    op.create_foreign_key(
        "fk_questions_source_lesson_id_lessons",
        "questions",
        "lessons",
        ["source_lesson_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_questions_source_lesson_id",
        "questions",
        ["source_lesson_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_questions_source_lesson_id", table_name="questions")
    op.drop_constraint("fk_questions_source_lesson_id_lessons", "questions", type_="foreignkey")
    op.drop_column("questions", "source_lesson_id")
    op.drop_column("users", "nickname")
