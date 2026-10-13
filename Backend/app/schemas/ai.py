from typing import Literal

from pydantic import BaseModel, Field, model_validator


class TutorMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)

    @model_validator(mode="after")
    def validate_user_message_length(self):
        if self.role == "user" and len(self.content) > 2000:
            raise ValueError("Student questions must be at most 2000 characters.")
        return self


class TutorRequest(BaseModel):
    course_id: str = Field(min_length=1, max_length=36)
    messages: list[TutorMessage] = Field(min_length=1, max_length=12)

    @model_validator(mode="after")
    def validate_conversation_length(self):
        if sum(len(message.content) for message in self.messages) > 24000:
            raise ValueError("The conversation history is too long. Clear the conversation and try again.")
        return self


class TutorResponse(BaseModel):
    answer: str
