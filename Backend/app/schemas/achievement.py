from pydantic import BaseModel
from app.schemas.common import ORMModel


class AchievementCreate(BaseModel):
    name: str
    description: str
    criteria_type: str = "correct_answers"
    threshold: int = 0


class AchievementOut(ORMModel):
    id: str
    name: str
    description: str
    criteria_type: str
    threshold: int
