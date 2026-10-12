from pydantic import BaseModel, Field
from app.schemas.common import ORMModel


class CourseCreate(BaseModel):
    code: str = Field(min_length=2, max_length=30)
    title: str = Field(min_length=2, max_length=180)
    description: str
    academic_level_id: str
    is_published: bool = True


class CourseUpdate(BaseModel):
    code: str | None = None
    title: str | None = None
    description: str | None = None
    academic_level_id: str | None = None
    is_published: bool | None = None


class CourseOut(ORMModel):
    id: str
    code: str
    title: str
    description: str
    academic_level_id: str
    is_published: bool


class TopicCreate(BaseModel):
    title: str
    description: str = ""
    order: int = 1


class TopicUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    order: int | None = None


class TopicOut(ORMModel):
    id: str
    course_id: str
    title: str
    description: str
    order: int
