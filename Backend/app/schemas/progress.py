from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class ProgressUpdate(BaseModel):
    course_id: str
    lesson_id: str | None = None
    completed: bool = False
    percent: int = Field(default=0, ge=0, le=100)


class ProgressOut(ORMModel):
    id: str
    course_id: str
    lesson_id: str | None
    completed: bool
    percent: int
    points: int
