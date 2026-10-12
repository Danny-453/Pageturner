from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Course, StudentProgress, User
from app.schemas.progress import ProgressOut, ProgressUpdate

router = APIRouter(prefix="/progress", tags=["Progress"])

@router.get("", response_model=list[ProgressOut])
def my_progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(db.scalars(select(StudentProgress).where(StudentProgress.user_id == user.id).order_by(StudentProgress.updated_at.desc())).all())

@router.put("", response_model=ProgressOut)
def update_progress(payload: ProgressUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.get(Course, payload.course_id): raise HTTPException(status_code=404, detail="Course not found.")
    stmt = select(StudentProgress).where(StudentProgress.user_id == user.id, StudentProgress.course_id == payload.course_id, StudentProgress.lesson_id == payload.lesson_id)
    progress = db.scalar(stmt)
    if not progress:
        progress = StudentProgress(user_id=user.id, **payload.model_dump()); db.add(progress)
    else:
        progress.completed = payload.completed; progress.percent = payload.percent
    db.commit(); db.refresh(progress); return progress
