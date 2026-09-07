import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User, UserRole


def get_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    return db.get(User, user_id)


def get_by_email(db: Session, email: str) -> User | None:
    stmt = select(User).where(User.email == email.lower())
    return db.scalar(stmt)


def list_supervisors(db: Session) -> list[User]:
    stmt = select(User).where(User.role == UserRole.SUPERVISOR).order_by(User.name)
    return list(db.scalars(stmt))


def create(db: Session, user: User) -> User:
    db.add(user)
    db.flush()
    return user
