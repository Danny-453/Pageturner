import os
from sqlalchemy import select

from app.core.config import settings
from app.core.security import hash_password
from app.db.session import get_session_factory
from app.models import AcademicLevel, Achievement, Course, LearningLevel, Lesson, Question, QuestionOption, Topic, User
from app.models.enums import Difficulty, QuestionType, UserRole


def seed() -> None:
    admin_password = settings.seed_admin_password or os.getenv("SEED_ADMIN_PASSWORD")
    student_password = settings.seed_student_password or os.getenv("SEED_STUDENT_PASSWORD")

    db = get_session_factory()()
    try:
        levels = []
        for index, name in enumerate(["100 Level", "200 Level", "300 Level", "400 Level", "500 Level"], start=1):
            item = db.scalar(select(AcademicLevel).where(AcademicLevel.name == name))
            if not item:
                item = AcademicLevel(name=name, order=index); db.add(item); db.flush()
            levels.append(item)

        learning = [(1,"Beginner",0),(2,"Explorer",10),(3,"Learner",20),(4,"Scholar",35),(5,"Advanced Scholar",50),(6,"Expert",75),(7,"Master",100)]
        for level, name, threshold in learning:
            if not db.scalar(select(LearningLevel).where(LearningLevel.level == level)):
                db.add(LearningLevel(level=level, name=name, required_correct_answers=threshold))

        achievement_data = [("First Steps","Answer your first question.","correct_answers",1),("Getting Started","Answer 25 questions correctly.","correct_answers",25),("Dedicated Learner","Complete your first course.","courses_completed",1),("Accuracy Master","Achieve 90% accuracy.","accuracy",90),("Rising Scholar","Reach Learning Level 5.","learning_level",5)]
        for name, description, criteria_type, threshold in achievement_data:
            if not db.scalar(select(Achievement).where(Achievement.name == name)):
                db.add(Achievement(name=name, description=description, criteria_type=criteria_type, threshold=threshold))

        course = db.scalar(select(Course).where(Course.code == "AGP-301"))
        if not course:
            course = Course(code="AGP-301", title="Geophysical Methods", description="Introduction to major geophysical exploration methods, acquisition and interpretation.", academic_level_id=levels[2].id)
            db.add(course); db.flush()
            topic = Topic(course_id=course.id, title="Seismic Methods", description="Fundamentals of seismic reflection and refraction.", order=1)
            db.add(topic); db.flush()
            lesson = Lesson(topic_id=topic.id, title="Introduction to Seismic Reflection", content="Seismic reflection uses contrasts in subsurface acoustic impedance to identify interfaces and geological structures. Field data are acquired with controlled sources and receivers, then processed and interpreted.", order=1, estimated_minutes=20)
            db.add(lesson); db.flush()
            question = Question(topic_id=topic.id, question_text="What is a primary purpose of seismic reflection?", question_type=QuestionType.multiple_choice, difficulty=Difficulty.medium, explanation="Seismic reflection is used to image subsurface interfaces by recording reflected seismic energy.", points=10, correct_answer="b")
            db.add(question); db.flush()
            db.add_all([
                QuestionOption(question_id=question.id, option_key="a", text="Measure only surface temperature", order=1),
                QuestionOption(question_id=question.id, option_key="b", text="Image subsurface geological interfaces", order=2),
                QuestionOption(question_id=question.id, option_key="c", text="Determine atmospheric pressure", order=3),
                QuestionOption(question_id=question.id, option_key="d", text="Measure river discharge", order=4),
            ])

        if admin_password and student_password:
            seed_users = [
                (settings.seed_admin_email, "admin@pageturners.local", "PageTurners Administrator", admin_password, None, UserRole.admin, levels[4].id),
                (settings.seed_student_email, "student@pageturners.local", "Demo Geology Student", student_password, "PT-DEMO-001", UserRole.student, levels[2].id),
            ]
            for email, legacy_email, full_name, password, student_id, role, level_id in seed_users:
                user = db.scalar(select(User).where(User.email == email))
                if user:
                    continue
                user = db.scalar(select(User).where(User.email == legacy_email, User.role == role))
                if user:
                    user.email = email
                else:
                    db.add(User(
                        full_name=full_name,
                        email=email,
                        password_hash=hash_password(password),
                        student_id=student_id,
                        role=role,
                        academic_level_id=level_id,
                    ))
        db.commit()
        print("PageTurners reference data seed completed.")
        if not admin_password or not student_password:
            print("Demo accounts were not created. Set both seed passwords in .env if you need them.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
