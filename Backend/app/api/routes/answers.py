from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import QuestionAttempt, User

router = APIRouter(prefix="/answers", tags=["Answers"])

@router.get("/history")
def history(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    attempts = db.scalars(select(QuestionAttempt).where(QuestionAttempt.user_id == user.id).order_by(QuestionAttempt.created_at.desc())).all()
    return [
        {"id": a.id, "question_id": a.question_id, "selected_answer": a.selected_answer,
         "is_correct": a.is_correct, "points_earned": a.points_earned, "created_at": a.created_at}
        for a in attempts
    ]
