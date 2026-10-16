from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models import User
from app.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)
        self.db = db

    def register(
        self,
        *,
        full_name: str,
        nickname: str,
        email: str,
        password: str,
        student_id: str | None,
        academic_level_id: str,
    ) -> User:
        email = email.lower()
        if self.users.by_email(email):
            raise ValueError("An account with this email already exists.")
        if student_id and self.users.by_student_id(student_id):
            raise ValueError("An account with this student ID already exists.")
        user = User(
            full_name=full_name.strip(), nickname=nickname.strip(), email=email, password_hash=hash_password(password),
            student_id=student_id, academic_level_id=academic_level_id,
        )
        self.users.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def authenticate(self, email: str, password: str) -> User | None:
        user = self.users.by_email(email.lower())
        if not user or not user.is_active or not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    def token_for(user: User) -> str:
        return create_access_token(user.id, user.role.value)
