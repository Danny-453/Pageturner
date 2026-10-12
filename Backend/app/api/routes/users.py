from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import AcademicLevel, User
from app.schemas.user import UserOut, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def user_out(db: Session, user: User) -> UserOut:
    accuracy = (user.correct_answers / user.questions_answered * 100) if user.questions_answered else 0
    return UserOut(
        id=user.id, full_name=user.full_name, email=user.email, student_id=user.student_id,
        role=user.role, academic_level_id=user.academic_level_id, total_points=user.total_points,
        current_streak=user.current_streak, questions_answered=user.questions_answered,
        correct_answers=user.correct_answers, accuracy=round(accuracy, 2),
    )


@router.get("/me", response_model=UserOut)
def profile(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return user_out(db, user)


@router.patch("/me", response_model=UserOut)
def update_profile(payload: UserUpdate, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    data = payload.model_dump(exclude_unset=True)
    if "academic_level_id" in data and not db.get(AcademicLevel, data["academic_level_id"]):
        raise HTTPException(status_code=400, detail="Academic level does not exist.")
    for key, value in data.items():
        setattr(user, key, value.strip() if isinstance(value, str) else value)
    db.commit()
    db.refresh(user)
    return user_out(db, user)


@router.get("", response_model=list[UserOut], dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    return [user_out(db, user) for user in db.scalars(select(User).order_by(User.full_name)).all()]
