"""initial PageTurners schema

Revision ID: 0001_initial
Revises:
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    user_role = postgresql.ENUM("student", "admin", name="user_role", create_type=False)
    question_type = postgresql.ENUM("multiple_choice", "true_false", "fill_blank", "multiple_answer", "matching", "short_answer", name="question_type", create_type=False)
    difficulty = postgresql.ENUM("easy", "medium", "hard", name="question_difficulty", create_type=False)
    user_role.create(op.get_bind(), checkfirst=True)
    question_type.create(op.get_bind(), checkfirst=True)
    difficulty.create(op.get_bind(), checkfirst=True)

    op.create_table("academic_levels", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(50), unique=True, nullable=False), sa.Column("order", sa.Integer, unique=True, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("learning_levels", sa.Column("id", sa.String(36), primary_key=True), sa.Column("level", sa.Integer, unique=True, nullable=False), sa.Column("name", sa.String(80), nullable=False), sa.Column("required_correct_answers", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("achievements", sa.Column("id", sa.String(36), primary_key=True), sa.Column("name", sa.String(120), unique=True, nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("criteria_type", sa.String(40), nullable=False, server_default="correct_answers"), sa.Column("threshold", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("users", sa.Column("id", sa.String(36), primary_key=True), sa.Column("full_name", sa.String(160), nullable=False), sa.Column("email", sa.String(255), unique=True, nullable=False), sa.Column("password_hash", sa.String(512), nullable=False), sa.Column("student_id", sa.String(80), unique=True), sa.Column("role", user_role, nullable=False), sa.Column("academic_level_id", sa.String(36), sa.ForeignKey("academic_levels.id"), nullable=False), sa.Column("total_points", sa.Integer, nullable=False, server_default="0"), sa.Column("current_streak", sa.Integer, nullable=False, server_default="0"), sa.Column("questions_answered", sa.Integer, nullable=False, server_default="0"), sa.Column("correct_answers", sa.Integer, nullable=False, server_default="0"), sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_student_id", "users", ["student_id"])
    op.create_table("courses", sa.Column("id", sa.String(36), primary_key=True), sa.Column("code", sa.String(30), unique=True, nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("academic_level_id", sa.String(36), sa.ForeignKey("academic_levels.id"), nullable=False), sa.Column("is_published", sa.Boolean, nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_index("ix_courses_code", "courses", ["code"])
    op.create_table("course_enrollments", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False), sa.Column("progress_percent", sa.Integer, nullable=False, server_default="0"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"))
    op.create_table("topics", sa.Column("id", sa.String(36), primary_key=True), sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("order", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("lessons", sa.Column("id", sa.String(36), primary_key=True), sa.Column("topic_id", sa.String(36), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("content", sa.Text, nullable=False), sa.Column("order", sa.Integer, nullable=False), sa.Column("estimated_minutes", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("questions", sa.Column("id", sa.String(36), primary_key=True), sa.Column("topic_id", sa.String(36), sa.ForeignKey("topics.id", ondelete="CASCADE"), nullable=False), sa.Column("question_text", sa.Text, nullable=False), sa.Column("question_type", question_type, nullable=False), sa.Column("difficulty", difficulty, nullable=False), sa.Column("explanation", sa.Text, nullable=False), sa.Column("points", sa.Integer, nullable=False), sa.Column("correct_answer", sa.String(120), nullable=False), sa.Column("is_published", sa.Boolean, nullable=False, server_default=sa.true()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("question_options", sa.Column("id", sa.String(36), primary_key=True), sa.Column("question_id", sa.String(36), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False), sa.Column("option_key", sa.String(10), nullable=False), sa.Column("text", sa.String(500), nullable=False), sa.Column("order", sa.Integer, nullable=False))
    op.create_table("question_attempts", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("question_id", sa.String(36), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False), sa.Column("selected_answer", sa.String(120), nullable=False), sa.Column("is_correct", sa.Boolean, nullable=False), sa.Column("points_earned", sa.Integer, nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False))
    op.create_table("student_progress", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("course_id", sa.String(36), sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False), sa.Column("lesson_id", sa.String(36), sa.ForeignKey("lessons.id", ondelete="CASCADE")), sa.Column("completed", sa.Boolean, nullable=False, server_default=sa.false()), sa.Column("percent", sa.Integer, nullable=False, server_default="0"), sa.Column("points", sa.Integer, nullable=False, server_default="0"), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("user_id", "course_id", "lesson_id", name="uq_progress_user_course_lesson"))
    op.create_table("student_achievements", sa.Column("id", sa.String(36), primary_key=True), sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("achievement_id", sa.String(36), sa.ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False), sa.Column("awarded_at", sa.DateTime(timezone=True), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False), sa.UniqueConstraint("user_id", "achievement_id", name="uq_student_achievement"))


def downgrade() -> None:
    for table in ["student_achievements", "student_progress", "question_attempts", "question_options", "questions", "lessons", "topics", "course_enrollments", "courses", "users", "achievements", "learning_levels", "academic_levels"]:
        op.drop_table(table)
    postgresql.ENUM(name="question_difficulty").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="question_type").drop(op.get_bind(), checkfirst=True)
    postgresql.ENUM(name="user_role").drop(op.get_bind(), checkfirst=True)
