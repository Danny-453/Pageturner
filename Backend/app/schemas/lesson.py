from pydantic import BaseModel
from app.schemas.common import ORMModel


class LessonCreate(BaseModel):
    topic_id: str
    title: str
    content: str
    order: int = 1
    estimated_minutes: int = 15


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    order: int | None = None
    estimated_minutes: int | None = None


class LessonOut(ORMModel):
    id: str
    topic_id: str
    title: str
    content: str
    order: int
    estimated_minutes: int
