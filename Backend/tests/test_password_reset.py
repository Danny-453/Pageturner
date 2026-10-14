from fastapi import BackgroundTasks, HTTPException
import pytest

from app.api.routes.auth import request_password_reset
from app.schemas.auth import PasswordResetRequest


class EmptyDatabase:
    def scalar(self, _statement):
        return None


def test_password_reset_rejects_unregistered_email_without_sending(monkeypatch):
    monkeypatch.setattr("app.api.routes.auth.settings.smtp_host", "smtp.example.com")
    monkeypatch.setattr("app.api.routes.auth.settings.smtp_sender_email", "noreply@example.com")
    background_tasks = BackgroundTasks()

    with pytest.raises(HTTPException) as error:
        request_password_reset(
            PasswordResetRequest(email="new-student@example.com"),
            background_tasks,
            EmptyDatabase(),
        )

    assert error.value.status_code == 404
    assert error.value.detail == "No active account is registered with this email address."
    assert background_tasks.tasks == []
