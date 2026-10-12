from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Achievement, StudentAchievement, User


def award_eligible_achievements(db: Session, user: User) -> list[Achievement]:
    achievements = list(db.scalars(select(Achievement).order_by(Achievement.threshold)).all())
    awarded_ids = {item.achievement_id for item in user.achievements}
    newly_awarded: list[Achievement] = []
    for achievement in achievements:
        if achievement.id in awarded_ids:
            continue
        if achievement.criteria_type == "correct_answers":
            metric = user.correct_answers
        elif achievement.criteria_type == "accuracy":
            metric = (user.correct_answers / user.questions_answered * 100) if user.questions_answered else 0
        elif achievement.criteria_type == "learning_level":
            from app.services.learning_service import current_learning_level
            current = current_learning_level(db, user)
            metric = current.level if current else 1
        elif achievement.criteria_type == "courses_completed":
            metric = sum(1 for progress in user.progress if progress.lesson_id is None and progress.completed)
        else:
            metric = 0
        eligible = metric >= achievement.threshold
        if eligible:
            db.add(StudentAchievement(user_id=user.id, achievement_id=achievement.id))
            newly_awarded.append(achievement)
    if newly_awarded:
        db.flush()
    return newly_awarded
