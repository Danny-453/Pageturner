from pydantic import BaseModel, EmailStr
from app.models.enums import UserRole


class UserOut(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    student_id: str | None
    role: UserRole
    academic_level_id: str
    total_points: int
    current_streak: int
    questions_answered: int
    correct_answers: int
    accuracy: float
    is_active: bool


class UserUpdate(BaseModel):
    full_name: str | None = None
    student_id: str | None = None
    academic_level_id: str | None = None


class UserStatusUpdate(BaseModel):
    is_active: bool
