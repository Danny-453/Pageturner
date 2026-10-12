from typing import Generic, TypeVar
from sqlalchemy import select
from sqlalchemy.orm import Session

T = TypeVar("T")


class Repository(Generic[T]):
    def __init__(self, db: Session, model: type[T]):
        self.db = db
        self.model = model

    def get(self, item_id: str) -> T | None:
        return self.db.get(self.model, item_id)

    def list(self) -> list[T]:
        return list(self.db.scalars(select(self.model)).all())

    def add(self, item: T) -> T:
        self.db.add(item)
        self.db.flush()
        return item

    def delete(self, item: T) -> None:
        self.db.delete(item)
        self.db.flush()
