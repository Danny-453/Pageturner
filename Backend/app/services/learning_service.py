from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import LearningLevel, User


def current_learning_level(db: Session, user: User) -> LearningLevel | None:
    levels = list(db.scalars(select(LearningLevel).order_by(LearningLevel.level)).all())
    selected = None
    for level in levels:
        if user.correct_answers >= level.required_correct_answers:
            selected = level
    return selected or (levels[0] if levels else None)
