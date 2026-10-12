from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.api.deps import require_admin
from app.db.session import get_db
from app.models import Course, Question, StudentProgress, User

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/analytics", dependencies=[Depends(require_admin)])
def analytics(db: Session = Depends(get_db)):
    return {
        "students": db.scalar(select(func.count(User.id)).where(User.role == "student")) or 0,
        "courses": db.scalar(select(func.count(Course.id))) or 0,
        "questions": db.scalar(select(func.count(Question.id))) or 0,
        "progress_records": db.scalar(select(func.count(StudentProgress.id))) or 0,
    }
