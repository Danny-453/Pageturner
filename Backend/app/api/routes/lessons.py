from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import Lesson, Topic, User
from app.schemas.lesson import LessonCreate, LessonOut, LessonUpdate

router = APIRouter(prefix="/lessons", tags=["Lessons"])

@router.get("", response_model=list[LessonOut])
def list_lessons(course_id: str | None = None, topic_id: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(Lesson).join(Topic)
    if course_id: stmt = stmt.where(Topic.course_id == course_id)
    if topic_id: stmt = stmt.where(Lesson.topic_id == topic_id)
    return list(db.scalars(stmt.order_by(Lesson.order)).all())

@router.get("/{lesson_id}", response_model=LessonOut)
def get_lesson(lesson_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(status_code=404, detail="Lesson not found.")
    return lesson

@router.post("", response_model=LessonOut, status_code=201, dependencies=[Depends(require_admin)])
def create_lesson(payload: LessonCreate, db: Session = Depends(get_db)):
    if not db.get(Topic, payload.topic_id): raise HTTPException(status_code=400, detail="Topic does not exist.")
    lesson = Lesson(**payload.model_dump()); db.add(lesson); db.commit(); db.refresh(lesson); return lesson

@router.patch("/{lesson_id}", response_model=LessonOut, dependencies=[Depends(require_admin)])
def update_lesson(lesson_id: str, payload: LessonUpdate, db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(status_code=404, detail="Lesson not found.")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(lesson, key, value)
    db.commit(); db.refresh(lesson); return lesson

@router.delete("/{lesson_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_lesson(lesson_id: str, db: Session = Depends(get_db)):
    lesson = db.get(Lesson, lesson_id)
    if not lesson: raise HTTPException(status_code=404, detail="Lesson not found.")
    db.delete(lesson); db.commit()
