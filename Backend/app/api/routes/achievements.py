from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import Achievement, StudentAchievement, User
from app.schemas.achievement import AchievementCreate, AchievementOut

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.get("", response_model=list[AchievementOut])
def achievements(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return list(db.scalars(select(Achievement).order_by(Achievement.threshold, Achievement.name)).all())

@router.get("/mine")
def my_achievements(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    rows = db.scalars(select(StudentAchievement).where(StudentAchievement.user_id == user.id).order_by(StudentAchievement.awarded_at.desc())).all()
    return [{"id": row.achievement.id, "name": row.achievement.name, "description": row.achievement.description, "awarded_at": row.awarded_at} for row in rows]

@router.post("", response_model=AchievementOut, status_code=201, dependencies=[Depends(require_admin)])
def create_achievement(payload: AchievementCreate, db: Session = Depends(get_db)):
    achievement = Achievement(**payload.model_dump()); db.add(achievement); db.commit(); db.refresh(achievement); return achievement
