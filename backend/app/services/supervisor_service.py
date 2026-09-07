import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models.user import User, UserRole, UserStatus
from app.repositories import user_repository
from app.schemas.user import SupervisorCreate, SupervisorUpdate


def list_supervisors(db: Session) -> list[User]:
    return user_repository.list_supervisors(db)


def get_supervisor_or_404(db: Session, supervisor_id: uuid.UUID) -> User:
    user = user_repository.get_by_id(db, supervisor_id)
    if not user or user.role != UserRole.SUPERVISOR:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supervisor not found.")
    return user


def create_supervisor(db: Session, payload: SupervisorCreate) -> User:
    if user_repository.get_by_email(db, payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="A user with this email already exists.")

    supervisor = User(
        name=payload.name,
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        role=UserRole.SUPERVISOR,
        phone=payload.phone,
        department=payload.department,
        status=UserStatus.ACTIVE,
    )
    user_repository.create(db, supervisor)
    db.commit()
    db.refresh(supervisor)
    return supervisor


def update_supervisor(db: Session, supervisor_id: uuid.UUID, payload: SupervisorUpdate) -> User:
    supervisor = get_supervisor_or_404(db, supervisor_id)
    if payload.name is not None:
        supervisor.name = payload.name
    if payload.phone is not None:
        supervisor.phone = payload.phone
    if payload.department is not None:
        supervisor.department = payload.department
    db.commit()
    db.refresh(supervisor)
    return supervisor


def set_supervisor_status(db: Session, supervisor_id: uuid.UUID, new_status: UserStatus) -> User:
    supervisor = get_supervisor_or_404(db, supervisor_id)
    supervisor.status = new_status
    db.commit()
    db.refresh(supervisor)
    return supervisor


def reset_supervisor_password(db: Session, supervisor_id: uuid.UUID, new_password: str) -> None:
    supervisor = get_supervisor_or_404(db, supervisor_id)
    supervisor.password_hash = hash_password(new_password)
    db.commit()
