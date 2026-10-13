from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.session import get_db
from app.models import AcademicLevel, PasswordResetToken, User
from app.models.enums import UserRole
from app.schemas.user import UserOut, UserStatusUpdate, UserUpdate

router = APIRouter(prefix="/users", tags=["Users"])


def user_out(db: Session, user: User) -> UserOut:
    accuracy = (user.correct_answers / user.questions_answered * 100) if user.questions_answered else 0
    return UserOut(
        id=user.id, full_name=user.full_name, email=user.email, student_id=user.student_id,
        role=user.role, academic_level_id=user.academic_level_id, total_points=user.total_points,
        current_streak=user.current_streak, questions_answered=user.questions_answered,
        correct_answers=user.correct_answers, accuracy=round(accuracy, 2), is_active=user.is_active,
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


def _protect_last_active_admin(db: Session, target: User) -> None:
    if target.role != UserRole.admin or not target.is_active:
        return
    active_admins = db.scalars(
        select(User)
        .where(
            User.role == UserRole.admin,
            User.is_active.is_(True),
        )
        .order_by(User.id)
        .with_for_update()
    ).all()
    if len(active_admins) <= 1:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The last active administrator cannot be deactivated or deleted.",
        )


@router.patch("/{user_id}/status", response_model=UserOut, dependencies=[Depends(require_admin)])
def update_user_status(
    user_id: str,
    payload: UserStatusUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user),
):
    if user_id == admin.id and not payload.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account.",
        )
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    if not payload.is_active:
        _protect_last_active_admin(db, target)
    target.is_active = payload.is_active
    db.commit()
    db.refresh(target)
    return user_out(db, target)


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    dependencies=[Depends(require_admin)],
)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_user),
):
    if user_id == admin.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own account.",
        )
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    _protect_last_active_admin(db, target)
    db.execute(delete(PasswordResetToken).where(PasswordResetToken.user_id == target.id))
    db.delete(target)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
