from urllib.parse import urlsplit

from pydantic import BaseModel
from pydantic import Field, field_validator
from app.schemas.common import ORMModel


def validate_video_url(value: str | None) -> str | None:
    if value is None or not value.strip():
        return None

    value = value.strip()
    try:
        parsed = urlsplit(value)
        parsed.port
    except ValueError as error:
        raise ValueError("Enter a valid HTTPS video URL.") from error
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Enter a valid HTTPS video URL.")
    return value


class LessonCreate(BaseModel):
    topic_id: str
    title: str
    content: str
    video_url: str | None = Field(default=None, max_length=2048)
    order: int = 1
    estimated_minutes: int = 15

    _validate_video_url = field_validator("video_url")(validate_video_url)


class LessonUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    video_url: str | None = Field(default=None, max_length=2048)
    order: int | None = None
    estimated_minutes: int | None = None

    _validate_video_url = field_validator("video_url")(validate_video_url)


class LessonOut(ORMModel):
    id: str
    topic_id: str
    title: str
    content: str
    video_url: str | None
    order: int
    estimated_minutes: int
