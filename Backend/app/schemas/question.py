from pydantic import BaseModel, Field
from app.models.enums import Difficulty, QuestionType
from app.schemas.common import ORMModel


class QuestionOptionCreate(BaseModel):
    option_key: str = Field(min_length=1, max_length=10)
    text: str = Field(min_length=1, max_length=500)
    order: int = 1


class QuestionCreate(BaseModel):
    topic_id: str
    question_text: str
    question_type: QuestionType = QuestionType.multiple_choice
    difficulty: Difficulty = Difficulty.medium
    explanation: str
    points: int = Field(default=10, ge=0)
    correct_answer: str
    options: list[QuestionOptionCreate] = []
    is_published: bool = True


class QuestionUpdate(BaseModel):
    question_text: str | None = None
    question_type: QuestionType | None = None
    difficulty: Difficulty | None = None
    explanation: str | None = None
    points: int | None = Field(default=None, ge=0)
    correct_answer: str | None = None
    is_published: bool | None = None
    options: list[QuestionOptionCreate] | None = None


class QuestionOptionOut(ORMModel):
    id: str
    option_key: str
    text: str
    order: int


class QuestionOut(ORMModel):
    id: str
    topic_id: str
    question_text: str
    question_type: QuestionType
    difficulty: Difficulty
    points: int
    is_published: bool
    options: list[QuestionOptionOut] = []


class QuestionAdminOut(QuestionOut):
    question_text: str
    explanation: str
    correct_answer: str


class AnswerRequest(BaseModel):
    answer_id: str


class AnswerResult(BaseModel):
    correct: bool
    points: int
    explanation: str
    total_points: int
    questions_answered: int
    correct_answers: int
    learning_level: int
