from types import SimpleNamespace

from app.api.routes.leaderboard import leaderboard
from app.schemas.auth import RegisterRequest


def test_registration_does_not_require_nickname():
    registration = RegisterRequest(
        full_name="Student Name",
        email="student@example.org",
        password="valid-test-password",
        academic_level_id="level-1",
    )

    assert registration.full_name == "Student Name"


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


def test_leaderboard_displays_student_full_name():
    student = SimpleNamespace(
        id="student-1",
        full_name="Student Full Name",
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

    assert result.entries[0].name == "Student Full Name"
