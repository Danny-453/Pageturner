from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.api.deps import get_current_user
from app.db.session import get_db
from app.models import AcademicLevel, LearningLevel
from app.schemas.academic import AcademicLevelOut, LearningLevelOut

router = APIRouter(tags=["Academic"])

@router.get("/academic-levels", response_model=list[AcademicLevelOut])
def academic_levels(db: Session = Depends(get_db)):
    return list(db.scalars(select(AcademicLevel).order_by(AcademicLevel.order)).all())

@router.get("/learning-levels", response_model=list[LearningLevelOut])
def learning_levels(db: Session = Depends(get_db)):
    return list(db.scalars(select(LearningLevel).order_by(LearningLevel.level)).all())
