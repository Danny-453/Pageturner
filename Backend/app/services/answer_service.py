from sqlalchemy.orm import Session
from app.models import Question, QuestionAttempt, User
from app.services.achievement_service import award_eligible_achievements
from app.services.learning_service import current_learning_level


def submit_answer(db: Session, user: User, question: Question, selected_answer: str) -> tuple[QuestionAttempt, object | None]:
    is_correct = selected_answer == question.correct_answer
    points = question.points if is_correct else 0
    attempt = QuestionAttempt(
        user_id=user.id, question_id=question.id, selected_answer=selected_answer,
        is_correct=is_correct, points_earned=points,
    )
    db.add(attempt)
    user.questions_answered += 1
    user.total_points += points
    if is_correct:
        user.correct_answers += 1
        user.current_streak += 1
    else:
        user.current_streak = 0
    db.flush()
    award_eligible_achievements(db, user)
    level = current_learning_level(db, user)
    db.commit()
    db.refresh(user)
    return attempt, level
