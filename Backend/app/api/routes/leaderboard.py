from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import AcademicLevel, Course, CourseEnrollment, User
from app.schemas.leaderboard import LeaderboardEntry, LeaderboardResponse

router = APIRouter(prefix="/leaderboard", tags=["Leaderboard"])

@router.get("", response_model=LeaderboardResponse)
def leaderboard(scope: str = Query("department", pattern="^(department|level|course)$"), course_id: str | None = None, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    stmt = select(User, AcademicLevel.name).join(AcademicLevel)
    if scope == "level": stmt = stmt.where(User.academic_level_id == user.academic_level_id)
    elif scope == "course" and course_id:
        stmt = stmt.join(CourseEnrollment, CourseEnrollment.user_id == User.id).where(CourseEnrollment.course_id == course_id)
    rows = db.execute(stmt.order_by(User.total_points.desc(), User.correct_answers.desc(), User.full_name.asc())).all()
    entries = []
    current_rank = None
    for index, (student, level_name) in enumerate(rows, start=1):
        accuracy = round(student.correct_answers / student.questions_answered * 100, 2) if student.questions_answered else 0
        entry = LeaderboardEntry(rank=index, user_id=student.id, name=student.full_name, academic_level=level_name, points=student.total_points, questions_answered=student.questions_answered, accuracy=accuracy)
        entries.append(entry)
        if student.id == user.id: current_rank = index
    return LeaderboardResponse(scope=scope, entries=entries, current_user_rank=current_rank)
