from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models import Course
from app.repositories.base import Repository


class CourseRepository(Repository[Course]):
    def __init__(self, db: Session):
        super().__init__(db, Course)

    def published(self) -> list[Course]:
        return list(self.db.scalars(select(Course).where(Course.is_published.is_(True))).all())
