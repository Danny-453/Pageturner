from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import Course, Topic, User
from app.schemas.ai import TutorRequest, TutorResponse
from app.services.ai_tutor_service import (
    TutorNotConfiguredError,
    TutorUnavailableError,
    ask_tutor,
)

router = APIRouter(prefix="/ai", tags=["AI Tutor"])


def _published_course(db: Session, course_id: str) -> Course:
    course = db.scalar(
        select(Course)
        .options(selectinload(Course.topics).selectinload(Topic.lessons))
        .where(Course.id == course_id, Course.is_published.is_(True))
    )
    if not course:
        raise HTTPException(status_code=404, detail="Course not found.")
    return course


@router.post("/tutor", response_model=TutorResponse)
def tutor(
    payload: TutorRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if payload.messages[-1].role != "user":
        raise HTTPException(status_code=422, detail="The latest tutor message must be from the student.")

    try:
        course = _published_course(db, payload.course_id)
        return TutorResponse(answer=ask_tutor(course, payload.messages))
    except HTTPException:
        raise
    except TutorNotConfiguredError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except TutorUnavailableError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
