from pydantic import BaseModel


class LeaderboardEntry(BaseModel):
    rank: int
    user_id: str
    name: str
    academic_level: str
    points: int
    questions_answered: int
    accuracy: float


class LeaderboardResponse(BaseModel):
    scope: str
    entries: list[LeaderboardEntry]
    current_user_rank: int | None = None
