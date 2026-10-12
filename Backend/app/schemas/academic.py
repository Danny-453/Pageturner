from pydantic import BaseModel
from app.schemas.common import ORMModel


class AcademicLevelOut(ORMModel):
    id: str
    name: str
    order: int


class LearningLevelOut(ORMModel):
    id: str
    level: int
    name: str
    required_correct_answers: int
