import pytest
from pydantic import ValidationError

from app.schemas.lesson import LessonCreate, LessonUpdate


def test_lesson_video_url_is_optional_and_blank_values_clear_it():
    lesson = LessonCreate(topic_id="topic-1", title="Lesson", content="Notes")
    assert lesson.video_url is None

    update = LessonUpdate(video_url="  ")
    assert update.video_url is None


def test_lesson_video_url_accepts_https_links():
    lesson = LessonCreate(
        topic_id="topic-1",
        title="Lesson",
        content="Notes",
        video_url=" https://youtu.be/abcdefghijk ",
    )
    assert lesson.video_url == "https://youtu.be/abcdefghijk"


@pytest.mark.parametrize(
    "video_url",
    [
        "http://example.com/video.mp4",
        "javascript:alert(1)",
        "//example.com/video.mp4",
        "https://user:password@example.com/video.mp4",
        "not a URL",
    ],
)
def test_lesson_video_url_rejects_unsafe_or_invalid_links(video_url):
    with pytest.raises(ValidationError):
        LessonUpdate(video_url=video_url)
