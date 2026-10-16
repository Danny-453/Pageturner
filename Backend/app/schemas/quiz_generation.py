from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import Difficulty


class GeneratedOption(BaseModel):
    model_config = ConfigDict(extra="forbid")

    option_key: Literal["a", "b", "c", "d"]
    text: str = Field(min_length=1, max_length=500)


class GeneratedQuestion(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_text: str = Field(min_length=1, max_length=2000)
    difficulty: Difficulty
    explanation: str = Field(min_length=1, max_length=2000)
    correct_answer: Literal["a", "b", "c", "d"]
    options: list[GeneratedOption] = Field(min_length=4, max_length=4)

    @model_validator(mode="after")
    def validate_answer_options(self):
        keys = [option.option_key for option in self.options]
        if len(set(keys)) != 4 or set(keys) != {"a", "b", "c", "d"}:
            raise ValueError("Each generated question must contain options a, b, c, and d exactly once.")
        return self


class GeneratedQuiz(BaseModel):
    model_config = ConfigDict(extra="forbid")

    questions: list[GeneratedQuestion] = Field(min_length=20, max_length=20)
