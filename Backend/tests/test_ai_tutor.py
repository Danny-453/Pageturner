from types import SimpleNamespace

import httpx
import pytest
from pydantic import ValidationError

from app.schemas.ai import TutorMessage, TutorRequest
from app.services import ai_tutor_service


def make_response(status_code, payload):
    return httpx.Response(
        status_code,
        json=payload,
        request=httpx.Request("POST", "https://agentrouter.org/v1/chat/completions"),
    )


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


def test_ask_tutor_uses_agentrouter_key_endpoint_and_model(monkeypatch):
    calls = {}

    def fake_post(url, **kwargs):
        calls.update(url=url, **kwargs)
        return make_response(
            200,
            {"choices": [{"message": {"role": "assistant", "content": "A rock is naturally occurring."}}]},
        )

    monkeypatch.setattr(ai_tutor_service.settings, "agentrouter_api_key", "agentrouter-test-key")
    monkeypatch.setattr(ai_tutor_service.settings, "ai_tutor_base_url", "https://agentrouter.org/v1")
    monkeypatch.setattr(ai_tutor_service.settings, "ai_tutor_models", "gpt-6-astra")
    monkeypatch.setattr(ai_tutor_service.httpx, "post", fake_post)

    answer = ai_tutor_service.ask_tutor(sample_course(), sample_messages())

    assert answer == "A rock is naturally occurring."
    assert calls["url"] == "https://agentrouter.org/v1/chat/completions"
    assert calls["headers"]["Authorization"] == "Bearer agentrouter-test-key"
    assert calls["json"]["model"] == "gpt-6-astra"
    assert calls["json"]["messages"][1:] == [{"role": "user", "content": "What is a rock?"}]
    assert calls["json"]["messages"][0]["role"] == "system"
    assert "never invent or guess image URLs" in calls["json"]["messages"][0]["content"]
    assert calls["timeout"] == ai_tutor_service.AI_REQUEST_TIMEOUT_SECONDS


def test_ask_tutor_falls_back_to_claude_through_agentrouter(monkeypatch):
    attempted = []

    def fake_post(url, **kwargs):
        model = kwargs["json"]["model"]
        attempted.append((url, kwargs["headers"]["Authorization"], model))
        if model == "gpt-6-astra":
            return make_response(503, {"error": {"message": "Temporarily unavailable"}})
        return make_response(
            200,
            {"choices": [{"message": {"role": "assistant", "content": "Claude answered."}}]},
        )

    monkeypatch.setattr(ai_tutor_service.settings, "agentrouter_api_key", "agentrouter-test-key")
    monkeypatch.setattr(ai_tutor_service.settings, "ai_tutor_base_url", "https://agentrouter.org/v1")
    monkeypatch.setattr(ai_tutor_service.settings, "ai_tutor_models", "gpt-6-astra,claude-opus-4-8")
    monkeypatch.setattr(ai_tutor_service.httpx, "post", fake_post)

    answer = ai_tutor_service.ask_tutor(sample_course(), sample_messages())

    assert answer == "Claude answered."
    assert attempted == [
        ("https://agentrouter.org/v1/chat/completions", "Bearer agentrouter-test-key", "gpt-6-astra"),
        ("https://agentrouter.org/v1/chat/completions", "Bearer agentrouter-test-key", "claude-opus-4-8"),
    ]


def test_ask_tutor_does_not_fallback_on_authentication_failure(monkeypatch):
    attempted = []

    def fake_post(url, **kwargs):
        attempted.append(kwargs["json"]["model"])
        return make_response(401, {"error": {"message": "Invalid API key"}})

    monkeypatch.setattr(ai_tutor_service.settings, "agentrouter_api_key", "agentrouter-test-key")
    monkeypatch.setattr(ai_tutor_service.settings, "ai_tutor_base_url", "https://agentrouter.org/v1")
    monkeypatch.setattr(ai_tutor_service.settings, "ai_tutor_models", "gpt-6-astra,claude-opus-4-8")
    monkeypatch.setattr(ai_tutor_service.httpx, "post", fake_post)

    with pytest.raises(ai_tutor_service.TutorUnavailableError):
        ai_tutor_service.ask_tutor(sample_course(), sample_messages())

    assert attempted == ["gpt-6-astra"]


def test_ask_tutor_requires_agentrouter_key(monkeypatch):
    monkeypatch.setattr(ai_tutor_service.settings, "agentrouter_api_key", None)

    with pytest.raises(ai_tutor_service.TutorNotConfiguredError, match="AgentRouter API key"):
        ai_tutor_service.ask_tutor(sample_course(), sample_messages())


def test_configured_models_keeps_order_and_deduplicates(monkeypatch):
    monkeypatch.setattr(
        ai_tutor_service.settings,
        "ai_tutor_models",
        " gpt-6-astra, claude-opus-4-8, gpt-6-astra ",
    )

    assert ai_tutor_service.configured_models() == ["gpt-6-astra", "claude-opus-4-8"]


def test_configured_models_normalizes_previous_openrouter_ids(monkeypatch):
    monkeypatch.setattr(
        ai_tutor_service.settings,
        "ai_tutor_models",
        "openai/gpt-6-astra,anthropic/claude-opus-4.8",
    )

    assert ai_tutor_service.configured_models() == ["gpt-6-astra", "claude-opus-4-8"]


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
