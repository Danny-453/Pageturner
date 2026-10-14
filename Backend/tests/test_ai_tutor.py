from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.schemas.ai import TutorMessage, TutorRequest
from app.services import ai_tutor_service


def sample_course():
    return SimpleNamespace(title="Geology", code="GEO-101", description="", topics=[])


def sample_messages():
    return [TutorMessage(role="user", content="What is a rock?")]


def test_course_context_orders_topics_and_lessons():
    course = SimpleNamespace(
        title="Geology",
        code="GEO-101",
        description="Earth science",
        topics=[
            SimpleNamespace(order=2, title="Rocks", description="", lessons=[
                SimpleNamespace(order=2, title="Igneous", content="Magma cools."),
                SimpleNamespace(order=1, title="Rock cycle", content="Rocks change."),
            ]),
            SimpleNamespace(order=1, title="Earth", description="", lessons=[]),
        ],
    )

    context = ai_tutor_service.course_context(course)

    assert context.index("Topic: Earth") < context.index("Topic: Rocks")
    assert context.index("Lesson: Rock cycle") < context.index("Lesson: Igneous")


def test_ask_tutor_uses_server_key_and_returns_answer(monkeypatch):
    calls = {}

    class FakeGemini:
        def __init__(self, **kwargs):
            calls["client"] = kwargs
            self.models = SimpleNamespace(
                generate_content=lambda **kwargs: (
                    calls.update(request=kwargs)
                    or SimpleNamespace(text="A rock is naturally occurring.")
                )
            )

    monkeypatch.setattr(ai_tutor_service.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(ai_tutor_service.settings, "gemini_models", "test-model")
    monkeypatch.setattr(ai_tutor_service.genai, "Client", FakeGemini)

    answer = ai_tutor_service.ask_tutor(sample_course(), sample_messages())

    assert answer == "A rock is naturally occurring."
    assert calls["client"]["api_key"] == "test-key"
    assert calls["client"]["http_options"].timeout == ai_tutor_service.GEMINI_REQUEST_TIMEOUT_MS
    assert calls["request"]["model"] == "test-model"
    assert calls["request"]["contents"][-1].role == "user"
    assert "never invent or guess image URLs" in calls["request"]["config"].system_instruction


def test_ask_tutor_uses_next_model_after_temporary_failure(monkeypatch):
    attempted_models = []

    class FakeGemini:
        def __init__(self, **kwargs):
            self.models = SimpleNamespace(generate_content=self.generate_content)

        def generate_content(self, **kwargs):
            attempted_models.append(kwargs["model"])
            if kwargs["model"] == "primary-model":
                raise ai_tutor_service.errors.ServerError(
                    503,
                    {"error": {"message": "Model is temporarily unavailable"}},
                )
            return SimpleNamespace(text="Fallback model answered.")

    monkeypatch.setattr(ai_tutor_service.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(ai_tutor_service.settings, "gemini_models", "primary-model, fallback-model")
    monkeypatch.setattr(ai_tutor_service.genai, "Client", FakeGemini)

    answer = ai_tutor_service.ask_tutor(sample_course(), sample_messages())

    assert answer == "Fallback model answered."
    assert attempted_models == ["primary-model", "fallback-model"]


def test_ask_tutor_does_not_fallback_on_authentication_failure(monkeypatch):
    attempted_models = []

    class FakeGemini:
        def __init__(self, **kwargs):
            self.models = SimpleNamespace(generate_content=self.generate_content)

        def generate_content(self, **kwargs):
            attempted_models.append(kwargs["model"])
            raise ai_tutor_service.errors.ClientError(
                401,
                {"error": {"message": "Invalid API key"}},
            )

    monkeypatch.setattr(ai_tutor_service.settings, "gemini_api_key", "test-key")
    monkeypatch.setattr(ai_tutor_service.settings, "gemini_models", "primary-model,fallback-model")
    monkeypatch.setattr(ai_tutor_service.genai, "Client", FakeGemini)

    with pytest.raises(ai_tutor_service.TutorUnavailableError):
        ai_tutor_service.ask_tutor(sample_course(), sample_messages())

    assert attempted_models == ["primary-model"]


def test_ask_tutor_requires_gemini_key(monkeypatch):
    monkeypatch.setattr(ai_tutor_service.settings, "gemini_api_key", None)

    with pytest.raises(ai_tutor_service.TutorNotConfiguredError):
        ai_tutor_service.ask_tutor(sample_course(), sample_messages())


def test_configured_models_keeps_order_and_deduplicates(monkeypatch):
    monkeypatch.setattr(
        ai_tutor_service.settings,
        "gemini_models",
        " gemini-flash-lite-latest, gemini-3.1-flash-lite, gemini-flash-lite-latest ",
    )

    assert ai_tutor_service.configured_models() == [
        "gemini-flash-lite-latest",
        "gemini-3.1-flash-lite",
    ]


def test_tutor_request_allows_longer_assistant_replies():
    request = TutorRequest(
        course_id="course-id",
        messages=[
            {"role": "user", "content": "Explain this topic."},
            {"role": "assistant", "content": "A detailed answer. " * 200},
            {"role": "user", "content": "Can you summarize?"},
        ],
    )

    assert len(request.messages[1].content) > 2000


def test_tutor_request_keeps_student_question_limit():
    with pytest.raises(ValidationError, match="Student questions must be at most 2000 characters"):
        TutorMessage(role="user", content="x" * 2001)


def test_tutor_request_limits_total_conversation_history():
    with pytest.raises(ValidationError, match="conversation history is too long"):
        TutorRequest(
            course_id="course-id",
            messages=[
                {"role": "assistant", "content": "x" * 12000},
                {"role": "assistant", "content": "x" * 12000},
                {"role": "user", "content": "What next?"},
            ],
        )
