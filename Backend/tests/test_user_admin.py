from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes.users import delete_user, update_user_status
from app.models.enums import UserRole
from app.schemas.user import UserStatusUpdate


def make_user(user_id, role=UserRole.student, is_active=True):
    return SimpleNamespace(
        id=user_id,
        full_name=f"User {user_id}",
        nickname=None,
        email=f"{user_id}@example.org",
        student_id=None,
        role=role,
        academic_level_id="level-1",
        total_points=0,
        current_streak=0,
        questions_answered=0,
        correct_answers=0,
        is_active=is_active,
    )


class FakeResults:
    def __init__(self, items):
        self.items = items

    def all(self):
        return self.items


class FakeDatabase:
    def __init__(self, users, active_admins=()):
        self.users = {user.id: user for user in users}
        self.active_admins = list(active_admins)
        self.deleted = []
        self.executed = []
        self.committed = False

    def get(self, model, user_id):
        return self.users.get(user_id)

    def scalars(self, statement):
        return FakeResults(self.active_admins)

    def execute(self, statement):
        self.executed.append(statement)

    def delete(self, item):
        self.deleted.append(item)

    def commit(self):
        self.committed = True

    def refresh(self, item):
        return None


def test_admin_can_deactivate_and_reactivate_user():
    admin = make_user("admin", UserRole.admin)
    student = make_user("student")
    db = FakeDatabase([admin, student], active_admins=[admin])

    deactivated = update_user_status(
        "student", UserStatusUpdate(is_active=False), db, admin
    )
    assert deactivated.is_active is False
    assert db.committed

    db.committed = False
    reactivated = update_user_status(
        "student", UserStatusUpdate(is_active=True), db, admin
    )
    assert reactivated.is_active is True
    assert db.committed


def test_admin_cannot_deactivate_self():
    admin = make_user("admin", UserRole.admin)

    with pytest.raises(HTTPException) as error:
        update_user_status(
            "admin", UserStatusUpdate(is_active=False), FakeDatabase([admin]), admin
        )
    assert error.value.detail == "You cannot deactivate your own account."


def test_last_active_admin_cannot_be_deactivated_or_deleted():
    admin = make_user("admin", UserRole.admin)
    target = make_user("other-admin", UserRole.admin)
    db = FakeDatabase([admin, target], active_admins=[target])

    with pytest.raises(HTTPException) as deactivate_error:
        update_user_status(
            target.id, UserStatusUpdate(is_active=False), db, admin
        )
    assert deactivate_error.value.status_code == 409

    with pytest.raises(HTTPException) as delete_error:
        delete_user(target.id, db, admin)
    assert delete_error.value.status_code == 409

    assert not db.committed
    assert not db.deleted


def test_permanent_delete_removes_user_and_clears_reset_tokens():
    admin = make_user("admin", UserRole.admin)
    student = make_user("student")
    db = FakeDatabase([admin, student], active_admins=[admin])

    response = delete_user("student", db, admin)

    assert response.status_code == 204
    assert db.deleted == [student]
    assert len(db.executed) == 1
    assert "password_reset_tokens" in str(db.executed[0])
    assert db.committed


def test_admin_cannot_permanently_delete_self():
    admin = make_user("admin", UserRole.admin)

    with pytest.raises(HTTPException) as error:
        delete_user("admin", FakeDatabase([admin]), admin)
    assert error.value.detail == "You cannot delete your own account."
