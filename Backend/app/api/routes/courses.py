from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import Course, CourseEnrollment, Topic, User
from app.repositories.course_repository import CourseRepository
from app.schemas.course import CourseCreate, CourseOut, CourseUpdate, TopicCreate, TopicOut, TopicUpdate

router = APIRouter(prefix="/courses", tags=["Courses"])

@router.get("", response_model=list[CourseOut])
def list_courses(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return CourseRepository(db).published()

@router.get("/{course_id}", response_model=CourseOut)
def get_course(course_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course or not course.is_published:
        raise HTTPException(status_code=404, detail="Course not found.")
    return course

@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED, dependencies=[Depends(require_admin)])
def create_course(payload: CourseCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Course).where(Course.code == payload.code)):
        raise HTTPException(status_code=409, detail="Course code already exists.")
    course = Course(**payload.model_dump())
    db.add(course); db.commit(); db.refresh(course)
    return course

@router.patch("/{course_id}", response_model=CourseOut, dependencies=[Depends(require_admin)])
def update_course(course_id: str, payload: CourseUpdate, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(status_code=404, detail="Course not found.")
    data = payload.model_dump(exclude_unset=True)
    if "code" in data and db.scalar(select(Course).where(Course.code == data["code"], Course.id != course_id)):
        raise HTTPException(status_code=409, detail="Course code already exists.")
    for key, value in data.items(): setattr(course, key, value)
    db.commit(); db.refresh(course); return course

@router.delete("/{course_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_course(course_id: str, db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(status_code=404, detail="Course not found.")
    db.delete(course); db.commit()

@router.post("/{course_id}/enroll", status_code=201)
def enroll(course_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(status_code=404, detail="Course not found.")
    existing = db.scalar(select(CourseEnrollment).where(CourseEnrollment.user_id == user.id, CourseEnrollment.course_id == course_id))
    if existing: return {"enrolled": True, "enrollment_id": existing.id}
    enrollment = CourseEnrollment(user_id=user.id, course_id=course_id)
    db.add(enrollment); db.commit(); db.refresh(enrollment)
    return {"enrolled": True, "enrollment_id": enrollment.id}

@router.get("/{course_id}/topics", response_model=list[TopicOut])
def list_topics(course_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    if not db.get(Course, course_id): raise HTTPException(status_code=404, detail="Course not found.")
    return list(db.scalars(select(Topic).where(Topic.course_id == course_id).order_by(Topic.order)).all())

@router.post("/{course_id}/topics", response_model=TopicOut, status_code=201, dependencies=[Depends(require_admin)])
def create_topic(course_id: str, payload: TopicCreate, db: Session = Depends(get_db)):
    if not db.get(Course, course_id): raise HTTPException(status_code=404, detail="Course not found.")
    topic = Topic(course_id=course_id, **payload.model_dump()); db.add(topic); db.commit(); db.refresh(topic); return topic

@router.patch("/topics/{topic_id}", response_model=TopicOut, dependencies=[Depends(require_admin)])
def update_topic(topic_id: str, payload: TopicUpdate, db: Session = Depends(get_db)):
    topic = db.get(Topic, topic_id)
    if not topic: raise HTTPException(status_code=404, detail="Topic not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(topic, key, value)
    db.commit(); db.refresh(topic); return topic

@router.delete("/topics/{topic_id}", status_code=204, dependencies=[Depends(require_admin)])
def delete_topic(topic_id: str, db: Session = Depends(get_db)):
    topic = db.get(Topic, topic_id)
    if not topic: raise HTTPException(status_code=404, detail="Topic not found.")
    db.delete(topic); db.commit()
