from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import UserRole


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=160)
    nickname: str = Field(min_length=2, max_length=40)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    student_id: str | None = Field(default=None, max_length=80)
    academic_level_id: str

    @field_validator("nickname", mode="before")
    @classmethod
    def trim_nickname(cls, value: str) -> str:
        return value.strip() if isinstance(value, str) else value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str = Field(min_length=32, max_length=200)
    new_password: str = Field(min_length=8, max_length=128)


class UserSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    full_name: str
    nickname: str | None = None
    email: EmailStr
    student_id: str | None
    role: UserRole
    academic_level_id: str
    total_points: int
    current_streak: int
    questions_answered: int
    correct_answers: int


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserSummary
