from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum as SAEnum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.enums import Difficulty, QuestionType, UserRole


def new_id() -> str:
    return str(uuid4())


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False)


class AcademicLevel(TimestampMixin, Base):
    __tablename__ = "academic_levels"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    order: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    users: Mapped[list["User"]] = relationship(back_populates="academic_level")


class LearningLevel(TimestampMixin, Base):
    __tablename__ = "learning_levels"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    level: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(80), nullable=False)
    required_correct_answers: Mapped[int] = mapped_column(Integer, nullable=False)


class User(TimestampMixin, Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    full_name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(512), nullable=False)
    student_id: Mapped[str | None] = mapped_column(String(80), unique=True, index=True)
    role: Mapped[UserRole] = mapped_column(SAEnum(UserRole, name="user_role"), default=UserRole.student, nullable=False)
    academic_level_id: Mapped[str] = mapped_column(ForeignKey("academic_levels.id"), nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    current_streak: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    questions_answered: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    correct_answers: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    academic_level: Mapped[AcademicLevel] = relationship(back_populates="users")
    enrollments: Mapped[list["CourseEnrollment"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    attempts: Mapped[list["QuestionAttempt"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    progress: Mapped[list["StudentProgress"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    achievements: Mapped[list["StudentAchievement"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token_hash: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped[User] = relationship()


class Course(TimestampMixin, Base):
    __tablename__ = "courses"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    academic_level_id: Mapped[str] = mapped_column(ForeignKey("academic_levels.id"), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topics: Mapped[list["Topic"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    enrollments: Mapped[list["CourseEnrollment"]] = relationship(back_populates="course", cascade="all, delete-orphan")
    progress: Mapped[list["StudentProgress"]] = relationship(back_populates="course", cascade="all, delete-orphan")


class CourseEnrollment(TimestampMixin, Base):
    __tablename__ = "course_enrollments"
    __table_args__ = (UniqueConstraint("user_id", "course_id", name="uq_enrollment_user_course"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    progress_percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped[User] = relationship(back_populates="enrollments")
    course: Mapped[Course] = relationship(back_populates="enrollments")


class Topic(TimestampMixin, Base):
    __tablename__ = "topics"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    course: Mapped[Course] = relationship(back_populates="topics")
    lessons: Mapped[list["Lesson"]] = relationship(back_populates="topic", cascade="all, delete-orphan")
    questions: Mapped[list["Question"]] = relationship(back_populates="topic", cascade="all, delete-orphan")


class Lesson(TimestampMixin, Base):
    __tablename__ = "lessons"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    video_url: Mapped[str | None] = mapped_column(String(2048), nullable=True)
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(Integer, default=15, nullable=False)

    topic: Mapped[Topic] = relationship(back_populates="lessons")


class Question(TimestampMixin, Base):
    __tablename__ = "questions"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    topic_id: Mapped[str] = mapped_column(ForeignKey("topics.id", ondelete="CASCADE"), nullable=False)
    source_lesson_id: Mapped[str | None] = mapped_column(ForeignKey("lessons.id", ondelete="SET NULL"))
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    question_type: Mapped[QuestionType] = mapped_column(SAEnum(QuestionType, name="question_type"), default=QuestionType.multiple_choice, nullable=False)
    difficulty: Mapped[Difficulty] = mapped_column(SAEnum(Difficulty, name="question_difficulty"), default=Difficulty.medium, nullable=False)
    explanation: Mapped[str] = mapped_column(Text, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=10, nullable=False)
    correct_answer: Mapped[str] = mapped_column(String(120), nullable=False)
    is_published: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    topic: Mapped[Topic] = relationship(back_populates="questions")
    options: Mapped[list["QuestionOption"]] = relationship(back_populates="question", cascade="all, delete-orphan", order_by="QuestionOption.order")
    attempts: Mapped[list["QuestionAttempt"]] = relationship(back_populates="question", cascade="all, delete-orphan")


class QuestionOption(Base):
    __tablename__ = "question_options"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    option_key: Mapped[str] = mapped_column(String(10), nullable=False)
    text: Mapped[str] = mapped_column(String(500), nullable=False)
    order: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    question: Mapped[Question] = relationship(back_populates="options")


class QuestionAttempt(TimestampMixin, Base):
    __tablename__ = "question_attempts"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    selected_answer: Mapped[str] = mapped_column(String(120), nullable=False)
    is_correct: Mapped[bool] = mapped_column(Boolean, nullable=False)
    points_earned: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped[User] = relationship(back_populates="attempts")
    question: Mapped[Question] = relationship(back_populates="attempts")


class StudentProgress(TimestampMixin, Base):
    __tablename__ = "student_progress"
    __table_args__ = (UniqueConstraint("user_id", "course_id", "lesson_id", name="uq_progress_user_course_lesson"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    course_id: Mapped[str] = mapped_column(ForeignKey("courses.id", ondelete="CASCADE"), nullable=False)
    lesson_id: Mapped[str | None] = mapped_column(ForeignKey("lessons.id", ondelete="CASCADE"))
    completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    percent: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    points: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped[User] = relationship(back_populates="progress")
    course: Mapped[Course] = relationship(back_populates="progress")


class Achievement(TimestampMixin, Base):
    __tablename__ = "achievements"
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    criteria_type: Mapped[str] = mapped_column(String(40), default="correct_answers", nullable=False)
    threshold: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    students: Mapped[list["StudentAchievement"]] = relationship(back_populates="achievement", cascade="all, delete-orphan")


class StudentAchievement(TimestampMixin, Base):
    __tablename__ = "student_achievements"
    __table_args__ = (UniqueConstraint("user_id", "achievement_id", name="uq_student_achievement"),)
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    achievement_id: Mapped[str] = mapped_column(ForeignKey("achievements.id", ondelete="CASCADE"), nullable=False)
    awarded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="achievements")
    achievement: Mapped[Achievement] = relationship(back_populates="students")
