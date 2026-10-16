from types import SimpleNamespace

import pytest
from pydantic import ValidationError

from app.api.routes.leaderboard import leaderboard
from app.schemas.auth import RegisterRequest


def test_registration_requires_and_trims_nickname():
    registration = RegisterRequest(
        full_name="Student Name",
        nickname="  RockStar  ",
        email="student@example.org",
        password="password123",
        academic_level_id="level-1",
    )

    assert registration.nickname == "RockStar"

    with pytest.raises(ValidationError):
        RegisterRequest(
            full_name="Student Name",
            email="student@example.org",
            password="password123",
            academic_level_id="level-1",
        )


class FakeRows:
    def __init__(self, rows):
        self.rows = rows

    def all(self):
        return self.rows


class FakeDatabase:
    def __init__(self, rows):
        self.rows = rows

    def execute(self, _statement):
        return FakeRows(self.rows)


def test_leaderboard_does_not_expose_full_name_when_nickname_is_missing():
    student = SimpleNamespace(
        id="student-1",
        full_name="Private Full Name",
        nickname=None,
        total_points=10,
        correct_answers=1,
        questions_answered=2,
    )
    current_user = SimpleNamespace(id="student-1", academic_level_id="level-1")

    result = leaderboard(
        scope="department",
        db=FakeDatabase([(student, "300 Level")]),
        user=current_user,
    )

    assert result.entries[0].nickname == "Student"
    assert not hasattr(result.entries[0], "name")
